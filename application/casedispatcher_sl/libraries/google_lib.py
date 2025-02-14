import io
import pickle
import re
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import psycopg2
import streamlit as st
import gspread
from gspread.worksheet import Worksheet
from oauth2client.client import OAuth2Credentials, OAuth2WebServerFlow, Storage
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

from .case_dispatcher_logging import setup_logger


# Global constants and logger
logger = setup_logger("google_logging", "cloud")
DB_CREDENTIALS = st.secrets["postgresql"]
CREDS_DICT = st.secrets["gs_cred"]
SCOPE = st.secrets["google"]["SCOPE"]
CLIENT_ID = st.secrets["google"]["CLIENT_ID"]
CLIENT_SECRET = st.secrets["google"]["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["google"]["REDIRECT_URI"]


def get_weights(weights_sheet: Worksheet, range_name: str) -> Dict[str, float]:
    """
    Extract weights from a specific named range in a worksheet.

    Args:
        weights_sheet: Worksheet containing weight configurations.
        range_name: Name of the range to extract weights from.

    Returns:
        Dictionary mapping weight names to their float values.

    Raises:
        ValueError: If the data format in the range is invalid.
    """
    result = weights_sheet.get_values(range_name)
    if not result or len(result) < 2:
        raise ValueError(f"Invalid data format in range {range_name}")

    # Assumes that the first row contains keys and the second row contains numeric values.
    return {result[0][i]: float(result[1][i]) for i in range(1, len(result[0]))}


def get_all_weights(
    credentials: OAuth2Credentials, workbook_name: str, range_names: List[str]
) -> Dict[str, float]:
    """
    Get all weight configurations from specified named ranges.

    Args:
        credentials: OAuth credentials for Google Sheets.
        workbook_name: Name of the workbook containing weights.
        range_names: List of named ranges to extract weights from.

    Returns:
        Dictionary mapping weight names to their float values.
    """
    gc = gspread.authorize(credentials)
    workbook = gc.open(workbook_name)
    weights_sheet = workbook.worksheet("weights")
    weights = {name: get_weights(weights_sheet, name) for name in range_names}
    # Flatten the nested dictionaries into one.
    return {k: v for d in weights.values() for k, v in d.items()}


def load_model_and_columns(
    drive_service: Any, model_name: str, cols_name: str, data_name: str
) -> Tuple[Any, Any, Any]:
    """
    Load model, columns, and data from Google Drive given file names.

    Args:
        drive_service: Authenticated Google Drive service instance.
        model_name: Name of the model file.
        cols_name: Name of the columns file.
        data_name: Name of the data file.

    Returns:
        Tuple containing (model, columns, data).
    """
    model_file_id = get_file_id(model_name, drive_service)
    model = load_from_cloud(drive_service, model_file_id)
    logger.info(f"Fetched {model_name} with file_id: {model_file_id}")

    cols_file_id = get_file_id(cols_name, drive_service)
    cols = load_from_cloud(drive_service, cols_file_id)

    data_file_id = get_file_id(data_name, drive_service)
    data = load_from_cloud(drive_service, data_file_id)

    return model, cols, data


def create_chart_metadata(chart_name: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create file metadata for a chart image to be uploaded to Google Drive.

    Args:
        chart_name: The name of the chart file (e.g., "sales_chart.png").
        parent_id: Optional ID of the folder to save the file in.

    Returns:
        File metadata dictionary.
    """
    file_metadata = {
        "name": chart_name,
        "mimeType": "image/png",  # MIME type for PNG images
    }
    if parent_id:
        file_metadata["parents"] = [parent_id]
    return file_metadata


def save_chart_to_cloud(
    chart: Any, drive_service: Any, file_metadata: Dict[str, Any], chart_format: str = "png"
) -> Optional[str]:
    """
    Save a matplotlib chart to Google Drive.

    Args:
        chart: The matplotlib figure to save.
        drive_service: Authenticated Google Drive service instance.
        file_metadata: Metadata for the file, including 'name'.
        chart_format: Format of the chart (e.g., 'png', 'pdf').

    Returns:
        The file ID of the uploaded chart.
    """
    # Serialize the chart into a bytes buffer.
    buffer = io.BytesIO()
    chart.savefig(buffer, format=chart_format)
    buffer.seek(0)

    mime_type = f"image/{chart_format}"
    file_name = file_metadata["name"]
    file_id = get_file_id(file_name, drive_service)
    media = MediaIoBaseUpload(buffer, mimetype=mime_type, resumable=True)

    if file_id:
        file = drive_service.files().update(
            fileId=file_id, body=file_metadata, media_body=media, fields="id"
        ).execute()
        logger.info(f"Updated file: {file_name} (ID: {file_id})")
    else:
        file = drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        logger.info(f"Created file: {file_name} (ID: {file.get('id')})")

    return file.get("id")


def get_matching_spreadsheets(credentials: Any, country: str) -> List[Any]:
    """
    Return a list of Google Spreadsheet objects whose titles start with 'Case Dispatcher'
    and include the specified country.

    Args:
        credentials: OAuth credentials for Google Sheets.
        country: Country string to filter spreadsheet titles.

    Returns:
        List of matching spreadsheet objects.
    """
    gc = gspread.authorize(credentials)
    all_spreadsheets = gc.openall()
    matching_spreadsheets = [
        sheet
        for sheet in all_spreadsheets
        if sheet.title.startswith("Case Dispatcher") and country in sheet.title
    ]
    return matching_spreadsheets


def make_file_bytes(model_to_save: Any) -> io.BytesIO:
    """
    Serialize an object to a BytesIO stream using pickle.

    Args:
        model_to_save: The model or object to serialize.

    Returns:
        A BytesIO stream containing the serialized object.
    """
    model_bytes = io.BytesIO()
    pickle.dump(model_to_save, model_bytes)
    model_bytes.seek(0)
    return model_bytes


def get_file_id(file_name: str, drive_service: Any) -> Optional[str]:
    """
    Retrieve the file ID for a given file name from Google Drive.

    Args:
        file_name: The name of the file to search for.
        drive_service: Authenticated Google Drive service.

    Returns:
        The file ID if found, otherwise None.
    """
    query = f"name='{file_name}'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get("files", [])

    if not items:
        logger.info("No files found.")
        return None
    elif len(items) > 1:
        logger.info(f"There are {len(items)} files with the name '{file_name}'. Using the first one.")

    file_id = items[0]["id"]
    logger.info(f"Found file: {items[0]['name']} (ID: {file_id})")
    return file_id


def load_from_cloud(drive_service: Any, file_id: str) -> Any:
    """
    Download and deserialize a file from Google Drive.

    Args:
        drive_service: Authenticated Google Drive service.
        file_id: ID of the file to download.

    Returns:
        The deserialized object.
    """
    request = drive_service.files().get_media(fileId=file_id)
    downloaded_bytes = io.BytesIO()
    downloader = MediaIoBaseDownload(downloaded_bytes, request)
    done = False

    while not done:
        status, done = downloader.next_chunk()
        logger.info("Download progress: {}%".format(int(status.progress() * 100)))

    downloaded_bytes.seek(0)
    return pickle.load(downloaded_bytes)


def load_data(drive_service: Any, filename: str) -> Any:
    """
    Load data from Google Drive given a filename.

    Args:
        drive_service: Authenticated Google Drive service.
        filename: Name of the file to load.

    Returns:
        The loaded data.
    """
    file_id = get_file_id(filename, drive_service)
    return load_from_cloud(drive_service, file_id)


def save_to_cloud(
    model_bytes: io.BytesIO, drive_service: Any, file_metadata: Dict[str, Any]
) -> Optional[str]:
    """
    Save a serialized model to Google Drive.

    Args:
        model_bytes: BytesIO stream containing the serialized model.
        drive_service: Authenticated Google Drive service.
        file_metadata: Metadata for the file.

    Returns:
        The file ID of the uploaded file.
    """
    file_name = file_metadata["name"]
    file_id = get_file_id(file_name, drive_service)
    media = MediaIoBaseUpload(model_bytes, mimetype="application/octet-stream", resumable=True)
    if file_id:
        file = drive_service.files().update(
            fileId=file_id, body=file_metadata, media_body=media, fields="id"
        ).execute()
        logger.info(f"Updated file: {file_name} (ID: {file_id})")
    else:
        file = drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        logger.info(f"Created file: {file_name} (ID: {file.get('id')})")
    return file.get("id")


def attrdict_to_dict(attrdict: Any) -> Dict[Any, Any]:
    """
    Recursively convert an object with an items() method to a standard dictionary.

    Args:
        attrdict: The object to convert.

    Returns:
        A dictionary with the same keys and values.
    """
    result = {}
    for key, value in attrdict.items():
        if hasattr(value, "items"):
            result[key] = attrdict_to_dict(value)
        else:
            result[key] = value
    return result


def get_gsheets(
    credentials: Any, workbook_name: str, sheet_names: List[str]
) -> Tuple[List[Worksheet], str, str]:
    """
    Retrieve specified worksheets from a Google workbook along with its URL and file ID.

    Args:
        credentials: OAuth credentials for Google Sheets.
        workbook_name: Name of the workbook.
        sheet_names: List of worksheet names to retrieve.

    Returns:
        A tuple containing:
          - List of worksheets.
          - The workbook URL.
          - The workbook file ID.
    """
    gc = gspread.authorize(credentials)
    workbook = gc.open(workbook_name)
    file_id = workbook.id
    file_url = workbook.url
    gsheets = [workbook.worksheet(name) for name in sheet_names]
    return gsheets, file_url, file_id


def get_auth_uri() -> OAuth2WebServerFlow:
    """
    Initialize the OAuth2WebServerFlow for Google authentication.

    Returns:
        An OAuth2WebServerFlow instance.
    """
    flow = OAuth2WebServerFlow(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope=SCOPE,
        redirect_uri=REDIRECT_URI,
    )
    return flow


def get_google_credentials(flow: OAuth2WebServerFlow, auth_code: str) -> OAuth2Credentials:
    """
    Exchange an auth code for Google credentials and save them locally.

    Args:
        flow: OAuth2WebServerFlow instance.
        auth_code: Authorization code obtained from the OAuth flow.

    Returns:
        OAuth2Credentials instance.
    """
    credentials = flow.step2_exchange(auth_code)
    with open("token.json", "w") as token_file:
        token_file.write(credentials.to_json())
    return credentials


def get_google_sheets_access(flow: OAuth2WebServerFlow, auth_code: str) -> gspread.Client:
    """
    Obtain a gspread client using Google credentials exchanged from an auth code.

    Args:
        flow: OAuth2WebServerFlow instance.
        auth_code: Authorization code obtained from the OAuth flow.

    Returns:
        gspread Client instance.
    """
    credentials = flow.step2_exchange(auth_code)
    with open("token.json", "w") as token_file:
        token_file.write(credentials.to_json())
    return gspread.authorize(credentials)


def get_or_create_spreadsheet(client: gspread.Client, spreadsheet_name: str) -> gspread.Spreadsheet:
    """
    Retrieve a spreadsheet by name if it exists, otherwise create a new one.

    Args:
        client: gspread Client instance.
        spreadsheet_name: Name of the spreadsheet.

    Returns:
        gspread Spreadsheet object.
    """
    spreadsheets = client.list_spreadsheet_files()
    for s in spreadsheets:
        if s["name"] == spreadsheet_name:
            logger.info(f"Spreadsheet '{spreadsheet_name}' already exists.")
            return client.open(spreadsheet_name)
    logger.info(f"Spreadsheet '{spreadsheet_name}' not found. Creating a new one.")
    return client.create(spreadsheet_name)


def get_or_create_worksheet(spreadsheet: gspread.Spreadsheet, worksheet_title: str) -> gspread.Worksheet:
    """
    Retrieve a worksheet by title from a spreadsheet, or create it if it doesn't exist.

    Args:
        spreadsheet: gspread Spreadsheet object.
        worksheet_title: Title of the worksheet.

    Returns:
        gspread Worksheet object.
    """
    try:
        worksheet = spreadsheet.worksheet(worksheet_title)
        logger.info(f"Worksheet '{worksheet_title}' already exists.")
    except gspread.exceptions.WorksheetNotFound:
        logger.error(f"Worksheet '{worksheet_title}' not found. Creating a new one.")
        worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows="100", cols="26")
    return worksheet


class GSheet:
    """
    Wrapper for a Google Worksheet to facilitate conversion to a pandas DataFrame.
    """

    def __init__(self, wrksht: Worksheet) -> None:
        self.wrksht = wrksht
        # Extract name using regex; note that this may be fragile.
        self.name = re.findall(r"'(.*?)'", str(wrksht))[0]
        values = self.wrksht.get_all_values()
        self.df = pd.DataFrame(values)
        if not self.df.empty:
            self.df.columns = self.df.iloc[0]
            self.df = self.df[1:].reset_index(drop=True)


def get_dfs(cdws: List[Worksheet]) -> Dict[str, pd.DataFrame]:
    """
    Convert a list of Google Worksheets to a dictionary of DataFrames.

    Args:
        cdws: List of gspread Worksheet objects.

    Returns:
        Dictionary mapping worksheet names to pandas DataFrames.
    """
    sheets = [GSheet(sheet) for sheet in cdws]
    return {sheet.name: sheet.df for sheet in sheets}


def get_sheet_id_by_name(
    spreadsheet_id: str, sheet_name: str, credentials: Credentials
) -> Optional[int]:
    """
    Retrieve the internal sheet ID for a given worksheet name in a Google Sheet.

    Args:
        spreadsheet_id: The spreadsheet ID.
        sheet_name: The title of the worksheet.
        credentials: Google credentials.

    Returns:
        The sheet ID as an integer if found, otherwise None.
    """
    try:
        service = build("sheets", "v4", credentials=credentials)
        response = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        for sheet in response.get("sheets", []):
            if sheet["properties"]["title"] == sheet_name:
                return sheet["properties"]["sheetId"]
        logger.info(f"Sheet '{sheet_name}' not found in spreadsheet '{spreadsheet_id}'")
        return None
    except HttpError as error:
        logger.error(f"An error occurred: {error}")
        return None


def get_spreadsheet_id_by_name(name: str, creds: Optional[Credentials] = None) -> Optional[str]:
    """
    Retrieve the spreadsheet ID from Google Drive by its name.

    Args:
        name: Name of the spreadsheet.
        creds: Google credentials (optional).

    Returns:
        Spreadsheet ID if found, otherwise None.
    """
    drive_service = build("drive", "v3", credentials=creds)
    results = drive_service.files().list(
        q=f"name='{name}' and mimeType='application/vnd.google-apps.spreadsheet'",
        fields="files(id, name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]
    logger.info(f"No spreadsheet found with name: {name}")
    return None


def share_sheet_with_user(
    sheet_id: str, email: str, role: str = "writer", creds: Optional[Credentials] = None
) -> None:
    """
    Share a Google Sheet with a specific user.

    Args:
        sheet_id: The ID of the spreadsheet to share.
        email: The email address of the user.
        role: The permission role to assign (e.g., 'writer').
        creds: Google credentials (optional).
    """
    try:
        drive_service = build("drive", "v3", credentials=creds)
        user_permission = {"type": "user", "role": role, "emailAddress": email}
        drive_service.permissions().create(
            fileId=sheet_id, body=user_permission, fields="id"
        ).execute()
        logger.info(f"Sheet shared with {email} as a {role}.")
    except HttpError as error:
        logger.error(f"An error occurred while sharing sheet: {error}")


def delete_worksheet(service: Any, worksheet_name: str) -> None:
    """
    Delete a worksheet (or file) from Google Drive by its name.

    Note: This function currently searches among Drive files and deletes the first matching file.
    If you intend to delete a worksheet within a spreadsheet, consider using the Sheets API.

    Args:
        service: Authenticated Google Drive service.
        worksheet_name: Name of the worksheet (or file) to delete.
    """
    results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get("files", [])
    for item in items:
        if item["name"] == worksheet_name:
            try:
                service.files().delete(fileId=item["id"]).execute()
                logger.info("Spreadsheet deleted.")
            except HttpError as error:
                logger.error(f"An error occurred while deleting worksheet: {error}")
            break


def get_drive_service() -> Optional[Any]:
    """
    Initialize and return the Google Drive service.

    Returns:
        Google Drive service instance, or None if authentication fails.
    """
    try:
        credentials = Credentials.from_service_account_info(st.secrets["gs_cred"], scopes=SCOPE)
        service = build("drive", "v3", credentials=credentials)
        return service
    except Exception as e:
        logger.error("Failed to authenticate with Google Drive: " + str(e))
        return None


def get_service_account() -> Optional[gspread.Client]:
    """
    Authenticate using the service account key and return a gspread client.

    Returns:
        gspread Client instance, or None if authentication fails.
    """
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gs_cred"], SCOPE)
        return gspread.authorize(credentials)
    except Exception as e:
        logger.error("Failed to authenticate with Google Sheets: " + str(e))
        return None


class DBConn:
    """
    Context manager for a PostgreSQL database connection.
    """

    def __init__(self) -> None:
        self._initialize_db_connection()

    def _initialize_db_connection(self) -> None:
        db_cred = st.secrets["postgresql"]
        self.conn = psycopg2.connect(**db_cred)
        self.cur = self.conn.cursor()

    def __enter__(self) -> "DBConn":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close_conn()

    def ex_query(self, select_query: str, parameters: Optional[tuple] = None) -> Optional[pd.DataFrame]:
        """
        Execute a SELECT query with optional parameters and return the results as a DataFrame.

        Args:
            select_query: SQL SELECT query.
            parameters: Optional tuple of query parameters.

        Returns:
            DataFrame containing the query results, or None if no results.
        """
        if parameters:
            self.cur.execute(select_query, parameters)
        else:
            self.cur.execute(select_query)

        if self.cur.description:
            colnames = [desc[0] for desc in self.cur.description]
            rows = self.cur.fetchall()
            return pd.DataFrame(rows, columns=colnames)
        return None

    def insert_query(self, insert_query: str, parameters: Optional[tuple] = None) -> None:
        """
        Execute an INSERT query with optional parameters.

        Args:
            insert_query: SQL INSERT query.
            parameters: Optional tuple of query parameters.
        """
        if parameters:
            self.cur.execute(insert_query, parameters)
        else:
            self.cur.execute(insert_query)
        self.conn.commit()

    def close_conn(self) -> None:
        """Close the database connection."""
        self.cur.close()
        self.conn.close()
