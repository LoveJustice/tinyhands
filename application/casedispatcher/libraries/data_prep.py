# data_prep.py
import streamlit as st
import pandas as pd
import re
import numpy as np
from copy import deepcopy

from fontTools.subset import subset

from .case_dispatcher_logging import setup_logger
from datetime import date
from typing import Optional, Dict, List, Tuple, Union, Any

logger = setup_logger("data_prep_logging", "data_prep_logging")


def extract_case_id(sf_number: str) -> Optional[str]:
    """
    Extracts the SF number group from a given SF number string.

    The SF number group consists of the first three characters followed by
    consecutive digits until a letter (A-Z or a-z) is encountered.

    Examples:
        - "ABC1234X" -> "ABC1234"
        - "XYZ12A34B" -> "XYZ12"
        - "DEF456" -> "DEF456"
        - "GH1A2B3C" -> "GH1"

    Args:
        sf_number (str): The input SF number string.

    Returns:
        Optional[str]: The extracted SF number group if the pattern matches;
                       otherwise, None.
    """
    if not isinstance(sf_number, str):
        return None

    pattern = r"^(.{3}\d+)(?=[A-Za-z]|$)"
    match = re.match(pattern, sf_number)
    if match:
        return match.group(1)
    return None


def do_audit(audit_series, description="audit"):
    if st.session_state["include_audit"] == "Yes":
        # audit = audit_series.isin([st.session_state['irf_audit_number']])
        audit = st.session_state["irf_audit_number"] in audit_series.values
        st.write(
            f"irf_audit_number = {st.session_state['irf_audit_number']} is in db_irf: {audit}, with description '{description}'"
        )


def add_country_stats(model_data, country_stats):
    # Simplify country replacement using `np.where`

    model_data["country"] = np.where(
        model_data["country"] == "India Network", "India", model_data["country"]
    )

    # Merge with country_stats and directly replace 'country' without creating a 'dummy_country'
    merged_data = model_data.merge(
        country_stats, left_on="country", right_on="Country", how="left"
    )

    # Drop the now redundant 'Country' column from country_stats
    merged_data.drop(columns=["Country"], inplace=True)

    # Convert 'IBR12' percentage strings to float
    merged_data["IBR12"] = merged_data["IBR12"].str.rstrip("%").astype(float) / 100
    return merged_data


def extract_role_series(role_series):
    default_value = "missing information"

    def clean_item(item):
        replacements = {
            "rapiSuspect": "suspect",
            "hosuspect": "suspect",
            "diver": "driver",
            "ST": "suspect",
            "st": "suspect",
            "PVOT": "victim",
            "pvot": "victim",
            "Suspect2": "suspect",
            "rapisuspect": "suspect",
            "hosuspect": "suspect",
            "masuspecter": "suspect",
            "boy friend": "boyfriend",
        }
        item = re.sub(r"\.$", "", item)
        return replacements.get(item, default_value if item == "none" else item)

    def process_series(series):
        series = series.fillna(default_value).replace("", default_value)
        series = series.str.lower().replace(
            {"\[": "", ", ": ";", "/": ";", " ;": ";"}, regex=True
        )
        series = series.str.split(";")
        series = series.apply(lambda lst: sorted(set(clean_item(item) for item in lst)))
        return series

    processed_series = process_series(role_series)

    roles_txt_series = processed_series.apply(";".join)

    # Flatten the list of lists into a single list and extract unique elements
    unique_elements = set(item for sublist in processed_series for item in sublist)

    return processed_series, roles_txt_series, unique_elements


def pre_proc_sus(suspects):
    """Generates suspect IDs and narratives."""
    # Create a new dataframe called 'soc_df' that only contains rows from the 'db_cif' dataframe where the 'role' column is not 'Complainant' or 'Witness'
    # soc_df = db_cif[(db_cif.role != "Complainant") & (db_cif.role != "Witness")]

    # Filter the 'soc_df' dataframe to only include rows where the 'pb_number' column is not null
    suspects = suspects[~suspects["sf_number"].isna()]

    # Convert the data type of the 'pb_number' column from float to integer
    # suspects["suspect_id"] = suspects["suspect_id"].astype(int)

    suspects["suspect_id"] = (
        suspects["sf_number"].str[:-1] + ".sus" + suspects["suspect_id"].map(str)
    )
    # Uncomment the following line to remove duplicate rows in the 'soc_df' dataframe based on the 'suspect_id' column
    # soc_df = soc_df.drop_duplicates(subset='suspect_id')

    # Call the 'generate_narrative()' function on the 'soc_df' dataframe and store the result in the 'soc_df' dataframe
    # soc_df = generate_narrative(soc_df)

    return suspects


def process_columns(column_series, default_value):
    """
    Process a given column series from a dataframe.

    Parameters:
    - column_series (pd.Series): The series to be processed.
    - default_value (str): The default value to replace missing or empty values.

    Returns:
    - new_cols (pd.DataFrame): Dataframe containing new columns to be concatenated with the original dataframe.
    - cols_above_threshold (list): List of column names that are above the threshold.
    """

    # Handle missing and empty values
    column_series = column_series.fillna(default_value).replace("", default_value)

    # Format the column values
    column_series = (
        column_series.str.lower()
        .str.replace(" ", "_")
        .str.replace("'", "")
        .str.replace(",", ";")
        .str.strip()
        .str.strip("_")
    )  # Strip leading and trailing underscores

    all_values = set()
    column_series.str.split(";").apply(all_values.update)
    all_values = {
        value.strip("_") for value in all_values if value.strip()
    }  # Ensure no leading/trailing underscores

    # Generate new columns

    new_cols = pd.DataFrame(
        {value: column_series.str.contains(re.escape(value)) for value in all_values}
    )

    threshold = 0.01 * len(column_series)
    cols_above_threshold = [
        col for col, col_sum in new_cols.sum().items() if col_sum > threshold
    ]
    cols_below_threshold = list(all_values - set(cols_above_threshold))

    # Add/update the default value column
    new_cols[default_value] = new_cols[cols_below_threshold].any(axis=1)
    new_cols.drop(columns=cols_below_threshold, inplace=True)

    return new_cols, cols_above_threshold


# @title
def generate_narrative(db_cif):
    """For cases that are missing a narrative, generate one from selected columns."""
    # without_cn = db_cif[db_cif['case_notes'] == '']
    without_cn = db_cif
    without_cn["narrative_broker_recruited"] = np.where(
        without_cn["recruited_broker"] == True, "They were recruited by a broker. ", ""
    )
    without_cn["narrative_recruited"] = np.where(
        without_cn["how_recruited_promised_job"] == True,
        "Recruited by job promise. ",
        "",
    )
    without_cn["narrative_recruited"] = np.where(
        without_cn["how_recruited_married"] == True,
        "Recruited by marriage. " + without_cn["narrative_recruited"],
        without_cn["narrative_recruited"],
    )
    without_cn["narrative_recruited"] = np.where(
        without_cn["how_recruited_promised_marriage"] == True,
        "Recruited by marriage promise. " + without_cn["narrative_recruited"],
        without_cn["narrative_recruited"],
    )
    without_cn["narrative_recruited"] = np.where(
        without_cn["how_recruited_at_work"] == True,
        "Recruited at work. " + without_cn["narrative_recruited"],
        without_cn["narrative_recruited"],
    )
    without_cn["narrative_recruited"] = np.where(
        without_cn["how_recruited_at_school"] == True,
        "Recruited at school. " + without_cn["narrative_recruited"],
        without_cn["narrative_recruited"],
    )
    without_cn["narrative_recruited"] = np.where(
        without_cn["how_recruited_job_ad"] == True,
        "Recruited through job ad. " + without_cn["narrative_recruited"],
        without_cn["narrative_recruited"],
    )
    without_cn["narrative_recruited"] = np.where(
        without_cn["how_recruited_broker_online"] == True,
        "Recruited online. " + without_cn["narrative_recruited"],
        without_cn["narrative_recruited"],
    )
    without_cn["narrative_recruited"] = np.where(
        without_cn["how_recruited_broker_approached"] == True,
        "Recruited by broker approaching them. " + without_cn["narrative_recruited"],
        without_cn["narrative_recruited"],
    )
    without_cn["narrative_recruited"] = np.where(
        without_cn["how_recruited_broker_approached"] == True,
        "Recruited by broker approaching them. " + without_cn["narrative_recruited"],
        without_cn["narrative_recruited"],
    )
    without_cn["narrative_recruited"] = np.where(
        without_cn["how_recruited_broker_through_friends"] == True,
        "Recruited through friends. " + without_cn["narrative_recruited"],
        without_cn["narrative_recruited"],
    )
    without_cn["narrative_recruited"] = np.where(
        without_cn["how_recruited_broker_through_family"] == True,
        "Recruited through family. " + without_cn["narrative_recruited"],
        without_cn["narrative_recruited"],
    )
    without_cn["narrative_travel_expenses_paid_themselves"] = np.where(
        without_cn["travel_expenses_paid_themselves"] == True,
        "They paid the travel expenses themselves. ",
        "",
    )
    without_cn["narrative_travel_expenses_paid_by_broker"] = np.where(
        without_cn["travel_expenses_paid_by_broker"] == True,
        "The broker paid the travel expenses. ",
        "",
    )
    without_cn["narrative_expected_earnings"] = np.where(
        without_cn["expected_earning"] != "",
        "Broker said they would be earning "
        + without_cn["expected_earning"]
        + " per month. ",
        "",
    )
    without_cn["narrative_purpose"] = np.where(
        without_cn["purpose_for_leaving_education"] == True,
        "Left home for education. ",
        "",
    )
    without_cn["narrative_purpose"] = np.where(
        without_cn["purpose_for_leaving_travel_tour"] == True,
        "Left home for travel or tour. ",
        without_cn["narrative_purpose"],
    )
    without_cn["narrative_purpose"] = np.where(
        without_cn["purpose_for_leaving_marriage"] == True,
        "Left home for marriage. ",
        without_cn["narrative_purpose"],
    )
    without_cn["narrative_purpose"] = np.where(
        without_cn["purpose_for_leaving_family"] == True,
        "Left home for family. ",
        without_cn["narrative_purpose"],
    )
    without_cn["narrative_purpose"] = np.where(
        without_cn["purpose_for_leaving_medical"] == True,
        "Left home for medical reasons. ",
        without_cn["narrative_purpose"],
    )
    without_cn["narrative_purpose"] = np.where(
        without_cn["purpose_for_leaving_job_hotel"] == True,
        "Left home for job at hotel. ",
        without_cn["narrative_purpose"],
    )
    without_cn["narrative_purpose"] = np.where(
        without_cn["purpose_for_leaving_job_household"] == True,
        "Left home for household job. ",
        without_cn["narrative_purpose"],
    )
    without_cn["narrative_destination"] = np.where(
        without_cn["planned_destination"] != "",
        "Planned destination: " + without_cn["planned_destination"] + " ",
        "",
    )
    without_cn["narrative_id"] = np.where(
        without_cn["id_made_no"] == True, "No ID made. ", ""
    )
    without_cn["narrative_id"] = np.where(
        without_cn["id_made_real"] == True, "Real ID made. ", without_cn["narrative_id"]
    )
    without_cn["narrative_id"] = np.where(
        without_cn["id_made_fake"] == True, "Fake ID made. ", without_cn["narrative_id"]
    )
    without_cn["narrative_id"] = np.where(
        without_cn["id_made_false_name"] == True,
        "ID with false name made. ",
        without_cn["narrative_id"],
    )
    without_cn["narrative_id"] = np.where(
        without_cn["id_made_other_false"] == True,
        "ID made with other false info. ",
        without_cn["narrative_id"],
    )
    without_cn["narrative_legal"] = np.where(
        without_cn["legal_action_taken"].str.contains("yes"), "Legal Case Filed. ", ""
    )
    without_cn["narrative_pv_believes"] = np.where(
        without_cn["pv_believes"].str.contains("Definitely", regex=False),
        "PV believes the suspect has definitely trafficked many. ",
        "",
    )
    without_cn["narrative_pv_believes"] = np.where(
        without_cn["pv_believes"].str.contains("some", regex=False),
        "PV believes the suspect has trafficked some. ",
        without_cn["narrative_pv_believes"],
    )
    without_cn["narrative_pv_believes"] = np.where(
        without_cn["pv_believes"].str.contains("Suspect", regex=False),
        "PV suspects they are a trafficker. ",
        without_cn["narrative_pv_believes"],
    )
    without_cn["narrative_pv_believes"] = np.where(
        without_cn["pv_believes"].str.contains("Don", regex=False),
        "PV does not believe the suspect is a trafficker. ",
        without_cn["narrative_pv_believes"],
    )
    without_cn["narrative"] = (
        without_cn["narrative_broker_recruited"].fillna("")
        + without_cn["narrative_recruited"].fillna("")
        + without_cn["narrative_travel_expenses_paid_themselves"].fillna("")
        + without_cn["narrative_travel_expenses_paid_by_broker"].fillna("")
        + without_cn["narrative_expected_earnings"].fillna("")
        + without_cn["narrative_purpose"].fillna("")
        + without_cn["narrative_destination"].fillna("")
        + without_cn["narrative_id"].fillna("")
        + without_cn["narrative_legal"].fillna("")
        + without_cn["narrative_pv_believes"].fillna("")
    )
    without_cn["case_notes"] = np.where(
        without_cn["case_notes"] == "",
        without_cn["narrative"],
        without_cn["case_notes"],
    )
    without_cn["case_notes"] = (
        without_cn["case_notes"].replace("nan", np.nan).fillna("")
    )
    without_cn = without_cn[
        without_cn.columns[~without_cn.columns.str.contains("narrative")]
    ]
    return without_cn


def pre_proc(db_cif):
    """Generates suspect IDs and narratives."""
    # Create a new dataframe called 'soc_df' that only contains rows from the 'db_cif' dataframe where the 'role' column is not 'Complainant' or 'Witness'
    soc_df = db_cif[(db_cif.role != "Complainant") & (db_cif.role != "Witness")]

    # Filter the 'soc_df' dataframe to only include rows where the 'pb_number' column is not null
    soc_df = soc_df[~soc_df["pb_number"].isna()]

    # Replace all '.' characters with an empty string in the 'cif_number' column and store the result in a new 'suspect_id' column
    soc_df["suspect_id"] = soc_df["cif_number"].str.replace(".", "")

    # Convert the data type of the 'pb_number' column from float to integer
    soc_df["pb_number"] = soc_df["pb_number"].astype(int)

    # Concatenate the 'suspect_id' column, '.PB', and the 'pb_number' column (converted to a string) and store the result in the 'suspect_id' column
    soc_df["suspect_id"] = (
        soc_df["suspect_id"].str[:-1] + ".PB" + soc_df["pb_number"].map(str)
    )

    # Uncomment the following line to remove duplicate rows in the 'soc_df' dataframe based on the 'suspect_id' column
    # soc_df = soc_df.drop_duplicates(subset='suspect_id')

    # Call the 'generate_narrative()' function on the 'soc_df' dataframe and store the result in the 'soc_df' dataframe
    soc_df = generate_narrative(soc_df)

    return soc_df


