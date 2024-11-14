from urllib.parse import urljoin, unquote

import libraries.neo4j_lib as nl


import requests
import re
import json
import os
import libraries.search_patterns as sp
import time
from typing import List, Dict, Optional
from st_aggrid import AgGrid, GridOptionsBuilder
from bs4 import BeautifulSoup, NavigableString
import base64
from dataclasses import dataclass
import streamlit as st
from PIL import Image
from io import BytesIO

# from libraries.image_conversion import analyze_image, ImageAnalysisResult
from logging.handlers import RotatingFileHandler
import logging
from datetime import datetime
import base64
import os
import json
from typing import Union
from pathlib import Path

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


# Set up logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(
    log_dir, f"image_analysis_{datetime.now().strftime('%Y%m%d')}.log"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Clear all existing handlers
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Create a FileHandler that overwrites the log file
file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)

file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

# Optional: Add a StreamHandler to also log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Log the start of the script
logger.info("Script started. Log file will be overwritten.")


class ImageAnalysisResult(BaseModel):
    description: str
    text: str = ""
    emails: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)
    phone_numbers: list[str] = Field(default_factory=list)
    names: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)


def create_node(label, properties):
    query = f"MERGE (n:{label} {{"
    for key in properties.keys():
        query += f"{key}: ${key}, "
    query = query.rstrip(", ") + "}) RETURN ID(n) as node_id"

    # Execute the query with the properties as parameters
    return nl.execute_neo4j_query(query, properties)[0]["node_id"]


# Function to create an edge between two nodes
def create_edge(from_node_id, to_node_id, relationship):
    query = f"""
    MATCH (a), (b)
    WHERE ID(a) = $from_node_id AND ID(b) = $to_node_id
    MERGE (a)-[r:{relationship}]->(b)
    RETURN type(r)
    """
    nl.execute_neo4j_query(
        query, {"from_node_id": from_node_id, "to_node_id": to_node_id}
    )


# Main function to process ImageAnalysisResult and create nodes/edges
def create_image_url_relationships(posting_id, analysis_result: ImageAnalysisResult):
    # Create or find the ImageUrl node (which is also a Url node)
    image_url_id = create_node(
        "ImageUrl:Url", {"url": st.session_state["selected_img"]}
    )
    create_edge(posting_id, image_url_id, "HAS_IMAGE_URL")

    if analysis_result.description:
        description_id = create_node(
            "Description", {"description": analysis_result.description}
        )
        create_edge(image_url_id, description_id, "HAS_DESCRIPTION")
    if analysis_result.text:
        text_id = create_node("Text", {"text": analysis_result.text})
        create_edge(image_url_id, text_id, "HAS_TEXT")

    for url in analysis_result.urls:
        url_id = create_node("Url", {"url": st.session_state["selected_img"]})

        # Create HAS_IMAGE_URL relationship to Posting node
        create_edge(image_url_id, url_id, "HAS_URL")

        # Create other nodes and relationships if values exist

    for email in analysis_result.emails:
        email_id = create_node("Email", {"email": email})
        create_edge(image_url_id, email_id, "HAS_EMAIL")

    for phone_number in analysis_result.phone_numbers:
        phone_number_id = create_node("PhoneNumber", {"phonenumber": phone_number})
        create_edge(image_url_id, phone_number_id, "HAS_PHONENUMBER")

    for name in analysis_result.names:
        name_id = create_node("Name", {"name": name})
        create_edge(image_url_id, name_id, "HAS_NAME")

    for location in analysis_result.locations:
        location_id = create_node("Location", {"location": location})
        create_edge(image_url_id, location_id, "HAS_LOCATION")

    for date in analysis_result.dates:
        date_id = create_node("Date", {"date": date})
        create_edge(image_url_id, date_id, "HAS_DATE")


