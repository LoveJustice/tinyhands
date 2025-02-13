#!/usr/bin/env python3
"""
Module for interacting with Neo4j.
"""

import os
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union

from neo4j import GraphDatabase
from pydantic import BaseModel, Field, ValidationError

# ------------------------------------------------------------------------------
# Logging Setup
# ------------------------------------------------------------------------------

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "neo4j_lib.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Pydantic Model for Analysis Response
# ------------------------------------------------------------------------------
class AnalysisResponse(BaseModel):
    result: str
    evidence: List[str] = Field(default_factory=list)
    explanation: str
    confidence: float


# ------------------------------------------------------------------------------
# Neo4j Configuration
# ------------------------------------------------------------------------------
neo4j_config = {
    "username": os.environ.get("NEO4J_USER"),
    "password": os.environ.get("NEO4J_PWD"),
    "uri": "bolt://localhost:7689",
}


# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------
def parse_analysis(
    analysis: Union[AnalysisResponse, Dict[str, Any]]
) -> Optional[AnalysisResponse]:
    """
    Ensure the analysis data is an instance of AnalysisResponse.

    Args:
        analysis: An AnalysisResponse or a dict with the required fields.

    Returns:
        An instance of AnalysisResponse if valid, otherwise None.
    """
    if isinstance(analysis, dict):
        try:
            return AnalysisResponse(**analysis)
        except ValidationError as e:
            logger.error("Validation error while parsing analysis dict: %s", e)
            return None
    elif isinstance(analysis, AnalysisResponse):
        return analysis
    else:
        logger.error(
            "Invalid type for analysis. Expected dict or AnalysisResponse, got %s",
            type(analysis),
        )
        return None


# ------------------------------------------------------------------------------
# Write Functions
# ------------------------------------------------------------------------------
def write_audit_to_neo4j(
    IDn: int, prompt_name: str, analysis: Union[AnalysisResponse, Dict[str, Any]]
) -> None:
    """
    Write audit results to Neo4j with a timestamp.

    Args:
        IDn: The Neo4j node ID of the posting.
        prompt_name: The prompt used for analysis.
        analysis: The analysis data (either as an AnalysisResponse or dict).
    """
    parsed_analysis = parse_analysis(analysis)
    if not parsed_analysis:
        logger.error("Invalid analysis data. Aborting write_audit_to_neo4j.")
        return

    current_time = datetime.utcnow()
    parameters = {
        "IDn": IDn,
        "prompt_name": prompt_name,
        "result": parsed_analysis.result,
        "evidence": parsed_analysis.evidence,
        "explanation": parsed_analysis.explanation,
        "confidence": parsed_analysis.confidence,
        "timestamp": current_time.isoformat(),
    }

    query = """
    MATCH (posting:Posting)-[:HAS_ANALYSIS {type: $prompt_name}]->(analysis:Analysis)
    WHERE ID(posting) = $IDn
    WITH analysis, posting
    MERGE (audit:Audit {
        result: $result,
        evidence: $evidence,
        explanation: $explanation,
        confidence: $confidence,
        timestamp: datetime($timestamp),
        posting_id: $IDn
    })
    MERGE (analysis)-[:HAS_AUDIT {type: $prompt_name}]->(audit)
    """

    logger.info("Writing audit to Neo4j with parameters: %s", parameters)
    try:
        execute_neo4j_query(query, parameters, write=True)
        logger.info("Audit successfully written to Neo4j.")
    except Exception as e:
        logger.error("Error writing audit to Neo4j: %s", e)


