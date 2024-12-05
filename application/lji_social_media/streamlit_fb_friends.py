import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from gspread_dataframe import set_with_dataframe
import gspread
import libraries.neo4j_lib as nl
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from urllib.parse import urlparse, parse_qs
import os
import time
import logging
import subprocess
from random import randint
import re
from bs4 import BeautifulSoup


from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, TimeoutException


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


def find_posts_comments_and_user_ids(soup):
    # Find all 'div', 'p', and 'span' tags
    div_p_tags = soup.find_all(["div", "p"])
    span_tags = soup.find_all("span")

    # Prepare regex for user_id extraction
    user_id_pattern = re.compile(r"/groups/\d+/user/(\d+)/")

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
            user_id_match = user_id_pattern.search(href)
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
            user_id_match = user_id_pattern.search(href)
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


# def save_page_source(this_page, description):
#     file_path = DIR_PATH / f"{this_page}_{description}_page_source.html"
#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(st.session_state["driver"].page_source)


def get_element_with_wait(driver: WebDriver, by: By, value: str, timeout: int = 10):
    """
    Waits for an element to be present in the DOM and returns it.

    :param driver: WebDriver instance
    :param by: Locator type (e.g., By.CLASS_NAME, By.CSS_SELECTOR)
    :param value: Locator value
    :param timeout: Time in seconds to wait for the element
    :return: The located WebElement or raises an exception if not found
    """
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def extract_source_name(soup: BeautifulSoup, css_selector: str) -> str:
    """
    Extracts the profile name using a CSS selector from the parsed HTML.

    :param soup: BeautifulSoup instance containing the parsed HTML
    :param css_selector: CSS selector string to locate the element
    :return: The extracted profile name or a default message if not found
    """
    h1_tag = soup.select_one(css_selector)
    if h1_tag:
        return h1_tag.get_text(strip=True)
    return "Source Name Not Found"


def get_source_name(driver: WebDriver, timeout: int = 10) -> str:
    """
    Extracts the profile name from the current page of the driver.
    Waits for dynamic content to load and handles possible errors.

    :param driver: WebDriver instance
    :param timeout: Time in seconds to wait for an element to load
    :return: Profile name as a string
    """
    try:
        # Wait for the h1 element to load
        get_element_with_wait(driver, By.CSS_SELECTOR, "h1.html-h1", timeout)

        # Parse the page source
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # CSS selector for the h1 tag
        css_selector = "h1.html-h1.x1heor9g.x1qlqyl8.x1pd3egz.x1a2a7pz"

        # Extract and return the source name
        return extract_source_name(soup, css_selector)

    except TimeoutException:
        logging.error("Timed out waiting for page to load")
        return "Loading Failed"

    except NoSuchElementException:
        logging.error("The necessary element was not found on the page")
        return "Element Not Found"

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return "Error Occurred"


def get_source_name_depr(driver, timeout=10):
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


def get_source_name_depr(driver, timeout=10):
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


def find_profiles(driver) -> dict:
    current_datetime = datetime.now().strftime("%Y%m%d %H:%M:%S")
    source_name = get_source_name(driver, timeout=10)
    page_url = driver.current_url
    soup = BeautifulSoup(driver.page_source, "html.parser")

    profile_containers = soup.find_all("div", class_="x1iyjqo2 x1pi30zi")

    links_with_details = []
    for container in profile_containers:
        link_tag = container.find("a", href=True)
        if link_tag:
            name_tag = link_tag.find("span")
            name = name_tag.get_text(strip=True) if name_tag else ""
            work_div = container.find("div", class_="x1gslohp")
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


def find_profiles_depr(driver):
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
        nl.execute_neo4j_query(query, parameters)
        profile_dicts.append(parameters)
    pd.DataFrame(profile_dicts).to_csv(
        "results/follower_profile_dicts.csv", index=False
    )
    logging.info("Successfully created results/follower_profile_dicts.csv")


