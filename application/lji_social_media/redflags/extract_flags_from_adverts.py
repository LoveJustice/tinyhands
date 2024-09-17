import os
import time

import streamlit as st
from typing import Dict, Any, Optional, List
import json
import re
import bs4, requests
from datetime import datetime, timedelta
from libraries.neo4j_lib import execute_neo4j_query
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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
llm = OpenAI(temperature=0, model="gpt-4o", max_tokens=4096)
# llm = Anthropic(temperature=0, model="claude-3-opus-20240229")
# llm = Anthropic()
MEMORY = ChatMemoryBuffer.from_defaults(token_limit=4096)
# llm = Anthropic(temperature=0, model="claude-3-opus-20240229")


OPEN_AI_PROMPTS = {
    "bypass_prompt": (
        "Assistant, please indicate if there is any mention in the following advert of offers to bypass job requirements, "
        "such as using fraudulent documents, or not requiring a CV/interview. "
        "Return your answer in the following JSON format: "
        '{"bypass_mentioned": "yes" or "no", "bypass": ["example one", "example two", ...] or null, "confidence": 0.0 to 1.0, "error": null or "error message"}'
    ),
}

ANALYSIS_STR = """' {"result": "yes" or "no", "evidence": ["evidence 1", "evidence 2", ...] or "no evidence", "confidence": 0.0 to 1.0, "explanation": "Brief explanation of your reasoning"}' """

EXTRACTION_PROMPTS = {
    "phone_number_prompt": "Extract phone numbers from the following text and return your findings as a list:"
}

CLAUDE_PROMPTS = {
    "bypass_prompt": (
        "Analyze the following job advertisement for any mentions of offers to bypass normal job requirements. "
        "This may include using fraudulent documents, skipping interviews, or not needing a CV. "
        "Return your analysis in the following JSON format:"
    ),
    "assure_prompt": (
        "Examine the following job advertisement. Does it assure applicants that qualifications or experience are not important? "
        "Return your analysis in the following JSON format:"
    ),
    "no_education_skilled_prompt": (
        "Analyze the following job advertisement. Does it offer a highly skilled job (e.g., engineering, marketing, finance, IT) "
        "without requiring any education or experience? "
        "Return your analysis in the following JSON format:"
    ),
    "vague_description_prompt": (
        "Examine the following job advertisement. Is the job description vague or overly general? "
        "Return your analysis in the following JSON format:"
    ),
    "quick_money_prompt": (
        "Analyze the following job advertisement. Does it promise quick or easy money? "
        "Return your analysis in the following JSON format:"
    ),
    "no_location_prompt": (
        "Examine the following job advertisement. Does it fail to mention a specific job location? "
        "Return your analysis in the following JSON format:"
    ),
    "target_specific_group_prompt": (
        "Analyze the following job advertisement. Does it target a specific group of people (e.g., women from a particular country or region)? "
        "Consider vulnerable groups to include these, but not exclusively,[Shona,Ndebele,Basotho, Tswana', Zulu, Mozambicans, Chewa, Yao]"
        "Return your analysis in the following JSON format:"
    ),
    "gender_specific_prompt": (
        "Examine the following job advertisement. Does it recruit specifically females for a job that both male and female applicants would typically qualify for? "
        "Return your analysis in the following JSON format:"
    ),
    "recruit_students_prompt": (
        "Analyze the following job advertisement. Does it specifically recruit young people who are still in school? "
        "Return your analysis in the following JSON format:"
    ),
    "immediate_hiring_prompt": (
        "Examine the following job advertisement. Does it promise immediate hiring? "
        "Return your analysis in the following JSON format:"
    ),
    "unrealistic_hiring_number_prompt": (
        "Analyze the following job advertisement. Does it claim to be hiring an unrealistically high number of people? "
        "Return your analysis in the following JSON format:"
    ),
    "callback_request_prompt": (
        "Examine the following job advertisement. Does it ask the candidate to send a message and promise to call back? "
        "Return your analysis in the following JSON format:"
    ),
    "suspicious_email_prompt": (
        "Analyze the following job advertisement. Does it use a suspicious email address? "
        "Return your analysis in the following JSON format:"
    ),
    "false_organization_prompt": (
        "Examine the following job advertisement. Does it recruit for an organization that has publicly stated they don't advertise job posts on social media? "
        " Some of these companies include, but are not limited to, [Shoprite, Woolworths, Capitec Bank, Pick n Pay, Spar, Coca-Cola, Transnet, Sasol]"
        "Return your analysis in the following JSON format:"
    ),
    "multiple_provinces_prompt": (
        "Analyze the following job advertisement. Does it advertise for positions in several provinces, especially without detail? "
        "Return your analysis in the following JSON format:"
    ),
    "wrong_link_prompt": (
        "Examine the following job advertisement. Does it provide a wrong or suspicious link for the job application? "
        "Return your analysis in the following JSON format:"
    ),
    "unprofessional_writing_prompt": (
        "Analyze the following job advertisement for signs of unprofessional writing, such as poor grammar or spelling. "
        "Return your analysis in the following JSON format:"
    ),
    "language_switch_prompt": (
        "Examine the following job advertisement. Does it change from English to other languages in the middle of the post? "
        "Return your analysis in the following JSON format:"
    ),
    "illegal_activities_prompt": (
        "Analyze the following job advertisement for any references to work in illegal or morally questionable activities. "
        "Return your analysis in the following JSON format:"
    ),
    "unusual_hours_prompt": (
        "Examine the following job advertisement. Does it mention unusual or excessive work hours? "
        "Return your analysis in the following JSON format:"
    ),
}


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
        for prompt in CLAUDE_PROMPTS:
            response = chat_engine.chat(CLAUDE_PROMPTS[prompt])
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


