import os
import time

import streamlit as st
from typing import Dict, Any, Optional, List
import json
import re
import bs4, requests
from datetime import datetime, timedelta
import libraries.neo4j_lib as nl
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core import download_loader
from llama_index.core import VectorStoreIndex, ServiceContext, Document
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
import pandas as pd
import json
from typing import Optional, Dict, Any
import re
import logging
from tqdm import tqdm
import libraries.claude_prompts as cp
from llama_index.llms.ollama import Ollama
import libraries.llm_functions as lf


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
llm = OpenAI(temperature=0, model="gpt-4o", max_tokens=4096)
llm = Ollama(model="llama3.1", temperature=0, max_tokens=4096)
# llm = Anthropic(temperature=0, model="claude-3-opus-20240229")
# llm = Anthropic()
MEMORY = ChatMemoryBuffer.from_defaults(token_limit=4096)
# llm = Anthropic(temperature=0, model="claude-3-opus-20240229")


red_flags = [
    "assure_prompt",
    "bypass_prompt",
    "callback_request_prompt",
    "drop_off_at_secure_location_prompt",
    "false_organization_prompt",
    "gender_specific_prompt",
    "illegal_activities_prompt",
    "immediate_hiring_prompt",
    "language_switch_prompt",
    "multiple_provinces_prompt",
    "no_education_skilled_prompt",
    "no_location_prompt",
    "overseas_prompt",
    "quick_money_prompt",
    "recruit_students_prompt",
    "requires_references",
    "suspicious_email_prompt",
    "target_specific_group_prompt",
    "unprofessional_writing_prompt",
    "unrealistic_hiring_number_prompt",
    "unusual_hours_prompt",
    "vague_description_prompt",
]


def analyze_dataframe(df):
    """
    Analyze a dataframe to:
    1. Count NaN values by column
    2. Count 'yes' and 'no' occurrences
    3. Filter for columns containing only 'yes' or 'no' and remove rows with NaN values

    Parameters:
    df (pandas.DataFrame): Input DataFrame

    Returns:
    tuple: (nan_counts, yes_no_counts, binary_df)
    """
    # 1. Count NaN values by column
    nan_counts = df.isna().sum()

    # 2. Count 'yes' and 'no' occurrences for each column
    yes_no_counts = {}
    for column in df.columns:
        value_counts = df[column].str.lower().value_counts()
        if "yes" in value_counts or "no" in value_counts:
            yes_no_counts[column] = {
                "yes": value_counts.get("yes", 0),
                "no": value_counts.get("no", 0),
            }

    # 3. Filter for columns containing only 'yes' or 'no'
    def is_binary_column(series):
        # Convert to lowercase and remove NaN values
        clean_series = series.str.lower().dropna()
        unique_values = set(clean_series.unique())
        return unique_values.issubset({"yes", "no"})

    binary_columns = [col for col in df.columns if is_binary_column(df[col])]
    binary_df = df[binary_columns].copy()

    # Remove rows where any column contains NaN values
    binary_df = binary_df.dropna(how="any")

    return nan_counts, yes_no_counts, binary_df


def extract_json_from_code_block(text):
    # Find the JSON content between the code block markers
    start = text.find("```json\n") + 8  # 8 is the length of '```json\n'
    end = text.rfind("\n```")

    if start == -1 or end == -1:
        raise ValueError("JSON code block not found in the input string")

    json_str = text[start:end].strip()

    # Parse the JSON string
    return json.loads(json_str)


def create_chat_engine(advert):
    if advert:
        documents = [Document(text=advert)]
        index = VectorStoreIndex.from_documents(documents)
        return index.as_chat_engine(
            chat_mode="context",
            llm=llm,
            memory=MEMORY,
            system_prompt=(
                "A a career forensic analyst you have deep insight into crime and criminal activity especially human trafficking.  "
                "Your express goal is to investigate online recruitment advert and extract pertinent factual detail."
            ),
        )
    else:
        st.error(f"Failed to extract text from URL: {advert}")
        return None


def process_adverts(adverts: List[Dict[str, Any]]) -> None:
    for advert in adverts:
        chat_engine = create_chat_engine(advert)
        if chat_engine:
            process_advert(advert)
        else:
            st.error(f"Failed to create chat engine for URL: {advert}")


def check_advert_presence(advert: str) -> bool:
    return False


