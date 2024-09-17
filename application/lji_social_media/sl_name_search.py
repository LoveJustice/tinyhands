from libraries.neo4j_lib import execute_neo4j_query

from fuzzywuzzy import process


import pandas as pd
import numpy as np
from rapidfuzz import process, fuzz
from tqdm.auto import tqdm
from functools import partial
from typing import List, Tuple, Optional


def get_POI(start_date, end_date, country):
    pass


# Call the function to start the import process


def is_valid_name(name):
    words = name.lower().split()
    return len(words) > 1 and len(set(words)) > 1


def match_names_rapidfuzz(name, candidates, score_cutoff=80):
    name = name.lower().strip()
    best_match = process.extractOne(
        name, candidates, scorer=fuzz.WRatio, score_cutoff=score_cutoff
    )
    return best_match[0] if best_match else None


def remove_repetitive_names(names_list):
    cleaned_list = [name for name in names_list if len(set(name.lower().split())) > 1]
    return cleaned_list


# Initialize Graph


profiles = pd.DataFrame(
    execute_neo4j_query(
        "MATCH (p:Profile) RETURN p.name AS name, p.url AS url, ID(p) AS id", {}
    )
)
valid_names = pd.DataFrame(
    execute_neo4j_query(
        "MATCH (valid_name:ValidName) RETURN ID(valid_name) as id, valid_name.full_name AS full_name, valid_name.name AS name",
        {},
    )
)
profiles = profiles[profiles["name"].apply(is_valid_name)]
people_names = valid_names["name"].tolist()

# Function to check if the name is a repetition or a single word

tqdm.pandas()

# Apply the matching function with a progress bar
profiles["matched_searchlight_name"] = profiles["name"].progress_apply(
    lambda x: match_names_rapidfuzz(x, people_names, 95)
)
profiles["matched_searchlight_name"].isna().sum()
matched_searchlight_names = profiles[~profiles["matched_searchlight_name"].isna()][
    "matched_searchlight_name"
].to_list()
profiles_dict = profiles[~profiles["matched_searchlight_name"].isna()].to_dict(
    "records"
)
# Run the script to create relationships
new_relationships_count = 0
for profile in profiles_dict:
    parameters = {
        "id": profile["id"],
        "matched_searchlight_name": profile["matched_searchlight_name"],
    }
    neo4j_query = """
    MATCH (profile:Profile), (valid_name:ValidName)
    WHERE ID(profile) = $id AND valid_name.name = $matched_searchlight_name
    MERGE (valid_name)-[r:HAS_PROFILE_NAME]->(profile)
    ON CREATE SET r.isNew = True
    RETURN r.isNew"""
    result = graph.run(neo4j_query, parameters).data()

    # Check if a new relationship was created
    if result and result[0]["r.isNew"]:
        new_relationships_count += 1

# Optionally, remove the isNew property from all HAS_PROFILE_NAME relationships
remove_is_new_query = """
MATCH ()-[r:HAS_PROFILE_NAME]-()
REMOVE r.isNew"""
graph.run(remove_is_new_query)

print(
    f"Number of new 'HAS_PROFILE_NAME' relationships created: {new_relationships_count}"
)

cleaned_searchlight_names_list = remove_repetitive_names(matched_searchlight_names)
# Preprocess the people names


# Cypher query
query = """
MATCH path = (startProfile:Profile)-[*..4]-(validname:ValidName)-[]-(person1:Person)-[]-(irf:IRF)
WHERE
    ANY(node in nodes(path) WHERE node:Person) AND
    ANY(node in nodes(path) WHERE node:IRF) AND
    NONE(node in nodes(path) WHERE node:Role OR node:WorkText OR (node:Name AND NOT node:ValidName))
    AND ID(startProfile) IN [466423,466098,626]
RETURN startProfile.name AS startProfileName, startProfile.url AS startProfileUrl,
       collect(distinct [profile.name, profile.url]) AS profileUrls,
       validname.name AS validName, person1.person_id AS personId,
       (MATCH (person1)-[:HAS_ROLE]->(role) RETURN role.role) AS role,
       irf.irf_number AS irfNumber
LIMIT 100;
"""

# Execute the query
results = graph.run(query)

# Process results and create DataFrame
data = []
for record in results:
    data.append(
        {
            "Start Profile Name": record["startProfileName"],
            "Start Profile URL": record["startProfileUrl"],
            "Profile URLs": record["profileUrls"],
            "Valid Name": record["validName"],
            "Person ID": record["personId"],
            "Role": record["role"],
            "IRF Number": record["irfNumber"],
        }
    )

df = pd.DataFrame(data)

# Export DataFrame to CSV
df.to_csv("report.csv", index=False)
