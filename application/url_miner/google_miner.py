#!/usr/bin/env python3
"""
Module for targeted news article search and filtering related to trafficking incidents.

Refactored to exclude async usage and concurrency references.

Usage:
    python google_miner.py --days_back 7
"""
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
)
# ------------------------------
# Configuration Loading & Logger Setup
# ------------------------------
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
        "Suspects has to be natural persons that is, the NAME (firstname and/or secondname of suspect) of a person, not organizations or any other entities. Exclude cases involving allegations and cases involving \
         politicians or celebrities or ANY other sensational reports or reporting"
        "If yes, provide the suspects(s) by name. EXCLUDE ALL other detail and ONLY provide the GIVEN NAME of the suspect(s)."
        "Return your answer in the following RAW JSON format ONLY and NO back ticks and with no code blocks:\n"
        "{\n"
        '  "answer": "yes" or "no",\n'
        '  "evidence": ["firstname and/or secondname of suspect1", '
        '"firstname and/or secondname of suspect2", "firstname and/or secondname of suspect3", ...] or null\n'
        "}"
    ),
}
llm = OpenAI(temperature=0, model="gpt-4o", request_timeout=120.0)
memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

logging.basicConfig(
    filename="google_miner.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
logger.info("Google Miner service started (refactored, sync version).")


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

def load_config(config_path: str) -> dict:
    """
    Load configuration from a JSON file.

    Args:
        config_path: Name of or path to the configuration file

    Returns:
        dict: Loaded configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file isn't valid JSON
    """
    # Look for config in current directory
    current_dir = os.getcwd()
    full_path = os.path.join(current_dir, config_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Configuration file not found: {full_path}")

    try:
        with open(full_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in config file: {str(e)}", e.doc, e.pos)



config = load_config("search_config.json")

logging.basicConfig(
    filename="google_miner.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
logger.info("Google Miner service started (refactored, sync version).")

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
        return driver

    except Exception as e:
        logger.error(f"Failed to initialize Selenium WebDriver: {e}")
        return None

def save_to_db(urls: List[str]) -> None:
    """
    Save filtered articles to a SQLite database.
    """
    db = URLDatabase()
    driver = initialize_selenium()

    for url in urls:
        extracted = tldextract.extract(url)
        domain_name = extracted.domain
        driver.get(url)
        driver.implicitly_wait(10)  # seconds
        text = extract_main_text_selenium(driver, url)
        try:
            db.insert_url({"url": url, "domain_name": domain_name, "source": "google_miner", "content": text})
            logger.info(f"Saved URL to database: {url}")
        except DatabaseError as e:
            logger.error(f"Error saving URL to database: {e}")

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
        f"Assistant, carefully extract the following detail for {suspect} from the text: "
        "1. Gender,"
        "2. Date of Birth,"
        "3. Age,"
        "4. Address Notes (any address/city/location associated with them would be stored here just as text)"
        "5. Phone number,"
        "6. Nationality,"
        "7. Occupation,"
        "8. Role: Recruiter, Transporter, Master, Facilitator, Boss Trafficker, Host, Other [other role must still be their role in trafficking, not general job posting]"
        "9. Suspect Appearance,"
        "10. Suspect Vehicle Description,"
        "11. Vehicle Plate #,"
        "12. What is evident of the suspect from the article:Definitely trafficked many people, Has trafficked some people, Suspect s/he's a trafficker, Don't believe s/he's a trafficker"
        "13. Arrested status? Yes - in police custody, Yes - but has been released (not on bail), Yes - but released on bail, No"
        "14. Arrest Date,"
        "15. Crime(s) Person Charged With,"
        "16. Yes, willing (list PV names): A list of any PVs that seem willing to testify against the suspect"
        "17. Suspect in police custody,"
        "18. Suspect's current location,"
        "19. Suspect's last known location (location text),"
        "20. Suspect's last known location date (date)"
        " Please return your answer in the following RAW JSON format ONLY and NO back ticks and NO code blocks, e.g.:\n"
        '{"gender": "male", "female" or null,\n'
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
            if url_id is None:
                logger.error(f"URL not found in database: {url}")
                return

            # Insert the data into the suspect_forms table
            db.insert_suspect_form(url_id, response_data)

            logger.info(f"Successfully inserted suspect form for suspect: {suspect}")

    except Exception as e:
        logger.error(f"Failed to populate suspect_forms table for suspect '{suspect}' from URL '{url}': {e}")


def confirm_natural_name(name):
    """
    Confirm if the provided name is a natural person's name.

    Args:
        name (str): The name to confirm.
        chat_engine:
    """
    try:

        prompt_text = (f"Assistant, is '{name}' the GIVEN name natural person? \
        Return your ANSWER in the following RAW JSON format ONLY and WITHOUT backticks:\n\""
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
    Uploads suspects to sqlite.

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
# ------------------------------
# Main Entry Point (Synchronous)
# ------------------------------
def main() -> None:

    # Override days_back from command-line if provided.
    db = URLDatabase()
    db.create_suspect_table()
    db.create_suspect_forms_table()
    db.create_incidents_table()

    driver = initialize_selenium()
    for search_config in config.get('run_configs', []):
        search_config['days_back'] = 1 #args.days_back

        searcher = TraffickingNewsSearch(search_config)
        urls = searcher.get_recent_articles(max_results=50)
        # urls = spoof_articles('../../../url_miner/output/saved_urls_generic_search_20250128_080112.csv')
        logger.info(f"Retrieved {len(urls)} articles in the past {search_config['days_back']} day(s).")
        if not urls:
            logger.info("No articles found for this configuration.")
            continue

        for url in urls:
            logger.info(f"Found article: {url}")
            extracted = tldextract.extract(url)
            domain_name = extracted.domain
            driver.get(url)
            driver.implicitly_wait(10)  # seconds
            text = extract_main_text_selenium(driver, url)
            result = {"url": url, "domain_name": domain_name, "source": "google_miner", "content": text}
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
                    if result["actual_incident"] == 1:
                        for incident in incidents:
                            db.insert_incident(url, incident)
                            logger.info(f"Inserted incident: {incident}")
                        suspects = upload_suspects(url, chat_engine)

                except Exception as e:
                    logger.error(f"Error processing URL {url}: {e}")
        else:
            logger.warning(f"No text extracted from URL: {url}")






if __name__ == "__main__":
    main()
