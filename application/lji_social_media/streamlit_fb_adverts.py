import streamlit as st
from typing import List, Dict, Optional
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd
import gspread
from st_pages import Page, Section, add_page_title, show_pages, show_pages_from_config

import json
from urllib.parse import urlparse, parse_qs
import os
import subprocess
from random import randint
import re
from bs4 import BeautifulSoup, Tag
from py2neo import Graph
import random
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from libraries.neo4j_lib import execute_neo4j_query
from dotenv import load_dotenv
from collections import namedtuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import libraries.search_patterns as sp
import logging
from selenium.webdriver import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


# extract_post_id
# find_comments_expanded
# extract_comment_info
# extract_comment_id
# find_advert_content
# find_group_name
# find_advert_poster
# snapshot


# Named tuple for structured return
PosterInfo = namedtuple("PosterInfo", ["poster", "commenters"])
load_dotenv()
neo4j_config = {
    "username": os.environ.get("NEO4J_USER"),
    "password": os.environ.get("NEO4J_PWD"),
    "uri": "bolt://localhost:7687",
}

# Environment variable fetching and error handling
neo4j_url = os.environ.get("NEO4J_URL")
neo4j_usr = os.environ.get("NEO4J_USR", "neo4j")  # Default to 'neo4j' if not set
neo4j_pwd = os.environ.get("NEO4J_PWD")

if not all([neo4j_url, neo4j_usr, neo4j_pwd]):
    raise EnvironmentError("Required NEO4J environment variables are not set.")

# Initialize Graph
graph = Graph(neo4j_url, user=neo4j_usr, password=neo4j_pwd)

import social_media.social_media as sm

from datetime import datetime
from pathlib import Path


# Define your directory and file paths
DIR_PATH = Path("data_sources")

# Check if the directory exists, if not, create it
if not DIR_PATH.exists():
    os.makedirs(DIR_PATH)

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SCOPES = [os.getenv("SCOPES")]
DB_PATH = os.getenv("DB_PATH")


CREDENTIALS = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
SERVICE = build("sheets", "v4", credentials=CREDENTIALS)

LIMIT_EXTRACT_COMMENTS = 3
GOOGLE_SPREADSHEET_NAME = st.secrets["sheets"]["links"]
GOOGLE_SHEET_NAME = "Sheet1"
SCROLL_SLEEP_TIME = 5
WAIT_TIME = 10
CREDS_DICT = st.secrets["face_matcher"]
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
LIMIT_EXTRACT_POSTS = 3
MAX_DIVS_PROCESSED = 2

log_directory = "log"
os.makedirs(log_directory, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_directory, "scraper.log"),
    level=logging.INFO,  # Change this line to DEBUG to see more messages
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Logging setup
log_directory = "log"
os.makedirs(log_directory, exist_ok=True)
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    filename=os.path.join(log_directory, "scraper.log"),
    level=log_level,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def return_ajax_requests():
    # Get the driver from session state
    driver = st.session_state["driver"]

    # Get the current URL
    page_url = driver.current_url

    # Enable network interception
    driver.execute_cdp_cmd("Network.enable", {})

    # Navigate to the page (if not already there)
    driver.get(page_url)

    # Wait for a short time to allow requests to complete
    time.sleep(2)

    # Capture requests
    requests = driver.execute_cdp_cmd("Network.getAllCookies", {})

    # Disable network interception
    driver.execute_cdp_cmd("Network.disable", {})

    # Filter and process AJAX requests
    ajax_requests = []
    for request in requests["cookies"]:
        if request.get("httpOnly"):  # This is often a characteristic of AJAX requests
            ajax_requests.append(
                {
                    "name": request["name"],
                    "value": request["value"],
                    "domain": request["domain"],
                    "path": request["path"],
                }
            )

    return ajax_requests


def return_iframes(driver):
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"Number of iframes found: {len(iframes)}")

    if iframes:
        for i, iframe in enumerate(iframes):
            st.write(f"Switching to iframe {i}")
            driver.switch_to.frame(iframe)
            print_all_text(driver)
            driver.switch_to.default_content()


def print_all_text(driver):
    elements = driver.find_elements(By.XPATH, "//*[string-length(text()) > 0]")
    for element in elements:
        print(element.text)


def get_shadow_dom_content(driver):
    script = """
    function getAllShadowContent(element) {
        var result = '';
        if (element.shadowRoot) {
            result += element.shadowRoot.textContent;
            for (var child of element.shadowRoot.children) {
                result += getAllShadowContent(child);
            }
        }
        for (var child of element.children) {
            result += getAllShadowContent(child);
        }
        return result;
    }
    return getAllShadowContent(document.body);
    """
    return driver.execute_script(script)


def find_aria_labels(driver):
    elements = driver.find_elements(By.XPATH, "//*[@aria-label]")
    for element in elements:
        print(f"Aria-label: {element.get_attribute('aria-label')}")


def find_hidden_elements(driver):
    script = """
    return Array.from(document.querySelectorAll('*'))
        .filter(el => window.getComputedStyle(el).display === 'none' && el.textContent.trim() !== '')
        .map(el => el.textContent);
    """
    hidden_texts = driver.execute_script(script)
    for text in hidden_texts:
        print(f"Hidden text: {text}")


