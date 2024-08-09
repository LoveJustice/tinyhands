import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd
import gspread
from st_pages import Page, Section, add_page_title, show_pages, show_pages_from_config
from urllib.parse import urlparse
from typing import Set
from selenium.webdriver.common.action_chains import ActionChains
import json
from urllib.parse import urlparse, parse_qs
import os
import logging
import subprocess
from random import randint
import re
from bs4 import BeautifulSoup
from py2neo import Graph
import random
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from libraries.neo4j_lib import execute_neo4j_query
from dotenv import load_dotenv
from collections import namedtuple

# Constants for regex patterns
GROUP_USER_ID_PATTERN = re.compile(r"/groups/([\w]+)/user/([\w]+)/?")
GROUP_ID_PATTERN = re.compile(r"groups/([\w]+)")
GROUP_POST_ID_PATTERN = re.compile(r"/groups/([\w]+)/posts/([\w]+)/?")
GROUP_COMMENT_ID_PATTERN = re.compile(
    r"groups/([\w]+)/posts/([\w]+)/.*[?&]comment_id=([\w]+)/?"
)

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

from social_media.social_media import (
    facebook_connect,
    find_search_urls,
    find_friend_urls,
)

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


def wait_for_element_by_id(driver, element_id, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, element_id))
    )


def is_facebook_groups_url(url: str) -> bool:
    """
    Check if the given URL is a valid Facebook groups URL.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is a valid Facebook groups URL, False otherwise.
    """
    VALID_DOMAINS: Set[str] = {"www.facebook.com", "web.facebook.com"}
    FORBIDDEN_SEGMENTS: Set[str] = {"user", "comment", "post"}

    try:
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.strip("/").split("/")

        return all(
            [
                parsed_url.scheme == "https",
                parsed_url.netloc in VALID_DOMAINS,
                len(path_segments) >= 2,
                path_segments[0] == "groups",
                not set(path_segments) & FORBIDDEN_SEGMENTS,
            ]
        )
    except Exception:
        return False


def is_valid_name(name):
    words = name.lower().split()
    return len(words) > 1 and len(set(words)) > 1


def extract_group_id(url):
    result = GROUP_ID_PATTERN.search(url)

    if result:
        # Extracted post ID is the second captured group
        group_id = result.group(1)
        return group_id
    else:
        # Return None or raise an error if the URL doesn't .match the expected format
        return None


def extract_post_id(url):
    # Define a regex pattern to match the URL format and capture the post ID
    # pattern = re.compile(r"https://www\.facebook\.com/groups/([\w]+)/posts/([\w]+)")
    # re.compile(r"https://www\.facebook\.com/groups/([\w]+)/posts/([\w]+)"(\d+))

    result = GROUP_POST_ID_PATTERN.search(url)

    if result:
        # Extracted post ID is the second captured group
        post_id = result.group(2)
        return post_id
    else:
        # Return None or raise an error if the URL doesn't .match the expected format
        return None


def find_posts_comments_and_user_ids(soup):
    # Find all 'div', 'p', and 'span' tags
    div_p_tags = soup.find_all(["div", "p"])
    span_tags = soup.find_all("span")

    # Prepare regex for user_id extraction
    # user_id_pattern = re.compile(r"/groups/\d+/user/(\d+)/")

    # Initialize lists to store results
    div_p_texts = []
    span_texts = []

    for tag in div_p_tags:
        text = tag.get_text(strip=True)
        # Find 'a' tags within the current tag
        a_tags = tag.find_all("a", href=True)
        # Extract user_id from the href of each 'a' tag
        for a_tag in a_tags:
            href = a_tag["href"]
            user_id_match = GROUP_USER_ID_PATTERN.search(href)
            if user_id_match:
                user_id = user_id_match.group(1)
                div_p_texts.append((text, user_id))

    for tag in span_tags:
        text = tag.get_text(strip=True)
        # Find 'a' tags within the current tag
        a_tags = tag.find_all("a", href=True)
        # Extract user_id from the href of each 'a' tag
        for a_tag in a_tags:
            href = a_tag["href"]
            user_id_match = GROUP_USER_ID_PATTERN.search(href)
            if user_id_match:
                user_id = user_id_match.group(1)
                span_texts.append((text, user_id))

    return div_p_texts, span_texts


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


