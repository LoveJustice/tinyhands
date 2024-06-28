from py2neo import Graph
import os
from pathlib import Path
from libraries.google_lib import DB_Conn
import pandas as pd
from libraries.network_data import get_suspects, get_irf, get_vdf, get_persons


def is_valid_name(name):
    words = name.lower().split()
    return len(words) > 1 and len(set(words)) > 1


def extract_column_values(column_series):
    all_values = []
    column_series.str.lower().str.split(";").apply(
        lambda x: all_values.extend(
            value.strip()
            .replace('"', "")
            .replace("'", "")
            .replace(" / ", "/")
            .replace("/ ", "/")
            .strip("_")
            for value in x
            if value.strip()
        )
    )
    return pd.Series(all_values)


# Environment variable fetching and error handling
neo4j_url = os.environ.get("NEO4J_URL")
neo4j_usr = os.environ.get("NEO4J_USR", "neo4j")  # Default to 'neo4j' if not set
neo4j_pwd = os.environ.get("NEO4J_PWD")


if not all([neo4j_url, neo4j_usr, neo4j_pwd]):
    raise EnvironmentError("Required NEO4J environment variables are not set.")

graph = Graph(neo4j_url, user=neo4j_usr, password=neo4j_pwd)


def create_indexes(graph):
    indexes = [
        "CREATE INDEX person_id_index FOR (p:Person) ON (p.person_id)",
        "CREATE INDEX master_person_id_index FOR (m:MasterPerson) ON (m.master_person_id)",
        "CREATE INDEX role_index FOR (r:Role) ON (r.role)",
        "CREATE INDEX full_name_index FOR (n:Name) ON (n.full_name)",
        "CREATE INDEX name_index FOR (n:Name) ON (n.name)",
    ]
    for index in indexes:
        graph.run(index)


persons = get_persons()
persons = persons[persons.full_name.notna()]
persons["role"] = persons["role"].fillna("unknown_role")
persons["role"] = extract_column_values(persons["role"])
persons_dict = persons.to_dict("records")

for person in persons_dict:
    parameters = {
        "person_id": person["person_id"],
        "full_name": person["full_name"],
        "name": person["full_name"].lower().strip(),
        "master_person_id": person["master_person_id"],
        "role": person["role"],
        "photo": person["photo"],
    }
    query = """MERGE (p:Person {person_id: $person_id})
    MERGE (photo:Photo {photo: $photo})
    MERGE (name:Name {full_name: $full_name, name: $name})
    MERGE (m:MasterPerson {master_person_id: $master_person_id})
    MERGE (role:Role {role: $role})
    MERGE (p)-[:HAS_MASTER_PERSON_ID]->(m)
    MERGE (p)-[:HAS_ROLE]->(role)
    MERGE (p)-[:HAS_NAME]->(name)
    MERGE (p)-[:HAS_PHOTO]->(photo)
    """

    graph.run(query, parameters)
    if is_valid_name(person["full_name"]):
        parameters = {
            "person_id": person["person_id"],
            "full_name": person["full_name"],
            "name": person["full_name"].lower().strip(),
        }
        query = """MATCH (person:Person {person_id:$person_id})-[:HAS_NAME]->(name:Name {full_name: $full_name, name: $name})
        SET name:ValidName"""
        graph.run(query, parameters)

suspects = get_suspects()
suspects["role"] = suspects["role"].fillna("unknown_role")
suspects["full_name"] = suspects["full_name"].fillna("unknown_name")
suspects["role"] = extract_column_values(suspects["role"])
suspects.loc[suspects["role"] == "", "role"] = "unknown_role"
suspects_dict = suspects.to_dict("records")

for suspect in suspects_dict:
    irf_number = suspect["sf_number"][:-1]
    parameters = {
        "sf_number": suspect["sf_number"],
        "person_id": suspect["person_id"],
        "full_name": suspect["full_name"],
        "role": suspect["role"],
        "name": suspect["full_name"].lower().strip(),
        "suspect_id": suspect["suspect_id"],
        "irf_number": irf_number,
        "master_person_id": suspect["master_person_id"],
    }
    query = """MERGE (person:Person {person_id: $person_id})
    MERGE (name:Name {full_name: $full_name, name: $name})
    MERGE (m:MasterPerson {master_person_id: $master_person_id})
    MERGE (suspect:Suspect {sf_number: $sf_number})
    MERGE (person)-[:HAS_MASTER_PERSON_ID]->(m)
    MERGE (person)-[:HAS_ROLE]->(role)
    MERGE (person)-[:HAS_NAME]->(name)
    MERGE (irf:IRF {irf_number: $irf_number})
    MERGE (person) - [:IS_SUSPECT] - (suspect)
    MERGE (irf) - [:HAS_SUSPECT] - (suspect)"""
    graph.run(query, parameters)
    if is_valid_name(suspect["full_name"]):
        parameters = {
            "person_id": suspect["person_id"],
            "full_name": suspect["full_name"],
            "name": suspect["full_name"].lower().strip(),
        }
        query = """MATCH (person:Person {person_id:$person_id})-[:HAS_NAME]->(name:Name {full_name: $full_name, name: $name})
        SET name:ValidName"""
        graph.run(query, parameters)

