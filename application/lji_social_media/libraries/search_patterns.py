import re
import streamlit as st
from bs4 import BeautifulSoup, Tag
import json
from typing import List, Dict, Optional


# Constants for regex patterns
GROUP_USER_ID_PATTERN = re.compile(r"/groups/([\w]+)/user/([\w]+)/?")
GROUP_ID_PATTERN = re.compile(r"groups/([\w]+)")
GROUP_POST_ID_PATTERN = re.compile(r"/groups/([\w]+)/posts/([\w]+)/?")
GROUP_COMMENT_ID_PATTERN = re.compile(
    r"groups/([\w]+)/posts/([\w]+)/.*[?&]comment_id=([\w]+)/?"
)


def find_advert_content() -> Optional[str]:
    """Extract the advertisement content from the current page."""
    try:
        soup = BeautifulSoup(st.session_state["driver"].page_source, "html.parser")
        message_div = soup.find("div", {"data-ad-comet-preview": "message"})

        if not message_div:
            st.warning("The message div could not be found in the HTML content.")
            return None

        return " ".join(
            div.get_text(strip=True)
            for div in message_div.find_all("div", recursive=False)
        )
    except Exception as e:
        st.error(f"An error occurred while extracting advert content: {str(e)}")
        return None


# Constants for regex patterns
GROUP_USER_ID_PATTERN = re.compile(r"/groups/([\w]+)/user/([\w]+)/?")
GROUP_ID_PATTERN = re.compile(r"groups/([\w]+)")
GROUP_POST_ID_PATTERN = re.compile(r"/groups/([\w]+)/posts/([\w]+)/?")
GROUP_COMMENT_ID_PATTERN = re.compile(
    r"groups/([\w]+)/posts/([\w]+)/.*[?&]comment_id=([\w]+)/?"
)

import re
from typing import Dict
from bs4 import BeautifulSoup
import streamlit as st


def find_advert_poster_alt() -> Dict[str, str]:
    """Extract information about the original poster of the advertisement and the advert content from the specific HTML structure."""
    try:
        # Parse the HTML content
        soup = BeautifulSoup(st.session_state["driver"].page_source, "html.parser")

        # Step 1: Find the poster's name and link
        name_anchor = soup.find(
            "a", attrs={"aria-label": True}, href=re.compile(r"/groups/\d+/user/\d+/")
        )
        if not name_anchor:
            st.warning("Poster link could not be found.")
            return {}

        # Extract the poster's name
        name = name_anchor.get("aria-label", "").strip()
        if not name:
            st.warning("Poster name could not be extracted.")
            return {}

        # Extract user_id and group_id from the href
        href = name_anchor.get("href", "")
        match = re.search(r"/groups/(\d+)/user/(\d+)/", href)
        if match:
            group_id, user_id = match.groups()
        else:
            st.warning("User ID or Group ID could not be extracted.")
            return {}

        # Step 2: Find the group name
        group_link = soup.find(
            "a", href=re.compile(r"https?://www\.mybooks\.com/groups/\d+/")
        )
        if group_link:
            group_name = group_link.text.strip()
        else:
            group_name = "Unknown Group"

        # Step 3: Extract the advert content
        # Find all divs with inline style containing 'font-size: 30px'
        advert_divs = soup.find_all(
            "div",
            style=lambda s: s and "font-size: 30px" in s and "font-weight: bold" in s,
        )

        advert_contents = []
        for div in advert_divs:
            # The advert text is within a child div
            content_div = div.find("div")
            if content_div:
                text = content_div.get_text(separator=" ", strip=True)
                if text:
                    advert_contents.append(text)
            else:
                # If there is no child div, get text from the current div
                text = div.get_text(separator=" ", strip=True)
                if text:
                    advert_contents.append(text)

        # Combine the advert contents
        advert_content = " ".join(advert_contents)
        if not advert_content:
            st.warning("Advert content could not be extracted.")
            advert_content = "Advert content not found."

        # Step 4: Extract the timestamp (if available)
        timestamp_elem = soup.find(
            lambda tag: tag.name in ["abbr", "span"] and tag.has_attr("data-utime")
        )
        if timestamp_elem:
            timestamp = timestamp_elem.get("data-utime")
        else:
            timestamp = "Unknown"

        # Step 5: Extract the post_id (if available)
        post_id = None  # Not available in the provided HTML

        # Return the extracted details
        return {
            "poster_info": {
                "name": name,
                "user_id": user_id,
                "group_id": group_id,
                "group_name": group_name,
                "post_id": post_id,
                "timestamp": timestamp,
            },
            "advert_content": advert_content,
        }

    except Exception as e:
        st.error(f"An error occurred while extracting information: {str(e)}")
        return {}


