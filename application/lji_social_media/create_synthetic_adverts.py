"""
Module for analyzing and generating synthetic job advertisements using various LLM models
and Neo4j database interactions.
"""

from typing import List, Dict, Optional, Union
import json
import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import tiktoken
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from llama_index.core.base.base_query_engine import BaseQueryEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    from libraries import neo4j_lib as nl, claude_prompts as cp
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    raise ImportError(f"Required modules not found: {e}")


@dataclass
class AdvertAnalysisConfig:
    """Configuration settings for advertisement analysis."""

    token_limit: int = 8192
    model_name: str = "o1-mini"
    temperature: float = 0
    request_timeout: float = 120.0
    output_path: Path = Path("results/synthetic_adverts.csv")
    sample_size: int = 10


class AdvertAnalyzer:
    """Main class for analyzing and generating synthetic advertisements."""

    ANALYSIS_FORMAT = (
        "Return your analysis STRICTLY and exclusively in the following JSON format: "
        '{"new_advert": "advert", "changes": ["change 1", "change 2", ...] or []}. '
        "Please do not use ANY other embedded explanation and please do not use backticks."
    )

    SYSTEM_PROMPT = (
        "As a career forensic analyst you have deep insight into crime and criminal activity "
        "especially human trafficking. Your express goal is to investigate online recruitment "
        "advert and extract pertinent factual detail."
    )

    def __init__(self, config: AdvertAnalysisConfig):
        """
        Initialize the AdvertAnalyzer with configuration settings.

        Args:
            config: Configuration settings for the analyzer
        """
        self.config = config
        self.llm = OpenAI(
            temperature=config.temperature,
            model=config.model_name,
            request_timeout=config.request_timeout,
        )
        self.memory = ChatMemoryBuffer.from_defaults(token_limit=config.token_limit)

    def _get_adverts_from_db(self, prompt_name: str) -> pd.DataFrame:
        """
        Retrieve advertisements from the database.

        Args:
            prompt_name: Name of the prompt to use for filtering

        Returns:
            DataFrame containing the advertisements
        """
        query = """
        MATCH (g:Group)-[:HAS_POSTING]-(n:RecruitmentAdvert)-[:HAS_ANALYSIS {type: $prompt_name}]-(:Analysis {result:'no'})
        WHERE g.country_id = 1
          AND n.text IS NOT NULL
          AND n.text <> ""
        RETURN ID(n) AS IDn, n.post_id AS post_id, n.text AS advert
        """
        try:
            df = pd.DataFrame(
                nl.execute_neo4j_query(query, {"prompt_name": prompt_name})
            )
            return df.sample(self.config.sample_size) if not df.empty else df
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return pd.DataFrame()

    def create_chat_engine(
        self, documents: List[Document]
    ) -> Optional[BaseQueryEngine]:
        """
        Create a chat engine from the provided documents.

        Args:
            documents: List of Document objects to create the index from

        Returns:
            Chat engine instance or None if creation fails
        """
        if not documents:
            logger.error("No documents provided for chat engine creation")
            return None

        index = VectorStoreIndex.from_documents(documents)
        return index.as_chat_engine(
            chat_mode="context",
            llm=self.llm,
            memory=self.memory,
            system_prompt=self.SYSTEM_PROMPT,
        )

    def analyze_adverts(self, prompt_name: str) -> List[Dict[str, Union[str, int]]]:
        """
        Analyze advertisements based on the given prompt type.

        Args:
            prompt_name: Name of the prompt to use for analysis

        Returns:
            List of analysis results for each advertisement
        """
        advert_sample = self._get_adverts_from_db(prompt_name)
        if advert_sample.empty:
            logger.warning(f"No advertisements found for prompt: {prompt_name}")
            return []

        documents = [
            Document(text=row["advert"]) for _, row in advert_sample.iterrows()
        ]
        chat_engine = self.create_chat_engine(documents)

        if not chat_engine:
            return []

        results = []
        for _, row in advert_sample.iterrows():
            try:
                prompt = self._construct_prompt(row["advert"], prompt_name)
                response = chat_engine.chat(prompt + self.ANALYSIS_FORMAT)
                parsed_response = json.loads(response.response)

                results.append(
                    {
                        "synthetic_advert": parsed_response["new_advert"],
                        "advert": row["advert"],
                        "IDn": row["IDn"],
                        "prompt_type": prompt_name,
                    }
                )
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse response for advert {row['IDn']}: {e}")
            except Exception as e:
                logger.error(f"Error processing advert {row['IDn']}: {e}")

        return results

    def _construct_prompt(self, advert: str, prompt_name: str) -> str:
        """
        Construct the analysis prompt for a given advertisement.

        Args:
            advert: Advertisement text to analyze
            prompt_name: Name of the prompt to use

        Returns:
            Constructed prompt string
        """
        return (
            f"Assistant, carefully consider this recruitment advert:{advert}. "
            f"I want you to change any or every detail of this advert so that the following prompt will be CLEARLY and unambiguously TRUE: "
            f"'{cp.CLAUDE_PROMPTS[prompt_name]}'. "
            "Please mimic the grammar, style and tone of "
            "the provided text."
        )


def save_results_to_csv(results: List[List[Dict]], output_path: Path) -> None:
    """
    Save analysis results to a CSV file.

    Args:
        results: List of analysis results for each prompt type
        output_path: Path where the CSV file should be saved
    """
    if not results:
        logger.warning("No results to save")
        return

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        flattened_results = [item for sublist in results for item in sublist]
        df = pd.DataFrame(flattened_results)
        df.to_csv(output_path, index=False)
        logger.info(f"Results successfully saved to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save results to CSV: {e}")
        raise


def main():
    """Main function to run the advertisement analysis."""
    sparse_flags = [
        "gender_specific_prompt",
        "illegal_activities_prompt",
        "no_education_skilled_prompt",
        "overseas_prompt",
        "recruit_students_prompt",
        "requires_references",
    ]
    sparse_flags = [
        "dance_bar_prompt",
        "drop_off_at_secure_location_prompt",
        "massage_or_spa_prompt",
        "no_education_skilled_prompt",
        "soccer_trial_prompt",
    ]
    config = AdvertAnalysisConfig()
    analyzer = AdvertAnalyzer(config)

    logger.info("Starting advertisement analysis")
    all_results = []

    for prompt_name in sparse_flags:
        logger.info(f"Processing prompt: {prompt_name}")
        results = analyzer.analyze_adverts(prompt_name)
        all_results.append(results)

    save_results_to_csv(all_results, config.output_path)
    logger.info("Analysis complete")

    return all_results


if __name__ == "__main__":
    main()
