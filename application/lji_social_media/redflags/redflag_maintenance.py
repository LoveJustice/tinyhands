import os
import sys
import tiktoken


def count_tokens(text, model_name):
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))


# Add the parent directory of both redflags and libraries to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)

# Import modules from libraries
try:
    from libraries import llm_functions as lf
    from libraries import neo4j_lib as nl
    from libraries import claude_prompts as cp
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# Confirming the path addition
print(f"Parent directory added to sys.path: {parent_dir}")

import time
import streamlit as st

from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core import VectorStoreIndex, Document
import pandas as pd
import json
from typing import Optional, Dict, Any
import re
import logging
from tqdm import tqdm

from llama_index.llms.ollama import Ollama
from typing import Any, List, Optional
from llama_index.llms.openai import OpenAI


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# llm = OpenAI(temperature=0, model="gpt-4o mini", max_tokens=8192, request_timeout=120.0)
llm = Ollama(
    model="llama3.1:latest", temperature=0, max_tokens=32768, request_timeout=120.0
)
llm = OpenAI(temperature=0, model="o1-mini", request_timeout=120.0)
# llm = Ollama(model="llama3.1", temperature=0, max_tokens=4096)
# llm = Anthropic(temperature=0, model="claude-3-opus-20240229")
# llm = Anthropic()
# MEMORY = ChatMemoryBuffer.from_defaults(token_limit=32768, memory_limit=1)
MEMORY = ChatMemoryBuffer.from_defaults(token_limit=8192)
# llm = Anthropic(temperature=0, model="claude-3-opus-20240229")


def count_tokens(text, model_name):
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))


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


def check_analysis_presence(IDn, prompt) -> bool:
    query = """MATCH (posting:Posting)-[:HAS_ANALYSIS {type: $prompt}]-(analysis:Analysis)
    WHERE ID(posting) = $IDn
    RETURN COUNT(analysis) AS analysis_count"""
    parameters = {"prompt": prompt, "IDn": IDn}
    result = nl.execute_neo4j_query(query, parameters)
    return result[0]["analysis_count"] > 0


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


# In your main script or where you call write_analysis_to_neo4j
def process_advert(IDn: int, prompt_name: str) -> None:
    advert = nl.get_neo4j_advert(IDn)
    # print(f" Count tokens: {count_tokens(advert, 'gpt-4o mini')}")
    chat_engine = create_chat_engine(advert)
    print(f"Processing : {advert}")
    if chat_engine:
        advert_analysis = lf.analyse_advert(chat_engine, advert, prompt_name)
        print(f"Response IDn:{IDn} to {prompt_name}: {advert_analysis}")
        if advert_analysis:
            nl.write_analysis_to_neo4j(IDn, prompt_name, advert_analysis)
        else:
            logger.error(f"Analysis failed for IDn {IDn}")
    else:
        print(f"Failed to create chat engine for advert {advert}")
    return None


def main() -> None:
    # prompt_names = [
    #     # "suspicious_email_prompt",
    #     "recruit_students_prompt",
    #     "gender_specific_prompt",
    #     "vague_description_prompt",
    #     "assure_prompt",
    # ]
    prompt_names = cp.RED_FLAGS
    for prompt_name in prompt_names:
        query = """
        MATCH (g:Group)-[:HAS_POSTING]-(n:Posting)
        WHERE g.country_id = 1
          AND n.text IS NOT NULL
          AND n.text <> ""
          AND (NOT EXISTS {
            MATCH (n)-[:HAS_ANALYSIS {type: $prompt_name}]-(:Analysis)
          })
        RETURN ID(n) AS IDn, n.post_id AS post_id, n.text AS advert
        """
        parameters = {"prompt_name": prompt_name}
        adverts = pd.DataFrame(nl.execute_neo4j_query(query, parameters))

        for IDn in tqdm(adverts["IDn"], desc="Processing adverts"):
            # delete_analysis(IDn=IDn, prompt_name="unprofessional_writing_prompt")
            MEMORY.reset()
            process_advert(IDn=IDn, prompt_name=prompt_name)


if __name__ == "__main__":
    main()