victims = get_vdf()
victims["role"] = victims["role"].fillna("unknown_role")
victims["full_name"] = victims["full_name"].fillna("unknown_name")
victims["role"] = extract_column_values(victims["role"])
victims.loc[victims["role"] == "", "role"] = "unknown_role"
victims_dict = victims.to_dict("records")
victims_dict[0]
for victim in victims_dict:
    irf_number = victim["vdf_number"][:-1]
    parameters = {
        "vdf_number": victim["vdf_number"],
        "person_id": victim["person_id"],
        "full_name": victim["full_name"],
        "role": victim["role"],
        "name": victim["full_name"].lower().strip(),
        "victim_id": victim["victim_id"],
        "irf_number": irf_number,
        "master_person_id": victim["master_person_id"],
    }
    query = """MERGE (person:Person {person_id: $person_id})
    MERGE (name:Name {full_name: $full_name, name: $name})
    MERGE (m:MasterPerson {master_person_id: $master_person_id})
    MERGE (victim:Victim {vdf_number: $vdf_number})
    MERGE (victim_id:VictimID {victim_id: $victim_id})
    MERGE (person)-[:HAS_MASTER_PERSON_ID]->(m)
    MERGE (person)-[:HAS_ROLE]->(role)
    MERGE (person)-[:HAS_NAME]->(name)
    MERGE (irf:IRF {irf_number: $irf_number})
    MERGE (person) - [:IS_VICTIM] - (victim)
    MERGE (person) - [:HAS_VICTIM_ID] - (victim_id)
    MERGE (irf) - [:HAS_VICTIM] - (victim)"""
    graph.run(query, parameters)
    if is_valid_name(victim["full_name"]):
        parameters = {
            "person_id": victim["person_id"],
            "full_name": victim["full_name"],
            "name": victim["full_name"].lower().strip(),
        }
        query = """MATCH (person:Person {person_id:$person_id})-[:HAS_NAME]->(name:Name {full_name: $full_name, name: $name})
        SET name:ValidName"""
        graph.run(query, parameters)

irfs = get_irf()
irfs["role"] = irfs["role"].fillna("unknown_role")
irfs["full_name"] = irfs["full_name"].fillna("unknown_name")
irfs["role"] = extract_column_values(irfs["role"])
irfs.loc[irfs["role"] == "", "role"] = "unknown_role"
irfs_dict = irfs.to_dict("records")
irfs_dict[0]
for irf in irfs_dict:
    irf_number = irf["irf_number"]
    parameters = {
        "irf_id": irf["irf_id"],
        "irf_number": irf["irf_number"],
        "person_id": irf["person_id"],
        "full_name": irf["full_name"],
        "role": irf["role"],
        "name": irf["full_name"].lower().strip(),
        "master_person_id": irf["master_person_id"],
        "operating_country_id": irf["operating_country_id"],
        "country": irf["country"],
        "station_name": irf["station_name"],
        "borderstation_id": irf["borderstation_id"],
    }
    query = """MERGE (person:Person {person_id: $person_id})
    MERGE (irf_id:IRF_ID {irf_id: $irf_id})
    MERGE (name:Name {full_name: $full_name, name: $name})
    MERGE (m:MasterPerson {master_person_id: $master_person_id})
    MERGE (role:Role {role: $role})
    MERGE (country:Country {name: $country, id: $operating_country_id})
    MERGE (borderstation:BorderStation {name: $station_name, id: $borderstation_id})
    MERGE (person)-[:HAS_MASTER_PERSON_ID]->(m)
    MERGE (person)-[:HAS_ROLE]->(role)
    MERGE (person)-[:HAS_NAME]->(name)
    MERGE (person)-[:HAS_IRF_ID]->(irf_id)
    MERGE (irf:IRF {irf_number: $irf_number})
    MERGE (person) - [:ON_IRF] -> (irf)
    MERGE (irf) <- [:FROM_IRF] - (irf_id)
    MERGE (irf) - [:AT_BORDER_STATION] -> (borderstation)
    MERGE (borderstation) - [:IN_COUNTRY] -> (country)"""
    graph.run(query, parameters)
    if is_valid_name(irf["full_name"]):
        parameters = {
            "person_id": irf["person_id"],
            "full_name": irf["full_name"],
            "name": irf["full_name"].lower().strip(),
        }
        query = """MATCH (person:Person {person_id:$person_id})-[:HAS_NAME]->(name:Name {full_name: $full_name, name: $name})
        SET name:ValidName"""
        graph.run(query, parameters)
