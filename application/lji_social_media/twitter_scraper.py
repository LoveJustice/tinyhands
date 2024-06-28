# Import the selenium library for web automation
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.chrome.options import Options

# Create a Chrome driver object with the path to the chromedriver executable
path_to_chromedriver = "~/Downloads/chromedriver-mac-arm64/chromedriver"
options = Options()
service = Service(path_to_chromedriver)
# service = Service(ChromeDriverManager().install())
# Use ChromeDriverManager to handle the driver's installation and path
driver = webdriver.Chrome(service=service, options=options)
# Maximize the browser window
driver.maximize_window()
# Navigate to the Twitter search page with the query "large language model"
driver.get("https://twitter.com/search?q=large%20language%20models&src=typed_query")
# Wait for 10 seconds to load the page
time.sleep(10)

# Find all the elements that have the attribute "lang" (which indicates a tweet)
elements = driver.find_elements_by_xpath("//div[@lang]")
# Loop through each element and print its text content
for element in elements:
    print(element.text)

# Close the browser and quit the driver
driver.quit()
