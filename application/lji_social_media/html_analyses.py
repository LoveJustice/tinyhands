from bs4 import BeautifulSoup
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

path_to_chromedriver = "~/Downloads/chromedriver-mac-arm64/chromedriver"
service = Service(path_to_chromedriver)


def find_posts_comments_and_user_ids(file_path):
    with open(file_path, "r") as f:
        contents = f.read()

    soup = BeautifulSoup(contents, "html.parser")

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


# Path to the new HTML file
new_file_path = Path("data_sources/1250339572505634_posts_1356304738575783.html")

# Find all posts, comments, and associated user_ids in the new HTML file
posts_new, comments_new = find_posts_comments_and_user_ids(new_file_path)
posts_new, comments_new

import json
import pandas as pd

filename = "results/results.json"
if Path(filename).exists():
    with open(filename, "r") as f:
        data = json.load(f)
else:
    data = {}
data.keys()

for key in data:
    print(key)
    print(data[key].keys())
    for post_id, post_info in data[key]["posts"].items():
        print(post_id)
        print(post_info.keys())
data["20230711 15:19:33"].keys()
data["1"].keys()
data["1"]["posts"]["1"]["div_p_texts"][2]
len(set(data["1"]["posts"]["1"]["div_p_texts"]))
data["1"]["post_content"]
data["1"]["post_content_element"]
data["1"]["posts"].keys()
data["1"]["posts"]["1"]
data["1"]["posts"]["1"]["comments"]
data["1"]["posts"]["1"]["div_p_texts"][1]

data["1"]
data["1"]["posts"]["1"].keys()
data["1"]["posts"]["1"]["post_id"]
data["1"]["posts"]["1"]["post_url"]
data["1"]["posts"]["1"]["comments"]
data["1"]["posts"]["1"]["div_p_texts"]
data["1"]["posts"]["1"]["span_texts"]

for key in data["1"]["posts"]["1"]["comments"].keys():
    print(key)
    print(data["1"]["posts"]["1"]["comments"][key])

for post_id, post_info in data[key]["posts"].items():
    data["1"]["posts"]["1"]["comments"]

# Extract the post_url


def make_sheet_records(data):
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

    # Create a DataFrame from the list of records
    return pd.DataFrame(records)