def organize_uganda_dest(soc_df):
    """Clean and organize desitnation data so it is ready for feature union."""
    # Replace all non-alphanumeric characters in the 'planned_destination' column with an empty string
    soc_df["planned_destination"] = soc_df["planned_destination"].str.replace(
        r"[^\w\s]+", ""
    )

    # Create a new column called 'destination_gulf' in the 'soc_df' dataframe
    # The value of this column will depend on the value of the 'planned_destination' column
    # If the value of 'planned_destination' contains any of the following strings: 'Gulf', 'Kuwait', 'Dubai', 'UAE', 'Oman', 'Saudi', 'Iraq', 'Qatar', or 'Bahrain', then the value of 'destination_gulf' will be True
    # Otherwise, the value of 'destination_gulf' will be False
    soc_df["destination_gulf"] = np.where(
        soc_df["planned_destination"].str.contains(
            "Gulf|Kuwait|Dubai|UAE|Oman|Saudi|Iraq|Qatar|Bahrain"
        ),
        True,
        False,
    )

    # Create a list of destinations
    dest = ["Kampala", "Kyegegwa", "Nairobi", "Kenya"]

    # For each destination in the 'dest' list, create a new column in the 'soc_df' dataframe called 'destination_' + destination (e.g. 'destination_Kampala')
    # The value of this column will depend on the value of the 'planned_destination' column
    # If the value of 'planned_destination' contains the current destination, then the value of 'destination_' + destination will be True
    # Otherwise, the value of 'destination_' + destination will be False
    for d in dest:
        soc_df["destination_" + str(d)] = np.where(
            soc_df["planned_destination"].str.contains(d), True, False
        )

    # Uncomment the following two lines to fill null values in the 'pb_number' column with 0 and convert the data type of the 'pb_number' column from float to integer
    # soc_df.pb_number = soc_df.pb_number.fillna(0)
    # soc_df.pb_number = soc_df.pb_number.astype(int)

    return soc_df


def organize_dtypes(soc_df):
    """Assigns relevant data types to variables."""

    # Define a list of numerical features
    num_features = [
        "number_of_traffickers",
        "number_of_victims",
    ]

    # Define a list of boolean features by subtracting the numerical features and a list of non-boolean features from the full list of columns
    boolean_features = list(
        set(list(soc_df.columns))
        - set(num_features)
        - set(
            [
                "suspect_id",
                "interview_date",
                "case_notes",
                "case_id",
                "master_person_id",
                "sf_number",
                "person_id",
            ]
        )
    )

    # Convert the data type of the boolean features to boolean
    soc_df[boolean_features] = soc_df[boolean_features].astype(bool)

    # Fill null values in the numerical features with 0 and convert the data type to float
    logger.error(f"<<< data_prep line 367")
    soc_df[num_features] = soc_df[num_features].fillna(0).astype(float)
    logger.error(f">>> data_prep line 369")
    return soc_df


def remove_non_numeric(x):
    try:
        x = re.sub("[^0-9]", 0, x)
    except:
        x = 0
    return x


def engineer_features(soc_df):
    """Engineer features for selected destinations Person Box variables."""
    # soc_df = organize_uganda_dest(soc_df)

    soc_df["job_promised_amount"] = soc_df["job_promised_amount"].apply(
        lambda x: remove_non_numeric(x)
    )
    # soc_df['expected_earning'] = soc_df['expected_earning'].astype(int)

    soc_df["number_of_victims"] = np.where(
        soc_df["number_of_victims"].isna(), 1, soc_df["number_of_victims"]
    )

    soc_df = soc_df.drop(
        columns=[
            "arrested",
            "borderstation_id",
            "role",
            "where_going_destination",
            "station_name",
            "role",
            "full_name",
            "phone_contact",
        ]
    )

    soc_df = organize_dtypes(soc_df)

    soc_df = soc_df.loc[:, (soc_df != False).any(axis=0)]
    return soc_df


def en_features(soc_df):
    """Engineer features for selected destinations Person Box variables."""
    soc_df = organize_uganda_dest(soc_df)

    soc_df["job_promised_amount"] = soc_df["job_promised_amount"].apply(
        lambda x: remove_non_numeric(x)
    )
    # soc_df['expected_earning'] = soc_df['expected_earning'].astype(int)

    soc_df["number_of_victims"] = np.where(
        soc_df["number_of_victims"].isna(), 1, soc_df["number_of_victims"]
    )

    soc_df["pv_believes_definitely_trafficked_many"] = np.where(
        soc_df["pv_believes"].str.contains("Definitely", regex=False), True, False
    )
    soc_df["pv_believes_trafficked_some"] = np.where(
        soc_df["pv_believes"].str.contains("some", regex=False), True, False
    )
    soc_df["pv_believes_suspect_trafficker"] = np.where(
        soc_df["pv_believes"].str.contains("Suspect", regex=False), True, False
    )
    soc_df["pv_believes_not_a_trafficker"] = np.where(
        soc_df["pv_believes"].str.contains("Don", regex=False), True, False
    )

    soc_df = soc_df.drop(
        columns=[
            "arrested",
            "station_id",
            "cif_id",
            "pb_number",
            "role",
            "where_going_destination",
            "pv_believes",
            "legal_action_taken",
            "station_name",
        ]
    )

    soc_df = organize_dtypes(soc_df)

    soc_df = soc_df.loc[:, (soc_df != False).any(axis=0)]

    return soc_df


def set_vic_id(new_victims):
    if "victim_id" not in new_victims.columns:
        logger.error("'victim_id' column is missing after setting victim IDs.")

    new_victims = new_victims[
        ["vdf_number", "full_name", "phone_contact", "address_notes", "social_media"]
    ]
    new_victims.loc[:, "Victim_ID"] = new_victims["vdf_number"]
    replacements = {
        "Victim_ID": {
            r"(\.1|A$)": ".V1",
            r"B$": ".V2",
            r"C$": ".V3",
            r"D$": ".V4",
            r"E$": ".V5",
            r"F$": ".V6",
            r"G$": ".V7",
            r"H$": ".V8",
            r"I$": ".V9",
            r"J$": ".V10",
        }
    }
    new_victims.replace(replacements, regex=True, inplace=True)
    new_victims.sort_values("full_name", inplace=True)
    new_victims = new_victims.drop_duplicates(subset="Victim_ID")
    non_blanks = new_victims["full_name"] != ""
    new_victims = new_victims[non_blanks]
    vcols = [
        "case_id",
        "name",
        "phone_numbers",
        "address",
        "social_media",
        "victim_id",
    ]
    new_victims.columns = vcols
    new_victims["narrative"] = ""
    return new_victims


def set_sus_id_depr(new_suspects, db_cif):
    """Creates a unique ID for each suspect from Case ID and subsets/renames
    columns."""
    new_suspects = new_suspects[
        ["person_id", "full_name", "phone_contact", "address_notes", "social_media"]
    ]
    cif_ids = db_cif[["cif_number", "person_id", "pb_number", "case_notes"]]
    new_suspects = pd.merge(
        new_suspects,
        cif_ids,
        how="outer",
        on="person_id",
        sort=True,
        suffixes=("x", "y"),
        copy=True,
    )
    new_suspects.loc[:, "pb_number"] = new_suspects["pb_number"].fillna(0).astype(int)
    new_suspects.loc[:, "Suspect_ID"] = new_suspects.loc[:, "cif_number"].str.replace(
        ".", ""
    )
    new_suspects.loc[:, "Suspect_ID"] = (
        new_suspects.loc[:, "Suspect_ID"].str[:-1]
        + ".PB"
        + new_suspects["pb_number"].map(str)
    )
    new_suspects = new_suspects.drop_duplicates(subset="Suspect_ID")
    new_suspects = new_suspects[
        [
            "cif_number",
            "Suspect_ID",
            "full_name",
            "phone_contact",
            "address_notes",
            "social_media",
            "case_notes",
        ]
    ]
    new_suspects.rename(
        columns={
            "full_name": "Name",
            "phone_contact": "Phone Number(s)",
            "address_notes": "Address",
            "social_media": "Social Media ID",
            "cif_number": "Case_ID",
            "case_notes": "Narrative",
        },
        inplace=True,
    )
    return new_suspects


def set_suspect_id(
    new_suspects: pd.DataFrame, db_suspects: pd.DataFrame
) -> pd.DataFrame:
    """
    Create a unique ID for each suspect by merging new and database suspect data.

    This function performs the following operations:
        1. Selects and renames relevant columns from the `new_suspects` and `db_suspects` DataFrames.
        2. Merges the two DataFrames on `person_id` using an outer join.
        3. Renames columns according to a predefined mapping.
        4. Drops duplicate entries based on `suspect_id`.
        5. Selects and orders the final set of columns.

    Parameters:
        new_suspects (pd.DataFrame):
            DataFrame containing new suspect information. Must include the following columns:
                - `person_id`
                - `full_name`
                - `phone_contact`
                - `address_notes`
                - `social_media`

        db_suspects (pd.DataFrame):
            DataFrame containing existing database suspect information. Must include the following columns:
                - `suspect_id`
                - `person_id`
                - `sf_number`
                - `case_id`
                - `case_notes`

    Returns:
        pd.DataFrame:
            The merged and processed DataFrame containing unique suspect records with the following columns:
                - `name`
                - `phone_numbers`
                - `address`
                - `social_media_id`
                - `suspect_id`
                - `case_id`
                - `narrative`

    Raises:
        RuntimeError:
            If required columns are missing from either input DataFrame or if the merge operation fails.
    """
    try:
        logger.info("Starting set_suspect_id function.")

        # Define required columns for new_suspects
        new_suspect_required_columns = {
            "person_id",
            "full_name",
            "phone_contact",
            "address_notes",
            "social_media",
        }
        missing_new_suspect_cols = new_suspect_required_columns - set(
            new_suspects.columns
        )
        if missing_new_suspect_cols:
            error_msg = f"new_suspects DataFrame is missing required columns: {missing_new_suspect_cols}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required columns are present in new_suspects DataFrame.")

        # Define required columns for db_suspects
        db_suspect_required_columns = {
            "suspect_id",
            "person_id",
            "sf_number",
            "case_id",
            "case_notes",
        }
        missing_db_suspect_cols = db_suspect_required_columns - set(db_suspects.columns)
        if missing_db_suspect_cols:
            error_msg = f"db_suspects DataFrame is missing required columns: {missing_db_suspect_cols}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required columns are present in db_suspects DataFrame.")

        # Define columns for selection and renaming
        new_suspect_cols = [
            "person_id",
            "full_name",
            "phone_contact",
            "address_notes",
            "social_media",
        ]
        db_suspect_cols = [
            "suspect_id",
            "person_id",
            "sf_number",
            "case_id",
            "case_notes",
        ]
        column_rename = {
            "full_name": "name",
            "phone_contact": "phone_numbers",
            "address_notes": "address",
            "social_media": "social_media_id",
            "case_notes": "narrative",
            # "sf_number": "case_id", # This line is commented out in original code
            "suspect_id": "suspect_id",
            "case_id": "case_id",
        }

        logger.debug(
            "Selecting and renaming columns from new_suspects and db_suspects."
        )

        # Subset columns
        filtered_new_suspects = new_suspects[new_suspect_cols].copy().drop_duplicates()
        logger.debug(f"Selected columns from new_suspects: {new_suspect_cols}")

        filtered_db_suspects = db_suspects[db_suspect_cols].copy().drop_duplicates()
        logger.debug(f"Selected columns from db_suspects: {db_suspect_cols}")

        # Merge dataframes
        logger.info("Merging new_suspects with db_suspects on 'person_id'.")
        merged_suspects = pd.merge(
            filtered_new_suspects,
            filtered_db_suspects,
            how="outer",
            on="person_id",
            sort=True,
            suffixes=("x", "y"),
            validate="many_to_one",  # assuming each person_id in new_suspects is unique
        )
        logger.debug("Merge operation completed successfully.")

        # Rename columns
        logger.debug("Renaming columns as per the column_rename mapping.")
        merged_suspects.rename(columns=column_rename, inplace=True)
        logger.debug(f"Columns after renaming: {list(merged_suspects.columns)}")

        # Drop duplicates based on 'suspect_id'
        if "suspect_id" not in merged_suspects.columns:
            error_msg = "'suspect_id' column is missing after merging."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.info("Dropping duplicate entries based on 'suspect_id'.")
        before_dropping = len(merged_suspects)
        merged_suspects.drop_duplicates(subset="suspect_id", inplace=True)
        after_dropping = len(merged_suspects)
        logger.debug(f"Dropped {before_dropping - after_dropping} duplicate records.")

        # Select final columns
        final_columns = list(column_rename.values())
        # Ensure all final_columns are in merged_suspects
        missing_final_columns = set(final_columns) - set(merged_suspects.columns)
        if missing_final_columns:
            # Depending on the use case, could fill missing columns with empty strings or other defaults
            logger.warning(
                f"The following expected columns are missing after renaming: {missing_final_columns}. Adding them with default values."
            )
            for col in missing_final_columns:
                merged_suspects[col] = ""

        logger.debug(f"Selecting final columns: {final_columns}")
        merged_suspects = merged_suspects[final_columns]

        logger.info("Completed set_suspect_id function successfully.")
        return merged_suspects

    except KeyError as ke:
        error_msg = f"Key error during set_suspect_id: {ke}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from ke
    except pd.errors.MergeError as me:
        error_msg = f"Merge error during set_suspect_id: {me}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from me
    except Exception as e:
        error_msg = f"An unexpected error occurred in set_suspect_id: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def sum_and_join_vic(x):
    """Aggregate count of victims willing to testify by Case ID."""
    return pd.Series(
        dict(
            count=x["count"].sum(),
            willing_to_testify=", ".join(x.astype(str)["willing_to_testify"]),
        )
    )


