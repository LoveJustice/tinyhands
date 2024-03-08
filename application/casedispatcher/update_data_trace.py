import os
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.client import OAuth2Credentials
import json
import streamlit as st
from libraries.google_lib import (
    attrdict_to_dict,
)

from datetime import datetime
case_dispatcher = st.secrets["case_dispatcher"]
access_token = case_dispatcher["access_token"]
sheet_names = case_dispatcher["sheet_names"]

toml_config_dict = attrdict_to_dict(access_token)
creds_json = json.dumps(toml_config_dict)
credentials = OAuth2Credentials.from_json(creds_json)
# Directory containing your CSV files
csv_directory = 'data_trace/'

# List of (filename, creation_datetime) tuples
csv_files_with_dates = [
    (filename, os.path.getctime(os.path.join(csv_directory, filename)))
    for filename in os.listdir(csv_directory)
    if filename.endswith('.csv')
]

# Sort files by creation datetime
csv_files_sorted = sorted(csv_files_with_dates, key=lambda x: x[1])

# Assuming you have 'credentials' set up as in your snippet
client = gspread.authorize(credentials)

# Name of your Google Sheets document
gs_name = 'Case Dispatcher Data Trace'
csv_files_sorted.index('irf_3.csv')
csv_files_sorted.pop(2)
csv_files_sorted[18]
for filename, _ in csv_files_sorted:
    # Read CSV into a DataFrame
    df = pd.read_csv(os.path.join(csv_directory, filename))

    # Extract sheet name from filename (without extension)
    sheet_name = os.path.splitext(filename)[0]

    # Check if the sheet exists, and create/update it
    try:
        worksheet = client.open(gs_name).worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        worksheet = client.open(gs_name).add_worksheet(title=sheet_name, rows=str(len(df)), cols=str(len(df.columns)))

    # Update the sheet with DataFrame content
    set_with_dataframe(worksheet, df)


