from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from random import randint
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import logging

# Example usage:


# driver = webdriver.Chrome(ChromeDriverManager(version="114.0.5735.90").install())
# driver.quit()
def find_search_urls(driver, name):
    url = f"https://www.facebook.com/search/people/?q={name}"
    driver.get(url)
    time.sleep(randint(3, 6))
    scroll_to_bottom(driver)

    try:
        # Try locating the people section
        # people_section = driver.find_element_by_css_selector('span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6')

        # Try finding all 'a' tags (links) within the people section
        links = driver.find_elements_by_xpath(
            "//a[contains(@href, 'https://www.facebook.com/')]"
        )
        urls = [
            link.get_attribute("href") for link in links if link.get_attribute("href")
        ]
        for url in urls:
            print(url)
    except Exception as e:
        print(f"An error occurred: {e}")
        urls = []  # Return an empty list if an error occurs

    time.sleep(randint(3, 10))
    return urls


# def find_search_urls(driver, name):
#     url = f"https://www.facebook.com/search/people/?q={name}"
#     driver.get(url)
#     time.sleep(randint(3,6))
#     scroll_to_bottom(driver)
#     links = driver.find_elements_by_css_selector(
#         "a.x1i10hfl.xjbqb8w.x6umtig.x1b1mbwd.xaqea5y.xav7gou.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.xt0b8zv.xzsf02u.x1s688f"
#     )
#
#     # print the href attribute of each 'a' tag
#     urls = []
#     for link in links:
#         # print(link.get_attribute('href'))
#         urls.append(link.get_attribute("href"))
#     time.sleep(randint(3,10))
#     return urls


def find_friend_urls(driver, search_urls):
    friend_urls = []
    for url in search_urls:
        driver.get(url + "/friends")
        time.sleep(5)
        scroll_to_bottom(driver)
        links = driver.find_elements_by_css_selector(
            "a.x1i10hfl.xjbqb8w.x6umtig.x1b1mbwd.xaqea5y.xav7gou.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.x1heor9g.xt0b8zv"
        )
        for link in links:
            # print(link.get_attribute('href'))
            friend_urls.append((url, link.get_attribute("href")))
    return friend_urls


def find_profile_links(driver, group_id):
    target_url = f"https://www.facebook.com/groups/{group_id}"
    driver.get(target_url)
    time.sleep(10)
    scroll_to_bottom(driver)
    time.sleep(2)
    # Wait for the results to render (use an appropriate locator or condition)

    scroll_to_bottom(driver)

    profile_link_selector = "a.x1i10hfl.xjbqb8w"
    all_profile_links = driver.find_elements(By.CSS_SELECTOR, profile_link_selector)
    profile_links = []
    # Iterate through the profile links and extract the URLs
    for profile_link in all_profile_links:
        user_profile_url = profile_link.get_attribute("href")
        profile_links.append(user_profile_url)
        print(user_profile_url)
    return profile_links


def find_admin_links(driver, group_id):
    target_url = f"https://www.facebook.com/groups/{group_id}/members/admins"
    driver.get(target_url)
    time.sleep(10)
    scroll_to_bottom(driver)
    time.sleep(2)
    # Wait for the results to render (use an appropriate locator or condition)

    # Locate all elements containing the links
    link_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'x1i10hfl')]")
    heading_element = driver.find_element(
        By.CSS_SELECTOR, "span.x1lliihq.x6ikm8r.x10wlt62.x1n2onr6"
    )
    heading_y = heading_element.location_once_scrolled_into_view["y"]
    # Find the index of the heading element in the list of link elements
    heading_index = -1
    for i, link_element in enumerate(link_elements):
        link_y = link_element.location_once_scrolled_into_view["y"]
        if link_y > heading_y:
            heading_index = i
            break

    # Extract the links after the heading element
    links = []
    for link_element in link_elements[heading_index:]:
        link = link_element.get_attribute("href")
        links.append(link)
    print(links)
    return links


