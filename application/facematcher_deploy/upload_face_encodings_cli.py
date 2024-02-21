import argparse
from threading import Semaphore
import requests
from PIL import Image
import face_recognition
import numpy as np
from libraries.google_lib import DB_Conn
from libraries.google_lib import setup_logger
from io import BytesIO
import streamlit as st
import psycopg2
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
import signal
from typing import Tuple, Union, Any

MAX_THREADS = 2
BATCH_SIZE = 50


# Initialize logger
logger = setup_logger("db_operations", "db_operations")
# logging.basicConfig(level=logging.DEBUG)


def get_countries():
    data_list = []
    sql_query = """SELECT DISTINCT country.name AS country
FROM public.dataentry_irfcommon irfcommon
INNER JOIN public.dataentry_intercepteecommon intercepteecommon
    ON intercepteecommon.interception_record_id = irfcommon.id
INNER JOIN public.dataentry_borderstation borderstation
    ON borderstation.id = irfcommon.station_id
INNER JOIN public.dataentry_country country
    ON country.id = borderstation.operating_country_id
INNER JOIN public.dataentry_person person
    ON person.id = intercepteecommon.person_id
WHERE person.photo IS NOT NULL
    AND person.photo <> ''
    """
    with DB_Conn() as dbc:
        data = dbc.ex_query(sql_query)
    data_list = data["country"].tolist()
    data_list.sort()
    return data_list


def get_photos_to_encode(country: str):
    sql_query = """
        SELECT intercepteecommon.person_id AS person_id,
            person.master_person_id AS master_person_id,
            country.name AS country,
            country.id AS operating_country_id,
            person.full_name AS full_name,
            person.photo AS photo,
            face_encodings.outcome AS outcome
        FROM public.dataentry_irfcommon irfcommon
        INNER JOIN public.dataentry_intercepteecommon intercepteecommon ON intercepteecommon.interception_record_id = irfcommon.id
        INNER JOIN public.dataentry_borderstation borderstation ON borderstation.id = irfcommon.station_id
        INNER JOIN public.dataentry_country country ON country.id = borderstation.operating_country_id
        INNER JOIN public.dataentry_person person ON person.id = intercepteecommon.person_id
        LEFT JOIN public.face_encodings face_encodings ON face_encodings.person_id = person.id
        WHERE person.photo IS NOT NULL
            AND person.photo <> ''
            AND country.name = %(country)s
            AND (face_encodings.person_id IS NULL);
    """

    parameters = {"country": country}

    with DB_Conn() as dbc:
        photos_to_process = dbc.ex_query(sql_query, parameters)

    return photos_to_process


def build_url(row: dict, curl: dict) -> str:
    """Constructs the URL for the image."""
    url = curl["url"] + row["photo"]
    return quote(url, safe=":/")


