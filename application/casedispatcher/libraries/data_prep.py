# data_prep.py
import streamlit as st
import pandas as pd
import re
from copy import deepcopy
from .case_dispatcher_logging import setup_logger
from datetime import date

logger = setup_logger("data_prep_logging", "data_prep_logging")


def do_audit(audit_series, description="audit"):
    if st.session_state["include_audit"] == "Yes":
        # audit = audit_series.isin([st.session_state['irf_audit_number']])
        audit = st.session_state["irf_audit_number"] in audit_series.values
        st.write(
            f"irf_audit_number = {st.session_state['irf_audit_number']} is in db_irf: {audit}, with description '{description}'"
        )


def add_country_stats(model_data, country_stats):
    # Simplify country replacement using `np.where`
    import numpy as np

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
                "sf_number_group",
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
    """Creates a unique ID for each suspect from Case ID and subsets/renames columns."""

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
        "sf_number_group",
        "case_notes",
    ]
    column_rename = {
        "full_name": "name",
        "phone_contact": "phone_numbers",
        "address_notes": "address",
        "social_media": "social_media_id",
        "sf_number": "case_id",
        "case_notes": "narrative",
        "suspect_id": "suspect_id",
    }

    # Subset columns
    filtered_new_suspects = new_suspects[new_suspect_cols]
    filtered_db_suspects = db_suspects[db_suspect_cols]

    # Merge dataframes
    merged_suspects = pd.merge(
        filtered_new_suspects,
        filtered_db_suspects,
        how="outer",
        on="person_id",
        sort=True,
        suffixes=("x", "y"),
    )

    # Drop duplicates and select final columns
    merged_suspects.rename(columns=column_rename, inplace=True)
    merged_suspects = merged_suspects.drop_duplicates(subset="suspect_id")
    merged_suspects = merged_suspects[list(column_rename.values())]

    # Rename columns

    return merged_suspects


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


def get_vics_willing_to_testify(victims):
    """Get subset of victims who have indicated they're willing to testify
    against traffickers."""
    vics_willing = victims.loc[
        victims["case_status"] == "Step Complete: Victim is willing to press charges"
    ]
    if len(vics_willing) > 0:
        vics_willing = vics_willing[["case_id", "name"]]
        vics_willing.rename(columns={"name": "willing_to_testify"}, inplace=True)
        vics_willing["count"] = 1
        vics_willing = vics_willing.groupby("case_id").apply(sum_and_join_vic)
    else:
        vics_willing["willing_to_testify"] = ""
    return vics_willing


def add_vic_names(target_sheet, vics_willing):
    """Add comma separated list of victims willing to testify to active police
    or suspect sheet."""
    if len(vics_willing) > 0:
        target_sheet = pd.merge(target_sheet, vics_willing, how="left", on="case_id")
        target_sheet["victims_willing_to_testify"] = target_sheet[
            "willing_to_testify"
        ].fillna("")
        target_sheet.drop(columns=["willing_to_testify", "count"], inplace=True)
    return target_sheet


def get_sus_located(suspects):
    """Get subset of suspects who have been identified and located."""
    sus_located = suspects.loc[
        suspects.case_status.str.contains("Step Complete", na=False)
    ]
    if len(sus_located) > 0:
        sus_located = sus_located[["case_id", "name"]]
        sus_located.rename(columns={"name": "located"}, inplace=True)
        sus_located["count"] = 1
        sus_located = sus_located.groupby("case_id").apply(sum_and_join_sus)
    return sus_located


def add_sus_located(target_sheet, sus_located):
    """Add comma separated list of suspects identified and located to other
    sheet."""
    if len(sus_located) > 0:
        target_sheet = pd.merge(target_sheet, sus_located, how="left", on="case_id")
        target_sheet["suspects_identified_and_located"] = target_sheet[
            "located"
        ].fillna("")
        target_sheet.drop(columns=["located", "count"], inplace=True)
    return target_sheet


import pandas as pd


def calc_vics_willing_scores(suspects, vics_willing):
    """Calculate scores for the number of victims willing to testify and add them to the suspect sheet."""

    # Define victim multiplier
    v_mult = {0: 0, 1: 0.5, 7: 1}
    for i in range(2, 7):
        v_mult[i] = v_mult[i - 1] + (1 - v_mult[i - 1]) * 0.5

    if not vics_willing.empty:
        # Merge data
        suspects = pd.merge(suspects, vics_willing, how="left", on="case_id")
        suspects["count"] = suspects["count"].fillna(0).astype(int)

        # Map counts to multipliers
        suspects["v_mult"] = suspects["count"].map(v_mult.get).fillna(0.0).astype(float)

        # Drop unnecessary columns
        suspects.drop(columns=["willing_to_testify", "count"], inplace=True)
    else:
        suspects["v_mult"] = 0.0

    return suspects


