import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from libraries.neo4j_lib import execute_neo4j_query, get_all_comments
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()


SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
MASTER_SPREADSHEET_ID = os.getenv("MASTER_SPREADSHEET_ID")
SCOPES = [os.getenv("SCOPES")]
DB_PATH = os.getenv("DB_PATH")


CREDENTIALS = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
SERVICE = build("sheets", "v4", credentials=CREDENTIALS)


def get_sheet_id(sheet_name):
    # Get the spreadsheet details including all sheets' information
    spreadsheet_info = (
        SERVICE.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    )

    # Iterate over each sheet in the spreadsheet
    for sheet in spreadsheet_info.get("sheets", []):
        # Check if the title of the sheet matches the desired sheet name
        if sheet["properties"]["title"] == sheet_name:
            # Return the sheetId of the matching sheet
            return sheet["properties"]["sheetId"]

    # If no matching sheet is found, raise an error or handle accordingly
    raise ValueError(f"No sheet found with the name: {sheet_name}")


def clear_google_adverts(tab):
    # Specify the range to clear; in this case, the entire sheet tab
    range_name = f"{tab}!A:Z"  # You can adjust this to clear a specific range or use '{tab}' to clear the whole sheet

    # Use the clear method to clear all data from the specified range
    result = (
        SERVICE.spreadsheets()
        .values()
        .clear(spreadsheetId=SPREADSHEET_ID, range=range_name, body={})
        .execute()
    )

    print("Sheet cleared successfully.")


# Note: get_sheet_id(tab) needs to be implemented or replaced with actual sheet ID if known.


def get_neo4j_adverts():
    parameters = {}
    query = f"""MATCH (posting:Posting)
        WHERE posting.text IS NOT NULL AND posting.post_id IS NOT NULL
        RETURN posting.post_id AS post_id, posting.post_url AS post_url, posting.text as advert;
        """
    # st.write(parameters)

    result = execute_neo4j_query(query, parameters)
    return pd.DataFrame(result)


def get_neo4j_groups():
    parameters = {}
    query = f"""MATCH (group:Group)
        RETURN group.name AS name, group.url as group_url, group.group_id as group_id;
        """
    # st.write(parameters)

    result = execute_neo4j_query(query, parameters)
    return pd.DataFrame(result)


def get_google_content(tab) -> pd.DataFrame:
    range_name = f"{tab}!A:J"  # Adjust the range as needed
    result = (
        SERVICE.spreadsheets()
        .values()
        .get(spreadsheetId=MASTER_SPREADSHEET_ID, range=range_name)
        .execute()
    )
    values = result.get("values", [])
    if not values:
        print("No data found.")
        return pd.DataFrame()
    else:
        df = pd.DataFrame(values[1:], columns=values[0])
        return df


def get_google_adverts(tab):
    range_name = f"{tab}!A:Z"  # Adjust the range as needed
    result = (
        SERVICE.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=range_name)
        .execute()
    )
    values = result.get("values", [])
    if not values:
        print("No data found.")
        return pd.DataFrame()
    else:
        df = pd.DataFrame(values[1:], columns=values[0])
        return df


def write_sheet(tab, data):
    """
    Appends data to a specific tab in a Google Sheet, ensuring that the header is included only once.

    Args:
    tab (str): The name of the sheet tab where data should be appended.
    data (pd.DataFrame): The DataFrame containing the data to append.

    Returns:
    dict: The response from the Google Sheets API after the append operation.
    """
    if data.empty:
        print("No data to write.")
        return {}

    # Check if the sheet is empty to decide whether to include headers
    range_name = f"{tab}!A1:Z"  # Assuming no more than 26 columns
    sheet_data = (
        SERVICE.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=range_name)
        .execute()
    )

    values = data.values.tolist()

    if "values" not in sheet_data:  # This means the sheet is empty
        # Include headers if the sheet is empty
        values.insert(0, data.columns.tolist())

    # Define the range where data should start being written
    range_name = f"{tab}!A1"  # This will automatically adjust to the next available row

    # Prepare the request body with the data
    body = {
        "values": values,
        "majorDimension": "ROWS",  # Ensures data is treated as rows
    }

    # Append the data to the specified range in the sheet
    try:
        response = (
            SERVICE.spreadsheets()
            .values()
            .append(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption="USER_ENTERED",  # Allows for formula parsing and formatting
                insertDataOption="INSERT_ROWS",  # Ensures new data rows are inserted
                body=body,
            )
            .execute()
        )
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