def fetch_image(row: dict, curl: dict) -> Tuple[Union[BytesIO, None], str]:
    """
    Fetches the image from a given URL.

    Parameters:
    - row: Dictionary containing photo information.
    - curl: Dictionary containing URL and authentication details.

    Returns:
    - BytesIO object of the image or None if there's an error.
    - String indicating the outcome ("Success", "Timeout", error message, "Invalid Image").
    """
    safe_url = build_url(row, curl)
    logger.info(f"Fetching image: {row['photo']}")

    try:
        response = requests.get(
            safe_url, auth=(curl["email"], curl["password"]), timeout=60
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout fetching image: {row['photo']}")
        return None, "Timeout"
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        logger.error(f"Error fetching image: {row['photo']}. Error: {error_message}")
        return None, error_message

    try:
        image_content = BytesIO(response.content)
        # Validate the image
        with Image.open(image_content):
            pass  # This just validates the image
        image_content.seek(0)
        logger.info(f"Successfully opened image: {row['photo']}")
        return image_content, "Success"
    except Exception as e:
        logger.error(f"Invalid image: {row['photo']}. Error: {e}")
        return None, "Invalid Image"


def process_photo(
    data: Tuple[int, dict], curl: dict
) -> Tuple[int, Union[Any, None], str]:
    """
    Processes the photo to generate facial encodings.

    Parameters:
    - data: Tuple containing the index and row data.
    - curl: Dictionary containing URL and authentication details.

    Returns:
    - person_id, encodings, outcome message.
    """
    _, row = data

    # Fetch image
    image, outcome_reason = fetch_image(row, curl)
    if not image:
        return row["person_id"], None, outcome_reason

    def handler(signum, frame):
        raise TimeoutError("Function call timed out")

    signal.signal(signal.SIGALRM, handler)
    try:
        # Face recognition
        face_recognition_image = face_recognition.load_image_file(image)

        try:
            # Set a timeout of 5 seconds (or whatever value you deem appropriate)
            signal.alarm(30)
            face_locations = face_recognition.face_locations(face_recognition_image)
            signal.alarm(0)  # Disable the alarm after the function call

        except TimeoutError:
            logger.error("Face recognition took too long and was timed out")
            return row["person_id"], None, "timed out"

        logger.info(f"Processing photo for person_id: {row['person_id']}")

        encodings = face_recognition.face_encodings(
            face_recognition_image, known_face_locations=face_locations
        )
        logger.info(f"Successfully processed photo for person_id: {row['person_id']}")
        # Determine outcome based on encodings
        if encodings:
            return row["person_id"], encodings[0], "encoded"
        else:
            return row["person_id"], None, "No face found"

    except Exception as e:
        logger.error(
            f"Error processing photo for person_id: {row['person_id']}. Error: {e}"
        )
        return row["person_id"], None, f"Error: {e}"


def check_for_duplicates(data):
    """Check for duplicates in the provided data based on person_id."""
    duplicates = data[data.duplicated(["person_id"])]
    if not duplicates.empty:
        logger.warning(
            f"Found duplicate person_ids in the data to be processed: {duplicates['person_id'].tolist()}"
        )
    return duplicates


def insert_face_encodings(encodings_batch):
    """Insert or update face encodings into the database."""
    insert_sql = """
    INSERT INTO face_encodings (person_id, face_encoding, outcome)
    VALUES (%s, %s, %s)
    ON CONFLICT (person_id)
    DO UPDATE SET face_encoding = EXCLUDED.face_encoding, outcome = EXCLUDED.outcome;
    """

    for person_id, encoding, outcome in encodings_batch:
        try:
            if isinstance(encoding, np.ndarray):
                encoding_list = encoding.tolist()
            else:
                encoding_list = []

            parameters = (
                int(person_id),
                encoding_list,
                outcome,
            )

            # Logging the SQL statement and parameters for debugging
            logger.debug(f"Executing SQL: {insert_sql} with parameters: {parameters}")
            with DB_Conn() as dbc:
                dbc.insert_query(insert_sql, parameters)
            logger.info(
                f"Successfully inserted/updated face encoding for person_id: {person_id} with outcome {outcome}"
            )
        except psycopg2.errors.UniqueViolation as uv:
            logger.warning(
                f"Duplicate key violation for person_id: {person_id}. Record already exists. Detail: {uv.diag.message_primary}"
            )
        except psycopg2.DatabaseError as de:
            # This captures other database-related errors and logs their details
            logger.error(
                f"Database error for person_id: {person_id}. Error: {de.pgerror}. Code: {de.pgcode}. Detail: {de.diag.message_primary}"
            )
        except Exception as e:
            # General exception logging
            logger.info(
                f"Error with encoding: {encoding}, person_id: {person_id}, outcome: {outcome}"
            )
            logger.error(
                f"Error inserting/updating for person_id: {person_id}. Error: {str(e)}"
            )


# Note: This modified function, insert_face_encodings, accepts a list of encodings and processes each encoding in the list.


def insert_face_encoding(dbc, encoding):
    """Insert or update face encoding into the database."""
    if not isinstance(encoding, (tuple, list)) or len(encoding) != 2:
        logger.error(f"Invalid encoding data format: {encoding}")
        return

    insert_sql = """
    INSERT INTO face_encodings (person_id, face_encoding)
    VALUES (%s, %s)
    ON CONFLICT (person_id)
    DO UPDATE SET face_encoding = EXCLUDED.face_encoding;
    """
    parameters = (encoding[0], encoding[1])

    try:
        logger.info(f"Inserting/updating face encoding for person_id: {encoding[0]}")
        dbc.insert_query(insert_sql, parameters)
        logger.info(
            f"Successfully inserted/updated face encoding for person_id: {encoding[0]}"
        )
    except psycopg2.errors.UniqueViolation:
        logger.warning(
            f"Duplicate key violation for person_id: {encoding[0]}. Record already exists."
        )
    except Exception as e:
        logger.error(
            f"Error inserting/updating for person_id: {encoding[0]}. Error: {str(e)}"
        )


def process_encodings_and_insert(encodings_to_insert):
    """Process the list of encodings and insert them into the database."""
    with DB_Conn() as dbc:
        for encoding in encodings_to_insert:
            if encoding:  # Check if encoding is not None
                insert_face_encoding(dbc, encoding)


def process_all_photos_mt(photos, curl, batch_size=50):
    """Process photos in batches using multithreading and upload encodings after each batch."""
    semaphore = Semaphore(5)  # Limit the number of concurrent image fetches

    def process_chunk(chunk):
        encodings = []
        for _, row in chunk.iterrows():
            try:
                with semaphore:
                    encoding = process_photo((_, row), curl)
                    if encoding:
                        encodings.append(encoding)
            except Exception as e:
                logger.error(f"Error processing photo for row {row}. Error: {str(e)}")
        return encodings

    total_photos = len(photos)
    logger.info(f"Total photos to process: {total_photos}")
    all_encodings = []

    # Process photos in batches
    try:
        with DB_Conn() as dbc:
            logger.info(f"Processing photos in batches of {batch_size}...")
            for start in range(0, total_photos, batch_size):
                end = start + batch_size
                batch = photos.iloc[start:end]
                logger.info(f"Processing photos {start+1} to {end}...")

                # Divide the batch into smaller chunks for multithreading
                chunks = np.array_split(batch, MAX_THREADS)
                logger.info(f"Divided batch into {len(chunks)} chunks.")

                batch_encodings = []
                with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                    results = list(executor.map(process_chunk, chunks))
                    logger.info(f"Finished processing photos {start+1} to {end}.")

                logger.info(f"Combining results from all threads...")
                for encoding_list in results:
                    batch_encodings.extend(encoding_list)
                logger.info(
                    f"Finished combining results. Total encodings: {len(batch_encodings)}"
                )
                all_encodings.extend(batch_encodings)

            # Upload all the encodings at once (or in larger batches if needed)
            logger.info("Uploading encodings...")
            insert_face_encodings(all_encodings)
            logger.info("Successfully uploaded all encodings.")
    except Exception as e:
        logger.error(f"Error in process_all_photos: {str(e)}")

    return all_encodings


def process_all_photos(photos, curl, batch_size=50):
    """Process photos in batches without using multithreading and upload encodings after each batch."""

    def process_single_photo(row):
        try:
            return process_photo((_, row), curl)
        except Exception as e:
            logger.error(f"Error processing photo for row {row}. Error: {str(e)}")
            return None

    total_photos = len(photos)
    logger.info(
        f"Starting processing of {total_photos} photos without multithreading..."
    )
    all_encodings = []

    # Process photos in batches
    try:
        with DB_Conn() as dbc:
            for start in range(0, total_photos, batch_size):
                end = start + batch_size
                batch = photos.iloc[start:end]
                logger.info(f"Processing photos {start+1} to {end}...")

                batch_encodings = []
                for _, row in batch.iterrows():
                    encoding = process_single_photo(row)
                    if encoding:
                        batch_encodings.append(encoding)
                logger.info(
                    f"Finished processing photos {start+1} to {end}. Total encodings: {len(batch_encodings)}"
                )

                all_encodings.extend(batch_encodings)

            # Upload all the encodings at once (or in larger batches if needed)
            logger.info("Uploading encodings...")
            insert_face_encodings(all_encodings)
            logger.info("Successfully uploaded all encodings.")
    except Exception as e:
        logger.info(f"Error in process_all_photos: {str(e)}")
        logger.error(f"Error in : {str(e)}")

    logger.info(
        f"Finished processing of {total_photos} photosprocess_all_photos_nomt without multithreading. Total encodings: {len(all_encodings)}"
    )
    return all_encodings


def process_all_photos_refactored(photos, curl, batch_size=50):
    """Process photos in batches using multithreading and upload encodings after each batch."""

    # Worker function to process a chunk of photos within a batch using multithreading

    def process_chunk(chunk):
        encodings = []
        for _, row in chunk.iterrows():
            with semaphore:
                try:
                    encoding = process_photo((_, row), curl)
                    if encoding:
                        encodings.append(encoding)
                except Exception as e:
                    logger.error(f"Error processing photo: {str(e)}")
        return encodings

    total_photos = len(photos)
    all_encodings = []
    logger.info(f"Total photos to process: {total_photos}")
    # Process photos in batcheswwith
    with DB_Conn() as dbc:
        logger.info(f"Processing photos in batches of {batch_size}...")
        for start in range(0, total_photos, batch_size):
            end = start + batch_size
            batch = photos.iloc[start:end]
            logger.info(f"Processing photos {start+1} to {end}...")
            # Divide the batch into smaller chunks for multithreading
            chunks = np.array_split(batch, MAX_THREADS)

            batch_encodings = []
            with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                results = list(executor.map(process_chunk, chunks))
                logger.info(f"Finished processing photos {start+1} to {end}.")

            # Combine results from all threads within the batch
            for encoding_list in results:
                batch_encodings.extend(encoding_list)

            # Upload the encodings from the batch
            try:
                logger.info(f"Uploading encodings for photos {start+1} to {end}...")
                insert_face_encodings(batch_encodings)
                logger.info(
                    f"Successfully uploaded encodings for photos {start+1} to {end}."
                )
                all_encodings.extend(batch_encodings)
            except Exception as e:
                logger.error(
                    f"Failed to upload encodings for photos {start+1} to {end}. Error: {str(e)}"
                )
                # Continue with the next batch.
                # Optionally, you could add a retry mechanism.

    return all_encodings


# Note: This implementation assumes the refactored_process_photo function, logger object, and MAX_THREADS are available in the script.


def main(country):
    logger.info(f"Starting processing photos for country: {country}")
    logger.info(f"Using {MAX_THREADS} threads.")
    logger.info(f"Using batch size of {BATCH_SIZE}.")

    logger.info("Established connection to the database.")
    photos_to_encode = get_photos_to_encode(country)
    logger.info(f"Found photo's to encode: {photos_to_encode.shape[0]}")

    # After fetching photos_to_encode, check for duplicates
    duplicates = check_for_duplicates(photos_to_encode)
    if not duplicates.empty:
        logger.warning(
            f"Found duplicate person_ids in the data to be processed: {duplicates['person_id'].tolist()}"
        )

    curl = st.secrets["face_matcher"]["curl"]

    total_photos = photos_to_encode.shape[0]
    for start in range(0, total_photos, BATCH_SIZE):
        end = start + BATCH_SIZE
        batch = photos_to_encode.iloc[start:end]
        logger.info(f"Processing photos {start + 1} to {end}...")

        encodings_to_insert = process_all_photos(batch, curl, batch_size=BATCH_SIZE)
        # process_encodings_and_insert(encodings_to_insert)
        logger.info(f"Finished processing and inserting photos {start + 1} to {end}.")

    logger.info(f"Finished processing photos for country: {country}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate and insert face encodings into the database."
    )
    parser.add_argument(
        "country", type=str, help="The country for which to process photos."
    )
    args = parser.parse_args()

    if args.country == "all":
        countries = get_countries()
        for country in countries:
            main(country)
    else:
        main(args.country)
