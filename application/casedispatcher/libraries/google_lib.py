import re
import pandas as pd
import psycopg2
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from oauth2client.client import OAuth2WebServerFlow, Storage
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .case_dispatcher_logging import setup_logger
import pickle
import io
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from typing import Dict, List, Any
from oauth2client.client import OAuth2Credentials
from gspread.worksheet import Worksheet


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
        weights_sheet: Worksheet containing weight configurations
        range_name: Name of the range to extract weights from

    Returns:
        Dictionary mapping weight names to their float values
    """
    result = weights_sheet.get_values(range_name)
    if not result or len(result) < 2:
        raise ValueError(f"Invalid data format in range {range_name}")

    return {result[0][i]: float(result[1][i]) for i in range(1, len(result[0]))}


def get_all_weights(
    credentials: OAuth2Credentials, workbook_name: str, range_names: List[str]
) -> Dict[str, Dict[str, float]]:
    """
    Get all weight configurations from specified ranges.

    Args:
        credentials: OAuth credentials for Google Sheets
        workbook_name: Name of the workbook containing weights
        range_names: List of named ranges to extract weights from

    Returns:
        Nested dictionary mapping range names to their weight configurations
    """
    gc = gspread.authorize(credentials)
    workbook = gc.open(workbook_name)
    weights_sheet = workbook.worksheet("weights")
    weights = {name: get_weights(weights_sheet, name) for name in range_names}
    return {k: v for d in weights.values() for k, v in d.items()}


def load_model_and_columns(drive_service, model_name, cols_name, data_name):
    model_file_id = get_file_id(model_name, drive_service)
    model = load_from_cloud(drive_service, model_file_id)
    st.write(f"Fetch {model_name} with file_id: {model_file_id}")

    cols_file_id = get_file_id(cols_name, drive_service)
    cols = load_from_cloud(drive_service, cols_file_id)

    data_file_id = get_file_id(data_name, drive_service)
    data = load_from_cloud(drive_service, data_file_id)

    return model, cols, data


def create_chart_metadata(chart_name, parent_id=None):
    """
    Create file metadata for a chart image to be uploaded to Google Drive.

    Args:
        chart_name (str): The name of the chart file (e.g., "sales_chart.png").
        parent_id (str, optional): The ID of the folder to save the file in.

    Returns:
        dict: File metadata for the chart.
    """
    file_metadata = {
        "name": chart_name,
        "mimeType": "image/png",  # MIME type for PNG images
    }

    if parent_id:
        file_metadata["parents"] = [parent_id]

    return file_metadata


# Assuming other necessary Google Drive API setup is done elsewhere


def save_chart_to_cloud(chart, drive_service, file_metadata, chart_format="png"):
    """
    Save a matplotlib chart to Google Drive.

    Args:
        chart (matplotlib.figure.Figure): The chart to save.
        drive_service: Authenticated Google Drive service instance.
        file_metadata (dict): Metadata for the file, including 'name'.
        chart_format (str): Format of the chart ('png', 'pdf', etc.).

    Returns:
        The ID of the file on Google Drive.
    """
    # Serialize the chart to a bytes-like object
    buffer = io.BytesIO()
    chart.savefig(buffer, format=chart_format)
    buffer.seek(0)  # Rewind the buffer to the beginning

    # Set the correct MIME type
    mime_type = f"image/{chart_format}"

    # Upload logic as in the original save_to_cloud function
    file_name = file_metadata["name"]
    file_id = get_file_id(file_name, drive_service)  # Ensure this function is defined
    media = MediaIoBaseUpload(buffer, mimetype=mime_type, resumable=True)

    if file_id:
        file = (
            drive_service.files()
            .update(fileId=file_id, body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        print(f"Updated file: {file_name} (ID: {file_id})")
    else:
        file = (
            drive_service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        print(f"Created file: {file_name} (ID: {file.get('id')})")

    return file.get("id")


def get_matching_spreadsheets(credentials, country):
    """Return a list of Google Spreadsheet names that start with 'Case Dispatcher'
    and include the specified country in their name."""

    gc = gspread.authorize(credentials)
    all_spreadsheets = gc.openall()  # List all spreadsheets

    # Filter spreadsheets based on naming criteria
    matching_spreadsheets = [
        sheet
        for sheet in all_spreadsheets
        if sheet.title.startswith("Case Dispatcher") and country in sheet.title
    ]

    return matching_spreadsheets


def make_file_bytes(model_to_save):
    model_bytes = io.BytesIO()
    pickle.dump(model_to_save, model_bytes)
    model_bytes.seek(0)
    return model_bytes  # Reset the position to the start of the stream


def get_file_id(file_name, drive_service):
    query = f"name='{file_name}'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get("files", [])

    if not items:
        print("No files found.")
        return None
    elif len(items) > 1:
        print(f"There are {len(items)} files with the name '{file_name}'.")

    # If multiple files have the same name, this will take the first one
    file_id = items[0]["id"]
    print(f"Found file: {items[0]['name']} (ID: {file_id})")
    return file_id


def load_from_cloud(drive_service, file_id):
    request = drive_service.files().get_media(fileId=file_id)
    downloaded_bytes = io.BytesIO()
    downloader = MediaIoBaseDownload(downloaded_bytes, request)
    done = False

    while done is False:
        status, done = downloader.next_chunk()
        print("Download progress: {}%".format(int(status.progress() * 100)))

    downloaded_bytes.seek(0)  # Reset the position to the start of the stream
    return pickle.load(downloaded_bytes)


def load_data(drive_service, filename):
    file_id = get_file_id(filename, drive_service)
    data = load_from_cloud(drive_service, file_id)
    return data


def save_to_cloud(model_bytes, drive_service, file_metadata):
    # Serialize the model to a bytes-like object

    # file_metadata = {'name': f'CD4_rf_{country}.pkl'}
    file_name = file_metadata["name"]
    file_id = get_file_id(file_name, drive_service)
    media = MediaIoBaseUpload(
        model_bytes, mimetype="application/octet-stream", resumable=True
    )
    if file_id:
        file = (
            drive_service.files()
            .update(fileId=file_id, body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        print(f"Updated file: {file_name} (ID: {file_id})")
    else:
        file = (
            drive_service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        print(f"Created file: {file_name} (ID: {file.get('id')})")
    # print('File ID:', file.get('id'))
    return file.get("id")


def attrdict_to_dict(attrdict):
    dict_ = {}
    for key, value in attrdict.items():
        if isinstance(value, attrdict.__class__):
            dict_[key] = attrdict_to_dict(value)
        else:
            dict_[key] = value
    return dict_


def get_gsheets(credentials, workbook_name, sheet_names):
    """Return a list of Google worksheets along with the workbook's link and file ID."""
    gc = gspread.authorize(credentials)

    # Open the workbook
    workbook = gc.open(workbook_name)

    # Get the file ID and URL from the workbook
    file_id = workbook.id
    file_url = workbook.url

    # Get the worksheets
    gsheets = []
    for name in sheet_names:
        sht = workbook.worksheet(name)
        gsheets.append(sht)

    return gsheets, file_url, file_id


