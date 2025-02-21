import streamlit as st
import json
import pandas as pd
import numpy as np
from datetime import date
from googleapiclient.discovery import build
from oauth2client.client import OAuth2Credentials

import libraries.data_prep as data_prep
from libraries.data_prep import remove_non_numeric, process_columns, extract_case_id
from libraries.case_dispatcher_data import get_vdf, get_suspects, get_irf, get_suspect_evaluations
from libraries.google_lib import attrdict_to_dict, make_file_bytes, save_to_cloud

# Global configuration (only variables used in this file are kept)
case_dispatcher = st.secrets["case_dispatcher"]
access_token = case_dispatcher["access_token"]

# Setup Google Drive service
creds_json = json.dumps(attrdict_to_dict(access_token))
credentials = OAuth2Credentials.from_json(creds_json)
drive_service = build("drive", "v3", credentials=credentials)

# Define feature sets
num_features = [
    "number_of_traffickers",
    "number_of_victims",
    "arrested",
    "job_promised_amount",
    "days",
    "age",
]
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
    "date_of_interception",
]

def main():
    st.sidebar.title("Case Dispatcher")
    include_audit = st.sidebar.radio("Include IRF audit?", ["No", "Yes"])
    if include_audit == "Yes":
        irf_audit_number = st.sidebar.text_input("Enter the case number:")
        if irf_audit_number:
            st.sidebar.write(f"Case number: {irf_audit_number}")
        else:
            st.sidebar.write("Please enter a case number.")
    else:
        st.sidebar.write("No case audit selected.")

    if st.button("Extract model data"):
        # === Data Loading ===
        vdf = get_vdf(None)
        suspects = get_suspects(None)
        irf = get_irf(None)
        suspect_evals = get_suspect_evaluations(None)
        today = pd.Timestamp(date.today())

        # === Process Suspects Data ===
        # Fill missing values and create dummy variables for role
        suspects["suspect_arrested"].fillna("No", inplace=True)
        role_dummies = data_prep.create_role_dummies(suspects["role"], top_n=8)
        suspects = pd.concat([suspects.drop(columns=["role"]), role_dummies], axis=1)
        suspects["arrested"] = suspects["suspect_arrested"].str.startswith("Yes").astype(int)
        suspects.drop(columns=["suspect_arrested", "arrest_date"], inplace=True)

        # === Process Suspect Evaluations ===
        suspect_evals = suspect_evals.drop_duplicates()
        pivoted_evals = (
            suspect_evals.assign(val=True)
            .pivot_table(index="master_person_id", columns="evaluation", values="val", fill_value=False)
            .reset_index()
        )
        pivoted_evals.rename(
            columns={
                "Definitely trafficked many people": "pv_believes_definitely_trafficked_many",
                "Don't believe s/he's a trafficker": "pv_believes_not_a_trafficker",
                "Has trafficked some people": "pv_believes_trafficked_some",
                "Suspect s/he's a trafficker": "pv_believes_suspect_trafficker",
            },
            inplace=True,
        )

        # === Process IRF Data ===
        irf_notes = irf[
            ["irf_number", "case_notes", "operating_country_id", "date_of_interception"]
        ].copy()
        irf_notes["date_of_interception"] = pd.to_datetime(
            irf_notes["date_of_interception"], errors="coerce"
        )
        irf_notes["days"] = (today - irf_notes["date_of_interception"]).dt.days

        # === Merge IRF Data into Suspects ===
        suspects["case_id"] = suspects["sf_number"].apply(extract_case_id)
        merge_cols = [
            "irf_number",
            "number_of_victims",
            "number_of_traffickers",
            "case_notes",
            "date_of_interception",
        ]
        suspects = suspects.merge(irf[merge_cols], left_on="case_id", right_on="irf_number", how="inner")
        suspects = suspects.merge(pivoted_evals, on="master_person_id", how="left")
        suspects = suspects.drop_duplicates()

        # === Process vdf Data ===
        data_mappings = {
            "pv_recruited_how": "pv_recruited_other",
            "pv_expenses_paid_how": "pv_expenses_paid_other",
        }
        for col, other in data_mappings.items():
            new_cols, _ = process_columns(vdf[col], other)
            vdf = pd.concat([vdf, new_cols], axis=1)
        vdf.drop(columns=list(data_mappings.keys()), inplace=True)

        # Prepare victims data from vdf
        vdf["irf_number"] = vdf["vdf_number"].apply(extract_case_id)
        vdf = vdf.query("role == 'PVOT'")
        victim_cols = [
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
        suspects = vdf[victim_cols].merge(suspects, on="irf_number", how="right")
        suspects["arrested"] = suspects["arrested"].fillna("No").replace({"Yes": 1, "No": 0}).astype(int)

        # === Process Gender, Age and Other Columns ===
        gender_dummies = pd.get_dummies(suspects["gender"], prefix="gender").rename(
            columns={
                "gender_F": "female",
                "gender_M": "male",
                "gender_U": "unknown_gender",
                "gender_": "none_gender",
            }
        )
        suspects = pd.concat([suspects, gender_dummies], axis=1)
        suspects["age"] = suspects["age"].fillna(-99)

        # === Create soc_df and Merge Additional Data ===
        soc_df = suspects.copy()

        # Merge job promised amounts (aggregated from IRF and vdf)
        job_amounts = (
            irf[["master_person_id", "irf_number"]]
            .merge(vdf[["job_promised_amount", "master_person_id"]], on="master_person_id")
            .drop_duplicates()
        )
        grouped = job_amounts.groupby("irf_number").agg(
            {"master_person_id": "first", "job_promised_amount": "sum"}
        ).reset_index()
        soc_df = soc_df.merge(grouped[["master_person_id", "job_promised_amount"]], on="master_person_id", how="left")
        soc_df["job_promised_amount"] = soc_df["job_promised_amount"].apply(remove_non_numeric)

        # Merge interview date from suspect evaluations
        soc_df = soc_df.merge(suspect_evals[["master_person_id", "interview_date"]], on="master_person_id", how="left")
        soc_df["date_of_interception"] = pd.to_datetime(soc_df["date_of_interception"], errors="coerce")
        soc_df["days"] = (today - soc_df["date_of_interception"]).dt.days
        soc_df["number_of_victims"] = soc_df["number_of_victims"].fillna(1)
        suspects["case_filed_against"] = suspects["case_filed_against"].fillna("No").replace({"Yes": True, "No": False})

        drop_cols = ["borderstation_id", "station_name", "full_name", "phone_contact", "address_notes", "gender"]
        soc_df.drop(columns=drop_cols, errors="ignore", inplace=True)

        # === Data Type Conversions ===
        boolean_features = list(set(soc_df.columns) - set(num_features) - set(non_boolean_features))
        soc_df[boolean_features] = soc_df[boolean_features].fillna(False).astype(bool)
        soc_df[num_features] = soc_df[num_features].replace("", np.nan).fillna(0).astype(int)
        soc_df["days"] = soc_df["days"].astype(int)
        soc_df["irf_number"] = soc_df["irf_number"].astype(str)
        soc_df = soc_df.loc[:, (soc_df != False).any(axis=0)].drop_duplicates()

        # === Add Country Statistics ===
        soc_df = data_prep.add_country_stats(
            model_data=soc_df, country_stats=pd.read_csv("data/final_data.csv")
        )

        # === Save Processed Data to Cloud ===
        datasets = {
            "case_dispatcher_soc_df.pkl": soc_df,
            "new_victims.pkl": vdf,
            "new_suspects.pkl": suspects,
            "irf_case_notes.pkl": irf_notes,
        }
        for filename, df in datasets.items():
            file_bytes = make_file_bytes(df)
            file_metadata = {"name": filename}
            file_id = save_to_cloud(file_bytes, drive_service, file_metadata)
            st.write(f"Saved {filename} to cloud with file_id: {file_id}")

        st.write("Success! Data has been saved to the cloud.")

if __name__ == "__main__":
    main()