def find_time_related_attributes(driver):
    script = """
    return Array.from(document.querySelectorAll('*'))
        .filter(el => el.attributes.length > 0)
        .flatMap(el => Array.from(el.attributes)
            .filter(attr => attr.name.toLowerCase().includes('time') || attr.value.toLowerCase().includes('time'))
            .map(attr => ({element: el.tagName, attribute: attr.name, value: attr.value})));
    """
    time_attributes = driver.execute_script(script)
    for attr in time_attributes:
        print(
            f"Element: {attr['element']}, Attribute: {attr['attribute']}, Value: {attr['value']}"
        )


def find_timestamp(driver):
    try:
        # Wait for the page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Look for elements that might contain the timestamp
        timestamp_elements = driver.find_elements(
            By.XPATH,
            "//span[contains(@class, 'x1i10hfl') and string-length(text()) > 0]",
        )

        for element in timestamp_elements:
            try:
                # Hover over the element
                ActionChains(driver).move_to_element(element).perform()

                # Wait for a short time to allow the tooltip to appear
                time.sleep(1)

                # Look for the tooltip
                tooltip = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@role='tooltip']"))
                )

                # Extract the text from the tooltip
                tooltip_text = tooltip.get_attribute("textContent")
                st.write(tooltip_text)

                if tooltip_text and any(
                    day in tooltip_text
                    for day in [
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                        "Sunday",
                    ]
                ):
                    return tooltip_text.strip()
            except:
                continue

        return "Detailed timestamp not found"
    except Exception as e:
        return f"Error finding timestamp: {str(e)}"


def wait_for_element_by_id(driver, element_id, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, element_id))
    )


def is_valid_name(name):
    words = name.lower().split()
    return len(words) > 1 and len(set(words)) > 1