def analyze_image(
    image: Union[str, Path],
    api_key: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 900,
    api_url: str = "https://api.openai.com/v1/chat/completions",
) -> ImageAnalysisResult:
    def clean_json_string(content):
        # Remove the ```json at the beginning and ``` at the end
        cleaned_content = content.strip("```json\n").strip("```")
        return cleaned_content

    logger.info(f"Starting image analysis for file: {image}")
    logger.debug(
        f"Analysis parameters - model: {model}, max_tokens: {max_tokens}, api_url: {api_url}"
    )

    def encode_image(image_path):
        logger.debug(f"Encoding image: {image_path}")
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    base64_image = encode_image(image)
    logger.debug("Image successfully encoded")

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    logger.debug("Headers prepared for API request")

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analyze this image. Give a brief description. If there is text then please return it as is. "
                            "Please also extract email, urls and phonenumbers and return your answer in following JSON format::"
                            '{"description": "brief description","text": "text extracted from image", '
                            '"emails": ["email1", "email2"], "urls": ["url1", "url2"], "phonenumbers": ["phonenumber1", "phonenumber2"]'
                            'names": ["name1", "name2"], "locations": ["location1", "location2"], "dates": ["date1", "date2"]}'
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": max_tokens,
    }
    logger.debug("Payload prepared for API request")

    try:
        logger.info("Sending request to OpenAI API")
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        logger.info("Received response from OpenAI API")
        logger.debug(f"Raw API response: {json.dumps(result, indent=2)}")

        content = result["choices"][0]["message"]["content"]
        logger.debug(f"Extracted content from API response: {content}")

        parsed_content = json.loads(clean_json_string(content))
        logger.debug(f"Parsed content: {json.dumps(parsed_content, indent=2)}")

        analysis_result = ImageAnalysisResult(
            description=parsed_content.get("description", ""),
            text=parsed_content.get("text", ""),
            emails=parsed_content.get("emails", []),
            urls=parsed_content.get("urls", []),
            phone_numbers=parsed_content.get("phonenumbers", []),
            names=parsed_content.get("names", []),
            locations=parsed_content.get("locations", []),
            dates=parsed_content.get("dates", []),
        )
        logger.info("Image analysis completed successfully")
        logger.debug(f"Analysis result: {analysis_result}")

        return analysis_result

    except requests.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        raise ValueError(f"API request failed: {str(e)}") from e
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse API response as JSON: {str(e)}")
        raise ValueError(f"Failed to parse API response as JSON: {str(e)}") from e
    except KeyError as e:
        logger.error(f"Unexpected API response structure: {str(e)}")
        raise ValueError(f"Unexpected API response structure: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error during image analysis: {str(e)}")
        raise ValueError(f"Unexpected error during image analysis: {str(e)}") from e


def analyze_images():
    logger.info("Starting image analysis process")
    img_urls = find_img_urls()

    if not img_urls:
        logger.warning("No image URLs found")
        st.warning("No image URLs found")
        return

    logger.info(f"Found {len(img_urls)} image URLs")
    st.write("Image URLs:")
    for url in img_urls:
        st.write(url)

    st.title("Display and Analyze Images from HTML")

    images = []  # Store image objects for later analysis

    for idx, url in enumerate(img_urls):
        logger.info(f"Processing image from URL: {url}")
        with st.expander(f"Image {idx + 1}", expanded=True):
            st.write(f"Fetching image from: {url}")
            try:
                if url.startswith("data:"):
                    logger.debug("Processing data URI")
                    match = re.match(
                        r"data:(?P<mime>.*?)(;charset=(?P<charset>.*?))?(;base64)?,(?P<data>.*)",
                        url,
                        re.DOTALL,
                    )
                    if match:
                        mime_type = match.group("mime")
                        data = match.group("data")
                        is_base64 = ";base64" in url
                        logger.debug(f"MIME type: {mime_type}, Base64: {is_base64}")

                        if "svg+xml" in mime_type:
                            logger.debug("Processing SVG image")
                            svg_data = (
                                base64.b64decode(data).decode("utf-8")
                                if is_base64
                                else unquote(data)
                            )
                            st.markdown(
                                f"<div>{svg_data}</div>", unsafe_allow_html=True
                            )
                        else:
                            logger.debug("Processing non-SVG image")
                            image_data = (
                                base64.b64decode(data)
                                if is_base64
                                else unquote(data).encode("utf-8")
                            )
                            image = Image.open(BytesIO(image_data))
                            st.image(
                                image,
                                caption="Image from data URI",
                                use_column_width=True,
                            )
                            images.append((image, url))
                    else:
                        logger.error(f"Invalid data URI: {url}")
                        st.error(f"Invalid data URI: {url}")
                else:
                    logger.debug(f"Fetching image from URL: {url}")
                    response = requests.get(url)
                    response.raise_for_status()
                    image = Image.open(BytesIO(response.content))
                    st.image(image, caption=url, use_column_width=True)
                    images.append((image, url))

                if st.button(f"Analyze Image {idx + 1}"):
                    analyze_single_image(image, url)

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch image from {url}: {str(e)}")
                st.error(f"Failed to fetch image from {url}: {str(e)}")
            except Exception as e:
                logger.exception(f"Error processing image from {url}: {str(e)}")
                st.error(f"Error processing image from {url}: {str(e)}")

    if images:
        if st.button("Analyze All Images"):
            analyze_all_images(images)

    logger.info("Image analysis process completed")


