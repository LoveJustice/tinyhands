# filename: update_casedispatcher_sheets.py
# author: christo strydom
# date: 2023-01-07

import os

import streamlit as st
import json
import pandas as pd
from googleapiclient.discovery import build
from copy import deepcopy
from oauth2client.client import OAuth2Credentials
import libraries.data_prep as data_prep
from libraries.entity_model import EntityGroup
from libraries.case_dispatcher_data import (
    get_countries,
)
from libraries.google_lib import (
    get_gsheets,
    get_dfs,
    attrdict_to_dict,
    get_all_weights,
    make_file_bytes,
    save_to_cloud,
    load_data,
    get_matching_spreadsheets,
)
import dotenv
from libraries.case_dispatcher_logging import setup_logger
import gspread

logger = setup_logger("update_logger", "update_logging")
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
WEIGHT_NAMES = os.getenv("WEIGHT_NAMES").split(",")
countries = get_countries()
# country_list = ["Select a country..."] + ["Nepal", "Uganda", "Malawi", "Namibia"]
case_dispatcher = st.secrets["case_dispatcher"]
access_token = case_dispatcher["access_token"]
sheet_names = case_dispatcher["sheet_names"]

toml_config_dict = attrdict_to_dict(access_token)
creds_json = json.dumps(toml_config_dict)
credentials = OAuth2Credentials.from_json(creds_json)
drive_service = build("drive", "v3", credentials=credentials)


links = {
    "Uganda": os.environ["UGANDA"],
    "Nepal": os.environ["NEPAL"],
    "Malawi": os.environ["MALAWI"],
    "Namibia": os.environ["NAMIBIA"],
    "Mozambique": os.environ["MOZAMBIQUE"],
    "Lesotho": os.environ["LESOTHO"],
    "UgandaSandbox": os.environ["UGANDASANDBOX"],
}


def get_country_id(df, country_name):
    # Normalize the case for comparison
    normalized_country_name = country_name.strip().lower()
    df["name_normalized"] = df["name"].str.lower()

    # Find the matching country_id
    matching_id = df.loc[df["name_normalized"] == normalized_country_name, "id"]

    if not matching_id.empty:
        return matching_id.values[0]
    else:
        st.write(f"Country not found: {country_name}")
        return "Country not found"


def filter_on_days(days_data, cases):
    cases = cases.merge(
        days_data[["irf_number", "days"]].drop_duplicates().copy(),
        left_on="case_id",
        right_on="irf_number",
        how="left",
    ).drop(columns=["irf_number"])
    numeric_days = pd.to_numeric(cases["days"], errors="coerce")
    return cases[(numeric_days <= 120) | numeric_days.isna()]


def make_predictions(model, X):
    best_pipeline = model.best_estimator_

    # Extract the RandomForestClassifier from the pipeline
    clf = best_pipeline.named_steps["clf"]

    # Transform the user input data with all pipeline steps except the classifier
    X_transformed = best_pipeline[:-1].transform(X)

    # Make a prediction using only the classifier
    prediction = clf.predict_proba(X_transformed)[:, 1]
    return prediction


def get_pv_believes_settings():
    pv_believes = case_dispatcher["pv_believes"]
    if st.checkbox("Adjust PV Believes"):
        pv_believes_text = case_dispatcher["pv_believes_text"]["text"]
        # Using st.expander to create a collapsible section for the variable description
        with st.expander("The PV believes settings"):
            st.markdown(pv_believes_text)
        st.subheader("Adjust PV Believes")
        # Assume pv_believes are fetched from case_dispatcher, initialize if not available

        pv_believes_definitely_trafficked_many = st.slider(
            "pv_believes_definitely_trafficked_many",
            0,
            1,
            int(pv_believes["pv_believes_definitely_trafficked_many"]),
        )
        pv_believes_not_a_trafficker = st.slider(
            "pv_believes_not_a_trafficker",
            0,
            1,
            int(pv_believes["pv_believes_not_a_trafficker"]),
        )
        pv_believes_trafficked_some = st.slider(
            "pv_believes_trafficked_some",
            0,
            1,
            int(pv_believes["pv_believes_trafficked_some"]),
        )
        pv_believes_suspect_trafficker = st.slider(
            "pv_believes_suspect_trafficker",
            0,
            1,
            int(pv_believes["pv_believes_suspect_trafficker"]),
        )

        # Update pv_believes based on slider input
        pv_believes = {
            "pv_believes_definitely_trafficked_many": pv_believes_definitely_trafficked_many,
            "pv_believes_not_a_trafficker": pv_believes_not_a_trafficker,
            "pv_believes_trafficked_some": pv_believes_trafficked_some,
            "pv_believes_suspect_trafficker": pv_believes_suspect_trafficker,
        }
    return pv_believes


