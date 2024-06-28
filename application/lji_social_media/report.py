# Willem Heinrich Pretorius
# suspect = [466423, 466098, 626, 466737]

# Errol Air-roll Tjipuka
# suspect = [6708, 6285, 464161, 465333]


import os
import pandas as pd

# from py2neo import Graph
from neomodel import db, config, StructuredNode, RelationshipTo, RelationshipFrom
from neomodel.integration.pandas import to_dataframe

# Environment variable fetching and error handling
neo4j_url = os.environ.get("NEO4J_URL")
neo4j_usr = os.environ.get("NEO4J_USR", "neo4j")  # Default to 'neo4j' if not set
neo4j_pwd = os.environ.get("NEO4J_PWD")
config.DATABASE_URL = "bolt://" + neo4j_usr + ":" + neo4j_pwd + "@localhost:7687"
if not all([neo4j_url, neo4j_usr, neo4j_pwd]):
    raise EnvironmentError("Required NEO4J environment variables are not set.")


query = """MATCH path = (startProfile:Profile)-[*..3]-(validname:ValidName)-[]-(person1:Person)-[]-(irf:IRF)
WHERE
    ID(startProfile) IN [6708, 6285, 464161, 465333] AND
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND size(nodes(path)) = size(apoc.coll.toSet(nodes(path)))
WITH startProfile, ID(startProfile) AS start_profile_id, path, person1, irf, [node in nodes(path) WHERE node:Profile | node.name] AS profile_names, [node in nodes(path) WHERE node:Profile | node.url] AS profile_urls
UNWIND [node in nodes(path) WHERE node:Person] AS personNode
OPTIONAL MATCH (personNode)-[:HAS_NAME]->(person_name:Name)-[:HAS_PROFILE_NAME]-(profile1:Profile)
OPTIONAL MATCH (personNode)-[:HAS_ROLE]->(role:Role)
OPTIONAL MATCH (personNode)-[:HAS_PHOTO]->(photo:Photo)
OPTIONAL MATCH (irf)-[:AT_BORDER_STATION]->(border_station:BorderStation)
OPTIONAL MATCH (border_station)-[:IN_COUNTRY]->(country:Country)
OPTIONAL MATCH (irf)<-[:ON_IRF]-(person:Person)
OPTIONAL MATCH (person)-[:HAS_NAME]-(other_person_name:Name)
OPTIONAL MATCH (person)-[:HAS_MASTER_PERSON_ID]->(master_person:MasterPerson)
CALL apoc.cypher.doIt(
  "MATCH (n:Name {name: $person_name})-[:HAS_NAME]-(p:Person)-[:HAS_MASTER_PERSON_ID]->(mp:MasterPerson) RETURN COUNT(DISTINCT mp.master_person_id) AS count",
  {person_name: person_name.name}
) YIELD value
WHERE value.count <=10
WITH startProfile, country, border_station, irf, person, other_person_name, person_name, master_person, profile1, profile_names, profile_urls, value
RETURN
    startProfile.name AS start_profile,
    country.name AS country,
    border_station.name AS border_station,
    irf.irf_number AS irf_number,
    COLLECT(DISTINCT other_person_name.name) AS searchlight_person_names,
    COLLECT(DISTINCT master_person.master_person_id) AS master_person_ids,
    person_name.name AS person1_name,
    profile1.url AS profile1_url,
    profile_names,
    profile_urls,
    size(profile_names)-1 AS degree_of_separation,
    value.count as name_count

LIMIT 5000;

"""
detail = to_dataframe(db.cypher_query(query))
detail.to_csv("results/errol_tjipuka.csv", index=False)
# Export DataFrame to CSV


irf_numbers = detail["irf_number"].unique()
irf_numbers.sort()
df["profile_names"]
unique_names = pd.Series(
    [name for sublist in df["profile_names"] for name in sublist]
).unique()
print(unique_names)
# Explode the 'profile_names' column to separate rows for each name
# Then count the occurrences of each name
frequency_table = df["profile_names"].explode().value_counts()
print(frequency_table)