def analyze_single_image(image, url):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OpenAI API key not found")
        st.error(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        )
        return

    with st.spinner(f"Analyzing image from {url[:50]}..."):
        logger.info(f"Analyzing image from URL: {url}")
        temp_image_path = f"temp_image_{hash(url)}.jpg"
        image.save(temp_image_path)
        logger.debug(f"Temporary image saved: {temp_image_path}")

        try:
            analysis_result = analyze_image(temp_image_path, api_key)
            logger.info("Image analysis completed successfully")

            write_analysis_results(analysis_result, url)
            logger.info("Analysis results written to file")

            display_analysis_results(analysis_result)
            logger.info("Analysis results displayed to user")
            return analysis_result
        except Exception as analysis_error:
            logger.exception(f"Error during image analysis: {str(analysis_error)}")
            st.error(f"An error occurred during image analysis: {str(analysis_error)}")
        finally:
            os.remove(temp_image_path)
            logger.debug(f"Temporary image removed: {temp_image_path}")


def analyze_all_images(images):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OpenAI API key not found")
        st.error(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        )
        return

    for image, url in images:
        analyze_single_image(image, url)


def write_analysis_results(result: ImageAnalysisResult, url: str):
    # Ensure the results directory exists
    os.makedirs("./results", exist_ok=True)

    file_path = "./results/image_extraction_result.jsonl"

    # Prepare the data to write
    data = {
        "url": url,
        "description": result.description,
        "text": result.text,
        "emails": result.emails,
        "urls": result.urls,
        "phone_numbers": result.phone_numbers,
        "names": result.names,
        "locations": result.locations,
        "dates": result.dates,
    }

    # Append the results to the file
    with open(file_path, "a+") as f:
        # Move to the end of the file
        f.seek(0, 2)
        # If the file is not empty, add a newline before the new data
        if f.tell() > 0:
            f.write("\n")
        f.write(json.dumps(data))

    st.success(
        f"Analysis results for image from {url} have been appended to {file_path}"
    )


def display_analysis_results(result: ImageAnalysisResult):
    st.write("Image Analysis Results:")
    st.write(f"Description: {result.description}")
    if result.text:
        st.write(f"Extracted Text: {result.text}")
    if result.emails:
        st.write("Emails found:", ", ".join(result.emails))
    if result.urls:
        st.write("URLs found:", ", ".join(result.urls))
    if result.phone_numbers:
        st.write("Phone numbers found:", ", ".join(result.phone_numbers))
    if result.names:
        st.write("Names found:", ", ".join(result.names))
    if result.locations:
        st.write("Locations found:", ", ".join(result.locations))
    if result.dates:
        st.write("Dates found:", ", ".join(result.dates))


@dataclass
class Comment:
    username: str
    user_profile_link: str
    comment_text: str
    timestamp: str
    reactions: int
    replies: Optional[List["Comment"]] = None