def get_recency_settings():
    recency_vars = case_dispatcher["recency_vars"]
    if st.checkbox("Adjust Recency Variables"):
        recency_text = case_dispatcher["recency_text"]["text"]
        # Using st.expander to create a collapsible section for the variable description
        with st.expander("The recency settings"):
            st.markdown(recency_text)
        st.subheader("Adjust Recency Variables")
        # Assume recency_vars are fetched from case_dispatcher, initialize if not available

        discount_coef = st.slider(
            "Discount Coefficient (discount_coef)",
            0.00,
            0.10,
            recency_vars["discount_coef"],
        )
        discount_exp = st.slider(
            "Discount Exponent (discount_exp)", 0, 5, recency_vars["discount_exp"]
        )

        # Update recency_vars based on slider input
        recency_vars = {"discount_coef": discount_coef, "discount_exp": discount_exp}
    return recency_vars


def get_exploitation_settings():
    exploitation_type = case_dispatcher["exploitation_type"]
    if st.checkbox("Adjust Exploitation Variables"):
        exploitation_type_text = case_dispatcher["exploitation_type_text"]["text"]
        # Using st.expander to create a collapsible section for the variable description
        with st.expander("The exploitation settings"):
            st.markdown(exploitation_type_text)
        st.subheader("Adjust Exploitation Variables")
        # Assume recency_vars are fetched from case_dispatcher, initialize if not available

        exploit_prostitution = st.slider(
            "exploit_prostitution",
            0.00,
            1.00,
            exploitation_type["exploit_prostitution"],
        )
        exploit_sexual_abuse = st.slider(
            "exploit_sexual_abuse",
            0.00,
            1.00,
            exploitation_type["exploit_sexual_abuse"],
        )
        exploit_physical_abuse = st.slider(
            "exploit_physical_abuse",
            0.00,
            1.00,
            exploitation_type["exploit_physical_abuse"],
        )
        exploit_debt_bondage = st.slider(
            "exploit_debt_bondage",
            0.00,
            1.00,
            exploitation_type["exploit_debt_bondage"],
        )
        exploit_forced_labor = st.slider(
            "exploit_forced_labor",
            0.00,
            1.00,
            exploitation_type["exploit_forced_labor"],
        )
        # Update recency_vars based on slider input
        exploitation_type = {
            "exploit_prostitution": exploit_prostitution,
            "exploit_sexual_abuse": exploit_sexual_abuse,
            "exploit_physical_abuse": exploit_physical_abuse,
            "exploit_debt_bondage": exploit_forced_labor,
            "exploit_forced_labor": exploit_forced_labor,
        }
    return exploitation_type


