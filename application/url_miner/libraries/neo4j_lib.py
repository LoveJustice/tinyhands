"""Neo4j database interaction library for URL management and article storage.

This module provides functionality for interacting with a Neo4j database,
specifically for managing URLs and article data. It includes functions for
checking URL presence, uploading articles, and managing article properties.
"""

import os
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
USERNAME = os.environ.get("NEO4J_USER")
if USERNAME is None:
    raise ValueError("NEO4J_USER environment variable is not set")

PASSWORD = os.environ.get("NEO4J_PWD")
if PASSWORD is None:
    raise ValueError("NEO4J_PWD environment variable is not set")

URI = "bolt://localhost:7689"


def check_url_presence(url: str) -> bool:
    """Check if a URL exists in the Neo4j database.

    Args:
        url: The URL to check for existence.

    Returns:
        bool: True if the URL exists in the database, False otherwise.
    """
    parameters = {"url": url}
    query = """MATCH (article:Article {url: $url}) RETURN article.url LIMIT 1"""
    result = execute_neo4j_query(query, parameters)
    return bool(result)


def upload_prompt_properties(
    url: str, property_name: str, property_value: Any
) -> Optional[List[Dict[str, Any]]]:
    """Upload or update properties for a specific URL in the database.

    Args:
        url: The URL of the article to update.
        property_name: The name of the property to set.
        property_value: The value to set for the property.

    Returns:
        Optional[List[Dict[str, Any]]]: The result of the database operation,
        or None if the operation fails.
    """
    parameters = {
        "url": url,
        "property_name": property_name,
        "property_value": property_value,
    }
    query = (
        """
    MATCH (a:Article {url: $url})
    FOREACH (_ IN CASE WHEN a IS NOT NULL THEN [1] ELSE [] END |
        SET a.%s = $property_value
    )
    RETURN a
    """
        % property_name
    )
    return execute_neo4j_query(query, parameters)


def upload_article(article: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """Upload an article to the Neo4j database.

    Args:
        article: Dictionary containing article data with keys for 'source',
                'author', 'title', 'description', 'url', 'urlToImage',
                'publishedAt', and 'content'.

    Returns:
        Optional[List[Dict[str, Any]]]: The result of the database operation,
        or None if the operation fails.
    """
    parameters = {
        "sourceName": article.get("source", {}).get("name"),
        "authorName": article.get("author"),
        "title": article.get("title"),
        "description": article.get("description"),
        "url": article.get("url"),
        "urlToImage": article.get("urlToImage"),
        "publishedAt": article.get("publishedAt"),
        "content": article.get("content"),
    }
    query = """
    MERGE (a:Article {url: $url})
    ON CREATE SET a += {
        sourceName: $sourceName,
        authorName: $authorName,
        title: $title,
        description: $description,
        urlToImage: $urlToImage,
        publishedAt: $publishedAt,
        content: $content
    }
    """
    return execute_neo4j_query(query, parameters)


class Neo4jConnection:
    """A context manager for Neo4j database connections.

    This class manages Neo4j database connections and provides methods
    for executing queries with proper resource cleanup.
    """

    def __init__(self, uri: str, user: str, pwd: str) -> None:
        """Initialize the Neo4j connection.

        Args:
            uri: The URI of the Neo4j database.
            user: The username for authentication.
            pwd: The password for authentication.
        """
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(
                self.__uri, auth=(self.__user, self.__pwd)
            )
        except Exception as e:
            print("Failed to create the driver:", e)

    def __enter__(self) -> "Neo4jConnection":
        """Set up the database connection when entering the context.

        Returns:
            Neo4jConnection: The current connection instance.
        """
        self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Clean up the database connection when exiting the context.

        Args:
            exc_type: The type of the exception that occurred, if any.
            exc_val: The instance of the exception that occurred, if any.
            exc_tb: The traceback of the exception that occurred, if any.
        """
        if self.__driver is not None:
            self.__driver.close()

    def close(self) -> None:
        """Close the database connection."""
        if self.__driver is not None:
            self.__driver.close()

    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        return_df: bool = False,
    ) -> Optional[Union[List[Dict[str, Any]], pd.DataFrame]]:
        """Execute a query on the Neo4j database.

        Args:
            query: The Cypher query to execute.
            parameters: Optional parameters for the query.
            return_df: If True, returns results as a pandas DataFrame.

        Returns:
            Optional[Union[List[Dict[str, Any]], pd.DataFrame]]: Query results
            in the requested format, or None if the query fails.
        """
        if self.__driver is None:
            return None

        with self.__driver.session(database="neo4j") as session:
            try:
                if return_df:
                    result = session.run(query, parameters)
                    return pd.DataFrame(
                        [record.values() for record in result],
                        columns=result.keys(),
                    )

                result = session.write_transaction(
                    lambda tx: tx.run(query, parameters).data()
                )
                return result
            except Exception as e:
                print("Query failed:", e)
                return None


def execute_neo4j_query(
    neo4j_query: str, parameters: Optional[Dict[str, Any]] = None
) -> Optional[List[Dict[str, Any]]]:
    """Execute a query using a temporary Neo4j connection.

    Args:
        neo4j_query: The Cypher query to execute.
        parameters: Optional parameters for the query.

    Returns:
        Optional[List[Dict[str, Any]]]: The query results, or None if the query fails.
    """
    if not isinstance(USERNAME, str):
        raise ValueError("USERNAME must be a string")
    if not isinstance(PASSWORD, str):
        raise ValueError("PASSWORD must be a string")

    with Neo4jConnection(URI, USERNAME, PASSWORD) as conn:
        return conn.execute_query(neo4j_query, parameters)