def scroll_to_page_bottom(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Adjust the sleep time as needed


def scroll_to_bottom(driver, sleep_time=5, max_scrolls=20):
    logging.basicConfig(level=logging.INFO)

    # Get scroll height
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll = 0
        while True:
            # Scroll down to the bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load the page
            time.sleep(sleep_time)
            scroll += 1
            logging.info(f"Scrolling: {scroll}")

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height or scroll == max_scrolls:
                break
            last_height = new_height

    except TimeoutException as ex:
        logging.error("TimeoutException while scrolling: %s", ex)


def collect_data(driver):
    post_containers = driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')
    post_data = []
    comment_data = []
    for post_container in post_containers:
        # Check if this is a post or a comment
        aria_label = post_container.get_attribute("aria-label")
        if aria_label and "Comment by" in aria_label:
            # This is a comment
            try:
                profile_link_selector = "a.x1i10hfl.xjbqb8w"
                profile_link = post_container.find_element(
                    By.CSS_SELECTOR, profile_link_selector
                )
                user_profile_url = profile_link.get_attribute("href")
            except NoSuchElementException:
                user_profile_url = None

            try:
                post_selector = 'div[dir="auto"][style="text-align: start;"]'
                post_element = post_container.find_element(
                    By.CSS_SELECTOR, post_selector
                )
                comment_text = post_element.text
            except NoSuchElementException:
                comment_text = None
            post_data.append((user_profile_url, comment_text))
            print(f"User profile URL: {user_profile_url}")
            print(f"Comment text: {comment_text}")
            print()
        else:
            # This is a post
            try:
                profile_link_selector = "a.x1i10hfl.xjbqb8w"
                profile_link = post_container.find_element(
                    By.CSS_SELECTOR, profile_link_selector
                )
                user_profile_url = profile_link.get_attribute("href")
            except NoSuchElementException:
                user_profile_url = None

            try:
                post_selector = 'div[dir="auto"][style="text-align: start;"]'
                post_element = post_container.find_element(
                    By.CSS_SELECTOR, post_selector
                )
                post_text = post_element.text
            except NoSuchElementException:
                post_text = None
            comment_data.append((user_profile_url, post_text))
            print(f"User profile URL: {user_profile_url}")
            print(f"Post text: {post_text}")
            print()

    return post_data, comment_data


def scroll_and_collect_data(driver, group_id, n):
    target_url = f"https://www.facebook.com/groups/{group_id}"
    driver.get(target_url)
    time.sleep(10)
    all_post_data = []
    all_comment_data = []
    for _ in range(n):
        scroll_to_page_bottom(driver)
        post_data, comment_data = collect_data(driver)
        all_post_data.extend(post_data)
        all_comment_data.extend(comment_data)
    return all_post_data, all_comment_data


def facebook_connect():
    # driver = webdriver.Chrome(ChromeDriverManager().install())
    # instance of Options class allows
    # us to configure Headless Chrome
    options = Options()

    # this parameter tells Chrome that
    # it should be run without UI (Headless)
    options.headless = False

    # initializing webdriver for Chrome with our options
    # driver = webdriver.Chrome(options=options)

    options = webdriver.ChromeOptions()
    options.headless = False
    path_to_chromedriver = "/opt/homebrew/bin/chromedriver"
    service = Service(path_to_chromedriver)
    # service = Service(ChromeDriverManager().install())
    # Use ChromeDriverManager to handle the driver's installation and path
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.get("https://www.facebook.com/")
    time.sleep(randint(3, 5))
    username = driver.find_element(By.XPATH, "//input[@type='text']")
    username.send_keys(os.environ.get("LJI_FB_USER"))
    time.sleep(randint(3, 5))
    password = driver.find_element(By.XPATH, "//input[@type='password']")
    password.send_keys(os.environ.get("LJI_FB_PWD"))
    time.sleep(randint(3, 5))
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()
    time.sleep(randint(3, 5))
    return driver
