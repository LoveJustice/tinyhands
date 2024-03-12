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