def postings_to_neo4j():
    if is_facebook_groups_url(st.session_state["driver"].current_url):
        st.write(
            "Upload all posts on group page to Neo4J:  The URL is a valid Facebook groups URL."
        )
        user_ids, comment_matches, post_matches = list_all_users()
        st.write(f"User IDs: {user_ids}")
        st.write(f"Comment matches: {comment_matches}")
        st.write(f"Post matches: {post_matches}")
        # st.session_state["options"] = [
        #     st.session_state["default_option"]
        # ] + st.session_state["post_ids"]
        for post_match in post_matches:
            st.write(
                f"Post match; group_id: {post_match['group_id']}, post_id: {post_match['post_id']}"
            )
            parameters = {
                "post_id": post_match["post_id"],
                "group_id": post_match["group_id"],
                "group_url": f"https://www.facebook.com/groups/{post_match['group_id']}",
                "post_url": f"https://www.facebook.com/groups/{post_match['group_id']}/posts/{post_match['post_id']}",
            }

            query = f"""MERGE (group:Group {{group_id: $group_id, url: $group_url}})
                        MERGE (posting:Posting {{post_id: $post_id, post_url: $post_url}})
                        MERGE (group)-[:HAS_POSTING]->(posting)
                    """
            # st.write(parameters)
            execute_neo4j_query(query, parameters)
    else:
        st.write("The URL does not match the required Facebook groups format.")


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
        driver = facebook_connect()
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


