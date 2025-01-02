import os.path
import pandas as pd
import streamlit as st
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from libraries.neo4j_lib import Neo4jConnection, execute_neo4j_query
import ast
import re
from libraries.claude_prompts import CLAUDE_PROMPTS, RED_FLAGS

query = """MATCH (ad:RecruitmentAdvert)-[ha:HAS_ANALYSIS]->(analysis:Analysis)-[hau:HAS_AUDIT]->(audit:Audit)
WHERE ha.type = hau.type AND ID(ad)=audit.posting_id AND analysis.result <> audit.result
WITH ad, ha.type as analysis_type, analysis.result as analysis_result, audit.result as audit_result, analysis.explanation as analysis_explanation, audit.confidence as confidence
RETURN
    analysis_type,
    count(*) as count,
    max(confidence) as max_confidence,
    min(confidence) as min_confidence,
    avg(confidence) as avg_confidence
ORDER BY count DESC;"""
df = pd.DataFrame(execute_neo4j_query(query, {}))
df.to_csv("results/analysis_audit_mismatch_confidence.csv", index=False)


query = """MATCH (ad:RecruitmentAdvert)-[ha:HAS_ANALYSIS]->(analysis:Analysis)-[hau:HAS_AUDIT]->(audit:Audit)
WHERE ha.type = hau.type AND ID(ad)=audit.posting_id AND analysis.result <> audit.result
WITH ad, ha.type as analysis_type, analysis.result as analysis_result, audit.result as audit_result
RETURN
    analysis_type,
    analysis_result,
    audit_result,
    count(*) as count
ORDER BY count DESC;"""
df = pd.DataFrame(execute_neo4j_query(query, {}))
df.to_csv("results/analysis_audit_mismatch.csv", index=False)
set(RED_FLAGS) - set(df["analysis_type"].to_list())
query = """MATCH (ad:RecruitmentAdvert)-[ha:HAS_ANALYSIS {type:'unprofessional_writing_prompt'}]->(analysis:Analysis)-[hau:HAS_AUDIT]->(audit:Audit)
WHERE ha.type = hau.type AND ID(ad)=audit.posting_id AND analysis.result <> audit.result
WITH ad, ha.type as analysis_type, analysis.result as analysis_result, audit.result as audit_result, analysis.explanation as analysis_explanation, audit.explanation as audit_explanation
RETURN
    ID(ad) as IDn,
    ad.text as ad,
    analysis_type,
    analysis_result,
    audit_result,
    analysis_explanation,
    audit_explanation,
    count(*) as count
ORDER BY analysis_type;"""
df = pd.DataFrame(execute_neo4j_query(query, {}))
df.to_csv("results/unprofessional_writing_mismatch.csv", index=False)


url = "https://www.facebook.com/groups/3261269040799650/posts/3683233125269904"
GROUP_POST_ID_PATTERN = re.compile(r"groups/([\w]+)/posts/([\w]+)/?")
match = GROUP_POST_ID_PATTERN.match(url)
post_id = match.group(2)


query = """"""
new_entries = pd.read_csv("results/new_entries.csv")
dict_string = new_entries.iloc[0]["parameters"]

# Convert string to dictionary
parameters = ast.literal_eval(dict_string)
query = new_entries.iloc[0]["query"]
print(query)
execute_neo4j_query(query, parameters)
load_dotenv()

# Now you can access the variables using os.getenv
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SCOPES = [os.getenv("SCOPES")]
DB_PATH = os.getenv("DB_PATH")


CREDENTIALS = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
SERVICE = build("sheets", "v4", credentials=CREDENTIALS)


df = pd.DataFrame(
    {
        "Name": ["John Doe", "Jane Doe"],
        "Age": [28, 32],
        "Occupation": ["Data Scientist", "Engineer"],
    }
)

# result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()

RANGE_NAME = "Sheet1!A1"  # Adjust based on where you want to start writing

# Convert DataFrame to list of lists
values = [df.columns.values.tolist()] + df.values.tolist()

# Prepare the request body
body = {"values": values}

# Use the Sheets API to write the data
request = (
    SERVICE.spreadsheets()
    .values()
    .update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="RAW",
        body=body,
    )
)
request.execute()