def write_analysis_to_neo4j(
    IDn: int, prompt_name: str, analysis: Union[AnalysisResponse, Dict[str, Any]]
) -> None:
    """
    Write analysis results to Neo4j.

    Args:
        IDn: The Neo4j node ID of the posting.
        prompt_name: The prompt used for analysis.
        analysis: The analysis data (either as an AnalysisResponse or dict).
    """
    parsed_analysis = parse_analysis(analysis)
    if not parsed_analysis:
        logger.error("Invalid analysis data. Aborting write_analysis_to_neo4j.")
        return

    parameters = {
        "IDn": IDn,
        "prompt_name": prompt_name,
        "result": parsed_analysis.result,
        "evidence": parsed_analysis.evidence,
        "explanation": parsed_analysis.explanation,
        "confidence": parsed_analysis.confidence,
    }

    query = """
    MATCH (posting:Posting)
    WHERE ID(posting) = $IDn
    WITH posting
    MERGE (an:Analysis {
        result: $result,
        evidence: $evidence,
        explanation: $explanation,
        confidence: $confidence
    })
    MERGE (posting)-[:HAS_ANALYSIS {type: $prompt_name}]->(an)
    """

    logger.info("Writing analysis to Neo4j with parameters: %s", parameters)
    try:
        execute_neo4j_query(query, parameters, write=True)
    except Exception as e:
        logger.error("Error writing analysis to Neo4j: %s", e)


# ------------------------------------------------------------------------------
# Read Functions
# ------------------------------------------------------------------------------
def get_neo4j_advert(IDn: int) -> Optional[str]:
    """
    Retrieve the advert text from a Posting node.

    Args:
        IDn: The Neo4j node ID of the posting.

    Returns:
        The advert text if found; otherwise, None.
    """
    query = "MATCH (n:Posting) WHERE ID(n) = $IDn RETURN n.text AS advert"
    parameters = {"IDn": IDn}
    result = execute_neo4j_query(query, parameters, write=False)
    return result[0]["advert"] if result else None


def get_neo4j_advert_analysis(
    posting_id: int, analysis_type: str
) -> Optional[Tuple[str, str]]:
    """
    Retrieve the advert text and its corresponding analysis result.

    Args:
        posting_id: The Neo4j node ID of the posting.
        analysis_type: The type of analysis.

    Returns:
        A tuple of (advert text, analysis result) if found; otherwise, None.
    """
    query = """
    MATCH (n:Posting)-[:HAS_ANALYSIS {type: $analysis_type}]-(analysis:Analysis)
    WHERE ID(n) = $posting_id
    RETURN n.text AS advert, analysis.result AS result
    """
    parameters = {"posting_id": posting_id, "analysis_type": analysis_type}
    try:
        result = execute_neo4j_query(query, parameters, write=False)
        if result:
            advert = result[0].get("advert")
            analysis_result = result[0].get("result")
            if advert is not None and analysis_result is not None:
                return advert, analysis_result
    except Exception as e:
        logger.error("Error retrieving advert analysis: %s", e)
    return None


def get_adverts() -> pd.DataFrame:
    """
    Retrieve all adverts with non-empty text.

    Returns:
        A pandas DataFrame containing advert data.
    """
    query = """
    MATCH (n:Posting)
    WHERE (n.text IS NOT NULL) AND NOT (n.text = "")
    RETURN ID(n) AS IDn, n.post_id, n.post_url AS post_url, n.text AS advert
    """
    postings = execute_neo4j_query(query, {}, write=False)
    return pd.DataFrame(postings) if postings is not None else pd.DataFrame()


def get_all_comments() -> List[Dict[str, Any]]:
    """
    Retrieve all comments from Neo4j.

    Returns:
        A list of dictionaries containing comment data.
    """
    query = """
    MATCH (profile:Profile)-[:MADE_COMMENT]->(comment:Comment)-[:HAS_COMMENT]-(posting:Posting)
    RETURN profile.name AS profile_name, profile.url AS profile_url,
           comment.comment_id AS comment_id, comment.url AS comment_url,
           comment.comment AS comment, posting.post_id AS post_id,
           posting.post_url AS post_url;
    """
    try:
        result = execute_neo4j_query(query, {}, write=False)
        return result if result is not None else []
    except Exception as e:
        logger.exception("Error fetching comments from Neo4j: %s", e)
        return []