def get_new_data(google_adverts, neo4j_adverts):
    # Check if the DataFrame from neo4j is not empty
    if not neo4j_adverts.empty:
        # Concatenate the two DataFrames and find duplicates based on the 'post_id' column
        # `keep=False` marks all duplicates as True, so dropping these will leave only unique rows in google_adverts
        new_adverts = pd.concat([google_adverts, neo4j_adverts]).drop_duplicates(
            subset="post_url", keep=False
        )
        return new_adverts
    else:
        # If neo4j_adverts is empty, all google_adverts are considered new
        print("No new records to add.")
        return pd.DataFrame()


def append_new_adverts(tab, existing_adverts, new_adverts):
    values = new_adverts.values.tolist()
    range_name = (
        f"{tab}!A{len(existing_adverts) + 2}"  # Start appending after existing data
    )

    body = {"values": values}
    request = (
        SERVICE.spreadsheets()
        .values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption="RAW",
            body=body,
            insertDataOption="INSERT_ROWS",
        )
    )
    return request.execute()


def get_sheet_details():
    # This function will return the basic details of the spreadsheet,
    # including its sheets with their IDs
    response = SERVICE.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    return response


def update_cell_format(tab, data):
    request_body = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": get_sheet_id(tab),
                        "startRowIndex": 0,
                        "endRowIndex": data.shape[0],  # Update this as needed
                        "startColumnIndex": 0,
                        "endColumnIndex": data.shape[1],  # Update this as needed
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 0.8, "green": 0.8, "blue": 0.8},
                            "textFormat": {
                                "fontSize": 10,
                                "bold": False,
                                "foregroundColor": {"red": 0, "green": 0, "blue": 0},
                            },
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat)",
                }
            }
        ]
    }
    result = (
        SERVICE.spreadsheets()
        .batchUpdate(spreadsheetId=SPREADSHEET_ID, body=request_body)
        .execute()
    )
    print("Cell format updated successfully.")
    return result


def freeze_top_row(tab):
    sheet_id = get_sheet_id(
        tab
    )  # Ensure you have implemented this function to retrieve the sheetId
    request_body = {
        "requests": [
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {"frozenRowCount": 1},  # Freeze the top row
                    },
                    "fields": "gridProperties.frozenRowCount",
                }
            }
        ]
    }

    result = (
        SERVICE.spreadsheets()
        .batchUpdate(spreadsheetId=SPREADSHEET_ID, body=request_body)
        .execute()
    )

    print("Top row frozen successfully.")


def format_existing_adverts(sheet_name, existing_adverts):
    format_body = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": get_sheet_id(sheet_name),
                        "startRowIndex": 0,
                        "endRowIndex": len(existing_adverts),
                        "startColumnIndex": 0,
                        "endColumnIndex": existing_adverts.shape[
                            1
                        ],  # Assuming existing_adverts is a DataFrame
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 0.8, "green": 0.8, "blue": 0.8}
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor",
                }
            }
        ]
    }
    SERVICE.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=format_body
    ).execute()


def format_new_adverts(response, existing_adverts, new_adverts):
    format_body = {
        "requests": [
            # New data formatting (red)
            {
                "repeatCell": {
                    "range": {
                        "sheetId": response["updates"]["sheetId"],
                        "startRowIndex": len(existing_adverts),
                        "endRowIndex": len(existing_adverts) + len(new_adverts),
                        "startColumnIndex": 0,
                        "endColumnIndex": new_adverts.shape[
                            1
                        ],  # Assuming new_adverts is a DataFrame
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 1, "green": 0, "blue": 0}
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor",
                }
            },
        ]
    }
    SERVICE.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=format_body
    ).execute()


