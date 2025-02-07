import pandas as pd
import logging
from typing import List, Optional, Any
import tldextract
import json
import os
from work_with_db import URLDatabase, DatabaseError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from trafficking_news import TraffickingNewsSearch, extract_main_text_selenium
from models import (
    ConfirmResponse,
    IncidentResponse,
    SuspectFormResponse,
    SuspectResponse,
    VictimResponse,
    VictimFormResponse
)
import requests
import math
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import random
from newspaper import Article
from get_urls_from_csvs import get_unique_urls_from_csvs

llm = OpenAI(temperature=0, model="o3-mini", request_timeout=120.0)
memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

# Configure Logging
logging.basicConfig(
    filename="google_search.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Load API credentials from environment variables
API_KEY = os.getenv('GOOGLE_API_KEY')
SEARCH_ENGINE_ID = os.getenv('GOOGLE_CSE_ID')

if not API_KEY or not SEARCH_ENGINE_ID:
    logger.critical("API_KEY and SEARCH_ENGINE_ID must be set as environment variables.")
    exit(1)

SHORT_PROMPTS = {
    "incident_prompt": (
        "Assistant, please indicate if it can be said with certainty that this article is a factual report of an "
        "actual incident of human trafficking or any closely associated crime."
        "Return your answer in the following RAW JSON format with NO backticks OR code blocks:\n"
        "{\n"
        '  "answer": "yes" or "no",\n'
        '  "evidence": ["incident1", "incident2", "incident3"] or null\n'
        "}"
    ),
    "crime_prompt": (
        "Assistant, please indicate if there is mention of crime in this article. If yes, provide the crime(s) by name. "
        "Return your answer in the following JSON format:\n"
        "{\n"
        '  "answer": "yes" or "no",\n'
        '  "evidence": ["crime1", "crime2", "crime3"] or null\n'
        "}"
    ),
    "suspect_prompt": (
        "Assistant, please indicate if there is mention of suspect(s) of a crime related to human trafficking in this article. "
        "Suspects has to be natural persons that is, the NAME (firstname and/or secondname of suspect) of a person, not organizations or any other entities. Exclude cases involving allegations and cases involving "
        "politicians or celebrities or ANY other sensational reports or reporting."
        "If yes, provide the suspects(s) by name. EXCLUDE ALL other detail and ONLY provide the GIVEN NAME of the suspect(s)."
        "Return your answer in the following RAW JSON format ONLY and NO back ticks and with no code blocks:\n"
        "{\n"
        '  "answer": "yes" or "no",\n'
        '  "evidence": ["firstname and/or secondname of suspect1", '
        '"firstname and/or secondname of suspect2", "firstname and/or secondname of suspect3", ...] or null\n'
        "}"
    ),
    "victim_prompt": (
        "Assistant, the following is a list of named suspects in the accompanying article.  Please indicate if there is mention of victim(s) of a crime related to human trafficking in this article. "
        "Victims have to be natural persons that is, the NAME (firstname and/or secondname of victim) of a person, not organizations or any other entities. Exclude cases involving allegations and cases involving "
        "politicians or celebrities or ANY other sensational reports or reporting."
        "If yes, provide the victim(s) by name. EXCLUDE ALL other detail and ONLY provide the GIVEN NAME of the victim(s)."
        "Return your answer in the following RAW JSON format ONLY with NO back ticks and with NO code blocks:\n"
        "{\n"
        '  "answer": "yes" or "no",\n'
        '  "evidence": ["firstname and/or secondname of victim1", '
        '"firstname and/or secondname of victim2", "firstname and/or secondname of victim2", ...] or null\n'
        "}"
    ),
}


def spoof_articles(path) -> List[str]:
    """
    Fetch articles synchronously using google search.
    """
    articles = []
    try:
        df = pd.read_csv(path)
        urls = df['url'].tolist()
        return urls
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        return []

def google_search(query, api_key, cse_id, start, num=10):
    """
    Performs a Google Custom Search and returns the search results.

    Args:
        query (str): The search query.
        api_key (str): Your Google API key.
        cse_id (str): Your Custom Search Engine ID.
        start (int): The index of the first result to return.
        num (int, optional): Number of results to return. Defaults to 10.

    Returns:
        list: A list of search result items.
    """
    service = build("customsearch", "v1", developerKey=api_key)
    try:
        res = service.cse().list(
            q=query,
            cx=cse_id,
            num=num,
            start=start
        ).execute()
        return res.get('items', [])
    except HttpError as e:
        error_content = e.content.decode('utf-8')
        logger.error(f"HTTP Error {e.resp.status}: {error_content}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during Google Search API call: {e}")
        return []

def extract_main_text_newspaper(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        logger.error(f"Error extracting text with newspaper from {url}: {e}")
        return ""

def fetch_all_results(query, api_key, cse_id, max_results=30):
    """
    Fetches all search results up to the specified maximum.

    Args:
        query (str): The search query.
        api_key (str): Your Google API key.
        cse_id (str): Your Custom Search Engine ID.
        max_results (int, optional): Maximum number of results to fetch. Defaults to 30.

    Returns:
        list: A list of all fetched search result items.
    """
    results = []
    num_per_page = 10
    total_pages = math.ceil(max_results / num_per_page)

    for page in range(total_pages):
        start = 1 + page * num_per_page
        logger.info(f"Fetching page {page + 1} with start={start}")
        page_results = google_search(query, api_key, cse_id, start, num=num_per_page)
        if not page_results:
            logger.warning(f"No results returned for start={start}. Ending search.")
            break
        results.extend(page_results)
        time.sleep(1)  # Delay to respect rate limits

    return results[:max_results]  # Ensure not to exceed max_results

def initialize_selenium() -> Optional[webdriver.Chrome]:
    """
    Initializes the Selenium WebDriver with headless Chrome,
    using a manually downloaded Apple Silicon chromedriver.

    Returns:
        webdriver.Chrome: An instance of the Selenium WebDriver.
    """
    try:
        # Update this path to wherever you placed your local (arm64) chromedriver
        driver_path = "/opt/homebrew/bin/chromedriver"

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/85.0.4183.102 Safari/537.36"
        )

        driver = webdriver.Chrome(
            service=ChromeService(driver_path),
            options=chrome_options,
        )
        logger.info("Selenium WebDriver initialized successfully.")
        driver.set_page_load_timeout(30)  # Set a 30-second timeout
        return driver

    except Exception as e:
        logger.error(f"Failed to initialize Selenium WebDriver: {e}")
        return None

def is_url_accessible(url):
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except requests.RequestException as e:
        logger.error(f"Request exception for URL {url}: {e}")
        return False

def get_validated_response(
    prompt_key: str, prompt_text: str, model_class: Any, chat_engine
) -> Optional[Any]:
    """
    Sends a prompt to the chat engine and returns a validated Pydantic model instance.

    Args:
        prompt_key (str): The key identifying the prompt and model.
        prompt_text (str): The prompt text to send.
        model_class (BaseModel): The Pydantic model to validate the response.

    Returns:
        Optional[Any]: An instance of the Pydantic model or None if validation fails.
        :param chat_engine:
    """
    try:
        response = chat_engine.chat(
            prompt_text
        )  # Assuming this returns a response object
        logger.info(
            f"Prompt '{prompt_key}' processed successfully with {response} and {response.response}"
        )
        response_text = response.response  # Adjust based on actual response structure
        response_data = model_class.model_validate_json(response_text)
        logger.info(f"Prompt '{prompt_key}' processed successfully.")
        return response_data
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding failed for '{prompt_key}': {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to parse response for '{prompt_key}': {e}")
        return None

def verify_incident(url: str, chat_engine):
    """
    Verifies incidents based on the URL and updates the database.
    Optionally uploads to Neo4j and Google Sheets based on user input.

    Args:
        url (str): The URL of the analyzed article.
        chat_engine: The chat engine instance used for processing.

    Returns:
        tuple: A dictionary containing the result and a list of incidents.
    """
    db = URLDatabase()
    result = {"actual_incident": -2}  # Default to -2 for unexpected cases
    incidents = []

    try:
        # Send prompt to chat engine
        prompt_key = "incident_prompt"
        prompt_text = SHORT_PROMPTS[prompt_key]

        response_data = get_validated_response(
            prompt_key, prompt_text, IncidentResponse, chat_engine
        )
        if response_data is None:
            logger.warning(f"Received no response or invalid response for URL: {url}")
            return result, incidents

        response_answer = response_data.answer.lower()
        if response_answer == "no":
            logger.info(f"No incident detected for URL: {url}")
            db.update_field(url, "actual_incident", 0)
            result["actual_incident"] = 0
            return result, incidents

        if response_answer == "yes":
            logger.info(f"Incident detected for URL: {url}")
            db.update_field(url, "actual_incident", 1)  # Optionally log this change
            result["actual_incident"] = 1
            incidents = response_data.evidence or []
            return result, incidents

        # Handle unexpected response cases
        logger.warning(f"Unexpected response answer for URL: {url} - {response_data.answer}")
        return result, incidents

    except Exception as e:
        logger.error(f"Error processing URL {url}: {e}")
        return result, incidents

def confirm_natural_name(name):
    """
    Confirm if the provided name is a natural person's name.

    Args:
        name (str): The name to confirm.
        chat_engine:
    """
    try:
        prompt_text = (f"Assistant, is '{name}' the GIVEN name of a natural person? "
                       "Return your ANSWER in the following RAW JSON format ONLY and WITHOUT backticks:\n"
                       "{\"answer\": \"yes\" or \"no\"}")
        resp = llm.complete(prompt_text)

        response_data = ConfirmResponse.model_validate_json(
            resp.text
        )
        if response_data is None:
            return False
        return response_data.answer.lower() == "yes"
    except Exception as e:
        logger.error(f"Failed to confirm natural name: {e}")
    return False

def upload_suspects(url: str, chat_engine):
    """
    Uploads suspects to the database.

    Args:
        url (str): The URL of the analyzed article.
        chat_engine:
    """
    suspects = []
    db = URLDatabase()
    try:
        # Send prompt to chat engine
        prompt_key = "suspect_prompt"

        prompt_text = SHORT_PROMPTS[prompt_key]
        response_data = get_validated_response(
            prompt_key, prompt_text, SuspectResponse, chat_engine
        )
        if response_data is None:
            return
        if response_data.answer.lower() == "yes":
            url_id = db.get_url_id(url)
            suspects = response_data.evidence or []
            for suspect in suspects:
                natural_name = confirm_natural_name(suspect)
                if natural_name:
                    try:
                        db.insert_suspect(url_id=url_id, suspect=suspect)
                        logger.info(f"Suspect inserted with natural name: {suspect}")
                    except DatabaseError as e:
                        logger.warning(f"Failed to insert suspect {suspect} for URL ID {url_id}: {e}")

                    # Attempt to populate suspect forms regardless of insertion success
                    try:
                        populate_suspect_forms_table(url, suspect, chat_engine)
                    except Exception as e:
                        logger.error(f"Failed to populate suspect form for suspect {suspect}: {e}")
        else:
            parameters = {"url": url, "suspect": "false"}
            logger.info(f"No suspect found: {parameters}")

    except Exception as e:
        logger.error(f"Failed to upload suspects: {e}")
    return suspects

def upload_victims(url: str, chat_engine):
    """
    Uploads victims to the database.

    Args:
        url (str): The URL of the analyzed article.
        chat_engine:
    """
    victims = []
    db = URLDatabase()
    try:
        # Send prompt to chat engine
        prompt_key = "victim_prompt"

        prompt_text = SHORT_PROMPTS[prompt_key]
        response_data = get_validated_response(
            prompt_key, prompt_text, VictimResponse, chat_engine
        )
        if response_data is None:
            return
        if response_data.answer.lower() == "yes":
            url_id = db.get_url_id(url)
            victims = response_data.evidence or []
            for victim in victims:
                natural_name = confirm_natural_name(victim)
                if natural_name:
                    try:
                        db.insert_victim(url_id=url_id, victim=victim)
                        logger.info(f"Victim inserted with natural name: {victim}")
                    except DatabaseError as e:
                        logger.warning(f"Failed to insert victim {victim} for URL ID {url_id}: {e}")

                    # Attempt to populate victim forms regardless of insertion success
                    try:
                        populate_victim_forms_table(url, victim, chat_engine)
                    except Exception as e:
                        logger.error(f"Failed to populate victim form for victim {victim}: {e}")
        else:
            parameters = {"url": url, "victim": "false"}
            logger.info(f"No victim found: {parameters}")

    except Exception as e:
        logger.error(f"Failed to upload victims: {e}")
    return victims


def populate_victim_forms_table(url: str, victim: str, chat_engine) -> None:
    """
    Populate the victim_forms table with data extracted from the victim_forms_prompt.

    Args:
        url (str): The URL of the article being analyzed.
        victim (str): The name of the victim.
        chat_engine: The chat engine instance for processing the prompt.
    """
    db = URLDatabase()

    try:
        # Generate the suspect form prompt
        victim_form_prompt = (
            f"Assistant, carefully extract the following details for {victim} from the text: "
            "1. Gender,"
            "2. Date of Birth,"
            "3. Age,"
            "4. Address Notes (any address/city/district associated with them would be stored here as text), "
            "5. Phone number,"
            "6. Nationality,"
            "7. Occupation,"
            "8. Victim Appearance,"
            "9. Victim Vehicle Description,"
            "10. Vehicle Plate #,"
            "11. Where is the victim been trafficked to?"
            "12. What job has the victim been offered?"
            
            
            "Please return your answer in the following RAW JSON format ONLY and NO backticks and NO code blocks, e.g.:\n"
            '{"gender": "male" or "female" or null,\n'
            '  "date_of_birth": "YYYY-MM-DD" or null,\n'
            '  "age": "integer" or null,\n'
            '  "address_notes": "text" or null,\n'
            '  "phone_number": "text" or null,\n'
            '  "nationality": "text" or null,\n'
            '  "occupation": "text" or null,\n'
            '  "appearance": "text" or null,\n'
            '  "vehicle_description": "text" or null,\n'
            '  "vehicle_plate_number": "text" or null,\n'
            '  "destination": "text" or null,\n'
            '  "job_offered": "text" or null\n'
            "}"
        )

        # Send the prompt to the chat engine
        response_text = chat_engine.chat(victim_form_prompt)

        # Add the suspect name to the response data dictionary
        response_json = json.loads(response_text.response)  # Convert response to dictionary
        response_json["name"] = victim  # Inject the suspect name

        # Validate the enriched response
        response_data = VictimFormResponse.model_validate(response_json)

        logger.info(f"Extracted victim form data: {response_data}")

        if response_data:
            # Retrieve the URL ID from the database
            url_id = db.get_url_id(url)
            victim_id = db.get_victim_id(url_id, victim)
            if url_id is None:
                logger.error(f"URL not found in database: {url}")
                return

            # Insert the data into the suspect_forms table
            db.insert_victim_form(url_id, response_data, victim_id)

            logger.info(f"Successfully inserted victim form for victim: {victim}")

    except Exception as e:
        logger.error(f"Failed to populate victim_forms table for victim '{victim}' from URL '{url}': {e}")

def populate_suspect_forms_table(url: str, suspect: str, chat_engine) -> None:
    """
    Populate the suspect_forms table with data extracted from the suspect_form_prompt.

    Args:
        url (str): The URL of the article being analyzed.
        suspect (str): The name of the suspect.
        chat_engine: The chat engine instance for processing the prompt.
    """
    db = URLDatabase()

    try:
        # Generate the suspect form prompt
        suspect_form_prompt = (
            f"Assistant, carefully extract the following details for {suspect} from the text: "
            "1. Gender,"
            "2. Date of Birth,"
            "3. Age,"
            "4. Address Notes (any address/city/location associated with them would be stored here just as text), "
            "5. Phone number,"
            "6. Nationality,"
            "7. Occupation,"
            "8. Role: Recruiter, Transporter, Master, Facilitator, Boss Trafficker, Host, Other [other role must still be their role in trafficking, not general job posting], "
            "9. Suspect Appearance,"
            "10. Suspect Vehicle Description,"
            "11. Vehicle Plate #,"
            "12. What is evident of the suspect from the article: Definitely trafficked many people, Has trafficked some people, Suspect s/he's a trafficker, Don't believe s/he's a trafficker, "
            "13. Arrested status? Yes - in police custody, Yes - but has been released (not on bail), Yes - but released on bail, No, "
            "14. Arrest Date,"
            "15. Crime(s) Person Charged With,"
            "16. Yes, willing (list PV names): A list of any PVs that seem willing to testify against the suspect, "
            "17. Suspect in police custody,"
            "18. Suspect's current location,"
            "19. Suspect's last known location (location text), "
            "20. Suspect's last known location date (date). "
            "Please return your answer in the following RAW JSON format ONLY and NO backticks and NO code blocks, e.g.:\n"
            '{"gender": "male" or "female" or null,\n'
            '  "date_of_birth": "YYYY-MM-DD" or null,\n'
            '  "age": "integer" or null,\n'
            '  "address_notes": "text" or null,\n'
            '  "phone_number": "text" or null,\n'
            '  "nationality": "text" or null,\n'
            '  "occupation": "text" or null,\n'
            '  "role": "text" or null,\n'
            '  "appearance": "text" or null,\n'
            '  "vehicle_description": "text" or null,\n'
            '  "vehicle_plate_number": "text" or null,\n'
            '  "evidence": "text" or null,\n'
            '  "arrested_status": "text" or null,\n'
            '  "arrest_date": "YYYY-MM-DD" or null,\n'
            '  "crimes_person_charged_with": "text" or null,\n'
            '  "willing_pv_names": "text" or null,\n'
            '  "suspect_in_police_custody": "text" or null,\n'
            '  "suspect_current_location": "text" or null,\n'
            '  "suspect_last_known_location": "text" or null,\n'
            '  "suspect_last_known_location_date": "YYYY-MM-DD" or null\n'
            "}"
        )

        # Send the prompt to the chat engine
        response_text = chat_engine.chat(suspect_form_prompt)

        # Add the suspect name to the response data dictionary
        response_json = json.loads(response_text.response)  # Convert response to dictionary
        response_json["name"] = suspect  # Inject the suspect name

        # Validate the enriched response
        response_data = SuspectFormResponse.model_validate(response_json)

        logger.info(f"Extracted suspect form data: {response_data}")

        if response_data:
            # Retrieve the URL ID from the database
            url_id = db.get_url_id(url)
            suspect_id = db.get_suspect_id(url_id, suspect)
            if url_id is None:
                logger.error(f"URL not found in database: {url}")
                return

            # Insert the data into the suspect_forms table
            db.insert_suspect_form(url_id, response_data, suspect_id)

            logger.info(f"Successfully inserted suspect form for suspect: {suspect}")

    except Exception as e:
        logger.error(f"Failed to populate suspect_forms table for suspect '{suspect}' from URL '{url}': {e}")

def fetch_url_with_retries(driver, url, max_retries=3, retry_delay=5):
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempt {attempt} to load URL: {url}")
            driver.get(url)
            logger.info(f"Successfully loaded URL: {url}")
            return True
        except TimeoutException:
            logger.warning(f"Attempt {attempt} timed out for URL: {url}")
        except WebDriverException as e:
            logger.error(f"WebDriverException on attempt {attempt} for URL {url}: {e}")
            break  # Break on WebDriver exceptions other than Timeout
        time.sleep(retry_delay)
    logger.error(f"Failed to load URL after {max_retries} attempts: {url}")
    return False

def get_new_urls(new_urls: List[str]) -> List[str]:
    """
    Get URLs that are not already in the database.

    Args:
        new_urls (List[str]): List of new URLs to check
        db_urls (List[str]): List of URLs already in the database

    Returns:
        List[str]: URLs that are not already in the database
    """
    db = URLDatabase()
    df = pd.DataFrame(db.search_urls(limit=1000000))
    db_urls = df['url'].tolist()
    return list(set(new_urls) - set(db_urls))

def main():
    # Initialize Database
    db = URLDatabase()

    # Define search parameters
    search_terms = [
        '"human trafficking"',
        '"cyber trafficking"',
        '"child trafficking"',
        '"organ trafficking"',
        '"sex trafficking"'
    ]

    # Define the location filter


    # Define domains to exclude
    excluded_domains = [
        'wikipedia',
        'ssrn',
        'cambridge',
        'merriam-webster'
        # Add other specific domains as needed
    ]

    # Build the exclusion part of the query
    exclusion_query = ' '.join([f'-site:{domain}' for domain in excluded_domains])
    country_list = ["Nigeria", "Ghana", "Kenya", "South Africa", "Uganda", "Tanzania", "Nepal", "India", "Bangladesh", "Pakistan",
     "Sri Lanka", "Philippines", "Indonesia", "Malaysia", "Thailand", "Vietnam", "Cambodia", "Myanmar", "Laos", "China",
     "Mongolia", "North Korea", "South Korea", "Japan", "Taiwan", "Hong Kong", "Macau", "Singapore", "Brunei",
     "Timor-Leste"]
    for location_filter in ["India"]:

        # Initialize Selenium WebDriver
        driver = initialize_selenium()
        # if driver is None:
        #     logger.critical("Selenium WebDriver initialization failed. Exiting.")
        #     exit(1)
        #
        # # Construct the final search query
        # query = ' OR '.join(search_terms) + f' AND {location_filter} {exclusion_query}'
        #
        # logger.info(f"Constructed search query: {query}")
        #
        # # Perform Google Search
        # search_results = fetch_all_results(query, API_KEY, SEARCH_ENGINE_ID, max_results=30)
        # logger.info(f"Retrieved {len(search_results)} search results.")
        #
        # new_urls = [item.get('link') for item in search_results if item.get('link')]
        # urls = new_urls
        # urls = get_new_urls(new_urls)
        # logger.info(f"Found {len(new_urls)} new URLs, {len(new_urls)-len(urls)} already in db, processing {len(urls)} urls.")
        urls_from_files = get_unique_urls_from_csvs('csv', 'url', 4, 1000)
        urls_from_db = pd.DataFrame(db.search_urls(limit=1000000))['url'].tolist()
        urls= list(set(urls_from_files) - set(urls_from_db))
        for url in urls:
            # Check accessibility before processing
            if not is_url_accessible(url):
                logger.warning(f"URL not accessible: {url}")
                # Record the URL in the database as inaccessible.
                # Set accessible to 0 and leave content empty.
                result = {
                    "url": url,
                    "domain_name": tldextract.extract(url).domain,
                    "source": "google_search",
                    "content": "",  # No content because URL is inaccessible
                    "actual_incident": -1,  # Use a default status (or -2) indicating not processed
                    "accessible": 0
                }
                db.insert_url(result)
                continue

            logger.info(f"Processing URL: {url}")
            extracted = tldextract.extract(url)
            domain_name = extracted.domain

            # Attempt to load the URL with retries
            success = fetch_url_with_retries(driver, url)
            if not success:
                # Even if retries failed, record the URL as inaccessible
                result = {
                    "url": url,
                    "domain_name": domain_name,
                    "source": "google_search",
                    "content": "",
                    "actual_incident": -1,
                    "accessible": 0
                }
                db.insert_url(result)
                continue

            # Extract Main Text
            text = extract_main_text_newspaper(url)

            # Build the record dictionary. Note that 'accessible' is 1 if text was successfully extracted.
            result = {
                "url": url,
                "domain_name": domain_name,
                "source": "google_search",
                "content": text,
                "actual_incident": -1,  # default value until verified
                "accessible": 1  # accessible if we reached this point
            }
            if text:
                try:
                    documents = [Document(text=text)]
                    index = VectorStoreIndex.from_documents(documents)
                    memory.reset()
                    chat_engine = index.as_chat_engine(
                        chat_mode="context",
                        llm=llm,
                        memory=memory,
                        system_prompt=(
                            "You are a career forensic analyst with deep insight into crime and criminal activity, especially human trafficking. "
                            "Your express goal is to investigate online reports and extract pertinent factual detail."
                        )
                    )
                    incident_type, incidents = verify_incident(url, chat_engine)
                    result.update(incident_type)
                    db.insert_url(result)
                    url_id = db.get_url_id(url)
                    if result.get("actual_incident") == 1:
                        for incident in incidents:
                            db.insert_incident(url_id, incident)
                            logger.info(f"Inserted incident: {incident}")
                        suspects = upload_suspects(url, chat_engine)
                        victims = upload_victims(url, chat_engine)
                except Exception as e:
                    logger.error(f"Error processing URL {url}: {e}")
            else:
                logger.warning(f"No text extracted from URL: {url}")
                # Even if text extraction fails, record the URL as inaccessible.
                result["accessible"] = 0
                db.insert_url(result)

            time.sleep(random.uniform(1, 3))

        # Clean Up
        driver.quit()
        logger.info("Google Miner service completed successfully.")

if __name__ == "__main__":
    main()