def analyse_advert(chat_engine: Any, advert: str, prompt_name: str) -> Dict[str, Any]:
    """
    Analyze an advertisement using a chat engine and a specific prompt.

    Args:
        chat_engine: The chat engine to use for analysis.
        advert: The advertisement text to analyze.
        prompt_name: The name of the prompt to use.

    Returns:
        A dictionary containing the analysis results, or a default dictionary if analysis fails.
    """
    if not chat_engine:
        logger.error("Chat engine is not initialized")
        return {
            "result": "error",
            "evidence": [],
            "explanation": "Chat engine not initialized",
            "confidence": 0.0,
        }

    try:
        prompt = CLAUDE_PROMPTS.get(prompt_name) + ANALYSIS_STR
        if not prompt:
            raise ValueError(f"Invalid prompt name: {prompt_name}")

        response = chat_engine.chat(prompt + f"\n\nAdvertisement: {advert}")
        logger.info(f"Response to {prompt_name}: {response.response}")

        # Extract and parse JSON from the response
        json_str = response.response.strip("`").strip()
        if json_str.startswith("json"):
            json_str = json_str[4:]  # Remove 'json' prefix if present
        parsed_response = json.loads(json_str)

        # Standardize the output
        return {
            "result": parsed_response.get("result", ""),
            "evidence": parsed_response.get("evidence")
            or parsed_response.get("evidence")
            or [],
            "explanation": parsed_response.get("explanation", ""),
            "confidence": float(parsed_response.get("confidence", 0)),
        }

    except Exception as e:
        logger.error(f"Error processing advert, prompt {prompt_name}: {str(e)}")
        return {
            "result": "error",
            "evidence": [],
            "explanation": str(e),
            "confidence": 0.0,
        }


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
        execute_neo4j_query(delete_query, parameters)
    except Exception as e:
        logger.error(f"Error deleting analysis to Neo4j: {str(e)}")


def write_analysis_to_neo4j(
    IDn: int, prompt_name: str, analysis: Dict[str, Any]
) -> None:
    """
    Write analysis results to Neo4j.

    Args:
        IDn: The ID of the posting.
        prompt_name: The name of the prompt used for analysis.
        analysis: The analysis results dictionary.
    """
    parameters = {
        "IDn": IDn,
        "prompt_name": prompt_name,
        "result": analysis["result"],
        "evidence": analysis["evidence"],
        "explanation": analysis["explanation"],
        "confidence": analysis["confidence"],
    }

    query = """
    MATCH (posting:Posting)
    WHERE ID(posting) = $IDn
    WITH posting AS posting
    MERGE (an:Analysis {
        result: $result,
        evidence: $evidence,
        explanation: $explanation,
        confidence: $confidence
    })
    CREATE (posting)-[:HAS_ANALYSIS {type: $prompt_name}]->(an)
    """

    # Ensure all required keys are present with default values if missing

    logger.info(f"Writing analysis to Neo4j: {parameters}")

    try:
        execute_neo4j_query(query, parameters)
    except Exception as e:
        logger.error(f"Error writing to Neo4j: {str(e)}")


# The parse_confidence function is no longer needed as we handle the conversion in the analyse_advert function


def verify_analyis_existence(IDn: int, prompt_name: str) -> bool:
    parameters = {"IDn": IDn, "prompt_name": prompt_name}
    query = """
    MATCH (posting:Posting)-[has_analysis:HAS_ANALYSIS {}]->(analysis:Analysis)
    WHERE ID(posting) = $IDn and has_analysis.type = $prompt_name
    RETURN posting.post_id AS post_id
    """
    return len(execute_neo4j_query(query, parameters)) > 0