def scroll_to_upload_postings(
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
        postings_to_neo4j()
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


def make_list_unique(list_of_dicts):
    unique_serialized = {json.dumps(d, sort_keys=True) for d in list_of_dicts}
    unique_list_of_dicts = [json.loads(s) for s in unique_serialized]
    return unique_list_of_dicts


def list_all_users():
    driver = st.session_state["driver"]
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")

    # Define regex patterns for extracting group_id, user_id, and comment_id

    # Assuming the rest of your code structure remains the same

    # Find all 'a' tags with 'href' attribute
    links = soup.find_all("a", href=True)
    post_matches = []
    comment_matches = []
    user_ids = []
    for link in links:
        href = link["href"]
        if "groups" in href:
            user_match = GROUP_USER_ID_PATTERN.search(href)
            post_match = GROUP_POST_ID_PATTERN.search(href)
            comment_match = GROUP_COMMENT_ID_PATTERN.search(href)

            if user_match:
                group_id, user_id = user_match.groups()
                poster_name = link.get_text(strip=True)
                user_ids.append(
                    {
                        "group_id": group_id,
                        "user_id": user_id,
                        "poster_name": poster_name,
                    }
                )

            if comment_match:
                # st.write("href (comment_match): ", href)
                group_id, post_id, comment_id = comment_match.groups()
                comment_matches.append(
                    {"group_id": group_id, "post_id": post_id, "comment_id": comment_id}
                )

            if post_match:
                # st.write("href (post_match): ", href)
                group_id, post_id = post_match.groups()
                # st.write("Post match; group_id: ", group_id, "post_id: ", post_id)
                post_matches.append({"group_id": group_id, "post_id": post_id})

    # user_ids.append((group_id, user_id, poster_name))
    # comment_matches.append((group_id, post_id, comment_id))
    # post_matches.append((group_id, post_id))
    unique_user_ids = make_list_unique(user_ids)
    unique_comment_matches = make_list_unique(comment_matches)
    unique_post_matches = make_list_unique(post_matches)
    return unique_user_ids, unique_comment_matches, unique_post_matches

    # Here you can add additional logic for comment-specific processing


#
# def find_group_name():
#     driver = st.session_state["driver"]
#     html_content = driver.page_source
#     soup = BeautifulSoup(html_content, "html.parser")
#
#     # Example of a simpler selector targeting a smaller, more stable subset of classes
#     class_selector = "a.x1i10hfl.xjbqb8w.x1ejq31n"
#
#     group_link = soup.select_one(class_selector)
#     group_name = group_link.get_text(strip=True) if group_link else "Text not found"
#
#     return group_name


def find_group_name():
    driver = st.session_state["driver"]
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the <h1> tag and then the <a> tag within it
    group_name_tag = soup.find("h1").find("a")

    # Extract the text if the tag is found
    group_name = (
        group_name_tag.get_text(strip=True) if group_name_tag else "Text not found"
    )
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the element containing the job title
    # group_name = soup.find("title").text.strip()
    title_element = soup.title.string

    # Extract and clean the title
    group_name = title_element.split("|")[0].strip()
    return group_name


def find_advert_content():
    try:
        driver = st.session_state["driver"]
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the parent div that contains the message
        message_div = soup.find("div", {"data-ad-comet-preview": "message"})
        if message_div is None:
            raise ValueError("The message div could not be found in the HTML content.")

        # Extract text from each child div within it
        advert_text = " ".join(
            div.get_text(strip=True)
            for div in message_div.find_all("div", recursive=False)
        )
        return advert_text

    except Exception as e:
        st.error(f"An error occurred in find_advert_content: {e}")
        # Depending on the context, you may want to return an empty string,
        # None, or re-raise the exception after logging it.
        return ""


def extract_poster_info(driver):
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    poster_info = []

    try:
        for link in soup.find_all("a", class_=["x1i10hfl", "xjbqb8w"]):
            href = link.get("href", "")
            match = GROUP_USER_ID_PATTERN.search(href)
            if match:
                group_id, user_id = match.groups()
                name = (
                    link.get_text(strip=True)
                    or link.find_next_sibling(text=True, strip=True)
                    or "N/A"
                )
                poster_info.append(
                    {"name": name, "group_id": group_id, "user_id": user_id}
                )
    except Exception as e:
        logging.error(f"Error in extract_poster_info: {e}")

    return poster_info


def find_advert_poster_depr():
    try:
        driver = st.session_state["driver"]
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")

        # Find all 'a' elements
        user_links = soup.find_all("a")

        if not user_links:
            st.write("No user links found.")
            return []

        posters = []
        for link in user_links:
            href = link.get("href")
            name = link.get_text(strip=True) if link.get_text(strip=True) else "N/A"
            classes = link.get("class")
            st.write(f"Checking link: {href} with name: {name} and classes: {classes}")

            if not href:
                continue  # Skip if href is None

            # Match group/user pattern
            match_user = GROUP_USER_ID_PATTERN.search(href)
            if match_user:
                group_id, user_id = match_user.groups()
                st.write(
                    f"Match found: Name: {name}, Group ID: {group_id}, User ID: {user_id}"
                )
                posters.append({"name": name, "group_id": group_id, "user_id": user_id})
                continue  # Skip further checks if user ID is found

            # Match group/post pattern
            match_post = GROUP_POST_ID_PATTERN.search(href)
            if match_post:
                group_id, post_id = match_post.groups()
                st.write(
                    f"Match found: Name: {name}, Group ID: {group_id}, Post ID: {post_id}"
                )
                posters.append({"name": name, "group_id": group_id, "post_id": post_id})

        # Remove duplicates by serializing the list of dictionaries to a set of unique JSON strings
        unique_serialized = {json.dumps(d, sort_keys=True) for d in posters}
        posters = [json.loads(s) for s in unique_serialized]

        if not posters:
            st.write("No matches found for the specified patterns.")
        return posters

    except Exception as e:
        st.error(f"An error occurred in find_advert_poster: {e}")
        return []


def find_advert_poster(html_content):
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        posters = {"poster": None, "commenters": []}

        # Debug: Print the structure of the HTML
        print(soup.prettify())

        # Find the main post container (Modify this selector as per your HTML structure)
        post_container = soup.find("div", class_="x1lliihq x1l90r2v")
        print(f"Post container found: {post_container is not None}")

        if post_container:
            # Find the poster link
            poster_link = post_container.find("a", href=GROUP_USER_ID_PATTERN)
            print(f"Poster link found: {poster_link is not None}")
            print(f"Poster link content: {poster_link}")

            if poster_link:
                poster_name_span = poster_link.find("span", class_="xt0psk2")
                print(f"Poster name span found: {poster_name_span is not None}")
                print(f"Poster name span content: {poster_name_span}")

                if poster_name_span:
                    poster_name = poster_name_span.get_text(strip=True)
                    poster_href = poster_link.get("href")
                    match = GROUP_USER_ID_PATTERN.search(poster_href)
                    if match:
                        group_id, user_id = match.groups()
                        posters["poster"] = {
                            "name": poster_name,
                            "group_id": group_id,
                            "user_id": user_id,
                        }
                        print(f"Poster details: {posters['poster']}")
                    else:
                        print("Poster href did not match the pattern.")
                else:
                    print("Poster name span not found.")
            else:
                print("Poster link not found.")

        return posters

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"poster": None, "commenters": []}


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def find_advert_poster_inside():
    try:
        driver = st.session_state["driver"]

        # Wait for the post content to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='article']"))
        )

        # Give additional time for JavaScript to run
        time.sleep(5)

        # Find the post container
        post_container = driver.find_element(By.CSS_SELECTOR, "div[role='article']")

        # Find the author link within the post container
        author_link = post_container.find_element(By.CSS_SELECTOR, "h2 a")

        name = author_link.text
        href = author_link.get_attribute("href")

        st.write(f"Author found: {name}")
        st.write(f"Author link: {href}")

        group_user_match = GROUP_USER_ID_PATTERN.search(href)
        post_match = GROUP_POST_ID_PATTERN.search(href)

        if group_user_match and post_match:
            group_id, user_id = group_user_match.groups()
            _, post_id = post_match.groups()

            st.write(
                f"Extracted: group_id={group_id}, user_id={user_id}, post_id={post_id}"
            )

            posters = [
                {
                    "name": name,
                    "group_id": group_id,
                    "user_id": user_id,
                    "post_id": post_id,
                }
            ]

            st.write("Final posters list:", posters)
            return posters

        st.write("No matching poster found")
        return []

    except Exception as e:
        st.write(f"An error occurred: {e}")
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