def sum_and_join_sus(x):
    """Aggregate count of suspects located by Case ID."""
    return pd.Series(
        dict(count=x["count"].sum(), located=", ".join(x.astype(str)["located"]))
    )


def get_vics_willing_to_testify(victims: pd.DataFrame) -> pd.DataFrame:
    """
    Extract and aggregate victims who are willing to testify against traffickers.

    This function filters the victims DataFrame to identify those who have indicated their willingness
    to testify. It then processes the relevant information by renaming columns, adding a count, and
    aggregating the data based on `case_id`.

    Parameters:
        victims (pd.DataFrame):
            DataFrame containing victim information. Must include the following columns:
                - `case_status`: Status of the case indicating victim's willingness.
                - `case_id`: Identifier for each case.
                - `name`: Name of the victim.

    Returns:
        pd.DataFrame:
            A DataFrame containing aggregated information of victims willing to testify. The DataFrame includes:
                - `case_id`: Identifier for each case.
                - `willing_to_testify`: Comma-separated list of victim names willing to testify.
                - `count`: Number of victims willing to testify per case.
            If no victims are willing to testify, an empty DataFrame with the specified columns is returned.

    Raises:
        RuntimeError:
            If the required columns are missing from the input DataFrame.
    """
    try:
        logger.info("Starting extraction of willing victims to testify.")

        # Define required columns
        required_columns = {"case_status", "case_id", "name"}
        missing_columns = required_columns - set(victims.columns)
        if missing_columns:
            error_msg = (
                f"Input DataFrame is missing required columns: {missing_columns}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Filter victims who are willing to testify
        willing_status = "Step Complete: Victim is willing to press charges"
        vics_willing = victims[victims["case_status"] == willing_status].copy()
        logger.debug(f"Filtered {len(vics_willing)} victims willing to testify.")

        if not vics_willing.empty:
            # Select relevant columns
            vics_willing = vics_willing[["case_id", "name"]]
            logger.debug("Selected 'case_id' and 'name' columns for willing victims.")

            # Rename 'name' to 'willing_to_testify'
            vics_willing.rename(columns={"name": "willing_to_testify"}, inplace=True)
            logger.debug("Renamed 'name' column to 'willing_to_testify'.")

            # Add a 'count' column with value 1
            vics_willing["count"] = 1
            logger.debug("Added 'count' column with default value 1.")

            # Group by 'case_id' and aggregate
            vics_willing = (
                vics_willing.groupby("case_id").apply(sum_and_join_vic).reset_index()
            )
            logger.info("Aggregated willing victims by 'case_id'.")
        else:
            # Create an empty DataFrame with the expected columns
            vics_willing = pd.DataFrame(
                columns=["case_id", "willing_to_testify", "count"]
            )
            logger.info(
                "No victims are willing to testify. Returning empty DataFrame with 'count' set to 0."
            )
            # Optionally, if you want to include cases with zero willing victims:
            # Extract unique case_ids from the original victims DataFrame
            # vics_willing['count'] = 0
            # vics_willing['willing_to_testify'] = ""

        # Ensure 'count' column exists and is properly set
        if "count" not in vics_willing.columns:
            vics_willing["count"] = 0
            logger.debug(
                "Added 'count' column with value 0 for cases with no willing victims."
            )

        logger.info("Completed extraction of willing victims to testify.")
        return vics_willing

    except KeyError as ke:
        error_msg = f"Key error during processing: {ke}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from ke
    except Exception as e:
        error_msg = f"An unexpected error occurred in get_vics_willing_to_testify: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def add_vic_names(
    target_sheet: pd.DataFrame, vics_willing: pd.DataFrame
) -> pd.DataFrame:
    """
    Integrate a list of victims willing to testify into the target DataFrame.

    This function merges the `vics_willing` DataFrame with the `target_sheet` DataFrame based on the `case_id`.
    It adds a new column `victims_willing_to_testify`, which contains a comma-separated list of victim names
    willing to testify for each case. After merging, it removes intermediary columns used during the process.

    Parameters:
        target_sheet (pd.DataFrame):
            The primary DataFrame to which victim information will be added. Must include:
                - `case_id`: Identifier for each case.

        vics_willing (pd.DataFrame):
            DataFrame containing aggregated victim willingness data. Must include:
                - `case_id`: Identifier for each case.
                - `willing_to_testify`: Comma-separated list of victim names willing to testify.
                - `count`: Number of victims willing to testify per case.

    Returns:
        pd.DataFrame:
            The updated `target_sheet` DataFrame with an additional `victims_willing_to_testify` column.
            If `vics_willing` is empty, the original `target_sheet` is returned unmodified.

    Raises:
        RuntimeError:
            If required columns are missing from the input DataFrames or if the merge operation fails.
    """
    try:
        logger.info("Starting integration of willing victims into the target sheet.")

        # Define required columns for vics_willing
        required_vics_columns = {"case_id", "willing_to_testify", "count"}
        missing_vics_columns = required_vics_columns - set(vics_willing.columns)
        if missing_vics_columns:
            error_msg = f"vics_willing DataFrame is missing required columns: {missing_vics_columns}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required columns are present in vics_willing DataFrame.")

        # Define required columns for target_sheet
        required_target_columns = {"case_id"}
        missing_target_columns = required_target_columns - set(target_sheet.columns)
        if missing_target_columns:
            error_msg = f"target_sheet DataFrame is missing required columns: {missing_target_columns}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required columns are present in target_sheet DataFrame.")

        if not vics_willing.empty:
            logger.info(
                f"Merging vics_willing DataFrame with {len(target_sheet)} records in target_sheet."
            )

            # Merge the vics_willing DataFrame into the target_sheet DataFrame on 'case_id'
            target_sheet = pd.merge(
                target_sheet,
                vics_willing,
                how="left",
                on="case_id",
                validate="many_to_one",  # Assuming each case_id in target_sheet is unique
            )
            logger.debug("Merge operation completed successfully.")

            # Create 'victims_willing_to_testify' column by filling NaN with empty strings
            target_sheet["victims_willing_to_testify"] = target_sheet[
                "willing_to_testify"
            ].fillna("")
            logger.debug("Created 'victims_willing_to_testify' column.")

            # Drop intermediary columns as they are no longer needed
            columns_to_drop = ["willing_to_testify", "count"]
            target_sheet.drop(columns=columns_to_drop, inplace=True)
            logger.debug(f"Dropped columns: {columns_to_drop}")
        else:
            logger.info("vics_willing DataFrame is empty. No merging performed.")

        logger.info("Completed integration of willing victims into the target sheet.")
        return target_sheet

    except pd.errors.MergeError as me:
        error_msg = f"Merge error during add_vic_names: {me}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from me
    except KeyError as ke:
        error_msg = f"Key error during add_vic_names: {ke}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from ke
    except Exception as e:
        error_msg = f"An unexpected error occurred in add_vic_names: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def get_sus_located(suspects: pd.DataFrame) -> pd.DataFrame:
    """
    Extract and aggregate suspects who have been identified and located.

    This function filters the suspects DataFrame to identify those who have been located based on
    their `case_status`. It then processes the relevant information by renaming columns, adding a count,
    and aggregating the data based on `case_id`.

    Parameters:
        suspects (pd.DataFrame):
            DataFrame containing suspect information. Must include the following columns:
                - `case_status`: Status of the case indicating if the suspect has been located.
                - `case_id`: Identifier for each case.
                - `name`: Name of the suspect.

    Returns:
        pd.DataFrame:
            A DataFrame containing aggregated information of located suspects. The DataFrame includes:
                - `case_id`: Identifier for each case.
                - `located`: Comma-separated list of suspect names who have been located.
                - `count`: Number of suspects located per case.
            If no suspects are located, an empty DataFrame with the specified columns is returned with `count` set to 0.

    Raises:
        RuntimeError:
            If the required columns are missing from the input DataFrame or if the aggregation fails.
    """
    try:
        logger.info("Starting extraction of located suspects.")

        # Define required columns
        required_columns = {"case_status", "case_id", "name"}
        missing_columns = required_columns - set(suspects.columns)
        if missing_columns:
            error_msg = (
                f"Input DataFrame is missing required columns: {missing_columns}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required columns are present in suspects DataFrame.")

        # Filter suspects who have been located
        located_status = "Step Complete"
        sus_located = suspects[
            suspects["case_status"].str.contains(located_status, na=False)
        ].copy()
        logger.debug(f"Filtered {len(sus_located)} suspects who have been located.")

        if not sus_located.empty:
            # Select relevant columns
            sus_located = sus_located[["case_id", "name"]]
            logger.debug("Selected 'case_id' and 'name' columns for located suspects.")

            # Rename 'name' to 'located'
            sus_located.rename(columns={"name": "located"}, inplace=True)
            logger.debug("Renamed 'name' column to 'located'.")

            # Add a 'count' column with value 1
            sus_located["count"] = 1
            logger.debug("Added 'count' column with default value 1.")

            # Group by 'case_id' and aggregate
            sus_located = (
                sus_located.groupby("case_id").apply(sum_and_join_sus).reset_index()
            )
            logger.info("Aggregated located suspects by 'case_id'.")
        else:
            # Create an empty DataFrame with the expected columns
            sus_located = pd.DataFrame(columns=["case_id", "located", "count"])
            logger.info(
                "No suspects have been located. Returning empty DataFrame with 'count' set to 0."
            )

        # Ensure 'count' column exists and is properly set
        if "count" not in sus_located.columns:
            sus_located["count"] = 0
            logger.debug(
                "Added 'count' column with value 0 for cases with no located suspects."
            )

        logger.info("Completed extraction of located suspects.")
        return sus_located

    except KeyError as ke:
        error_msg = f"Key error during processing: {ke}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from ke
    except Exception as e:
        error_msg = f"An unexpected error occurred in get_sus_located: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def add_sus_located(
    target_sheet: pd.DataFrame, sus_located: pd.DataFrame
) -> pd.DataFrame:
    """
    Integrate a list of located suspects into the target DataFrame.

    This function merges the `sus_located` DataFrame with the `target_sheet` DataFrame based on the `case_id`.
    It adds a new column `suspects_identified_and_located`, which contains a comma-separated list of suspect names
    who have been identified and located for each case. After merging, it removes intermediary columns used during
    the process.

    Parameters:
        target_sheet (pd.DataFrame):
            The primary DataFrame to which located suspect information will be added. Must include:
                - `case_id`: Identifier for each case.

        sus_located (pd.DataFrame):
            DataFrame containing aggregated located suspect data. Must include:
                - `case_id`: Identifier for each case.
                - `located`: Comma-separated list of suspect names who have been located.
                - `count`: Number of suspects located per case.

    Returns:
        pd.DataFrame:
            The updated `target_sheet` DataFrame with an additional `suspects_identified_and_located` column.
            If `sus_located` is empty, the original `target_sheet` is returned unmodified.

    Raises:
        RuntimeError:
            If required columns are missing from the input DataFrames or if the merge operation fails.
    """
    try:
        logger.info("Starting integration of located suspects into the target sheet.")

        # Define required columns for sus_located
        required_sus_located_columns = {"case_id", "located", "count"}
        missing_sus_located_columns = required_sus_located_columns - set(
            sus_located.columns
        )
        if missing_sus_located_columns:
            error_msg = f"sus_located DataFrame is missing required columns: {missing_sus_located_columns}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required columns are present in sus_located DataFrame.")

        # Define required columns for target_sheet
        required_target_columns = {"case_id"}
        missing_target_columns = required_target_columns - set(target_sheet.columns)
        if missing_target_columns:
            error_msg = f"target_sheet DataFrame is missing required columns: {missing_target_columns}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required columns are present in target_sheet DataFrame.")

        if not sus_located.empty:
            logger.info(
                f"Merging sus_located DataFrame with {len(target_sheet)} records in target_sheet."
            )

            # Merge the sus_located DataFrame into the target_sheet DataFrame on 'case_id'
            target_sheet = pd.merge(
                target_sheet,
                sus_located,
                how="left",
                on="case_id",
                validate="many_to_one",  # Assuming each case_id in target_sheet is unique
            )
            logger.debug("Merge operation completed successfully.")

            # Create 'suspects_identified_and_located' column by filling NaN with empty strings
            target_sheet["suspects_identified_and_located"] = target_sheet[
                "located"
            ].fillna("")
            logger.debug("Created 'suspects_identified_and_located' column.")

            # Drop intermediary columns as they are no longer needed
            columns_to_drop = ["located", "count"]
            target_sheet.drop(columns=columns_to_drop, inplace=True)
            logger.debug(f"Dropped columns: {columns_to_drop}")
        else:
            logger.info("sus_located DataFrame is empty. No merging performed.")

        logger.info("Completed integration of located suspects into the target sheet.")
        return target_sheet

    except pd.errors.MergeError as me:
        error_msg = f"Merge error during add_sus_located: {me}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from me
    except KeyError as ke:
        error_msg = f"Key error during add_sus_located: {ke}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from ke
    except Exception as e:
        error_msg = f"An unexpected error occurred in add_sus_located: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def calc_vics_willing_scores(
    suspects: pd.DataFrame, vics_willing: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate and assign victim willingness multipliers to suspects.

    This function computes a multiplier based on the number of victims willing to testify for each suspect case.
    The multiplier reflects the strength or reliability of the case, enhancing the suspect's profile accordingly.
    It merges the `suspects` DataFrame with the `vics_willing` DataFrame on the `case_id`, applies the
    multiplier based on predefined rules, and adds a new column `v_mult` to the suspects DataFrame.

    Parameters:
        suspects (pd.DataFrame):
            DataFrame containing suspect information. Must include a `case_id` column to identify each case.

        vics_willing (pd.DataFrame):
            DataFrame containing victim willingness data. Must include:
                - `case_id`: Identifier to merge with the suspects DataFrame.
                - `count`: Integer representing the number of victims willing to testify.

    Returns:
        pd.DataFrame:
            The updated suspects DataFrame with an additional `v_mult` column representing the victim willingness multiplier.
            If `vics_willing` is empty, `v_mult` is set to 0.0 for all suspects.

    Multiplier Calculation:
        The multiplier (`v_mult`) is determined based on the number of willing victims (`count`) as follows:
            count | v_mult
            ------|-------
              0   | 0.0
              1   | 0.5
              2   | 0.75
              3   | 0.875
              4   | 0.9375
              5   | 0.96875
              6   | 0.984375
              7+  | 1.0

    Notes:
        - The function uses a predefined incremental approach to calculate multipliers for counts between 2 and 6.
        - Columns `willing_to_testify` and `count` are removed from the final suspects DataFrame after processing.
        - Ensure that the input DataFrames have the required columns to avoid merge issues.
    """
    # Define victim multiplier
    v_mult: Dict[int, float] = {0: 0.0, 1: 0.5, 7: 1.0}
    for i in range(2, 7):
        v_mult[i] = v_mult[i - 1] + (1 - v_mult[i - 1]) * 0.5

    try:
        if not vics_willing.empty:
            # Define required columns
            required_suspect_cols = {"case_id"}
            required_vics_cols = {"case_id", "count"}

            # Check for missing columns in suspects DataFrame
            missing_suspect_cols = required_suspect_cols - set(suspects.columns)
            if missing_suspect_cols:
                raise ValueError(
                    f"Missing columns in suspects DataFrame: {missing_suspect_cols}"
                )

            # Check for missing columns in vics_willing DataFrame
            missing_vics_cols = required_vics_cols - set(vics_willing.columns)
            if missing_vics_cols:
                raise ValueError(
                    f"Missing columns in vics_willing DataFrame: {missing_vics_cols}"
                )

            # Merge data
            suspects = pd.merge(suspects, vics_willing, how="left", on="case_id")
            suspects["count"] = suspects["count"].fillna(0).astype(int)

            # Map counts to multipliers
            suspects["v_mult"] = suspects["count"].map(v_mult).fillna(0.0).astype(float)

            # Drop unnecessary columns if they exist
            columns_to_drop = ["willing_to_testify", "count"]
            existing_columns_to_drop = [
                col for col in columns_to_drop if col in suspects.columns
            ]
            suspects.drop(columns=existing_columns_to_drop, inplace=True)
        else:
            # If vics_willing is empty, set v_mult to 0.0 for all suspects
            suspects["v_mult"] = 0.0

    except pd.errors.MergeError as me:
        raise RuntimeError(f"DataFrame merge failed: {me}") from me
    except KeyError as ke:
        raise RuntimeError(f"Key error during processing: {ke}") from ke
    except ValueError as ve:
        raise RuntimeError(f"Value error: {ve}") from ve
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}") from e

    return suspects


def calc_arrest_scores(
    suspects: pd.DataFrame, states_of_charge: pd.DataFrame, police: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate scores based on the number of other suspects arrested in each case,
    and create fields for 'bio_known' and for police willingness to arrest.

    This function performs the following operations:
        1. Sets the 'bio_known' flag based on the 'case_status' of each suspect.
        2. Calculates the total number of arrests in each case and merges this data into the suspects DataFrame.
        3. Determines police willingness to arrest based on their 'case_status' and merges this information into the suspects DataFrame.

    Parameters:
        suspects (pd.DataFrame):
            DataFrame containing suspect information. Must include:
                - `case_id`: Identifier for each case.
                - `case_status`: Status of the case.

        states_of_charge (pd.DataFrame):
            DataFrame containing state of charge information. Must include:
                - `case_id`: Group identifier (used in `get_total_arrests`).
                - `arrested`: Indicator if arrested.
                - `case_id`: Identifier to merge with suspects.

        police (pd.DataFrame):
            DataFrame containing police information. Must include:
                - `case_id`: Identifier to merge with suspects.
                - `case_status`: Status indicating willingness to arrest.

    Returns:
        pd.DataFrame:
            The updated suspects DataFrame with additional columns:
                - `bio_known`: Binary indicator (1 if bio is known, else 0).
                - `others_arrested`: Total number of other arrests in the case.
                - `willing_to_arrest`: Binary indicator (1 if police are willing to arrest, else 0).

    Raises:
        RuntimeError:
            If any step in the calculation process fails due to missing columns or other issues.
    """
    try:
        # Log the initial state of the DataFrames
        logger.info(
            f"Starting calc_arrest_scores with the following DataFrame columns:\n"
            f"suspects.columns = {list(suspects.columns)},\n"
            f"states_of_charge.columns = {list(states_of_charge.columns)},\n"
            f"police.columns = {list(police.columns)}"
        )

        # Define required columns for each DataFrame
        required_suspects_cols = {"case_id", "case_status"}
        required_states_cols = {"arrested", "case_id"}
        required_police_cols = {"case_id", "case_status"}

        # Validate required columns in suspects DataFrame
        missing_suspects_cols = required_suspects_cols - set(suspects.columns)
        if missing_suspects_cols:
            error_msg = f"suspects DataFrame is missing required columns: {missing_suspects_cols}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Validate required columns in states_of_charge DataFrame
        missing_states_cols = required_states_cols - set(states_of_charge.columns)
        if missing_states_cols:
            error_msg = f"states_of_charge DataFrame is missing required columns: {missing_states_cols}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Validate required columns in police DataFrame
        missing_police_cols = required_police_cols - set(police.columns)
        if missing_police_cols:
            error_msg = (
                f"police DataFrame is missing required columns: {missing_police_cols}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 1. Setting the 'bio_known' column
        logger.info("Calculating 'bio_known' column.")
        suspects["bio_known"] = (
            suspects["case_status"] != "Step Complete: Identity and Location Confirmed"
        ).astype(int)
        logger.info("'bio_known' column calculated successfully.")

        # 2. Fetching and merging arrest data
        logger.info("Fetching total arrests using 'get_total_arrests' function.")
        # Select only required columns for get_total_arrests
        states_subset = states_of_charge[["arrested", "case_id"]].copy()
        arrests = get_total_arrests(states_subset)
        logger.info("Total arrests fetched successfully.")

        # Ensure 'case_id' is present in arrests DataFrame
        if "case_id" not in arrests.columns or "total_arrests" not in arrests.columns:
            error_msg = "get_total_arrests must return a DataFrame with 'case_id' and 'total_arrests' columns."
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("Merging total arrests into suspects DataFrame.")
        suspects = suspects.merge(
            arrests[["case_id", "total_arrests"]], on="case_id", how="left"
        )
        suspects["others_arrested"] = suspects["total_arrests"].fillna(0).astype(int)
        suspects.drop(columns=["total_arrests"], inplace=True)
        logger.info("'others_arrested' column added successfully.")

        # 3. Identifying police willingness to arrest
        logger.info("Calculating 'willing_to_arrest' column in police DataFrame.")
        police["willing_to_arrest"] = (
            police["case_status"].str.contains("Step Complete", na=False).astype(int)
        )
        logger.info("'willing_to_arrest' column calculated successfully.")

        # Validate 'case_id' and 'willing_to_arrest' columns in police DataFrame
        if "case_id" not in police.columns or "willing_to_arrest" not in police.columns:
            error_msg = "After processing, police DataFrame must contain 'case_id' and 'willing_to_arrest' columns."
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("Merging 'willing_to_arrest' into suspects DataFrame.")
        suspects = suspects.merge(
            police[["case_id", "willing_to_arrest"]], on="case_id", how="left"
        )
        suspects["willing_to_arrest"] = (
            suspects["willing_to_arrest"].fillna(0).astype(int)
        )
        logger.info("'willing_to_arrest' column merged successfully.")

    except ValueError as ve:
        logger.error(f"Value error in calc_arrest_scores: {ve}")
        raise RuntimeError(f"Value error in calc_arrest_scores: {ve}") from ve
    except KeyError as ke:
        logger.error(f"Key error in calc_arrest_scores: {ke}")
        raise RuntimeError(f"Key error in calc_arrest_scores: {ke}") from ke
    except pd.errors.MergeError as me:
        logger.error(f"Merge error in calc_arrest_scores: {me}")
        raise RuntimeError(f"Merge error in calc_arrest_scores: {me}") from me
    except Exception as e:
        logger.error(f"An unexpected error occurred in calc_arrest_scores: {e}")
        raise RuntimeError(
            f"An unexpected error occurred in calc_arrest_scores: {e}"
        ) from e

    logger.info("Successfully completed calc_arrest_scores.")
    return suspects


def get_total_arrests(soc_df):
    """Create case_id from suspect_id and aggregate arrests. ['case_id',
    'case_id', 'arrested']"""

    # Create case_id from case_id and aggregate arrests
    arrests = soc_df.assign(case_id=soc_df["case_id"])
    arrests = arrests.groupby("case_id")["arrested"].sum().reset_index()
    arrests.columns = ["case_id", "total_arrests"]

    return arrests


def weight_pv_believes(
    suspects: pd.DataFrame, states_of_charge: pd.DataFrame, weights: Dict[str, Any]
) -> pd.DataFrame:
    """
    Weight beliefs about suspects' involvement in trafficking.

    This function calculates a "pv_believes" score for each suspect based on various indicators
    of their involvement in trafficking. The score is determined by evaluating multiple belief
    indicators and applying corresponding weights.

    The function performs the following operations:
        1. Extracts relevant columns from the `states_of_charge` DataFrame.
        2. Computes the "pv_believes" score using the provided weights.
        3. Processes and derives the `case_id` from `sf_number`.
        4. Cleans and finalizes the data by selecting necessary columns and removing duplicates.
        5. Merges the computed "pv_believes" score into the `suspects` DataFrame.

    Parameters:
        suspects (pd.DataFrame):
            DataFrame containing suspect information. Must include:
                - `case_id`: Identifier for each case.
                - `suspect_id`: Unique identifier for each suspect.

        states_of_charge (pd.DataFrame):
            DataFrame containing state of charge information. Must include:
                - `sf_number`: Group identifier used to derive `case_id`.
                - `pv_believes_definitely_trafficked_many`: Indicator of definite trafficking beliefs.
                - `pv_believes_trafficked_some`: Indicator of some trafficking beliefs.
                - `pv_believes_suspect_trafficker`: Indicator of suspect being a trafficker.

        weights (Dict[str, Any]):
            Dictionary containing weight values for each belief indicator. Must include:
                - `pv_believes_definitely_trafficked_many`: Weight for definite trafficking beliefs.
                - `pv_believes_trafficked_some`: Weight for some trafficking beliefs.
                - `pv_believes_suspect_trafficker`: Weight for suspect being a trafficker.

    Returns:
        pd.DataFrame:
            The updated suspects DataFrame with an additional `pv_believes` column.

    Raises:
        RuntimeError:
            If any step in the calculation process fails due to missing columns, data inconsistencies,
            or unexpected errors during processing.
    """
    try:
        # Log the initial state of the DataFrames and weights
        logger.info(
            "Starting weight_pv_believes with the following DataFrame columns:\n"
            f"suspects.columns = {list(suspects.columns)},\n"
            f"states_of_charge.columns = {list(states_of_charge.columns)},\n"
            f"weights keys = {list(weights.keys())}"
        )

        # Define required columns for each DataFrame
        required_suspects_cols = {"case_id", "suspect_id"}
        required_states_cols = {
            "sf_number",
            "pv_believes_definitely_trafficked_many",
            "pv_believes_trafficked_some",
            "pv_believes_suspect_trafficker",
        }
        required_weights_keys = {
            "pv_believes_definitely_trafficked_many",
            "pv_believes_trafficked_some",
            "pv_believes_suspect_trafficker",
        }

        # Validate required columns in suspects DataFrame
        missing_suspects_cols = required_suspects_cols - set(suspects.columns)
        if missing_suspects_cols:
            error_msg = f"suspects DataFrame is missing required columns: {missing_suspects_cols}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required columns are present in suspects DataFrame.")

        # Validate required columns in states_of_charge DataFrame
        missing_states_cols = required_states_cols - set(states_of_charge.columns)
        if missing_states_cols:
            error_msg = f"states_of_charge DataFrame is missing required columns: {missing_states_cols}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required columns are present in states_of_charge DataFrame.")

        # Validate required keys in weights dictionary
        missing_weights_keys = required_weights_keys - set(weights.keys())
        if missing_weights_keys:
            error_msg = (
                f"weights dictionary is missing required keys: {missing_weights_keys}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required keys are present in weights dictionary.")

        # 1. Extract and compute the "pv_believes" score
        logger.info(
            "Extracting relevant columns from states_of_charge for pv_believes calculation."
        )
        pvb = states_of_charge[
            [
                "sf_number",
                "pv_believes_definitely_trafficked_many",
                "pv_believes_trafficked_some",
                "pv_believes_suspect_trafficker",
            ]
        ].copy()

        # Ensure that the belief indicators are numeric
        belief_indicators = [
            "pv_believes_definitely_trafficked_many",
            "pv_believes_trafficked_some",
            "pv_believes_suspect_trafficker",
        ]
        for col in belief_indicators:
            pvb[col] = pd.to_numeric(pvb[col], errors="coerce").fillna(0)
            if pvb[col].isnull().any():
                logger.warning(
                    f"Found NaN values in '{col}' after conversion. These have been filled with 0."
                )
        logger.debug("Converted belief indicators to numeric successfully.")

        logger.info("Calculating 'pv_believes' score using weighted indicators.")
        # Extract weights
        weights_dict = {
            "pv_believes_definitely_trafficked_many": weights[
                "pv_believes_definitely_trafficked_many"
            ],
            "pv_believes_trafficked_some": weights["pv_believes_trafficked_some"],
            "pv_believes_suspect_trafficker": weights["pv_believes_suspect_trafficker"],
        }

        # Validate weights are numeric
        for key, value in weights_dict.items():
            if not isinstance(value, (int, float)):
                error_msg = f"Weight value for '{key}' must be numeric."
                logger.error(error_msg)
                raise RuntimeError(error_msg)
        logger.debug("All weights for pv_believes are numeric.")

        # Calculate the weighted pv_believes score
        pvb["pv_believes"] = (
            pvb["pv_believes_definitely_trafficked_many"]
            * weights_dict["pv_believes_definitely_trafficked_many"]
            + pvb["pv_believes_trafficked_some"]
            * weights_dict["pv_believes_trafficked_some"]
            + pvb["pv_believes_suspect_trafficker"]
            * weights_dict["pv_believes_suspect_trafficker"]
        )
        logger.info("'pv_believes' score calculated successfully.")

        # 2. Process the Case ID
        logger.info("Deriving 'case_id' from 'sf_number'.")
        pvb["case_id"] = (
            pvb["sf_number"]
            .astype(str)
            .str.rstrip(".")
            .str.replace(".", "", regex=False)
        )
        logger.debug("Derived 'case_id' successfully.")

        # 3. Clean up and finalize the data
        logger.info("Preparing 'pvb' DataFrame for merging.")
        pvb = pvb[["case_id", "pv_believes"]].copy()
        pvb["pv_believes"] = pvb["pv_believes"].astype(float)
        logger.debug(f"pv_believes DataFrame after cleanup:\n{pvb.head()}")
        pvb.drop_duplicates(subset="case_id", inplace=True)
        logger.info("Cleaned 'pvb' DataFrame successfully.")

        # 4. Merge the data
        logger.info("Merging 'pv_believes' scores into suspects DataFrame.")
        suspects = suspects.merge(pvb, on="case_id", how="left")
        suspects["pv_believes"] = suspects["pv_believes"].fillna(0.0).astype(float)
        logger.info("'pv_believes' scores merged successfully.")

    except RuntimeError as re:
        logger.error(f"Runtime error in weight_pv_believes: {re}")
        raise
    except KeyError as ke:
        error_msg = f"Key error in weight_pv_believes: {ke}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from ke
    except Exception as e:
        error_msg = f"An unexpected error occurred in weight_pv_believes: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

    logger.info("Successfully completed weight_pv_believes.")
    return suspects


