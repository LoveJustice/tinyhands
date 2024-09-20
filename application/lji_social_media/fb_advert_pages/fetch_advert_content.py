import streamlit as st
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import libraries.neo4j_lib as nl
from social_media.social_media import is_facebook_groups_url
import libraries.search_patterns as sp
from random import randint
import time
from selenium.webdriver.support import expected_conditions as EC
import random
import social_media.social_media as sm
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from typing import List, Dict, Optional
from typing import Dict
from bs4 import BeautifulSoup


def fetch_advert_data():
    neo4j_query = """MATCH (posting:Posting) 
    RETURN ID(posting) AS IDn,
    posting.post_id AS post_id, 
    posting.text AS post_text, 
    posting.post_url AS post_url 
    ORDER BY post_id;"""
    return pd.DataFrame(nl.execute_neo4j_query(neo4j_query, {}))


def postings_to_neo4j(post_matches):
    if is_facebook_groups_url(st.session_state["driver"].current_url):
        st.write(
            "Upload all posts on group page to Neo4J:  The URL is a valid Facebook groups URL."
        )

        st.write(f"Post matches: {post_matches}")

        for post_match in post_matches:
            st.write(
                f"Post match; group_id: {post_match['group_id']}, post_id: {post_match['post_id']}"
            )
            nl.post_to_neo4j(post_match)
    else:
        st.write("The URL does not match the required Facebook groups format.")


def sample_group_page(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_length = random.uniform(0.5, 0.9) * last_height
    _, _, post_matches = sp.list_all_users()
    # postings_to_neo4j(post_matches)
    st.write(f"last_height: {last_height}")
    st.write(f"scroll_length: {scroll_length}")
    st.write(f"Post matches: {post_matches}")


def sample_advert_page():
    post_id = sp.extract_post_id(st.session_state["driver"].current_url)
    st.write(f"Post ID: {post_id}")
    # Wait for the element with ID 'MANIFEST_LINK' to be present
    st.write(f"New advert URL: {st.session_state['driver'].current_url}")
    advert_poster = sp.find_advert_poster()
    st.write(f"Advert poster: {advert_poster}")
    advert_text = sp.find_advert_content()
    st.write(f"Advert text: {advert_text}")


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
        _, _, post_matches = sp.list_all_users()
        postings_to_neo4j(post_matches)
        # Update the last height for next loop
        last_height = new_height

    # Return the final scroll height
    return last_height


def main():
    # Fetch the advert content
    st.write(f"The webrowser should be on {st.session_state['driver'].current_url}")
    st.write(pd.DataFrame(st.session_state["group_adverts"]))
    st.selectbox(
        "Select an advert:",
        st.session_state["group_adverts"]["post_url"],
        key="selected_advert",
    )
    if st.button("Proceed with selected advert"):
        if st.session_state["selected_advert"] is not None:
            st.write(f"You selected the group: {st.session_state['selected_group']}")
            # Fetch the corresponding URL for the selected group
            selected_advert = (
                st.session_state["group_adverts"]
                .loc[
                    st.session_state["group_adverts"]["post_url"]
                    == st.session_state["selected_advert"],
                    "post_url",
                ]
                .values[0]
            )

            # Display or execute the action
            st.write(
                f"Opening URL: {st.session_state['selected_advert']} with content {selected_advert}"
            )
            st.session_state["driver"].get(st.session_state["selected_advert"])
            # Example action
    if st.button("Sample current GROUP page:"):
        sample_group_page(st.session_state["driver"])

    if st.button("Sample current ADVERT page:"):
        sample_advert_page()

    if st.button("Upload all posts on group page to Neo4J"):
        st.write(st.session_state["driver"].current_url)
        if sm.is_facebook_groups_url(st.session_state["driver"].current_url):
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

    if st.button("Update_new_adverts"):
        try:
            new_adverts_urls = nl.all_new_adverts_urls(
                st.session_state["driver"].current_url
            )
            original_url = st.session_state["driver"].current_url
            st.write(f"Original URL: {original_url}")
            st.write(new_adverts_urls)
            wait = WebDriverWait(st.session_state["driver"], 30)
            entries = []
            for new_advert_url in new_adverts_urls:
                st.session_state["driver"].get(new_advert_url["post_url"])
                post_id = sp.extract_post_id(new_advert_url["post_url"])
                # Wait for the element with ID 'MANIFEST_LINK' to be present
                element = wait.until(
                    EC.presence_of_element_located((By.ID, "MANIFEST_LINK"))
                )
                st.write(f"New advert URL: {new_advert_url['post_url']}")
                # advert_poster = sp.find_advert_poster()
                advert_detail = sp.find_advert_poster()
                st.write(f"Advert poster: {advert_detail}")
                if advert_detail:
                    poster = advert_detail["poster_info"]

                    advert_text = advert_detail["advert_content"]

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
                    # pd.DataFrame(entries).to_csv("results/new_entries.csv", index=False)
                    nl.execute_neo4j_query(query, parameters)
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
                    posters = sp.find_advert_poster()  # [(name, group_id, user_id)]
                    advert_text = sp.find_advert_content()
                    comments = sp.find_comments_expanded()
                    all_users_and_comments = sp.list_all_users_and_comments()
                    st.write(f"Comments: {comments}")
                    st.write(f"All users and comments: {all_users_and_comments}")
                    st.write(f"Advert: {advert_text}")

                except TimeoutException:
                    # Handle the case where the element is not found within the specified time
                    st.error(
                        "Failed to find the required element within the time limit."
                    )
        if st.button("Extract advert"):
            posters = sp.find_advert_poster()  # [(name, group_id, user_id)]
            poster_inside = sp.find_advert_poster_inside()
            advert_text = sp.find_advert_content()
            st.write(f"Advert text: {advert_text}; Posters: {posters}")
            st.write(f"Posters inside: {poster_inside}")

        if st.button("Extract comments"):
            all_users_and_comments = sp.find_comments_expanded()
            st.write(f"All users and comments: {all_users_and_comments}")

        if st.button("find poster"):
            posters = sp.find_advert_poster()
            st.write(f"Posters: {posters}")

        if st.button("find inside poster"):
            posters = sp.find_advert_poster_inside()
            st.write(f"Inside Posters: {posters}")


if __name__ == "__main__":
    main()
