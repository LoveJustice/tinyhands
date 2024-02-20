import streamlit as st
import json
import pandas as pd
import shap
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
from sklearn.tree import export_text
from oauth2client.client import OAuth2Credentials
from libraries.case_dispatcher_data import (

    get_countries,
)
from pages.model_build import display_feature_importances

from libraries.google_lib import (
    get_gsheets,
    get_dfs,
    load_model_and_columns,
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
        st.session_state['tree'] = st.session_state["case_dispatcher_model"].best_estimator_.named_steps["clf"].estimators_[0]
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

        with st.expander("See decision tree rules:"):
            tree = st.session_state['tree'].best_estimator_.named_steps["clf"].estimators_[0]
            tree_rules = export_text(tree, feature_names=st.session_state["case_dispatcher_model_cols"])
            st.text(tree_rules)

        with st.expander("See feature importances:"):
            display_feature_importances(st.session_state["case_dispatcher_model"], st.session_state["case_dispatcher_model_cols"])

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
        else:
            st.error("Selected country not found in the list.")

    # Define a mapping from the user-friendly options to the codes
    gender_options = {"Male": 0, "Female": 1, "Unknown": 2}

    # Create a list of the user-friendly gender options for display
    options_list = list(gender_options.keys())  # ["Male", "Female", "Unknown"]

    # Initialize a dictionary to store form data
    form_data = {
        "age": st.number_input("Age of suspect", min_value=12, format="%i"),
        "gender": st.selectbox("Gender of suspect", options=options_list),
        # Additional fields follow...
        "number_of_victims": st.number_input(
            "Number of Victims", min_value=0, format="%i"
        ),
        "number_of_traffickers": st.number_input(
            "Number of Traffickers", min_value=0, format="%i"
        ),
        "operating_country_id": operating_country_id,
        # Checkbox fields
        "pv_believes_definitely_trafficked_many": st.checkbox(
            "pv_believes_definitely_trafficked_many"
        ),
        "pv_believes_not_a_trafficker": st.checkbox("pv_believes_not_a_trafficker"),
        "pv_believes_trafficked_some": st.checkbox("pv_believes_trafficked_some"),
        "pv_believes_suspect_trafficker": st.checkbox("pv_believes_suspect_trafficker"),
        "exploit_debt_bondage": st.checkbox("exploit_debt_bondage"),
        "exploit_forced_labor": st.checkbox("exploit_forced_labor"),
        "exploit_physical_abuse": st.checkbox("exploit_physical_abuse"),
        "exploit_prostitution": st.checkbox("exploit_prostitution"),
        "exploit_sexual_abuse": st.checkbox("exploit_sexual_abuse"),
        "pv_recruited_agency": st.checkbox("pv_recruited_agency"),
        "pv_recruited_broker": st.checkbox("pv_recruited_broker"),
        "pv_recruited_no": st.checkbox("pv_recruited_no"),
        "friend": st.checkbox("friend"),
        "suspect": st.checkbox("suspect"),
        "missing_information": st.checkbox("missing_information"),
        "transporter": st.checkbox("transporter"),
        "boss_trafficker": st.checkbox("boss_trafficker"),
        "recruiter": st.checkbox("recruiter"),
        "host": st.checkbox("host"),
        "facilitator": st.checkbox("facilitator"),
        "role_other": st.checkbox("role_other"),
        "case_filed_against": st.checkbox("case_filed_against"),
        "pv_attempt": st.checkbox("pv_attempt"),
    }

    # Update the gender in form_data to store the code instead of the user-friendly option
    form_data["gender"] = gender_options[form_data["gender"]]

    input_list = [
        "gender",
        "age",
        "exploit_debt_bondage",
        "exploit_forced_labor",
        "exploit_physical_abuse",
        "exploit_prostitution",
        "exploit_sexual_abuse",
        "pv_recruited_agency",
        "pv_recruited_broker",
        "pv_recruited_no",
        "case_filed_against",
        "operating_country_id",
        "pv_attempt",
        "number_of_victims",
        "number_of_traffickers",
        "pv_believes_definitely_trafficked_many",
        "pv_believes_not_a_trafficker",
        "pv_believes_trafficked_some",
        "pv_believes_suspect_trafficker",
        "transporter",
        "missing_information",
        "boss_trafficker",
        "friend",
        "suspect",
        "facilitator",
        "host",
        "recruiter",
        "role_other",
    ]

    if st.button("Predict"):
        if operating_country_id is not None:
            st.write("Predicting...")
            # Assume form_data and input_list are previously defined and valid
            user_data = pd.DataFrame([form_data])

            # Transform the user input data with all pipeline steps except the classifier
            user_data_transformed = st.session_state["best_pipeline"][:-1].transform(
                user_data[st.session_state["case_dispatcher_model_cols"]]
            )
            # Make a prediction using only the classifier

            prediction = st.session_state["clf"].predict_proba(user_data_transformed)[
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
            shap_values = explainer(user_data_transformed, check_additivity=False)

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