def get_auth_uri():
    flow = OAuth2WebServerFlow(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope=SCOPE,
        redirect_uri=REDIRECT_URI,
    )
    # flow.step1_get_authorize_url()
    return flow


def get_google_credentials(flow, auth_code):
    credentials = flow.step2_exchange(auth_code)

    # Save the credentials for future use
    with open("token.json", "w") as token_file:
        token_file.write(credentials.to_json())
    return credentials


def get_google_sheets_access(flow, auth_code):
    credentials = flow.step2_exchange(auth_code)

    # Save the credentials for future use
    with open("token.json", "w") as token_file:
        token_file.write(credentials.to_json())

    # Authorize gspread with these credentials
    client = gspread.authorize(credentials)
    return client


def get_or_create_spreadsheet(client, spreadsheet_name):
    """Gets a Google Spreadsheet if it exists, otherwise creates one."""

    # Get list of all spreadsheets
    spreadsheets = client.list_spreadsheet_files()

    # Check if spreadsheet exists
    for s in spreadsheets:
        if s["name"] == spreadsheet_name:
            logger.info(f"Spreadsheet '{spreadsheet_name}' already exists.")
            return client.open(spreadsheet_name)

    # If spreadsheet doesn't exist, create one
    logger.info(f"Spreadsheet '{spreadsheet_name}' not found. Creating a new one.")
    new_spreadsheet = client.create(spreadsheet_name)

    return new_spreadsheet


