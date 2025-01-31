import logging
import os
import sqlite3
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List, Dict, Any, Union
from datetime import datetime, timedelta
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import Optional
from models import (
    SuspectFormResponse, VictimFormResponse,
)


# Load environment variables
load_dotenv()


@dataclass
class URLRecord:
    """Data class representing a URL record for database operations."""

    url: str
    domain_name: str
    source: str
    id: Optional[int] = field(default=None)
    extracted_date: Optional[str] = None
    content: Optional[str] = None
    actual_incident: Optional[int] = 0
    author: Optional[str] = None
    published_date: Optional[str] = None
    title: Optional[str] = None


class DatabaseError(Exception):
    """Custom exception for database-related errors."""

    pass


class URLDatabase:
    """Handler for URL database operations with logging and error handling."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        """
        Initialize the URL database handler.

        Args:
            db_path: Optional path to the database file. If None, uses HTDB_PATH from environment.

        Raises:
            DatabaseError: If database path is not set or environment variable is missing.
        """
        self.db_path = db_path or os.getenv("HTDB_PATH")
        if not self.db_path:
            raise DatabaseError(
                "Database path not set. Check HTDB_PATH environment variable."
            )

        # Ensure logs directory exists
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        # Configure logging
        self._setup_logging()

        # Ensure database directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self.create_database()

    def _setup_logging(self) -> None:
        """Configure rotating file logger for database operations."""
        log_file = self.log_dir / "work_with_db.log"

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        handler = RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5  # 10MB
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        self.logger = logger

    def get_column_names(self, table_name: str) -> List[str]:
        """
        Retrieve all column names from a specified table in the database.

        Args:
            table_name: The name of the table to fetch column names from.

        Returns:
            A list of column names as strings.

        Raises:
            DatabaseError: If the query fails or the table does not exist.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall()]  # Extract column names from PRAGMA result
                if not columns:
                    raise DatabaseError(f"Table '{table_name}' does not exist or has no columns.")
                return columns
        except sqlite3.Error as e:
            error_msg = f"Failed to retrieve column names for table '{table_name}': {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)

    def create_victim_table(self) -> None:
        """
        Create the 'suspects' table if it doesn't exist.

        The table maintains a relationship with the 'urls' table via the 'url_id' field.

        Raises:
            DatabaseError: If table creation fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS victims (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url_id INTEGER NOT NULL,
                        victim TEXT NOT NULL,
                        UNIQUE (url_id, victim),  -- Ensures unique combination of url_id and victim
                        FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE ON UPDATE CASCADE
                    )
                    """
                )
                conn.commit()
                self.logger.info("Database table 'victims' created or verified successfully.")
        except sqlite3.Error as e:
            error_msg = f"Failed to create 'victims' table: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)


    def create_suspect_table(self) -> None:
        """
        Create the 'suspects' table if it doesn't exist.

        The table maintains a relationship with the 'urls' table via the 'url_id' field.

        Raises:
            DatabaseError: If table creation fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS suspects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url_id INTEGER NOT NULL,
                        suspect TEXT NOT NULL,
                        UNIQUE (url_id, suspect),  -- Ensures unique combination of url_id and suspect
                        FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE ON UPDATE CASCADE
                    )
                    """
                )
                conn.commit()
                self.logger.info("Database table 'suspects' created or verified successfully.")
        except sqlite3.Error as e:
            error_msg = f"Failed to create 'suspects' table: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)

    def create_incidents_table(self) -> None:
        """
        Create the 'incidents' table if it doesn't exist.

        The table maintains a relationship with the 'urls' table via the 'url_id' field.

        Raises:
            DatabaseError: If table creation fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS incidents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url_id INTEGER NOT NULL,
                        incident TEXT NOT NULL,
                        FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE ON UPDATE CASCADE
                    )
                    """
                )
                conn.commit()
                self.logger.info("Database table 'incidents' created or verified successfully.")
        except sqlite3.Error as e:
            error_msg = f"Failed to create 'incidents' table: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)

    def create_victim_forms_table(self) -> None:
        """
        Create the 'suspect_forms' table if it doesn't exist.

        The table maintains a relationship with the 'urls' table via the 'url_id' field.

        Raises:
            DatabaseError: If table creation fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS victim_forms (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url_id INTEGER NOT NULL,
                        name TEXT NOT NULL, -- The name of the victim
                        gender TEXT CHECK(gender IN ('male', 'female', NULL)),
                        date_of_birth TEXT, -- Format: YYYY-MM-DD
                        age INTEGER,
                        address_notes TEXT,
                        phone_number TEXT,
                        nationality TEXT,
                        occupation TEXT,
                        appearance TEXT,
                        vehicle_description TEXT,
                        vehicle_plate_number TEXT,
                        evidence TEXT,
                        destination TEXT,
                        job_offered TEXT,
                        FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE ON UPDATE CASCADE
                    )
                    """
                )
                conn.commit()
                self.logger.info("Database table 'suspect_forms' created or verified successfully.")
        except sqlite3.Error as e:
            error_msg = f"Failed to create 'suspect_forms' table: {str(e)}"


    def create_suspect_forms_table(self) -> None:
        """
        Create the 'suspect_forms' table if it doesn't exist.

        The table maintains a relationship with the 'urls' table via the 'url_id' field.

        Raises:
            DatabaseError: If table creation fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS suspect_forms (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url_id INTEGER NOT NULL,
                        name TEXT NOT NULL, -- The name of the suspect
                        gender TEXT CHECK(gender IN ('male', 'female', NULL)),
                        date_of_birth TEXT, -- Format: YYYY-MM-DD
                        age INTEGER,
                        address_notes TEXT,
                        phone_number TEXT,
                        nationality TEXT,
                        occupation TEXT,
                        role TEXT,
                        appearance TEXT,
                        vehicle_description TEXT,
                        vehicle_plate_number TEXT,
                        evidence TEXT,
                        arrested_status TEXT,
                        arrest_date TEXT, -- Format: YYYY-MM-DD
                        crimes_person_charged_with TEXT,
                        willing_pv_names TEXT,
                        suspect_in_police_custody TEXT,
                        suspect_current_location TEXT,
                        suspect_last_known_location TEXT,
                        suspect_last_known_location_date TEXT, -- Format: YYYY-MM-DD
                        FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE ON UPDATE CASCADE
                    )
                    """
                )
                conn.commit()
                self.logger.info("Database table 'suspect_forms' created or verified successfully.")
        except sqlite3.Error as e:
            error_msg = f"Failed to create 'suspect_forms' table: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)

    def create_database(self) -> None:
        """
        Create the URLs table if it doesn't exist.

        Raises:
            DatabaseError: If table creation fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS urls (
                        id INTEGER PRIMARY KEY,
                        url TEXT UNIQUE,
                        extracted_date TEXT,
                        content TEXT,
                        domain_name TEXT,
                        source TEXT,
                        actual_incident INTEGER DEFAULT -1,
                        author TEXT,
                        published_date TEXT,
                        title TEXT
                    )
                    """
                )
                conn.commit()
                self.logger.info(
                    "Database table 'urls' created or verified successfully"
                )
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create database table: {str(e)}")
            raise DatabaseError(f"Failed to create database table: {str(e)}")

    def update_field(self, url: str, field: str, value: Any) -> None:
        """
        Update a specific field for a URL in the database.

        Args:
            url: The URL whose field needs to be updated.
            field: The name of the field to update.
            value: The new value to set for the field.

        Raises:
            ValueError: If the field name is invalid.
            DatabaseError: If the update fails.
        """
        valid_fields = {
            "content",
            "domain_name",
            "source",
            "extracted_date",
            "actual_incident",
            "author",
            "published_date",
            "title",
        }

        if field not in valid_fields:
            raise ValueError(f"Invalid field name: {field}. Valid fields are: {', '.join(valid_fields)}")

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = f"UPDATE urls SET {field} = ? WHERE url = ?"
                cursor.execute(query, (value, url))
                if cursor.rowcount == 0:
                    self.logger.warning(f"No record found for URL: {url}")
                else:
                    self.logger.info(f"Successfully updated field '{field}' for URL: {url}")
                conn.commit()
        except sqlite3.Error as e:
            error_msg = f"Failed to update field '{field}' for URL {url}: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)

    def insert_url(self, record: Dict[str, Any]) -> None:
        """
        Insert a URL record into the database.

        Args:
            record: Dictionary containing URL data with keys:
                   'url', 'domain_name', 'source'

        Raises:
            DatabaseError: If insertion fails.
            KeyError: If required fields are missing from the record.
        """
        try:
            url_record = URLRecord(
                url=record["url"],
                domain_name=record["domain_name"],
                source=record["source"],
                extracted_date=datetime.now().isoformat(),
                actual_incident=record["actual_incident"]
            )

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO urls
                    (url, domain_name, source, extracted_date, actual_incident)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        url_record.url,
                        url_record.domain_name,
                        url_record.source,
                        url_record.extracted_date,
                        url_record.actual_incident
                    ),
                )
                conn.commit()
                self.logger.info(f"Successfully inserted URL: {url_record.url}")

        except KeyError as e:
            error_msg = f"Missing required field in record: {str(e)}"
            self.logger.error(error_msg)
            raise KeyError(error_msg)
        except sqlite3.Error as e:
            error_msg = f"Failed to insert URL record: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)

    def update_content(self, url: str, content: str) -> None:
        """
        Update the content field for a specific URL in the database.

        Args:
            url: The URL whose content field needs to be updated.
            content: The content to be updated in the database.

        Raises:
            DatabaseError: If the update fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE urls
                    SET content = ?
                    WHERE url = ?
                    """,
                    (content, url),
                )
                if cursor.rowcount == 0:
                    self.logger.warning(f"No record found for URL: {url}")
                else:
                    self.logger.info(f"Successfully updated content for URL: {url}")
                conn.commit()
        except sqlite3.Error as e:
            error_msg = f"Failed to update content for URL {url}: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)

    def get_url_by_id(self, url_id: int) -> Optional[URLRecord]:
        """
        Retrieve a URL record by its ID.

        Args:
            url_id: The ID of the URL record to retrieve.

        Returns:
            URLRecord if found, None otherwise.

        Raises:
            DatabaseError: If the query fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT id, url, extracted_date, content, domain_name, source
                    FROM urls
                    WHERE id = ?
                """,
                    (url_id,),
                )

                row = cursor.fetchone()
                if row:
                    return URLRecord(
                        id=row[0],
                        url=row[1],
                        extracted_date=row[2],
                        content=row[3],
                        domain_name=row[4],
                        source=row[5],
                    )
                return None

        except sqlite3.Error as e:
            error_msg = f"Failed to retrieve URL with ID {url_id}: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)

    def search_urls(
            self,
            domain: Optional[str] = None,
            source: Optional[str] = None,
            date_from: Optional[Union[str, datetime]] = None,
            date_to: Optional[Union[str, datetime]] = None,
            limit: int = 100,
    ) -> List[URLRecord]:
        """
        Search URLs based on various criteria.

        Args:
            domain: Optional domain name to filter by
            source: Optional source to filter by
            date_from: Optional start date for extraction date range
            date_to: Optional end date for extraction date range
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of URLRecord objects matching the criteria

        Raises:
            DatabaseError: If the query fails
        """
        try:
            query_parts = ["SELECT * FROM urls WHERE 1=1"]
            params = []

            if domain:
                query_parts.append("AND domain_name LIKE ?")
                params.append(f"%{domain}%")

            if source:
                query_parts.append("AND source = ?")
                params.append(source)

            if date_from:
                if isinstance(date_from, datetime):
                    date_from = date_from.isoformat()
                query_parts.append("AND extracted_date >= ?")
                params.append(date_from)

            if date_to:
                if isinstance(date_to, datetime):
                    date_to = date_to.isoformat()
                query_parts.append("AND extracted_date <= ?")
                params.append(date_to)

            query_parts.append("ORDER BY extracted_date DESC LIMIT ?")
            params.append(limit)

            query = " ".join(query_parts)

            self.logger.debug(f"Executing query: {query} with params: {params}")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, params)
                return [
                    URLRecord(
                        id=row[0],
                        url=row[1],
                        extracted_date=row[2],
                        content=row[3],
                        domain_name=row[4],
                        source=row[5],
                        author=row[6],
                        actual_incident=row[7],
                        published_date=row[8],
                        title=row[9]
                    )
                    for row in cursor.fetchall()
                ]

        except sqlite3.Error as e:
            error_msg = f"Failed to search URLs: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)

    def get_recent_urls(self, days: int = 7, limit: int = 50) -> List[URLRecord]:
        """
        Retrieve URLs extracted within the specified number of days.

        Args:
            days: Number of days to look back (default: 7)
            limit: Maximum number of records to return (default: 50)

        Returns:
            List of URLRecord objects from the specified time period

        Raises:
            DatabaseError: If the query fails
        """
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        return self.search_urls(date_from=date_from, limit=limit)

    def get_urls_by_domain(self, domain: str) -> List[URLRecord]:
        """
        Retrieve all URLs for a specific domain.

        Args:
            domain: The domain name to search for

        Returns:
            List of URLRecord objects matching the domain

        Raises:
            DatabaseError: If the query fails
        """
        return self.search_urls(domain=domain)

    def insert_incident(self, url_id: int, incident: str) -> None:
        """
        Insert an incident into the incidents table.

        Args:
            url_id: The ID of the URL the incident relates to.
            incident: The text of the incident.

        Raises:
            DatabaseError: If the insertion fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO incidents (url_id, incident)
                    VALUES (?, ?)
                    """,
                    (url_id, incident),
                )
                conn.commit()
        except sqlite3.Error as e:
            error_msg = f"Failed to insert incident for URL ID {url_id}: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)

    def insert_suspect(self, url_id: int, suspect: str) -> None:
        """
        Insert a suspect into the suspects table.

        Args:
            url_id: The ID of the URL the suspect relates to.
            suspect: The name(s) of the suspect.

        Raises:
            DatabaseError: If the insertion fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO suspects (url_id, suspect)
                    VALUES (?, ?)
                    """,
                    (url_id, suspect),
                )
                conn.commit()
        except sqlite3.Error as e:
            error_msg = f"Failed to insert suspect for URL ID {url_id}: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)

    def insert_victim(self, url_id: int, victim: str) -> None:
        """
        Insert a suspect into the suspects table.

        Args:
            url_id: The ID of the URL the suspect relates to.
            suspect: The name(s) of the suspect.

        Raises:
            DatabaseError: If the insertion fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO victims (url_id, victim)
                    VALUES (?, ?)
                    """,
                    (url_id, victim),
                )
                conn.commit()
        except sqlite3.Error as e:
            error_msg = f"Failed to insert victim for URL ID {url_id}: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)

    def insert_victim_form(self, url_id: int, victim_data: VictimFormResponse) -> None:
        """
        Insert a suspect form into the suspect_forms table.

        Args:
            url_id (int): The ID of the URL to which the suspect form relates.
            victim_data (VictimFormResponse): The data extracted from the suspect form prompt.

        Raises:
            DatabaseError: If the insertion fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO victim_forms (
                        url_id, name, gender, date_of_birth, age, address_notes, phone_number,
                        nationality, occupation, appearance, vehicle_description,
                        vehicle_plate_number, destination, job_offered
                    )
                    VALUES (
                        :url_id, :name, :gender, :date_of_birth, :age, :address_notes, :phone_number,
                        :nationality, :occupation, :appearance, :vehicle_description,
                        :vehicle_plate_number, :destination, :job_offered
                    )
                    """,
                    {
                        "url_id": url_id,
                        "name": victim_data.name,
                        "gender": victim_data.gender,
                        "date_of_birth": victim_data.date_of_birth,
                        "age": victim_data.age,
                        "address_notes": victim_data.address_notes,
                        "phone_number": victim_data.phone_number,
                        "nationality": victim_data.nationality,
                        "occupation": victim_data.occupation,
                        "appearance": victim_data.appearance,
                        "vehicle_description": victim_data.vehicle_description,
                        "vehicle_plate_number": victim_data.vehicle_plate_number,
                        "destination": victim_data.destination,
                        "job_offered": victim_data.job_offered,
                    },
                )
                conn.commit()
        except sqlite3.Error as e:
            error_msg = f"Failed to insert suspect form for URL ID {url_id}: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)


    def insert_suspect_form(self, url_id: int, suspect_data: SuspectFormResponse) -> None:
        """
        Insert a suspect form into the suspect_forms table.

        Args:
            url_id (int): The ID of the URL to which the suspect form relates.
            suspect_data (SuspectFormResponse): The data extracted from the suspect form prompt.

        Raises:
            DatabaseError: If the insertion fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO suspect_forms (
                        url_id, name, gender, date_of_birth, age, address_notes, phone_number,
                        nationality, occupation, role, appearance, vehicle_description,
                        vehicle_plate_number, evidence, arrested_status, arrest_date,
                        crimes_person_charged_with, willing_pv_names, suspect_in_police_custody,
                        suspect_current_location, suspect_last_known_location, suspect_last_known_location_date
                    )
                    VALUES (
                        :url_id, :name, :gender, :date_of_birth, :age, :address_notes, :phone_number,
                        :nationality, :occupation, :role, :appearance, :vehicle_description,
                        :vehicle_plate_number, :evidence, :arrested_status, :arrest_date,
                        :crimes_person_charged_with, :willing_pv_names, :suspect_in_police_custody,
                        :suspect_current_location, :suspect_last_known_location, :suspect_last_known_location_date
                    )
                    """,
                    {
                        "url_id": url_id,
                        "name": suspect_data.name,
                        "gender": suspect_data.gender,
                        "date_of_birth": suspect_data.date_of_birth,
                        "age": suspect_data.age,
                        "address_notes": suspect_data.address_notes,
                        "phone_number": suspect_data.phone_number,
                        "nationality": suspect_data.nationality,
                        "occupation": suspect_data.occupation,
                        "role": suspect_data.role,
                        "appearance": suspect_data.appearance,
                        "vehicle_description": suspect_data.vehicle_description,
                        "vehicle_plate_number": suspect_data.vehicle_plate_number,
                        "evidence": suspect_data.evidence,
                        "arrested_status": suspect_data.arrested_status,
                        "arrest_date": suspect_data.arrest_date,
                        "crimes_person_charged_with": suspect_data.crimes_person_charged_with,
                        "willing_pv_names": suspect_data.willing_pv_names,
                        "suspect_in_police_custody": suspect_data.suspect_in_police_custody,
                        "suspect_current_location": suspect_data.suspect_current_location,
                        "suspect_last_known_location": suspect_data.suspect_last_known_location,
                        "suspect_last_known_location_date": suspect_data.suspect_last_known_location_date,
                    },
                )
                conn.commit()
        except sqlite3.Error as e:
            error_msg = f"Failed to insert suspect form for URL ID {url_id}: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)

    def get_url_id(self, url: str) -> Optional[int]:
        """
        Retrieve the ID of a URL from the database.

        Args:
            url: The URL to look up.

        Returns:
            The ID of the URL if found, otherwise None.

        Raises:
            DatabaseError: If the query fails.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT id FROM urls WHERE url = ?", (url,)
                )
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error as e:
            error_msg = f"Failed to retrieve URL ID for {url}: {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)
