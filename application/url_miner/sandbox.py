from work_with_db import URLDatabase, DatabaseError
import pandas as pd
from typing import List, Optional, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
import os
import json
import logging
from tldextract import tldextract
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
# from google_miner import logger
from models import (
    IncidentResponse,
)
from get_urls_from_csvs import get_unique_urls_from_csvs
from work_with_db import URLDatabase, DatabaseError
import pandas as pd
db=URLDatabase()
df=pd.DataFrame(db.search_urls(limit=1000000))
df['url'].tolist()
import sqlite3
db_path = os.getenv("HTDB_PATH")




saved_urls_generic_search_20250131_110058 = pd.read_csv('csv/saved_urls_generic_search_20250131_110058.csv')
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
len(get_new_urls(saved_urls_generic_search_20250131_110058['url'].tolist()))
l=db.search_urls()

urls = get_unique_urls_from_csvs('csv','url',4,1000)

llm = OpenAI(temperature=0, model="gpt-4o-mini", request_timeout=120.0)
memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
from newspaper import Article
url='https://www.ijm.ca/news/over-a-decade-of-partnership-with-the-philippines-history-of-ijm-canada-philippines-relationship'
def extract_main_text_newspaper(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        logger.error(f"Error extracting text with newspaper from {url}: {e}")
        return ""
text = extract_main_text_newspaper(url)
logging.basicConfig(
    filename="google_miner.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
logger.info("Google Miner service started (refactored, sync version).")



db=URLDatabase()
db.create_urls_table()
db.get_column_names('urls')
SHORT_PROMPTS = {
    "incident_prompt": (
        "Assistant, please indicate if it can be said with certainty that this article is a factual report of an "
        "actual incident of human trafficking or any closely associated crime."
        "Return your answer in the following JSON format:\n"
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
        "Assistant, please indicate if the suspect(s) are named explicitly in this article. "
        "If yes, provide the suspects(s) by name. "
        "Return your answer in the following JSON format:\n"
        "{\n"
        '  "answer": "yes" or "no",\n'
        '  "evidence": ["suspect1", "suspect2", "suspect3"] or null\n'
        "}"
    ),
}


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


# URL = st.text_input("Enter Article URL", key="search_url")
def extract_main_text_selenium(driver, url: str) -> str:
    """
    Extracts the main text from a given URL using Selenium.

    Args:
        url (str): The URL of the article to extract.

    Returns:
        str: The main text of the article.
    """
    try:


        # Adjust the CSS selector based on the website's structure
        try:
            article_body = driver.find_element("css selector", "div.detail-content")
            text = article_body.text
            logger.info("Main article content extracted successfully.")
        except Exception:
            # Fallback to extracting all body text
            text = driver.find_element("tag name", "body").text
            logger.warning(
                "Specific article content not found; extracted entire body text."
            )


        return text
    except Exception as e:
        logger.error(f"Selenium extraction failed for URL {url}: {e}")
        return ""



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

def upload_incidents(url: str, chat_engine):
    """
    Uploads incidents to Neo4j and Google Sheets based on user input.

    Args:
        url (str): The URL of the analyzed article.
        chat_engine:
    """
    db = URLDatabase()
    try:
        # Send prompt to chat engine
        prompt_key = "incident_prompt"
        prompt_text = SHORT_PROMPTS[prompt_key]
        response_data = get_validated_response(
            prompt_key, prompt_text, IncidentResponse, chat_engine
        )
        logger.info(f"Received response data: {response_data}")
        if response_data is None:
            return False
        if response_data.answer.lower() == "yes":
            incidents = response_data.evidence or []
            db.update_field(url, 'actual_incident', 1)
            for incident in incidents:
                parameters = {"evidence": incident, "url": url}
                logger.info(f"Uploading incident with parameters: {parameters}")
                # execute_neo4j_query(neo4j_query, parameters)
            return True
        else:
            parameters = {"url": url}

            # execute_neo4j_query(neo4j_query, parameters)
            logger.info(f"Uploading incident with parameters: {parameters}")
            return False

    except Exception as e:
        logger.error(f"Failed to upload incidents: {e}")


df = pd.read_csv('../../../url_miner/output/saved_urls_generic_search_20250124_120904.csv')
driver = initialize_selenium()
urls = df['url'].tolist()
url = urls[1]
for url in urls:
    extracted = tldextract.extract(url)
    domain_name = extracted.domain
    db.insert_url({"url": url, "domain_name": domain_name, "source": "google_miner"})

for url in urls:
    driver.get(url)
    driver.implicitly_wait(10)  # seconds
    text = extract_main_text_selenium(driver, url)
    try:
        db.update_content(url, text)
        logger.info(f"Saved URL to database: {url}")
    except DatabaseError as e:
        logger.error(f"Error saving URL to database: {e}")

config = load_config("search_config.json")


import datetime
db.search_urls(date_from=datetime.datetime(2025,1,24).isoformat())
datetime.datetime.now().isoformat()
datetime.datetime(2025,1,24).isoformat()
datetime().isoformat()
db_search_urls = db.search_urls()
db_search_urls[0]
df=pd.DataFrame(db_search_urls, columns=['id', 'url', 'extracted_date', 'content', 'domain_name', 'source'])
df['url']==url[1]
df = df[~df['content'].isna()]
for i,row in df[:50].iterrows():
    print(row['content'])
    text = row['content']
    url = row['url']


    # Create Document for LlamaIndex
    documents = [Document(text=text)]

    try:
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
        logger.info("Chat engine initialized successfully.")
        # upload_article_metadata(url, chat_engine)
        upload_incidents(url, chat_engine)
        # upload_crimes(url, chat_engine)
        # suspects = upload_suspects(url, chat_engine)
        # Create suspect form
        # victims = upload_victims(url, chat_engine)
        # for suspect in suspects:
        #     create_suspect_form(url, suspect, chat_engine)
    except Exception as e:
        logger.error(f"Failed to initialize chat engine: {e}")
        logger.error(f"Failed to process URL: {url}")