def friend_profiles_to_graph(profiles):
    """
    Inserts profile data into the Neo4j graph database and returns the count of new and existing profiles.

    :param profiles: Dictionary containing profile data
    :return: Tuple containing the count of existing and new profiles
    """
    profile_dicts = []
    logging.info("Creating results/profile_dicts.csv")
    for profile in profiles["data"]:
        parameters = {
            "source_name": profiles["source_name"],
            "source_url": profiles["source_url"]
            .replace("&sk=friends", "")
            .replace("/friends", "")
            .replace("web.", ""),
            "friend_url": profile[0]
            .replace("&sk=friends", "")
            .replace("/friends", "")
            .replace("web.", "www."),
            "friend_name": profile[1],
            "work_text": profile[2],
        }
        logging.info(parameters)
        query = """MERGE (p:Profile {url: $source_url, name: $source_name})
MERGE (f:Profile {url: $friend_url, name: $friend_name})
MERGE (w:WorkText {work_text: $work_text})
MERGE (p)-[:IS_FRIENDS_WITH]->(f)
MERGE (f)-[:HAS_WORK_TEXT]->(w)
WITH p, f
CALL apoc.create.addLabels(p, CASE WHEN NOT 'SourceProfile' IN labels(p) THEN ['SourceProfile'] ELSE [] END) YIELD node as pNode
CALL apoc.create.addLabels(f, CASE WHEN $friend_url = $source_url AND NOT 'FriendProfile' IN labels(f) THEN ['FriendProfile'] ELSE [] END) YIELD node as fNode
RETURN pNode, fNode
"""

        nl.execute_neo4j_query(query, parameters)
        profile_dicts.append(parameters)
    pd.DataFrame(profile_dicts).to_csv("results/profile_dicts.csv", index=False)
    logging.info("Successfully created results/profile_dicts.csv")


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
# save_page_usernames(driver, 'path_to_your_file.csv')


def save_page_source(driver, base_filename, description):
    """
    Save the HTML source of the current page in the WebDriver to a file.

    Args:
        driver (WebDriver): The WebDriver instance.
        dir_path (str): The directory to save the file.
        base_filename (str): The base name for the file (without the extension).
        :param description:
    """

    base_filename = clean_filename(base_filename)

    # # Ensure the directory exists
    # Path(dir_path).mkdir(parents=True, exist_ok=True)

    # Get the current date in the format yyyymmdd
    date_str = datetime.now().strftime("%Y%m%d")

    # Replace slashes in the base filename with underscores
    base_filename = base_filename.replace("/", "_")

    # Create the full filename
    filename = f"{base_filename}_{date_str}_{description}.html"

    # Create the full path to the file
    file_path = DIR_PATH / filename

    # Get the HTML source of the current page
    page_source = driver.page_source

    # Write the HTML source to the file
    with file_path.open("w", encoding="utf-8") as f:
        f.write(page_source)

    print(f"Saved page source to {file_path}")


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


import time
import random


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