def save_results(filename, results):
    # Convert the Path to a string if necessary
    logging.info(f"Saving results to: {filename}")
    Path("results").mkdir(parents=True, exist_ok=True)

    if isinstance(filename, Path):
        filename = str(filename)

    # If the file already exists, read the existing data
    if Path(filename).exists():
        with open(filename, "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    # Update the existing data with the new results
    existing_data.update(results)

    # Write the data back to the file
    with open(filename, "w") as f:
        json.dump(existing_data, f, indent=4)


def clean_filename(filename, replacement="_"):
    """
    Clean the filename by replacing all disallowed characters with a replacement character.

    Args:
        filename (str): The filename to clean.
        replacement (str): The character to replace disallowed characters with.

    Returns:
        str: The cleaned filename.
    """
    logging.info(f"Cleaning filename: {filename}")
    disallowed_chars = ["\0", "/", "\\", "?", "%", "*", ":", '"', "<", ">", "|"]

    for char in disallowed_chars:
        filename = filename.replace(char, replacement)
    logging.info(f"Cleaned filename: {filename}")

    return filename


def get_source_name(driver, timeout=10):
    """
    Extracts the profile name from the current page of the driver.
    Waits for dynamic content to load and handles possible errors.

    :param driver: WebDriver instance
    :param timeout: Time in seconds to wait for an element to load
    :return: Dictionary containing the source profile name and page URL
    """
    try:
        # Wait for the page elements to load
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "x1heor9g"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Navigating through the nested div structure to find the h1 tag
        outer_div = soup.find(
            "div",
            class_="x78zum5 x15sbx0n x5oxk1f x1jxijyj xym1h4x xuy2c7u x1ltux0g xc9uqle",
        )
        if outer_div:
            h1_tag = outer_div.find("h1", class_="x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz")
            if h1_tag:
                source_name = h1_tag.get_text(strip=True)
            else:
                source_name = "Source Name Not Found"
        else:
            source_name = "Source Name Not Found"

        return source_name

    except TimeoutException:
        logging.info("Timed out waiting for page to load")
        return "Loading Failed"

    except NoSuchElementException:
        logging.info("The necessary element was not found on the page")
        return "Element Not Found"

    except Exception as e:
        logging.info(f"An error occurred: {e}")
        return "Error Occurred"


def find_profiles(driver):
    """
    Extracts profile information including work or education details, and the source name from the current page of the driver.
    Additionally, extracts the name of the source profile.

    :param driver: WebDriver instance
    :return: Dictionary containing the source profile name, profile URLs, names, work/education details, and extraction datetime
    """
    current_datetime = datetime.now().strftime("%Y%m%d %H:%M:%S")
    source_name = get_source_name(driver, timeout=10)
    page_url = driver.current_url
    soup = BeautifulSoup(driver.page_source, "html.parser")
    profile_containers = soup.find_all(
        "div",
        class_="x1iyjqo2 x1pi30zi",  # Adjust this class to match the container of the profiles
    )

    links_with_details = []
    for container in profile_containers:
        link_tag = container.find(
            "a",
            class_="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv",
        )

        if link_tag:
            name = (
                link_tag.find("span").get_text(strip=True)
                if link_tag.find("span")
                else ""
            )
            # Assuming work/education detail extraction remains the same or adjust accordingly.
            work_div = container.find(
                "div", class_="x1gslohp"
            )  # Update this class if necessary
            work_text = work_div.get_text(strip=True) if work_div else ""
            links_with_details.append((link_tag["href"], name, work_text))

    profiles = {
        "source_url": page_url.replace("&sk=friends", "")
        .replace("/friends", "")
        .replace("web.", ""),
        "source_name": source_name,
        "data": links_with_details,
        "datetime": current_datetime,
    }

    return profiles


def follower_profiles_to_graph(profiles):
    """
    Inserts profile data into the Neo4j graph database and returns the count of new and existing profiles.

    :param profiles: Dictionary containing profile data
    :return: Tuple containing the count of existing and new profiles
    """
    profile_dicts = []
    logging.info("Creating results/follower_profile_dicts.csv")
    for profile in profiles["data"]:
        parameters = {
            "source_name": profiles["source_name"],
            "source_url": profiles["source_url"]
            .replace("&sk=friends", "")
            .replace("/friends", "")
            .replace("/followers", "")
            .replace("web.", "")
            .replace("&sk=followers", ""),
            "follower_url": profile[0]
            .replace("&sk=friends", "")
            .replace("/friends", "")
            .replace("/followers", "")
            .replace("web.", "www.")
            .replace("&sk=followers", ""),
            "follower_name": profile[1],
            "work_text": profile[2],
        }
        logging.info(parameters)
        query = """MERGE (p:Profile {url: $source_url, name: $source_name})
MERGE (f:Profile {url: $follower_url, name: $follower_name})
MERGE (w:WorkText {work_text: $work_text})
MERGE (p)<-[:FOLLOWS]-(f)
MERGE (f)-[:HAS_WORK_TEXT]->(w)
WITH p, f
CALL apoc.create.addLabels(p, CASE WHEN NOT 'SourceProfile' IN labels(p) THEN ['SourceProfile'] ELSE [] END) YIELD node as pNode
CALL apoc.create.addLabels(f, CASE WHEN $follower_url = $source_url AND NOT 'FollowerProfile' IN labels(f) THEN ['FollowerProfile'] ELSE [] END) YIELD node as fNode
RETURN pNode, fNode
"""

        graph.run(query, parameters).data()
        profile_dicts.append(parameters)
    pd.DataFrame(profile_dicts).to_csv(
        "results/follower_profile_dicts.csv", index=False
    )
    logging.info("Successfully created results/follower_profile_dicts.csv")


def save_page_usernames(driver, file_path):
    # Use the current URL from the WebDriver
    page_url = driver.current_url

    # Use BeautifulSoup to parse HTML from the WebDriver's page source
    soup = BeautifulSoup(driver.page_source, features="html.parser")

    # Extract all text from the HTML
    text = soup.get_text()

    # Regular expression for names (assuming "First Middle Last" format)
    name_regex = r"\b[A-Z][a-z]+(?: [A-Z][a-z]+){1,2}\b"

    # Find all names using the regular expression
    names = re.findall(name_regex, text)

    # Remove duplicates by converting to a set, then back to a list
    unique_names = list(set(names))

    # Sort the names for better readability
    unique_names.sort()

    # Prepare data for DataFrame
    data = {"URL": [page_url] * len(unique_names), "Name": unique_names}

    # Create a DataFrame
    df = pd.DataFrame(data)

    # If the file does not exist, create it; otherwise, append to it
    try:
        df.to_csv(
            file_path, mode="a", header=not pd.read_csv(file_path).empty, index=False
        )
    except FileNotFoundError:
        df.to_csv(file_path, mode="w", header=True, index=False)

    return df


# Example usage (You need to initialize the WebDriver in your environment)
# service = Service(executable_path)
# options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(service=service, options=options)
# driver.maximize_window()
# driver.implicitly_wait(10)


def kill_all_chromedriver_instances():
    """
    Kills all instances of Chrome WebDriver (chromedriver) on macOS and logs the number of instances closed.
    """
    try:
        # Count the number of running Chrome WebDriver instances
        result = subprocess.run(["pgrep", "-x", "chromedriver"], stdout=subprocess.PIPE)
        num_instances = len(result.stdout.splitlines())

        # Kill all running Chrome WebDriver instances
        subprocess.run(["killall", "chromedriver"])

        # Log the number of instances closed
        logging.info(
            f"{num_instances} instances of Chrome WebDriver have been terminated."
        )
    except Exception as e:
        logging.error(f"Error while terminating Chrome WebDriver instances: {e}")


def click_see_more(driver, delay=randint(13, 26)):
    try:
        # Increase the wait time
        wait_time = 60  # Increase to 60 seconds

        # Check if the page is loaded completely
        logging.info("Checking if the page is loaded completely.")
        logging.debug(
            "Page source right before locating 'See more' buttons: "
            + driver.page_source
        )
        WebDriverWait(driver, wait_time).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Log page source (for debugging)

        # Wait for the "See more" buttons to be visible.
        logging.info("Waiting for 'See more' buttons to be visible.")
        WebDriverWait(driver, wait_time).until(
            EC.visibility_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    "span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft",
                )
            )
        )

        # Find all the "See more" buttons.
        logging.info("Find all the 'See more' buttons.")
        see_more_buttons = driver.find_elements(
            By.CSS_SELECTOR, "span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft"
        )
        logging.info(f"Found {len(see_more_buttons)} 'See more' buttons.")

        # Click each "See more" button with a delay between clicks.
        for button in see_more_buttons:
            # Scroll the button into view
            logging.info("Scrolling button into view.")
            driver.execute_script("arguments[0].scrollIntoView();", button)

            # Wait for the element to be clickable
            logging.info("Waiting for button to be clickable.")
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft",
                    )
                )
            )

            # Try JavaScript click
            try:
                logging.info("Trying JavaScriptclick.")
                driver.execute_script("arguments[0].click();", button)
            except:
                # Use ActionChains to move to the element and click it
                logging.info("Trying ActionChains click.")
                actions = ActionChains(driver)
                actions.move_to_element(button).click(button).perform()

            time.sleep(delay)

    except TimeoutException as e:
        logging.error(f"'See more' buttons not found within {wait_time} seconds: {e}")
        logging.info(f"Timeout Error: {e}")
    except Exception as e:
        logging.error(f"Failed to click on 'See more' button: {e}")
        logging.info(f"Error: {e}")


