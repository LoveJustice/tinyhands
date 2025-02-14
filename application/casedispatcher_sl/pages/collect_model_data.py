import streamlit as st
import json
import pandas as pd
import numpy as np
from datetime import date
from googleapiclient.discovery import build
from oauth2client.client import OAuth2Credentials
import libraries.data_prep as data_prep


from libraries.data_prep import (
    remove_non_numeric,
    process_columns,
    do_audit,
    extract_case_id,
)
from libraries.case_dispatcher_data import (
    get_vdf,
    get_suspects,
    get_irf,
    get_suspect_evaluations,
)
from libraries.google_lib import (
    attrdict_to_dict,
    make_file_bytes,
    save_to_cloud,
)


country_list = ["Select a country..."] + ["Nepal", "Uganda"]
case_dispatcher = st.secrets["case_dispatcher"]
access_token = case_dispatcher["access_token"]
recency_vars = case_dispatcher["recency_vars"]
pv_believes = case_dispatcher["pv_believes"]
solvability_weights = case_dispatcher["solvability_weights"]
exploitation_type = case_dispatcher["exploitation_type"]
priority_weights = case_dispatcher["priority_weights"]


sheet_names = case_dispatcher["sheet_names"]
weights = {
    **solvability_weights,
    **recency_vars,
    **exploitation_type,
    **pv_believes,
    **priority_weights,
}

values_and_weights = {
    "version": "test",
    "priority_weights": priority_weights,
    "solvability_weights": solvability_weights,
    "recency_vars": recency_vars,
    "pv_believes": pv_believes,
    "exploitation_type": exploitation_type,
    "sheet_names": sheet_names,
}


toml_config_dict = attrdict_to_dict(access_token)
creds_json = json.dumps(toml_config_dict)
credentials = OAuth2Credentials.from_json(creds_json)
drive_service = build("drive", "v3", credentials=credentials)

# Define numerical features
num_features = [
    "number_of_traffickers",
    "number_of_victims",
    "arrested",
    "job_promised_amount",
    "days",
    "age",
]

# Define boolean features
non_boolean_features = [
    "interview_date",
    "case_notes",
    "case_id",
    "master_person_id",
    "sf_number",
    "person_id",
    "country",
    "operating_country_id",
    "social_media",
    "irf_number",
    "gender",
    "date_of_interception"
]


def refine_model_cols(cols):
    cols.pop(cols.index("arrested"))
    cols.pop(cols.index("lightgbm_arrest_prediction"))
    return cols


def add_missing_model_cols(data, model_cols):
    for column in model_cols:
        # Check if the column is not in the DataFrame
        if column not in data.columns:
            # Add the column with all values set to False
            data[column] = False
    return data


def make_lgbm_predictions(model, X):
    return model.predict_proba(X)[:, 1]


