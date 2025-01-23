import logging
import os
import sqlite3
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Type definitions
@dataclass
class URLRecord:
    """Data class representing a URL record for database operations."""

    url: str
    domain_name: str
    source: str
    extracted_date: Optional[str] = None
    content: Optional[str] = None
    id: Optional[int] = None


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
        log_file = self.log_dir / "url_database.log"

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
                        source TEXT
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
            )

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO urls
                    (url, domain_name, source, extracted_date)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        url_record.url,
                        url_record.domain_name,
                        url_record.source,
                        url_record.extracted_date,
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