def find_advert_poster() -> Dict[str, str]:
    """Extract information about the original poster of the advertisement and the advert content."""
    try:
        # Assuming st.session_state["driver"].page_source contains the HTML content
        soup = BeautifulSoup(st.session_state["driver"].page_source, "html.parser")

        # Try to locate the primary ad content, handling both complex and simple structures.
        post_content = soup.find("div", {"data-ad-preview": "message"})

        # If the above fails, search for more generic div/span elements that may contain the advert content.
        if not post_content:
            post_content = soup.find(
                "div", {"class": re.compile(r"x18d9i69")}
            )  # General content container
            if not post_content:
                st.warning("Post content could not be found.")
                return {}

        # Check if the content is in a simple span or direct text in the found div
        advert_content = (
            post_content.text.strip() if post_content else "Advert content not found."
        )

        # Try to find the nearest preceding h2 that contains the poster's name
        poster_h2 = post_content.find_previous("h2")
        if not poster_h2:
            st.warning("Poster information could not be found.")
            return {}

        # Find the anchor tag within the h2 for the user information
        name_anchor = poster_h2.find("a", href=re.compile(r"/groups/\d+/user/\d+/"))
        if not name_anchor:
            st.warning("Poster link could not be found.")
            return {}

        # Extract the poster's name
        name = name_anchor.text.strip()

        # Extract user_id and group_id
        href = name_anchor.get("href", "")
        match = re.search(r"/groups/(\d+)/user/(\d+)/", href)
        if not match:
            st.warning("User ID or Group ID could not be extracted.")
            return {}

        group_id, user_id = match.groups()

        # Extract post_id from the current URL
        post_id_match = re.search(
            r"/posts/(\d+)", st.session_state["driver"].current_url
        )
        post_id = post_id_match.group(1) if post_id_match else None

        # Return the extracted details
        return {
            "poster_info": {
                "name": name,
                "user_id": user_id,
                "group_id": group_id,
                "post_id": post_id,
            },
            "advert_content": advert_content,
        }

    except Exception as e:
        st.error(f"An error occurred while extracting information: {str(e)}")
        return {}


def extract_post_id(url: str) -> Optional[str]:
    """Extract post ID from the given URL."""
    match = GROUP_POST_ID_PATTERN.search(url)
    return match.group(2) if match else None


def extract_poster_info(name: str, href: str) -> Optional[Dict[str, str]]:
    """
    Extract poster information from the name and href.

    Args:
        name (str): The name of the poster
        href (str): The href attribute of the poster's link

    Returns:
        Optional[Dict[str, str]]: A dictionary with poster information if matches are found, None otherwise
    """
    group_user_match = GROUP_USER_ID_PATTERN.search(href)
    post_match = GROUP_POST_ID_PATTERN.search(href)

    if group_user_match and post_match:
        group_id, user_id = group_user_match.groups()
        _, post_id = post_match.groups()
        return {
            "name": name,
            "group_id": group_id,
            "user_id": user_id,
            "post_id": post_id,
        }
    return None


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


def extract_group_id(url):
    result = GROUP_ID_PATTERN.search(url)

    if result:
        # Extracted post ID is the second captured group
        group_id = result.group(1)
        return group_id
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
        st.write(f"Error in extract_poster_info: {e}")

    return poster_info


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


def find_comments_expanded() -> List[Dict[str, str]]:
    """Extract and return expanded comment information from the current page."""
    soup = BeautifulSoup(st.session_state["driver"].page_source, "html.parser")
    comment_blocks = soup.find_all(
        "div", class_="x1r8uery x1iyjqo2 x6ikm8r x10wlt62 x1pi30zi"
    )

    return list(
        {
            json.dumps(comment, sort_keys=True): comment
            for block in comment_blocks
            if (comment := extract_comment_info(block)) is not None
        }.values()
    )


def extract_comment_id(comment_link: Optional[Tag]) -> str:
    """Extract the comment ID from a comment link."""
    if comment_link and (
        match_comment := GROUP_COMMENT_ID_PATTERN.search(comment_link["href"])
    ):
        return match_comment.group(3)
    return "Comment ID not found"


def extract_comment_info(parent_element: Tag) -> Optional[Dict[str, str]]:
    """Extract comment information from a single comment block."""
    user_link = parent_element.find("a", href=GROUP_USER_ID_PATTERN)
    if not user_link or not (
        match_user := GROUP_USER_ID_PATTERN.search(user_link["href"])
    ):
        return None

    group_id, user_id = match_user.groups()
    text_container = parent_element.find("div", class_="x1lliihq xjkvuk6 x1iorvi4")
    comment_link = parent_element.find("a", href=GROUP_COMMENT_ID_PATTERN)

    return {
        "user_id": user_id,
        "name": user_link.text,
        "text": text_container.text if text_container else "Text not found",
        "group_id": group_id,
        "comment_id": extract_comment_id(comment_link),
    }
