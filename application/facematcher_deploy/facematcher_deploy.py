import streamlit as st
import cv2
import streamlit_authenticator as stauth
import ast
import requests
import os
import psutil
from io import BytesIO
import numpy as np
import face_recognition
from urllib.parse import quote
from PIL import Image, ImageDraw
from typing import List, Optional
import psycopg2
import pandas as pd
import fitz
import io

# Constants
DEFAULT_IRF_PROMPT = "Select an IRF number..."
DEFAULT_PERSON_PROMPT = "Select a person..."

curl = st.secrets["face_matcher"]["curl"]
gender_mapping = {"M": "male", "F": "female"}

role_mapping = {
    "PVOT": "victim",
    "Broker": "broker",
    "Companion": "companion",
    "Suspect": "suspect",
}


def update_match_index(increment=True):
    """Update the match index by incrementing or decrementing it."""
    max_index = (
        st.session_state.data.shape[0] - 1
    )  # Assuming data is a pandas DataFrame

    # Initialize match_index to 0 if it doesn't exist
    if "match_index" not in st.session_state:
        st.session_state.match_index = 1

    if increment:
        # Increment match_index, but don't go past max_index
        st.session_state.match_index = min(st.session_state.match_index + 1, max_index)
    else:
        # Decrement match_index, but don't go below 0
        st.session_state.match_index = max(st.session_state.match_index - 1, 0)


def attrdict_to_dict(attrdict):
    dict_ = {}
    for key, value in attrdict.items():
        if isinstance(value, attrdict.__class__):
            dict_[key] = attrdict_to_dict(value)
        else:
            dict_[key] = value
    return dict_


class DB_Conn(object):
    """A class for establishing a connection with the database."""

    def __init__(self):
        """Initialize the connection with the database."""
        self._initialize_db_connection()

    def _initialize_db_connection(self):
        db_cred = st.secrets["postgresql"]
        self.conn = psycopg2.connect(**db_cred)
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_conn()

    def ex_query(self, select_query, parameters=None):
        """Execute query with parameters and return dataframe."""
        if parameters:
            self.cur.execute(select_query, parameters)
        else:
            self.cur.execute(select_query)

        if self.cur.description:
            colnames = [desc[0] for desc in self.cur.description]
            rows = self.cur.fetchall()
            return pd.DataFrame(rows, columns=colnames)
        else:
            return None

    def insert_query(self, insert_query, parameters=None):
        """Execute insert query with parameters."""
        if parameters:
            self.cur.execute(insert_query, parameters)
        else:
            self.cur.execute(insert_query)
        self.conn.commit()

    def close_conn(self):
        """Close the cursor and the connection."""
        self.cur.close()
        self.conn.close()


def system_monitor():
    process = psutil.Process(os.getpid())

    # get the memory usage in bytes
    mem = process.memory_info().rss / (1024**2)  # convert bytes to MB
    cpu = process.cpu_percent()

    st.text(f"Memory usage: {mem:.2f} MB")
    st.text(f"CPU usage: {cpu}%")


def face_landmarks_regions(image):
    face_locations = face_recognition.face_locations(image, model="hog")
    face_landmarks = face_recognition.face_landmarks(image, face_locations)
    face_location = face_locations[
        0
    ]  # Let's assume you're interested in the first detected face
    top, right, bottom, left = face_location
    face_region = image[top:bottom, left:right]
    return face_landmarks, face_region


