from work_with_db import URLDatabase, DatabaseError
import pandas as pd
from typing import List, Optional, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
import os
import sqlite3
import os
import pandas as pd
import json
import logging
from tldextract import tldextract
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
# from google_miner import logger
from models import (
    IncidentResponse,
)
from get_urls_from_csvs import get_unique_urls_from_csvs
from work_with_db import URLDatabase, DatabaseError
import pandas as pd
db=URLDatabase()
df=pd.DataFrame(db.search_urls(limit=1000000))
df['url'].tolist()
import sqlite3
db_path = os.getenv("HTDB_PATH")



deleted_urls = ['https://www.herald.co.zw/human-trafficker-convicted-sentencing-on-tomorrow/',
'https://www.herald.co.zw/human-trafficker-convicted-sentencing-on-tomorrow/',
'https://www.thestar.com/news/world/asia/china-detains-suspect-in-human-trafficking-cases-linked-to-online-scam-networks-in-myanmar/article_6f9bc2f1-695c-5f57-882c-5914586c491e.html',
'https://www.belgrade-news.com/news/briefs/senior-israeli-member-of-orthodox-jewish-sect-lev-tahor-arrested-for-alleged-human-trafficking/article_29fe7f90-dd0d-11ef-95e9-7f26ee63097a.html',
'https://www.hindustantimes.com/india-news/three-more-held-in-inter-state-child-trafficking-racket-belagavi-sp-101738004232680.html',
'https://obamawhitehouse.archives.gov/blog/2012/11/26/fighting-human-trafficking-cambodia',
'https://www.destinyrescue.org/our-work/where-we-work/cambodia/',
'https://www.destinyrescue.org/our-work/where-we-work/cambodia/',
'https://www.destinyrescue.org/our-work/where-we-work/cambodia/',
'https://crownschool.uchicago.edu/student-life/advocates-forum/sex-trafficking-cambodia-complex-humanitarian-emergency',]



db_path = os.getenv("HTDB_PATH")

with sqlite3.connect(db_path) as conn:
    cursor = conn.execute("SELECT * FROM urls")

    urls = pd.DataFrame(cursor.fetchall(), columns=[description[0] for description in cursor.description])
    cursor = conn.execute("SELECT * FROM suspect_forms")
    suspect_forms = pd.DataFrame(cursor.fetchall(), columns=[description[0] for description in cursor.description])
    cursor = conn.execute("SELECT * FROM victim_forms")
    victim_forms = pd.DataFrame(cursor.fetchall(), columns=[description[0] for description in cursor.description])

with sqlite3.connect(db_path) as conn:
    cursor = conn.execute("""SELECT url_id, victim_id, COUNT(*) AS cnt
FROM victim_forms
GROUP BY url_id, victim_id
HAVING cnt > 1;""")
    victims_duplicated = pd.DataFrame(cursor.fetchall(), columns=[description[0] for description in cursor.description])

with sqlite3.connect(db_path) as conn:
    cursor = conn.execute("""SELECT url_id, suspect_id, COUNT(*) AS cnt
FROM suspect_forms
GROUP BY url_id, suspect_id
HAVING cnt > 1;""")
    suspects_duplicated = pd.DataFrame(cursor.fetchall(), columns=[description[0] for description in cursor.description])
suspects_duplicated['url_id'].tolist()


deleted_url_ids = urls[urls['url'].isin(deleted_urls)]['id'].tolist()
urls[urls['url'].isin(deleted_urls)].to_csv('output/deleted_urls.csv', index=False)
suspect_forms[suspect_forms['url_id'].isin(deleted_url_ids)].to_csv('output/deleted_suspect_forms.csv', index=False)
victim_forms[victim_forms['url_id'].isin(deleted_url_ids)].to_csv('output/deleted_victim_forms.csv', index=False)

query="""CREATE TABLE victim_forms_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_id INTEGER NOT NULL,
    victim_id INTEGER,
    name TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('male', 'female', NULL)),
    date_of_birth TEXT,
    age INTEGER,
    address_notes TEXT,
    phone_number TEXT,
    nationality TEXT,
    occupation TEXT,
    appearance TEXT,
    vehicle_description TEXT,
    vehicle_plate_number TEXT,
    evidence TEXT,
    destination TEXT,
    job_offered TEXT,
    UNIQUE(url_id, victim_id),
    FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (victim_id) REFERENCES victims (id) ON DELETE SET NULL ON UPDATE CASCADE
);"""
with sqlite3.connect(db_path) as conn:
    cursor = conn.execute(query)

# -- Copy data over (since duplicates are removed, a simple insert will do):
query="""INSERT INTO victim_forms_new (
    url_id, victim_id, name, gender, date_of_birth, age,
    address_notes, phone_number, nationality, occupation,
    appearance, vehicle_description, vehicle_plate_number, evidence,
    destination, job_offered
)
SELECT url_id, victim_id, name, gender, date_of_birth, age,
       address_notes, phone_number, nationality, occupation,
       appearance, vehicle_description, vehicle_plate_number, evidence,
       destination, job_offered
FROM victim_forms;"""
with sqlite3.connect(db_path) as conn:
    cursor = conn.execute(query)

# -- Replace the old table:
query = """
DROP TABLE victim_forms;
ALTER TABLE victim_forms_new RENAME TO victim_forms;
"""

with sqlite3.connect(db_path) as conn:
    conn.executescript(query)


import sqlite3

query = """
CREATE TABLE suspect_forms_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url_id INTEGER NOT NULL,
    suspect_id INTEGER,
    name TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('male', 'female', NULL)),
    date_of_birth TEXT,
    age INTEGER,
    address_notes TEXT,
    phone_number TEXT,
    nationality TEXT,
    occupation TEXT,
    role TEXT,
    appearance TEXT,
    vehicle_description TEXT,
    vehicle_plate_number TEXT,
    evidence TEXT,
    arrested_status TEXT,
    arrest_date TEXT,
    crimes_person_charged_with TEXT,
    willing_pv_names TEXT,
    suspect_in_police_custody TEXT,
    suspect_current_location TEXT,
    suspect_last_known_location TEXT,
    suspect_last_known_location_date TEXT,
    UNIQUE(url_id, suspect_id),
    FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (suspect_id) REFERENCES suspects (id) ON DELETE SET NULL ON UPDATE CASCADE
);
"""

with sqlite3.connect(db_path) as conn:
    conn.execute(query)
    conn.commit()

query = """
INSERT INTO suspect_forms_new (
    url_id, suspect_id, name, gender, date_of_birth, age,
    address_notes, phone_number, nationality, occupation, role,
    appearance, vehicle_description, vehicle_plate_number, evidence,
    arrested_status, arrest_date, crimes_person_charged_with,
    willing_pv_names, suspect_in_police_custody,
    suspect_current_location, suspect_last_known_location,
    suspect_last_known_location_date
)
SELECT url_id, suspect_id, name, gender, date_of_birth, age,
       address_notes, phone_number, nationality, occupation, role,
       appearance, vehicle_description, vehicle_plate_number, evidence,
       arrested_status, arrest_date, crimes_person_charged_with,
       willing_pv_names, suspect_in_police_custody,
       suspect_current_location, suspect_last_known_location,
       suspect_last_known_location_date
FROM suspect_forms;
"""

with sqlite3.connect(db_path) as conn:
    conn.execute(query)
    conn.commit()

query = """
DROP TABLE suspect_forms;
ALTER TABLE suspect_forms_new RENAME TO suspect_forms;
"""

with sqlite3.connect(db_path) as conn:
    conn.executescript(query)
    conn.commit()
