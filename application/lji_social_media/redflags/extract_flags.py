#!/usr/bin/env python3
"""
Module for processing recruitment adverts using a chat engine and analyzing them via Neo4j.
"""

import os
import sys
import time
import json
import re
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
from tqdm import tqdm

import streamlit as st

import libraries.claude_prompts as cp
import libraries.llm_functions as lf
import libraries.neo4j_lib as nl

from pydantic import BaseModel, Field, ValidationError
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core import VectorStoreIndex, Document
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic

# ------------------------------------------------------------------------------
# Logging Setup
# ------------------------------------------------------------------------------

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "extract_flags.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Path Configuration
# ------------------------------------------------------------------------------

# Append the absolute path to the libraries directory if not already present.
MODULE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../libraries"))
if MODULE_PATH not in sys.path:
    sys.path.append(MODULE_PATH)

# ------------------------------------------------------------------------------
# Global LLM and Memory Initialization
# ------------------------------------------------------------------------------

llm = OpenAI(temperature=0, model="o3-mini", max_tokens=4096)
MEMORY = ChatMemoryBuffer.from_defaults(token_limit=4096)

# ------------------------------------------------------------------------------
# Utility Functions
# ------------------------------------------------------------------------------


def extract_json_from_code_block(text: str) -> Any:
    """
    Extract and parse JSON content from a text containing a JSON code block.

    Args:
        text (str): The text containing the JSON code block.

    Returns:
        Any: The parsed JSON data.

    Raises:
        ValueError: If the JSON code block is not found.
    """
    start = text.find("```json\n") + len("```json\n")
    end = text.rfind("\n```")
    if start == -1 or end == -1:
        raise ValueError("JSON code block not found in the input string")
    json_str = text[start:end].strip()
    return json.loads(json_str)


# ------------------------------------------------------------------------------
# Chat Engine and Advert Processing Functions
# ------------------------------------------------------------------------------


def create_chat_engine(advert: str) -> Optional[Any]:
    """
    Create a chat engine instance for a given advert text.

    Args:
        advert (str): The advert text to process.

    Returns:
        Optional[Any]: The chat engine instance or None if advert is empty.
    """
    if advert:
        documents = [Document(text=advert)]
        index = VectorStoreIndex.from_documents(documents)
        return index.as_chat_engine(
            chat_mode="context",
            llm=llm,
            memory=MEMORY,
            system_prompt=(
                "As a career forensic analyst with deep insight into crime and criminal activity, especially human trafficking, "
                "your explicit goal is to investigate online recruitment adverts and extract pertinent factual detail."
            ),
        )
    else:
        error_msg = f"Failed to extract text from advert: {advert}"
        st.error(error_msg)
        logger.error(error_msg)
        return None


def check_advert_presence(advert: str) -> bool:
    """
    Check if the advert is already present (stub implementation).

    Args:
        advert (str): The advert text.

    Returns:
        bool: Always returns False.
    """
    # Stub implementation; replace with actual check if needed.
    return False


def process_advert_text(advert: str) -> None:
    """
    Process an advert text by running all available prompts if the advert is not already present.

    Args:
        advert (str): The advert text.
    """
    if not check_advert_presence(advert):
        chat_engine = create_chat_engine(advert)
        if chat_engine:
            for prompt_name, prompt_text in cp.CLAUDE_PROMPTS.items():
                response = chat_engine.chat(prompt_text)
                logger.info(f"Response to {prompt_name}: {response}")
        else:
            logger.error("Chat engine creation failed for advert.")
    else:
        logger.info("Advert already processed.")


def extract_value(response: Any, key: str) -> str:
    """
    Extract the value associated with a key from a response string using regex.

    Args:
        response (Any): The response string.
        key (str): The key to search for.

    Returns:
        str: The extracted value or empty string if not found.
    """
    pattern = f'"{key}": ?"?([^,"}}]+)"?'
    match = re.search(pattern, str(response))
    return match.group(1) if match else ""


def extract_list(response: Any, key: str) -> List[str]:
    """
    Extract a list associated with a key from a response string using regex.

    Args:
        response (Any): The response string.
        key (str): The key to search for.

    Returns:
        List[str]: The extracted list or an empty list if not found.
    """
    pattern = f'"{key}": ?\\[(.*?)\\]'
    match = re.search(pattern, str(response))
    if match:
        return [
            item.strip(' "') for item in match.group(1).split(",") if item.strip(' "')
        ]
    return []