def extract_comments_gpt():
    try:
        # Get the HTML content of the current page
        html_content = st.session_state["driver"].page_source
    except Exception as e:
        logging.error(f"Failed to retrieve page source: {e}")
        return

    try:
        # Parse the HTML content
        soup = BeautifulSoup(html_content, "html.parser")
    except Exception as e:
        logging.error(f"Failed to parse HTML content: {e}")
        return

    try:
        # Find all the div elements with the specified aria-label attribute
        div_elements = soup.find_all("div", {"aria-label": True, "role": "article"})
    except Exception as e:
        logging.error(f"Failed to find div elements: {e}")
        return

    # Extract information
    for div_element in div_elements:
        try:
            # Extract user_name and time from aria-label
            aria_label = div_element["aria-label"]
            user_name = aria_label.split(" ")[2]
            time = aria_label.split(" ")[4] + " " + aria_label.split(" ")[5]
        except Exception as e:
            logging.error(f"Failed to extract user_name or time: {e}")
            continue

        try:
            # Extract href attribute
            href_element = div_element.find_next("a", href=True)
            href = href_element["href"]
            parts = href.split("/")
            group_id = parts[2]
            user_id = parts[4]
        except Exception as e:
            logging.error(f"Failed to extract href attribute or user_id: {e}")
            continue

        try:
            # Extract comment
            comment_element = div_element.find_next(
                "div", {"class": "xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs"}
            )
            comment = comment_element.text
        except Exception as e:
            logging.error(f"Failed to extract comment: {e}")
            continue

        try:
            # Extract comment_id, post_id, and group_id from URL
            link_element = div_element.find_next("a", href=True, attrs={"href": True})
            link = link_element["href"]

            # Parse the URL
            parsed_url = urlparse(link)

            # Extract group_id and post_id
            path_parts = parsed_url.path.split("/")
            group_id = None
            post_id = None
            if len(path_parts) > 4:
                group_id = path_parts[2]
                post_id = path_parts[4]

            # Extract comment_id
            query_parameters = parse_qs(parsed_url.query)
            comment_id = query_parameters.get("comment_id", [None])[0]

        except Exception as e:
            logging.error(f"Failed to extract comment_id, post_id, or group_id: {e}")
            continue

        # Log the information
        logging.info(
            f"User Name: {user_name}, Time: {time}, Group ID: {group_id}, User ID: {user_id}, Comment: {comment}, Post ID: {post_id}, Comment ID: {comment_id}"
        )


def extract_comments():
    html_content = st.session_state["driver"].page_source

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all the div elements with the specified aria-label attribute
    div_elements = soup.find_all("div", {"aria-label": True, "role": "article"})

    # Extract information
    for div_element in div_elements:
        # Extract user_name and time from aria-label
        aria_label = div_element["aria-label"]
        user_name = aria_label.split(" ")[2]
        time = aria_label.split(" ")[4] + " " + aria_label.split(" ")[5]

        # Extract href attribute
        href_element = div_element.find_next("a", href=True)
        href = href_element["href"]
        parts = href.split("/")
        group_id = parts[2]
        user_id = parts[4]

        # Extract comment
        comment_element = div_element.find_next(
            "div", {"class": "xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs"}
        )
        comment = comment_element.text

        # Extract comment_id, post_id from URL
        link_element = div_element.find_next("a", href=True, attrs={"href": True})
        link = link_element["href"]
        link_parts = link.split("/")
        post_id = link_parts[4]
        comment_id = link.split("comment_id=")[1].split("&")[0]

        # Print the information
        logging.info(
            f"User Name: {user_name}, Time: {time}, Group ID: {group_id}, User ID: {user_id}, Comment: {comment}, Post ID: {post_id}, Comment ID: {comment_id}"
        )

    # Close the WebDriver


def extract_user_ids():
    # Get the HTML content of the current page
    html_content = st.session_state["driver"].page_source

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all the links with the specified format
    links = soup.find_all("a", href=True)

    # Extract user_id's
    for link in links:
        href = link["href"]
        if "/groups/" in href and "/user/" in href:
            # Split the href by slashes and get the user_id
            parts = href.split("/")
            if len(parts) >= 2:
                user_id = parts[-2]
                logging.info(f"User ID: {user_id}")


def get_service_account():
    """
    Authenticate using the JSON key file and return the gspread client.
    """
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            CREDS_DICT, SCOPE
        )
        return gspread.authorize(credentials)
    except Exception as e:
        logging.error("Failed to authenticate with Google Sheets: " + str(e))
        return None


