import json

from nltk.sem.chat80 import country

import libraries.case_dispatcher_data as cdd
import pandas as pd
import streamlit as st
from googleapiclient.discovery import build
from oauth2client.client import OAuth2Credentials
from libraries.data_prep import extract_case_id
from libraries.google_lib import (
    attrdict_to_dict,
    get_file_id,
    load_from_cloud,
    load_model_and_columns,
    load_data,
)
import pickle
import os
from libraries.google_lib import DB_Conn
from pages.irf_evaluation import case_dispatcher_soc_df
case_dispatcher = st.secrets["case_dispatcher"]
access_token = case_dispatcher["access_token"]
toml_config_dict = attrdict_to_dict(access_token)
creds_json = json.dumps(toml_config_dict)
credentials = OAuth2Credentials.from_json(creds_json)
drive_service = build("drive", "v3", credentials=credentials)

case_dispatcher_soc_file_name = f"case_dispatcher_soc_df.pkl"
case_dispatcher_soc_file_id = get_file_id(
    case_dispatcher_soc_file_name, drive_service
)

model_data = load_from_cloud(drive_service, case_dispatcher_soc_file_id)
list(model_data)

os.getcwd()
country="Uganda"
suspect_evaluations = cdd.get_suspect_evaluations(country=country)
sql_query =  """SELECT person.arrested AS arrested \
    ,vdfcommon.station_id AS station_id \
    ,person.id AS person_id \
    ,vdfcommon.pv_recruited_how AS pv_recruited_how \
    ,vdfcommon.pv_recruited_no AS pv_recruited_no \
    ,vdfcommon.pv_recruited_broker AS pv_recruited_broker \
    ,vdfcommon.pv_recruited_agency AS pv_recruited_agency \
    ,vdfcommon.exploit_prostitution AS exploit_prostitution \
    ,vdfcommon.exploit_forced_labor AS exploit_forced_labor \
    ,vdfcommon.exploit_physical_abuse AS exploit_physical_abuse \
    ,vdfcommon.exploit_sexual_abuse AS exploit_sexual_abuse \
    ,vdfcommon.exploit_debt_bondage AS exploit_debt_bondage \
    ,vdfcommon.pv_expenses_paid_how AS pv_expenses_paid_how \
    ,vdfcommon.job_promised_amount AS job_promised_amount \
    ,vdfcommon.vdf_number AS vdf_number \
    ,person.full_name AS full_name \
    ,person.phone_contact AS phone_contact \
    ,person.address_notes AS address_notes \
    ,person.role AS role \
    ,person.social_media AS social_media \
    ,borderstation.station_name AS station_name \
    ,country.name AS country \
    ,country.id AS operating_country_id \
    ,person.master_person_id AS master_person_id \
    FROM public.dataentry_vdfcommon vdfcommon \
    INNER JOIN public.dataentry_person person ON person.id = vdfcommon.victim_id  \
    INNER JOIN public.dataentry_borderstation borderstation ON borderstation.id = vdfcommon.station_id \
    INNER JOIN public.dataentry_country country ON country.id = borderstation.operating_country_id \
    WHERE vdfcommon.exploit_prostitution IS TRUE \
    OR vdfcommon.exploit_forced_labor IS TRUE \
    OR vdfcommon.exploit_physical_abuse IS TRUE \
    OR vdfcommon.exploit_sexual_abuse IS TRUE \
    OR vdfcommon.exploit_debt_bondage IS TRUE"""

parameters={}
country='Uganda'
sql_query += " AND country.name = %(country)s"
parameters["country"] = country
with DB_Conn() as dbc:
    result = dbc.ex_query(sql_query, parameters)
result["case_id"] = result["vdf_number"].apply(extract_case_id)
df = case_dispatcher_soc_df[case_dispatcher_soc_df["case_id"].isin(result["case_id"])]
df[df["days"]<120]