def delete_analysis(IDn: int, prompt_name: str) -> None:
    """
    Delete existing analysis from Neo4j for a given posting ID and prompt.

    Args:
        IDn (int): The Neo4j node ID.
        prompt_name (str): The name of the prompt.
    """
    parameters = {"IDn": IDn, "prompt_name": prompt_name}
    delete_query = (
        "MATCH (posting:Posting)-[:HAS_ANALYSIS {type: $prompt_name}]-(analysis:Analysis) "
        "WHERE ID(posting) = $IDn "
        "DETACH DELETE analysis"
    )
    logger.info(f"Deleting existing analysis in Neo4j: {parameters}")
    try:
        nl.execute_neo4j_query(delete_query, parameters)
    except Exception as e:
        logger.error(f"Error deleting analysis in Neo4j: {e}")


def verify_analysis_existence(IDn: int, prompt_name: str) -> bool:
    """
    Verify if an analysis exists in Neo4j for a given posting ID and prompt.

    Args:
        IDn (int): The Neo4j node ID.
        prompt_name (str): The name of the prompt.

    Returns:
        bool: True if analysis exists, False otherwise.
    """
    parameters = {"IDn": IDn, "prompt_name": prompt_name}
    query = (
        "MATCH (posting:Posting)-[has_analysis:HAS_ANALYSIS {}]->(analysis:Analysis) "
        "WHERE ID(posting) = $IDn AND has_analysis.type = $prompt_name "
        "RETURN posting.post_id AS post_id"
    )
    results = nl.execute_neo4j_query(query, parameters)
    return len(results) > 0


def process_adverts_from_dataframe(IDn_list: List[int]) -> None:
    """
    Process multiple adverts identified by their Neo4j node IDs from a dataframe.

    Args:
        IDn_list (List[int]): List of Neo4j node IDs.
    """
    for IDn in IDn_list:
        time.sleep(5)
        for prompt_name in cp.CLAUDE_PROMPTS.keys():
            if verify_analysis_existence(IDn=IDn, prompt_name=prompt_name):
                logger.info(
                    f"Analysis for IDn {IDn} and prompt '{prompt_name}' already exists."
                )
                continue
            else:
                logger.info(
                    f"Processing advert with IDn {IDn} for prompt '{prompt_name}'."
                )
                process_advert_by_id(IDn, prompt_name)


def process_advert_by_id(IDn: int, prompt_name: str) -> None:
    """
    Process an advert by its Neo4j node ID and a specific prompt.

    Args:
        IDn (int): The Neo4j node ID.
        prompt_name (str): The name of the prompt to be applied.
    """
    advert = nl.get_neo4j_advert(IDn)
    chat_engine = create_chat_engine(advert)
    logger.info(f"Processing advert: {advert}")
    if chat_engine:
        advert_analysis = lf.analyse_advert(chat_engine, prompt_name)
        logger.info(f"Response to '{prompt_name}': {advert_analysis}")
        nl.write_analysis_to_neo4j(IDn, prompt_name, advert_analysis)
    else:
        logger.error(f"Failed to create chat engine for advert: {advert}")


# ------------------------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------------------------


def main() -> None:
    """
    Main function to process recruitment adverts from Neo4j.
    """
    query = (
        "MATCH (g:Group)-[:HAS_POSTING]-(n:RecruitmentAdvert) "
        "WHERE g.country_id = 1 AND n.text IS NOT NULL AND n.text <> '' "
        "RETURN ID(n) AS IDn, n.post_id AS post_id, n.text AS advert"
    )
    parameters = {}
    adverts_df = pd.DataFrame(nl.execute_neo4j_query(query, parameters))

    prompt_names = list(cp.CLAUDE_PROMPTS.keys())

    for IDn in tqdm(adverts_df["IDn"], desc="Processing IDs"):
        for prompt_name in tqdm(
            prompt_names, desc=f"Processing prompts for ID {IDn}", leave=False
        ):
            if verify_analysis_existence(IDn=IDn, prompt_name=prompt_name):
                logger.info(
                    f"Analysis for IDn {IDn} and prompt '{prompt_name}' already exists."
                )
                continue
            else:
                logger.info(
                    f"Processing advert with IDn {IDn} for prompt '{prompt_name}'."
                )
                process_advert_by_id(IDn, prompt_name)


if __name__ == "__main__":
    main()