def get_exp_score(
    suspects: pd.DataFrame,
    states_of_charges: pd.DataFrame,
    weights: Dict[str, float],
) -> pd.DataFrame:
    """
    Calculate exploitation score based on parameters and reported exploitation.

    This function computes an "exp" (exploitation) score for each suspect based on various exploitation indicators.
    The score is calculated by applying weights to different exploitation factors, reflecting the level of exploitation
    associated with each suspect.

    The function performs the following operations:
        1. Extracts relevant exploitation-related columns from the `states_of_charges` DataFrame.
        2. Computes the "exp" score using provided weights for each exploitation indicator.
        3. Processes and derives the `case_id` from `sf_number`.
        4. Cleans and finalizes the data by selecting necessary columns and removing duplicates.
        5. Merges the computed "exp" score into the `suspects` DataFrame.

    Parameters:
        suspects (pd.DataFrame):
            DataFrame containing suspect information. Must include:
                - `case_id`: Identifier for each case.
                - `suspect_id`: Unique identifier for each suspect.

        states_of_charges (pd.DataFrame):
            DataFrame containing state of charge information. Must include:
                - `sf_number`: Group identifier used to derive `case_id`.
                - Various exploitation indicator columns containing boolean values (e.g.,
                  `pv_believes_definitely_trafficked_many`, `pv_believes_trafficked_some`, etc.).

        exploitation_type (Dict[str, float]):
            Dictionary containing weight values for each exploitation indicator. The keys should correspond
            to the exploitation indicator column names in `states_of_charges`, and the values are the weights
            to be applied.

    Returns:
        pd.DataFrame:
            The updated suspects DataFrame with an additional `exp` column representing the exploitation score.

    Raises:
        RuntimeError:
            If any step in the calculation process fails due to missing columns or other issues.
    """

    def get_exploitation_weights(weights):

        exploitation_weights = {
            "exploit_prostitution": weights["exploit_prostitution"],
            "exploit_sexual_abuse": weights["exploit_sexual_abuse"],
            "exploit_physical_abuse": weights["exploit_physical_abuse"],
            "exploit_debt_bondage": weights["exploit_forced_labor"],
            "exploit_forced_labor": weights["exploit_forced_labor"],
        }
        return exploitation_weights

    exploitation_type = get_exploitation_weights(weights)
    try:
        # Log the initial state of the DataFrames
        logger.info(
            "Starting get_exp_score with the following DataFrame columns:\n"
            f"suspects.columns = {list(suspects.columns)},\n"
            f"states_of_charges.columns = {list(states_of_charges.columns)},\n"
            f"exploitation_type.keys() = {list(exploitation_type.keys())}"
        )

        # Define required columns for each DataFrame
        required_suspects_cols = {"case_id", "suspect_id"}
        required_states_cols = set(exploitation_type.keys()).union({"sf_number"})

        # Validate required columns in suspects DataFrame
        missing_suspects_cols = required_suspects_cols - set(suspects.columns)
        if missing_suspects_cols:
            error_msg = f"suspects DataFrame is missing required columns: {missing_suspects_cols}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Validate required columns in states_of_charges DataFrame
        missing_states_cols = required_states_cols - set(states_of_charges.columns)
        if missing_states_cols:
            error_msg = f"states_of_charges DataFrame is missing required columns: {missing_states_cols}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 1. Extract relevant columns and data
        logger.info("Extracting relevant exploitation columns from states_of_charges.")
        exp_cols = [
            col for col in states_of_charges.columns if "exploitation" in col
        ] + ["sf_number"]
        exp_df = states_of_charges[exp_cols].copy()
        exp_df["exp"] = 0.0  # Initialize exploitation score

        # 2. Compute the exploitation score
        logger.info(
            "Calculating 'exp' score based on exploitation indicators and weights."
        )
        for col in exploitation_type:
            if col in exp_df.columns:
                # Ensure the column contains boolean values
                exp_df[col] = exp_df[col].astype(bool)
                weight = exploitation_type[col]
                exp_df["exp"] += exp_df[col].astype(int) * weight
                logger.debug(f"Applied weight {weight} to column '{col}'.")

        logger.info("'exp' score calculated successfully.")

        # 3. Process the Case ID
        logger.info("Deriving 'case_id' from 'sf_number'.")
        exp_df["case_id"] = (
            exp_df["sf_number"].str.rstrip(".").str.replace(".", "", regex=True)
        )
        logger.info("'case_id' derived successfully.")

        # 4. Clean up and finalize the data
        logger.info("Preparing 'exp_df' DataFrame for merging.")
        logger.debug(f"<<< Before converting 'exp' to float:\n{exp_df['exp'].head()}")
        exp_df = exp_df[["case_id", "exp"]].copy()
        exp_df["exp"] = exp_df["exp"].astype(float)
        logger.debug(f">>> After converting 'exp' to float:\n{exp_df['exp'].head()}")

        exp_df.drop_duplicates(subset="case_id", inplace=True)
        logger.info("Removed duplicate 'case_id' entries from 'exp_df'.")

        # 5. Merge suspect data with the exploitation score data
        logger.info("Merging 'exp' scores into suspects DataFrame.")
        suspects = suspects.merge(exp_df, on="case_id", how="left")
        suspects["exp"] = suspects["exp"].fillna(0.0).astype(float)
        logger.info("'exp' scores merged successfully into suspects DataFrame.")

    except ValueError as ve:
        logger.error(f"Value error in get_exp_score: {ve}")
        raise RuntimeError(f"Value error in get_exp_score: {ve}") from ve
    except KeyError as ke:
        logger.error(f"Key error in get_exp_score: {ke}")
        raise RuntimeError(f"Key error in get_exp_score: {ke}") from ke
    except pd.errors.MergeError as me:
        logger.error(f"Merge error in get_exp_score: {me}")
        raise RuntimeError(f"Merge error in get_exp_score: {me}") from me
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_exp_score: {e}")
        raise RuntimeError(f"An unexpected error occurred in get_exp_score: {e}") from e

    logger.info("Successfully completed get_exp_score.")
    return suspects