def calc_arrest_scores(suspects, states_of_charge, police):
    """Calculate scores based on the number of other suspects arrested in each case,
    and create fields for 'bio known' and for police willingness to arrest."""

    # Setting the 'Bio_Known' column
    suspects["bio_known"] = (
        suspects["case_status"] != "Step Complete: Identity and Location Confirmed"
    ).astype(int)

    # Fetching and merging arrest data
    arrests = get_total_arrests(states_of_charge[["sf_number_group", "arrested"]])
    suspects = suspects.merge(arrests, on="case_id", how="left")
    suspects["others_arrested"] = suspects.pop("total_arrests").fillna(0).astype(int)

    # Identifying police willingness to arrest
    police["willing_to_arrest"] = (
        police["case_status"].str.contains("Step Complete", na=False).astype(int)
    )

    # Merging police willingness data
    suspects = suspects.merge(
        police[["case_id", "willing_to_arrest"]], on="case_id", how="left"
    )

    return suspects


def get_total_arrests(soc_df):
    """Create case_id from suspect_id and aggregate arrests. ['sf_number_group',
    'case_id', 'arrested']"""

    # Create case_id from sf_number_group and aggregate arrests
    arrests = soc_df.assign(case_id=soc_df["sf_number_group"])
    arrests = arrests.groupby("case_id")["arrested"].sum().reset_index()
    arrests.columns = ["case_id", "total_arrests"]

    return arrests


import numpy as np


def weight_pv_believes(suspects, states_of_charge, pv_believes):
    """Weight beliefs about suspects' involvement in trafficking."""

    # Extract and compute the "pv_believes" score
    pvb = states_of_charge[
        [
            "sf_number",
            "pv_believes_definitely_trafficked_many",
            "pv_believes_trafficked_some",
            "pv_believes_suspect_trafficker",
        ]
    ].copy()

    conditions = [
        pvb["pv_believes_definitely_trafficked_many"],
        pvb["pv_believes_trafficked_some"],
        pvb["pv_believes_suspect_trafficker"],
    ]
    choices = [pv_believes[col] for col in pvb.columns[1:]]
    pvb["pv_believes"] = np.select(conditions, choices, default=0)

    # Process the Case ID
    pvb["case_id"] = pvb["sf_number"].str.rstrip(".").replace(".", "", regex=True)

    # Clean up and finalize the data
    logger.error(f"<<< data_prep pvb['pv_believes']")
    pvb = pvb[["case_id", "pv_believes"]].copy()
    pvb["pv_believes"] = pvb["pv_believes"].astype(float)
    logger.error(f">>> data_prep pvb['pv_believes']")
    pvb.drop_duplicates(subset="case_id", inplace=True)

    # Merging the data
    suspects = suspects.merge(pvb, on="case_id", how="left")

    return suspects


import numpy as np


def get_exp_score(suspects, states_of_charges, exploitation_type):
    """Calculate exploitation score based on parameters and reported exploitation."""

    # Extract relevant columns and data
    exp_cols = [col for col in states_of_charges.columns if "exploitation" in col] + [
        "sf_number"
    ]
    exp_df = states_of_charges[exp_cols].copy()
    exp_df["exp"] = 0

    # Compute the exploitation score
    for col in exp_cols:
        if col in exploitation_type:
            exp_df["exp"] += (exp_df[col] == True) * exploitation_type[col]

    # Process the Case ID and finalize the data
    exp_df["case_id"] = exp_df["sf_number"].str.rstrip(".").replace(".", "", regex=True)
    exp_df = exp_df[["case_id", "exp"]].copy()
    logger.error(f"<<< data_prep exp_df['exp'].astype(float)")
    exp_df["exp"] = exp_df["exp"].astype(float)
    logger.error(f">>> data_prep exp_df['exp'].astype(float)")
    exp_df.drop_duplicates(subset="case_id", inplace=True)

    # Merge suspect data with the exploitation score data
    suspects = suspects.merge(exp_df, on="case_id", how="left")

    return suspects


def calc_recency_scores(suspects, states_of_charge, weights):
    """Assign score to each case that is higher the more recent it is."""

    # Calculate days since interview
    today = pd.Timestamp.now().normalize()
    cif_dates = states_of_charge[["sf_number", "interview_date"]].copy()
    cif_dates["interview_date"] = pd.to_datetime(cif_dates["interview_date"])
    cif_dates["days_old"] = (today - cif_dates["interview_date"]).dt.days
    cif_dates["case_id"] = (
        cif_dates["sf_number"].str.rstrip(".").replace(".", "", regex=True)
    )

    # Merge suspects data with days since interview
    suspects = suspects.merge(
        cif_dates[["case_id", "days_old"]], on="case_id", how="left"
    )

    # Calculate the Recency Score
    coef, exp = weights["discount_coef"], weights["discount_exp"]
    score_formula = 1 - coef * suspects["days_old"] ** exp
    suspects["recency_score"] = np.maximum(score_formula, 0)

    # Remove duplicate entries based on Suspect_ID
    suspects = suspects.drop_duplicates(subset="suspect_id")

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