def find_comments_expanded():
    driver = st.session_state["driver"]
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")

    # Regex patterns remain unchanged
    # user_href_pattern = re.compile(r"/groups/(\d+)/user/(\d+)/")
    # comment_href_pattern = re.compile(
    #     r"/groups/(\d+)/posts/(\d+)/.*[?&]comment_id=(\d+)"
    # )

    extracted_info = []

    # Assuming 'x1r8uery x1iyjqo2 x6ikm8r x10wlt62 x1pi30zi' uniquely identifies the comment blocks
    parent_elements = soup.find_all(
        "div", class_="x1r8uery x1iyjqo2 x6ikm8r x10wlt62 x1pi30zi"
    )

    for parent_element in parent_elements:
        # Adjusted to find the user link within the nested structure
        user_link = parent_element.find("a", href=GROUP_USER_ID_PATTERN)
        if user_link:
            href = user_link["href"]
            match_user = GROUP_USER_ID_PATTERN.search(href)
            if match_user:
                group_id, user_id = match_user.groups()
                name = user_link.text  # Direct extraction of the user name

                # For text, assume it's directly within a certain class in 'parent_element'
                text_container = parent_element.find(
                    "div", class_="x1lliihq xjkvuk6 x1iorvi4"
                )
                text = text_container.text if text_container else "Text not found"

                # Assuming comment links are also within 'parent_element'
                comment_link = parent_element.find("a", href=GROUP_COMMENT_ID_PATTERN)
                comment_id = "Comment ID not found"
                if comment_link:
                    match_comment = GROUP_COMMENT_ID_PATTERN.search(
                        comment_link["href"]
                    )
                    if match_comment:
                        _, _, comment_id = match_comment.groups()

                extracted_info.append(
                    {
                        "user_id": user_id,
                        "name": name,
                        "text": text,
                        "group_id": group_id,
                        "comment_id": comment_id,
                    }
                )
    unique_serialized = {json.dumps(d, sort_keys=True) for d in extracted_info}

    # Deserialize back to a list of dictionaries
    extracted_info = [json.loads(s) for s in unique_serialized]
    return extracted_info