def parse_fb_comments() -> List[Comment]:
    html_content = st.session_state["driver"].page_source
    soup = BeautifulSoup(html_content, "html.parser")
    comments = []

    # Find all top-level comment containers
    comment_containers = soup.find_all(
        "div", attrs={"aria-label": re.compile("^Comment by")}
    )

    for container in comment_containers:
        # Extract username and profile link
        user_info = container.find("a", href=re.compile("/user/"))
        if user_info:
            username = user_info.get_text(strip=True)
            user_profile_link = user_info["href"]
        else:
            username = ""
            user_profile_link = ""

        # Extract timestamp
        timestamp_a = container.find("a", href=re.compile("comment_id"))
        timestamp = timestamp_a.get_text(strip=True) if timestamp_a else ""

        # Extract comment text
        comment_text_div = container.find("div", {"dir": "auto"})
        comment_text = (
            comment_text_div.get_text(separator=" ", strip=True)
            if comment_text_div
            else ""
        )

        # Extract reactions count
        reactions_div = container.find(
            "div", {"aria-label": re.compile("^\\d+ reaction")}
        )
        reactions = 0
        if reactions_div and "aria-label" in reactions_div.attrs:
            match = re.search(r"(\d+) reaction", reactions_div["aria-label"])
            if match:
                reactions = int(match.group(1))

        # Parse replies if any
        replies = []
        replies_container = container.find("div", text=re.compile("View \\d+ reply"))
        if replies_container:
            # The replies are often within the next sibling div
            replies_html = replies_container.find_next_sibling("div")
            if replies_html:
                replies.extend(parse_fb_comments(str(replies_html)))

        comments.append(
            Comment(
                username=username,
                user_profile_link=user_profile_link,
                comment_text=comment_text,
                timestamp=timestamp,
                reactions=reactions,
                replies=replies if replies else None,
            )
        )

    return comments


def extract_advert_content_nodiv() -> str:
    """Extract the advertisement content from the HTML page."""
    try:
        html_content = st.session_state["driver"].page_source
        soup = BeautifulSoup(html_content, "html.parser")

        # Find all div elements that contain text
        text_divs = soup.find_all(
            lambda tag: tag.name == "div" and tag.get_text(strip=True)
        )

        # Initialize a set to store unique text contents
        text_contents = set()

        for div in text_divs:
            text = div.get_text(separator="\n").strip()
            if text:
                text_contents.add(text)

        if not text_contents:
            st.warning("No advertisement content found.")
            return ""

        # Combine all text contents
        advert_content = "\n".join(text_contents)

        return advert_content

    except Exception as e:
        st.error(f"An error occurred while extracting advertisement content: {str(e)}")
        return ""


def extract_structured_content(element):
    content = []
    for child in element.children:
        if isinstance(child, NavigableString):
            content.append(child.strip())
        elif child.name in ["br", "p", "div"]:
            content.append("\n")
        else:
            content.append(extract_structured_content(child))
    return " ".join(filter(None, content))


def extract_advert_content() -> str:
    """Extract the advertisement content from the HTML page."""
    try:
        # Assuming st.session_state["driver"].page_source contains the HTML content
        html_content = st.session_state["driver"].page_source
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the div containing the post content
        post_content = soup.find("div", {"data-ad-preview": "message"})
        if not post_content:
            st.warning("Post content could not be found.")
            return ""

        # Extract advert content as plain text
        # advert_content = post_content.get_text(separator="\n").strip()
        # advert_content = post_content.get_text(separator="\n").strip()
        advert_content = (
            post_content.get_text(separator="\n").replace("\n", " ").strip()
        )
        advert_content = post_content.get_text(separator=" ").strip()
        advert_content = re.sub(r"\s+", " ", advert_content)
        return advert_content

    except Exception as e:
        st.error(f"An error occurred while extracting advertisement content: {str(e)}")
        return ""


def find_img_urls() -> List[str]:
    html_content = st.session_state["driver"].page_source
    base_url = st.session_state["driver"].current_url

    soup = BeautifulSoup(html_content, "html.parser")

    # Initialize a set to store unique image URLs
    img_urls = set()

    # Extract from img tags
    for img in soup.find_all("img"):
        if "src" in img.attrs:
            img_urls.add(urljoin(base_url, img["src"]))
        elif "data-src" in img.attrs:
            img_urls.add(urljoin(base_url, img["data-src"]))

    # Extract from meta tags
    for meta in soup.find_all("meta", property="og:image"):
        if "content" in meta.attrs:
            img_urls.add(urljoin(base_url, meta["content"]))

    # Extract from inline styles
    for tag in soup.find_all(style=True):
        style = tag["style"]
        urls = re.findall(r'background-image:\s*url\(["\']?([^"\')]+)["\']?\)', style)
        for url in urls:
            if url.startswith("https://scontent"):
                img_urls.add(urljoin(base_url, url))

    return list(img_urls)