def get_eminence_score(suspects):
    """Get eminence score from active sheet, if blank enter '1'."""
    suspects["em2"] = suspects["eminence"].fillna(1)
    suspects.loc[suspects["eminence"].str.len() < 1, "em2"] = 1
    logger.error(f">>> data_prep sus['em2'] = sus['em2'].astype(float)")
    suspects["em2"] = suspects["em2"].astype(float)
    logger.error(f"<<< data_prep sus['em2'] = sus['em2'].astype(float)")
    if "net_weight" in suspects:
        suspects["em2"] += suspects["net_weight"]
        suspects["em2"] = np.where(suspects["em2"] > 9, 9, suspects["em2"])
        suspects["em2"] = suspects["em2"].fillna(0)
        suspects.drop(columns=["net_weight"], inplace=True)
    return suspects


def get_sus_located_in(sus, location):
    """Get subset of suspects who have a particular location mentioned in
    their address."""
    sus["loc"] = np.where(sus["Address"].str.contains(location), 1, 0)
    return sus


def get_new_soc_score(suspects, states_of_charges):
    """Merge newly calculated Strength of Case scores to suspects sheet."""
    suspects = pd.merge(
        suspects,
        states_of_charges[["suspect_id", "soc"]],
        how="left",
        left_on="suspect_id",
        right_on="suspect_id",
    )
    suspects["strength_of_case"] = suspects["soc"].round(decimals=3)
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


def calc_solvability(suspects, weights):
    """Calculate weighted solvability score on active suspects."""

    factors = [
        ("v_mult", "victim_willing_to_testify"),
        ("bio_known", "bio_and_location_of_suspect"),
        ("others_arrested", "other_suspect(s)_arrested"),
        ("willing_to_arrest", "police_willing_to_arrest"),
        ("recency_score", "recency_of_case"),
        ("pv_believes", "pv_believes"),
        ("exp", "exploitation_reported"),
    ]

    weighted_scores = [
        suspects[factor].fillna(0) * weights[weight_key]
        for factor, weight_key in factors
    ]

    suspects["solvability"] = sum(weighted_scores) / sum(weights.values())

    return suspects


def calc_priority(new_suspects, weights, existing_suspects):
    """Calculate weighted priority score on active suspects."""
    logger.info(f"""existing_suspects.columns {existing_suspects.columns}""")
    logger.info(f"""new_suspects.columns {new_suspects.columns}""")
    factors = [
        ("solvability", weights["solvability"]),
        ("strength_of_case", weights["strength_of_case"]),
        ("em2", 0.1 * weights["eminence"]),
    ]

    weighted_scores = [new_suspects[factor] * weight for factor, weight in factors]

    logger.info(f"""new_suspects.columns {new_suspects.columns}""")
    new_suspects["priority"] = sum(weighted_scores).round(decimals=3)

    logger.info(f"""new_suspects.columns {new_suspects.columns}""")
    new_suspects["priority"] = new_suspects["priority"].fillna(0)

    logger.info(f"""new_suspects.columns {new_suspects.columns}""")
    new_suspects.sort_values("priority", ascending=False, inplace=True)

    logger.info(f"""new_suspects.columns {new_suspects.columns}""")
    # new_suspects = new_suspects[existing_suspects.columns].fillna("").drop_duplicates(subset="suspect_id")
    new_suspects = (
        new_suspects.iloc[:, 0 : len(existing_suspects.columns)]
        .fillna("")
        .drop_duplicates(subset="suspect_id")
    )
    logger.info(f"""new_suspects.columns {new_suspects.columns}""")
    return new_suspects


def truncate_rows(df, nrow=200):
    df = df.iloc[:nrow, :]
    return df


