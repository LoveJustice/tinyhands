#!/usr/bin/env python3
"""
Module for targeted news article search and filtering related to trafficking incidents.

Refactored to exclude async usage and concurrency references.

Usage:
    python google_miner.py --days_back 7
"""
import csv
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from urllib.parse import urlparse
import tldextract
from googlesearch import search  # Ensure you are using the correct googlesearch package.
import json
import os
from libraries.neo4j_lib import execute_neo4j_query
from libraries.work_with_db import URLDatabase, DatabaseError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from libraries.trafficking_news import TraffickingNewsSearch, extract_main_text_selenium
from libraries.models import (
    Age,
    ArticleMetaData,
    CaseNotesResponse,
    CountryResponse,
    ConfirmResponse,
    CrimeDateResponse,
    CrimeResponse,
    Gender,
    IncidentResponse,
    LocationResponse,
    PersonResponse,
    PlacenameResponse,
    PublishedDateResponse,
    SuspectFormResponse,
    SuspectOriginResponse,
    SuspectResponse,
    VictimDestinationResponse,
    VictimOriginResponse,
    VictimResponse,
)
# ------------------------------
# Configuration Loading & Logger Setup
# ------------------------------
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
    Uploads incidents to the database and optionally to Neo4j and Google Sheets based on user input.

    Args:
        url (str): The URL of the analyzed article.
        chat_engine: The chat engine instance used for processing.
    """
    db = URLDatabase()
    result = {}
    incidents = []
    try:
        # Send prompt to chat engine
        prompt_key = "incident_prompt"
        prompt_text = SHORT_PROMPTS[prompt_key]
        response_data = get_validated_response(
            prompt_key, prompt_text, IncidentResponse, chat_engine
        )
        logger.info(f"Received response data: {response_data}")
        if response_data is None:
            # Broken or None return
            logger.warning(f"Received a broken or None response for URL: {url}")
            result["actual_incident"]=-2
            return result, incidents

        if response_data.answer.lower() == "no":
            # Valid response with "no"
            logger.info(f"No incident for URL: {url}")
            db.update_field(url, "actual_incident", 0)
            result["actual_incident"] = 0
            return result, incidents

        if response_data.answer.lower() == "yes":
            # Valid response with "yes"
            logger.info(f"Incident detected for URL: {url}")
            result["actual_incident"] = 1

            # Insert incidents into the incidents table
            incidents = response_data.evidence or []
            return result, incidents

        # Handle unexpected cases
        logger.warning(f"Unexpected response answer for URL: {url} - {response_data.answer}")
        db.update_field(url, "actual_incident", -2)  # Use -2 for unexpected answers


    except Exception as e:
        logger.error(f"Failed to upload incidents for URL {url}: {e}")
        return result, incidents

# ------------------------------
# Main Entry Point (Synchronous)
# ------------------------------
def main() -> None:

    # Override days_back from command-line if provided.
    db = URLDatabase()
    driver = initialize_selenium()
    for search_config in config.get('run_configs', []):
        search_config['days_back'] = 1 #args.days_back

        searcher = TraffickingNewsSearch(search_config)
        urls = searcher.get_recent_articles()

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
            prompt_key = "incident_prompt"
            prompt_text = SHORT_PROMPTS[prompt_key]
            response_data = get_validated_response(
                prompt_key, prompt_text, IncidentResponse, chat_engine
        )
        # Uncomment the next line if you wish to store into Neo4j:
        # searcher.save_to_neo4j(articles)

        # searcher.save_to_csv(articles)
        # searcher.save_to_db(articles)

if __name__ == "__main__":
    main()