def get_solvability_weights():
    solvability_weights = case_dispatcher["solvability_weights"]
    if st.checkbox("Adjust Solvability Weights"):
        solvability_weights_text = case_dispatcher["solvability_weights_text"]["text"]
        # Using st.expander to create a collapsible section for the variable description
        with st.expander("The solvability weights"):
            st.markdown(solvability_weights_text)
        st.subheader("Adjust Solvability Weights")
        # Assume solvability_weights are fetched from case_dispatcher, initialize if not available

        victim_willing_to_testify = st.slider(
            "victim_willing_to_testify",
            0.00,
            10.00,
            solvability_weights["victim_willing_to_testify"],
        )
        bio_and_location_of_suspect = st.slider(
            "bio_and_location_of_suspect",
            0.00,
            10.00,
            solvability_weights["bio_and_location_of_suspect"],
        )
        other_suspect_arrested = st.slider(
            "other_suspect(s)_arrested",
            0.00,
            10.00,
            solvability_weights["other_suspect(s)_arrested"],
        )
        police_willing_to_arrest = st.slider(
            "police_willing_to_arrest",
            0.00,
            10.00,
            solvability_weights["police_willing_to_arrest"],
        )
        recency_of_case = st.slider(
            "recency_of_case", 0.00, 10.00, solvability_weights["recency_of_case"]
        )
        exploitation_reported = st.slider(
            "exploitation_reported",
            0.00,
            10.00,
            solvability_weights["exploitation_reported"],
        )
        pv_believes = st.slider(
            "pv_believes", 0.00, 10.00, solvability_weights["pv_believes"]
        )
        # Update solvability_weights based on slider input
        solvability_weights = {
            "victim_willing_to_testify": victim_willing_to_testify,
            "bio_and_location_of_suspect": bio_and_location_of_suspect,
            "other_suspect(s)_arrested": other_suspect_arrested,
            "police_willing_to_arrest": police_willing_to_arrest,
            "recency_of_case": recency_of_case,
            "exploitation_reported": exploitation_reported,
            "pv_believes": pv_believes,
        }
    return solvability_weights


def get_priority_weights():
    priority_weights = case_dispatcher["priority_weights"]
    if st.checkbox("Adjust Priority Weights"):
        priority_weights_text = case_dispatcher["priority_weights_text"]["text"]
        # Using st.expander to create a collapsible section for the variable description
        with st.expander("The priority weights"):
            st.markdown(priority_weights_text)
        st.subheader("Adjust Priority Weights")
        # Assume priority_weights are fetched from case_dispatcher, initialize if not available

        eminence = st.slider("eminence", 0.0, 1.0, priority_weights["eminence"])
        solvability = st.slider(
            "solvability", 0.0, 1.00, priority_weights["solvability"]
        )
        strength_of_case = st.slider(
            "strength_of_case", 0.00, 1.00, priority_weights["strength_of_case"]
        )
        # Update priority_weights based on slider input

        priority_weights = {
            "eminence": eminence,
            "solvability": solvability,
            "strength_of_case": strength_of_case,
        }
    return priority_weights


def sort_cases(cases, to_sort, sort_heading):
    # 1. Verify that 'case_id' in 'cases' is unique
    if not cases["case_id"].is_unique:
        raise ValueError("The 'case_id' in 'cases' DataFrame must be unique.")

    # 2. Create a list of 'case_id' in the desired order from 'cases'
    cases_order = cases["case_id"].tolist()

    # 3. Convert 'case_id' in 'victims' to a categorical type with the specified order
    to_sort["case_id"] = pd.Categorical(
        to_sort["case_id"], categories=cases_order, ordered=True
    )

    # 4. Sort 'victims' based on the categorical 'case_id'
    sorted = to_sort.sort_values("case_id").reset_index(drop=True)

    # Optional: If you have other sorting preferences within the same 'case_id', you can add them
    # For example, sorting by 'victim_id' within each 'case_id'
    return sorted.sort_values(["case_id", sort_heading]).reset_index(drop=True)


