import json
import pandas as pd
from pathlib import Path

path_to_har = Path("~/Downloads/AirRoll friends.har").expanduser()
# Load HAR file
with open(path_to_har, "r") as f:
    har_data = json.load(f)

# Parse the HAR data
entries = har_data["log"]["entries"]
# https://scontent-jnb1-1.xx.fbcdn.net/v/t39.30808-1/278057717_1339044126596265_3717750557938261734_n.jpg?stp=c0.0.160.160a_dst-jpg_p160x160&_nc_cat=101&ccb=1-7&_nc_sid=5f2048&_nc_ohc=c2JcMwa871wAX9bnkDA&_nc_ht=scontent-jnb1-1.xx&oh=00_AfDhYlNx4EDV5cPdfB3s1fFmc_qAkxJZmAjbJjDZrU2v8w&oe=6561ED83
# Create a DataFrame
df = pd.DataFrame(
    [
        {
            "startedDateTime": entry["startedDateTime"],
            "url": entry["request"]["url"],
            "status": entry["response"]["status"],
            "time": entry["time"],
            "responseSize": entry["response"]["bodySize"],
        }
        for entry in entries
    ]
)

# Basic analysis
print(df.describe())

# You can perform more detailed analysis, filtering, graphing, etc., as needed
import urllib.parse
import json


# Function to extract query parameters that might contain user identifiers
def extract_query_params(url):
    query_params = {}
    parsed_url = urllib.parse.urlparse(url)
    query_pairs = urllib.parse.parse_qs(parsed_url.query)
    for key, value in query_pairs.items():
        # Assuming identifiers might be numeric or alphanumeric strings
        if value and (value[0].isdigit() or (len(value[0]) > 5 and value[0].isalnum())):
            query_params[key] = value[0]
    return query_params


# Path to the HAR file
har_file_path = Path("~/Downloads/AirRoll posts.har").expanduser()

# Read the HAR file and load it as a JSON object
with open(har_file_path, "r") as file:
    har_data = json.load(file)

# Extract the entries from the HAR data
entries = har_data["log"]["entries"]
# Enhanced search for Facebook user profile identifiers in URLs and query parameters
facebook_identifiers = set()

for entry in entries:
    url = entry.get("request", {}).get("url", "")
    if "facebook.com" in url:
        # Extracting query parameters
        params = extract_query_params(url)
        for param, value in params.items():
            facebook_identifiers.add((param, value))

# Displaying the found identifiers (if any)
facebook_identifiers
