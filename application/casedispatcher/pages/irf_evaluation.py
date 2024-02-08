import streamlit as st
import json
import pandas as pd
import shap
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
from oauth2client.client import OAuth2Credentials
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
    make_file_bytes,
    save_to_cloud,
    get_file_id,
    load_from_cloud,
    get_matching_spreadsheets,
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

cutoff_days = 90
toml_config_dict = attrdict_to_dict(access_token)
creds_json = json.dumps(toml_config_dict)
credentials = OAuth2Credentials.from_json(creds_json)
drive_service = build("drive", "v3", credentials=credentials)


def load_model_and_columns(drive_service, model_name, cols_name, data_name):
    model_file_id = get_file_id(model_name, drive_service)
    model = load_from_cloud(drive_service, model_file_id)
    st.write(f"Fetch {model_name} with file_id: {model_file_id}")

    cols_file_id = get_file_id(cols_name, drive_service)
    cols = load_from_cloud(drive_service, cols_file_id)

    data_file_id = get_file_id(data_name, drive_service)
    data = load_from_cloud(drive_service, data_file_id)

    return model, cols, data


def get_country_selection(countries):
    countries_list = ["Select a country..."] + sorted(countries["name"].values.tolist())
    selected_country = st.selectbox("Select a country", countries_list)
    if selected_country != "Select a country...":
        country_id = countries[countries["name"] == selected_country]["id"].values[0]
        st.write(f"You selected {selected_country} with country_id: {country_id}")
    else:
        country_id = None
    return selected_country, country_id


def main():
    if "case_dispatcher_model" not in st.session_state:
        (
            st.session_state["case_dispatcher_model"],
            st.session_state["case_dispatcher_model_cols"],
            st.session_state["case_dispatcher_soc_df"],
        ) = load_model_and_columns(
            drive_service,
            "case_dispatcher_model.pkl",
            "case_dispatcher_model_cols.pkl",
            "case_dispatcher_soc_df.pkl",
        )
        st.session_state["best_pipeline"] = st.session_state[
            "case_dispatcher_model"
        ].best_estimator_
        st.session_state["clf"] = st.session_state["best_pipeline"].named_steps["clf"]
        st.session_state["model_data_transformed"] = st.session_state["best_pipeline"][
            :-1
        ].transform(
            st.session_state["case_dispatcher_soc_df"][
                st.session_state["case_dispatcher_model_cols"]
            ]
        )
        st.write(st.session_state["case_dispatcher_model_cols"])
    # Initialize the country list and selected country only once
    if "countries" not in st.session_state:
        st.session_state["countries"] = get_countries()
        countries_list = ["Select a country..."] + sorted(
            st.session_state["countries"]["name"].values.tolist()
        )
    else:
        countries_list = ["Select a country..."] + sorted(
            st.session_state["countries"]["name"].values.tolist()
        )
        if st.session_state["country"] not in countries_list:
            st.session_state["country"] = "Select a country..."

    if "irf" not in st.session_state:
        st.session_state["irf"] = "Select an IRF ..."
    # Country selection dropdown
    st.session_state["country"] = st.selectbox(
        "Select a country",
        countries_list,
        index=countries_list.index(
            st.session_state.get("country", "Select a country...")
        ),
    )

    operating_country_id = None
    if st.session_state["country"] != "Select a country...":
        filtered_countries = st.session_state["countries"][
            st.session_state["countries"]["name"] == st.session_state["country"]
        ]
        if not filtered_countries.empty:
            operating_country_id = filtered_countries["id"].values[0]
            st.write("You selected:", st.session_state["country"])
            st.write(
                f"You selected country: {st.session_state['country']} with country_id: {operating_country_id}"
            )
            irf_list = list(
                set(st.session_state["case_dispatcher_soc_df"]["irf_number"])
            )
            irf_list.sort()
            st.session_state["irfs"] = ["Select an IRF ..."] + irf_list
        else:
            st.error("Selected country not found in the list.")

    if st.session_state["country"] != "Select a country...":
        st.session_state["irf"] = st.selectbox(
            "Select an IRF ...",
            st.session_state["irfs"],
            index=st.session_state["irfs"].index(
                st.session_state.get("irf", "Select an IRF...")
            ),
        )

    if st.session_state["irf"] != "Select an IRF ...":
        st.write("You selected:", st.session_state["irf"])
        form_data = (
            st.session_state["case_dispatcher_soc_df"]
            .loc[
                st.session_state["case_dispatcher_soc_df"]["irf_number"]
                == st.session_state["irf"],
                st.session_state["case_dispatcher_model_cols"],
            ]
            .drop_duplicates()
        )

        st.write(form_data)

    if st.button("Predict") and st.session_state["irf"] != "Select an IRF ...":
        if operating_country_id is not None:
            st.write("Predicting...")
            # Assume form_data and input_list are previously defined and valid
            user_data = pd.DataFrame(form_data)

            # Transform the user input data with all pipeline steps except the classifier
            form_data_transformed = st.session_state["best_pipeline"][:-1].transform(
                form_data
            )
            # Make a prediction using only the classifier

            prediction = st.session_state["clf"].predict_proba(form_data_transformed)[
                :, 1
            ]
            st.write("Prediction:", prediction)

            # Transform the model data with all pipeline steps except the classifier

            # Initialize SHAP explainer with the model and the transformed model data
            explainer = shap.Explainer(
                st.session_state["clf"],
                st.session_state["model_data_transformed"],
                feature_names=st.session_state["case_dispatcher_model_cols"],
            )

            # Calculate SHAP values for the transformed user data
            shap_values = explainer(form_data_transformed, check_additivity=True)

            # Plot SHAP values for the user's data
            fig, ax = plt.subplots()
            shap.plots.waterfall(
                shap_values[0, :, 1]
            )  # Optionally limit the number of features displayed
            st.pyplot(fig, bbox_inches="tight")

        else:
            st.error("Please select a valid country before predicting.")


if __name__ == "__main__":
    main()
