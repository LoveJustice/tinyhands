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

    if "country_stats" not in st.session_state:
        st.session_state["country_stats"] = pd.read_csv('data/final_data.csv')
        country_list = list(st.session_state["country_stats"]['Country'])

    if "country" not in st.session_state:
        st.session_state["country"] = "Nepal"

    st.session_state["country"] = st.selectbox("Select country stats", country_list, index = country_list.index('Nepal'))
    country_stats = st.session_state["country_stats"][st.session_state["country_stats"]['Country'] == st.session_state["country"]].to_dict('records')

    st.session_state['tree'] = st.session_state["case_dispatcher_model"].best_estimator_.named_steps["clf"].estimators_[0]

    st.session_state["best_pipeline"] = st.session_state[
        "case_dispatcher_model"
    ].best_estimator_
    st.session_state["clf"] = st.session_state["best_pipeline"].named_steps["clf"]

    transformed_array = st.session_state["best_pipeline"][:-1].transform(
        st.session_state["case_dispatcher_soc_df"][st.session_state["case_dispatcher_model_cols"]]
    )

    # Assuming 'case_dispatcher_model_cols' maintains the original desired column order
    model_data_transformed = pd.DataFrame(
        transformed_array,
        columns=st.session_state["case_dispatcher_model_cols"]
    )

    st.session_state["model_data_transformed"] = model_data_transformed

    with st.expander("See decision tree rules:"):
        tree = st.session_state['tree']
        tree_rules = export_text(tree, feature_names=st.session_state["case_dispatcher_model_cols"])
        st.text(tree_rules)

    with st.expander("See feature importances:"):
        display_feature_importances(st.session_state["case_dispatcher_model"], st.session_state["case_dispatcher_model_cols"])

    # Initialize a dictionary to store form data
    form_data = {
        "age": st.number_input("Age of suspect", min_value=40, format="%i"),
        # Additional fields follow...
        "number_of_victims": st.number_input(
            "Number of Victims", min_value=4, format="%i"
        ),
        "number_of_traffickers": st.number_input(
            "Number of Traffickers", min_value=2, format="%i"
        ),
        # Checkbox fields

        "female": st.checkbox("female"),
        "male": st.checkbox("male"),
        "unknown_gender": st.checkbox("unknown_gender"),
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

        "country_reduced": st.checkbox("country_reduced"),
        "country_Bangladesh": st.checkbox("country_Bangladesh"),
        "country_India": st.checkbox("country_India"),
        "country_India Network": st.checkbox("country_India Network"),
        "country_Kenya": st.checkbox("country_Kenya"),
        "country_Liberia": st.checkbox("country_Liberia"),
        "country_Mozambique": st.checkbox("country_Mozambique"),
        "country_Namibia": st.checkbox("country_Namibia"),
        "country_Nepal": st.checkbox("country_Nepal"),
        "country_Other": st.checkbox("country_Other"),
        "country_South Africa": st.checkbox("country_South Africa"),
        "country_Uganda": st.checkbox("country_Uganda"),
        'IBR12': st.number_input('IBR12', min_value=-100.0, max_value=100.0, value=country_stats['IBR12'], format="%f"),
        'eco_ind': st.number_input('Economic Indicator', min_value=-100.0, max_value=100.0, value=country_stats['eco_ind'], format="%f"),
        'edu_human_dev': st.number_input('Education and Human Development', min_value=-100.0, max_value=100.0,
                                         value=country_stats['edu_human_dev'], format="%f"),
        'demo_environ': st.number_input('Demographic Environment', min_value=-100.0, max_value=100.0, value=country_stats['demo_environ'],
                                        format="%f"),
        'adult_migr': st.number_input('Adult Migration', min_value=-100.0, max_value=100.0, value=country_stats['adult_migr'], format="%f"),
        'child_migr': st.number_input('Child Migration', min_value=-100.0, max_value=100.0, value=country_stats['child_migr'], format="%f"),
        'refugee_asylum': st.number_input('Refugee and Asylum Seekers', min_value=-100.0, max_value=100.0, value=country_stats['refugee_asylum'],
                                          format="%f"),
        'resilience': st.number_input('Resilience', min_value=-100.0, max_value=100.0, value=country_stats['resilience'], format="%f"),
        'criminal_markets': st.number_input('Criminal Markets', min_value=-100.0, max_value=100.0, value=country_stats['criminal_markets'],
                                            format="%f"),
        'criminal_actors': st.number_input('Criminal Actors', min_value=-100.0, max_value=100.0, value=country_stats['criminal_actors'],
                                           format="%f"),
        'gov_rol': st.number_input('Governance and Rule of Law', min_value=-100.0, max_value=100.0, value=country_stats['gov_rol'],
                                   format="%f"),
    }




    if st.button("Predict"):
        st.write("Predicting...")
        # Assume form_data and input_list are previously defined and valid
        user_data = pd.DataFrame([form_data])
        user_data.reindex(columns=st.session_state["case_dispatcher_model_cols"])
        user_data_transformed = st.session_state["best_pipeline"][:-1].transform(
            user_data
        )
        display_model_data_transformed = pd.DataFrame(st.session_state["model_data_transformed"].copy())
        with st.expander("See model_data_transformed:"):

            # display_model_data_transformed.columns = st.session_state["case_dispatcher_model_cols"]
            st.dataframe(display_model_data_transformed)
            st.write(display_model_data_transformed.dtypes)

        with st.expander("See scenario data:"):
            st.dataframe(user_data)
            st.write(user_data.dtypes)
        # Transform the user input data with all pipeline steps except the classifier

        with st.expander("See transformed data:"):
            display_user_data_transformed = pd.DataFrame(user_data_transformed.copy())
            # display_user_data_transformed.columns = st.session_state["case_dispatcher_model_cols"]
            st.dataframe(display_user_data_transformed)
            st.write(display_user_data_transformed.dtypes)

        with st.expander("See transformed array:"):
            st.write(transformed_array)
            st.write(display_user_data_transformed.dtypes)
        # Make a prediction using only the classifier

        # prediction = st.session_state["clf"].predict_proba(user_data_transformed)[
        #     :, 1
        # ]
        # st.write("Prediction:", prediction)

        # Transform the model data with all pipeline steps except the classifier

        # Initialize SHAP explainer with the model and the transformed model data
        transformed_array = transformed_array.astype(
            {col: 'int' for col in transformed_array.select_dtypes(['bool']).columns})
        explainer = shap.Explainer(
            st.session_state["clf"],
            transformed_array,
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



if __name__ == "__main__":
    main()