def calc_all_sus_scores(
    suspects_entity_active, vics_willing, pol, weights, soc_df, google_sheets_suspects
):
    """Complete all suspect sheet calculations in priority_calc module."""

    def record_columns(
        description, new_columns, current_columns, original_columns, counter
    ):
        current_difference = list(set(new_columns) - set(current_columns))
        current_columns = new_columns
        original_difference = list(set(current_columns) - set(original_columns))
        logger.info(f""" {counter}. after {description} sus.columns = {new_columns}""")
        logger.info(
            f""" {counter}. after {description} current_differences = {current_difference}"""
        )
        logger.info(
            f""" {counter}. after {description} original_difference = {original_difference}"""
        )
        return current_columns, original_columns

    original_columns = suspects_entity_active.columns
    current_columns = suspects_entity_active.columns
    logger.info(
        f"""at start of calc_all_sus_scores
    sus.columns = {suspects_entity_active.columns}, \
    vics_willing.columns = {vics_willing.columns}, \
    pol.columns = {pol.columns}, \
    soc_df.columns = {soc_df.columns}, \
    Supects.columns = {google_sheets_suspects.columns}
    """
    )

    suspects_entity_active = calc_vics_willing_scores(
        suspects_entity_active, vics_willing
    )
    record_columns(
        "calc_vics_willing_scores",
        suspects_entity_active.columns,
        current_columns,
        original_columns,
        1,
    )
    current_columns = suspects_entity_active.columns

    suspects_entity_active = calc_arrest_scores(suspects_entity_active, soc_df, pol)
    record_columns(
        "calc_arrest_scores",
        suspects_entity_active.columns,
        current_columns,
        original_columns,
        2,
    )
    current_columns = suspects_entity_active.columns

    suspects_entity_active = calc_recency_scores(
        suspects_entity_active, soc_df, weights
    )
    record_columns(
        "calc_recency_scores",
        suspects_entity_active.columns,
        current_columns,
        original_columns,
        3,
    )
    current_columns = suspects_entity_active.columns

    suspects_entity_active = weight_pv_believes(suspects_entity_active, soc_df, weights)
    record_columns(
        "weight_pv_believes",
        suspects_entity_active.columns,
        current_columns,
        original_columns,
        4,
    )
    current_columns = suspects_entity_active.columns

    suspects_entity_active = get_exp_score(suspects_entity_active, soc_df, weights)
    record_columns(
        "get_exp_score",
        suspects_entity_active.columns,
        current_columns,
        original_columns,
        5,
    )
    current_columns = suspects_entity_active.columns

    suspects_entity_active = get_new_soc_score(suspects_entity_active, soc_df)
    record_columns(
        "get_new_soc_score",
        suspects_entity_active.columns,
        current_columns,
        original_columns,
        6,
    )
    current_columns = suspects_entity_active.columns

    suspects_entity_active = get_eminence_score(suspects_entity_active)
    record_columns(
        "get_eminence_score",
        suspects_entity_active.columns,
        current_columns,
        original_columns,
        7,
    )
    current_columns = suspects_entity_active.columns

    suspects_entity_active = calc_solvability(suspects_entity_active, weights)
    record_columns(
        "calc_solvability",
        suspects_entity_active.columns,
        current_columns,
        original_columns,
        8,
    )
    current_columns = suspects_entity_active.columns

    logger.info(
        f""" BEFORE calc_priority len(suspects_entity_active) {len(suspects_entity_active)}"""
    )
    suspects_entity_active = calc_priority(
        suspects_entity_active, weights, google_sheets_suspects
    )
    logger.info(
        f"""AFTER calc_priority len(suspects_entity_active) {len(suspects_entity_active)}"""
    )

    record_columns(
        "calc_priority",
        suspects_entity_active.columns,
        current_columns,
        original_columns,
        9,
    )
    current_columns = suspects_entity_active.columns

    suspects_entity_active = truncate_rows(suspects_entity_active)
    record_columns(
        "truncate_rows",
        suspects_entity_active.columns,
        current_columns,
        original_columns,
        10,
    )
    current_columns = suspects_entity_active.columns
    return suspects_entity_active


def add_priority_to_others(sus, other_entity_group, id_type, entity_gsheet, uid):
    """Copy priority score from suspects to other active sheets and sort them
    by priority."""
    other_entity_group = pd.merge(
        other_entity_group,
        sus[[id_type, "priority", "narrative"]],
        how="outer",
        on=id_type,
    )
    other_entity_group = other_entity_group[other_entity_group["priority"] != ""]
    logger.error(f"<<< data_prep priority")
    other_entity_group["priority"] = (
        other_entity_group["priority"].fillna(0).astype(float)
    )
    logger.error(f">>> data_prep priority")
    other_entity_group["narrative_x"] = other_entity_group["narrative_y"]
    other_entity_group.rename(columns={"narrative_x": "narrative"}, inplace=True)
    other_entity_group.drop_duplicates(subset=uid, inplace=True)
    other_entity_group.sort_values("priority", ascending=False, inplace=True)
    other_entity_group = other_entity_group.iloc[
        :, 0 : len(entity_gsheet.columns)
    ].fillna("")
    return other_entity_group


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
    single_victim = active_suspects[active_suspects.victims_willing_to_testify != ""][
        "case_id"
    ]

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
