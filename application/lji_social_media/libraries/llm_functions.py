import sys
import os
import re

sys.path.append("../libraries/")
import pandas as pd
from typing import Any, Dict
import logging
import json
from libraries import claude_prompts as cp
from libraries import neo4j_lib as nl


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import json
import logging
from typing import Any, Dict, List
from libraries import claude_prompts as cp
from libraries import neo4j_lib as nl
from pydantic import BaseModel, Field, ValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyse_advert(
    chat_engine: Any, advert: str, prompt_name: str
) -> nl.AnalysisResponse:
    """
    Analyze an advertisement using a chat engine and a specific prompt.

    Args:
        chat_engine: The chat engine to use for analysis.
        advert: The advertisement text to analyze.
        prompt_name: The name of the prompt to use.

    Returns:
        An AnalysisResponse object containing the analysis results, or a default AnalysisResponse if analysis fails.
    """
    if not chat_engine:
        logger.error("Chat engine is not initialized")
        return nl.AnalysisResponse(
            result="error",
            evidence=[],
            explanation="Chat engine not initialized",
            confidence=0.0,
        )

    try:
        # Construct the prompt
        prompt = cp.CLAUDE_PROMPTS.get(prompt_name) + cp.ANALYSIS_STR
        if not prompt:
            raise ValueError(f"Invalid prompt name: {prompt_name}")

        # Get response from chat engine
        response = chat_engine.chat(prompt)
        logger.info(f"Response to {prompt_name}: {response.response}")

        # Directly parse the JSON string
        json_str = response.response.strip()
        parsed_response = json.loads(json_str)

        # Create an AnalysisResponse instance from the parsed JSON
        analysis_response = nl.AnalysisResponse(**parsed_response)

        # Return the AnalysisResponse object
        return analysis_response

    except (json.JSONDecodeError, ValueError, ValidationError) as e:
        logger.error(f"Error processing advert, prompt {prompt_name}: {str(e)}")
        return nl.AnalysisResponse(
            result="error",
            evidence=[],
            explanation=str(e),
            confidence=0.0,
        )