def get_sharpness_quality(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    variance_of_laplacian = cv2.Laplacian(gray, cv2.CV_64F).var()

    if variance_of_laplacian < 50:
        return 1, "Blurry"
    elif variance_of_laplacian < 100:
        return 2, "Moderately Sharp"
    else:
        return 3, "Sharp"


def get_lighting_quality(face_region):
    mean = np.mean(face_region)
    std = np.std(face_region)

    if mean < 50 or mean > 205:
        return 1, "Poor Lighting"
    elif std < 50:
        return 1, "Flat Lighting"
    else:
        return 3, "Good Lighting"


def get_face_position_quality(face_landmarks):
    if not face_landmarks:
        return 0, "No Face Detected"

    # Just using the first face for this example
    landmarks = face_landmarks[0]

    left_eye = np.array(landmarks["left_eye"])
    right_eye = np.array(landmarks["right_eye"])

    left_eye_center = left_eye.mean(axis=0)
    right_eye_center = right_eye.mean(axis=0)

    dx = right_eye_center[0] - left_eye_center[0]
    dy = right_eye_center[1] - left_eye_center[1]

    angle = np.arctan2(dy, dx) * 180 / np.pi

    if abs(angle) > 15:
        return 1, "Tilted Face"
    elif abs(angle) > 5:
        return 2, "Slightly Tilted Face"
    else:
        return 3, "Frontal Face"


def get_occlusion_quality(face_landmarks):
    # Assume the face landmarks for eyes and nose are crucial
    landmarks = face_landmarks[0]
    if (
        not landmarks["left_eye"]
        or not landmarks["right_eye"]
        or not landmarks["nose_tip"]
    ):
        return 1, "Significant Occlusion"
    else:
        return 3, "Clear Face"


def get_resolution_quality(face_region):
    height, width = face_region.shape[:2]

    if height * width < 60 * 80:  # Roughly passport photo size
        return 1, "Low Resolution"
    elif height * width < 120 * 160:  # Roughly twice the passport size
        return 2, "Medium Resolution"
    else:
        return 3, "High Resolution"


def image_summary(image):
    face_landmarks, face_region = face_landmarks_regions(image)
    sharpness_quality, sharpness_quality_label = get_sharpness_quality(face_region)
    lighting_quality, lighting_quality_label = get_lighting_quality(face_region)
    face_position_quality, face_position_quality_label = get_face_position_quality(
        face_landmarks
    )
    occlusion_quality, occlusion_quality_label = get_occlusion_quality(face_landmarks)
    resolution_quality, resolution_quality_label = get_resolution_quality(face_region)

    narrative = f"The image has a {sharpness_quality_label} face. "

    if lighting_quality_label == "Flat Lighting":
        narrative += f"It appears somewhat uniformly lit, lacking depth due to {lighting_quality_label}. "
    else:
        narrative += f"It exhibits {lighting_quality_label}. "

    if face_position_quality_label == "Frontal Face":
        narrative += f"The subject is facing the camera directly, providing a {face_position_quality_label}. "
    elif face_position_quality_label == "Slightly Tilted Face":
        narrative += f"The subject's face is slightly tilted, but mostly frontal. "
    else:
        narrative += f"The face seems to be at an angle, showing a {face_position_quality_label}. "

    if occlusion_quality_label == "Clear Face":
        narrative += f"There aren't any significant obstructions, resulting in a {occlusion_quality_label}. "
    else:
        narrative += f"There are elements obscuring the facial features, indicating a {occlusion_quality_label}. "

    narrative += f"Lastly, we can describe it as a {resolution_quality_label} image."

    return narrative


# @st.cache(show_spinner=False)
# @st.cache_data(show_spinner=False, allow_output_mutation=True)


def get_image(photo_url, curl, max_size=(200, 200), timeout_duration=10):
    safe_url = curl["url"] + photo_url
    try:
        response = requests.get(
            safe_url, auth=(curl["email"], curl["password"]), timeout=timeout_duration
        )
        response.raise_for_status()
        bytesio_obj = BytesIO(response.content)

        # Load the image
        person_image = Image.open(bytesio_obj)

        # Resize the image
        person_image.thumbnail(max_size, Image.ANTIALIAS)

        # Convert to NumPy array for further processing
        person_image_array = np.array(person_image)

        # For face recognition, reload the image from the resized BytesIO object
        bytesio_obj_resized = BytesIO()
        person_image.save(bytesio_obj_resized, format="JPEG")
        bytesio_obj_resized.seek(0)
        person_np = face_recognition.load_image_file(bytesio_obj_resized)

        return person_image_array, person_np

    except requests.Timeout:
        print(
            f"Request timed out after {timeout_duration} seconds when trying to retrieve: {safe_url}"
        )
        return None, None
    except requests.RequestException as e:
        print(f"An error occurred while trying to retrieve: {safe_url}. Error: {e}")
        return None, None


def face_landmarks_regions(image):
    face_locations = face_recognition.face_locations(image, model="hog")
    face_landmarks = face_recognition.face_landmarks(image, face_locations)
    face_location = face_locations[0]
    top, right, bottom, left = face_location
    face_region = image[top:bottom, left:right]
    return face_landmarks, face_region


def display_face_and_rectangle(image_pil, image_np):
    try:
        # Get face landmarks and face region
        face_landmarks, face_region = face_landmarks_regions(image_np)

        # Ensure there are face landmarks detected
        if not face_landmarks:
            return

        # Extract bounding box of the detected face directly from face_landmarks_regions
        # face_location = face_recognition.face_locations(image_np, model="hog")[0]
        # top, right, bottom, left = face_location

        # Draw a red rectangle around the detected face on the original image
        # draw = ImageDraw.Draw(image_pil)

        # draw.rectangle(((left, top), (right, bottom)), outline="red", width=3)

    except Exception as e:
        return

    # Convert face region numpy array to PIL Image
    face_image_pil = Image.fromarray(face_region)

    return image_pil, face_image_pil


def get_distinct_column(
    column_name: str, countries: Optional[List[str]] = None
) -> List[str]:
    """
    Returns distinct values for the given column from the database.

    Args:
    - column_name: Name of the column for which distinct values are to be fetched.
    - countries: Optional list of countries to filter by.

    Returns:
    - List of distinct values for the column.
    """
    country_condition = ""
    if countries:
        country_placeholders = ", ".join(["%s"] * len(countries))
        country_condition = f"AND country.name IN ({country_placeholders})"

    sql_query = f"""
        SELECT DISTINCT
            person.{column_name} AS {column_name}
        FROM public.dataentry_irfcommon irfcommon
        INNER JOIN public.dataentry_intercepteecommon intercepteecommon ON intercepteecommon.interception_record_id = irfcommon.id
        INNER JOIN public.dataentry_borderstation borderstation ON borderstation.id = irfcommon.station_id
        INNER JOIN public.dataentry_country country ON country.id = borderstation.operating_country_id
        INNER JOIN public.dataentry_person person ON person.id = intercepteecommon.person_id
        INNER JOIN public.face_encodings face_encodings ON face_encodings.person_id = person.id
        WHERE person.photo IS NOT NULL
            AND face_encodings.face_encoding = 'encoded'
            AND person.photo <> ''
            {country_condition}
    """
    with DB_Conn() as dbc:
        result = dbc.ex_query(sql_query, countries if countries else [])
    return result[column_name].tolist()


def get_roles(countries):
    country_placeholders = ", ".join(["%s"] * len(countries))
    sql_query = f"""SELECT DISTINCT person.role AS role
    FROM public.dataentry_irfcommon irfcommon
    INNER JOIN public.dataentry_intercepteecommon intercepteecommon
        ON intercepteecommon.interception_record_id = irfcommon.id
    INNER JOIN public.dataentry_borderstation borderstation
        ON borderstation.id = irfcommon.station_id
    INNER JOIN public.dataentry_country country
        ON country.id = borderstation.operating_country_id
    INNER JOIN public.dataentry_person person
        ON person.id = intercepteecommon.person_id
    INNER JOIN public.face_encodings face_encodings
        ON face_encodings.person_id = person.id
    WHERE person.photo IS NOT NULL
        AND face_encodings.outcome = 'encoded'
        AND person.photo <> ''
        AND country.name IN ({country_placeholders})
        """
    with DB_Conn() as dbc:
        data = dbc.ex_query(sql_query, countries)
    return data["role"].tolist()


def get_genders(countries):
    country_placeholders = ", ".join(["%s"] * len(countries))
    sql_query = f"""SELECT DISTINCT person.gender AS gender
    FROM public.dataentry_irfcommon irfcommon
    INNER JOIN public.dataentry_intercepteecommon intercepteecommon
        ON intercepteecommon.interception_record_id = irfcommon.id
    INNER JOIN public.dataentry_borderstation borderstation
        ON borderstation.id = irfcommon.station_id
    INNER JOIN public.dataentry_country country
        ON country.id = borderstation.operating_country_id
    INNER JOIN public.dataentry_person person
        ON person.id = intercepteecommon.person_id
    INNER JOIN public.face_encodings face_encodings
        ON face_encodings.person_id = person.id
    WHERE person.photo IS NOT NULL
        AND face_encodings.outcome = 'encoded'
        AND person.photo <> ''
        AND country.name IN ({country_placeholders})
        """
    with DB_Conn() as dbc:
        data = dbc.ex_query(sql_query, countries)
    return data["gender"].tolist()


def get_countries():
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
INNER JOIN public.face_encodings face_encodings
    ON face_encodings.person_id = person.id
WHERE person.photo IS NOT NULL
    AND face_encodings.outcome = 'encoded'
    AND person.photo <> ''
    """
    with DB_Conn() as dbc:
        data = dbc.ex_query(sql_query)
    return data["country"].tolist()


@st.cache_data()
def get_data(countries, roles, genders):
    country_placeholders = ", ".join(["%s"] * len(countries))
    role_placeholders = ", ".join(["%s"] * len(roles))
    gender_placeholders = ", ".join(["%s"] * len(genders))

    sql_query = f"""
        SELECT intercepteecommon.person_id AS person_id,
               person.master_person_id AS master_person_id,
               country.name AS country,
               person.full_name AS full_name,
               person.role AS role,
               person.photo AS photo,
               person.gender AS gender,
               person.age AS age,
               face_encodings.face_encoding AS face_encoding,
            irfcommon.irf_number AS irf_number,
            irfcommon.date_time_entered_into_system AS date_time_entered_into_system
        FROM public.dataentry_irfcommon irfcommon
        INNER JOIN public.dataentry_intercepteecommon intercepteecommon ON intercepteecommon.interception_record_id = irfcommon.id
        INNER JOIN public.dataentry_borderstation borderstation ON borderstation.id = irfcommon.station_id
        INNER JOIN public.dataentry_country country ON country.id = borderstation.operating_country_id
        INNER JOIN public.dataentry_person person ON person.id = intercepteecommon.person_id
        INNER JOIN public.face_encodings face_encodings ON face_encodings.person_id = person.id
        WHERE person.photo IS NOT NULL AND face_encodings.outcome = 'encoded'
          AND person.photo <> ''
          AND country.name IN ({country_placeholders})
          AND person.role IN ({role_placeholders})
          AND person.gender IN ({gender_placeholders})
    """

    parameters = countries + roles + genders
    with DB_Conn() as dbc:
        data = dbc.ex_query(sql_query, parameters)
    return data


def convert_to_list_ast(face_encoding_str):
    try:
        return ast.literal_eval(face_encoding_str)
    except (ValueError, SyntaxError):
        return None


def attrdict_to_dict(attrdict):
    dict_ = {}
    for key, value in attrdict.items():
        if isinstance(value, attrdict.__class__):
            dict_[key] = attrdict_to_dict(value)
        else:
            dict_[key] = value
    return dict_


def initialize_session():
    try:
        # Initialize country options
        country_options = ["Select a country..."] + get_countries()
        role_options = get_roles(country_options)
        gender_options = get_genders(country_options)
        # gender_options = ["Select a country..."] + get_genders(country_options)

        st.session_state.setdefault("country_options", country_options)
        st.session_state.setdefault("role_options", role_options)
        st.session_state.setdefault("gender_options", gender_options)
        # Initialize other session state variables
        st.session_state.setdefault("initialized", True)
        st.session_state.setdefault("previous_country", None)
        st.session_state.setdefault("data", None)
        st.session_state.setdefault("match_index", 1)

        # Add other keys as necessary...

    except Exception as e:
        st.error(f"An error occurred during session initialization: {e}")


def convert_to_list(face_encoding_str):
    try:
        # If the data is in the format "1,2,3", split by comma and convert to list
        return [float(x) for x in face_encoding_str.split(",")]
    except (ValueError, TypeError):
        return None


def authenticate():
    toml_config = st.secrets["auth"]
    toml_config_dict = attrdict_to_dict(toml_config)
    authenticator = stauth.Authenticate(
        toml_config_dict["credentials"],
        toml_config_dict["cookie"]["name"],
        toml_config_dict["cookie"]["key"],
        toml_config_dict["cookie"]["expiry_days"],
        toml_config_dict["preauthorized"],
    )

    return authenticator, toml_config_dict


@st.cache_data(
    ttl=None,
    persist=True,
)
def get_photo_and_encoding(selected_person):
    """
    Retrieves the photo URL and face encoding for a given person.

    Args:
        selected_person (str/int): The ID of the person for whom to retrieve the photo and encoding.

    Returns:
        tuple: A tuple containing the photo_url and the face encoding.
              Returns (None, None) if the person is not found.
    """
    try:
        filtered_photos = st.session_state.data[
            st.session_state.data.person_id == int(selected_person)
        ].photo
        filtered_encoding = st.session_state.data[
            st.session_state.data.person_id == int(selected_person)
        ].face_encoding

        # Check if the person was found and data is available
        if not filtered_photos.empty and not filtered_encoding.empty:
            given_encoding = np.array(filtered_encoding.iloc[0])
            raw_url = filtered_photos.iloc[0]

            return raw_url, given_encoding
        else:
            st.warning(f"No data found for person ID: {selected_person}")
            return None, None

    except Exception as e:
        st.error(
            f"An error occurred while retrieving data for person ID {selected_person}: {e}"
        )
        return None, None


def get_closest_face_matches(encoding, limit):
    """
    Retrieves the closest face matches and their distances for a given face encoding.

    Args:
        encoding (array): The face encoding of the person to be matched.

    Returns:
        tuple: A tuple containing the IDs of the closest matches, the corresponding distances, and photo URLs.
              Returns (None, None, None) if no match is found or an error occurs.
    """
    try:
        # Calculate face distances
        face_distances = face_recognition.face_distance(
            st.session_state.known_encodings, encoding
        )

        # Find the indices of the matches sorted by distance
        sorted_indices = np.argsort(face_distances)

        # Sort known labels and distances using sorted_indices
        sorted_labels = [st.session_state.known_labels[i] for i in sorted_indices]
        sorted_distances = [face_distances[i] for i in sorted_indices]

        # Get photo URLs for sorted labels
        sorted_photo_urls = [
            st.session_state.data[
                st.session_state.data.person_id == int(label)
            ].photo.iloc[0]
            for label in sorted_labels
        ]

        upper_bound = min(limit, len(sorted_labels))
        return (
            sorted_labels[1:upper_bound],
            sorted_distances[1:upper_bound],
            sorted_photo_urls[1:upper_bound],
        )

    except Exception as e:
        st.error(f"An error occurred while finding the closest face matches: {e}")
        return None, None, None


def get_closest_face_match(encoding):
    """
    Retrieves the closest face match and its distance for a given face encoding.

    Args:
        encoding (array): The face encoding of the person to be matched.

    Returns:
        tuple: A tuple containing the ID of the closest match and the corresponding distance.
              Returns (None, None) if no match is found or an error occurs.
    """
    try:
        # Calculate face distances
        face_distances = face_recognition.face_distance(
            st.session_state.known_encodings, encoding
        )

        # Find the index of the closest match
        sorted_indices = np.argsort(face_distances)

        best_match_index = sorted_indices[st.session_state.match_index]

        # Determine if there's a match
        matches = face_recognition.compare_faces(
            st.session_state.known_encodings, encoding, tolerance=1.0
        )
        closest_match = (
            st.session_state.known_labels[best_match_index]
            if matches[best_match_index]
            else None
        )

        photo_url = st.session_state.data[
            st.session_state.data.person_id == int(closest_match)
        ].photo.iloc[0]
        return closest_match, face_distances[best_match_index], photo_url

    except Exception as e:
        st.error(f"An error occurred while finding the closest face match: {e}")
        return None, None, None


def get_similarity_description(face_distance):
    if face_distance <= 0.1:
        return "Appears identical"
    if face_distance <= 0.2:
        return "Almost identical"
    if face_distance <= 0.3:
        return "Highly Similar"
    elif face_distance <= 0.4:
        return "Very Similar"
    elif face_distance <= 0.5:
        return "Similar"
    elif face_distance <= 0.6:
        return "Moderately Similar"
    elif face_distance <= 0.7:
        return "Slightly Similar"

    else:
        return "Not Similar at all"


def load_data_for_countries(selected_countries, selected_roles, selected_genders):
    """Load data only if selected countries have changed.
    :param selected_roles:
    :param selected_genders:
    """
    # If selected countries changed, fetch data
    if (
        (st.session_state.get("previous_countries", []) != selected_countries)
        & (st.session_state.get("previous_roles", []) != selected_roles)
        & (st.session_state.get("previous_genders", []) != selected_genders)
    ):
        st.session_state.data = get_data(
            selected_countries, selected_roles, selected_genders
        )
        st.write(f"Loaded {len(st.session_state.data)} rows of data")
        st.session_state.previous_countries = selected_countries
        st.session_state.previous_roles = selected_roles
        st.session_state.previous_genders = selected_genders

        st.session_state.known_encodings = np.array(
            st.session_state.data["face_encoding"].tolist()
        )
        st.session_state.known_labels = st.session_state.data["person_id"].tolist()


def create_person_summary(person_id):
    try:
        results = st.session_state.data.loc[
            st.session_state.data["person_id"] == int(person_id), :
        ].to_dict(orient="records")

        if not results:
            return f"no data for {person_id}"

        for result in results:
            gender_description = gender_mapping.get(
                result["gender"], "with unknown gender"
            )
            role_description = role_mapping.get(result["role"], "with unknown role")
            narrative = f"{result['full_name']}, with person_id {result['person_id']} and IRF {result['irf_number']}, of {result['age']} years of age at interception, is a {gender_description} {role_description} from {result['country']} who was entered into the system on {result['date_time_entered_into_system']}."
        return narrative
    except Exception as e:
        return f"an error occurred retrieving data for {person_id}"


def record_vote(username, person_id1, person_id2, user_vote):
    insert_query = """
        INSERT INTO face_match_polls ("user_id", person_id1, person_id2, vote)
        VALUES (%s, %s, %s, %s);
    """

    # Convert numpy.int64 values to regular int values
    person_id1 = int(person_id1)
    person_id2 = int(person_id2)
    username = int(
        username
    )  # Assuming username is also a numpy.int64; if not, remove this line

    parameters = (username, person_id1, person_id2, user_vote)

    try:
        with DB_Conn() as dbc:
            dbc.insert_query(insert_query, parameters)
            dbc.conn.commit()

    except Exception as e:
        raise e  # Or handle this exception in a way that makes sense for your application

        # Optionally re-raise the exception if you want the error to propagate
        # raise


def get_user_id(toml_config_dict, username):
    email = toml_config_dict["credentials"]["usernames"][username]["email"]
    parameters = (email,)
    sql_query = """SELECT id FROM accounts_account WHERE email= %s"""
    with DB_Conn() as dbc:
        data = dbc.ex_query(sql_query, parameters)
    return data["id"].values[0]


def check_logout(authenticator):
    """Check if the user clicked the logout button."""
    if authenticator.logout("Logout", "main"):
        st.session_state["initialized"] = False
        st.session_state["previous_country"] = None


def on_increment():
    update_match_index()


def on_decrement():
    update_match_index(increment=False)


def set_match_index(sidebar):
    sidebar.title("Match Index Updater")

    # Create increment and decrement buttons with callbacks
    col1, col2 = sidebar.columns(2)
    increment_button = col1.button("Increment", on_click=on_increment)
    decrement_button = col2.button("Decrement", on_click=on_decrement)

    # Display the current match_index value
    sidebar.write(f"Current Match Index: {st.session_state.match_index}")


def select_countries():
    """Allow the user to select countries."""
    country_options = st.session_state.get("country_options", [])
    selected_countries = st.multiselect(
        "Select countries:",
        options=["All countries"] + country_options,
        help="Select one or multiple countries",
        default=[],
        placeholder="Select countries...",
    )
    return (
        country_options if "All countries" in selected_countries else selected_countries
    )


def select_roles(sidebar):
    """Allow the user to select roles from the sidebar."""
    role_options = st.session_state.get("role_options", [])
    return sidebar.multiselect(
        "Select roles:",
        options=role_options,
        help="Select one or multiple roles",
        default=role_options,
        placeholder="Select roles...",
    )


def select_genders(sidebar):
    """Allow the user to select genders from the sidebar."""
    gender_options = st.session_state.get("gender_options", [])
    return sidebar.multiselect(
        "Select genders:",
        options=gender_options,
        help="Select gender",
        default=gender_options,
        placeholder="Select gender...",
    )


def data_available():
    """Check if data is available in the session state."""
    return (
        "data" in st.session_state
        and st.session_state.data is not None
        and not st.session_state.data.empty
    )


def display_image_in_column(column, summary, image, image_np):
    """Display the image and its face rectangle in the given column.
    :param summary:
    """
    image_pil, face_image_pil = display_face_and_rectangle(image, image_np)
    result = display_face_and_rectangle(image, image_np)
    if result is None:
        st.error("Failed to get image details from display_face_and_rectangle.")
        return
    image_pil, face_image_pil = result
    column.image(image_pil, width=300)
    with column.expander("Person Summary"):
        column.write(summary)
    column.image(face_image_pil, width=300)
    image_summary_text = image_summary(image_np)
    with column.expander("Image Summary"):
        column.write(image_summary_text)


def display_selected_and_closest_match_images(
    given_encoding, selected_person, selected_person_image, user_id
):
    """Display the selected image and its closest match."""
    limit = st.slider(
        "Select number of face matches to retrieve:",
        min_value=1,
        max_value=20,
        value=5,
        step=1,
    )

    closest_matches, face_distances, closest_photo_urls = get_closest_face_matches(
        given_encoding, limit
    )
    for idx, (closest_match, face_distance, closest_photo_url) in enumerate(
        zip(closest_matches, face_distances, closest_photo_urls), 1
    ):
        # Write "Face pair {#}" in a larger text above each pairing
        st.markdown(
            f"<h3 style='text-align: center;'>Face pair {idx}</h3>",
            unsafe_allow_html=True,
        )
        selected_person_col, closest_matches_col = st.columns(2)

        selected_person_np = np.array(selected_person_image)
        selected_person_summary = create_person_summary(int(selected_person))
        display_image_in_column(
            selected_person_col,
            selected_person_summary,
            selected_person_image,
            selected_person_np,
        )

        safe_url = quote(closest_photo_url, safe=":/")
        match_person_image, match_person_np = get_image(
            safe_url, curl, (200, 200), timeout_duration=20
        )
        match_person_pil_image = Image.fromarray(match_person_image.astype("uint8"))

        closest_person_summary = create_person_summary(closest_match)
        display_image_in_column(
            closest_matches_col,
            closest_person_summary,
            match_person_pil_image,
            match_person_np,
        )

        similarity_description = get_similarity_description(face_distance)
        st.markdown(
            f"<p style='font-size: 20px; color: yellow; font-weight: bold;'>This match is from person_id: {closest_match}. "
            f"The faces appear to be {similarity_description}. There is a {(1-face_distance)*100:.0f}% match between the two faces.</p>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

    # handle_voting(user_id, selected_person, closest_match)


def handle_voting(user_id, selected_person, closest_match):
    """Allow the user to vote on the match quality and record the vote."""
    # Initialize 'voted' in session_state if not present
    st.session_state.setdefault("voted", False)

    vote_options = ["Yes", "No", "Maybe"]
    user_vote = st.radio("Do you think the faces are of the same person?", vote_options)

    # Button to confirm the vote
    if st.button("Submit Vote"):
        record_vote(user_id, selected_person, closest_match, user_vote)
        st.write(f"Vote recorded as: {user_vote}")


def handle_image_choice(choice):
    """Handle the user's image choice and return the encoding and image."""
    if choice == "Take a picture":
        return handle_take_picture_choice()
    elif choice == "Upload an image":
        return handle_upload_image_choice()
    elif choice == "Select from records":
        return handle_select_from_records_choice()
    return None, None, None, None


def authenticate_and_initialize_session():
    """Authenticate the user and initialize the session."""
    authenticator, toml_config_dict = authenticate()
    name, authentication_status, username = authenticator.login("Login", "main")

    if not authentication_status:
        return None, None

    user_id = get_user_id(toml_config_dict, username)
    initialize_session()
    st.write(f"Welcome *{name}*")

    return user_id, authenticator


def handle_sidebar(authenticator):
    """Manage sidebar functionalities."""
    sidebar = st.sidebar
    check_logout(authenticator)
    # set_match_index(sidebar)
    selected_countries = select_countries()
    selected_roles = select_roles(sidebar)
    selected_genders = select_genders(sidebar)
    return selected_countries, selected_roles, selected_genders


def handle_take_picture_choice():
    """Handle the 'Take a picture' choice and return the encoding and image."""
    img_file_buffer = st.camera_input("Take a picture")
    given_encoding, selected_person_image, selected_person_np = None, None, None
    selected_person = -999

    if img_file_buffer:
        try:
            selected_person_image = Image.open(img_file_buffer)

            selected_person_np = np.array(selected_person_image)

            face_locations = face_recognition.face_locations(
                selected_person_np, model="hog"
            )
            encodings = face_recognition.face_encodings(
                selected_person_np, known_face_locations=face_locations
            )

            if encodings:
                given_encoding = encodings[0]

            else:
                st.error("No face detected in the image.")
                return (
                    given_encoding,
                    selected_person,
                    selected_person_image,
                    selected_person_np,
                )

        except (IndexError, IOError) as e:
            st.error(f"Error processing the image: {str(e)}")
            return (
                given_encoding,
                selected_person,
                selected_person_image,
                selected_person_np,
            )

    return given_encoding, selected_person, selected_person_image, selected_person_np


def handle_upload_image_choice():
    """
    Handle the 'Upload an image' choice, process the image,
    and return its encoding along with other related information.
    """
    uploaded_file = st.file_uploader(
        "Upload your file here...", type=["png", "jpg", "jpeg", "pdf"]
    )

    # Initialize default return values
    given_encoding, selected_person_image, selected_person_np = None, None, None
    selected_person = -9999

    if uploaded_file:
        try:
            if uploaded_file.name.lower().endswith(".pdf"):
                # Open the PDF file
                st.write(uploaded_file.name.lower())
                pdf = fitz.open("pdf", uploaded_file.read())
                # Look for the first image in the PDF
                image_found = False
                for page_num in range(len(pdf)):
                    page = pdf[page_num]
                    for img_index, img in enumerate(page.get_images(full=True)):
                        xref = img[0]
                        base_image = pdf.extract_image(xref)
                        image_bytes = base_image["image"]
                        selected_person_image = Image.open(io.BytesIO(image_bytes))
                        selected_person_np = np.array(selected_person_image)
                        face_locations = face_recognition.face_locations(
                            selected_person_np, model="hog"
                        )
                        if face_locations:
                            given_encoding = face_recognition.face_encodings(
                                selected_person_np, known_face_locations=face_locations
                            )
                            image_found = True
                            break  # Only take the first image
                    if image_found:
                        break
                if not image_found:
                    st.error(
                        "No images found in the PDF. Please upload a PDF with images."
                    )
            else:
                # It's an image file, not a PDF
                selected_person_image = Image.open(uploaded_file).convert("RGB")
                selected_person_np = np.array(selected_person_image)
                face_locations = face_recognition.face_locations(
                    selected_person_np, model="hog"
                )
            # If an image is loaded, process it

            if selected_person_image:
                if face_locations:
                    encodings = face_recognition.face_encodings(
                        selected_person_np, known_face_locations=face_locations
                    )
                    if encodings:
                        given_encoding = encodings[0]
                else:
                    st.error(
                        "No face detected in the uploaded image. Please upload a different image."
                    )
        except Exception as e:  # Catch any other exceptions
            st.error(f"An error occurred: {e}")

    return given_encoding, selected_person, selected_person_image, selected_person_np


def get_irfs():
    """Retrieve unique person IDs from the available data."""
    if data_available():
        return [DEFAULT_IRF_PROMPT] + sorted(
            st.session_state.data["irf_number"].unique().astype(str).tolist()
        )
    return [DEFAULT_IRF_PROMPT]


def get_person_ids(irf_number):
    """Retrieve unique person IDs from the available data."""
    if data_available():
        return [DEFAULT_PERSON_PROMPT] + sorted(
            st.session_state.data.loc[
                st.session_state.data["irf_number"] == irf_number
            ]["person_id"]
            .unique()
            .astype(str)
            .tolist()
        )
    return [DEFAULT_PERSON_PROMPT]


def retrieve_photo_and_encoding(selected_person):
    """Retrieve photo URL and encoding for a given person."""
    selected_photo_url, given_encoding = get_photo_and_encoding(selected_person)
    if selected_photo_url and given_encoding is not None and given_encoding.size > 0:
        safe_url = quote(selected_photo_url, safe=":/")
        selected_person_image, selected_person_np = get_image(
            safe_url, curl, (200, 200), timeout_duration=20
        )
        selected_person_pil_image = Image.fromarray(
            selected_person_image.astype("uint8")
        )
        return given_encoding, selected_person_pil_image, selected_person_np
    return None, None, None


def handle_select_from_records_choice():
    """Handle the 'Select from records' choice and return the encoding and image."""
    irfs = get_irfs()
    selected_irf = st.selectbox("Select an IRF number:", irfs, key="selected_irf")

    # Initialize default return values
    (
        given_encoding,
        selected_person,
        selected_person_pil_image,
        selected_person_np,
    ) = (
        None,
        None,
        None,
        None,
    )

    if selected_irf != DEFAULT_IRF_PROMPT:
        try:
            person_ids = get_person_ids(selected_irf)
            selected_person = st.selectbox(
                "Select a person id:", person_ids, key="selected_person_id"
            )
            if selected_person != DEFAULT_PERSON_PROMPT:
                try:
                    (
                        given_encoding,
                        selected_person_pil_image,
                        selected_person_np,
                    ) = retrieve_photo_and_encoding(selected_person)
                except Exception as e:
                    st.error(
                        f"Error processing the selected_person {selected_person}: {str(e)}"
                    )

        except Exception as e:
            st.error(f"Error processing the IRF {selected_irf}: {str(e)}")

    return (
        given_encoding,
        selected_person,
        selected_person_pil_image,
        selected_person_np,
    )


def main():
    """Main function for the Streamlit app."""
    user_id, authenticator = authenticate_and_initialize_session()

    if user_id is None:
        return

    selected_countries, selected_roles, selected_genders = handle_sidebar(authenticator)

    load_data_for_countries(selected_countries, selected_roles, selected_genders)

    if not data_available():
        return

    # Main block functionalities
    choice = st.radio(
        "Choose an option:",
        ["Upload an image", "Select from records", "Take a picture"],
    )

    (
        given_encoding,
        selected_person,
        selected_person_image,
        selected_person_np,
    ) = handle_image_choice(choice)

    if given_encoding is not None and given_encoding.size > 0 and selected_person_image:
        display_selected_and_closest_match_images(
            given_encoding, selected_person, selected_person_image, user_id
        )


if __name__ == "__main__":
    main()