def append_comments(data_dict):
    # Authenticate and get the client
    worksheet = get_sheet(st.session_state["client"], "facebook links", "comments")

    # Extract values from the dictionary in the specified order
    values_to_append = [
        data_dict.get("group", ""),
        data_dict.get("group_id", ""),
        data_dict.get("time", ""),
        data_dict.get("post_id", ""),
        data_dict.get("post_url", ""),
        data_dict.get("user_id", ""),
        data_dict.get("username", ""),
        data_dict.get("comment_by_info", ""),
        data_dict.get("comment_text", ""),
    ]

    # Append the data to the sheet

    try:
        worksheet.append_row(values_to_append)
        logging.info(f"Appended {values_to_append} to the sheet.")
    except gspread.exceptions.APIError as e:
        logging.error(f"Failed to append data to Google Sheets: {e}")
        st.write("Failed to append data to Google Sheets: " + str(e))


def get_sheet(client, spreadsheet_name, sheet_name):
    """
    Open the Google Sheets file and return the sheet if it exists.
    """
    try:
        logging.info(f"Accessing Google Sheets file: {spreadsheet_name}")
        spreadsheet = client.open(spreadsheet_name)
        logging.info(f"Accessing sheet: {sheet_name}")
        return spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        logging.info("WorksheetNotFound: " + sheet_name)
        return None
    except Exception as e:
        st.error("Failed to access the Google Sheets file: " + str(e))
        logging.error("Failed to access the Google Sheets file: " + str(e))
        return None


def clean_sheet_name(sheet_name):
    """
    Clean the sheet name by converting to lowercase and replacing disallowed characters with underscores.

    Args:
        sheet_name (str): The sheet name to clean.

    Returns:
        str: The cleaned sheet name.
    """
    # Convert to lowercase
    sheet_name = sheet_name.lower()

    # List of disallowed characters in sheet names
    disallowed_chars = ["\\", "/", "?", "*", "[", "]", ":"]

    # Replace disallowed characters with underscores
    for char in disallowed_chars:
        sheet_name = sheet_name.replace(char, "_")

    return sheet_name


def create_sheet(client, spreadsheet_name, sheet_name):
    """
    Create a new sheet in the Google Sheets file and return it.
    """
    try:
        spreadsheet = client.open(spreadsheet_name)
        logging.info("Opened the Google Sheets file: " + spreadsheet_name)
        return spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")
    except Exception as e:
        st.error("Failed to create the sheet: " + str(e))
        logging.error("Failed to create the sheet: " + str(e))
        return None


def get_worksheet(client, spreadsheet_name, sheet_name):
    """
    Open the Google Sheet and return the worksheet.
    """
    try:
        return client.open(spreadsheet_name).worksheet(sheet_name)
    except Exception as e:
        st.error("Failed to access the Google Sheet: " + str(e))
        logging.error("Failed to access the Google Sheet: " + str(e))
        return None


def connect_facebook():
    """
    Connect to Facebook and return the driver.
    """
    try:
        st.write("Check your browser!")
        driver = sm.facebook_connect()
        st.session_state["driver"] = driver
        st.session_state["connected"] = True
        st.write("You are now connected!")
        return driver
    except Exception as e:
        st.error("Failed to connect to Facebook: " + str(e))
        return None


def scroll_to_end(
    driver,
    wait_time=10,
    min_sleep=1,
    max_sleep=6,
    target_mean_sleep=1.8,
    chance_of_reverse_scroll=0.1,
    reverse_scroll_factor=0.5,
):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Random scroll length: scroll less than the full height of the page
        scroll_length = random.uniform(0.5, 0.9) * last_height

        # Scroll down part of the way
        driver.execute_script(f"window.scrollTo(0, {scroll_length});")

        # Randomize sleep interval with a mean around target_mean_sleep
        sleep_time = random.triangular(min_sleep, max_sleep, target_mean_sleep)
        time.sleep(sleep_time)

        # Occasionally scroll back up
        if random.random() < chance_of_reverse_scroll:
            reverse_scroll_length = scroll_length - (
                reverse_scroll_factor * last_height
            )
            driver.execute_script(f"window.scrollTo(0, {reverse_scroll_length});")
            time.sleep(random.uniform(min_sleep, max_sleep))

        # Wait to load page
        WebDriverWait(driver, wait_time).until(
            lambda d: d.execute_script("return document.body.scrollHeight")
            > last_height
        )

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same, it's the end of the page
            break

        # Update the last height for next loop
        last_height = new_height

    # Return the final scroll height
    return last_height


def scroll_down(driver, wait_time=10):
    last_height = driver.execute_script("return document.body.scrollHeight")

    # Scroll down to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for the page to load
    try:
        WebDriverWait(driver, wait_time).until(
            lambda driver: driver.execute_script("return document.body.scrollHeight;")
            > last_height
        )
    except TimeoutException:
        # If timed out, the page is likely fully loaded
        return

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        return
    return (last_height, new_height)