def process_advert(advert: str) -> None:
    if not check_advert_presence(advert):
        chat_engine = create_chat_engine(advert)
        for prompt in cp.CLAUDE_PROMPTS:
            response = chat_engine.chat(cp.CLAUDE_PROMPTS[prompt])
            print(f"Response to {prompt}: {response}")


def extract_value(response, key):
    pattern = f'"{key}": ?"?([^,"}}]+)"?'
    match = re.search(pattern, str(response))
    return match.group(1) if match else ""


def extract_list(response, key):
    pattern = f'"{key}": ?\[(.*?)\]'
    match = re.search(pattern, str(response))
    if match:
        return [item.strip(' "') for item in match.group(1).split(",")]
    return []


def delete_analysis(IDn: int, prompt_name: str) -> None:
    parameters = {
        "IDn": IDn,
        "prompt_name": prompt_name,
    }

    delete_query = """MATCH (posting:Posting)-[:HAS_ANALYSIS {type: $prompt_name}]-(analysis:Analysis)
    WHERE ID(posting) = $IDn
    DETACH DELETE analysis"""

    logger.info(f"Delete existing analysis to Neo4j: {parameters}")

    try:
        nl.execute_neo4j_query(delete_query, parameters)
    except Exception as e:
        logger.error(f"Error deleting analysis to Neo4j: {str(e)}")


# The parse_confidence function is no longer needed as we handle the conversion in the analyse_advert function


def verify_analyis_existence(IDn: int, prompt_name: str) -> bool:
    parameters = {"IDn": IDn, "prompt_name": prompt_name}
    query = """
    MATCH (posting:Posting)-[has_analysis:HAS_ANALYSIS {}]->(analysis:Analysis)
    WHERE ID(posting) = $IDn and has_analysis.type = $prompt_name
    RETURN posting.post_id AS post_id
    """
    return len(nl.execute_neo4j_query(query, parameters)) > 0


def process_adverts_from_dataframe(IDn_list: list) -> None:
    for IDn in IDn_list:
        time.sleep(5)
        for prompt_name, prompt in cp.CLAUDE_PROMPTS.items():
            if verify_analyis_existence(IDn=IDn, prompt_name=prompt_name):
                print(
                    f"Analysis for IDn: {IDn} and  prompt_name = {prompt_name} exists!"
                )
                continue
            else:
                print(f"Processing IDn {IDn}")
                process_advert(IDn, prompt_name)
    return None


def process_advert(IDn: int, prompt_name: str) -> None:
    advert = nl.get_neo4j_advert(IDn)
    chat_engine = create_chat_engine(advert)
    print(f"Processing : {advert}")
    if chat_engine:
        advert_analysis = lf.analyse_advert(chat_engine, advert, prompt_name)
        print(f"Response to {prompt_name}: {advert_analysis}")
        nl.write_analysis_to_neo4j(IDn, prompt_name, advert_analysis)
    else:
        print(f"Failed to create chat engine for advert {advert}")
    return None


IDn = 573388
prompt_name = "bypass_prompt"
query = """MATCH (g:Group)-[:HAS_POSTING]-(n:Posting) WHERE (g.country_id) = 1 AND (n.text IS NOT NULL) AND NOT (n.text = "") RETURN ID(n) AS IDn, n.post_id AS post_id, n.text AS advert"""
parameters = {}
adverts = pd.DataFrame(nl.execute_neo4j_query(query, parameters))

adverts = pd.read_csv("results/adverts_sample_2024-10-03T10_35_46_17e314.csv")
new_prompts = [
    "requires_references",
    "multiple_applicants_prompt",
    "multiple_jobs_prompt",
]

subdirectory_path = "results"

# List all files in the subdirectory
files_in_subdirectory = [
    file
    for file in os.listdir(subdirectory_path)
    if os.path.isfile(os.path.join(subdirectory_path, file))
]


process_adverts_from_dataframe(adverts["IDn"][80:100])

# Loop through the outer loop with a progress bar
for IDn in tqdm(adverts["IDn"], desc="Processing IDs"):
    for prompt_name in tqdm(
        new_prompts, desc=f"Processing Prompts for ID: {IDn}", leave=False
    ):
        # delete_analysis(IDn=IDn, prompt_name=prompt_name)
        if verify_analyis_existence(IDn=IDn, prompt_name=prompt_name):
            print(f"Analysis for IDn: {IDn} and  prompt_name = {prompt_name} exists!")
            continue
        else:
            print(f"Processing IDn {IDn}")
            process_advert(IDn, prompt_name)
        process_advert(IDn=IDn, prompt_name=prompt_name)

