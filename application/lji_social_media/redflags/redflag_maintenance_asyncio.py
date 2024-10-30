import os
import sys
import tiktoken
import concurrent.futures
import asyncio
import time
import logging
import pandas as pd
import json
import re
from typing import Any, List, Dict, Optional
from openai import RateLimitError

# from openai.error import RateLimitError
import backoff


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

from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core import VectorStoreIndex, Document

from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Create a single event loop for the application
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Semaphore for Neo4j connections
neo4j_semaphore = asyncio.Semaphore(8)
# Model and memory configurations
llm = Ollama(
    model="llama3.1:latest", temperature=0, max_tokens=64768, request_timeout=120.0
)
llm = OpenAI(temperature=0, model="o1-mini", request_timeout=120.0)
MEMORY = ChatMemoryBuffer.from_defaults(token_limit=8192)


# Utility functions
def count_tokens(text: str, model_name: str) -> int:
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))


def extract_json_from_code_block(text: str) -> dict:
    start = text.find("```json\n") + 8
    end = text.rfind("\n```")
    if start == -1 or end == -1:
        raise ValueError("JSON code block not found")
    return json.loads(text[start:end].strip())


def extract_value(response: str, key: str) -> str:
    pattern = f'"{key}": ?"?([^,"}}]+)"?'
    match = re.search(pattern, response)
    return match.group(1) if match else ""


def extract_list(response: str, key: str) -> List[str]:
    pattern = f'"{key}": ?\[(.*?)\]'
    match = re.search(pattern, response)
    return [item.strip(' "') for item in match.group(1).split(",")] if match else []


# Neo4j-related functions
def check_analysis_presence(IDn: int, prompt: str) -> bool:
    query = """MATCH (posting:Posting)-[:HAS_ANALYSIS {type: $prompt}]-(analysis:Analysis)
               WHERE ID(posting) = $IDn
               RETURN COUNT(analysis) AS analysis_count"""
    result = nl.execute_neo4j_query(query, {"prompt": prompt, "IDn": IDn})
    return result[0]["analysis_count"] > 0


def delete_analysis(IDn: int, prompt_name: str) -> None:
    query = """MATCH (posting:Posting)-[:HAS_ANALYSIS {type: $prompt_name}]-(analysis:Analysis)
               WHERE ID(posting) = $IDn
               DETACH DELETE analysis"""
    nl.execute_neo4j_query(query, {"IDn": IDn, "prompt_name": prompt_name})
    logger.info(f"Deleted existing analysis for IDn: {IDn}, prompt: {prompt_name}")


@backoff.on_exception(backoff.expo, RateLimitError)
def create_chat_engine(advert: str) -> Optional[Any]:
    documents = [Document(text=advert)]
    index = VectorStoreIndex.from_documents(documents)
    return index.as_chat_engine(
        chat_mode="context",
        llm=llm,
        memory=MEMORY,
        system_prompt=(
            "As a career forensic analyst, you have deep insight into crime "
            "and criminal activity, especially human trafficking. Investigate "
            "the online recruitment advert and extract pertinent details."
        ),
    )


# Keep under max_connection_pool_size of 10


async def process_advert_async(IDn: int, prompt_name: str) -> None:
    try:
        async with neo4j_semaphore:
            # Get advert
            advert = await loop.run_in_executor(None, nl.get_neo4j_advert, IDn)
            if not advert:
                logger.error(f"Failed to get advert for IDn: {IDn}")
                return

            # Create chat engine
            chat_engine = create_chat_engine(advert)
            if not chat_engine:
                logger.error(f"Failed to create chat engine for IDn: {IDn}")
                return

            # Analyze advert
            try:
                response = await loop.run_in_executor(
                    None, lf.analyse_advert, chat_engine, advert, prompt_name
                )
                if response:
                    await loop.run_in_executor(
                        None, nl.write_analysis_to_neo4j, IDn, prompt_name, response
                    )
                    logger.info(f"Successfully processed IDn: {IDn}")
            except Exception as e:
                logger.error(f"Error processing IDn {IDn}: {str(e)}")
    except Exception as e:
        logger.error(f"Outer error processing IDn {IDn}: {str(e)}")


async def process_batch_async(adverts: pd.DataFrame, prompt_name: str) -> None:
    if adverts.empty:
        logger.warning(f"No adverts to process for prompt: {prompt_name}")
        return

    tasks = []
    for IDn in adverts["IDn"]:
        task = loop.create_task(process_advert_async(IDn, prompt_name))
        tasks.append(task)

    logger.info(f"Processing {len(tasks)} adverts for prompt: {prompt_name}")
    await asyncio.gather(*tasks, return_exceptions=True)


def query_adverts(prompt_name: str) -> pd.DataFrame:
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
    result = nl.execute_neo4j_query(query, {"prompt_name": prompt_name})
    if not result:
        logger.warning(f"No data returned for prompt: {prompt_name}")
    return pd.DataFrame(result)


def main():
    prompt_names = [
        "recruit_students_prompt",
        "gender_specific_prompt",
        "vague_description_prompt",
        "assure_prompt",
    ]

    try:
        for prompt_name in prompt_names:
            adverts = query_adverts(prompt_name)
            if not adverts.empty:
                loop.run_until_complete(process_batch_async(adverts, prompt_name))
            else:
                logger.info(f"No adverts to process for prompt: {prompt_name}")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
