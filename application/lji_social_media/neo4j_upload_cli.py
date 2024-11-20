#!/usr/bin/env python3

"""
trafficking_data_processor.py - Process and load human trafficking data into Neo4j graph database.
"""

import argparse
import logging
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from typing import List, Dict, Any

from libraries.neo4j_lib import execute_neo4j_query
from libraries.network_data import (
    get_suspects,
    get_irf,
    get_vdf,
    get_persons,
    get_countries,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TraffickingDataProcessor:
    """Process and load human trafficking data into Neo4j graph database."""

    def __init__(self):
        """Initialize the processor."""
        self.countries = get_countries()

    @staticmethod
    def is_valid_name(name: str) -> bool:
        """Check if a name is valid (contains multiple unique words)."""
        if not isinstance(name, str):
            return False
        words = name.lower().split()
        return len(words) > 1 and len(set(words)) > 1

    @staticmethod
    def extract_column_values(column_series: pd.Series) -> pd.Series:
        """Extract and clean values from a semicolon-separated column."""
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
                if value and value.strip()
            )
        )
        return pd.Series(all_values)

    def create_indexes(self):
        """Create necessary indexes in Neo4j database."""
        indexes = [
            "CREATE INDEX person_id_index FOR (p:Person) ON (p.person_id)",
            "CREATE INDEX master_person_id_index FOR (m:MasterPerson) ON (m.master_person_id)",
            "CREATE INDEX role_index FOR (r:Role) ON (r.role)",
            "CREATE INDEX full_name_index FOR (n:Name) ON (n.full_name)",
            "CREATE INDEX name_index FOR (n:Name) ON (n.name)",
        ]
        for index in indexes:
            try:
                execute_neo4j_query(index, {})
                logger.info(f"Created index: {index}")
            except Exception as e:
                logger.warning(f"Failed to create index: {e}")

    def process_persons(self):
        """Process and load person data."""
        logger.info("Processing persons data")
        persons = get_persons()
        persons = persons[persons.full_name.notna()]
        persons["role"] = persons["role"].fillna("unknown_role")
        persons["role"] = self.extract_column_values(persons["role"])

        for person in tqdm(persons.to_dict("records"), desc="Processing persons"):
            self._create_person_nodes(person)
            if self.is_valid_name(person["full_name"]):
                self._mark_valid_name(person)

    def process_victims(self):
        """Process and load victim data."""
        logger.info("Processing victims data")
        victims = get_vdf()
        victims = self._prepare_dataframe(victims)

        for victim in tqdm(victims.to_dict("records"), desc="Processing victims"):
            self._create_victim_nodes(victim)
            if self.is_valid_name(victim["full_name"]):
                self._mark_valid_name(victim)

    def process_suspects(self):
        """Process and load suspect data."""
        logger.info("Processing suspects data")
        suspects = get_suspects()
        suspects = self._prepare_dataframe(suspects)

        for suspect in tqdm(suspects.to_dict("records"), desc="Processing suspects"):
            self._create_suspect_nodes(suspect)
            if self.is_valid_name(suspect["full_name"]):
                self._mark_valid_name(suspect)

    def process_irfs(self):
        """Process and load IRF (Incident Report Form) data."""
        logger.info("Processing IRFs data")
        irfs = self._get_new_irfs()
        irfs = self._prepare_dataframe(irfs)

        for irf in tqdm(irfs.to_dict("records"), desc="Processing IRFs"):
            self._create_irf_nodes(irf)
            if self.is_valid_name(irf["full_name"]):
                self._mark_valid_name(irf)

    def _prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare dataframe by cleaning and standardizing fields."""
        df["role"] = df["role"].fillna("unknown_role")
        df["full_name"] = df["full_name"].fillna("unknown_name")
        df["role"] = self.extract_column_values(df["role"])
        df.loc[df["role"] == "", "role"] = "unknown_role"
        return df

    def _get_new_irfs(self) -> pd.DataFrame:
        """Get IRFs that haven't been processed yet."""
        query = """MATCH (irf_id:IRF_ID) RETURN irf_id.irf_id AS irf_id"""
        irf_ids = pd.DataFrame(execute_neo4j_query(query, {}))
        irfs = get_irf()
        return irfs[~irfs["irf_id"].isin(irf_ids["irf_id"])]

    def _create_person_nodes(self, person: Dict[str, Any]):
        """Create person-related nodes and relationships."""
        parameters = {
            "person_id": person["person_id"],
            "full_name": person["full_name"],
            "name": person["full_name"].lower().strip(),
            "master_person_id": person["master_person_id"],
            "role": person["role"],
            "photo": person["photo"],
        }
        query = """
        MERGE (p:Person {person_id: $person_id})
        MERGE (photo:Photo {photo: $photo})
        MERGE (name:Name {full_name: $full_name, name: $name})
        MERGE (m:MasterPerson {master_person_id: $master_person_id})
        MERGE (role:Role {role: $role})
        MERGE (p)-[:HAS_MASTER_PERSON_ID]->(m)
        MERGE (p)-[:HAS_ROLE]->(role)
        MERGE (p)-[:HAS_NAME]->(name)
        MERGE (p)-[:HAS_PHOTO]->(photo)
        """
        execute_neo4j_query(query, parameters)

    def _create_victim_nodes(self, victim: Dict[str, Any]):
        """Create victim-related nodes and relationships."""
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
        query = """
        MERGE (person:Person {person_id: $person_id})
        MERGE (name:Name {full_name: $full_name, name: $name})
        MERGE (m:MasterPerson {master_person_id: $master_person_id})
        MERGE (victim:Victim {vdf_number: $vdf_number})
        MERGE (victim_id:VictimID {victim_id: $victim_id})
        MERGE (person)-[:HAS_MASTER_PERSON_ID]->(m)
        MERGE (person)-[:HAS_ROLE]->(role)
        MERGE (person)-[:HAS_NAME]->(name)
        MERGE (irf:IRF {irf_number: $irf_number})
        MERGE (person)-[:IS_VICTIM]->(victim)
        MERGE (person)-[:HAS_VICTIM_ID]->(victim_id)
        MERGE (irf)-[:HAS_VICTIM]->(victim)
        """
        execute_neo4j_query(query, parameters)

    def _create_suspect_nodes(self, suspect: Dict[str, Any]):
        """Create suspect-related nodes and relationships."""
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
        query = """
        MERGE (person:Person {person_id: $person_id})
        MERGE (name:Name {full_name: $full_name, name: $name})
        MERGE (m:MasterPerson {master_person_id: $master_person_id})
        MERGE (suspect:Suspect {sf_number: $sf_number})
        MERGE (person)-[:HAS_MASTER_PERSON_ID]->(m)
        MERGE (person)-[:HAS_ROLE]->(role)
        MERGE (person)-[:HAS_NAME]->(name)
        MERGE (irf:IRF {irf_number: $irf_number})
        MERGE (person)-[:IS_SUSPECT]->(suspect)
        MERGE (irf)-[:HAS_SUSPECT]->(suspect)
        """
        execute_neo4j_query(query, parameters)

    def _create_irf_nodes(self, irf: Dict[str, Any]):
        """Create IRF-related nodes and relationships."""
        parameters = {
            "irf_id": irf["irf_id"],
            "date_of_interception": irf["date_of_interception"],
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
        query = """
        MERGE (person:Person {person_id: $person_id})
        MERGE (irf_id:IRF_ID {irf_id: $irf_id, date_of_interception: date($date_of_interception)})
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
        MERGE (person)-[:ON_IRF]->(irf)
        MERGE (irf)<-[:FROM_IRF]-(irf_id)
        MERGE (irf)-[:AT_BORDER_STATION]->(borderstation)
        MERGE (borderstation)-[:IN_COUNTRY]->(country)
        """
        execute_neo4j_query(query, parameters)

    def _mark_valid_name(self, record: Dict[str, Any]):
        """Mark a name as valid in the database."""
        parameters = {
            "person_id": record["person_id"],
            "full_name": record["full_name"],
            "name": record["full_name"].lower().strip(),
        }
        query = """
        MATCH (person:Person {person_id:$person_id})-[:HAS_NAME]->(name:Name {full_name: $full_name, name: $name})
        SET name:ValidName
        """
        execute_neo4j_query(query, parameters)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Process and load human trafficking data into Neo4j database"
    )
    parser.add_argument(
        "--create-indexes",
        action="store_true",
        help="Create database indexes before processing",
    )
    parser.add_argument(
        "--skip-persons", action="store_true", help="Skip processing persons data"
    )
    parser.add_argument(
        "--skip-victims", action="store_true", help="Skip processing victims data"
    )
    parser.add_argument(
        "--skip-suspects", action="store_true", help="Skip processing suspects data"
    )
    parser.add_argument(
        "--skip-irfs", action="store_true", help="Skip processing IRF data"
    )

    args = parser.parse_args()

    processor = TraffickingDataProcessor()

    try:
        if args.create_indexes:
            processor.create_indexes()

        if not args.skip_persons:
            processor.process_persons()

        if not args.skip_victims:
            processor.process_victims()

        if not args.skip_suspects:
            processor.process_suspects()

        if not args.skip_irfs:
            processor.process_irfs()

        logger.info("Data processing completed successfully")

    except Exception as e:
        logger.error(f"An error occurred during processing: {e}")
        raise


if __name__ == "__main__":
    main()
