from neo4j import GraphDatabase
import pandas as pd
import os

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
        try:
            self.__driver = GraphDatabase.driver(
                self.__uri, auth=(self.__user, self.__pwd)
            )
        except Exception as e:
            print("Failed to create the driver:", e)

    def __enter__(self):
        self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__driver is not None:
            self.__driver.close()

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def execute_query(self, query, parameters=None, return_df=False):
        if self.__driver is not None:
            with self.__driver.session(
                database="neo4j"
            ) as session:  # Specify database if needed
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
                    print("Query failed:", e)
                    return None


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
