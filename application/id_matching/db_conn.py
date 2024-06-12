'''
Module for connecting to Searchlight postgresql database and executing queries.
'''

from configparser import ConfigParser
import pandas as pd
import psycopg2
from django.db import connection
from dataentry.models import Person


import pandas as pd
import psycopg2
from configparser import ConfigParser

class DB_Conn(object):
    """A class for establishing a connection with the database."""

    def __init__(self, db_config=None, db_filename=None, section='postgresql'):
        """
        Initialize the connection with the database.
        :param db_config: A dictionary containing the database connection parameters (optional).
        :param db_filename: A filename from which to read the database configuration (optional).
        :param section: The section of the configuration file to read for the database settings (optional).
        """
        if db_config:
            self.db_config = db_config
        elif db_filename:
            self.db_config = self._get_db_config(db_filename, section)
        else:
            raise ValueError("Either db_config or db_filename must be provided.")
        self._initialize_db_connection()

    def _get_db_config(self, db_filename, section):
        parser = ConfigParser()
        parser.read(str(db_filename))
        if parser.has_section(section):
            return {param[0]: param[1] for param in parser.items(section)}
        else:
            raise Exception(f'Section {section} not found in the {db_filename} file')

    def _initialize_db_connection(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cur = self.conn.cursor()
        except psycopg2.Error as e:
            raise Exception(f"Database connection failed: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_conn()

    def ex_query(self, select_query, parameters=None):
        """Execute query with parameters and return dataframe."""
        self.cur.execute(select_query, parameters) if parameters else self.cur.execute(select_query)
        if self.cur.description:
            colnames = [desc[0] for desc in self.cur.description]
            rows = self.cur.fetchall()
            return pd.DataFrame(rows, columns=colnames)
        else:
            return None

    def insert_query(self, insert_query, parameters=None):
        """Execute insert query with parameters."""
        try:
            self.cur.execute(insert_query, parameters) if parameters else self.cur.execute(insert_query)
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise Exception(f"Insert query failed: {e}")

    def close_conn(self):
        """Close the cursor and the connection."""
        self.cur.close()
        self.conn.close()

#WIP Fix this
def get_sl_data(db_cred):
    # Check to see if it opens a separate thread
    dbc = DB_Conn(db_cred)
    dp = dbc.ex_query("SELECT * FROM public.dataentry_person;")
    intees = dbc.ex_query("SELECT person_id, interception_record_id FROM public.dataentry_intercepteecommon;")
    irfs = dbc.ex_query("SELECT id, irf_number FROM public.dataentry_irfcommon;")
    cifs = dbc.ex_query("SELECT id, main_pv_id, cif_number FROM public.dataentry_cifcommon;")
    sfs = dbc.ex_query("SELECT id, merged_person_id, sf_number FROM public.dataentry_suspect;")
    vdfs = dbc.ex_query("SELECT id, vdf_number FROM public.dataentry_vdfcommon;")
    pbs = dbc.ex_query("SELECT cif_id, person_id FROM dataentry_personboxcommon;")
    sis = dbc.ex_query("SELECT sf_id, person_id FROM dataentry_suspectinformation;")
    c = dbc.ex_query("SELECT * FROM public.dataentry_country;")
    bs = dbc.ex_query("SELECT * FROM public.dataentry_borderstation;")
    dbc.close_conn()
    return dp, intees, irfs, cifs, sfs, vdfs, pbs, c, bs

def get_sl_data2(db_cred):
    # Check to see if it opens a separate thread
    dbc = DB_Conn(db_cred)
    slp = dbc.ex_query("SELECT * FROM public.id_match_source;")
    dbc.close_conn()
    return slp

#get_sl_data('/data/dataentry/id_matching/database.ini')