def main():
    if st.button("Show sheet details"):
        response = get_sheet_details()
        st.write(response)
        st.write(response["sheets"][0]["properties"]["sheetId"])
        st.write(get_sheet_id("Adverts"))

    if st.button("Compare adverts from GoogleSheet with existing Graph adverts"):
        google_adverts = get_google_adverts("Adverts")
        neo4j_adverts = get_neo4j_adverts()
        st.write("Google adverts:")
        st.dataframe(google_adverts)
        st.write("Neo4j adverts:")
        st.dataframe(neo4j_adverts)
        new_adverts = get_new_data(google_adverts, neo4j_adverts)
        st.write("New adverts to add:")
        st.dataframe(new_adverts)

    if st.button("Clear GoogleSheet"):
        clear_google_adverts("Adverts")
        google_adverts = get_google_adverts("Adverts")
        st.write("Google adverts:")
        st.dataframe(google_adverts)

    if st.button("Dump Graph Adverts to GoogleSheet"):
        tab = "Adverts"
        neo4j_adverts = get_neo4j_adverts()
        st.dataframe(neo4j_adverts)
        response = write_sheet(tab, neo4j_adverts)
        # format_existing_adverts(response, neo4j_adverts)
        update_cell_format(tab, neo4j_adverts)
        freeze_top_row(tab)

    if st.button("Write Graph Adverts to GoogleSheet"):
        google_adverts = get_google_adverts("Adverts")
        neo4j_adverts = get_neo4j_adverts()
        st.write("Google adverts:")
        st.dataframe(google_adverts)
        st.write("Neo4j adverts:")
        st.dataframe(neo4j_adverts)
        new_adverts = get_new_data(google_adverts, neo4j_adverts)
        st.write("New adverts to add:")
        st.dataframe(new_adverts)
        st.write(google_adverts.dtypes)
        st.write(new_adverts.dtypes)
        # st.dataframe(new_adverts.merge(google_adverts, on="post_id", how="inner"))
        st.write("New adverts: ")
        new_adverts = neo4j_adverts[
            ~neo4j_adverts["post_url"].isin(google_adverts["post_url"])
        ]
        st.dataframe(
            neo4j_adverts[~neo4j_adverts["post_url"].isin(google_adverts["post_url"])]
        )
        response = write_sheet("Adverts", new_adverts)
        st.write(response)
        # format_existing_adverts(response, google_adverts)
        # format_new_adverts(response, google_adverts, new_adverts)

    if st.button("Write Graph Groups to GoogleSheet"):
        neo4j_groups = get_neo4j_groups()
        neo4j_groups = neo4j_groups.sort_values(by="name")
        st.dataframe(neo4j_groups)
        response = write_sheet("Groups", neo4j_groups)
        freeze_top_row("Groups")

    # get_neo4j_groups():

    if st.button("Format existing adverts to GoogleSheet"):
        response = get_sheet_details()
        existing_adverts = get_google_adverts("Adverts")
        format_existing_adverts(response, existing_adverts)

    if st.button("Write new comments to 'Comments':"):
        response = (
            SERVICE.spreadsheets().get(spreadsheetId=MASTER_SPREADSHEET_ID).execute()
        )
        google_comments = get_google_content("Comments")
        st.dataframe(google_comments)
        st.write(google_comments.shape)
        neo4j_comments = get_all_comments()
        neo4j_comments = pd.DataFrame(neo4j_comments).sort_values(by="comment_id")
        st.write(neo4j_comments.shape)

        # st.dataframe(neo4j_comments)
        st.write("These comments will be appended to the 'Comments' sheet: ")
        data = neo4j_comments[
            ~neo4j_comments["comment_url"].isin(google_comments["comment_url"])
        ]
        st.dataframe(data)
        # response = write_sheet("Comments", data)
        # st.write(response)


if __name__ == "__main__":
    main()
