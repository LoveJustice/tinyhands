'''
Module for connecting to Searchlight postgresql database and executing queries.
'''

from configparser import ConfigParser
import pandas as pd
import psycopg2
from django.db import connection
from dataentry.models import Person


class DB_Conn(object):
    """This is a class for establishing a connection with the database."""
    def __init__(self, db_filename, section='postgresql'):
        
        if db_filename is not None:
            # create a parser
            parser = ConfigParser()
            # read config file
            parser.read(str(db_filename))
            #db = {}
            if parser.has_section(section):
                params = parser.items(section)
                for param in params:
                    db[param[0]] = param[1]
            else:
                raise Exception('Section {0} not found in the {1} file'.format(section, db_filename))
    
            params = db
    
            conn = psycopg2.connect(**params)
            self.conn = conn
            self.cur = conn.cursor()
        else:
            self.conn = None
            self.cur = connection.cursor()

    def ex_query(self, select_query):
        """Execute query and return dataframe."""
        query = select_query
        cur = self.cur
        cur.execute(query)
        colnames = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        return pd.DataFrame(rows, columns=colnames)

    def close_conn(self):
        """Close the cursor and the connection."""
        self.cur.close()
        if self.conn is not None:
            self.conn.close()

#WIP Fix this
def get_sl_data(db_cred):
    # Check to see if it opens a separate thread
    dbc = DB_Conn(db_cred)
    dp = dbc.ex_query("SELECT * FROM public.dataentry_person;")
    intees = dbc.ex_query("SELECT person_id, interception_record_id FROM public.dataentry_intercepteecommon;")
    irfs = dbc.ex_query("SELECT id, irf_number FROM public.dataentry_irfcommon;")
    cifs = dbc.ex_query("SELECT id, main_pv_id, cif_number FROM public.dataentry_cifcommon;")
    vdfs = dbc.ex_query("SELECT id, vdf_number FROM public.dataentry_vdfcommon;")
    pbs = dbc.ex_query("SELECT cif_id, person_id FROM dataentry_personboxcommon;")
    c = dbc.ex_query("SELECT * FROM public.dataentry_country;")
    bs = dbc.ex_query("SELECT * FROM public.dataentry_borderstation;")
    dbc.close_conn()
    return dp, intees, irfs, cifs, vdfs, pbs, c, bs

#get_sl_data('/data/dataentry/id_matching/database.ini')