def validate_required_columns(df, required_cols, df_name):
    """Validate that the DataFrame contains the required columns."""
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        error_msg = f"{df_name} DataFrame is missing required columns: {missing_cols}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    logger.debug(f"All required columns are present in {df_name} DataFrame.")
    return True


def validate_required_keys(dictionary, required_keys, dict_name):
    """Validate that the dictionary contains the required keys."""
    missing_keys = required_keys - set(dictionary.keys())
    if missing_keys:
        error_msg = f"{dict_name} dictionary is missing required keys: {missing_keys}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    logger.debug(f"All required keys are present in {dict_name} dictionary.")
    return True


def calc_recency_scores(
    suspects: pd.DataFrame, states_of_charge: pd.DataFrame, weights: Dict[str, Any]
) -> pd.DataFrame:
    """
    Assign a recency score to each suspect based on the number of days since their interview.

    The recency score is higher for more recent interviews and decreases as the number of days since the interview increases.
    The score is calculated using the formula:
        recency_score = max(1 - discount_coef * (days_old ** discount_exp), 0)

    This function performs the following operations:
        1. Calculates the number of days since each suspect's interview.
        2. Merges this information into the suspects DataFrame.
        3. Computes the recency score using provided weights.
        4. Removes duplicate suspect entries based on 'suspect_id'.

    Parameters:
        suspects (pd.DataFrame):
            DataFrame containing suspect information. Must include:
                - `case_id`: Identifier for each case.
                - `suspect_id`: Unique identifier for each suspect.

        states_of_charge (pd.DataFrame):
            DataFrame containing state of charge information. Must include:
                - `sf_number`: Group identifier used to derive `case_id`.
                - `interview_date`: Date of the suspect's interview.

        weights (Dict[str, Any]):
            Dictionary containing weight parameters for score calculation. Must include:
                - `discount_coef`: Coefficient used in the recency score formula.
                - `discount_exp`: Exponent used in the recency score formula.

    Returns:
        pd.DataFrame:
            The updated suspects DataFrame with an additional `recency_score` column.

    Raises:
        RuntimeError:
            If any step in the calculation process fails due to missing columns, data inconsistencies,
            or unexpected errors during processing.
    """
    try:
        # Log the initial state of the DataFrames and weights
        logger.info(
            "Starting calc_recency_scores with the following DataFrame columns:\n"
            f"  suspects.columns = {list(suspects.columns)},\n"
            f"  states_of_charge.columns = {list(states_of_charge.columns)},\n"
            f"  weights keys = {list(weights.keys())}"
        )

        # Define required columns and keys
        required_suspects_cols = {"case_id", "suspect_id"}
        required_states_cols = {"sf_number", "interview_date"}
        required_weights_keys = {"discount_coef", "discount_exp"}

        # Validate required columns and keys using helper functions
        validate_required_columns(suspects, required_suspects_cols, "suspects")
        validate_required_columns(
            states_of_charge, required_states_cols, "states_of_charge"
        )
        validate_required_keys(weights, required_weights_keys, "weights")

        # 1. Calculate days since interview
        logger.info("Calculating days since interview.")
        today = pd.Timestamp.now().normalize()
        cif_dates = states_of_charge[["sf_number", "interview_date"]].copy()

        # Convert 'interview_date' to datetime; coerce errors to NaT
        cif_dates["interview_date"] = pd.to_datetime(
            cif_dates["interview_date"], errors="coerce"
        )
        invalid_dates = cif_dates[cif_dates["interview_date"].isnull()]
        if not invalid_dates.empty:
            logger.warning(
                f"Found {len(invalid_dates)} records with invalid 'interview_date'. "
                "These will be assigned a default 'days_old' value."
            )
            logger.debug(
                f"Invalid 'interview_date' records (sample):\n{invalid_dates[['sf_number']].head()}"
            )

        # Calculate 'days_old'
        cif_dates["days_old"] = (today - cif_dates["interview_date"]).dt.days
        # Assign default value for any NaT days
        cif_dates["days_old"] = cif_dates["days_old"].fillna(9999).astype(int)
        logger.info("Calculated 'days_old' successfully.")

        # Derive 'case_id' from 'sf_number'
        logger.info("Deriving 'case_id' from 'sf_number'.")
        cif_dates["case_id"] = (
            cif_dates["sf_number"]
            .astype(str)
            .str.rstrip(".")
            .str.replace(".", "", regex=False)
        )
        logger.debug("Derived 'case_id' successfully.")

        # 2. Merge suspects data with days since interview
        logger.info("Merging 'days_old' into suspects DataFrame.")
        cif_unique = cif_dates[["case_id", "days_old"]].drop_duplicates(
            subset="case_id"
        )
        suspects = suspects.merge(
            cif_unique,
            on="case_id",
            how="left",
            validate="many_to_one",  # Assuming each case_id in suspects is unique
        )
        suspects["days_old"] = suspects["days_old"].fillna(9999).astype(int)
        logger.info("Merged 'days_old' successfully.")

        # 3. Calculate the Recency Score
        logger.info("Calculating 'recency_score'.")
        coef = weights["discount_coef"]
        exp = weights["discount_exp"]

        # Validate that coef and exp are numeric
        if not isinstance(coef, (int, float)) or not isinstance(exp, (int, float)):
            error_msg = "'discount_coef' and 'discount_exp' must be numeric."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug(
            f"Using discount_coef={coef} and discount_exp={exp} for recency score calculation."
        )

        score_formula = 1 - coef * (suspects["days_old"] ** exp)
        suspects["recency_score"] = np.maximum(score_formula, 0)
        logger.info("'recency_score' calculated successfully.")

        # 4. Remove duplicate entries based on 'suspect_id'
        logger.info("Removing duplicate suspects based on 'suspect_id'.")
        before_dropping = len(suspects)
        suspects = suspects.drop_duplicates(subset="suspect_id")
        after_dropping = len(suspects)
        logger.info(f"Removed {before_dropping - after_dropping} duplicate suspects.")

    except RuntimeError as re:
        logger.error(f"Runtime error in calc_recency_scores: {re}")
        raise
    except KeyError as ke:
        error_msg = f"Key error in calc_recency_scores: {ke}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from ke
    except Exception as e:
        error_msg = f"An unexpected error occurred in calc_recency_scores: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

    logger.info("Successfully completed calc_recency_scores.")
    return suspects


def calc_network_scores(sus_with_links, sus):
    """
    Calculate weighted scores based on 1st and 2nd degree links that each suspect
    has with suspects from other cases and add these scores to the 'sus' dataframe.

        1st degree case link = two suspects have a direct connection
        2nd degree case link = two suspects are connected by one or more mutual contacts

    The calculations are made by dividing the number of first and second degree case links
    by the log (base 10) of the total number of connections the suspect has (plus nine).
    Nine is added to the number of connections so that if the number of connections is
    between 1-9 the product of the log will not be less than 1.
    """
    sus_with_links["1d_case_score"] = sus_with_links[
        "first_degree_case_links"
    ] / np.log10(sus_with_links["first_degree_links"] + 9)
    sus_with_links["2d_case_score"] = sus_with_links[
        "second_degree_case_links"
    ] / np.log10(sus_with_links["first_degree_links"] + 9)
    sus = pd.merge(
        sus,
        sus_with_links[["suspect_case_id", "1d_case_score", "2d_case_score"]],
        how="left",
        left_on="Suspect_ID",
        right_on="suspect_case_id",
    )
    sus.drop(columns=["suspect_case_id"], inplace=True)
    return sus


def get_network_weights(parameters):
    """Get weights for network analysis from Parameters Google Sheet."""
    net_weights = pd.DataFrame(parameters.iloc[5:9, 4:6])
    net_weights.columns = ["key", "value"]
    return net_weights