sql_query = """
    SELECT
        suspect.sf_number AS sf_number,
        suspectevaluation.evaluation,
        country.name AS country,
        person.id AS person_id,
        person.arrested AS arrested,
        person.master_person_id AS master_person_id,
        suspect_information.interview_date AS interview_date
    FROM public.dataentry_person person
    INNER JOIN public.dataentry_suspect suspect ON suspect.merged_person_id = person.id
    INNER JOIN public.dataentry_suspectlegal suspectlegal ON suspectlegal.suspect_id = suspect.id
    INNER JOIN public.dataentry_borderstation borderstation ON borderstation.id = suspect.station_id
    INNER JOIN public.dataentry_country country ON country.id = borderstation.operating_country_id
    INNER JOIN public.dataentry_suspectevaluation suspectevaluation ON suspectevaluation.suspect_id = suspect.id
    INNER JOIN public.dataentry_suspectinformation suspect_information ON suspect_information.suspect_id = suspect.id
    WHERE suspectevaluation.evaluator_type = 'PV'
"""
parameters={}
country='Uganda'
sql_query += " AND country.name = %(country)s"
parameters["country"] = country
with DB_Conn() as dbc:
    result = dbc.ex_query(sql_query, parameters)
result["case_id"] = result["sf_number"].apply(extract_case_id)

result = suspect_evaluations.drop_duplicates()
pivoted_results = (
    result.assign(val=True)
    .pivot_table(
        index="sf_number",
        columns="evaluation",
        values="val",
        fill_value=False,
    )
    .reset_index()
)
evaluation_types = pivoted_results.astype(
    {
        col: bool
        for col in pivoted_results.columns
        if col != "sf_number"
    }
)

column_rename_mapping = {
    "Definitely trafficked many people": "pv_believes_definitely_trafficked_many",
    "Don't believe s/he's a trafficker": "pv_believes_not_a_trafficker",
    "Has trafficked some people": "pv_believes_trafficked_some",
    "Suspect s/he's a trafficker": "pv_believes_suspect_trafficker",
}
suspect_evaluation_types = evaluation_types.rename(
    columns=column_rename_mapping
)





evaluation_types["case_id"] = evaluation_types["sf_number"].apply(extract_case_id)
df = case_dispatcher_soc_df[case_dispatcher_soc_df["case_id"].isin(evaluation_types["case_id"])]
df = df[df["days"]<120]

def get_suspects(country=None):
    parameters = {}
    sql_query = """SELECT suspect.id as suspect_id, person.full_name AS full_name \
                            ,person.phone_contact AS phone_contact \
                            ,person.address_notes AS address_notes \
                            ,person.case_filed_against AS case_filed_against \
                            ,person.social_media AS social_media \
                            ,person.arrested AS arrested \
                            ,person.id AS person_id \
                            ,person.role AS role \
                            ,person.master_person_id AS master_person_id \
                            ,person.gender AS gender \
                            ,person.age AS age \
                            ,country.name AS country \
                            ,country.id AS operating_country_id \
                            ,borderstation.station_name AS station_name \
                            ,borderstation.id AS borderstation_id \
                            ,suspect.sf_number AS sf_number \
                            ,suspectlegal.pv_attempt AS pv_attempt \
                            ,suspectlegal.arrest_date AS arrest_date \
                            ,suspectlegal.arrested AS suspect_arrested \
                            FROM public.dataentry_person person \
                            INNER JOIN public.dataentry_suspect suspect ON suspect.merged_person_id = person.id \
                            INNER JOIN public.dataentry_suspectlegal suspectlegal ON suspectlegal.suspect_id = suspect.id \
                            INNER JOIN public.dataentry_borderstation borderstation ON borderstation.id = suspect.station_id \
                            INNER JOIN public.dataentry_country country ON country.id = borderstation.operating_country_id"""
    if country:
        sql_query += " WHERE country.name = %(country)s"
        parameters["country"] = country
    with DB_Conn() as dbc:
        suspects = dbc.ex_query(sql_query, parameters)

    return suspects

vdf = cdd.get_vdf(country="Uganda")
df = vdf[vdf["vdf_number"] == "LWK1158A"][['exploit_debt_bondage', 'exploit_forced_labor', 'exploit_physical_abuse', 'exploit_prostitution', 'exploit_sexual_abuse']]
db_vics_11 = pd.read_csv("data_trace/soc_df_8.csv")
db_vics_11[db_vics_11["sf_number"] == "LWK1158A"][['exploit_debt_bondage', 'exploit_forced_labor', 'exploit_physical_abuse', 'exploit_prostitution', 'exploit_sexual_abuse']]