def snapshot():
    st.write(f"Post ID: {st.session_state['post_id']}")
    posters = sp.find_advert_poster()
    # st.write(f"Posters: {posters}")
    st.write(f"Posters: {posters}")
    # advert_text = sp.find_advert_content()
    all_users_and_comments = sp.find_comments_expanded()
    st.write(all_users_and_comments)

    st.write(f"Group name: {st.session_state['group_name']}")

    # Upload comments
    for comment in all_users_and_comments:
        comment["post_id"] = st.session_state["post_id"]
        comment["group_name"] = st.session_state["group_name"]
        result = nl.upload_comment_to_neo4j(comment)
        st.write(result)
        st.write(f"Uploaded comment {comment}")
    st.write("Comments upload completed.")

    # Upload poster information
    for poster in [posters]:
        st.write(f"Uploading poster {poster['poster_info']}")
        payload = poster["poster_info"]
        payload["post_id"] = st.session_state["post_id"]
        payload["group_name"] = st.session_state["group_name"]
        result = nl.upload_post_to_neo4j(payload)
        st.write(result)
        st.write(f"Uploaded post {payload}")
    st.write("Post upload completed.")

    st.write("Upload completed.")
    st.write(posters)


def main():
    st.title("Facebook Advert Pages")
    st.write("This tool helps you investigate Facebook advert pages.")
    st.write(f"The webrowser should be on {st.session_state['driver'].current_url}")
    # Store selected_post_IDn in session state for access across the app
    if "selected_post_IDn" not in st.session_state:
        st.session_state["selected_post_IDn"] = None

    try:
        # Configure grid options
        gb = GridOptionsBuilder.from_dataframe(st.session_state["group_adverts"])

        # Dynamically configure all columns
        for col in st.session_state["group_adverts"].columns:
            # Convert column name to more readable header
            header_name = col.replace("_", " ").title()

            # Configure each column with appropriate settings
            gb.configure_column(
                col,
                header_name=header_name,
                sortable=True,
                filterable=True,
                # Set width based on content type
                width=350 if "url" in col.lower() or "advert" in col.lower() else 150,
            )

        # Configure selection
        gb.configure_selection("single", use_checkbox=True)
        gb.configure_grid_options(domLayout="normal")
        grid_options = gb.build()

        # Display the grid
        grid_response = AgGrid(
            st.session_state["group_adverts"],
            gridOptions=grid_options,
            update_mode="SELECTION_CHANGED",
            height=400,
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
            theme="streamlit",
        )

        # Handle selection
        if grid_response["selected_rows"]:
            selected_row = grid_response["selected_rows"][0]

            # Show selection details
            st.write("**Selected Advertisement:**")
            st.json(selected_row)

            # Create columns for buttons
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Go to Selected Advert"):
                    with st.spinner("Navigating to advertisement..."):
                        try:
                            st.session_state["driver"].get(selected_row["post_url"])
                            time.sleep(5)
                            st.session_state["post_id"] = sp.extract_post_id(
                                st.session_state["driver"].current_url
                            )
                            if not st.session_state["post_id"]:
                                st.error("Could not extract post ID from the URL.")
                            else:
                                st.success(
                                    f"Navigated to post ID: {st.session_state['post_id']}"
                                )
                        except Exception as e:
                            st.error(f"Navigation error: {str(e)}")

            with col2:
                if st.button("Show Advert Details"):
                    # Dynamically display all fields except URL
                    for field, value in selected_row.items():
                        if "url" not in field.lower():
                            st.write(f"{field.replace('_', ' ').title()}: {value}")

    except Exception as e:
        st.error(f"Error setting up or displaying grid: {str(e)}")
        st.write("Exception details:", e)

    # Separate section for general actions
    st.markdown("---")
    st.subheader("Advertisement Actions")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Take snapshot and upload to Neo4J"):
            snapshot()

        if st.button("Extract advert content"):
            advert_text = extract_advert_content()
            advert_detail = sp.find_advert_poster()

        if st.button("Take snapshot and upload to Neo4J"):
            snapshot()

        if st.button("Extract advert content"):
            advert_text = extract_advert_content()
            advert_detail = sp.find_advert_poster()
            st.write(advert_detail)
            if advert_text:
                st.write(advert_text)
            else:
                st.write("No advertisement content found.")

        if st.button("Alternative content extraction"):
            advert_detail = sp.find_advert_poster_alt()
            st.write(advert_detail)

        if st.button("Extract advert content without div"):
            nodiv_content = extract_advert_content_nodiv()
            if nodiv_content:
                st.write(nodiv_content)
            else:
                st.write("No advertisement content found.")

        with col2:
            if st.button("Extract comments"):
                comments = parse_fb_comments()
                for comment in comments:
                    st.write(comment)

        # Image analysis section
        st.markdown("---")
        st.subheader("Image Analysis")

        if st.button("Extract and Analyze Images"):
            analyze_images()

        if st.button("Extract image URLs"):
            st.session_state["img_urls"] = find_img_urls()

            if st.session_state["img_urls"]:
                st.write("Image URLs:")
                for url in st.session_state["img_urls"]:
                    st.write(url)

                st.title("Display Images from HTML")
                for url in st.session_state["img_urls"]:
                    st.write(f"Fetching image from: {url}")
                    try:
                        if url.startswith("data:"):
                            # Handle data URIs
                            # Split the data URI into metadata and data
                            match = re.match(
                                r"data:(?P<mime>.*?)(;charset=(?P<charset>.*?))?(;base64)?,(?P<data>.*)",
                                url,
                                re.DOTALL,
                            )
                            if match:
                                mime_type = match.group("mime")
                                data = match.group("data")
                                is_base64 = ";base64" in url

                                # SVG handling
                                if "svg+xml" in mime_type:
                                    if is_base64:
                                        # Decode Base64-encoded SVG data
                                        svg_data = base64.b64decode(data).decode(
                                            "utf-8"
                                        )
                                    else:
                                        # Decode URL-encoded SVG data
                                        svg_data = unquote(data)
                                    # Display the SVG using st.image or st.markdown
                                    st.markdown(
                                        f"<div>{svg_data}</div>", unsafe_allow_html=True
                                    )
                                else:
                                    # Handle other image types
                                    if is_base64:
                                        # Decode Base64-encoded data
                                        image_data = base64.b64decode(data)
                                    else:
                                        # Decode URL-encoded data
                                        image_data = unquote(data).encode("utf-8")
                                    # Open image with PIL
                                    image = Image.open(BytesIO(image_data))
                                    # Display image in Streamlit
                                    st.image(
                                        image,
                                        caption="Image from data URI",
                                        use_column_width=True,
                                    )
                            else:
                                st.error(f"Invalid data URI: {url}")
                        else:
                            # Fetch image content from the web
                            response = requests.get(url)
                            response.raise_for_status()
                            # Open image with PIL
                            image = Image.open(BytesIO(response.content))
                            # Display image in Streamlit
                            st.image(image, caption=url, use_column_width=True)
                    except requests.exceptions.RequestException as e:
                        st.error(f"Failed to fetch image from {url}: {e}")
                    except Exception as e:
                        st.error(f"Error displaying image from {url}: {e}")

        if "img_urls" in st.session_state:
            st.selectbox(
                "Select img to analyze:",
                st.session_state["img_urls"],
                index=0,
                key="selected_img",  # This links the selectbox directly to the session state variable
            )

        if ("selected_img" in st.session_state) and (
            st.session_state["selected_img"] is not None
        ):
            if st.button(f"Analyze {st.session_state['selected_img']}"):
                st.write(f"Analyze {st.session_state['selected_img']}")
                response = requests.get(st.session_state["selected_img"])
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
                st.image(
                    image,
                    caption=st.session_state["selected_img"],
                    use_column_width=True,
                )
                st.session_state["analysis_result"] = analyze_single_image(
                    image, st.session_state["selected_img"]
                )
                st.write(st.session_state["analysis_result"])

            if (
                "selected_img" in st.session_state
                and st.session_state["selected_img"] is not None
                and st.session_state.get("selected_post_IDn")
            ):
                if "analysis_result" in st.session_state:
                    if st.button("Upload analysis results to Neo4J"):
                        create_image_url_relationships(
                            st.session_state["selected_post_IDn"],
                            st.session_state["analysis_result"],
                        )

        else:
            st.write("No img selected.")


if __name__ == "__main__":
    main()
