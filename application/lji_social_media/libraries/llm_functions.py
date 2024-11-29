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


def analyse_advert(chat_engine: Any, prompt_name: str) -> nl.AnalysisResponse:
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

    # Retrieve prompt and validate its existence
    prompt = cp.CLAUDE_PROMPTS.get(prompt_name)
    if not prompt:
        logger.error(f"Invalid or missing prompt name: {prompt_name}")
        return nl.AnalysisResponse(
            result="error",
            evidence=[],
            explanation=f"Invalid prompt name: {prompt_name}",
            confidence=0.0,
        )

    # Combine prompt with analysis string
    prompt += cp.ANALYSIS_STR

    try:
        # Send prompt to chat engine
        response = chat_engine.chat(prompt)
        logger.info(f"Response to {prompt_name}: {response.response}")

        # Parse JSON response
        json_str = response.response.strip()
        parsed_response = json.loads(json_str)

        # Instantiate AnalysisResponse from parsed JSON
        analysis_response = nl.AnalysisResponse(**parsed_response)
        logger.info(f"Response ****analysis_response**** {analysis_response}")
        return analysis_response

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error for prompt {prompt_name}: {e}")
        return nl.AnalysisResponse(
            result="error",
            evidence=[],
            explanation="Invalid JSON format in response",
            confidence=0.0,
        )

    except ValidationError as e:
        logger.error(f"Validation error for prompt {prompt_name}: {e}")
        return nl.AnalysisResponse(
            result="error",
            evidence=[],
            explanation="Validation error in response schema",
            confidence=0.0,
        )

    except Exception as e:
        logger.error(f"Unexpected error for prompt {prompt_name}: {e}")
        return nl.AnalysisResponse(
            result="error",
            evidence=[],
            explanation=str(e),
            confidence=0.0,
        )


def audit_analysis(chat_engine: Any, prompt_name: str) -> nl.AnalysisResponse:
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

    # Retrieve prompt and validate its existence
    prompt = cp.CLAUDE_PROMPTS.get(prompt_name)
    prompt = """Is the following """
    if not prompt:
        logger.error(f"Invalid or missing prompt name: {prompt_name}")
        return nl.AnalysisResponse(
            result="error",
            evidence=[],
            explanation=f"Invalid prompt name: {prompt_name}",
            confidence=0.0,
        )

    # Combine prompt with analysis string
    prompt += cp.ANALYSIS_STR

    try:
        # Send prompt to chat engine
        response = chat_engine.chat(prompt)
        logger.info(f"Response to {prompt_name}: {response.response}")

        # Parse JSON response
        json_str = response.response.strip()
        parsed_response = json.loads(json_str)

        # Instantiate AnalysisResponse from parsed JSON
        analysis_response = nl.AnalysisResponse(**parsed_response)
        logger.info(f"Response ****analysis_response**** {analysis_response}")
        return analysis_response

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error for prompt {prompt_name}: {e}")
        return nl.AnalysisResponse(
            result="error",
            evidence=[],
            explanation="Invalid JSON format in response",
            confidence=0.0,
        )

    except ValidationError as e:
        logger.error(f"Validation error for prompt {prompt_name}: {e}")
        return nl.AnalysisResponse(
            result="error",
            evidence=[],
            explanation="Validation error in response schema",
            confidence=0.0,
        )

    except Exception as e:
        logger.error(f"Unexpected error for prompt {prompt_name}: {e}")
        return nl.AnalysisResponse(
            result="error",
            evidence=[],
            explanation=str(e),
            confidence=0.0,
        )
