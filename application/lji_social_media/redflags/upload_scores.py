import pandas as pd
from libraries.neo4j_lib import execute_neo4j_query


def count_nodes_with_monitor_score():
    count_query = "MATCH (n) WHERE n.monitor_score IS NOT NULL RETURN count(n) AS count"
    result = execute_neo4j_query(count_query, {})
    return result[0]["count"]


# Read and process the CSV file
adverts = pd.read_csv("data/adverts_round1.csv")
columns = [
    "IDn",
    "advert",
    "monitor_score",
    "monitor_rank",
    "model_score",
    "model_rank",
    "col0",
    "col1",
    "col3",
]
adverts.columns = columns

# Update nodes in Neo4j with monitor_score
for idx, row in adverts.iterrows():
    parameters = {"IDn": row["IDn"], "monitor_score": row["monitor_score"]}
    query = """
    MATCH (posting:Posting)
    WHERE ID(posting) = $IDn
    SET posting.monitor_score = $monitor_score
    RETURN posting
    """
    execute_neo4j_query(query, parameters)


# Get and print the count
node_count = count_nodes_with_monitor_score()
print(f"Number of nodes with 'monitor_score': {node_count}")