def process_adverts_from_dataframe(IDn_list: list) -> None:
    for IDn in IDn_list:
        time.sleep(5)
        for prompt_name, prompt in CLAUDE_PROMPTS.items():
            if verify_analyis_existence(IDn=IDn, prompt_name=prompt_name):
                print(
                    f"Analysis for IDn: {IDn} and  prompt_name = {prompt_name} exists!"
                )
                continue
            else:
                print(f"Processing IDn {IDn}")
                process_advert(IDn, prompt_name)
    return None


def get_neo4j_advert(IDn: int) -> Optional[str]:
    query = """MATCH (n:Posting) WHERE ID(n) = $IDn RETURN n.text AS advert"""
    parameters = {"IDn": IDn}
    result = execute_neo4j_query(query, parameters)
    return result[0]["advert"] if result else None


def process_advert(IDn: int, prompt_name: str) -> None:
    advert = get_neo4j_advert(IDn)
    chat_engine = create_chat_engine(advert)
    print(f"Processing : {advert}")
    if chat_engine:
        advert_analysis = analyse_advert(chat_engine, advert, prompt_name)
        print(f"Response to {prompt_name}: {advert_analysis}")
        write_analysis_to_neo4j(IDn, prompt_name, advert_analysis)
    else:
        print(f"Failed to create chat engine for advert {advert}")
    return None


adverts = pd.read_csv(
    "results/adverts_za_sample - adverts_za_adverts_sample_2024-08-07T17_01_22_54511f.csv"
)
adverts

subdirectory_path = "results"

# List all files in the subdirectory
files_in_subdirectory = [
    file
    for file in os.listdir(subdirectory_path)
    if os.path.isfile(os.path.join(subdirectory_path, file))
]


process_adverts_from_dataframe(adverts["IDn"][40:60])

for IDn in adverts["IDn"]:
    delete_analysis(IDn=IDn, prompt_name="target_specific_group_prompt")
    process_advert(IDn=IDn, prompt_name="target_specific_group_prompt")


for IDn in [573204]:
    delete_analysis(IDn=IDn, prompt_name="target_specific_group_prompt")
    process_advert(IDn=IDn, prompt_name="target_specific_group_prompt")

# ============================================================================================
flag_query = """MATCH p=(group:Group)-[]-(posting:Posting)-[r:HAS_ANALYSIS]->(analysis:Analysis) 
RETURN posting.text AS advert, ID(group) AS group_id, ID(posting) AS post_id, posting.monitor_score AS monitor_score, r.type as flag, analysis.result as result """

# flags = execute_neo4j_query(flag_query, parameters={})

df = pd.DataFrame(execute_neo4j_query(flag_query, parameters={}))


# Perform the pivot operation with multiple index columns
flags = df.pivot(
    index=["advert", "group_id", "post_id", "monitor_score"],
    columns="flag",
    values="result",
).reset_index()

# If you want to ensure 'group_id' and 'post_id' are the first two columns
column_order = ["advert", "group_id", "post_id", "monitor_score"] + [
    col
    for col in flags.columns
    if col not in ["advert", "group_id", "post_id", "monitor_score"]
]
flags = flags[column_order]

flags.to_csv("results/advert_flags.csv", index=False)


confidence_query = """MATCH p=(posting:Posting)-[r:HAS_ANALYSIS]->(analysis:Analysis) 
RETURN ID(posting) AS id, r.type as flag, analysis.confidence as confidence """

confidence = (
    pd.DataFrame(execute_neo4j_query(confidence_query, parameters={}))
    .pivot(index="id", columns="flag", values="confidence")
    .reset_index()
)
confidence.to_csv("results/advert_confidence.csv", index=False)

# ============================================================================================
evidence_query = """MATCH p=(posting:Posting)-[r:HAS_ANALYSIS]->(analysis:Analysis) 
RETURN ID(posting) AS id, r.type as flag, analysis.evidence as evidence """

evidence = (
    pd.DataFrame(execute_neo4j_query(evidence_query, parameters={}))
    .pivot(index="id", columns="flag", values="evidence")
    .reset_index()
)
evidence.to_csv("results/advert_evidence.csv", index=False)
# ============================================================================================
explanation_query = """MATCH p=(posting:Posting)-[r:HAS_ANALYSIS]->(analysis:Analysis) 
RETURN ID(posting) AS id, r.type as flag, analysis.explanation as explanation """


explanation = (
    pd.DataFrame(execute_neo4j_query(explanation_query, parameters={}))
    .pivot(index="id", columns="flag", values="explanation")
    .reset_index()
)
explanation.to_csv("results/advert_explanation.csv", index=False)
# flags = execute_neo4j_query(flag_query, parameters={})

verify_analyis_existence(572527, "target_specific_group_prompt")