for IDn in adverts["IDn"]:
    print(IDn)
    delete_analysis(IDn=IDn, prompt_name="unprofessional_writing_prompt")
    process_advert(IDn=IDn, prompt_name="unprofessional_writing_prompt")


for IDn in [573204]:
    delete_analysis(IDn=IDn, prompt_name="target_specific_group_prompt")
    process_advert(IDn=IDn, prompt_name="target_specific_group_prompt")

# ============================================================================================
flag_query = """MATCH p=(group:Group)-[]-(posting:Posting)-[r:HAS_ANALYSIS]->(analysis:Analysis)
RETURN posting.text AS advert, ID(group) AS group_id, ID(posting) AS IDn, posting.monitor_score AS monitor_score, r.type as flag, analysis.result as result """

# flags = execute_neo4j_query(flag_query, parameters={})

df = pd.DataFrame(nl.execute_neo4j_query(flag_query, parameters={}))
# df = df[["advert", "group_id", "IDn", "monitor_score", "flag"]+red_flags]
duplicates = df.duplicated(
    subset=["advert", "group_id", "IDn", "monitor_score", "flag"], keep=False
)
duplicate_rows = df[duplicates].sort_values(
    by=["advert", "group_id", "IDn", "monitor_score", "flag"]
)
list(duplicate_rows["flag"].unique())
print("Duplicate rows:")
print(duplicate_rows)
# Perform the pivot operation with multiple index columns
flags = df.pivot(
    index=["advert", "group_id", "IDn", "monitor_score"],
    columns="flag",
    values="result",
).reset_index()

flags = df.pivot_table(
    index=["advert", "group_id", "IDn", "monitor_score"],
    columns="flag",
    values="result",
    aggfunc="first",
).reset_index()

# If you want to ensure 'group_id' and 'post_id' are the first two columns
column_order = ["advert", "group_id", "IDn", "monitor_score"] + [
    col
    for col in flags.columns
    if col not in ["advert", "group_id", "IDn", "monitor_score"]
]
flags = flags[column_order]

flags[["advert", "group_id", "IDn", "monitor_score"] + red_flags].to_csv(
    "results/advert_flags.csv", index=False
)


# Run analysis
nan_counts, yes_no_counts, binary_df = analyze_dataframe(flags[red_flags])
model_data = flags[
    (flags["monitor_score"] != "unknown") & (~flags["monitor_score"].isna())
]
nan_counts, yes_no_counts, binary_df = analyze_dataframe(model_data[red_flags])
# Print results
print("NaN counts by column:")
print(nan_counts)
print("\nYes/No counts by column:")
for col, counts in yes_no_counts.items():
    print(f"{col}: {counts}")
print("\nColumns with only yes/no values:")
print(binary_df)


list(flags)
model_data.to_csv("results/advert_flags.csv", index=False)

# --------------------------------------------------------------------------------
confidence_query = """MATCH p=(posting:Posting)-[r:HAS_ANALYSIS]->(analysis:Analysis)
RETURN ID(posting) AS id, r.type as flag, analysis.confidence as confidence """

confidence = (
    pd.DataFrame(nl.execute_neo4j_query(confidence_query, parameters={}))
    .pivot(index="id", columns="flag", values="confidence")
    .reset_index()
)

confidence[["id"] + red_flags].to_csv("results/advert_confidence.csv", index=False)

# ============================================================================================
evidence_query = """MATCH p=(posting:Posting)-[r:HAS_ANALYSIS]->(analysis:Analysis)
RETURN ID(posting) AS id, r.type as flag, analysis.evidence as evidence """

evidence = (
    pd.DataFrame(nl.execute_neo4j_query(evidence_query, parameters={}))
    .pivot(index="id", columns="flag", values="evidence")
    .reset_index()
)
evidence[["id"] + red_flags].to_csv("results/advert_evidence.csv", index=False)
# ============================================================================================
explanation_query = """MATCH p=(posting:Posting)-[r:HAS_ANALYSIS]->(analysis:Analysis)
RETURN ID(posting) AS id, r.type as flag, analysis.explanation as explanation """


explanation = (
    pd.DataFrame(nl.execute_neo4j_query(explanation_query, parameters={}))
    .pivot(index="id", columns="flag", values="explanation")
    .reset_index()
)
explanation[["id"] + red_flags].to_csv("results/advert_explanation.csv", index=False)
# flags = execute_neo4j_query(flag_query, parameters={})

verify_analyis_existence(572527, "target_specific_group_prompt")