def logout(driver):
    """
    Logs out of Facebook by clicking the profile button and then the logout option.
    """
    try:
        # Wait for the profile button to be clickable and click it
        wait = WebDriverWait(driver, 10)
        logging.info("Waiting for profile button...")
        profile_button = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'svg[aria-label="Your profile"]')
            )
        )
        logging.info("Profile button found. Clicking...")
        profile_button.click()

        # Wait for the logout option to be clickable and click it
        logging.info("Waiting for logout option...")
        logout_option = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//span[contains(text(), "Log out")]')
            )
        )
        logging.info("Logout option found. Clicking...")
        logout_option.click()

        logging.info("Successfully logged out of Facebook.")
        # kill_all_chromedriver_instances()

    except Exception as e:
        logging.error(f"Failed to log out of Facebook: {e}", exc_info=True)


def record_time_str():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")
    # Here you can add additional logic for comment-specific processing


def find_advert_poster_inside(
    driver, wait_time: int = 20, sleep_time: int = 5
) -> List[Dict[str, str]]:
    """
    Find the advertisement poster information from the current page.

    Args:
        driver: Selenium WebDriver instance
        wait_time (int): Maximum time to wait for elements to load (default: 20 seconds)
        sleep_time (int): Additional time to wait for JavaScript to run (default: 5 seconds)

    Returns:
        List[Dict[str, str]]: List containing a dictionary with poster information, or an empty list if not found
    """
    try:
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='article']"))
        )
        time.sleep(sleep_time)

        post_container = driver.find_element(By.CSS_SELECTOR, "div[role='article']")
        author_link = post_container.find_element(By.CSS_SELECTOR, "h2 a")

        name = author_link.text
        href = author_link.get_attribute("href")

        logging.info(f"Author found: {name}")
        logging.info(f"Author link: {href}")

        poster_info = sp.extract_poster_info(name, href)

        if poster_info:
            logging.info(f"Extracted: {poster_info}")
            logging.info(f"Final posters list: {[poster_info]}")
            return [poster_info]

        logging.warning("No matching poster found")
        return []

    except (TimeoutException, NoSuchElementException) as e:
        logging.error(f"Element not found: {e}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return []


def extract_names(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    names = []

    # Find all 'a' tags with the long class list
    name_links = soup.find_all(
        "a",
        class_="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 xggy1nq x1a2a7pz xt0b8zv x1hl2dhg xzsf02u x1s688f",
    )

    for link in name_links:
        # Extract text from the span inside the 'a' tag
        name = link.find("span", class_="xt0psk2")
        if name:
            names.append(name.get_text(strip=True))

    return names


def wait_for_element(driver, element_locator):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, element_locator))
    )


def get_advert_details():
    original_url = st.session_state["driver"].current_url


def all_new_adverts_urls():
    parameters = {}
    query = f"""MATCH (posting:Posting)
        WHERE posting.text IS NULL
        RETURN posting.post_id AS post_id, posting.post_url AS post_url LIMIT 22;
        """
    # st.write(parameters)
    result = execute_neo4j_query(query, parameters)
    return result


def all_full_adverts_urls():
    parameters = {}
    query = f"""MATCH (posting:Posting)
        WHERE posting.text IS NOT NULL AND posting.post_id IS NOT NULL
        RETURN posting.post_id AS post_id, posting.post_url AS post_url, posting.text as advert;
        """
    # st.write(parameters)
    result = execute_neo4j_query(query, parameters)
    return result


def get_group_urls():
    parameters = {}
    query = f"""MATCH (group:Group)
        WHERE group.name IS NULL
        RETURN group.group_id as group_id, group.url as group_url;
        """
    # st.write(parameters)
    result = execute_neo4j_query(query, parameters)
    return result


def update_group_name(group_id, group_url, group_name):
    parameters = {"group_id": group_id, "group_name": group_name, "url": group_url}
    query = """MERGE (group:Group {group_id:$group_id, url:$url})
        SET group.name = $group_name
        """
    # st.write(parameters)
    execute_neo4j_query(query, parameters)


def all_comments():
    parameters = {}
    query = f"""MATCH (profile:Profile)-[:MADE_COMMENT]-(comment:Comment)-[:HAS_COMMENT]-(posting:Posting)
        RETURN profile.name  AS profile_name, profile.url AS profile_url, comment.comment_id AS comment_id, comment.url AS comment_url, comment.comment as comment, posting.post_id AS post_id, posting.post_url AS post_url;
        """
    # st.write(parameters)
    result = execute_neo4j_query(query, parameters)
    return result


def write_sheet(tab, data):
    range_name = f"{tab}!A1"  # Adjust based on where you want to start writing

    # Convert DataFrame to list of lists
    values = data.values.tolist()

    # Prepare the request body
    body = {"values": values}

    # Use the Sheets API to write the data
    request = (
        SERVICE.spreadsheets()
        .values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption="RAW",
            body=body,
        )
    )
    request.execute()


def wait_for_link_by_href(driver, href, timeout=10):
    try:
        print(f"Searching {href} ...")
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"a[href='{href}']"))
        )
        print(f"Element {href} found!")
    except Exception as e:
        print(f"An error occurred: {e}")


def find_group_name() -> Optional[str]:
    """Extract the group name from the current page."""
    try:
        soup = BeautifulSoup(st.session_state["driver"].page_source, "html.parser")

        if h1_tag := soup.find("h1"):
            if a_tag := h1_tag.find("a"):
                return a_tag.get_text(strip=True)

        if title_tag := soup.title:
            return title_tag.string.split("|")[0].strip()

        st.warning("Group name could not be found in the HTML content.")
        return None
    except Exception as e:
        st.error(f"An error occurred while extracting group name: {str(e)}")
        return None