# ------------------------------------------------------------------------------
# Neo4j Connection Class
# ------------------------------------------------------------------------------
class Neo4jConnection:
    def __init__(self, uri: str, user: str, pwd: str) -> None:
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        self.__connect()

    def __connect(self) -> None:
        """Establish the connection to the Neo4j database."""
        try:
            self.__driver = GraphDatabase.driver(
                self.__uri,
                auth=(self.__user, self.__pwd),
                max_connection_lifetime=30 * 60,
                max_connection_pool_size=10,
            )
        except Exception as e:
            logger.error("Failed to create the Neo4j driver: %s", e)
            raise

    def __enter__(self) -> "Neo4jConnection":
        if self.__driver is None:
            self.__connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self.__driver is not None:
            self.__driver.close()

    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        return_df: bool = False,
        write: bool = False,
    ) -> Any:
        """
        Execute a Cypher query.

        Args:
            query: The Cypher query string.
            parameters: A dictionary of parameters.
            return_df: Whether to return the result as a pandas DataFrame.
            write: Whether to run the query in a write transaction.

        Returns:
            The query result, either as a DataFrame (if return_df is True) or a list of dictionaries.
        """
        if self.__driver is None:
            raise Exception("Driver not connected.")
        with self.__driver.session() as session:
            try:
                if write:
                    result = session.write_transaction(
                        lambda tx: tx.run(query, parameters).data()
                    )
                else:
                    result = session.read_transaction(
                        lambda tx: tx.run(query, parameters).data()
                    )
                if return_df and result is not None:
                    return pd.DataFrame(result)
                return result
            except Exception as e:
                logger.error("Query failed: %s", e)
                return None

    def reconnect(self) -> None:
        """Reconnect to the Neo4j database."""
        self.close()
        self.__connect()


# ------------------------------------------------------------------------------
# Query Execution Helper
# ------------------------------------------------------------------------------
def execute_neo4j_query(
    query: str, parameters: Optional[Dict[str, Any]] = None, write: bool = False
) -> Any:
    """
    Execute a Neo4j query using a context-managed connection.

    Args:
        query: The Cypher query string.
        parameters: A dictionary of parameters.
        write: Whether this is a write query.

    Returns:
        The result of the query.
    """
    with Neo4jConnection(
        neo4j_config["uri"], neo4j_config["username"], neo4j_config["password"]
    ) as conn:
        return conn.execute_query(query, parameters, return_df=False, write=write)


# ------------------------------------------------------------------------------
# Placeholders for Additional Functions
# ------------------------------------------------------------------------------
def create_user_comment_parameters(
    user_comment: Dict[str, Any], post_id: Any, group_name: str, advert_text: str
) -> Dict[str, Any]:
    raise NotImplementedError("create_user_comment_parameters is not implemented yet.")


def create_poster_parameters(
    poster: Dict[str, Any], post_id: Any, group_name: str, advert_text: str
) -> Dict[str, Any]:
    raise NotImplementedError("create_poster_parameters is not implemented yet.")


def construct_query_based_on_parameters(parameters: Dict[str, Any]) -> str:
    raise NotImplementedError(
        "construct_query_based_on_parameters is not implemented yet."
    )


def process_users_comments(
    users_and_comments: List[Dict[str, Any]],
    post_id: Any,
    group_name: str,
    advert_text: str,
    config: Dict[str, Any],
) -> None:
    for user_comment in users_and_comments:
        params = create_user_comment_parameters(
            user_comment, post_id, group_name, advert_text
        )
        execute_neo4j_query(params, write=True)


def process_posters(
    posters: List[Dict[str, Any]],
    post_id: Any,
    group_name: str,
    advert_text: str,
    config: Dict[str, Any],
) -> None:
    for poster in posters:
        params = create_poster_parameters(poster, post_id, group_name, advert_text)
        execute_neo4j_query(params, write=True)


# ------------------------------------------------------------------------------
# Additional Write/Upload Functions
# ------------------------------------------------------------------------------
def post_to_neo4j(post: Dict[str, Any]) -> Any:
    parameters = {
        "post_id": post["post_id"],
        "group_id": post["group_id"],
        "group_url": f"https://www.facebook.com/groups/{post['group_id']}",
        "post_url": f"https://www.facebook.com/groups/{post['group_id']}/posts/{post['post_id']}",
        "collected_date": datetime.now().isoformat(),
    }
    query = """
    MERGE (group:Group {group_id: $group_id, url: $group_url})
    MERGE (posting:Posting {post_id: $post_id})
    ON CREATE SET posting.post_url = $post_url,
                  posting.collected_date = datetime($collected_date),
                  posting.is_new = true
    ON MATCH SET posting.is_new = false
    MERGE (group)-[:HAS_POSTING]->(posting)
    RETURN posting.is_new as is_new
    """
    result = execute_neo4j_query(query, parameters, write=True)
    return result[0]["is_new"] if result else None


