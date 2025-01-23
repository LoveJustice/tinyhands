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

import os

# Define file paths
PRESENCE_CSV = "results/advert_flags.csv"
CONFIDENCE_CSV = "results/advert_confidence.csv"

# Load Presence DataFrame
new_advert_flags = pd.read_csv(PRESENCE_CSV)
old_advert_flags = pd.read_csv("results/archive/advert_flags.csv")
presence = new_advert_flags.copy()
# Define mapping for presence values
presence_mapping = {"yes": 1, "no": 0}
new_advert_flags["unprofessional_writing_prompt"]
old_advert_flags["unprofessional_writing_prompt"]
new_advert_flags["unprofessional_writing_prompt"].equals(
    old_advert_flags["unprofessional_writing_prompt"]
)
sum(
    new_advert_flags["unprofessional_writing_prompt"]
    == old_advert_flags["unprofessional_writing_prompt"]
)
sum(
    new_advert_flags["target_specific_group_prompt"]
    == old_advert_flags["target_specific_group_prompt"]
)

sum(
    new_advert_flags["gender_specific_prompt"]
    == old_advert_flags["gender_specific_prompt"]
)

# Replace categorical values with numerical mapping
presence.replace(presence_mapping, inplace=True)

# Load Confidence DataFrame
confidence = pd.read_csv(CONFIDENCE_CSV)

# Rename 'id' column to 'IDn' for consistency
confidence.rename(columns={"id": "IDn"}, inplace=True)

# Set 'IDn' as the index for both DataFrames
confidence.set_index("IDn", inplace=True)
presence.set_index("IDn", inplace=True)

# Check for duplicate IDs in Presence DataFrame
if presence.index.duplicated().any():
    duplicated_ids = presence.index[presence.index.duplicated()].unique()
    raise ValueError(
        f"Duplicate IDn values found in presence DataFrame: {duplicated_ids}"
    )

# Check for duplicate IDs in Confidence DataFrame
if confidence.index.duplicated().any():
    duplicated_ids = confidence.index[confidence.index.duplicated()].unique()
    raise ValueError(
        f"Duplicate IDn values found in confidence DataFrame: {duplicated_ids}"
    )

# Identify common IDn values
common_idn = presence.index.intersection(confidence.index)

# Filter both DataFrames to include only common IDs
presence = presence.loc[common_idn]
confidence = confidence.loc[common_idn]

# Verify that the indices are identical and sorted
assert presence.index.equals(
    confidence.index
), "Indices of presence and confidence DataFrames do not match."

# Define the list of features to transform
# Replace this with your actual list of 20 features


# Ensure that RED_FLAGS columns exist in both DataFrames
missing_features_presence = set(RED_FLAGS) - set(presence.columns)
missing_features_confidence = set(RED_FLAGS) - set(confidence.columns)

if missing_features_presence:
    raise ValueError(
        f"The following RED_FLAGS columns are missing in presence DataFrame: {missing_features_presence}"
    )

if missing_features_confidence:
    raise ValueError(
        f"The following RED_FLAGS columns are missing in confidence DataFrame: {missing_features_confidence}"
    )

# Transform presence: 1 -> 1, 0 -> -1
presence_transformed = 2 * presence[RED_FLAGS] - 1

# Calculate new_presence by multiplying transformed presence with confidence
new_presence = presence_transformed * confidence[RED_FLAGS]

# Reset index to bring 'IDn' back as a column
new_presence.reset_index(inplace=True)
advert_flags[
    ["IDn"] + list(set(list(advert_flags)) - set(list(new_presence.columns)))
].merge(new_presence, on="IDn").to_csv("results/new_presence.csv", index=False)

# Optionally, save the new_presence DataFrame to a CSV file
new_presence.to_csv("results/new_presence.csv", index=False)

# Display the first few rows to verify
print(new_presence.head())


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