suspects = get_suspects(country="Uganda")
# Copy and extract suspect_id from the closed entity
suspects_entity_closed = suspects_entity.closed.copy()
suspects_entity_closed["suspect_id"] = (
    suspects_entity_closed["sf_numer"]
    .str.extract(r"sus(\d+)", expand=False)
    .astype(int)
)

# Perform a right merge so that all rows from suspects_entity_closed are retained
suspect_closed_save = suspects[["suspect_id", "sf_number", "full_name"]].merge(
    suspects_entity_closed[["suspect_id", "name"]], on="suspect_id", how="right"
)

# Reorder suspect_closed_save to exactly match the order in suspects_entity_closed.
# Here we assume that 'suspect_id' is unique in suspects_entity_closed.
ordered_ids = suspects_entity_closed["suspect_id"]
suspect_closed_save = suspect_closed_save.set_index("suspect_id")
suspect_closed_save = suspect_closed_save.loc[ordered_ids]
suspect_closed_save = suspect_closed_save.reset_index()
suspect_closed_save.to_csv("data/suspect_closed_save.csv", index=False)
print(suspect_closed_save)
# ---------------------------------------------------------------------
police_entity_closed = police_entity.closed.copy()
police_entity_closed["suspect_id"] = (
    police_entity_closed["sf_number"].str.extract(r"sus(\d+)", expand=False).astype(int)
)

# Perform a right merge so that all rows from suspects_entity_closed are retained
police_entity_closed_saved = suspects[["suspect_id", "sf_number", "full_name"]].merge(
    police_entity_closed[["suspect_id", "suspect_name"]], on="suspect_id", how="right"
)

# Reorder suspect_closed_save to exactly match the order in suspects_entity_closed.
# Here we assume that 'suspect_id' is unique in suspects_entity_closed.
ordered_ids = police_entity_closed_saved["suspect_id"]
police_entity_closed_saved = police_entity_closed_saved.set_index("suspect_id")
police_entity_closed_saved = police_entity_closed_saved.loc[ordered_ids]
police_entity_closed_saved = police_entity_closed_saved.reset_index()
police_entity_closed_saved.to_csv("data/police_entity_closed_saved.csv", index=False)
print(police_entity_closed_saved)

# ---------------------------------------------------------------------
police_entity_active = police_entity.active.copy()
police_entity_active = police_entity_active[~police_entity_active.case_name.isna()]
police_entity_active["suspect_id"] = police_entity_active["sf_number"]
police_entity_active["suspect_id"] = (
    police_entity_active["sf_number"].str.extract(r"sus(\d+)", expand=False).astype(int)
)

# Perform a right merge so that all rows from suspects_entity_closed are retained
police_entity_active_saved = suspects[["suspect_id", "sf_number", "full_name"]].merge(
    police_entity_active[["suspect_id", "suspect_name"]], on="suspect_id", how="right"
)

# Reorder suspect_closed_save to exactly match the order in suspects_entity_closed.
# Here we assume that 'suspect_id' is unique in suspects_entity_closed.
ordered_ids = police_entity_active_saved["suspect_id"]
(
    police_entity_active_saved.set_index("suspect_id")
    .loc[ordered_ids]
    .reset_index()
    .to_csv("data/police_entity_active_saved.csv", index=False)
)
print(police_entity_closed_saved)

# ---------------------------------------------------------------------
suspects_entity_active = suspects_entity.active.copy()
suspects_entity_active = suspects_entity_active[
    ~suspects_entity_active.case_name.isna()
]
suspects_entity_active["suspect_id"] = suspects_entity_active["sf_number"]
suspects_entity_active["suspect_id"] = (
    suspects_entity_active["sf_number"]
    .str.extract(r"sus(\d+)", expand=False)
    .astype(int)
)

# Perform a right merge so that all rows from suspects_entity_closed are retained
suspects_entity_active_saved = suspects[["suspect_id", "sf_number", "full_name"]].merge(
    suspects_entity_active[["suspect_id", "name"]], on="suspect_id", how="right"
)

