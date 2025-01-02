import json
import streamlit as st
from googleapiclient.discovery import build
from oauth2client.client import OAuth2Credentials
from libraries.google_lib import (
    attrdict_to_dict,
    get_file_id,
    load_from_cloud,
    load_model_and_columns,
)
import pickle


# To reload the dictionary later:
def load_sheet_columns(filename="sheet_columns.pkl"):
    with open(filename, "rb") as file:
        sheet_columns_dict = pickle.load(file)
    return sheet_columns_dict


sheet_columns_dict = load_sheet_columns()
for key, value in sheet_columns_dict.items():
    print(key, value)


case_dispatcher = st.secrets["case_dispatcher"]
access_token = case_dispatcher["access_token"]
toml_config_dict = attrdict_to_dict(access_token)
creds_json = json.dumps(toml_config_dict)
credentials = OAuth2Credentials.from_json(creds_json)
drive_service = build("drive", "v3", credentials=credentials)
(
    case_dispatcher_model,
    case_dispatcher_model_cols,
    case_dispatcher_soc_df,
) = load_model_and_columns(
    drive_service,
    "case_dispatcher_model.pkl",
    "case_dispatcher_model_cols.pkl",
    "case_dispatcher_soc_df.pkl",
)


def get_dtype_mapping(cols):
    # Only include specific columns in the dtype mapping
    dtype_map = {
        "age": "int64",
        "number_of_victims": "int64",
        "number_of_traffickers": "int64",
    }
    # Assuming all other columns in cols should be boolean
    for col in cols:
        if col not in dtype_map:
            dtype_map[col] = "bool"
    return dtype_map


dtype_map = get_dtype_mapping(case_dispatcher_model_cols)
case_dispatcher_soc_df[case_dispatcher_model_cols].dtypes


import streamlit as st
import json
from googleapiclient.discovery import build
from oauth2client.client import OAuth2Credentials

import pickle
from libraries.case_dispatcher_data import (
    get_vdf,
    get_suspects,
    get_irf,
    get_suspect_evaluations,
    get_countries,
)
from libraries.google_lib import (
    get_gsheets,
    get_dfs,
    attrdict_to_dict,
    make_file_bytes,
    save_to_cloud,
    load_data,
    get_matching_spreadsheets,
)
import gspread
import dotenv
import os

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)


case_dispatcher = st.secrets["case_dispatcher"]
access_token = case_dispatcher["access_token"]


toml_config_dict = attrdict_to_dict(access_token)
creds_json = json.dumps(toml_config_dict)
credentials = OAuth2Credentials.from_json(creds_json)
service = build("sheets", "v4", credentials=credentials)
workbook_name = "Case Dispatcher 6.0 - Uganda"

"""Return a list of Google worksheets along with the workbook's link and file ID."""
gc = gspread.authorize(credentials)

# Open the workbook
workbook = gc.open(workbook_name)

# Get the file ID and URL from the workbook
file_id = workbook.id
file_url = workbook.url

# Get the worksheets


def get_weights(weights_sheet, range_name):
    result = weights_sheet.get_values(range_name)
    weights = {}
    for idx in range(1, len(result[0])):
        weights[result[0][idx]] = float(result[1][idx])
    return weights


def get_all_weights(range_names):
    weights_sheet = workbook.worksheet("weights")
    weights = {}
    for range_name in range_names:
        weights[range_name] = get_weights(weights_sheet, range_name)
    return weights


range_names = [
    "priority_weights",
    "recency_vars",
    "exploitation_type",
    "solvability_weights",
    "pv_believes",
]
all_weights = get_all_weights(range_names)
result = weights_sheet.get_values("priority_weights")
weights = {}
for idx in range(1, len(result[0])):
    weights[result[0][idx]] = float(result[1][idx])


spreadsheet_id = os.environ["WEIGHTS_ID"]
# Make sure your environment variable is correctly set
named_range = "priority_weights"  #

# Fetch the values from the named range
result = (
    service.spreadsheets()
    .values()
    .get(spreadsheetId=spreadsheet_id, range=named_range)
    .execute()
)

# Get values
values = result.get("values", [])

# Check if values were found and print them
if not values:
    print("No data found.")
else:
    for row in values:
        print(row)  # Each 'row' corresponds to a row of data in your named range

weights = {}
for idx in range(1, len(values[0])):
    weights[values[0][idx]] = float(values[1][idx])

    print(row)  # Each 'row' corresponds to a row of data in your named range
values[0]
range_data = service.spreadsheets().values_get("priority_weights").execute()


def read_from_sheet(tab: str, named_range: str):
    # Construct the range name
    RANGE_NAME = f"{tab}!{named_range}"

    # Use the Sheets API to get the data
    request = (
        SERVICE.spreadsheets()
        .values()
        .get(spreadsheetId=KORRIDORBOT_UI_FEEDBACK_ID, range=RANGE_NAME)
    )
    response = request.execute()

    # The data returned is in 'values' key if the range has data
    values = response.get("values", [])

    return values
