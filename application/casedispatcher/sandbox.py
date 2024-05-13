import json
import streamlit as st
from googleapiclient.discovery import build
from oauth2client.client import OAuth2Credentials
from libraries.google_lib import (
    attrdict_to_dict,
    get_file_id,
    load_from_cloud,
    load_model_and_columns
)

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
        'age': 'int64',
        'number_of_victims': 'int64',
        'number_of_traffickers': 'int64',
    }
    # Assuming all other columns in cols should be boolean
    for col in cols:
        if col not in dtype_map:
            dtype_map[col] = 'bool'
    return dtype_map
dtype_map = get_dtype_mapping(case_dispatcher_model_cols)
case_dispatcher_soc_df[case_dispatcher_model_cols].dtypes


import streamlit as st
import json
import pandas as pd
import numpy as np
from datetime import date
from googleapiclient.discovery import build
from copy import deepcopy
from oauth2client.client import OAuth2Credentials
import libraries.data_prep as data_prep
import pickle
from libraries.case_dispatcher_model import (
    check_grid_search_cv,
    save_results,
    make_new_predictions,
)
from libraries.data_prep import remove_non_numeric, process_columns
from libraries.entity_model import EntityGroup
from libraries.case_dispatcher_model import TypeSelector
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

countries = get_countries()
country_list = ["Select a country..."] + ["Nepal", "Uganda", "Malawi", "Namibia"]
case_dispatcher = st.secrets["case_dispatcher"]
access_token = case_dispatcher["access_token"]
sheet_names = case_dispatcher["sheet_names"]

toml_config_dict = attrdict_to_dict(access_token)
creds_json = json.dumps(toml_config_dict)
credentials = OAuth2Credentials.from_json(creds_json)
service = build("sheets", "v4", credentials=credentials)
spreadsheet_id = os.environ['WEIGHTS_ID']
 # Make sure your environment variable is correctly set
named_range = 'priority_weights'  # Replace 'YourNamedRange' with the actual named range

# Fetch the values from the named range
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range=named_range
).execute()

# Get values
values = result.get('values', [])

# Check if values were found and print them
if not values:
    print('No data found.')
else:
    for row in values:
        print(row)  # Each 'row' corresponds to a row of data in your named range

weights = {}
for idx in range(1,len(values[0])):
    weights[values[0][idx]] = float(values[1][idx])

    print(row)  # Each 'row' corresponds to a row of data in your named range
values[0]
range_data = service.spreadsheets().values_get('priority_weights').execute()
def read_from_sheet(tab: str, named_range: str):
    # Construct the range name
    RANGE_NAME = f'{tab}!{named_range}'

    # Use the Sheets API to get the data
    request = SERVICE.spreadsheets().values().get(
        spreadsheetId=KORRIDORBOT_UI_FEEDBACK_ID, range=RANGE_NAME)
    response = request.execute()

    # The data returned is in 'values' key if the range has data
    values = response.get('values', [])

    return values