def weight_network_scores(sus, net_weights):
    """Weight the network scores according to the weights provided in the
    Parameters Sheet."""
    s = net_weights.set_index("key")["value"]
    one_link_add = float(s["1 Link Em Added"])
    max_add = float(s["Max Em Added"])
    second_d_weight = float(s["2nd Degree Weight"])
    sus["net_weight"] = (
        sus["1d_case_score"] * one_link_add
        + (sus["2d_case_score"] * one_link_add) * second_d_weight
    )
    sus["net_weight"].round(2)
    sus["net_weight"] = np.where(
        sus["net_weight"] > max_add, max_add, sus["net_weight"]
    )
    sus.drop(columns=["1d_case_score", "2d_case_score"], inplace=True)
    return sus


def check_update_links(sus_with_links, sus, Parameters):
    """Check to see if Network Analysis is on, and if it is calculate network
    scores and weight."""
    net_weights = get_network_weights(Parameters)
    if net_weights.iloc[0, 1] == "On":
        sus = calc_network_scores(sus_with_links, sus)
        sus = weight_network_scores(sus, net_weights)
    return sus


def get_eminence_score(suspects: pd.DataFrame) -> pd.DataFrame:
    """
    Assign an eminence score to each suspect based on existing data, defaulting to '1' where necessary.

    This function performs the following operations:
        1. Assigns a default eminence score of '1' where the 'eminence' field is missing or empty.
        2. Converts the 'em2' field to a float type.
        3. If a 'net_weight' column exists, adds its value to the 'em2' score, caps the score at '9',
           and fills any resulting missing values with '0'.
        4. Cleans up by removing the 'net_weight' column if it was used.

    Parameters:
        suspects (pd.DataFrame):
            DataFrame containing suspect information. Must include:
                - `suspect_id`: Unique identifier for each suspect.
                - `eminence`: Current eminence score (can be missing or empty).

    Returns:
        pd.DataFrame:
            The updated suspects DataFrame with an additional `em2` column representing the processed eminence score.

    Raises:
        RuntimeError:
            If any step in the processing fails due to missing columns or other issues.
    """
    try:
        # Log the initial state of the DataFrame
        logger.info(
            "Starting get_eminence_score with the following DataFrame columns:\n"
            f"suspects.columns = {list(suspects.columns)}"
        )

        # Define required columns for the DataFrame
        required_suspects_cols = {"suspect_id", "eminence"}

        # Validate required columns in suspects DataFrame
        missing_suspects_cols = required_suspects_cols - set(suspects.columns)
        if missing_suspects_cols:
            error_msg = f"suspects DataFrame is missing required columns: {missing_suspects_cols}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 1. Assign default eminence score where 'eminence' is missing
        logger.info(
            "Assigning default eminence score where 'eminence' is missing or empty."
        )
        suspects["em2"] = suspects["eminence"].fillna(1)
        suspects.loc[suspects["eminence"].astype(str).str.len() < 1, "em2"] = 1
        logger.debug(f"<<< Before converting 'em2' to float:\n{suspects['em2'].head()}")

        # 2. Convert 'em2' to float
        logger.info("Converting 'em2' to float type.")
        suspects["em2"] = suspects["em2"].astype(float)
        logger.debug(f">>> After converting 'em2' to float:\n{suspects['em2'].head()}")

        # 3. Handle 'net_weight' if it exists
        if "net_weight" in suspects.columns:
            logger.info("Processing 'net_weight' column for 'em2' score adjustment.")
            # Ensure 'net_weight' is numeric
            suspects["net_weight"] = pd.to_numeric(
                suspects["net_weight"], errors="coerce"
            ).fillna(0.0)
            logger.debug(
                f"<<< Before adjusting 'em2' with 'net_weight':\n{suspects[['em2', 'net_weight']].head()}"
            )

            # Add 'net_weight' to 'em2'
            suspects["em2"] += suspects["net_weight"]

            # Cap 'em2' at 9
            suspects["em2"] = np.where(suspects["em2"] > 9, 9, suspects["em2"])

            # Fill any remaining missing values with 0
            suspects["em2"] = suspects["em2"].fillna(0.0)
            logger.debug(
                f">>> After adjusting 'em2' with 'net_weight' and capping:\n{suspects['em2'].head()}"
            )

            # Remove the 'net_weight' column
            suspects.drop(columns=["net_weight"], inplace=True)
            logger.info("Removed 'net_weight' column after adjusting 'em2' score.")

        else:
            logger.info(
                "'net_weight' column not found. Skipping adjustment of 'em2' score."
            )

        logger.info("Successfully assigned and processed 'em2' eminence scores.")

    except ValueError as ve:
        logger.error(f"Value error in get_eminence_score: {ve}")
        raise RuntimeError(f"Value error in get_eminence_score: {ve}") from ve
    except KeyError as ke:
        logger.error(f"Key error in get_eminence_score: {ke}")
        raise RuntimeError(f"Key error in get_eminence_score: {ke}") from ke
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_eminence_score: {e}")
        raise RuntimeError(
            f"An unexpected error occurred in get_eminence_score: {e}"
        ) from e

    return suspects


def get_sus_located_in(sus, location):
    """Get subset of suspects who have a particular location mentioned in
    their address."""
    sus["loc"] = np.where(sus["Address"].str.contains(location), 1, 0)
    return sus


