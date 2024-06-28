import pandas as pd
import psycopg2
import streamlit as st
import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

# Now you can access the variables using os.getenv
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SCOPES = [os.getenv("SCOPES")]
DB_PATH = os.getenv("DB_PATH")


CREDENTIALS = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
SERVICE = build("sheets", "v4", credentials=CREDENTIALS)


class DB_Conn(object):
    """A class for establishing a connection with the database."""

    def __init__(self):
        """Initialize the connection with the database."""
        self._initialize_db_connection()

    def _initialize_db_connection(self):
        db_cred = st.secrets["postgresql"]
        self.conn = psycopg2.connect(**db_cred)
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_conn()

    def ex_query(self, select_query, parameters=None):
        """Execute query with parameters and return dataframe."""
        if parameters:
            self.cur.execute(select_query, parameters)
        else:
            self.cur.execute(select_query)

        if self.cur.description:
            colnames = [desc[0] for desc in self.cur.description]
            rows = self.cur.fetchall()
            return pd.DataFrame(rows, columns=colnames)
        else:
            return None

    def insert_query(self, insert_query, parameters=None):
        """Execute insert query with parameters."""
        if parameters:
            self.cur.execute(insert_query, parameters)
        else:
            self.cur.execute(insert_query)
        self.conn.commit()

    def close_conn(self):
        """Close the cursor and the connection."""
        self.cur.close()
        self.conn.close()