def main():
    # Initialize session state variables if they don't exist
    country = None
    counter = 0
    # Sidebar radio selection
    st.sidebar.radio(
        "Do you want to include an audit of a IRF case number?",
        options=["No", "Yes"],
        key="include_audit",
    )

    # Initialize case_number as None
    irf_audit_number = None

    # Conditionally display the text input if 'Yes' is selected
    if st.session_state["include_audit"] == "Yes":
        st.sidebar.text_input("Enter the case number:", key="irf_audit_number")

        # Check if a case number is provided
        if irf_audit_number:
            # This is where you can place the rest of your app's functionality
            # that depends on having a case number.
            st.sidebar.write("You have entered a case number: ", irf_audit_number)
            # Here you can add more code to process the case number.

            # Example function call (you would define this function elsewhere in your code)
            # process_case(case_number)
        else:
            st.sidebar.write("Please enter a case number to proceed.")
    else:
        st.sidebar.write("No case audit selected.")

    if st.button("Extract model data"):
        # Assuming get_gsheets and get_dfs are defined and take the necessary arguments
        st.write("Retrieve vdf data ...")
        db_vdf = get_vdf(country)
        counter += 1
        db_vdf.to_csv(f"data_trace/vdf_{counter}.csv", index=False)
        st.write("Retrieve suspect data ...")
        db_sus = get_suspects(country)
        counter += 1
        db_sus.to_csv(f"data_trace/db_sus_{counter}.csv", index=False)
        st.write("Retrieve irf data ...")
        db_irf = get_irf(country)
        counter += 1
        db_irf.to_csv(f"data_trace/irf_{counter}.csv", index=False)
        st.write("Retrieve suspect_evaluations data ...")
        suspect_evaluations = get_suspect_evaluations(country)
        counter += 1
        suspect_evaluations.to_csv(
            f"data_trace/suspect_evaluations_{counter}.csv", index=False
        )
        st.write("Start data manipulation  ...")
        # TODO: This is commented out.  In the model building process, we need to remove the rows with missing values
        # db_sus = db_sus.dropna(subset=["suspect_arrested"])
        db_sus["suspect_arrested"].fillna("No", inplace=True)
        # Create the 'any_arrest' column
        st.write("Process the role column ...")
        st.write(f"Unique values for 'role' in db_sus: {db_sus['role'].unique()}")
        do_audit(db_irf["irf_number"], "*** Audit 1")
        do_audit(
            db_sus["sf_number"].apply(extract_case_id), "*** Audit original db_sus"
        )

        # (
        #     processed_series,
        #     db_sus["role"],
        #     unique_elements,
        # ) = data_prep.extract_role_series(db_sus["role"])
        # ===== Example usage in your collect_model_data.py =====
        # Assuming `db_sus` is your DataFrame and it has a 'role' column:

        # Create dummy columns for the top 5 most frequent roles.
        role_dummies = data_prep.create_role_dummies(db_sus["role"], top_n=8)

        # Drop the original 'role' column and concatenate the dummy columns.
        db_sus = pd.concat([db_sus.drop(columns=["role"]), role_dummies], axis=1)

        st.write("Process the arrest column ...")
        db_sus["arrested"] = (
            db_sus["suspect_arrested"].str.startswith("Yes").astype(int)
        )
        db_sus = db_sus.drop(columns=["suspect_arrested", "arrest_date"])

        # Remove duplicated rows from suspect_evaluations dataframe
        st.write("Suspect evaluations ...")
        suspect_evaluations = suspect_evaluations.drop_duplicates()
        pivoted_suspect_evaluations = (
            suspect_evaluations.assign(val=True)
            .pivot_table(
                index="master_person_id",
                columns="evaluation",
                values="val",
                fill_value=False,
            )
            .reset_index()
        )
        suspect_evaluation_types = pivoted_suspect_evaluations.astype(
            {
                col: bool
                for col in pivoted_suspect_evaluations.columns
                if col != "master_person_id"
            }
        )
        st.write(
            f"Found the following suspect_evaluation_types {suspect_evaluations['evaluation'].unique().tolist()}"
        )

        # Rename columns of suspect_evaluation_types dataframe
        column_rename_mapping = {
            "Definitely trafficked many people": "pv_believes_definitely_trafficked_many",
            "Don't believe s/he's a trafficker": "pv_believes_not_a_trafficker",
            "Has trafficked some people": "pv_believes_trafficked_some",
            "Suspect s/he's a trafficker": "pv_believes_suspect_trafficker",
        }
        suspect_evaluation_types = suspect_evaluation_types.rename(
            columns=column_rename_mapping
        )
        st.write(f"Extract irf_case_notes ...")
        # Extract irf_case_notes from db_irf dataframe
        irf_case_notes = db_irf[
            ["irf_number", "case_notes", "operating_country_id", "date_of_interception"]
        ]
        st.write("Calculate days since interview: ...")
        today = pd.Timestamp(date.today())
        # Convert 'interview_date' to datetime, errors='coerce' will turn incorrect formats to NaT
        irf_case_notes["date_of_interception"] = pd.to_datetime(
            irf_case_notes["date_of_interception"], errors="coerce"
        )

        # Calculate the number of days, with a default of -999 for NaT or missing values
        irf_case_notes["days"] = (
            today - irf_case_notes["date_of_interception"]
        ).dt.days
        # Merge db_vdf and db_sus with db_irf on 'master_person_id'
        merge_cols = [
            "irf_number",
            "number_of_victims",
            "number_of_traffickers",
            "case_notes",
            "date_of_interception",
        ]

        db_sus["case_id"] = db_sus["sf_number"].apply(extract_case_id)
        # db_vdf = db_vdf.merge(db_irf[merge_cols], left_on='case_id', right_on="irf_number", how="inner")
        counter += 1
        db_sus.to_csv(f"data_trace/db_sus_{counter}.csv", index=False)
        db_sus = db_sus.merge(
            db_irf[merge_cols],
            left_on=["case_id"],
            right_on=["irf_number"],
            how="inner",
        )

        do_audit(db_sus["irf_number"], "*** Audit 2 on db_sus")

        db_sus = db_sus.drop_duplicates()
        counter += 1
        db_sus.to_csv(f"data_trace/db_sus_{counter}.csv", index=False)
        # db_sus = db_sus[~db_sus.arrested.isna()]

        # Merge db_sus with suspect_evaluation_types on 'master_person_id'
        st.write(
            f"Merge db_sus with suspect_evaluation_types on 'master_person_id' ..."
        )
        db_sus = db_sus.merge(
            suspect_evaluation_types, on="master_person_id", how="left"
        )

        # Define mappings for processing columns
        st.write(
            f"Define mappings for processing columns and expanding to a wide format ..."
        )
        data_mappings = {
            "db_vdf_1": (db_vdf, "pv_recruited_how", "pv_recruited_other"),
            "db_vdf_2": (
                db_vdf,
                "pv_expenses_paid_how",
                "pv_expenses_paid_other",
            ),
            # "db_sus_1": (db_sus, "role", "role_other"),
        }

        # Process columns based on the data mappings
        for key, (
            dataframe,
            column_name,
            other_column_name,
        ) in data_mappings.items():
            new_cols, _ = process_columns(dataframe[column_name], other_column_name)
            dataframe = pd.concat([dataframe, new_cols], axis=1)
            if "db_vdf" in key:
                db_vdf = dataframe
            elif "db_sus" in key:
                db_sus = dataframe

        st.write(f"Refine db_vdf and create db_vics...")
        db_vdf.drop(columns=["pv_recruited_how", "pv_expenses_paid_how"], inplace=True)


        # Extract selected columns from db_vdf into db_vics dataframe
        db_vics = db_vdf[
            [
                "vdf_number",
                "full_name",
                "phone_contact",
                "address_notes",
                "social_media",
                "person_id",
                "operating_country_id",
            ]
        ]

        db_vdf["irf_number"] = db_vdf["vdf_number"].apply(extract_case_id)
        do_audit(db_vdf["irf_number"], )

        list_db_vdf_columns = list(db_vdf)
        st.write(f"A list of the db_vdf columns {list_db_vdf_columns}")
        st.write(f"Refine db_vdf and create db_vics...")
        st.write(f"Unigue values for 'role' in db_sus: {db_vdf['role'].unique()}")
        db_vdf.query("role == 'PVOT'", inplace=True)

        merge_cols = [
            "exploit_debt_bondage",
            "exploit_forced_labor",
            "exploit_physical_abuse",
            "exploit_prostitution",
            "exploit_sexual_abuse",
        ]
        st.write(f"Merge suspect and victim dataframes...")

        db_sus = db_vdf[
            [
                "exploit_debt_bondage",
                "exploit_forced_labor",
                "exploit_physical_abuse",
                "exploit_prostitution",
                "exploit_sexual_abuse",
                "pv_recruited_agency",
                "pv_recruited_broker",
                "pv_recruited_no",
                "irf_number",
            ]
        ].merge(db_sus, left_on="irf_number", right_on="irf_number", how="right")
        do_audit(db_sus["irf_number"], "db_sus and db_vdf merge")
        # ======================================================================

        db_sus["arrested"] = (
            db_sus["arrested"].fillna("No").replace({"Yes": 1, "No": 0}).astype(int)
        )

        gender_dummies = pd.get_dummies(db_sus["gender"], prefix="gender")
        st.write(f"Columns of gender_dummies: {gender_dummies.columns}")
        # Rename the columns to the desired names
        # gender_dummies.columns = ["gender_N", "gender_F", "gender_M", "gender_U"]
        # 'gender_', 'gender_F', 'gender_M', 'gender_U'
        # If you prefer specific column names like male, female, unknown_gender, you can rename them:
        gender_dummies.rename(
            columns={
                "gender_F": "female",
                "gender_M": "male",
                "gender_U": "unknown_gender",
                "gender_": "none_gender"
            },
            inplace=True,
        )

        # Now, concatenate these new columns back to the original DataFrame
        db_sus = pd.concat([db_sus, gender_dummies], axis=1)

        # # Determine the top N countries to keep
        # top_n_countries = db_sus['country'].value_counts().nlargest(10).index
        #
        # # Create a new column where less common countries are labeled as 'Other'
        # db_sus['country_reduced'] = db_sus['country'].apply(
        #     lambda x: x if x in top_n_countries else 'Other')
        #
        # # Apply one-hot encoding to the reduced country column
        # country_dummies = pd.get_dummies(db_sus['country_reduced'], prefix='country')
        #
        # # Concatenate these new columns back to the original DataFrame
        # db_sus = pd.concat([db_sus, country_dummies], axis=1)

        db_sus["age"] = db_sus["age"].fillna(-99)  # Fill missing values with -99

        # Copy the dataframe
        st.write("Create soc_df from db_sus: ...")
        soc_df = db_sus.copy()
        list(soc_df.columns)
        # Merge the dataframes on 'master_person_id' and filter out duplicated rows
        st.write("Extract job_promised_amounts from the db_vdf table")
        job_promised_amounts = (
            db_irf[["master_person_id", "irf_number"]]
            .merge(
                db_vdf[["job_promised_amount", "master_person_id"]],
                on="master_person_id",
            )
            .drop_duplicates()
        )

        # Group by 'irf_number', aggregate and reset the index
        grouped = (
            job_promised_amounts.groupby("irf_number")
            .agg({"master_person_id": "first", "job_promised_amount": "sum"})
            .reset_index()
        )

        # Merge the grouped dataframe and suspect evaluations dataframe with the soc_df dataframe
        soc_df = soc_df.merge(
            grouped[["master_person_id", "job_promised_amount"]],
            on="master_person_id",
            how="left",
        )
        do_audit(db_sus["irf_number"], "soc_df merge with grouped")

        soc_df["job_promised_amount"] = soc_df["job_promised_amount"].apply(
            remove_non_numeric
        )
        do_audit(db_sus["irf_number"], "remove_non_numeric")

        st.write(
            "Extract interview_date from the suspect_evaluations table and merge onto soc_df"
        )
        soc_df = soc_df.merge(
            suspect_evaluations[["master_person_id", "interview_date"]],
            on="master_person_id",
            how="left",
        )
        do_audit(db_sus["irf_number"], "suspect_evaluations merge with soc_df")

        st.write("Calculate days since interview: ...")
        today = pd.Timestamp(date.today())
        # Convert 'interview_date' to datetime, errors='coerce' will turn incorrect formats to NaT
        soc_df["date_of_interception"] = pd.to_datetime(
            soc_df["date_of_interception"], errors="coerce"
        )

        # Calculate the number of days, with a default of -999 for NaT or missing values
        soc_df["days"] = (today - soc_df["date_of_interception"]).dt.days

        st.write("If 'number_of_victims' is NaN, replace it with 1")
        soc_df["number_of_victims"] = soc_df["number_of_victims"].fillna(1)
        st.write("Make case_filed_against a boolean value")
        db_sus["case_filed_against"] = (
            db_sus["case_filed_against"]
            .fillna("No")
            .replace({"Yes": True, "No": False})
        )
        columns_to_drop = [
            "borderstation_id",
            "station_name",
            "full_name",
            "phone_contact",
            "address_notes",
            "gender",
            # "irf_number",
        ]
        st.write(f"Drop irrelevant columns {columns_to_drop}")
        soc_df = soc_df.drop(columns=columns_to_drop)
        counter += 1
        soc_df.to_csv(f"data_trace/soc_df_{counter}.csv", index=False)
        boolean_features = list(
            set(soc_df.columns) - set(num_features) - set(non_boolean_features)
        )
        st.write(
            f"Convert the data type of the boolean features to boolean {boolean_features}"
        )
        # Convert the data type of the boolean features to boolean
        st.write(soc_df[soc_df["sf_number"] == "LWK1158A"][
            ['exploit_debt_bondage', 'exploit_forced_labor', 'exploit_physical_abuse', 'exploit_prostitution',
             'exploit_sexual_abuse']])

        soc_df[boolean_features] = soc_df[boolean_features].fillna(False).astype(bool)
        st.write(soc_df[soc_df["sf_number"] == "LWK1158A"][
            ['exploit_debt_bondage', 'exploit_forced_labor', 'exploit_physical_abuse', 'exploit_prostitution',
             'exploit_sexual_abuse']])
        # Fill null values in the numerical features with 0 and convert the data type to float
        st.write(
            f"Fill null values in the numerical features with 0 and convert the data type to float {num_features}"
        )
        soc_df[num_features] = (
            soc_df[num_features].replace("", np.nan).fillna(0).astype(int)
        )
        st.write("Convert 'days' to integer values")
        soc_df["days"] = soc_df["days"].astype(int)
        st.write("Convert 'irf_number' to string values")
        soc_df["irf_number"].astype(str)
        st.write("Drop columns that have only False values")
        do_audit(db_sus["irf_number"], " *** before excluding all false columns.")
        soc_df = soc_df.loc[:, (soc_df != False).any(axis=0)]
        do_audit(db_sus["irf_number"], " *** after excluding all false columns.")
        counter += 1
        soc_df.to_csv(f"data_trace/soc_df_{counter}.csv", index=False)
        # TODO: Rework the model to use the new features
        soc_df = soc_df.drop_duplicates()
        counter += 1
        soc_df.to_csv(f"data_trace/soc_df_{counter}.csv", index=False)
        counter += 1
        db_vics.to_csv(f"data_trace/db_vics_{counter}.csv", index=False)
        db_vics = db_vics.drop_duplicates()
        counter += 1
        db_vics.to_csv(f"data_trace/db_vics_{counter}.csv", index=False)
        db_sus = db_sus.drop_duplicates()
        irf_case_notes = irf_case_notes.drop_duplicates()

        soc_df = data_prep.add_country_stats(
            model_data=soc_df, country_stats=pd.read_csv("data/final_data.csv")
        )
        file_bytes = make_file_bytes(soc_df)
        file_metadata = {"name": "case_dispatcher_soc_df.pkl"}
        file_id = save_to_cloud(file_bytes, drive_service, file_metadata)
        st.write(f"Save case_dispatcher_soc_df to cloud with file_id: {file_id}")
        st.write(f"Success!  Case dispatcher data has been save to the cloud.")

        file_bytes = make_file_bytes(db_vics)
        file_metadata = {"name": "new_victims.pkl"}
        file_id = save_to_cloud(file_bytes, drive_service, file_metadata)
        st.write(f"Save new_victims to cloud with file_id: {file_id}")

        counter += 1
        db_sus.to_csv(f"data_trace/new_suspects_{counter}.csv", index=False)
        file_bytes = make_file_bytes(db_sus)
        file_metadata = {"name": "new_suspects.pkl"}
        file_id = save_to_cloud(file_bytes, drive_service, file_metadata)
        st.write(f"Save new_suspects to cloud with file_id: {file_id}")
        do_audit(db_sus["irf_number"], " *** last audit on db_sus.")

        counter += 1
        irf_case_notes.to_csv(f"data_trace/irf_case_notes_{counter}.csv", index=False)
        file_bytes = make_file_bytes(irf_case_notes)
        file_metadata = {"name": "irf_case_notes.pkl"}
        file_id = save_to_cloud(file_bytes, drive_service, file_metadata)
        st.write(f"Save irf_case_notes to cloud with file_id: {file_id}")
        st.write(
            f"Success!  New victims, suspects, and irf_case_notes have been save to the cloud."
        )
        do_audit(irf_case_notes["irf_number"], " *** last audit on irf_case_notes.")


if __name__ == "__main__":
    main()