def all_new_adverts_urls(group_url: Optional[str] = None) -> Any:
    parameters = {}
    if group_url:
        parameters["group_url"] = group_url
        query = """
        MATCH (group:Group {url: $group_url})-[:HAS_POSTING]->(posting:Posting)
        WHERE posting.text IS NULL
        RETURN posting.post_id AS post_id, posting.post_url AS post_url;
        """
    else:
        query = """
        MATCH (posting:Posting)
        WHERE posting.text IS NULL
        RETURN posting.post_id AS post_id, posting.post_url AS post_url LIMIT 22;
        """
    return execute_neo4j_query(query, parameters, write=False)


def upload_comment_to_neo4j(comment: Dict[str, Any]) -> Any:
    parameters = {
        "full_name": comment["name"],
        "name": comment["name"].lower().strip(),
        "post_id": comment["post_id"],
        "group_id": comment["group_id"],
        "group_name": comment["group_name"],
        "user_id": comment["user_id"],
        "group_url": f"https://www.facebook.com/groups/{comment['group_id']}",
        "user_url": f"https://www.facebook.com/{comment['user_id']}",
        "post_url": f"https://www.facebook.com/groups/{comment['group_id']}/posts/{comment['post_id']}",
        "comment_url": f"https://www.facebook.com/groups/{comment['group_id']}/posts/{comment['post_id']}/?comment_id={comment['comment_id']}",
        "comment_text": comment["text"],
        "comment_id": comment["comment_id"],
    }
    query = """
    MERGE (group:Group {group_id: $group_id, url: $group_url})
    MERGE (profile:Profile {name: $full_name, url: $user_url})
    MERGE (name:Name {full_name: $full_name, name: $name})
    MERGE (posting:Posting {post_id: $post_id, post_url: $post_url})
    MERGE (comment:Comment {comment_id: $comment_id, comment: $comment_text, url: $comment_url})
    MERGE (profile)-[:HAS_PROFILE_NAME]->(name)
    MERGE (group)-[:HAS_POSTING]->(posting)
    MERGE (posting)-[:HAS_COMMENT]->(comment)
    MERGE (profile)-[:MADE_COMMENT]->(comment)
    SET group.name = $group_name
    """
    return execute_neo4j_query(query, parameters, write=True)


def upload_post_to_neo4j(poster: Dict[str, Any]) -> Any:
    parameters = {
        "full_name": poster["name"],
        "name": poster["name"].lower().strip(),
        "group_id": poster["group_id"],
        "group_name": poster["group_name"],
        "user_id": poster["user_id"],
        "post_id": poster["post_id"],
        "group_url": f"https://www.facebook.com/groups/{poster['group_id']}",
        "user_url": f"https://www.facebook.com/{poster['user_id']}",
        "post_url": f"https://www.facebook.com/groups/{poster['group_id']}/posts/{poster['post_id']}",
    }
    query = """
    MERGE (group:Group {name: $group_name, group_id: $group_id, url: $group_url})
    MERGE (profile:Profile {name: $full_name, url: $user_url})
    MERGE (name:Name {full_name: $full_name, name: $name})
    MERGE (posting:Posting {post_id: $post_id, post_url: $post_url})
    MERGE (profile)-[:HAS_PROFILE_NAME]->(name)
    MERGE (profile)-[:POSTED]->(posting)
    MERGE (group)-[:HAS_POSTING]->(posting)
    """
    return execute_neo4j_query(query, parameters, write=True)


def all_group_adverts(group_url: Optional[str] = None) -> Any:
    parameters = {}
    if group_url:
        parameters["group_url"] = group_url
        query = """
        MATCH (group:Group {url: $group_url})-[:HAS_POSTING]->(posting:Posting)
        RETURN ID(posting) AS IDn, posting.text AS advert, posting.post_id AS post_id, posting.post_url AS post_url
        ORDER BY IDn DESC;
        """
    else:
        query = """
        MATCH (posting:Posting)
        RETURN ID(posting) AS IDn, posting.post_id AS post_id, posting.post_url AS post_url;
        """
    return execute_neo4j_query(query, parameters, write=False)
