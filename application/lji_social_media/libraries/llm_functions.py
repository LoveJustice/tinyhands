import sys

sys.path.append("../libraries/")
import pandas as pd
from typing import Any, Dict
import logging
import json
from libraries import claude_prompts as cp
from libraries import neo4j_lib as nl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        prompt = cp.CLAUDE_PROMPTS.get(prompt_name) + cp.ANALYSIS_STR
        if not prompt:
            raise ValueError(f"Invalid prompt name: {prompt_name}")

        response = chat_engine.chat(prompt + f"\n\nAdvertisement: {advert}")
        logger.info(f"Response to {prompt_name}: {response.response}")

        # Extract and parse JSON from the response
        json_str = response.response.strip("`").strip()
        if json_str.startswith("json"):
            json_str = json_str[4:]  # Remove 'json' prefix if present
        parsed_response = json.loads(json_str)

        analysis_response = nl.AnalysisResponse(**parsed_response)
        # Standardize the output
        return analysis_response

    except Exception as e:
        logger.error(f"Error processing advert, prompt {prompt_name}: {str(e)}")
        return {
            "result": "error",
            "evidence": [],
            "explanation": str(e),
            "confidence": 0.0,
        }