def process_comments(soup):
    # Loop through each comment
    comment_count = 0
    comment_dict = {}
    for comment in soup.find_all(
        "div",
        class_="x1n2onr6 x4uap5 x18d9i69 x1swvt13 x1iorvi4 x78zum5 x1q0g3np x1a2a7pz",
    ):
        # Extract 'Comment by' information
        comment_count += 1
        comment_dict[comment_count] = {}
        comment_dict[comment_count]["time"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        comment_by_info = comment.get("aria-label")
        if comment_by_info:
            comment_dict[comment_count]["comment_by_info"] = comment_by_info
            logging.info(f"Comment By Info: {comment_by_info}")

        # Extract user_id
        user_link = comment.find("a", href=True, class_="x1i10hfl")
        if user_link:
            user_id_match = re.search(r"/groups/\d+/user/(\d+)/", user_link["href"])
            if user_id_match:
                user_id = user_id_match.group(1)
                comment_dict[comment_count]["user_id"] = user_id
                logging.info(f"User ID: {user_id}")

        # Extract username
        username_element = comment.find("span", class_="x193iq5w")
        if username_element:
            username = username_element.get_text()
            comment_dict[comment_count]["user_id"] = user_id
            comment_dict[comment_count]["username"] = username
            logging.info(f"Username: {username}")

        # Extract comment text
        comment_text_element = comment.find("div", class_="xdj266r")
        if comment_text_element:
            comment_text = comment_text_element.get_text()
            comment_dict[comment_count]["comment_text"] = comment_text
            logging.info(f"Comment Text: {comment_text}")

        logging.info("------")
    return comment_dict


def record_time_str():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


# Create a list to store the records
def make_sheet_records(data):
    logging.info("Making sheet records...")
    records = []

    # Loop over each numbered key in the data
    for key in data:
        # Check if 'posts' key exists in the dictionary
        if "posts" in data[key]:
            # Loop over each post
            for post_id, post_info in data[key]["posts"].items():
                # Extract the post_url
                post_url = post_info["post_url"]
                # Extract the group_id
                group_id = data[key]["group_id"]

                # Loop over each div_p_text
                for div_p_text in post_info.get("div_p_texts", []):
                    # Create a record for this div_p_text
                    record = {
                        "group_id": group_id,
                        "post_id": post_id,
                        "post_url": post_url,
                        "div_text": div_p_text[0],
                        "user_id": div_p_text[1],
                        "text_type": "div",
                    }
                    # Add the record to the list of records
                    records.append(record)

                # Loop over each span_text
                for span_text in post_info.get("span_texts", []):
                    # Create a record for this span_text
                    record = {
                        "group_id": group_id,
                        "post_id": post_id,
                        "post_url": post_url,
                        "span_text": span_text[0],
                        "user_id": span_text[1],
                        "text_type": "span",
                    }
                    # Add the record to the list of records
                    records.append(record)
    logging.info("Sheet records created.")
    # Create a DataFrame from the list of records
    return pd.DataFrame(records)


def insert_sheet_records(sheet_records):
    # Get the last row index with data in the Google Sheet
    logging.info("Inserting sheet records...")
    last_row = len(st.session_state["sheet"].get_all_values())
    logging.info(f"Inserting {last_row} sheet records...")
    # Set the DataFrame to the Google Sheet starting at the last row
    # include_index=False and include_column_header=False are set so that the index and column headers of the DataFrame are not included.
    # If the sheet is empty (last_row == 0), include the column headers
    set_with_dataframe(
        st.session_state["sheet"],
        sheet_records,
        row=last_row + 1,
        include_index=False,
        include_column_header=(last_row == 0),
    )
    logging.info("Sheet records inserted.")


def debug_extract_posts():
    # Define the maximum number of group_divs and post_links to process
    max_group_divs = 3
    max_post_links = 3

    try:
        driver = st.session_state["driver"]
        original_url = driver.current_url
        html_content = driver.page_source
    except Exception as e:
        logging.error(f"Failed to retrieve page source: {e}")
        return

    try:
        soup = BeautifulSoup(html_content, "html.parser")
    except Exception as e:
        logging.error(f"Failed to parse HTML content: {e}")
        return

    try:
        group_divs = soup.find_all("div", class_="x9f619 x1n2onr6 x1ja2u2z")
        logging.info(f"Found {len(group_divs)} outer div elements.")
    except Exception as e:
        logging.error(f"Failed to find outer div elements: {e}")
        return

    div_dict = {}

    # Display a progress bar for group_divs
    group_divs_progress = st.progress(0)
    for i, group_div in enumerate(group_divs, start=1):
        if i > max_group_divs:
            logging.info(f"Reached the maximum number of group_divs: {max_group_divs}")
            break

        # Update the progress bar
        group_divs_progress.progress(i / min(len(group_divs), max_group_divs))

        div_dict[i] = {}
        logging.info(f"Processing div {i}")

        div_dict[i] = {}  # Create a new dictionary for this div
        logging.info(f"Processing div {i}")

        # Extract group_id
        group_id_match = re.search(
            r"https://www\.facebook\.com/groups/(\d+)", st.session_state.selected_link
        )
        group_id = group_id_match.group(1) if group_id_match else None
        div_dict[i]["group_id"] = group_id
        div_dict[i]["time"] = record_time_str()
        logging.info(f"Found group_id: {group_id}")

        # Extract post content
        post_content_element = group_div.find("div", class_="x1s85apg")
        div_dict[i]["post_content_element"] = (
            post_content_element.text if post_content_element else None
        )
        post_content = post_content_element.text if post_content_element else None
        div_dict[i]["post_content"] = post_content
        logging.info(f"Post Content: {post_content}")

        # Find all post links within the group
        post_links = group_div.find_all(
            "a",
            href=re.compile(rf"https://www.facebook.com/groups/{group_id}/posts/\d+/"),
        )
        logging.info(f"Found {len(post_links)} post links in the group {group_id}.")
        post_dict = {}

        # Display a progress bar for post_links
        post_links_progress = st.progress(0)
        for j, post_link in enumerate(post_links, start=1):
            if j > max_post_links:
                logging.info(
                    f"Reached the maximum number of post_links: {max_post_links}"
                )
                break

            # Update the progress bar
            post_links_progress.progress(j / min(len(post_links), max_post_links))

            post_dict[j] = {}
            logging.info(f"Processing post {j}")

            # Extract post_id
            post_id_match = re.search(r"/posts/(\d+)/", post_link["href"])
            post_id = post_id_match.group(1) if post_id_match else None
            post_dict[j]["post_id"] = post_id
            post_dict[j]["time"] = record_time_str()
            logging.info(f"Found post_id: {post_id}")

            # Navigate to the post URL
            post_url = f"https://www.facebook.com/groups/{group_id}/posts/{post_id}/"
            post_dict[j]["post_url"] = post_url
            driver.get(post_url)

            # Wait for the page to load
            time.sleep(randint(7, 19))

            # Get the HTML content of the current page
            new_html_content = driver.page_source

            # Parse the HTML content
            new_soup = BeautifulSoup(new_html_content, "html.parser")
            div_p_texts, span_texts = find_posts_comments_and_user_ids(new_soup)
            post_dict[j]["div_p_texts"] = list(set(div_p_texts))
            post_dict[j]["span_texts"] = list(set(span_texts))
            # Process comments
            comment_dict = process_comments(new_soup)
            post_dict[j]["comments"] = comment_dict
            for key in comment_dict.keys():
                write_dict = {
                    "group": st.session_state["sheet_name"],
                    "group_id": group_id,
                    "time": post_dict[j]["time"],
                    "post_id": post_id,
                    "post_url": post_url,
                    "user_id": comment_dict[key]["user_id"],
                    "username": comment_dict[key]["username"],
                    "comment_by_info": comment_dict[key]["comment_by_info"],
                    "comment_text": comment_dict[key]["comment_text"],
                }
                append_comments(write_dict)
                logging.info(f"Writing comment to sheet: {write_dict}")
        div_dict[i]["posts"] = post_dict

        # Return to the original page
        driver.get(original_url)
        time.sleep(randint(7, 19))
    return div_dict


def extract_posts():
    # Counter for the number of posts processed
    posts_processed = 0
    divs_processed = 0
    comments_processed = 0

    try:
        # Get the WebDriver from the session state
        driver = st.session_state["driver"]

        # Store the current URL to return to it later
        original_url = driver.current_url

        # Get the HTML content of the current page
        html_content = driver.page_source
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
        # Find all the outer div elements containing the posts
        group_divs = soup.find_all("div", class_="x9f619 x1n2onr6 x1ja2u2z")
        logging.info(f"Found {len(group_divs)} outer div elements.")
    except Exception as e:
        logging.error(f"Failed to find outer div elements: {e}")
        return

    # Extract information
    divs_processed = 0
    for group_div in group_divs:
        divs_processed += 1
        logging.info(f"Processing div {divs_processed}")
        # Extract group_id
        # group_link = group_div.find("a", href=re.compile(r"/groups/\d+/user/\d+/"))
        # group_id = st.session_state.group_id
        group_id_match = re.search(
            r"https://www\.facebook\.com/groups/([^/]+)", st.session_state.selected_link
        )
        logging.info(f"Found group_id_match: {group_id_match}")
        group_id = group_id_match.group(1) if group_id_match else None
        logging.info(f"Found group_id: {group_id}")
        # Find all post links within the group
        post_links = group_div.find_all(
            "a",
            href=re.compile(rf"https://www.facebook.com/groups/{group_id}/posts/\d+/"),
        )
        logging.info(f"Found {len(post_links)} post links in the group {group_id}.")
        posts_processed = 0
        for post_link in post_links:
            logging.info(f" === Processing post {posts_processed + 1}... ===")
            if posts_processed >= LIMIT_EXTRACT_POSTS:
                break

            # Extract post_id
            post_id = (
                re.search(r"/posts/(\d+)/", post_link["href"]).group(1)
                if post_link
                else None
            )
            logging.info(f"Found post_id: {post_id}")

            # Navigate to the post URL to get the full content
            driver.get(post_link["href"])
            time.sleep(randint(randint(2, 5), randint(5, 9)))  # Mimic human pause

            # Extract post text
            # post_content_element = driver.find_element_by_css_selector('div.x1s85apg')
            post_content_element = soup.select_one("div.x1s85apg")

            # ...

            # Extract post text
            post_content_elements = soup.select("div.x1s85apg")

            post_texts = []  # Initialize an empty list to store post_texts
            poster_ids = []  # Initialize an empty list to store poster_ids

            for post_content_element in post_content_elements:
                post_text = post_content_element.text if post_content_element else None
                if post_text != "Facebook":
                    logging.info(f"Found post_text: {post_text}")

                    post_texts.append(post_text)  # Append post_text to the list
                    logging.info(f"Found post_text: {post_text}")

                    # Extract poster_id
                    poster_links = post_content_element.select(
                        "a[href*='/groups/'][href*='/user/']"
                    )

                    for poster_link in poster_links:
                        if poster_link:
                            href = poster_link.get_attribute("href")
                            if href:
                                poster_id_match = re.search(r"/user/(\d+)", href)
                                poster_id = (
                                    poster_id_match.group(1)
                                    if poster_id_match
                                    else None
                                )
                            else:
                                poster_id = None
                                logging.warning(
                                    "href attribute is not present in poster_link"
                                )
                        else:
                            poster_id = None
                            logging.warning("poster_link is None")

                # logging.info(f"Found poster_link: {poster_link}")
                # poster_id = (
                #     re.search(r"/user/(\d+)/", poster_link.get_attribute("href")).group(1)
                #     if poster_link
                #     else None
                # )
                # logging.info(f"Found poster_link: {poster_link}")

            comment_links = soup.select(
                "a[href*='https://www.facebook.com/groups/'][href*='/posts/'][href*='?comment_id=']"
            )
            comments_processed = 0
            for comment_link in comment_links:
                if comments_processed >= LIMIT_EXTRACT_COMMENTS:
                    break
                logging.info(f"Processing comment {comments_processed + 1}...")
                # Extract comment_id
                # logging.info(f"comment_link: {comment_link}")
                comment_id = (
                    re.search(r"\?comment_id=(\d+)", comment_link["href"]).group(1)
                    if comment_link
                    else None
                )
                logging.info(f"comment_id: {comment_id}")
                # Extract comment text
                if comment_link:
                    comment_text_element = comment_link.find("div", class_="x1n2onr6")
                    comment_text = (
                        comment_text_element.text if comment_text_element else None
                    )
                    logging.info(f"comment_text: {comment_text}")
                    # rest of the code
                else:
                    logging.warning("comment_link is None")
                    comment_text = None

                logging.info(f"comment_text: {comment_text}")
                if comment_text_element:
                    commenter_link = comment_text_element.select_one(
                        "a[href*='/groups/'][href*='/user/']"
                    )
                    logging.info(f"commenter_link: {commenter_link}")
                    commenter_id = (
                        re.search(
                            r"/user/(\d+)/", commenter_link.get_attribute("href")
                        ).group(1)
                        if commenter_link
                        else None
                    )
                    logging.info(f"commenter_id: {commenter_id}")
                else:
                    commenter_link = None
                    commenter_id = None
                    logging.warning("comment_text_element is None")

                # Log the information
                logging.info(
                    f"Group {group_id} Post {post_id} poster_ids: {poster_ids} with post_texts {post_texts} and comment_id {comment_id} and comment {comment_text} and commenter_id {commenter_id}"
                )

            # Increment the counter for posts processed
            posts_processed += 1

            # Return to the original page
            logging.info(f"Returning to the original page {original_url}")
            driver.get(original_url)
            logging.info("===time.sleep(randint(randint(2,4),randint(5,9)))===")
            time.sleep(randint(randint(2, 4), randint(5, 9)))  # Mimic human pause


def extract_posts_depr():
    # Counter for the number of posts processed
    posts_processed = 0
    try:
        # Get the WebDriver from the session state
        driver = st.session_state["driver"]

        # Store the current URL to return to it later
        original_url = driver.current_url

        # Get the HTML content of the current page
        html_content = driver.page_source
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
        # Find all the outer div elements containing the posts
        # outer_divs = soup.find_all("div", class_="xu06os2 x1ok221b")
        post_outer_div = st.secrets["selectors"][
            "extract_post_outer_div"
        ]  # st.secrets['selectors']['post_outer_div']
        logging.info(f"use post_outer_div: {post_outer_div}")
        # logging.info(f"use post_outer_div: {post_outer_div}")
        # outer_divs = soup.find_all(lambda tag: tag.name == 'div' and post_outer_div in tag.get('class', []))
        # Find all the outer div elements containing the posts using XPath
        #  outer_divs = driver.find_elements_by_xpath('//div[contains(@class, "xu06os2") and contains(@class, "x1ok221b")]')
        outer_divs = soup.find_all(
            lambda tag: tag.name == "div" and post_outer_div in tag.get("class", [])
        )

    except Exception as e:
        logging.error(f"Failed to find outer div elements: {e}")
        return

    # Extract information
    for outer_div in outer_divs:
        if posts_processed >= LIMIT_EXTRACT_POSTS:
            break
        try:
            # Mimic human pause
            time.sleep(2)

            # Extract and print the text content within the div
            post_content = outer_div.text
            logging.info(f"Post Content: {post_content}")
            # logging.info(f"Post outer_div: {outer_div}")

            # Find the anchor tag with href containing '/groups/' and '/posts/'
            # post_link = outer_div.find(
            #     "a", href=lambda x: x and "/groups/" in x and "/posts/" in x
            # )
            # post_link = outer_div.find_element_by_xpath(".//a[contains(@href, '/groups/') and contains(@href, '/posts/')]")
            post_link = outer_div.find(
                "a", href=lambda x: x and "/groups/" in x and "/posts/" in x
            )
            # logging.info(f"post_link: {post_link}")
            logging.info(f"post_link: {post_link}")
            if post_link:
                # Extract href attribute
                href = post_link["href"]
                logging.info(f"href: {href}")
                # Split the href by slashes and get the group_id and post_id
                parts = href.split("/")
                if len(parts) >= 4:
                    group_id = parts[parts.index("groups") + 1]
                    post_id = parts[parts.index("posts") + 1]
                    logging.info(f"Group ID: {group_id}, Post ID: {post_id}")

                    # Navigate to the post URL to get the full content
                    driver.get(href)
                    logging.info(f"href: {href}")
                    # Mimic human pause
                    time.sleep(2)

                    # Extract the full content here if needed

                    # Return to the original page
                    driver.get(original_url)

                    # Mimic human pause
                    time.sleep(2)
            # Increment the counter for posts processed
            posts_processed += 1
        except Exception as e:
            logging.error(f"Failed to extract post content, group_id, or post_id: {e}")
            continue


def main():
    # Path to the JSON key file
    # Connect button
    # ... rest of the logic ...
    if "connected" not in st.session_state:
        st.session_state["connected"] = False

        # Check if the driver is already initialized
    if "driver" not in st.session_state:
        st.session_state["driver"] = None

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
        # st.write("You are now connected!")
        # Google Sheet information
        # Authenticate using the JSON key file
        st.session_state["client"] = get_service_account()
        st.session_state["worksheet"] = get_worksheet(
            st.session_state["client"], GOOGLE_SPREADSHEET_NAME, GOOGLE_SHEET_NAME
        )
        st.session_state["results_file"] = Path("results/results.json")
        st.session_state["session_result"] = {}

    if ("links" not in st.session_state) and st.session_state["connected"]:
        st.session_state.links = st.session_state["worksheet"].col_values(1)

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
                save_results(
                    st.session_state["results_file"], st.session_state["session_result"]
                )
                st.session_state["sheet_records"].to_csv(
                    Path("results/sheet_records.csv"), index=False
                )
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

        # Scroll down button
        if "scrolling" not in st.session_state:
            st.session_state.scrolling = False

        # Start button
        if not st.session_state.scrolling and st.button("Start Scrolling"):
            st.session_state.scrolling = True
        st.session_state["scrolled_count"] = 0

        # Assuming get_profile_name function is defined as shown earlier

        if st.button("Collect friends details"):
            try:
                logging.info("Collecting friends!")
                scroll_down(st.session_state["driver"])

                st.session_state["scrolled_count"] += 1

                # save_page_source(this_page, "scrolldown", None)
                save_page_usernames(
                    st.session_state["driver"], "results/friends_url_usernames.txt"
                )
                profiles = find_profiles(st.session_state["driver"])
                friend_profiles_to_graph(profiles)

            except TimeoutException:
                logging.error(
                    "The elements were not found within the specified timeout."
                )

        if st.button("Collect follower details"):
            try:
                logging.info("Collecting followers!")
                scroll_down(st.session_state["driver"])
                save_page_usernames(
                    st.session_state["driver"], "results/follower_url_usernames.txt"
                )
                profiles = find_profiles(st.session_state["driver"])
                follower_profiles_to_graph(profiles)

            except TimeoutException:
                logging.error(
                    "The elements were not found within the specified timeout."
                )

            # Scroll down button

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

                # save_page_source(this_page, "scrolldown", None)
            except TimeoutException:
                logging.error(
                    "The elements were not found within the specified timeout."
                )


# This is the standard boilerplate that calls the 'main' function
if __name__ == "__main__":
    main()
