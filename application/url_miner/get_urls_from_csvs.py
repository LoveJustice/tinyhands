import logging
from pathlib import Path
from typing import List, Set, Optional
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from functools import partial
import hashlib

logging.basicConfig(
    filename="get_urls.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

@dataclass
class URLProcessingResult:
    """Container for URL processing results and metadata."""
    source_file: str
    urls: Set[str]
    errors: List[str]
    row_count: int
    duplicate_count: int


def get_unique_urls_from_csvs(
        csv_directory: str | Path,
        url_column: str = 'url',
        worker_count: int = 4,
        chunk_size: int = 1000
) -> Optional[List[str]]:
    """
    Extract and deduplicate URLs from all CSV files in the specified directory.

    Uses parallel processing for large files and implements memory-efficient
    chunk processing. Includes comprehensive error handling and detailed logging.

    Args:
        csv_directory: Directory containing CSV files
        url_column: Name of the URL column in CSV files (default: 'url')
        worker_count: Number of parallel workers for processing (default: 4)
        chunk_size: Number of rows to process per chunk (default: 1000)

    Returns:
        Optional[List[str]]: Deduplicated list of URLs or None if critical failure

    Raises:
        ValueError: If csv_directory doesn't exist or contains no CSV files
    """
    logger = logging.getLogger(__name__)
    directory = Path(csv_directory)

    if not directory.exists():
        logger.error(f"Directory not found: {directory}")
        raise ValueError(f"Directory not found: {directory}")

    csv_files = list(directory.glob("*.csv"))
    if not csv_files:
        logger.error(f"No CSV files found in {directory}")
        raise ValueError(f"No CSV files found in {directory}")

    logger.info(f"Found {len(csv_files)} CSV files to process")

    # Initialize URL set with hash-based deduplication
    master_urls: Set[str] = set()
    processing_results: List[URLProcessingResult] = []

    def process_csv_file(file_path: Path) -> URLProcessingResult:
        """Process a single CSV file and return its URLs and metadata."""
        urls = set()
        errors = []
        row_count = 0
        initial_url_count = 0

        try:
            # Use chunked reading for memory efficiency
            for chunk in pd.read_csv(file_path, chunksize=chunk_size, usecols=[url_column]):
                chunk_urls = chunk[url_column].dropna().astype(str)

                # Normalize URLs
                chunk_urls = chunk_urls.str.strip().str.lower()

                initial_url_count += len(chunk_urls)
                urls.update(chunk_urls)
                row_count += len(chunk)

        except pd.errors.EmptyDataError:
            errors.append(f"Empty CSV file: {file_path}")
            logger.warning(f"Empty CSV file encountered: {file_path}")
        except KeyError:
            errors.append(f"URL column '{url_column}' not found in {file_path}")
            logger.error(f"Missing URL column in file: {file_path}")
        except Exception as e:
            errors.append(f"Error processing {file_path}: {str(e)}")
            logger.error(f"Failed to process {file_path}: {str(e)}", exc_info=True)

        return URLProcessingResult(
            source_file=str(file_path),
            urls=urls,
            errors=errors,
            row_count=row_count,
            duplicate_count=initial_url_count - len(urls)
        )

    try:
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            future_to_file = {
                executor.submit(process_csv_file, file_path): file_path
                for file_path in csv_files
            }

            for future in as_completed(future_to_file):
                result = future.result()
                processing_results.append(result)
                master_urls.update(result.urls)

                # Log processing results
                logger.info(
                    f"Processed {result.source_file}: "
                    f"{result.row_count} rows, "
                    f"{len(result.urls)} unique URLs, "
                    f"{result.duplicate_count} duplicates removed"
                )

                if result.errors:
                    for error in result.errors:
                        logger.warning(error)

        # Generate summary statistics
        total_rows = sum(r.row_count for r in processing_results)
        total_duplicates = sum(r.duplicate_count for r in processing_results)

        logger.info(
            f"Processing complete - "
            f"Total rows: {total_rows}, "
            f"Unique URLs: {len(master_urls)}, "
            f"Duplicates removed: {total_duplicates}"
        )

        # Convert to sorted list for consistent output
        return sorted(master_urls)

    except Exception as e:
        logger.critical(f"Critical error during URL extraction: {str(e)}", exc_info=True)
        return None


# Add this at the end of get_urls_from_csvs.py
if __name__ == "__main__":
    try:
        urls = get_unique_urls_from_csvs(
            csv_directory="csv",
            url_column="url",
            worker_count=4,
            chunk_size=1000
        )

        if urls:
            logger.info(f"Successfully extracted {len(urls)} unique URLs")
        else:
            logger.error("Failed to extract URLs")

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)