def snapshot():
    """Take a snapshot of the current Facebook post and upload to Neo4j."""
    driver = st.session_state["driver"]
    post_id = sp.extract_post_id(driver.current_url)
    if not post_id:
        st.error("Could not extract post ID from the current URL.")
        return

    st.write(f"Post ID: {post_id}")
    posters = sp.find_advert_poster()
    st.write(f"Posters: {posters}")
    advert_text = sp.find_advert_content()
    all_users_and_comments = sp.find_comments_expanded()
    st.write(all_users_and_comments)
    group_name = find_group_name()
    st.write(f"Group name: {group_name}")

    # Upload comments
    for comment in all_users_and_comments:
        parameters = {
            "full_name": comment["name"],
            "name": comment["name"].lower().strip(),
            "post_id": post_id,
            "group_id": comment["group_id"],
            "group_name": group_name,
            "user_id": comment["user_id"],
            "group_url": f"https://www.facebook.com/groups/{comment['group_id']}",
            "user_url": f"https://www.facebook.com/{comment['user_id']}",
            "post_url": f"https://www.facebook.com/groups/{comment['group_id']}/posts/{post_id}",
            "comment_url": f"https://www.facebook.com/groups/{comment['group_id']}/posts/{post_id}/?comment_id={comment['comment_id']}",
            "comment_text": comment["text"],
            "comment_id": comment["comment_id"],
            "advert_text": advert_text,
        }
        st.write(parameters)
        query = """
        MERGE (group:Group {group_id: $group_id, url: $group_url})
        MERGE (profile:Profile {name: $full_name, url: $user_url})
        MERGE (name:Name {full_name: $full_name, name: $name})
        MERGE (posting:Posting {post_id: $post_id, post_url: $post_url})
        MERGE (comment:Comment {comment_id: $comment_id, comment: $comment_text, url: $comment_url})
        MERGE (profile)-[:HAS_PROFILE_NAME]->(name)
        MERGE (group)-[:HAS_POSTING]->(posting)
        MERGE (posting)-[:HAS_COMMENT]->(comment)
        MERGE (profile)-[:MADE_COMMENT]->(comment)
        SET group.name = $group_name
        SET posting.text = $advert_text
        """
        result = execute_neo4j_query(query, parameters)
        st.write(result)

    # Upload poster information
    for poster in posters:
        parameters = {
            "full_name": poster["name"],
            "name": poster["name"].lower().strip(),
            "group_id": poster["group_id"],
            "group_name": group_name,
            "user_id": poster["user_id"],
            "post_id": post_id,
            "group_url": f"https://www.facebook.com/groups/{poster['group_id']}",
            "user_url": f"https://www.facebook.com/{poster['user_id']}",
            "post_url": f"https://www.facebook.com/groups/{poster['group_id']}/posts/{post_id}",
            "advert_text": advert_text,
        }
        st.write(parameters)
        query = """
        MERGE (group:Group {name: $group_name, group_id: $group_id, url: $group_url})
        MERGE (profile:Profile {name: $full_name, url: $user_url})
        MERGE (name:Name {full_name: $full_name, name: $name})
        MERGE (posting:Posting {post_id: $post_id, post_url: $post_url})
        MERGE (profile)-[:HAS_PROFILE_NAME]->(name)
        MERGE (profile)-[:POSTED]->(posting)
        MERGE (group)-[:HAS_POSTING]->(posting)
        SET posting.text = $advert_text
        """
        result = execute_neo4j_query(query, parameters)
        st.write(result)

    st.write("Upload completed.")
    st.write(posters)


