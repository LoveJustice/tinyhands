import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import psycopg2
import gspread
from pathlib import Path
from .case_dispatcher_logging import setup_logger

# Create a logger
logger = setup_logger("connectivity_logging", "connectivity")


credentials = ServiceAccountCredentials.from_json_keyfile_dict(CREDS_DICT, SCOPE)
