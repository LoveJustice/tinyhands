from libraries.google_lib import (
    get_gsheets,
    get_dfs,
    attrdict_to_dict,
    make_file_bytes,
    save_to_cloud,
    load_data,
    get_matching_spreadsheets,
)
from llama_index.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
import pandas as pd
from llama_index import Document

from llama_index import VectorStoreIndex

from libraries.case_dispatcher_data import (
    get_vdf,
    get_suspects,
    get_irf,
    get_suspect_evaluations,
    get_countries,
)
import streamlit as st
import json
from googleapiclient.discovery import build
from copy import deepcopy
from oauth2client.client import OAuth2Credentials

countries = get_countries()
country_list = ["Select a country..."] + ["Nepal", "Uganda", "Malawi", "Namibia"]
case_dispatcher = st.secrets["case_dispatcher"]
access_token = case_dispatcher["access_token"]
sheet_names = case_dispatcher["sheet_names"]

toml_config_dict = attrdict_to_dict(access_token)
creds_json = json.dumps(toml_config_dict)
credentials = OAuth2Credentials.from_json(creds_json)
drive_service = build("drive", "v3", credentials=credentials)

operating_country_id = 8

db_vics = load_data(drive_service, 'new_victims.pkl')
db_vics = db_vics[db_vics['operating_country_id'] == operating_country_id].drop(columns=['operating_country_id'])
db_sus = load_data(drive_service, 'new_suspects.pkl')
db_sus = db_sus[db_sus['operating_country_id'] == operating_country_id].drop(columns=['operating_country_id'])
irf_case_notes = load_data(drive_service, 'irf_case_notes.pkl')
irf_case_notes = irf_case_notes[irf_case_notes['operating_country_id'] == operating_country_id].drop \
    (columns=['operating_country_id'])
print(f"Get the model (pkl):")
case_dispatcher_model = load_data(drive_service, 'case_dispatcher_model.pkl')
print("Get the model columns:")
case_dispatcher_model_cols = load_data(drive_service, 'case_dispatcher_model_cols.pkl')
print(f"Predict likelihood of arrest and add prediction to dataframe")
case_dispatcher_soc_df = load_data(drive_service, 'case_dispatcher_soc_df.pkl')

case_dispatcher_soc_df.dtypes
db_vics.dtypes
db_sus.dtypes
irf = 'LWK764'
irf = 'BUS479'
entries = case_dispatcher_soc_df.loc[case_dispatcher_soc_df['irf_number'] == irf,:]
entries.to_csv(f'data/entries-{irf}.csv',index=False)
complete_story=[]
llm = OpenAI(temperature=0.0, model="gpt-4-turbo-2024-04-09")
memory = ChatMemoryBuffer.from_defaults(token_limit=30000)
documents = []
stories = []
for index, row in entries.iterrows():
    print(row['irf_number'])
    print(row['person_id'])
    story = (
        f"Case Number {row['irf_number']} involves suspect {row['suspect_id']} who was intercepted on {row['interview_date']} "
        f"and involves  {row['number_of_traffickers']} traffickers. "
        f"This suspect, identified as {row['gender']} aged {row['age']}, hails from {row['country']} and has been {'arrested' if row['arrested'] else 'not arrested'} so far. "
        f"The operations included "
        f"{'forced labor, ' if row['exploit_forced_labor'] else ''}"
        f"{'physical abuse, ' if row['exploit_physical_abuse'] else ''}"
        f"{'prostitution, ' if row['exploit_prostitution'] else ''}"
        f"{'sexual abuse, ' if row['exploit_sexual_abuse'] else ''}"
        f"{'debt bondage, ' if row['exploit_debt_bondage'] else ''}. "
        f"The case, filed under SF number {row['sf_number']}, has {row['number_of_victims']} victims. "
        f"Social media used by the suspect includes: {row['social_media']}. "
        f"This individual was identified as "
        f"{'host, ' if row['host'] else ''}"
        f"{'friend, ' if row['friend'] else ''}"
        f"{'recruiter, ' if row['recruiter'] else ''}"
        f"{'facilitator, ' if row['facilitator'] else ''}"
        f"{'transporter, ' if row['transporter'] else ''}"
        f"{'boss trafficker.' if row['boss_trafficker'] else ''} "
        f"The victim(s) "
        f"{'believes the suspect(s) trafficked many people, ' if row['pv_believes_definitely_trafficked_many'] else ''}"
        f"{'does not believe the suspect(s) are a trafficker, ' if row['pv_believes_not_a_trafficker'] else ''}"
        f"{'believes they trafficked some people, ' if row['pv_believes_trafficked_some'] else ''}"
        f"{'is definitely considered a trafficker by victims' if row['pv_believes_suspect_trafficker'] else ''}. "
        f"Economic and criminal indices in their operating country are indicated by resilience {row['resilience']}, criminal markets {row['criminal_markets']}, and government role (gov_rol) {row['gov_rol']} scores."
    )
    documents.append(Document(text=story))
    stories.append(story)
len(documents)
print(stories[0])
index = VectorStoreIndex.from_documents(documents)
chat_engine = index.as_chat_engine(
    chat_mode="context",
    llm=llm,
    memory=memory,
    system_prompt=(
        "A a career forensic analyst you have deep insight into crime and criminal activity especially human trafficking.  "
        "Your express goal is to investigate online and legal reports and extract pertinent factual detail."
    ),
)
prompt = """ 
In the following set of documents, each documents relates to one suspect.  The set of documents make up the entire case.
Please provide a comprehensive narrative of this case, combining all documents.  An age of -99 means an unknown age.
Do not embellish beyond the facts of the documents.  Any of host, friend, recruiter, suspect, missing_information, facilitator, transporter, boss_trafficker, role_other may consitute the role of a trafficker.
Pay particular attention to correct grammar and spelling."""

response = chat_engine.chat(prompt)

response1=response
response2=response

response1.response
cases=[]
cases.append(Document(text=response1.response))
cases.append(Document(text=response2.response))
index = VectorStoreIndex.from_documents(cases)
chat_engine = index.as_chat_engine(
    chat_mode="context",
    llm=llm,
    memory=memory,
    system_prompt=(
        "A a career forensic analyst you have deep insight into crime and criminal activity especially human trafficking.  "
        "Your express goal is to investigate online and legal reports and extract pertinent factual detail."
    ),
)
prompt = """Assistant, I have two criminal cases to work on and I need to know which case I should prioritize.  Also provide with a detailed  summary of the differences between the two cases and a reasoning behind prioritizing."""
priority_answer = chat_engine.chat(prompt)