from py2neo import Graph, Node, Relationship
from libraries.google_lib import DB_Conn
import os
import pandas as pd
from fuzzywuzzy import process
import swifter
import pandas as pd
from rapidfuzz import process, fuzz
from tqdm.auto import tqdm


# Environment variable fetching and error handling
neo4j_url = os.environ.get("NEO4J_URL")
neo4j_usr = os.environ.get("NEO4J_USR", "neo4j")  # Default to 'neo4j' if not set
neo4j_pwd = os.environ.get("NEO4J_PWD")

if not all([neo4j_url, neo4j_usr, neo4j_pwd]):
    raise EnvironmentError("Required NEO4J environment variables are not set.")


def create_person_node(neo4j_graph, person_data):
    # Create Person node
    person_node = Node(
        "Person",
        full_name=person_data["full_name"],
        person_id=person_data["person_id"],
        gender=person_data["gender"],
        phone_contact=person_data["phone_contact"],
        address_notes=person_data["address_notes"],
    )
    neo4j_graph.create(person_node)

    # Create related nodes and relationships
    if person_data["master_person_id"]:
        master_person_node = Node("MasterPerson", id=person_data["master_person_id"])
        neo4j_graph.merge(master_person_node, "MasterPerson", "id")
        neo4j_graph.create(
            Relationship(person_node, "HAS_MASTER_PERSON_ID", master_person_node)
        )

    if person_data["role"]:
        role_node = Node("Role", name=person_data["role"])
        neo4j_graph.merge(role_node, "Role", "name")
        neo4j_graph.create(Relationship(person_node, "HAS_ROLE", role_node))

    # Add more relationships as needed


def import_data_to_neo4j():
    persons = get_persons()
    for person in persons:
        create_person_node(person)


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


def get_persons():
    parameters = {}
    sql_query = """SELECT    person.full_name AS full_name \
                            ,person.id AS person_id \
                            ,person.role AS role \
                            ,person.master_person_id AS master_person_id \
                            ,person.gender as gender \
                            ,person.phone_contact as phone_contact \
                            ,person.address_notes as address_notes \
                            FROM public.dataentry_person person """
    with DB_Conn() as dbc:
        persons = dbc.ex_query(sql_query, parameters)
    return persons


# Initialize Graph
graph = Graph(neo4j_url, user=neo4j_usr, password=neo4j_pwd)
profiles = graph.run(
    "MATCH (p:Profile) RETURN p.name AS name, p.url AS url, ID(p) AS id"
).to_data_frame()
valid_names = graph.run(
    "MATCH (valid_name:ValidName) RETURN ID(valid_name) as id, valid_name.full_name AS full_name, valid_name.name AS name"
).to_data_frame()
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