def get_or_create_worksheet(spreadsheet, worksheet_title):
    """Gets a Google Worksheet if it exists in the given spreadsheet, otherwise creates one."""

    # Try to get the worksheet
    try:
        worksheet = spreadsheet.worksheet(worksheet_title)
        logger.info(f"Worksheet '{worksheet_title}' already exists.")
    except gspread.exceptions.WorksheetNotFound:
        # If worksheet does not exist, create a new one
        logger.error(f"Worksheet '{worksheet_title}' not found. Creating a new one.")
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_title, rows="100", cols="26"
        )

    return worksheet


"""## Generate Narrative"""


class GSheet:
    """This is a class for Google Worksheets."""

    def __init__(self, wrksht):
        self.wrksht = wrksht
        self.name = re.findall(r"'(.*?)'", str(wrksht))[0]
        df = pd.DataFrame(self.wrksht.get_all_values())

        # Check if the dataframe is empty
        if not df.empty:
            df.columns = df.iloc[0]
            df.drop(0, inplace=True)

        self.df = df


def get_dfs(cdws):
    """Completes conversion of Google Sheets to Dataframes."""
    all_sheets = []
    for i in range(len(cdws)):
        sheet = GSheet(cdws[i])
        all_sheets.append(sheet)
    dfs = {sheet.name: sheet.df for sheet in all_sheets}
    return dfs


def get_sheet_id_by_name(sheet_id, sheet_name, credentials):
    try:
        service = build("sheets", "v4", credentials=credentials)
        response = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        for sheet in response["sheets"]:
            if sheet["properties"]["title"] == sheet_name:
                return sheet["properties"]["sheetId"]
        logger.info(f"Sheet '{sheet_name}' not found in the Google Sheet '{sheet_id}'")
        return None
    except HttpError as error:
        logger.error(f"An error occurred: {error}")
        return None


def get_spreadsheet_id_by_name(name, creds=None):
    drive_service = build("drive", "v3", credentials=creds)
    results = (
        drive_service.files()
        .list(
            q=f"name='{name}' and mimeType='application/vnd.google-apps.spreadsheet'",
            fields="files(id, name)",
            supportsAllDrives=True,  # to search across all drives
            includeItemsFromAllDrives=True,  # to include files from all drives
        )
        .execute()
    )
    files = results.get("files", [])
    if files:
        # If the file is found, return the first match's ID
        return files[0]["id"]
    else:
        logger.info(f"No spreadsheet found with name: {name}")
        return None


def share_sheet_with_user(sheet_id, email, role="writer", creds=None):
    try:
        drive_service = build("drive", "v3", credentials=creds)
        file = (
            drive_service.files().get(fileId=sheet_id, fields="permissions").execute()
        )
        user_permission = {"type": "user", "role": role, "emailAddress": email}
        command = drive_service.permissions().create(
            fileId=sheet_id, body=user_permission, fields="id"
        )
        command.execute()
        logger.info(f"Sheet shared with {email} as a {role}.")
    except HttpError as error:
        logger.error(f"An error occurred: {error}")
        return None


def delete_worksheet(service, worksheet_name):
    results = (
        service.files()
        .list(pageSize=10, fields="nextPageToken, files(id, name)")
        .execute()
    )
    items = results.get("files", [])

    # Look for the file that matches our target spreadsheet
    for item in items:
        if item["name"] == worksheet_name:
            try:
                service.files().delete(fileId=item["id"]).execute()
                logger.info("Spreadsheet deleted.")
            except HttpError as error:
                logger.error(f"An error occurred: {error}")
            break


def get_drive_service():
    credentials = Credentials.from_service_account_info(
        st.secrets["gs_cred"], scopes=SCOPE
    )
    try:
        service = build("drive", "v3", credentials=credentials)
        return service
    except Exception as e:
        logger.error("Failed to authenticate with Google Drive: " + str(e))
        return None


def get_service_account():
    """
    Authenticate using the JSON key file and return the gspread client.
    """
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["gs_cred"], SCOPE
        )
        return gspread.authorize(credentials)
    except Exception as e:
        logger.error("Failed to authenticate with Google Sheets: " + str(e))
        return None


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
