# update_casedispatcher_sheets.py
# author: christo strydom

import os

import streamlit as st
import json
import pandas as pd
import numpy as np
from datetime import date
from googleapiclient.discovery import build
from copy import deepcopy
from oauth2client.client import OAuth2Credentials
import libraries.data_prep as data_prep
import pickle
from libraries.case_dispatcher_model import (
    check_grid_search_cv,
    save_results,
    make_new_predictions,
)
from libraries.data_prep import remove_non_numeric, process_columns
from libraries.entity_model import EntityGroup
from libraries.case_dispatcher_model import TypeSelector
from libraries.case_dispatcher_data import (
    get_vdf,
    get_suspects,
    get_irf,
    get_suspect_evaluations,
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
from libraries.data_prep import extract_case_id
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
    "UGANDASANDBOX2": os.environ["UGANDASANDBOX2"],
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
    country = "Uganda"
    spreadsheet_name = "Case Dispatcher 6.0 - Uganda Sandbox"
    case_dispatcher_soc_df = load_data(drive_service, "case_dispatcher_soc_df.pkl")
    case_dispatcher_soc_df.to_csv("data/case_dispatcher_soc_df.csv", index=False)
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

    # Proceed only if a country has been selected

    operating_country_id = get_country_id(countries, country)

    case_dispatcher_soc_df = case_dispatcher_soc_df.loc[
        case_dispatcher_soc_df["operating_country_id"] == operating_country_id, :
    ].copy()
    weights = get_all_weights(credentials, spreadsheet_name, WEIGHT_NAMES)

    url = links[country]



    db_vics = load_data(drive_service, "new_victims.pkl")
    db_vics = db_vics[db_vics["operating_country_id"] == operating_country_id].drop(
        columns=["operating_country_id"]
    )

    db_sus = load_data(drive_service, "new_suspects.pkl")
    db_sus = db_sus[db_sus["operating_country_id"] == operating_country_id].drop(
        columns=["operating_country_id"]
    )

    irf_case_notes = load_data(drive_service, "irf_case_notes.pkl")
    irf_case_notes = irf_case_notes[
        irf_case_notes["operating_country_id"] == operating_country_id
    ].drop(columns=["operating_country_id"])

    case_dispatcher_model = load_data(drive_service, "case_dispatcher_model.pkl")

    case_dispatcher_model_cols = load_data(
        drive_service, "case_dispatcher_model_cols.pkl"
    )

    case_dispatcher_soc_df.loc[:, "soc"] = 0.0
    # case_dispatcher_soc_df["soc"] = case_dispatcher_soc_df["soc"].astype(float)
    soc = make_predictions(
        case_dispatcher_model,
        case_dispatcher_soc_df.loc[:, case_dispatcher_model_cols].copy(),
    )
    case_dispatcher_soc_df.loc[:, "soc"] = soc

    new_victims = db_vics.copy()


    sheets, file_url, file_id = get_gsheets(credentials, spreadsheet_name, sheet_names)
    dfs = get_dfs(sheets)
    EntityGroup.sheets = []
    victims_entity = EntityGroup(
        "victim_id", new_victims, "victims", "closed_victims", dfs
    )

    victims_entity.new = data_prep.set_vic_id(victims_entity.new)
    # victims_entity.new.shape
    # victims_entity.new['irf_number'] = victims_entity.new['case_id'].apply(extract_sf_number_group)
    # list(case_dispatcher_soc_df)
    # list(db_sus)
    # case_dispatcher_soc_df[['sf_number', 'soc']]
    # case_dispatcher_soc_df.drop_duplicates(subset=['sf_number'])
    # case_dispatcher_soc_df.drop_duplicates()
    # sf_number
    # db_sus.merge(case_dispatcher_soc_df, on='sf_number', how='left')
    # db_sus[case_dispatcher_model_cols]
    for sheet in EntityGroup.sheets:
        print(sheet.active_name)

        # st.dataframe(EntityGroup.new)
        # -----------------------------------------------------------------------------------

    new_suspects = db_sus.copy()
    suspects_entity = EntityGroup(
        "sf_number", new_suspects, "suspects", "closed_suspects", dfs
    )
    suspects_entity.new = data_prep.set_suspect_id(suspects_entity.new, db_sus)

    EntityGroup.set_case_id()

    new_police = deepcopy(x=suspects_entity.new)
    new_police.rename(columns={"name": "suspect_name"}, inplace=True)
    police_entity = EntityGroup("sf_number", new_police, "police", "closed_police", dfs)

    EntityGroup.combine_sheets()
    suspects_entity.active = suspects_entity.active[
        ~(suspects_entity.active["case_id"] == "")
    ]

    EntityGroup.add_irf_notes(irf_case_notes[["irf_number", "case_notes"]])

    # logger.info(f"Move closed cases: {uid}")
    EntityGroup.move_closed(case_dispatcher_soc_df)
    EntityGroup.move_other_closed(suspects_entity, police_entity, victims_entity)

    vics_willing = data_prep.get_vics_willing_to_testify(victims_entity.active)
    weighting_sheet = vics_willing[["case_id", "willing_to_testify", "count"]].copy()

    police_entity.active = data_prep.add_vic_names(police_entity.active, vics_willing)
    suspects_entity.active = data_prep.add_vic_names(
        suspects_entity.active, vics_willing
    )
    suspects_entity.active = suspects_entity.active.drop_duplicates()

    sus_located = data_prep.get_sus_located(suspects_entity.active)
    victims_entity.active = data_prep.add_sus_located(
        victims_entity.active, sus_located
    )

    police_entity.active["case_status"] = police_entity.active["case_status"].astype(
        str
    )

    police_entity.active.loc[
        (police_entity.active["case_status"] == "nan"), "case_status"
    ] = ""
    suspects_entity.active.loc[
        (suspects_entity.active["case_status"] == "nan"), "case_status"
    ] = ""
    suspects_entity.active["case_status"] = suspects_entity.active[
        "case_status"
    ].astype(str)
    suspects_entity.active["victims_willing_to_testify"] = suspects_entity.active[
        "victims_willing_to_testify"
    ].astype(str)

    # Suspects = dfs["suspects"].copy()
    # sus = suspects_entity.active.copy()

    # -------------------------------------------------------------------------------------
    suspects_entity_active = suspects_entity.active.copy()
    soc_df = case_dispatcher_soc_df
    police_entity_active = police_entity.active.copy()
    google_sheets_suspects = dfs["suspects"]
    case_dispatcher_soc_df.loc[case_dispatcher_soc_df["days"]<120, ['case_id', 'sf_number', 'arrested', 'interview_date', 'pv_believes_definitely_trafficked_many', 'pv_believes_not_a_trafficker', 'pv_believes_trafficked_some', 'pv_believes_suspect_trafficker', 'exploit_debt_bondage', 'exploit_forced_labor', 'exploit_physical_abuse', 'exploit_prostitution', 'exploit_sexual_abuse']].to_csv("data/case_dispatcher_soc_df.csv", index=False)
    try:
          # Log the initial state of the DataFrames
        logger.info(
            f"Starting calc_all_sus_scores with the following DataFrame columns:\n"
            f"suspects_entity_active.columns = {list(suspects_entity.active.columns)},\n"
            f"vics_willing.columns = {list(vics_willing.columns)},\n"
            f"police_entity_active.columns = {list(police_entity_active.columns)},\n"
            f"soc_df.columns = {list(case_dispatcher_soc_df.columns)},\n"
            f"google_sheets_suspects.columns = {list(dfs['suspects'].columns)}"
        )

        # 1. Calculate victim willingness scores
        # Select only required columns for calc_vics_willing_scores
        required_vics_columns = {"case_id", "count", "willing_to_testify"}
        if not required_vics_columns.issubset(vics_willing.columns):
            missing = required_vics_columns - set(vics_willing.columns)
            error_msg = f"vics_willing is missing required columns: {missing}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Create a subset of vics_willing with only the required columns
        vics_willing_subset = vics_willing[list(required_vics_columns)].copy()

        # Calculate the victim willingness multipliers.
        vics_multiplier_df = data_prep.calc_vics_willing_multiplier(vics_willing)

        # Merge the multipliers onto the suspects DataFrame on 'case_id'.
        suspects_entity_active = suspects_entity_active.merge(vics_multiplier_df, how="left", on="case_id")

        # Ensure that any suspects without a matching record have a multiplier of 0.0.
        suspects_entity_active["v_mult"] = suspects_entity_active["v_mult"].fillna(0.0)
        multipliers = suspects_entity_active[["sf_number", "case_id", "v_mult", "count"]]

        logger.info("Completed calc_vics_willing_scores.")

        # 2. Calculate arrest scores
        suspects_entity_active = data_prep.calc_arrest_scores(suspects_entity_active, soc_df, police_entity_active)

        logger.info("Completed calc_arrest_scores.")
        multipliers = multipliers[["sf_number", "case_id", "v_mult", "count"]].merge(suspects_entity_active[["sf_number","bio_known","others_arrested","willing_to_arrest"]], on="sf_number", how="inner")

        # 3. Calculate recency scores
        suspects_entity_active = data_prep.calc_recency_scores(suspects_entity_active, soc_df, weights)
        multipliers = multipliers[["sf_number", "case_id", "v_mult", "count"]].merge(suspects_entity_active[["sf_number", "bio_known", "others_arrested", "willing_to_arrest"]],
                                                                                     on="sf_number", how="inner")
        multipliers_cols = multipliers.columns

        multipliers = multipliers[multipliers_cols].merge(suspects_entity_active[["sf_number", "recency_score", "days_old"]], on="sf_number", how="inner")
        logger.info("Completed calc_recency_scores.")
        multipliers_cols = multipliers.columns

        # ------------------------------------------------------
        # 4. Weight belief scores
        suspects_entity_active = data_prep.weight_pv_believes(suspects_entity_active, case_dispatcher_soc_df, weights)
        suspects_entity_active[['sf_number','pv_believes_definitely_trafficked_many', 'pv_believes_trafficked_some',
        'pv_believes_suspect_trafficker', 'pv_believes_not_a_trafficker',
        'pv_believes']]
        multipliers = multipliers[multipliers_cols].merge(suspects_entity_active[['sf_number','pv_believes_definitely_trafficked_many', 'pv_believes_trafficked_some',
        'pv_believes_suspect_trafficker', 'pv_believes_not_a_trafficker','pv_believes']], on="sf_number", how="inner")
        multipliers_cols = multipliers.columns
        logger.info("Completed weight_pv_believes.")

        # 5. Calculate exploitation scores

        suspects_entity_active = data_prep.get_exp_score(suspects_entity_active, case_dispatcher_soc_df, weights)
        logger.info("Completed get_exp_score.")
        multipliers=multipliers[multipliers_cols].merge(suspects_entity_active[['sf_number','exploit_debt_bondage',
       'exploit_forced_labor', 'exploit_physical_abuse',
       'exploit_prostitution', 'exploit_sexual_abuse', 'exp']], on="sf_number", how="inner")
        multipliers_cols = multipliers.columns

        # 6. Merge and round Strength of Case (SOC) scores
        suspects_entity_active = data_prep.get_new_soc_score(suspects_entity_active, case_dispatcher_soc_df)
        logger.info("Completed get_new_soc_score.")
        multipliers = multipliers[multipliers_cols].merge(suspects_entity_active[['sf_number', 'strength_of_case']], on="sf_number", how="inner")
        multipliers_cols = multipliers.columns

        # 7. Assign and adjust eminence scores
        suspects_entity_active = data_prep.get_eminence_score(suspects_entity_active)
        logger.info("Completed get_eminence_score.")
        multipliers = multipliers[multipliers_cols].merge(suspects_entity_active[['sf_number', 'em2']],
                                                        on="sf_number", how="inner")
        multipliers_cols = multipliers.columns

        # 8. Calculate solvability scores

        suspects_entity_active = data_prep.calc_solvability(
            suspects_entity_active, weights
        )
        logger.info("Completed calc_solvability.")


        # Log the number of suspects before priority calculation
        logger.info(
            f"BEFORE calc_priority: Number of suspects = {len(suspects_entity_active)}"
        )

        # 9. Calculate priority scores
        test_df=data_prep.calc_priority_detailed(suspects_entity_active, weights)
        suspects_entity_active = data_prep.calc_priority(
            suspects_entity_active, weights, dfs["suspects"]
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

    # ----------------------------------------------------------------------------------------

    suspects_entity.active = data_prep.calc_all_sus_scores(suspects_entity.active, vics_willing, police_entity.active,
                                                           weights, case_dispatcher_soc_df, dfs["suspects"])
    df = data_prep.calc_all_sus_scores(suspects_entity.active.copy(), vics_willing, police_entity.active.copy(),
                                                           weights, case_dispatcher_soc_df.copy(), dfs["suspects"].copy())
    victims_entity.active = data_prep.add_priority_to_others(
        suspects_entity.active,
        victims_entity.active,
        "case_id",
        dfs["victims"],
        "victim_id",
    )

    police_entity.active = data_prep.add_priority_to_others(
        suspects_entity.active,
        police_entity.active,
        "sf_number",
        dfs["police"],
        "sf_number",
    )
    # -------------------------------------------------------------------------------------

    active_cases = data_prep.update_active_cases(
        suspects_entity.active, police_entity.active
    )

    EntityGroup.add_case_name_formula()
    # st.dataframe(soc_df[["irf_number", "days"]])

    active_cases["priority"] = (
        active_cases["priority"] - active_cases["priority"].min()
    ) / (active_cases["priority"].max() - active_cases["priority"].min())

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
    victims_entity.active = filter_on_days(irf_case_notes, victims_entity.active)
    suspects_entity.active = filter_on_days(irf_case_notes, suspects_entity.active)

    police_entity.active = sort_cases(active_cases, police_entity.active, "sf_number")
    victims_entity.active = sort_cases(active_cases, victims_entity.active, "victim_id")
    suspects_entity.active = sort_cases(
        active_cases, suspects_entity.active, "sf_number"
    )

    EntityGroup.update_gsheets(credentials, spreadsheet_name, active_cases)


if __name__ == "__main__":
    main()
