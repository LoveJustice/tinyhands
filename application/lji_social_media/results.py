from py2neo import Graph
import os

# Environment variable fetching and error handling
neo4j_url = os.environ.get("NEO4J_URL")
neo4j_usr = os.environ.get("NEO4J_USR", "neo4j")  # Default to 'neo4j' if not set
neo4j_pwd = os.environ.get("NEO4J_PWD")

if not all([neo4j_url, neo4j_usr, neo4j_pwd]):
    raise EnvironmentError("Required NEO4J environment variables are not set.")
graph = Graph(neo4j_url, user=neo4j_usr, password=neo4j_pwd)
parameters = {"id1": 5419, "id2": 7100}
neo4j_query = """MATCH path1 = (valid_nameX:ValidName)-[:HAS_NAME]-(personX:Person)-[:ON_IRF]-(irf0:IRF)-[:ON_IRF]-(person0:Person)-[:HAS_NAME]-(valid_name0:ValidName)- [:HAS_PROFILE_NAME]-(profile0:Profile)-[:IS_FRIENDS_WITH]-(source_profile1:SourceProfile)-[]-(valid_name1:ValidName)-[]-(person1:Person)-[]-(irf:IRF)<-[:ON_IRF]-(person2:Person)-[:HAS_NAME]-(valid_name2:ValidName)
WHERE ID(source_profile1) IN [$id1, $id2]
OPTIONAL MATCH (person1) -[:HAS_MASTER_PERSON_ID]- (master1:MasterPerson),
              (person2) -[:HAS_MASTER_PERSON_ID]- (master2:MasterPerson),
              (personX) -[:HAS_MASTER_PERSON_ID]- (masterX:MasterPerson),
              (person0) -[:HAS_MASTER_PERSON_ID]- (master0:MasterPerson)
RETURN valid_nameX.full_name AS full_nameX
, personX.person_id AS person_idX
, irf0.irf_number AS irf_number0
, person0.person_id AS person_id0
, profile0.name AS friend
, source_profile1.name AS source_profile1_name
, valid_name1.full_name AS valid_name1_full_name
, person1.person_id AS person_id1
, irf.irf_number AS irf_number
, person2.person_id AS person_id2
, valid_name2.full_name AS full_name2
, master0.master_person_id AS master_person_id0
, master1.master_person_id AS master_person_id1
, master2.master_person_id AS master_person_id2
, masterX.master_person_id AS master_person_idX
LIMIT 100;"""
matches = graph.run(neo4j_query, parameters).to_data_frame()

matches.to_csv("results/willemheinrichpretorius.csv", index=False)
