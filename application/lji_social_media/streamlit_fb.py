import streamlit as st
from social_media.social_media import (
    facebook_connect,
    find_search_urls,
    find_friend_urls,
)
import re
import gspread
from pathlib import Path
import time
from random import randint
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Path to the JSON key file
key_file = Path("SL_Access/facematcher_creds.json")

# Google Sheet information
google_sheet_name = "Sheet1"
# Authenticate using the JSON key file
gc = gspread.service_account(filename=key_file)
google_spreadsheet_name = "facebook links"
# Open the Google Sheet

worksheet = gc.open(google_spreadsheet_name).worksheet(google_sheet_name)

# Read the contents of column A into a list
links = worksheet.col_values(1)


def scroll_down(driver, sleep_time=5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    last_height = driver.execute_script("return document.body.scrollHeight")
    # Wait to load the page
    time.sleep(sleep_time)
    # logging.info(f"Scrolling: {scroll}")

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        return
    return (last_height, new_height)


if "connected" not in st.session_state:
    st.session_state["connected"] = False

# Check if the driver is already initialized
if "driver" not in st.session_state:
    st.session_state["driver"] = None

# Connect button
if st.button("Connect") and not st.session_state["connected"]:
    st.write("Check your browser!")
    driver = facebook_connect()
    st.session_state["driver"] = driver
    st.session_state["connected"] = True
    st.write("You are now connected!")

# Check if the page is already loaded
if "page_loaded" not in st.session_state:
    st.session_state["page_loaded"] = False

# Check if the last selected link is stored
if "last_selected_link" not in st.session_state:
    st.session_state["last_selected_link"] = None


if st.session_state["connected"]:
    selected_link = st.selectbox("Select a link below", links, key="selected_link")
    selected_link = "/".join(selected_link.split("/")[0:5])
    if selected_link:
        st.write(f"You chose {selected_link}!")

        # Check if the selected link has changed
        if st.session_state["last_selected_link"] != selected_link:
            st.session_state["page_loaded"] = False

        # Load the page if not already loaded
        if not st.session_state["page_loaded"]:
            st.session_state["driver"].get(selected_link)
            st.session_state["page_loaded"] = True

        # Store the current selected link as the last selected link
        st.session_state["last_selected_link"] = selected_link
        wait = WebDriverWait(st.session_state["driver"], 10)
        # Find all comments elements
        raw_elements = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//span[contains(text(), 'comment')]")
            )
        )
        comments_elements = [
            element
            for element in raw_elements
            if re.match(r"^\d+ comments?$", element.text)
        ]
        main_page = st.session_state["driver"].current_window_handle
        st.write(f"main_page: {main_page}")
        # Check if comments_elements is not empty before accessing the first element
        if comments_elements:
            st.write(f"Found {len(comments_elements)} comments elements")
            for comment_element in comments_elements:
                pass
                # element_text = comment_element.text
                # # Use regular expression to match text format '{n} comment' or '{n} comments'
                # if re.match(r'^\d+ comments?$', element_text):
                #     st.write(f'element.text: {element_text}')
                #     class_attribute = comment_element.get_attribute('class')
                #     st.write(f'class_attribute: {class_attribute}')
                #
                #     # Scroll the element into view
                #     st.session_state['driver'].execute_script("arguments[0].scrollIntoView();", comment_element)
                #
                #     # Click the element
                #     try:
                #         # Wait for the element to be clickable
                #         wait.until(EC.element_to_be_clickable(
                #             (By.XPATH, "//span[contains(text(), 'comment') and text() = '{}']".format(element_text))))
                #         # Perform action, e.g., click to expand comments
                #         st.write('comment_element.click()')
                #         # Optionally add sleep to simulate user behavior
                #         time.sleep(2)
                #     except Exception as e:
                #         # If normal click fails, try clicking with JavaScript
                #         try:
                #             st.session_state['driver'].execute_script("arguments[0].click();", comment_element)
                #         except Exception as js_exception:
                #             st.write(f"Could not click on the element: {js_exception}")

        # Get the first element

        else:
            st.write("No comments elements found")

        # Scroll down button
        if st.button("Scroll down"):
            try:
                st.write("Check your browser!")
                scroll_down(st.session_state["driver"], sleep_time=randint(1, 5))
                this_page = st.session_state["driver"].current_window_handle
                st.write(f"this_page: {this_page}")
                with open(
                    Path("data_sources/page_source.html"), "w", encoding="utf-8"
                ) as f:
                    f.write(st.session_state["driver"].page_source)
            except TimeoutException:
                st.write("The elements were not found within the specified timeout.")

        # Click comments button
        if st.button("Click comments"):
            try:
                # Wait for comments element to be present
                element = comments_elements[0]
                element_text = element.text

                # Scroll the element into view
                st.session_state["driver"].execute_script(
                    "arguments[0].scrollIntoView();", element
                )

                # Wait for the element to be clickable
                wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//span[contains(text(), 'comment') and text() = '{}']".format(
                                element_text
                            ),
                        )
                    )
                )
                with open(
                    Path("data_sources/click_comments.html"), "w", encoding="utf-8"
                ) as f:
                    f.write(st.session_state["driver"].page_source)
                # Perform action, e.g., click to expand comments
                try:
                    # Try clicking normally
                    element.click()
                except Exception as normal_click_exception:
                    # If normal click fails, try clicking with JavaScript
                    st.session_state["driver"].execute_script(
                        "arguments[0].click();", element
                    )

                # Optionally, add a sleep between actions to simulate user behavior and avoid being blocked
                time.sleep(2)
                driver = st.session_state["driver"]
                try:
                    # Locate the element by its class attributes
                    # Iterate through all window handles
                    for handle in st.session_state["driver"].window_handles:
                        st.write(f"handle: {handle}")

                        # Switch to the window with the given handle
                        st.session_state["driver"].switch_to.window(handle)

                        # Perform actions within the window, e.g., finding elements, clicking, etc.
                        # For example, printing the title of each window:
                        st.write(
                            f"Title of window with handle {handle}: {st.session_state['driver'].title}"
                        )

                    comments_page = st.session_state["driver"].current_window_handle
                    st.write(f"comments_page: {comments_page}")
                    # see_more_element = driver.find_element_by_css_selector(
                    #     '.x1i10hfl.xjbqb8w.x6umtig.x1b1mbwd.xaqea5y.xav7gou.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.xt0b8zv.xzsf02u.x1s688f')
                    # see_more_element = driver.find_element_by_xpath(
                    #     "//div[contains(@class, 'x1i10hfl') and contains(text(), 'See more')]")
                    wait = WebDriverWait(driver, 10)
                    see_more_element = driver.find_element(
                        By.CSS_SELECTOR, ".x1i10hfl.xjbqb8w"
                    )
                    # driver.execute_script("arguments[0].scrollIntoView();", see_more_element)
                    # see_more_element.click()

                    # see_more_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                    #                                                           '.x1i10hfl.xjbqb8w.x6umtig.x1b1mbwd.xaqea5y.xav7gou.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.xt0b8zv.xzsf02u.x1s688f')))
                    # see_more_element.click()

                    # Optionally, add a sleep between actions to simulate user behavior and avoid being blocked
                    time.sleep(2)

                except Exception as e:
                    st.write(f"Could not click on the 'See more' element: {e}")

                # Get and display the heading text
                try:
                    # heading_element = driver.find_element(By.CSS_SELECTOR, '#mount_0_0_gb > div > div:nth-child(1) > div > div:nth-child(7) > div > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div.x1uvtmcs.x4k7w5x.x1h91t0o.x1beo9mf.xaigb6o.x12ejxvf.x3igimt.xarpa2k.xedcshv.x1lytzrv.x1t2pt76.x7ja8zs.x1n2onr6.x1qrby5j.x1jfb8zj > div > div > div > div > div > div > div:nth-child(1) > div')
                    # driver.execute_script("arguments[0].scrollIntoView();", heading_element)
                    comments_page = st.session_state["driver"].current_window_handle
                    st.write(f"comments_page: {comments_page}")
                    # heading_element.click()
                    # # Locate the heading element by its class attributes
                    # heading_element = driver.find_element_by_css_selector(
                    #     '.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6.xlyipyv.xuxw1ft')

                    # Extract the text from the heading element
                    # heading_text = heading_element.text

                    # Display the heading text
                    # st.write(f"Heading text: {heading_text}")

                except Exception as e:
                    st.write(f"Could not extract heading text: {e}")

                time.sleep(2)

                # Close comments if the Close comments button is clicked
                if st.button("Close comments"):
                    close_button = st.session_state["driver"].find_element_by_xpath(
                        "//div[@aria-label='Close']"
                    )
                    close_button.click()
                    time.sleep(2)
            except Exception as e:
                st.write(f"Could not interact with element: {e}")

        # Quit browser button
        if st.button("Quit browser"):
            st.session_state["driver"].quit()
            st.session_state["connected"] = False
            st.session_state["page_loaded"] = False
            st.write("Browser closed!")
    else:
        st.write("No URL selected")