def main():
    show_pages(
        [
            Page("streamlit_fb_adverts.py", "Home", "🏠"),
            Page("fb_advert_pages/google_store.py", "Google sheet", "📖"),
            Page("fb_advert_pages/fetch_advert_content.py", "Get adverts", "🔗"),
            Page("fb_advert_pages/groups.py", "Stored groups", "🔗"),
        ]
    )

    if "default_option" not in st.session_state:
        st.session_state["default_option"] = "Please select a post_id"

    if "connected" not in st.session_state:
        st.session_state["connected"] = False

        # Check if the driver is already initialized
    if "driver" not in st.session_state:
        st.session_state["driver"] = None

    if "post_matches" not in st.session_state:
        st.session_state["post_matches"] = []

    if "options" not in st.session_state:
        st.session_state["options"] = None

    if st.button("Connect") and not st.session_state["connected"]:
        # Get the current date and time
        now = datetime.now()
        # Format the date and time as a string
        st.session_state["datetime_key"] = now.strftime("%Y%m%d %H:%M:%S")
        logging.info("Check your browser!")
        kill_all_chromedriver_instances()
        driver = sm.facebook_connect()
        st.session_state["driver"] = driver
        st.session_state["connected"] = True
        logging.info("You are now connected!")

    if st.button("Quit browser"):
        try:
            # Check if the WebDriver instance exists in the session state
            if "driver" in st.session_state and st.session_state["driver"] is not None:
                # Attempt to quit the browser
                st.session_state["driver"].quit()
                st.session_state[
                    "driver"
                ] = None  # Set the driver to None after quitting
                st.session_state["connected"] = False
                st.session_state["page_loaded"] = False
                st.session_state["source_name"] = ""
                st.session_state["source_url"] = ""

                kill_all_chromedriver_instances()
                st.write("Browser closed!")  # Debug message to confirm button press
                logging.info("Browser closed!")
            else:
                st.write("WebDriver instance not found in session state.")
        except Exception as e:
            st.write(f"An error occurred: {e}")
            logging.error(f"An error occurred while trying to quit the browser: {e}")

        # ("Browser closed!")

    if st.session_state["connected"]:
        if st.button("Logout"):
            logout(st.session_state["driver"])
            st.session_state["connected"] = False
            logging.info("Logged out and disconnected.")

        if "selected_option" not in st.session_state:
            st.session_state["selected_option"] = st.session_state[
                "default_option"
            ]  # Default value

        # Assuming list_all_users returns lists of user_ids, comment_matches, and post_matches
        if st.button("list all posts on group page"):
            st.write(st.session_state["driver"].current_url)
            if sm.is_facebook_groups_url(st.session_state["driver"].current_url):
                st.write("list_all_users")
                user_ids, comment_matches, post_matches = sp.list_all_users()
                st.write(user_ids)
                st.write("done list_all_users")
                st.session_state["post_matches"] = post_matches
                st.write("post_matches: ", post_matches)
                st.dataframe(pd.DataFrame(post_matches))
                st.session_state["post_ids"] = [
                    post_match["post_id"] for post_match in post_matches
                ]
                # user_ids.append((group_id, user_id, poster_name))
                # comment_matches.append((group_id, post_id, comment_id))
                # post_matches.append((group_id, post_id))
                st.write(st.session_state["selected_option"])
                st.write(st.session_state["post_ids"])
                # Initialize with a default option
                st.session_state["options"] = [
                    st.session_state["default_option"]
                ] + st.session_state["post_ids"]
                st.write("The URL is a valid Facebook groups URL.")
            else:
                st.write("The URL does not match the required Facebook groups format.")

        if st.session_state["options"]:
            st.selectbox(
                "Select post to scrape:",
                st.session_state["options"],
                index=0,
                key="selected_option",  # This links the selectbox directly to the session state variable
            )

        if st.button("Update group name"):
            current_url = st.session_state["driver"].current_url
            if sm.is_facebook_groups_url(current_url):
                group_name = find_group_name()
                group_id = sp.extract_group_id(current_url)
                st.write(f"Group name: {group_name}, Group ID: {group_id}")
                update_group_name(
                    group_id, st.session_state["driver"].current_url, group_name
                )

        if st.button("Update group URLs"):
            group_urls = get_group_urls()
            # st.write(group_urls)
            for group_url in group_urls:
                st.session_state["driver"].get(group_url["group_url"])

                # Wait for a specific element that indicates the page has loaded
                # wait_for_element(st.session_state["driver"], "mount_0_0_bw")
                wait_for_link_by_href(
                    st.session_state["driver"], group_url["group_url"], timeout=10
                )

                group_name = find_group_name()
                st.write(group_url["group_id"], group_url["group_url"], group_name)

                update_group_name(
                    group_url["group_id"], group_url["group_url"], group_name
                )

        if st.button("Write Graph Comments to GoogleSheet"):
            comments = all_comments()
            comments = pd.DataFrame(comments)
            st.dataframe(comments)
            write_sheet("Comments", comments)

        if st.button("Snapshot"):
            snapshot()

        if st.button("find time stamp"):
            all_text = print_all_text(st.session_state["driver"])
            st.write("all_text:", all_text)
            aria_labels = find_aria_labels(st.session_state["driver"])
            st.write("aria_labels:", aria_labels)
            hidden_elements = find_hidden_elements(st.session_state["driver"])
            st.write("hidden_elements:", hidden_elements)
            time_related_attributes = find_time_related_attributes(
                st.session_state["driver"]
            )
            st.write("time_related_attributes:", time_related_attributes)
            shadow_content = get_shadow_dom_content(st.session_state["driver"])
            st.write("shadow_content: ", shadow_content)
            iframes = return_iframes(st.session_state["driver"])
            st.write("iframes: ", iframes)
            # timestamp = find_timestamp(st.session_state["driver"])
            # st.write(timestamp)
        # Usage in Streamlit
        if st.button("Get AJAX Requests"):
            ajax_requests = return_ajax_requests()
            st.write("AJAX Requests:")
            for request in ajax_requests:
                st.write(f"Name: {request['name']}")
                st.write(f"Domain: {request['domain']}")
                st.write(f"Path: {request['path']}")
                st.write("---")

        if st.button("Scroll to bottom of page"):
            st.session_state.scrolling = True
            try:
                logging.info("Scrolling to end of page!")
                scroll_to_end(
                    st.session_state["driver"],
                    wait_time=20,
                    min_sleep=2.01,
                    max_sleep=9.9,
                    target_mean_sleep=2.609,
                )
            except TimeoutException:
                logging.error(
                    "The elements were not found within the specified timeout."
                )


# This is the standard boilerplate that calls the 'main' function
if __name__ == "__main__":
    main()
