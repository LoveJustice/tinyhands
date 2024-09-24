from neo4j import GraphDatabase
import pandas as pd
import os
from datetime import datetime

neo4j_config = {
    "username": os.environ.get("NEO4J_USER"),
    "password": os.environ.get("NEO4J_PWD"),
    "uri": "bolt://localhost:7687",
}


def get_adverts():
    query = """MATCH (n:Posting) WHERE (n.text IS NOT NULL) AND NOT (n.text = "") RETURN ID(n) AS IDn, n.post_id, n.post_url AS post_url, n.text AS advert"""
    postings = execute_neo4j_query(query, {})
    return pd.DataFrame(postings)


class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        self.__connect()

    def __connect(self):
        """Establishes the connection to the Neo4j database."""
        try:
            self.__driver = GraphDatabase.driver(
                self.__uri,
                auth=(self.__user, self.__pwd),
                max_connection_lifetime=30 * 60,
                max_connection_pool_size=10,
            )
            print("Neo4j connection established.")
        except Exception as e:
            print(f"Failed to create the driver: {e}")
            raise e

    def __enter__(self):
        """For use with context manager (with statement)."""
        if self.__driver is None:
            self.__connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Closes the connection when exiting the context manager."""
        self.close()

    def close(self):
        """Closes the Neo4j driver connection."""
        if self.__driver is not None:
            self.__driver.close()
            print("Neo4j connection closed.")

    def execute_query(self, query, parameters=None, return_df=False):
        """Executes a Neo4j query.

        Args:
            query (str): The Cypher query to run.
            parameters (dict): Parameters to pass into the query.
            return_df (bool): Whether to return the result as a pandas DataFrame.

        Returns:
            DataFrame or List of dict: The query result, either as a pandas DataFrame or a list of dictionaries.
        """
        if self.__driver is not None:
            with self.__driver.session() as session:
                try:
                    if return_df:
                        result = session.run(query, parameters)
                        return pd.DataFrame(
                            [record.values() for record in result],
                            columns=result.keys(),
                        )
                    else:
                        result = session.write_transaction(
                            lambda tx: tx.run(query, parameters).data()
                        )
                        return result
                except Exception as e:
                    print(f"Query failed: {e}")
                    return None

    def run_read_query(self, query, parameters=None):
        """Executes a read-only transaction (uses `read_transaction`)."""
        if self.__driver is not None:
            with self.__driver.session() as session:
                try:
                    result = session.read_transaction(
                        lambda tx: tx.run(query, parameters).data()
                    )
                    return result
                except Exception as e:
                    print(f"Read query failed: {e}")
                    return None

    def reconnect(self):
        """Reconnects to Neo4j if the connection is lost."""
        self.close()
        self.__connect()


def get_all_comments():
    parameters = {}
    query = f"""MATCH (profile:Profile)-[:MADE_COMMENT]-(comment:Comment)-[:HAS_COMMENT]-(posting:Posting)
        RETURN profile.name  AS profile_name, profile.url AS profile_url, comment.comment_id AS comment_id, comment.url AS comment_url, comment.comment as comment, posting.post_id AS post_id, posting.post_url AS post_url;
        """
    # st.write(parameters)
    result = execute_neo4j_query(query, parameters)
    return result


def process_users_comments(
    users_and_comments, post_id, group_name, advert_text, neo4j_config
):
    for user_comment in users_and_comments:
        parameters = create_user_comment_parameters(
            user_comment, post_id, group_name, advert_text
        )
        execute_neo4j_query(parameters, neo4j_config)


def process_posters(posters, post_id, group_name, advert_text, neo4j_config):
    for poster in posters:
        parameters = create_poster_parameters(poster, post_id, group_name, advert_text)
        execute_neo4j_query(parameters, neo4j_config)


def create_user_comment_parameters(user_comment, post_id, group_name, advert_text):
    # Create parameters for users and comments
    # Returns a dictionary of parameters
    ...


def create_poster_parameters(poster, post_id, group_name, advert_text):
    # Create parameters for posters
    # Returns a dictionary of parameters
    ...


def execute_neo4j_query(query, parameters):
    with Neo4jConnection(
        neo4j_config["uri"], neo4j_config["username"], neo4j_config["password"]
    ) as conn:
        return conn.execute_query(query, parameters)


def construct_query_based_on_parameters(parameters):
    # Depending on the parameters, construct and return the appropriate Cypher query
    ...


def post_to_neo4j(post):
    parameters = {
        "post_id": post["post_id"],
        "group_id": post["group_id"],
        "group_url": f"https://www.facebook.com/groups/{post['group_id']}",
        "post_url": f"https://www.facebook.com/groups/{post['group_id']}/posts/{post['post_id']}",
        "collected_date": datetime.now().isoformat(),  # Current date and time in ISO format
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
    result = execute_neo4j_query(query, parameters)
    return result[0]["is_new"]


def all_new_adverts_urls(group_url=None):
    parameters = {}
    if group_url:
        parameters["group_url"] = group_url
        query = f"""MATCH (group:Group {{url: $group_url}})-[:HAS_POSTING]->(posting:Posting)
        WHERE posting.text IS NULL
        RETURN posting.post_id AS post_id, posting.post_url AS post_url;
        """
    else:
        query = f"""MATCH (posting:Posting)
            WHERE posting.text IS NULL
            RETURN posting.post_id AS post_id, posting.post_url AS post_url LIMIT 22;
            """
    # st.write(parameters)
    result = execute_neo4j_query(query, parameters)
    return result


def all_group_adverts(group_url=None):
    parameters = {}
    if group_url:
        parameters["group_url"] = group_url
        query = f"""MATCH (group:Group {{url: $group_url}})-[:HAS_POSTING]->(posting:Posting)
        RETURN ID(posting) AS IDn, posting.text AS advert, posting.post_id AS post_id, posting.post_url AS post_url
        ORDER BY IDn DESC;
        """
    else:
        query = f"""MATCH (posting:Posting)
            RETURN ID(posting) AS IDn, posting.post_id AS post_id, posting.post_url AS post_url;
            """
    # st.write(parameters)
    result = execute_neo4j_query(query, parameters)
    return result