def get_new_soc_score(
    suspects: pd.DataFrame, states_of_charges: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge newly calculated Strength of Case (SOC) scores into the suspects DataFrame.

    This function performs the following operations:
        1. Validates the presence of required columns in the input DataFrames.
        2. Selects the necessary columns from the `states_of_charges` DataFrame.
        3. Merges the SOC scores into the `suspects` DataFrame based on `suspect_id`.
        4. Rounds the SOC scores to six decimal places.

    Parameters:
        suspects (pd.DataFrame):
            DataFrame containing suspect information. Must include:
                - `suspect_id`: Unique identifier for each suspect.

        states_of_charges (pd.DataFrame):
            DataFrame containing state of charge information. Must include:
                - `suspect_id`: Unique identifier for each suspect.
                - `soc`: Strength of Case score.

    Returns:
        pd.DataFrame:
            The updated suspects DataFrame with an additional `strength_of_case` column.

    Raises:
        RuntimeError:
            If any step in the merging process fails due to missing columns or other issues.
    """
    try:
        # Log the initial state of the DataFrames
        logger.info(
            "Starting get_new_soc_score with the following DataFrame columns:\n"
            f"suspects.columns = {list(suspects.columns)},\n"
            f"states_of_charges.columns = {list(states_of_charges.columns)}"
        )

        # Define required columns for each DataFrame
        required_suspects_cols = {"suspect_id"}
        required_soc_cols = {"suspect_id", "soc"}

        # Validate required columns in suspects DataFrame
        missing_suspects_cols = required_suspects_cols - set(suspects.columns)
        if missing_suspects_cols:
            error_msg = f"suspects DataFrame is missing required columns: {missing_suspects_cols}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Validate required columns in states_of_charges DataFrame
        missing_soc_cols = required_soc_cols - set(states_of_charges.columns)
        if missing_soc_cols:
            error_msg = f"states_of_charges DataFrame is missing required columns: {missing_soc_cols}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 1. Extract necessary columns from states_of_charges
        logger.info("Extracting 'suspect_id' and 'soc' columns from states_of_charges.")
        soc_df = states_of_charges[["suspect_id", "soc"]].copy()

        # Ensure 'soc' column is numeric
        logger.info("Ensuring 'soc' column is numeric.")
        soc_df["soc"] = pd.to_numeric(soc_df["soc"], errors="coerce")
        if soc_df["soc"].isnull().any():
            error_msg = "Some 'soc' entries could not be converted to numeric values."
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 2. Merge SOC scores into suspects DataFrame
        logger.info("Merging SOC scores into suspects DataFrame.")
        suspects = suspects.merge(soc_df, on="suspect_id", how="left")

        # 3. Handle missing SOC scores by filling with default value (e.g., 0.0)
        logger.info("Handling missing SOC scores by filling with 0.0.")
        suspects["soc"] = suspects["soc"].fillna(0.0)

        # 4. Round the SOC scores to six decimal places
        logger.info("Rounding 'soc' scores to six decimal places.")
        suspects["strength_of_case"] = suspects["soc"].round(decimals=6)

        # 5. Optionally, drop the original 'soc' column if no longer needed
        logger.info("Dropping the original 'soc' column.")
        suspects.drop(columns=["soc"], inplace=True)

        logger.info("Successfully merged SOC scores into suspects DataFrame.")

    except ValueError as ve:
        logger.error(f"Value error in get_new_soc_score: {ve}")
        raise RuntimeError(f"Value error in get_new_soc_score: {ve}") from ve
    except KeyError as ke:
        logger.error(f"Key error in get_new_soc_score: {ke}")
        raise RuntimeError(f"Key error in get_new_soc_score: {ke}") from ke
    except pd.errors.MergeError as me:
        logger.error(f"Merge error in get_new_soc_score: {me}")
        raise RuntimeError(f"Merge error in get_new_soc_score: {me}") from me
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_new_soc_score: {e}")
        raise RuntimeError(
            f"An unexpected error occurred in get_new_soc_score: {e}"
        ) from e

    return suspects


def calculate_weights(Parameters):
    """Get current weights from Parameters Google Sheet."""
    logger.error(
        f"<<< data_prep     weights_vs = ( \
        pd.Series(Parameters.iloc[0:16, 1]) \
        .replace('', 0) \
        .append(pd.Series(Parameters.iloc[0:3, 5])) \
        .astype(float) \
    )"
    )
    weights_vs = (
        pd.Series(Parameters.iloc[0:16, 1])
        .replace("", 0)
        .append(pd.Series(Parameters.iloc[0:3, 5]))
        .astype(float)
    )
    logger.error(
        f">>> data_prep     weights_vs = ( \
        pd.Series(Parameters.iloc[0:16, 1]) \
        .replace('', 0) \
        .append(pd.Series(Parameters.iloc[0:3, 5])) \
        .astype(float) \
    )"
    )
    weights_keys = pd.Series(Parameters.iloc[0:16, 0]).append(
        pd.Series(Parameters.iloc[0:3, 4])
    )
    weights = {k: v for k, v in zip(weights_keys, weights_vs)}
    return weights


import pandas as pd
import numpy as np
import logging
from typing import Any, Dict, List, Tuple

# Assuming the logger is already set up as per your provided setup_logger function
from .case_dispatcher_logging import setup_logger

# Initialize the existing logger
logger = setup_logger("data_prep_logging", "data_prep_logging")


def calc_solvability(suspects: pd.DataFrame, weights: Dict[str, Any]) -> pd.DataFrame:
    """
    Calculate a weighted solvability score for each active suspect.

    The solvability score is a composite metric derived from multiple factors related to the strength and
    progress of a case. Each factor is weighted according to predefined coefficients to reflect its
    importance in determining the overall solvability of the case.

    The function performs the following operations:
        1. Validates the presence of required columns in the input DataFrames.
        2. Computes weighted scores for each factor based on the provided weights.
        3. Aggregates the weighted scores to compute the final solvability score.
        4. Handles any missing values and ensures data consistency.

    Parameters:
        suspects (pd.DataFrame):
            DataFrame containing suspect information. Must include the following columns:
                - `v_mult`: Multiplier based on victims' willingness to testify.
                - `bio_known`: Indicator if bio and location of suspect are known.
                - `others_arrested`: Number of other suspects arrested in the case.
                - `willing_to_arrest`: Indicator if police are willing to arrest.
                - `recency_score`: Score representing the recency of the case.
                - `pv_believes`: Belief score regarding suspects' involvement.
                - `exp`: Exploitation score based on reported exploitation.
                - `suspect_id`: Unique identifier for each suspect.

        weights (Dict[str, Any]):
            Dictionary containing weight parameters for each factor. Must include the following keys:
                - `victim_willing_to_testify`: Weight for `v_mult`.
                - `bio_and_location_of_suspect`: Weight for `bio_known`.
                - `other_suspect(s)_arrested`: Weight for `others_arrested`.
                - `police_willing_to_arrest`: Weight for `willing_to_arrest`.
                - `recency_of_case`: Weight for `recency_score`.
                - `pv_believes`: Weight for `pv_believes`.
                - `exploitation_reported`: Weight for `exp`.

    Returns:
        pd.DataFrame:
            The updated suspects DataFrame with an additional `solvability` column representing the weighted solvability score.

    Raises:
        RuntimeError:
            If any step in the calculation process fails due to missing columns, data inconsistencies,
            or unexpected errors during processing.
    """
    try:
        # Log the initial state of the DataFrames and weights
        logger.info(
            "Starting calc_solvability with the following DataFrame columns:\n"
            f"suspects.columns = {list(suspects.columns)},\n"
            f"weights keys = {list(weights.keys())}"
        )

        # Define the factors and their corresponding weight keys
        factors: List[Tuple[str, str]] = [
            ("v_mult", "victim_willing_to_testify"),
            ("bio_known", "bio_and_location_of_suspect"),
            ("others_arrested", "other_suspect(s)_arrested"),
            ("willing_to_arrest", "police_willing_to_arrest"),
            ("recency_score", "recency_of_case"),
            ("pv_believes", "pv_believes"),
            ("exp", "exploitation_reported"),
        ]

        # Extract factor names and weight keys
        factor_columns: List[str] = [factor for factor, _ in factors]
        weight_keys: List[str] = [weight_key for _, weight_key in factors]

        # Validate required columns in suspects DataFrame
        missing_suspects_cols = set(factor_columns).union({"suspect_id"}) - set(
            suspects.columns
        )
        if missing_suspects_cols:
            error_msg = f"suspects DataFrame is missing required columns: {missing_suspects_cols}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required columns are present in suspects DataFrame.")

        # Validate required keys in weights dictionary
        missing_weights_keys = set(weight_keys) - set(weights.keys())
        if missing_weights_keys:
            error_msg = (
                f"weights dictionary is missing required keys: {missing_weights_keys}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required keys are present in weights dictionary.")

        # Ensure all weight values are numeric
        logger.info("Validating that all weight values are numeric.")
        for weight_key in weight_keys:
            if not isinstance(weights[weight_key], (int, float)):
                error_msg = f"Weight value for '{weight_key}' must be numeric."
                logger.error(error_msg)
                raise RuntimeError(error_msg)
        logger.info("All weight values are numeric.")

        # 1. Compute weighted scores for each factor
        logger.info("Calculating weighted scores for each factor.")
        weighted_scores: List[pd.Series] = []
        total_weight: float = sum(weights[weight_key] for weight_key in weight_keys)

        if total_weight == 0:
            error_msg = "The sum of all weight values is zero. Cannot compute solvability score."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        for factor, weight_key in factors:
            logger.debug(
                f"Processing factor '{factor}' with weight key '{weight_key}'."
            )
            # Fill NaN values with 0 for computation
            factor_series = suspects[factor].fillna(0).astype(float)
            weight = weights[weight_key]
            weighted_score = factor_series * weight
            weighted_scores.append(weighted_score)
            logger.debug(f"Weighted score for '{factor}':\n{weighted_score.head()}")

        # 2. Aggregate the weighted scores to compute the solvability score
        logger.info("Aggregating weighted scores to compute 'solvability' score.")
        total_weighted_score = sum(weighted_scores)
        suspects["solvability"] = total_weighted_score / total_weight
        logger.debug(
            f"Computed 'solvability' scores:\n{suspects['solvability'].head()}"
        )

        # 3. Handle any potential NaN values resulting from division
        suspects["solvability"] = suspects["solvability"].fillna(0.0).astype(float)
        logger.info("'solvability' scores calculated and NaN values handled.")

        # 4. Remove duplicate entries based on 'suspect_id'
        logger.info("Removing duplicate suspects based on 'suspect_id'.")
        before_dropping = len(suspects)
        suspects = suspects.drop_duplicates(subset="suspect_id")
        after_dropping = len(suspects)
        logger.info(f"Removed {before_dropping - after_dropping} duplicate suspects.")

    except RuntimeError as re:
        logger.error(f"Runtime error in calc_solvability: {re}")
        raise
    except KeyError as ke:
        error_msg = f"Key error in calc_solvability: {ke}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from ke
    except Exception as e:
        error_msg = f"An unexpected error occurred in calc_solvability: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

    logger.info("Successfully completed calc_solvability.")
    return suspects


import pandas as pd
import numpy as np
import logging
from typing import Any, Dict, List, Tuple

# Assuming the logger is already set up as per your provided setup_logger function
from .case_dispatcher_logging import setup_logger

# Initialize the existing logger
logger = setup_logger("data_prep_logging", "data_prep_logging")


def calc_priority(
    new_suspects: pd.DataFrame, weights: Dict[str, Any], existing_suspects: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate a weighted priority score for each active suspect and update the suspects DataFrame accordingly.

    The priority score is a composite metric derived from multiple factors such as solvability, strength of case,
    and eminence. Each factor is weighted according to predefined coefficients to reflect its importance in
    determining the overall priority of the suspect.

    The function performs the following operations:
        1. Validates the presence of required columns in the input DataFrames.
        2. Computes weighted scores for each factor based on the provided weights.
        3. Aggregates the weighted scores to compute the final priority score.
        4. Handles any missing values and ensures data consistency.
        5. Sorts the suspects based on the priority score in descending order.
        6. Aligns the columns of the updated suspects DataFrame with the existing suspects DataFrame.
        7. Removes duplicate entries based on 'suspect_id'.

    Parameters:
        new_suspects (pd.DataFrame):
            DataFrame containing updated suspect information. Must include:
                - `suspect_id`: Unique identifier for each suspect.
                - `solvability`: Solvability score of the case.
                - `strength_of_case`: Strength of the case score.
                - `em2`: Eminence score.

        weights (Dict[str, Any]):
            Dictionary containing weight parameters for each factor. Must include:
                - `solvability`: Weight for the `solvability` factor.
                - `strength_of_case`: Weight for the `strength_of_case` factor.
                - `eminence`: Weight for the `em2` (eminence) factor.

        existing_suspects (pd.DataFrame):
            DataFrame containing the original suspect information. Used to align columns in the updated suspects DataFrame.

    Returns:
        pd.DataFrame:
            The updated suspects DataFrame with an additional `priority` column representing the weighted priority score,
            sorted in descending order of priority.

    Raises:
        RuntimeError:
            If any step in the calculation process fails due to missing columns or other issues.
    """
    try:
        # Log the initial state of the DataFrames and weights
        logger.info(
            "Starting calc_priority with the following DataFrame columns:\n"
            f"existing_suspects.columns = {list(existing_suspects.columns)},\n"
            f"new_suspects.columns = {list(new_suspects.columns)},\n"
            f"weights keys = {list(weights.keys())}"
        )

        # Define the factors and their corresponding weight keys
        factors: List[Tuple[str, str]] = [
            ("solvability", "solvability"),
            ("strength_of_case", "strength_of_case"),
            ("em2", "eminence"),
        ]

        # Extract factor names and weight keys
        factor_columns: List[str] = [factor for factor, _ in factors]
        weight_keys: List[str] = [weight_key for _, weight_key in factors]

        # Validate required columns in new_suspects DataFrame
        required_new_suspects_cols = set(factor_columns).union({"suspect_id"})
        missing_new_suspects_cols = required_new_suspects_cols - set(
            new_suspects.columns
        )
        if missing_new_suspects_cols:
            error_msg = f"new_suspects DataFrame is missing required columns: {missing_new_suspects_cols}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required columns are present in new_suspects DataFrame.")

        # Validate required keys in weights dictionary
        missing_weights_keys = set(weight_keys) - set(weights.keys())
        if missing_weights_keys:
            error_msg = (
                f"weights dictionary is missing required keys: {missing_weights_keys}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required keys are present in weights dictionary.")

        # Ensure all weight values are numeric
        logger.info("Validating that all weight values are numeric.")
        for weight_key in weight_keys:
            if not isinstance(weights[weight_key], (int, float)):
                error_msg = f"Weight value for '{weight_key}' must be numeric."
                logger.error(error_msg)
                raise RuntimeError(error_msg)
        logger.info("All weight values are numeric.")

        # 1. Compute weighted scores for each factor
        logger.info("Calculating weighted scores for each factor.")
        weighted_scores: List[pd.Series] = []
        total_weight: float = sum(weights[weight_key] for weight_key in weight_keys)

        if total_weight == 0:
            error_msg = (
                "The sum of all weight values is zero. Cannot compute priority score."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        for factor, weight_key in factors:
            logger.debug(
                f"Processing factor '{factor}' with weight key '{weight_key}'."
            )
            # Fill NaN values with 0 for computation
            factor_series = new_suspects[factor].fillna(0).astype(float)
            weight = weights[weight_key]
            weighted_score = factor_series * weight
            weighted_scores.append(weighted_score)
            logger.debug(f"Weighted score for '{factor}':\n{weighted_score.head()}")

        # 2. Aggregate the weighted scores to compute the priority score
        logger.info("Aggregating weighted scores to compute 'priority' score.")
        total_weighted_score = sum(weighted_scores)
        new_suspects["priority"] = total_weighted_score / total_weight
        logger.debug(f"Computed 'priority' scores:\n{new_suspects['priority'].head()}")

        # 3. Handle any potential NaN values resulting from division
        new_suspects["priority"] = new_suspects["priority"].fillna(0.0).astype(float)
        logger.info("'priority' scores calculated and NaN values handled.")

        # 4. Sort suspects by priority in descending order
        logger.info("Sorting suspects by 'priority' in descending order.")
        new_suspects.sort_values("priority", ascending=False, inplace=True)
        logger.debug(f"Sorted 'priority' scores:\n{new_suspects['priority'].head()}")

        # 5. Align the columns of new_suspects with existing_suspects
        logger.info("Aligning columns of new_suspects with existing_suspects.")
        expected_columns = list(existing_suspects.columns)
        current_columns = list(new_suspects.columns)
        if len(current_columns) < len(expected_columns):
            # If new_suspects has fewer columns, pad with empty strings
            for col in expected_columns[len(current_columns) :]:
                new_suspects[col] = ""
            logger.debug("Added missing columns to align with existing_suspects.")
        elif len(current_columns) > len(expected_columns):
            # If new_suspects has more columns, truncate to match
            new_suspects = new_suspects.iloc[:, : len(expected_columns)]
            logger.debug("Truncated extra columns to align with existing_suspects.")
        else:
            # Reorder columns to match existing_suspects
            new_suspects = new_suspects[expected_columns]
            logger.debug("Reordered columns to align with existing_suspects.")

        logger.debug(f"Aligned columns: {list(new_suspects.columns)}")

        # 6. Remove duplicate entries based on 'suspect_id'
        logger.info("Removing duplicate suspects based on 'suspect_id'.")
        before_dropping = len(new_suspects)
        new_suspects = new_suspects.drop_duplicates(subset="suspect_id")
        after_dropping = len(new_suspects)
        logger.info(f"Removed {before_dropping - after_dropping} duplicate suspects.")

    except RuntimeError as re:
        logger.error(f"Runtime error in calc_priority: {re}")
        raise
    except KeyError as ke:
        error_msg = f"Key error in calc_priority: {ke}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from ke
    except Exception as e:
        error_msg = f"An unexpected error occurred in calc_priority: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

    logger.info("Successfully completed calc_priority.")
    return new_suspects


def truncate_rows(df, nrow=200):
    df = df.iloc[:nrow, :]
    return df


def calc_all_sus_scores(
    suspects_entity_active: pd.DataFrame,
    vics_willing: pd.DataFrame,
    pol: pd.DataFrame,
    weights: Dict[str, Any],
    soc_df: pd.DataFrame,
    google_sheets_suspects: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate and integrate comprehensive scores for active suspects.

    This function orchestrates the end-to-end calculation of multiple scores that evaluate various aspects of active suspects.
    By sequentially invoking specialized scoring functions, it enriches the `suspects_entity_active` DataFrame with
    comprehensive metrics that assess victim willingness, arrest dynamics, case recency, belief weights, exploitation,
    social influence, eminence, solvability, and overall priority. The cumulative effect of these scores provides a holistic
    view of each suspect's profile, enabling informed decision-making and prioritization.

    **Function Workflow:**

    1. **Victim Willingness Scores (`calc_vics_willing_scores`):**
        - Integrates victim willingness data into the suspects DataFrame.
        - Assigns a multiplier (`v_mult`) based on the number of victims willing to testify, enhancing the suspect's profile.

    2. **Arrest Scores (`calc_arrest_scores`):**
        - Evaluates the number of other suspects arrested in the case.
        - Determines if the suspect's bio and location are known (`bio_known`).
        - Assesses police willingness to arrest (`willing_to_arrest`).

    3. **Recency Scores (`calc_recency_scores`):**
        - Calculates the recency of the case based on days since the suspect's interview.
        - Generates a `recency_score` reflecting the timeliness of the case.

    4. **Belief Weights (`weight_pv_believes`):**
        - Computes a belief score (`pv_believes`) indicating the level of belief in the suspect's involvement in trafficking.

    5. **Exploitation Score (`get_exp_score`):**
        - Assesses the extent of exploitation reported against the suspect.
        - Incorporates various exploitation indicators into an `exp` score.

    6. **Strength of Case Score (`get_new_soc_score`):**
        - Merges and rounds the Strength of Case (`strength_of_case`) scores into the suspects DataFrame.

    7. **Eminence Score (`get_eminence_score`):**
        - Assigns an eminence score (`em2`) to each suspect, reflecting their prominence or influence.
        - Adjusts scores based on network weights if applicable.

    8. **Solvability Score (`calc_solvability`):**
        - Calculates a solvability score based on multiple factors, indicating the likelihood of resolving the case successfully.

    9. **Priority Score (`calc_priority`):**
        - Aggregates all previously computed scores to determine an overall priority (`priority`) for each suspect.
        - Sorts suspects in descending order of priority to facilitate focused action.

    **Net Effect:**
    The function sequentially enhances the `suspects_entity_active` DataFrame by appending various computed scores.
    The final DataFrame provides a multifaceted assessment of each suspect, enabling prioritization based on a
    combination of factors such as victim cooperation, arrest history, case recency, belief in involvement,
    exploitation levels, case strength, eminence, and overall solvability.
    This comprehensive scoring facilitates strategic decision-making and resource allocation in investigative processes.

    **Parameters:**
        suspects_entity_active (pd.DataFrame):
            DataFrame containing active suspect information. Must include a `case_id` column to uniquely identify each case.

        vics_willing (pd.DataFrame):
            DataFrame containing victim willingness data. Must include `case_id` and `count` columns, where `count` indicates
            the number of victims willing to testify.

        pol (pd.DataFrame):
            DataFrame containing police-related information necessary for calculating arrest scores. Must include relevant
            `case_id` and `case_status` columns.

        weights (pd.DataFrame):
            DataFrame containing weight parameters used across various scoring functions. Must include all necessary weight
            columns as referenced by the individual scoring functions.

        soc_df (pd.DataFrame):
            DataFrame containing social and case-related data relevant to scoring. Must include necessary identifiers and
            metrics required by the scoring functions.

        google_sheets_suspects (pd.DataFrame):
            DataFrame containing suspect information sourced from Google Sheets. Used specifically in the priority calculation
            to align and integrate additional suspect data.

    Returns:
        pd.DataFrame:
            The enriched `suspects_entity_active` DataFrame with all calculated scores appended as new columns. These
            scores include `v_mult`, `bio_known`, `others_arrested`, `willing_to_arrest`, `recency_score`,
            `pv_believes`, `exp`, `strength_of_case`, `em2`, `solvability`, and `priority`.

    Raises:
        RuntimeError:
            If any of the scoring functions encounter issues such as missing required columns, data inconsistencies,
            or unexpected errors during processing. The error message will indicate the specific step and nature of the
            failure to aid in debugging and resolution.
    """
    try:
        # Log the initial state of the DataFrames
        logger.info(
            f"Starting calc_all_sus_scores with the following DataFrame columns:\n"
            f"suspects_entity_active.columns = {list(suspects_entity_active.columns)},\n"
            f"vics_willing.columns = {list(vics_willing.columns)},\n"
            f"pol.columns = {list(pol.columns)},\n"
            f"soc_df.columns = {list(soc_df.columns)},\n"
            f"google_sheets_suspects.columns = {list(google_sheets_suspects.columns)}"
        )

        # Select only required columns for calc_vics_willing_scores
        required_vics_columns = {"case_id", "count"}
        if not required_vics_columns.issubset(vics_willing.columns):
            missing = required_vics_columns - set(vics_willing.columns)
            error_msg = f"vics_willing is missing required columns: {missing}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Create a subset of vics_willing with only the required columns
        vics_willing_subset = vics_willing[list(required_vics_columns)].copy()

        # 1. Calculate victim willingness scores
        suspects_entity_active = calc_vics_willing_scores(
            suspects=suspects_entity_active, vics_willing=vics_willing_subset
        )
        logger.info("Completed calc_vics_willing_scores.")

        # 2. Calculate arrest scores
        suspects_entity_active = calc_arrest_scores(suspects_entity_active, soc_df, pol)
        logger.info("Completed calc_arrest_scores.")

        # 3. Calculate recency scores
        suspects_entity_active = calc_recency_scores(
            suspects_entity_active, soc_df, weights
        )
        logger.info("Completed calc_recency_scores.")

        # 4. Weight belief scores
        suspects_entity_active = weight_pv_believes(
            suspects_entity_active, soc_df, weights
        )
        logger.info("Completed weight_pv_believes.")

        # 5. Calculate exploitation scores
        suspects_entity_active = get_exp_score(suspects_entity_active, soc_df, weights)
        logger.info("Completed get_exp_score.")

        # 6. Merge and round Strength of Case (SOC) scores
        suspects_entity_active = get_new_soc_score(suspects_entity_active, soc_df)
        logger.info("Completed get_new_soc_score.")

        # 7. Assign and adjust eminence scores
        suspects_entity_active = get_eminence_score(suspects_entity_active)
        logger.info("Completed get_eminence_score.")

        # 8. Calculate solvability scores
        suspects_entity_active = calc_solvability(suspects_entity_active, weights)
        logger.info("Completed calc_solvability.")

        # Log the number of suspects before priority calculation
        logger.info(
            f"BEFORE calc_priority: Number of suspects = {len(suspects_entity_active)}"
        )

        # 9. Calculate priority scores
        suspects_entity_active = calc_priority(
            suspects_entity_active, weights, google_sheets_suspects
        )
        logger.info("Completed calc_priority.")

        # Log the number of suspects after priority calculation
        logger.info(
            f"AFTER calc_priority: Number of suspects = {len(suspects_entity_active)}"
        )

    except ValueError as ve:
        logger.error(f"Value error in calc_all_sus_scores: {ve}")
        raise RuntimeError(f"Value error in calc_all_sus_scores: {ve}") from ve
    except KeyError as ke:
        logger.error(f"Key error in calc_all_sus_scores: {ke}")
        raise RuntimeError(f"Key error in calc_all_sus_scores: {ke}") from ke
    except pd.errors.MergeError as me:
        logger.error(f"Merge error in calc_all_sus_scores: {me}")
        raise RuntimeError(f"Merge error in calc_all_sus_scores: {me}") from me
    except Exception as e:
        logger.error(f"An unexpected error occurred in calc_all_sus_scores: {e}")
        raise RuntimeError(
            f"An unexpected error occurred in calc_all_sus_scores: {e}"
        ) from e

    logger.info("Successfully completed calc_all_sus_scores.")
    return suspects_entity_active


def add_priority_to_others(
    sus: pd.DataFrame,
    other_entity_group: pd.DataFrame,
    id_type: str,
    entity_gsheet: pd.DataFrame,
    uid: str,
) -> pd.DataFrame:
    """
    Integrate priority scores from suspects into other active entity sheets.

    This function merges the `sus` DataFrame containing priority scores with the `other_entity_group` DataFrame
    based on a specified identifier (`id_type`). It adds a new column `suspects_identified_and_located`
    containing a comma-separated list of suspects identified and located. The function also ensures that
    the resulting DataFrame aligns with the structure of `entity_gsheet` by matching the number of columns
    and handling duplicates based on a unique identifier (`uid`).

    Parameters:
        sus (pd.DataFrame):
            DataFrame containing suspect information. Must include the following columns:
                - `id_type`: Identifier used to merge with other_entity_group (e.g., 'case_id').
                - `priority`: Priority score assigned to each suspect.
                - `narrative`: Narrative or description related to the suspect.

        other_entity_group (pd.DataFrame):
            DataFrame representing other active entities (e.g., police, cases) to which priority scores will be added.
            Must include the following column:
                - `id_type`: Identifier used to merge with the sus DataFrame.

        id_type (str):
            The name of the identifier column used for merging (e.g., 'case_id').

        entity_gsheet (pd.DataFrame):
            Reference DataFrame (e.g., from Google Sheets) that defines the expected structure of the resulting DataFrame.

        uid (str):
            The name of the unique identifier column used to remove duplicate entries (e.g., 'unique_id').

    Returns:
        pd.DataFrame:
            The updated `other_entity_group` DataFrame with an additional `suspects_identified_and_located` column.
            The DataFrame is sorted in descending order of priority and aligned with the structure of `entity_gsheet`.
            If no priority scores are available, the original `other_entity_group` is returned unmodified.

    Raises:
        RuntimeError:
            If required columns are missing from the input DataFrames or if the merge operation fails.
    """
    try:
        logger.info("Starting integration of priority scores into other entity sheets.")

        # Define required columns for sus
        required_sus_columns = {id_type, "priority", "narrative"}
        missing_sus_columns = required_sus_columns - set(sus.columns)
        if missing_sus_columns:
            error_msg = (
                f"sus DataFrame is missing required columns: {missing_sus_columns}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("All required columns are present in sus DataFrame.")

        # Define required columns for other_entity_group
        required_other_columns = {id_type}
        missing_other_columns = required_other_columns - set(other_entity_group.columns)
        if missing_other_columns:
            error_msg = f"other_entity_group DataFrame is missing required columns: {missing_other_columns}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug(
            "All required columns are present in other_entity_group DataFrame."
        )

        # Define required columns for entity_gsheet
        if entity_gsheet.empty:
            error_msg = "entity_gsheet DataFrame is empty. Cannot align columns."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.debug("entity_gsheet DataFrame is non-empty.")

        # Merge sus with other_entity_group on id_type using outer join
        logger.info("Merging sus DataFrame with other_entity_group DataFrame.")
        merged_df = pd.merge(
            other_entity_group,
            sus[[id_type, "priority", "narrative"]],
            how="outer",
            on=id_type,
            validate="many_to_one",  # Assuming each id_type in other_entity_group is unique
        )
        logger.debug("Merge operation completed successfully.")

        # Filter out rows where priority is empty string
        logger.info("Filtering out entries with empty priority scores.")
        filtered_df = merged_df[merged_df["priority"] != ""].copy()
        logger.debug(f"Number of records after filtering: {len(filtered_df)}")

        # Fill NaN priority scores with 0 and convert to float
        logger.info("Filling missing priority scores with 0 and converting to float.")
        filtered_df["priority"] = filtered_df["priority"].fillna(0).astype(float)
        logger.debug("Priority scores filled and converted to float.")

        # Rename 'narrative_y' to 'narrative'
        narrative_y_exists = "narrative_y" in filtered_df.columns
        if narrative_y_exists:
            logger.info("Renaming 'narrative_y' to 'narrative'.")
            filtered_df["narrative_x"] = filtered_df["narrative_y"]
            filtered_df.rename(columns={"narrative_x": "narrative"}, inplace=True)
            logger.debug("Renaming completed.")
        else:
            logger.warning(
                "'narrative_y' column not found after merge. 'narrative' may be missing or differently named."
            )

        # Remove duplicate entries based on uid
        if uid not in filtered_df.columns:
            error_msg = (
                f"Unique identifier column '{uid}' not found in the merged DataFrame."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.info(f"Removing duplicate entries based on '{uid}'.")
        before_dropping = len(filtered_df)
        filtered_df.drop_duplicates(subset=uid, inplace=True)
        after_dropping = len(filtered_df)
        logger.debug(f"Removed {before_dropping - after_dropping} duplicate entries.")

        # Sort the DataFrame by priority in descending order
        logger.info("Sorting DataFrame by priority in descending order.")
        filtered_df.sort_values("priority", ascending=False, inplace=True)
        logger.debug("Sorting completed.")

        # Align the columns with entity_gsheet by selecting the first N columns and filling NaNs with empty strings
        expected_columns = list(entity_gsheet.columns)
        current_columns = list(filtered_df.columns)
        logger.info("Aligning columns with entity_gsheet structure.")
        if len(current_columns) < len(expected_columns):
            # If filtered_df has fewer columns, add missing columns with empty strings
            for col in expected_columns[len(current_columns) :]:
                filtered_df[col] = ""
            logger.debug("Added missing columns to align with entity_gsheet.")
        elif len(current_columns) > len(expected_columns):
            # If filtered_df has more columns, truncate to match
            filtered_df = filtered_df.iloc[:, : len(expected_columns)]
            logger.debug("Truncated extra columns to align with entity_gsheet.")
        else:
            # Reorder columns to match entity_gsheet
            filtered_df = filtered_df[expected_columns]
            logger.debug("Reordered columns to align with entity_gsheet.")

        # Fill any remaining NaN values with empty strings
        filtered_df.fillna("", inplace=True)
        logger.debug("Filled remaining NaN values with empty strings.")

        logger.info(
            "Completed integration of priority scores into other entity sheets."
        )
        return filtered_df

    except pd.errors.MergeError as me:
        error_msg = f"Merge error during add_priority_to_others: {me}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from me
    except KeyError as ke:
        error_msg = f"Key error during add_priority_to_others: {ke}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from ke
    except Exception as e:
        error_msg = f"An unexpected error occurred in add_priority_to_others: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def update_status_based_on_conditions(row, condition_tuples):
    for condition_set, status in condition_tuples:
        if row["case_id"] in condition_set:
            return status
    return ""


def update_active_cases(
    active_suspects: pd.DataFrame, active_police: pd.DataFrame
) -> pd.DataFrame:
    """
    Updates active cases based on the status and actions of suspects and police.

    Parameters:
    active_suspects (pd.DataFrame): A DataFrame containing information about active suspects.
    active_police (pd.DataFrame): A DataFrame containing information about active police actions.

    Returns:
    pd.DataFrame: A DataFrame with updated active cases information.
    """

    # Select only relevant columns from active_suspects
    active_police.loc[active_police["case_status"] == "nan", "case_status"] = ""
    active_suspects.loc[active_suspects["case_status"] == "nan", "case_status"] = ""

    active_cases = active_suspects[
        [
            "case_id",
            "case_name",
            "priority",
            "irf_case_notes",
            "narrative",
            "case_status",
        ]
    ].copy()
    active_cases.loc[:, "case_status"] = active_cases.loc[:, "case_status"].fillna("")
    active_cases.loc[active_cases["case_status"] == "nan", "case_status"] = ""
    # Create a mask for each condition
    police_complete = active_police[active_police.case_status.str.contains("Complete")][
        "case_id"
    ]
    suspect_complete = active_suspects[
        active_suspects.case_status.str.contains("Complete")
    ]["case_id"]
    multiple_victims = active_suspects[
        active_suspects.victims_willing_to_testify.str.contains(",")
    ]["case_id"]
    single_victim = active_suspects[
        (active_suspects.victims_willing_to_testify != "")
        | (active_suspects.victims_willing_to_testify.isna())
    ]["case_id"]

    # Update 'Case_Status' based on the conditions
    active_cases.loc[active_cases.case_id.isin(police_complete), "case_status"] = (
        "Third Step Complete - Police are willing to arrest suspect."
    )
    active_cases.loc[active_cases.case_id.isin(suspect_complete), "case_status"] = (
        "Second Step Complete: Suspect Located"
    )
    active_cases.loc[active_cases.case_id.isin(multiple_victims), "case_status"] = (
        "First Step Complete: Two or more PVs willing to testify"
    )
    active_cases.loc[active_cases.case_id.isin(single_victim), "case_status"] = (
        "First Step Complete: One PV willing to testify"
    )

    # Update 'Next_Action_Priority' based on the conditions
    active_cases["Next_Action_Priority"] = ""
    active_cases.loc[
        active_cases.case_id.isin(police_complete), "Next_Action_Priority"
    ] = "Ensure Arrest is Made"
    active_cases.loc[
        active_cases.case_id.isin(suspect_complete), "Next_Action_Priority"
    ] = "Ask Police to Arrest"
    active_cases.loc[
        active_cases.case_id.isin(single_victim), "Next_Action_Priority"
    ] = "Locate Suspect"
    active_cases.loc[
        ~active_cases.case_id.isin(single_victim), "Next_Action_Priority"
    ] = "Contact Victim"

    # Drop duplicates based on 'Case_ID'
    active_cases = active_cases.drop_duplicates("case_id")

    return active_cases


def update_active_cases_2(active_suspects, active_police):
    """
    This function updates the status and next action priority for active human trafficking cases.
    It takes in two dataframes: active_suspects and active_police.
    """

    def get_status_conditions():
        is_in_completed_police_cases = active_cases.case_id.isin(
            active_police[active_police.case_status.str.contains("Complete")]["case_id"]
        )
        is_in_completed_suspect_cases = active_cases.case_id.isin(
            active_suspects[active_suspects.case_status.str.contains("Complete")][
                "case_id"
            ]
        )
        has_multiple_victims_willing = active_cases.case_id.isin(
            active_suspects[
                active_suspects.victims_willing_to_testify.str.contains(",")
            ]["case_id"]
        )
        has_at_least_one_victim_willing = active_cases.case_id.isin(
            active_suspects[pd.notna(active_suspects.victims_willing_to_testify)][
                "case_id"
            ]
        )
        logger.info(
            f"get_status_conditions: {active_suspects.victims_willing_to_testify.value_counts()}"
        )

        return [
            is_in_completed_police_cases,
            is_in_completed_suspect_cases,
            has_multiple_victims_willing,
            has_at_least_one_victim_willing,
        ]

    def get_next_action_conditions():
        return get_status_conditions()[:-1]  # Exclude the last condition

    # Extract relevant columns
    active_cases = active_suspects[
        [
            "case_id",
            "case_name",
            "priority",
            "irf_case_notes",
            "narrative",
            "case_status",
        ]
    ].copy()

    # Define status values
    case_status_values = [
        "Third Step Complete - Police are willing to arrest suspect.",
        "Second Step Complete: Suspect Located",
        "First Step Complete: Two or more PVs willing to testify",
        "First Step Complete: One PV willing to testify",
    ]

    # Define next action values
    next_action_priority_values = [
        "Ensure Arrest is Made",
        "Ask Police to Arrest",
        "Locate Suspect",
    ]

    # Update Case_Status and Next_Action_Priority columns
    active_cases["case_status"] = np.select(
        get_status_conditions(), case_status_values, default=""
    )
    active_cases["next_action_priority"] = np.select(
        get_next_action_conditions(),
        next_action_priority_values,
        default="Contact Victim",
    )

    # Remove duplicates
    active_cases.drop_duplicates("case_id", inplace=True)

    return active_cases
