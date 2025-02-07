import logging
import logging.handlers  # <-- Ensure the logging.handlers submodule is imported.
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Union, Optional, Iterator

from dotenv import load_dotenv
from models import SuspectFormResponse, VictimFormResponse

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
    """
    Handler for URL database operations with logging, error handling, and improved connection management.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        """
        Initialize the URL database handler.

        Args:
            db_path: Optional path to the database file. If None, uses HTDB_PATH from environment.

        Raises:
            DatabaseError: If database path is not set.
        """
        self.db_path = db_path or os.getenv("HTDB_PATH")
        if not self.db_path:
            raise DatabaseError("Database path not set. Check HTDB_PATH environment variable.")

        # Ensure the parent directory for the database exists.
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Setup logging.
        self._setup_logging()

        # Initialize database schema.
        self._initialize_schema()

    def _setup_logging(self) -> None:
        """Configure a rotating file logger for database operations."""
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        log_file = self.log_dir / "work_with_db.log"

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # Avoid adding duplicate handlers
        if not self.logger.handlers:
            handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10 * 1024 * 1024, backupCount=5
            )
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """
        Context manager for database connections.
        Ensures that foreign keys are enabled for each new connection.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            yield conn
        except sqlite3.Error as e:
            self.logger.error(f"Database connection error: {str(e)}")
            raise DatabaseError(f"Database connection error: {str(e)}")
        finally:
            conn.close()

    @contextmanager
    def _execute_query(self, query: str, params: tuple = ()) -> Iterator[sqlite3.Cursor]:
        """
        Helper context manager to execute a query with standardized error handling.

        Args:
            query: The SQL query to execute.
            params: Parameters for the query.

        Yields:
            A sqlite3.Cursor object.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                yield cursor
        except sqlite3.Error as e:
            error_msg = f"Database query failed: {query} with params {params} - {str(e)}"
            self.logger.error(error_msg)
            raise DatabaseError(error_msg)

    def _initialize_schema(self) -> None:
        """
        Initialize (or upgrade) the database schema.
        For future upgrades consider using a migration framework.
        """
        self.create_urls_table()
        self.create_victim_table()
        self.create_suspect_table()
        self.create_incidents_table()
        self.create_victim_forms_table()
        self.create_suspect_forms_table()

    def get_column_names(self, table_name: str) -> List[str]:
        """
        Retrieve all column names from a specified table.

        Args:
            table_name: The name of the table.

        Returns:
            A list of column names.

        Raises:
            DatabaseError: If table retrieval fails.
        """
        query = f"PRAGMA table_info({table_name})"
        with self._execute_query(query) as cursor:
            rows = cursor.fetchall()
            columns = [row[1] for row in rows]
            if not columns:
                error_msg = f"Table '{table_name}' does not exist or has no columns."
                self.logger.error(error_msg)
                raise DatabaseError(error_msg)
            return columns

    def create_urls_table(self) -> None:
        """
        Create the URLs table if it doesn't exist.
        The table now includes an 'accessible' column (1 = accessible, 0 = inaccessible).
        """
        query = """
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                extracted_date TEXT,
                content TEXT,
                domain_name TEXT,
                source TEXT,
                actual_incident INTEGER DEFAULT -1,
                accessible INTEGER DEFAULT 1,  -- New column to record accessibility status
                author TEXT,
                published_date TEXT,
                title TEXT
            )
        """
        with self._execute_query(query):
            self.logger.info("Database table 'urls' created or verified successfully")

    def create_victim_table(self) -> None:
        """Create the 'victims' table if it doesn't exist."""
        query = """
            CREATE TABLE IF NOT EXISTS victims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER NOT NULL,
                victim TEXT NOT NULL,
                UNIQUE (url_id, victim),
                FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """
        with self._execute_query(query):
            self.logger.info("Database table 'victims' created or verified successfully.")

    def create_suspect_table(self) -> None:
        """Create the 'suspects' table if it doesn't exist."""
        query = """
            CREATE TABLE IF NOT EXISTS suspects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER NOT NULL,
                suspect TEXT NOT NULL,
                UNIQUE (url_id, suspect),
                FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """
        with self._execute_query(query):
            self.logger.info("Database table 'suspects' created or verified successfully.")

    def create_incidents_table(self) -> None:
        """Create the 'incidents' table if it doesn't exist."""
        query = """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER NOT NULL,
                incident TEXT NOT NULL,
                FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """
        with self._execute_query(query):
            self.logger.info("Database table 'incidents' created or verified successfully.")

    def create_victim_forms_table(self) -> None:
        """
        Create the 'victim_forms' table if it doesn't exist.
        A new column 'victim_id' is added to relate to the victims table.
        """
        query = """
            CREATE TABLE IF NOT EXISTS victim_forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER NOT NULL,
                victim_id INTEGER,  -- New column referencing victims.id
                name TEXT NOT NULL,
                gender TEXT CHECK(gender IN ('male', 'female', NULL)),
                date_of_birth TEXT,
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
                FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (victim_id) REFERENCES victims (id) ON DELETE SET NULL ON UPDATE CASCADE
            )
        """
        with self._execute_query(query):
            self.logger.info("Database table 'victim_forms' created or verified successfully.")

    def create_suspect_forms_table(self) -> None:
        """
        Create the 'suspect_forms' table if it doesn't exist.
        A new column 'suspect_id' is added to relate to the suspects table.
        """
        query = """
            CREATE TABLE IF NOT EXISTS suspect_forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_id INTEGER NOT NULL,
                suspect_id INTEGER,  -- New column referencing suspects.id
                name TEXT NOT NULL,
                gender TEXT CHECK(gender IN ('male', 'female', NULL)),
                date_of_birth TEXT,
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
                arrest_date TEXT,
                crimes_person_charged_with TEXT,
                willing_pv_names TEXT,
                suspect_in_police_custody TEXT,
                suspect_current_location TEXT,
                suspect_last_known_location TEXT,
                suspect_last_known_location_date TEXT,
                FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (suspect_id) REFERENCES suspects (id) ON DELETE SET NULL ON UPDATE CASCADE
            )
        """
        with self._execute_query(query):
            self.logger.info("Database table 'suspect_forms' created or verified successfully.")

    def update_field(self, url: str, field: str, value: Any) -> None:
        """
        Update a specific field for a URL in the database.

        Args:
            url: The URL to update.
            field: The field name.
            value: The new value.

        Raises:
            ValueError: If the field name is invalid.
            DatabaseError: If the update fails.
        """
        valid_fields = {"content", "domain_name", "source", "extracted_date",
                        "actual_incident", "author", "published_date", "title"}
        if field not in valid_fields:
            raise ValueError(f"Invalid field name: {field}. Valid fields are: {', '.join(valid_fields)}")

        query = f"UPDATE urls SET {field} = ? WHERE url = ?"
        with self._execute_query(query, (value, url)) as cursor:
            if cursor.rowcount == 0:
                self.logger.warning(f"No record found for URL: {url}")
            else:
                self.logger.info(f"Successfully updated field '{field}' for URL: {url}")

    def insert_url(self, record: Dict[str, Any]) -> None:
        """
        Insert a URL record into the database.

        The record should include:
          - 'url'
          - 'domain_name'
          - 'source'
          - 'content'
          - 'actual_incident'
          - 'accessible' (1 for accessible, 0 for not accessible)

        Raises:
            KeyError: If required fields are missing.
            DatabaseError: If insertion fails.
        """
        try:
            url_record = URLRecord(
                url=record["url"],
                domain_name=record["domain_name"],
                source=record["source"],
                extracted_date=datetime.now().isoformat(),
                actual_incident=record["actual_incident"]
            )
        except KeyError as e:
            error_msg = f"Missing required field in record: {str(e)}"
            self.logger.error(error_msg)
            raise KeyError(error_msg)

        query = """
            INSERT OR IGNORE INTO urls
            (url, domain_name, source, extracted_date, actual_incident, accessible, content)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self._execute_query(query, (
                url_record.url,
                url_record.domain_name,
                url_record.source,
                url_record.extracted_date,
                url_record.actual_incident,
                record.get("accessible", 1),  # default to accessible if not provided
                record.get("content", None)
        )):
            self.logger.info(f"Successfully inserted URL: {url_record.url}")

    def update_content(self, url: str, content: str) -> None:
        """
        Update the content field for a specific URL.

        Args:
            url: The URL whose content to update.
            content: The new content.

        Raises:
            DatabaseError: If the update fails.
        """
        query = "UPDATE urls SET content = ? WHERE url = ?"
        with self._execute_query(query, (content, url)) as cursor:
            if cursor.rowcount == 0:
                self.logger.warning(f"No record found for URL: {url}")
            else:
                self.logger.info(f"Successfully updated content for URL: {url}")

    def get_url_by_id(self, url_id: int) -> Optional[URLRecord]:
        """
        Retrieve a URL record by its ID.

        Args:
            url_id: The URL record ID.

        Returns:
            URLRecord if found, else None.

        Raises:
            DatabaseError: If retrieval fails.
        """
        query = """
            SELECT id, url, extracted_date, content, domain_name, source,
                   author, actual_incident, published_date, title
            FROM urls
            WHERE id = ?
        """
        with self._execute_query(query, (url_id,)) as cursor:
            row = cursor.fetchone()
            if row:
                return URLRecord(
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
            return None

    def search_urls(self,
                    domain: Optional[str] = None,
                    source: Optional[str] = None,
                    date_from: Optional[Union[str, datetime]] = None,
                    date_to: Optional[Union[str, datetime]] = None,
                    limit: int = 100) -> List[URLRecord]:
        """
        Search URLs based on criteria.

        Args:
            domain: Domain filter.
            source: Source filter.
            date_from: Start date (ISO string or datetime).
            date_to: End date (ISO string or datetime).
            limit: Maximum records to return.

        Returns:
            A list of URLRecord objects.

        Raises:
            DatabaseError: If the search fails.
        """
        query_parts = ["SELECT * FROM urls WHERE 1=1"]
        params: List[Any] = []

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

        self.logger.debug(f"Executing search query: {query} with params: {params}")

        with self._execute_query(query, tuple(params)) as cursor:
            rows = cursor.fetchall()
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
                for row in rows
            ]

    def get_recent_urls(self, days: int = 7, limit: int = 50) -> List[URLRecord]:
        """
        Retrieve URLs extracted within a number of days.

        Args:
            days: Number of days to look back.
            limit: Maximum records to return.

        Returns:
            A list of recent URLRecord objects.
        """
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        return self.search_urls(date_from=date_from, limit=limit)

    def get_urls_by_domain(self, domain: str) -> List[URLRecord]:
        """
        Retrieve all URLs for a specific domain.

        Args:
            domain: The domain name.

        Returns:
            A list of URLRecord objects.
        """
        return self.search_urls(domain=domain)

    def insert_incident(self, url_id: int, incident: str) -> None:
        """
        Insert an incident record.

        Args:
            url_id: The associated URL record ID.
            incident: The incident details.

        Raises:
            DatabaseError: If insertion fails.
        """
        query = "INSERT INTO incidents (url_id, incident) VALUES (?, ?)"
        with self._execute_query(query, (url_id, incident)):
            self.logger.info(f"Inserted incident for URL ID {url_id}")

    def insert_suspect(self, url_id: int, suspect: str) -> None:
        """
        Insert a suspect record.

        Args:
            url_id: The associated URL record ID.
            suspect: The suspect name.

        Raises:
            DatabaseError: If insertion fails.
        """
        query = "INSERT INTO suspects (url_id, suspect) VALUES (?, ?)"
        with self._execute_query(query, (url_id, suspect)):
            self.logger.info(f"Inserted suspect for URL ID {url_id}")

    def get_victim_id(self, url_id: int, victim: str) -> Optional[int]:
        """
        Retrieve the victim_id for a given URL and victim name.

        Args:
            url_id (int): The ID of the URL record.
            victim (str): The name of the victim.

        Returns:
            Optional[int]: The ID of the victim if found, otherwise None.

        Raises:
            DatabaseError: If the query fails.
        """
        query = "SELECT id FROM victims WHERE url_id = ? AND victim = ?"
        with self._execute_query(query, (url_id, victim)) as cursor:
            row = cursor.fetchone()
            return row[0] if row else None

    def get_suspect_id(self, url_id: int, suspect: str) -> Optional[int]:
        """
        Retrieve the suspect_id for a given URL and suspect name.

        Args:
            url_id (int): The ID of the URL record.
            suspect (str): The name of the suspect.

        Returns:
            Optional[int]: The ID of the suspect if found, otherwise None.

        Raises:
            DatabaseError: If the query fails.
        """
        query = "SELECT id FROM suspects WHERE url_id = ? AND suspect = ?"
        with self._execute_query(query, (url_id, suspect)) as cursor:
            row = cursor.fetchone()
            return row[0] if row else None

    def insert_victim(self, url_id: int, victim: str) -> None:
        """
        Insert a victim record.

        Args:
            url_id: The associated URL record ID.
            victim: The victim name.

        Raises:
            DatabaseError: If insertion fails.
        """
        query = "INSERT INTO victims (url_id, victim) VALUES (?, ?)"
        with self._execute_query(query, (url_id, victim)):
            self.logger.info(f"Inserted victim for URL ID {url_id}")

    def insert_victim_form(self, url_id: int, victim_data: VictimFormResponse, victim_id: Optional[int] = None) -> None:
        """
        Insert a victim form record.

        Args:
            url_id: The URL record ID.
            victim_data: Data from the victim form.
            victim_id: (Optional) ID from the victims table to associate with.

        Raises:
            DatabaseError: If insertion fails.
        """
        query = """
            INSERT INTO victim_forms (
                url_id, victim_id, name, gender, date_of_birth, age, address_notes, phone_number,
                nationality, occupation, appearance, vehicle_description,
                vehicle_plate_number, destination, job_offered
            )
            VALUES (
                :url_id, :victim_id, :name, :gender, :date_of_birth, :age, :address_notes, :phone_number,
                :nationality, :occupation, :appearance, :vehicle_description,
                :vehicle_plate_number, :destination, :job_offered
            )
        """
        params = {
            "url_id": url_id,
            "victim_id": victim_id,
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
        }
        with self._execute_query(query, tuple(params.values())):
            self.logger.info(f"Inserted victim form for URL ID {url_id}")

    def insert_suspect_form(self, url_id: int, suspect_data: SuspectFormResponse, suspect_id: Optional[int] = None) -> None:
        """
        Insert a suspect form record.

        Args:
            url_id: The URL record ID.
            suspect_data: Data from the suspect form.
            suspect_id: (Optional) ID from the suspects table to associate with.

        Raises:
            DatabaseError: If insertion fails.
        """
        query = """
            INSERT INTO suspect_forms (
                url_id, suspect_id, name, gender, date_of_birth, age, address_notes, phone_number,
                nationality, occupation, role, appearance, vehicle_description,
                vehicle_plate_number, evidence, arrested_status, arrest_date,
                crimes_person_charged_with, willing_pv_names, suspect_in_police_custody,
                suspect_current_location, suspect_last_known_location, suspect_last_known_location_date
            )
            VALUES (
                :url_id, :suspect_id, :name, :gender, :date_of_birth, :age, :address_notes, :phone_number,
                :nationality, :occupation, :role, :appearance, :vehicle_description,
                :vehicle_plate_number, :evidence, :arrested_status, :arrest_date,
                :crimes_person_charged_with, :willing_pv_names, :suspect_in_police_custody,
                :suspect_current_location, :suspect_last_known_location, :suspect_last_known_location_date
            )
        """
        params = {
            "url_id": url_id,
            "suspect_id": suspect_id,
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
        }
        with self._execute_query(query, tuple(params.values())):
            self.logger.info(f"Inserted suspect form for URL ID {url_id}")

    def get_url_id(self, url: str) -> Optional[int]:
        """
        Retrieve the ID of a URL given the URL string.

        Args:
            url: The URL string.

        Returns:
            The URL's ID if found, else None.

        Raises:
            DatabaseError: If the query fails.
        """
        query = "SELECT id FROM urls WHERE url = ?"
        with self._execute_query(query, (url,)) as cursor:
            row = cursor.fetchone()
            return row[0] if row else None
