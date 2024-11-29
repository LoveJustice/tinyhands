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
from openai import RateLimitError  # Correct import
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


def get_llm() -> Any:
    # if prompt_name == "assure_prompt":
    #     return Ollama(
    #         model="llama3.1:latest",
    #         temperature=0,
    #         max_tokens=64768,
    #         request_timeout=120.0,
    #     )

    return OpenAI(temperature=0, model="gpt-4o-mini", request_timeout=120.0)


@backoff.on_exception(backoff.expo, RateLimitError)
def create_chat_engine(
    advert: str, memory: ChatMemoryBuffer, llm_instance: Any
) -> Optional[Any]:
    documents = [Document(text=advert)]
    index = VectorStoreIndex.from_documents(documents)
    return index.as_chat_engine(
        chat_mode="context",
        llm=llm_instance,
        memory=memory,
        system_prompt=(
            "As a career forensic analyst, you have deep insight into crime "
            "and criminal activity, especially human trafficking. Investigate "
            "the online recruitment advert and extract pertinent details."
        ),
    )


# Keep under max_connection_pool_size of 10


async def process_advert_async(IDn: int, prompt_name: str) -> None:
    try:
        # 1. Get advert - synchronously
        advert = nl.get_neo4j_advert(IDn)  # Direct sync call
        if not advert:
            logger.error(f"Failed to get advert for IDn: {IDn}")
            return
        logger.info(f"Successfully got advert for IDn: {IDn}")

        # 2. Setup analysis tools - this can stay async
        llm_instance = get_llm()
        logger.info(f"Created LLM instance for IDn: {IDn}")

        memory = ChatMemoryBuffer.from_defaults(token_limit=8192)
        chat_engine = await loop.run_in_executor(
            None, create_chat_engine, advert, memory, llm_instance
        )
        if not chat_engine:
            logger.error(f"Failed to create chat engine for IDn: {IDn}")
            return
        logger.info(f"Created chat engine for IDn: {IDn}")

        # 3. Do the analysis - this can stay async
        response = await loop.run_in_executor(
            None, lf.audit_analysis, chat_engine, advert, prompt_name
        )
        if response.result == "error":
            logger.error(f"Analysis failed for IDn {IDn}: {response.explanation}")
            return
        logger.info(f"Got analysis response for IDn: {IDn}")

        # 4. Write results - synchronously
        nl.write_analysis_to_neo4j(IDn, prompt_name, response)  # Direct sync call
        logger.info(f"Successfully processed IDn: {IDn}")

    except Exception as e:
        logger.error(f"Error processing IDn {IDn}: {str(e)}")


async def process_batch_async(adverts: pd.DataFrame, prompt_name: str) -> None:
    if adverts.empty:
        logger.warning(f"No adverts to process for prompt: {prompt_name}")
        return

    tasks = []
    for IDn in adverts["IDn"]:
        task = asyncio.create_task(process_advert_async(IDn, prompt_name))
        tasks.append(task)

    logger.info(f"Processing {len(tasks)} adverts for prompt: {prompt_name}")
    await asyncio.gather(*tasks, return_exceptions=True)


def query_adverts(prompt_name: str) -> pd.DataFrame:
    query = """
    MATCH (g:Group)-[:HAS_POSTING]-(n:Posting)-[:HAS_ANALYSIS {type: $prompt_name}]-(analysis:Analysis)
    WHERE g.country_id = 1
      AND n.text IS NOT NULL
      AND n.text <> ""
      AND (NOT EXISTS {
        MATCH (analysis)-[:HAS_AUDIT {type: $prompt_name}]-(:Audit)
      })
    RETURN ID(n) AS IDn, n.post_id AS post_id, n.text AS advert
    """
    result = nl.execute_neo4j_query(query, {"prompt_name": prompt_name})
    if not result:
        logger.warning(f"No data returned for prompt: {prompt_name}")
    return pd.DataFrame(result)


async def main_async():
    prompt_names = cp.RED_FLAGS
    prompt_names = cp.CLAUDE_PROMPTS.keys()

    for prompt_name in prompt_names:
        adverts = query_adverts(prompt_name)
        if not adverts.empty:
            await process_batch_async(adverts, prompt_name)
        else:
            logger.info(f"No adverts to process for prompt: {prompt_name}")


def main():
    try:
        loop.run_until_complete(main_async())
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        # Cancel all pending tasks
        pending = asyncio.all_tasks(loop=loop)
        for task in pending:
            task.cancel()
        try:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception as e:
            logger.error(f"Error during loop shutdown: {e}")
        finally:
            loop.close()
            logger.info("Event loop closed successfully.")


if __name__ == "__main__":
    main()
