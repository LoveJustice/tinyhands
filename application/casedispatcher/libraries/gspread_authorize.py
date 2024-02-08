import json
from pathlib import Path
import gspread
from oauth2client.client import OAuth2WebServerFlow, Storage

# Opening JSON file
f = open(
    Path(
        "client_secret_501273095419-bo0ohkl9vmg0eqg348jpdfnm53u1atis.apps.googleusercontent.com.json"
    ),
    "r",
)

# returns JSON object as
# a dictionary
with open(
    Path(
        "client_secret_501273095419-bo0ohkl9vmg0eqg348jpdfnm53u1atis.apps.googleusercontent.com.json"
    ),
    "r",
) as file:
    data = json.load(file)
    credentials_data = data["installed"]
CLIENT_ID = credentials_data["client_id"]
CLIENT_SECRET = credentials_data["client_secret"]
REDIRECT_URI = credentials_data["redirect_uris"][0]  # Use the first redirect URI listed
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
]

flow = OAuth2WebServerFlow(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope=SCOPE,
    redirect_uri=REDIRECT_URI,
)
auth_uri = flow.step1_get_authorize_url()

print("Visit this URL to authenticate:")
print(auth_uri)

auth_code = input("Enter the authentication code: ")
credentials = flow.step2_exchange(auth_code)

# Save the credentials for future use
with open("token.json", "w") as token_file:
    token_file.write(credentials.to_json())

# Authorize gspread with these credentials
gc = gspread.authorize(credentials)

data["installed"].keys()
# This is the scope for Google Sheets API
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
]

# flow = OAuth2WebServerFlow(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scope=SCOPE)
flow = OAuth2WebServerFlow(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scope=SCOPE,
    redirect_uri="urn:ietf:wg:oauth:2.0:oob",
)
auth_uri = flow.step1_get_authorize_url()

print("Visit this URL to authenticate:")
print(auth_uri)

auth_code = input("Enter the authentication code: ")
credentials = flow.step2_exchange(auth_code)

# Save the credentials for future use
with open("token.json", "w") as token_file:
    token_file.write(credentials.to_json())

# Authorize gspread with these credentials
gc = gspread.authorize(credentials)