def main():

    # Initialize session state variables if they don't exist
    if "country" not in st.session_state:
        st.session_state["country"] = None

    if "spreadsheet_name" not in st.session_state:
        st.session_state["spreadsheet_name"] = None

    if "case_dispatcher_soc_df" not in st.session_state:
        st.session_state["case_dispatcher_soc_df"] = load_data(
            drive_service, "case_dispatcher_soc_df.pkl"
        )

    # Get the settings from the case_dispatcher

    # exploitation_type = get_exploitation_settings()
    # recency_vars = get_recency_settings()
    # pv_believes = get_pv_believes_settings()
    # solvability_weights = get_solvability_weights()
    # priority_weights = get_priority_weights()
    #
    # # Now recency_vars is updated, you can proceed to construct weights
    # weights = {
    #     **solvability_weights,
    #     **recency_vars,
    #     **exploitation_type,
    #     **pv_believes,
    #     **priority_weights,
    # }
    # st.write(f"weights: {weights}")

    # Country selection
    country_list = ["Select a country..."] + list(links.keys())
    country = st.selectbox("Select a country to update", country_list, index=0)

    # Proceed only if a country has been selected
    if country and country != "Select a country...":
        operating_country_id = get_country_id(countries, country)
        if operating_country_id == "Country not found":
            st.write(f"Country not found: {country}")
            return
        st.write(
            f"Selected {country} has operating_country_id: {operating_country_id}, continuing..."
        )
        case_dispatcher_soc_df = st.session_state["case_dispatcher_soc_df"][
            st.session_state["case_dispatcher_soc_df"].operating_country_id
            == operating_country_id
        ].copy()

        st.session_state["country"] = country
        st.write("You selected:", country)
        st.session_state["spreadsheet_name"] = f"Case Dispatcher 6.0 - {country}"

        weights = get_all_weights(
            credentials, st.session_state["spreadsheet_name"], WEIGHT_NAMES
        )

        url = links[country]
        st.markdown(f"[Open {country} Google Sheet]({url})")
    else:
        st.session_state["spreadsheet_name"] = None

    # Proceed only if a spreadsheet has been selected
    if st.session_state["spreadsheet_name"]:
        st.write(
            f"Get the sheets from the selected spreadsheet {st.session_state['spreadsheet_name']}"
        )

        # Only execute this part if the "Update" button hasn't been clicked yet
        if st.button("Update"):
            # Assuming get_gsheets and get_dfs are defined and take the necessary arguments
            # st.dataframe(st.session_state["case_dispatcher_soc_df"].loc[
            #              st.session_state["case_dispatcher_soc_df"]["irf_number"] == "BUS089", :])

            st.write(st.session_state["spreadsheet_name"])
            sheets, file_url, file_id = get_gsheets(
                credentials, st.session_state["spreadsheet_name"], sheet_names
            )
            st.write(f"Found the following sheets {sheets}")
            st.write(f"Found the following file_url {file_url}")
            dfs = get_dfs(sheets)

            st.write(f"Get the data from collect_model_data.py")
            db_vics = load_data(drive_service, "new_victims.pkl")
            db_vics = db_vics[
                db_vics["operating_country_id"] == operating_country_id
            ].drop(columns=["operating_country_id"])
            db_sus = load_data(drive_service, "new_suspects.pkl")
            db_sus = db_sus[
                db_sus["operating_country_id"] == operating_country_id
            ].drop(columns=["operating_country_id"])
            irf_case_notes = load_data(drive_service, "irf_case_notes.pkl")
            irf_case_notes = irf_case_notes[
                irf_case_notes["operating_country_id"] == operating_country_id
            ].drop(columns=["operating_country_id"])
            st.write(f"Get the model (pkl):")
            case_dispatcher_model = load_data(
                drive_service, "case_dispatcher_model.pkl"
            )
            st.write("Get the model columns:")
            case_dispatcher_model_cols = load_data(
                drive_service, "case_dispatcher_model_cols.pkl"
            )
            st.write(f"Predict likelihood of arrest and add prediction to dataframe")
            # st.dataframe(soc_df[model_cols])
            case_dispatcher_soc_df.loc[:, "soc"] = 0.0
            # case_dispatcher_soc_df["soc"] = case_dispatcher_soc_df["soc"].astype(float)
            soc = make_predictions(
                case_dispatcher_model,
                case_dispatcher_soc_df.loc[:, case_dispatcher_model_cols].copy(),
            )
            case_dispatcher_soc_df.loc[:, "soc"] = soc

            # st.dataframe()
            # ===========================================================================================================
            st.write(f"Create the victims_entity from db_vics")
            new_victims = db_vics.copy()
            st.dataframe(new_victims)
            EntityGroup.sheets = []
            victims_entity = EntityGroup(
                "victim_id", new_victims, "victims", "closed_victims", dfs
            )

            victims_entity.new = data_prep.set_vic_id(victims_entity.new)
            st.write("st.dataframe(victims_entity.new):\n")
            st.dataframe(victims_entity.new)

            st.write("for sheet in EntityGroup.sheets:\n")
            for sheet in EntityGroup.sheets:
                st.write(sheet.active_name)
                st.dataframe(sheet.new)
            # st.dataframe(EntityGroup.new)
            # -----------------------------------------------------------------------------------

            new_suspects = db_sus.copy()
            st.dataframe(new_suspects)
            suspects_entity = EntityGroup(
                "sf_number", new_suspects, "suspects", "closed_suspects", dfs
            )
            suspects_entity.new = data_prep.set_suspect_id(suspects_entity.new, db_sus)
            st.write("st.dataframe(suspects_entity.new):")
            st.dataframe(suspects_entity.new)
            # -----------------------------------------------------------------------------------
            EntityGroup.set_case_id()
            for sheet in EntityGroup.sheets:
                st.write(sheet.active_name)
                st.dataframe(sheet.new)
                st.write("------------------------------------------")
            # st.dataframe(EntityGroup.new)
            st.write(
                f"Create the police entity from a  copy of the suspects_entity.new"
            )
            new_police = deepcopy(x=suspects_entity.new)
            new_police.rename(columns={"name": "suspect_name"}, inplace=True)
            police_entity = EntityGroup(
                "sf_number", new_police, "police", "closed_police", dfs
            )

            EntityGroup.combine_sheets()
            suspects_entity.active = suspects_entity.active[
                ~(suspects_entity.active["case_id"] == "")
            ]

            st.write(f"Add irf_case_notes")
            EntityGroup.add_irf_notes(irf_case_notes[["irf_number", "case_notes"]])
            st.write(f"Move closed cases")
            # logger.info(f"Move closed cases: {uid}")
            st.dataframe(suspects_entity.active)
            st.dataframe(case_dispatcher_soc_df.head())
            EntityGroup.move_closed(case_dispatcher_soc_df)
            EntityGroup.move_other_closed(
                suspects_entity, police_entity, victims_entity
            )
            st.write(f"Get victims willing to testify")
            vics_willing = data_prep.get_vics_willing_to_testify(victims_entity.active)
            st.write(f"Add victim names")
            police_entity.active = data_prep.add_vic_names(
                police_entity.active, vics_willing
            )
            suspects_entity.active = data_prep.add_vic_names(
                suspects_entity.active, vics_willing
            )
            suspects_entity.active = suspects_entity.active.drop_duplicates()
            st.write(f"Get located suspects")
            sus_located = data_prep.get_sus_located(suspects_entity.active)
            victims_entity.active = data_prep.add_sus_located(
                victims_entity.active, sus_located
            )

            police_entity.active["case_status"] = police_entity.active[
                "case_status"
            ].astype(str)
            police_entity.active.loc[
                (police_entity.active["case_status"] == "nan"), "case_status"
            ] = ""
            suspects_entity.active.loc[
                (suspects_entity.active["case_status"] == "nan"), "case_status"
            ] = ""
            suspects_entity.active["case_status"] = suspects_entity.active[
                "case_status"
            ].astype(str)
            suspects_entity.active["victims_willing_to_testify"] = (
                suspects_entity.active["victims_willing_to_testify"].astype(str)
            )

            # Suspects = dfs["suspects"].copy()
            # sus = suspects_entity.active.copy()

            # -------------------------------------------------------------------------------------
            st.write(f"Calculate all suspect scores")
            st.dataframe(suspects_entity.active)
            suspect_cols = ['case_id', 'case_name', 'sf_number', 'strength_of_case', 'solvability', 'eminence',
                            'priority', 'case_status', 'date', 'legal_status', 'name', 'address', 'phone_numbers',
                            'social_media_id', 'phone_#_failure', 'victims_willing_to_testify', 'relationships',
                            'date_relationships_updated', 'confirm_photo', 'photo_confirmation_status', 'narrative',
                            'irf_case_notes', 'updates', 'victim_interview', 'suspect_interview', 'social_media',
                            'phone_records', 'legal_info', 'fb_line_up', 'border_station', 'informants',
                            'community_groups', 'advertising', 'surveillance', 'uc_operation', 'supervisor_review',
                            'boom_button', 'date_closed', ]

            all_sus_scores = data_prep.calc_all_sus_scores(suspects_entity.active, vics_willing, police_entity.active,
                                                           weights, case_dispatcher_soc_df, dfs["suspects"])
            suspects_entity.active = data_prep.align_columns(all_sus_scores[suspect_cols], dfs["suspects"])

            st.dataframe(suspects_entity.active)
            st.write(
                """At data_prep.calc_all_sus_scores(
                suspects_entity.active,
                vics_willing,
                police.active,
                weights,
                soc_df,
                dfs["suspects"],
            )"""
            )
            pd.DataFrame(suspects_entity.active)
            st.write(f"Add priorities to victims")
            victims_entity.active = data_prep.add_priority_to_others(
                suspects_entity.active,
                victims_entity.active,
                "case_id",
                dfs["victims"],
                "victim_id",
            )
            st.write(f"Add priorities to police")
            police_entity.active = data_prep.add_priority_to_others(
                suspects_entity.active,
                police_entity.active,
                "sf_number",
                dfs["police"],
                "sf_number",
            )
            # -------------------------------------------------------------------------------------
            st.write(f"Derive active cases")
            active_cases = data_prep.update_active_cases(
                suspects_entity.active, police_entity.active
            )

            EntityGroup.add_case_name_formula()
            # st.dataframe(soc_df[["irf_number", "days"]])
            st.write("Update Case Dispatcher Google Sheet")
            active_cases["priority"] = (
                active_cases["priority"] - active_cases["priority"].min()
            ) / (active_cases["priority"].max() - active_cases["priority"].min())
            st.write("---active_cases before merge:")


            active_cases = filter_on_days(irf_case_notes, active_cases)

            # Filter out rows where 'days' is greater than 365 and is not NaN (thus a number)
            # Also, implicitly keeps rows where 'days' is NaN or None, since comparison with NaN is false

            active_cases = active_cases[~(active_cases["case_id"] == "")]

            # set(filtered_active_cases["case_id"])
            logger.info(
                f"Do EntityGroup.update_gsheets(credentials, st.session_state['spreadsheet_name'], filtered_active_cases here            # )"
            )
            # filtered_active_cases = filtered_active_cases[['case_id','priority','irf_case_notes','narrative','case_status','Next_Action_Priority','days']]
            police_entity.active = filter_on_days(irf_case_notes, police_entity.active)
            victims_entity.active = filter_on_days(
                irf_case_notes, victims_entity.active
            )
            # st.dataframe(victims_entity.active)
            suspects_entity.active = filter_on_days(
                irf_case_notes, suspects_entity.active
            )
            st.write("st.dataframe(suspects_entity.active):")
            st.dataframe(suspects_entity.closed)
            police_entity.active = sort_cases(
                active_cases, police_entity.active, "sf_number"
            )
            victims_entity.active = sort_cases(
                active_cases, victims_entity.active, "victim_id"
            )
            suspects_entity.active = sort_cases(
                active_cases, suspects_entity.active, "sf_number"
            )

            EntityGroup.update_gsheets(
                credentials, st.session_state["spreadsheet_name"], active_cases
            )
            st.dataframe(active_cases)
            st.write(
                f"Success! {st.session_state['spreadsheet_name']} has been updated."
            )


if __name__ == "__main__":
    main()