def find_comments():
    # Your HTML content
    driver = st.session_state["driver"]
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")

    # Regex pattern to extract group_id, user_id, and comment_id from href
    # href_pattern = re.compile(r"/groups/(\d+)/user/(\d+)/")
    # comment_pattern = re.compile(r"/groups/(\d+)/posts/(\d+)/.*[?&]comment_id=(\d+)")

    # List to store extracted information
    extracted_info = []

    # Find all div elements for the new pattern
    new_elements = soup.find_all("div", class_="x1y1aw1k xn6708d xwib8y2 x1ye3gou")

    for element in new_elements:
        # Find the 'a' tag with the user link
        user_link = element.find("a", href=True)
        if user_link:
            href = user_link["href"]
            match = GROUP_USER_ID_PATTERN.search(href)
            if match:
                group_id, user_id = match.groups()
                # Attempt to find the comment_id in a different 'a' tag within the same larger container
                comment_link = element.find("a", href=GROUP_COMMENT_ID_PATTERN)
                comment_id_match = (
                    GROUP_COMMENT_ID_PATTERN.search(comment_link["href"])
                    if comment_link
                    else None
                )
                if comment_id_match:
                    group_id, post_id, comment_id = comment_id_match.groups()
                    # Name extraction
                    name_container = element.find("span", class_="x3nfvp2")
                    name = (
                        name_container.get_text(strip=True)
                        if name_container
                        else "Unknown"
                    )
                    # Extract the text within the div for the comment text
                    text_container = element.find(
                        "div", class_="xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs"
                    )
                    text = (
                        text_container.get_text(strip=True)
                        if text_container
                        else "No text"
                    )
                    extracted_info.append(
                        {
                            "user_id": user_id,
                            "comment": text,
                            "group_id": group_id,
                            "post_id": post_id,
                            "comment_id": comment_id,
                            "name": name,
                        }
                    )

    # Optionally, remove duplicates
    extracted_info = list(set(extracted_info))

    for info in extracted_info:
        st.write(
            f"User ID: {info[0]}, Text: {info[1]}, Group ID: {info[2]}, Post ID: {info[3]}, Comment ID: {info[4]}, Name: {info[5]}"
        )

    return extracted_info


def list_all_users_and_comments():
    driver = st.session_state["driver"]
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, "html.parser")

    # Adjusted patterns if necessary
    # group_user_pattern = re.compile(r"/groups/(\d+)/user/(\d+)/?")
    # group_comment_pattern = re.compile(
    #     r"/groups/(\d+)/posts/(\d+)/.*[?&]comment_id=(\d+)"
    # )

    user_comments = []

    # Assume a more targeted search approach, focusing on the known structure
    # For example, if users and comments are always within a certain div class:
    posts = soup.find_all(
        "div", class_="x1y1aw1k xn6708d xwib8y2 x1ye3gou"
    )  # Adjust class as needed

    for post in posts:
        user_link = post.find("a", href=GROUP_USER_ID_PATTERN)
        if user_link:
            group_id, user_id = GROUP_USER_ID_PATTERN.search(user_link["href"]).groups()
            poster_name = user_link.text.strip()

            # Find the comment link within the same or related structure
            comment_link = post.find("a", href=GROUP_COMMENT_ID_PATTERN)
            if comment_link:
                _, _, comment_id = GROUP_COMMENT_ID_PATTERN.search(
                    comment_link["href"]
                ).groups()

                user_comments.append(
                    {
                        "group_id": group_id,
                        "user_id": user_id,
                        "poster_name": poster_name,
                        "comment_ids": [
                            comment_id
                        ],  # This assumes one comment per post; adjust as needed
                    }
                )

    return user_comments


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