# Reorder suspect_closed_save to exactly match the order in suspects_entity_closed.
# Here we assume that 'suspect_id' is unique in suspects_entity_closed.
ordered_ids = suspects_entity_active_saved["suspect_id"]
(
    suspects_entity_active_saved.set_index("suspect_id")
    .loc[ordered_ids]
    .reset_index()
    .to_csv("data/suspects_entity_active_saved.csv", index=False)
)
print(suspects_entity_active_saved)


suspects_entity_gsheet = pd.read_csv("data/suspects_entity_gsheet.csv")

suspects_entity_gsheet["suspect_id"] = suspects_entity_gsheet["sf_number"].str.extract(
    r"sus(\d+)", expand=False
)
suspects_entity_gsheet["suspect_id"] = suspects_entity_gsheet["suspect_id"].astype(int)
suspect_save = suspects[["suspect_id", "sf_number", "full_name"]].merge(
    suspects_entity_gsheet[["suspect_id", "name"]], on="suspect_id"
)
suspect_save.to_csv("data/suspect_save.csv", index=False)

# Convert the extracted values to integers
suspects_entity_gsheet["suspect_id"] = suspects_entity_gsheet["suspect_id"].astype(int)
case_dispatcher_soc_df.to_csv("data/case_dispatcher_soc_df.csv", index=False)

# ---------------------------------------------------------------------
police_entity_closed = police_entity.closed.copy()
police_entity_closed["suspect_id"] = (
    police_entity_closed["sf_number"].str.extract(r"sus(\d+)", expand=False).astype(int)
)

# Perform a right merge so that all rows from suspects_entity_closed are retained
police_entity_closed_saved = suspects[["suspect_id", "sf_number", "full_name"]].merge(
    police_entity_closed[["suspect_id", "suspect_name"]], on="suspect_id", how="right"
)

# Reorder suspect_closed_save to exactly match the order in suspects_entity_closed.
# Here we assume that 'suspect_id' is unique in suspects_entity_closed.
ordered_ids = police_entity_closed_saved["suspect_id"]
police_entity_closed_saved = police_entity_closed_saved.set_index("suspect_id")
police_entity_closed_saved = police_entity_closed_saved.loc[ordered_ids]
police_entity_closed_saved = police_entity_closed_saved.reset_index()
police_entity_closed_saved.to_csv("data/police_entity_closed_saved.csv", index=False)
print(police_entity_closed_saved)


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
case_dispatcher_soc_df = load_data(drive_service, "case_dispatcher_soc_df.pkl")
list(case_dispatcher_soc_df)
"LWK1143" in case_dispatcher_soc_df.irf_number
case_dispatcher_soc_df[case_dispatcher_soc_df.irf_number == "LWK1154"]
case_dispatcher_model_cols = load_data(drive_service, "case_dispatcher_model_cols.pkl")
case_dispatcher_soc_df[case_dispatcher_model_cols]
db_vics = load_data(drive_service, "new_victims.pkl")
db_sus = load_data(drive_service, "new_suspects.pkl")
irf_case_notes = load_data(drive_service, "irf_case_notes.pkl")
soc_df_0 = pd.read_csv("data_trace/soc_df_7.csv")

vdf_1 = pd.read_csv("data_trace/vdf_1.csv")
list(vdf_1)
vdf_1.vdf_number
vdf_1["irf_number"] = vdf_1.vdf_number.apply(extract_case_id)
db_vics["irf_number"] = db_vics.vdf_number.apply(extract_case_id)
db_sus["arrested"].unique()
vdf_1[vdf_1.irf_number == "LWK1154"]
list(db_vics)
list(soc_df_0)
db_vics[db_vics.irf_number == "LWK1154"]
db_vics.vdf_number
# Example usage with a pandas DataFrame:
db_vics.vdf_number.apply(extract_case_id)

db_sus[db_sus.sf_number_group == "LWK1165"]
db_sus.sf_number_group


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


def get_all_weights(credentials, workbook_name, range_names):
    gc = gspread.authorize(credentials)
    workbook = gc.open(workbook_name)
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