def extract_info():
    html_content = st.session_state["driver"].page_source
    soup = BeautifulSoup(html_content, "html.parser")

    # Compile the regex patterns

    results = []

    # Find all relevant 'a' tags with the specific class for the names
    links = soup.find_all(
        "a",
        class_="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 xggy1nq x1a2a7pz xt0b8zv x1hl2dhg xzsf02u x1s688f",
    )

    for link in links:
        href = link.get("href")
        person_name = link.text.strip()
        user_match = GROUP_USER_ID_PATTERN.search(href)
        group_match = GROUP_ID_PATTERN.search(href)

        if user_match:
            group_id, user_id = user_match.groups()
            results.append(
                {"person_name": person_name, "group_id": group_id, "user_id": user_id}
            )
        elif group_match:
            group_id = group_match.group(1)
            results.append(
                {"person_name": person_name, "group_id": group_id, "user_id": None}
            )

    return results


def wait_for_link_by_href(driver, href, timeout=10):
    try:
        print(f"Searching {href} ...")
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"a[href='{href}']"))
        )
        print(f"Element {href} found!")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    show_pages(
        [
            Page("streamlit_fb_adverts.py", "Home", "🏠"),
            Page("fb_advert_pages/google_store.py", "Google sheet", "📖"),
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
        driver = facebook_connect()
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
            if is_facebook_groups_url(st.session_state["driver"].current_url):
                st.write("list_all_users")
                user_ids, comment_matches, post_matches = list_all_users()
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

        # st.write(st.session_state["options"])
        if st.button("Upload all posts on group page to Neo4J"):
            st.write(st.session_state["driver"].current_url)
            if is_facebook_groups_url(st.session_state["driver"].current_url):
                scroll_to_upload_postings(
                    st.session_state["driver"],
                    wait_time=20,
                    min_sleep=2.01,
                    max_sleep=9.9,
                    target_mean_sleep=2.609,
                    chance_of_reverse_scroll=0.1,
                    reverse_scroll_factor=0.5,
                )
            else:
                st.write("The URL does not match the required Facebook groups format.")

        if st.session_state["options"]:
            st.selectbox(
                "Select post to scrape:",
                st.session_state["options"],
                index=0,
                key="selected_option",  # This links the selectbox directly to the session state variable
            )
            # Initialize variable to None to handle the case where no match is found

            # At this point, group_id_for_selected_option contains the desired group ID or remains None if no match was found

        # Execute the following block if a post has been selected (not the default option)
        if st.button("Scrape selected post..."):
            if st.session_state["selected_option"] != "Please select a post_id":
                try:
                    group_id_for_selected_option = None
                    # Iterate through post_matches and find the first match

                    for post_match in st.session_state["post_matches"]:
                        if post_match["post_id"] == st.session_state["selected_option"]:
                            st.session_state["group_id"] = post_match["group_id"]
                            break  # Exit loop after finding the first match

                    st.write(f"Selected post: {st.session_state['selected_option']}")
                    # Construct the URL for the selected post
                    url = f"https://www.facebook.com/groups/{st.session_state['group_id']}/posts/{st.session_state['selected_option']}"
                    st.write(f"Selected post URL: {url}")

                    # Navigate to the URL
                    st.session_state["driver"].get(url)
                    # Initialize WebDriverWait with the driver and timeout
                    wait = WebDriverWait(st.session_state["driver"], 30)
                    # Wait for the element with ID 'MANIFEST_LINK' to be present
                    element = wait.until(
                        EC.presence_of_element_located((By.ID, "MANIFEST_LINK"))
                    )

                    # Proceed with the rest of your logic only if the above line doesn't raise an exception
                    posters = find_advert_poster()  # [(name, group_id, user_id)]
                    advert_text = find_advert_content()
                    comments = find_comments_expanded()
                    all_users_and_comments = list_all_users_and_comments()
                    st.write(f"Comments: {comments}")
                    st.write(f"All users and comments: {all_users_and_comments}")
                    st.write(f"Advert: {advert_text}")

                except TimeoutException:
                    # Handle the case where the element is not found within the specified time
                    st.error(
                        "Failed to find the required element within the time limit."
                    )

                # Your code to handle the selected option here
                # This part will only execute if a non-default value has been selected
        if st.button("Update group name"):
            current_url = st.session_state["driver"].current_url
            if is_facebook_groups_url(current_url):
                group_name = find_group_name()
                group_id = extract_group_id(current_url)
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
            post_id = extract_post_id(st.session_state["driver"].current_url)
            st.write(f"Post ID: {post_id}")
            posters = find_advert_poster()  # [(name, group_id, user_id)]
            posters = extract_poster_info()
            st.write(f"Posters: {posters}")
            advert_text = find_advert_content()
            all_users_and_comments = find_comments_expanded()
            st.write(all_users_and_comments)
            #                    {
            #     "user_id": user_id,
            #     "name": name,
            #     "text": text,
            #     "group_id": group_id,
            #     "comment_id": comment_id,
            # }
            group_name = find_group_name()
            st.write(f"Group name {group_name}")

            for users_and_comments in all_users_and_comments:
                parameters = {
                    "full_name": users_and_comments["name"],
                    "name": users_and_comments["name"].lower().strip(),
                    "post_id": post_id,
                    "group_id": users_and_comments["group_id"],
                    "group_name": group_name,
                    "user_id": users_and_comments["user_id"],
                    "group_url": f"https://www.facebook.com/groups/{users_and_comments['group_id']}",
                    "user_url": f"https://www.facebook.com/{users_and_comments['user_id']}",
                    "post_url": f"https://www.facebook.com/groups/{users_and_comments['group_id']}/posts/{post_id}",
                    "comment_url": f"https://www.facebook.com/groups/{users_and_comments['group_id']}/posts/{post_id}/?comment_id={users_and_comments['comment_id']}",
                    "comment_text": users_and_comments["text"],
                    "comment_id": users_and_comments["comment_id"],
                    "advert_text": advert_text,
                }
                st.write(parameters)
                query = f"""MERGE (group:Group {{group_id: $group_id, url: $group_url}})
                    WITH group
                    MERGE (profile:Profile {{name: $full_name, url: $user_url}})
                    MERGE (name:Name {{full_name: $full_name, name: $name}})
                    MERGE (posting:Posting {{post_id: $post_id, post_url: $post_url}})
                    MERGE (comment:Comment {{comment_id: $comment_id, comment:$comment_text, url: $comment_url}})
                    MERGE (profile)-[:HAS_PROFILE_NAME]->(name)
                    MERGE (group)-[:HAS_POSTING]->(posting)
                    MERGE (posting)-[:HAS_COMMENT]->(comment)
                    MERGE (profile)-[:MADE_COMMENT]->(comment)
                    SET group.name = $group_name
                    SET posting.text = $advert_text
                    """
                # st.write(parameters)
                result = execute_neo4j_query(query, parameters)
                # st.write(result)
                # if is_valid_name(users_and_comments["name"]):
                #     st.write(f"Valid name: {users_and_comments['name']}")

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
                query = f"""MERGE (group:Group {{name: $group_name, group_id: $group_id, url: $group_url}})
                    MERGE (profile:Profile {{name: $full_name, url: $user_url}})
                    MERGE (name:Name {{full_name: $full_name, name: $name}})
                    MERGE (posting:Posting {{post_id: $post_id, post_url: $post_url}})
                    MERGE (profile)-[:HAS_PROFILE_NAME]->(name)
                    MERGE (profile)-[:POSTED]->(posting)
                    MERGE (group)-[:HAS_POSTING]->(posting)
                    SET posting.text = $advert_text
                        """

            execute_neo4j_query(query, parameters)
            st.write("Done upload...")
            st.write(posters)
            # if is_valid_name(poster["name"]):
            #     st.write(f"Valid name: {poster['name']}")

        if st.button("Extract advert"):
            posters = find_advert_poster()  # [(name, group_id, user_id)]
            poster_inside = find_advert_poster_inside()
            advert_text = find_advert_content()
            st.write(f"Advert text: {advert_text}; Posters: {posters}")
            st.write(f"Posters inside: {poster_inside}")

        if st.button("Extract comments"):
            all_users_and_comments = find_comments_expanded()
            st.write(f"All users and comments: {all_users_and_comments}")

        if st.button("find poster"):
            posters = find_advert_poster()
            st.write(f"Posters: {posters}")

        if st.button("find inside poster"):
            posters = find_advert_poster_inside()
            st.write(f"Inside Posters: {posters}")

        if st.button("Update_new_adverts"):
            try:
                new_adverts_urls = all_new_adverts_urls()
                original_url = st.session_state["driver"].current_url
                st.write(f"Original URL: {original_url}")
                st.write(new_adverts_urls)
                wait = WebDriverWait(st.session_state["driver"], 30)
                entries = []
                for new_advert_url in new_adverts_urls:
                    st.session_state["driver"].get(new_advert_url["post_url"])
                    post_id = extract_post_id(new_advert_url["post_url"])
                    # Wait for the element with ID 'MANIFEST_LINK' to be present
                    element = wait.until(
                        EC.presence_of_element_located((By.ID, "MANIFEST_LINK"))
                    )
                    st.write(f"New advert URL: {new_advert_url['post_url']}")
                    advert_poster = find_advert_poster()
                    st.write(f"Advert poster: {advert_poster}")
                    if advert_poster:
                        poster = advert_poster[0]
                        advert_text = find_advert_content()

                        st.write(
                            f"https://www.facebook.com/groups/{poster['group_id']}/posts/{post_id}"
                        )
                        parameters = {
                            "full_name": poster["name"],
                            "name": poster["name"].lower().strip(),
                            "user_id": poster["user_id"],
                            "post_id": post_id,
                            "user_url": f"https://www.facebook.com/{poster['user_id']}",
                            "post_url": f"https://www.facebook.com/groups/{poster['group_id']}/posts/{post_id}",
                            "advert_text": advert_text,
                        }
                        st.write(parameters)
                        query = f"""
                        MERGE (profile:Profile {{url: $user_url}})
                        SET profile.name = $full_name
                        WITH profile
                        MERGE (posting:Posting {{post_id: $post_id}}) SET posting.text = $advert_text
                        WITH profile, posting
                        MERGE (profile)-[:POSTED]->(posting)
                                """
                        entry = {"parameters": parameters, "query": query}
                        entries.append(entry)
                        pd.DataFrame(entries).to_csv(
                            "results/new_entries.csv", index=False
                        )
                        execute_neo4j_query(query, parameters)
                        waiting_time = randint(1, 7)
                        st.write(f"waiting {waiting_time}s... ")
                        time.sleep(waiting_time)
            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                # Ensure the driver navigates back to the original URL regardless of success or failure
                st.write("Finally!")
                st.session_state["driver"].get(original_url)
                wait.until(EC.presence_of_element_located((By.ID, "MANIFEST_LINK")))

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
