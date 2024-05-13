import shap
import matplotlib.pyplot as plt
from libraries.google_lib import (
    get_gsheets,
    get_dfs,
    attrdict_to_dict,
    make_file_bytes,
    save_to_cloud,
    load_data,
    get_matching_spreadsheets,
)
from llama_index.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
import pandas as pd
from llama_index import Document

from llama_index import VectorStoreIndex

from libraries.case_dispatcher_data import (
    get_vdf,
    get_suspects,
    get_irf,
    get_suspect_evaluations,
    get_countries,
)
import streamlit as st
import json
from googleapiclient.discovery import build
from copy import deepcopy
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
import logging
import sys
import pandas as pd
from llama_index.query_engine import PandasQueryEngine


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))



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

case_dispatcher_soc_df = load_data(drive_service, 'case_dispatcher_soc_df.pkl')
llm = OpenAI(temperature=0.0, model="gpt-4-turbo-2024-04-09")
memory = ChatMemoryBuffer.from_defaults(token_limit=30000)


def create_case_summary(documents):
    index = VectorStoreIndex.from_documents(documents)
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        llm=llm,
        memory=memory,
        system_prompt=(
            "A a career forensic analyst you have deep insight into crime and criminal activity especially human trafficking.  "
            "Your express goal is to investigate online and legal reports and extract pertinent factual detail."
        ),
    )
    prompt = """ 
    In the following set of documents, each documents relates to one suspect.  The set of documents make up the entire case.
    Please provide a comprehensive narrative of this case, combining all documents.  An age of -99 means an unknown age.
    Do not embellish beyond the facts of the documents.  Any of host, friend, recruiter, suspect, missing_information, facilitator, transporter, boss_trafficker, role_other may consitute the role of a trafficker.
    Pay particular attention to correct grammar and spelling."""
    response = chat_engine.chat(prompt)
    return response
def create_documents(data):
    documents = []
    stories = []
    for index, row in data.iterrows():
        story = create_story(row)
        documents.append(Document(text=story))
        stories.append(story)
    return documents, stories
def left_callback():
    if st.session_state["selected_irf_left"] != "Select an IRF ...":
        st.session_state['entries_left'] = case_dispatcher_soc_df.loc[
                                           case_dispatcher_soc_df['irf_number'] == st.session_state[
                                               'selected_irf_left'], :]
        st.session_state['left_summary'] = None
        st.session_state['left_documents'] = None
        st.session_state['priority_answer']=None



def right_callback():
    if st.session_state["selected_irf_right"] != "Select an IRF ...":
        st.session_state['entries_right'] = case_dispatcher_soc_df.loc[
                                            case_dispatcher_soc_df['irf_number'] == st.session_state[
                                                'selected_irf_right'], :]
        st.session_state['right_summary']=None
        st.session_state['right_documents'] = None
        st.session_state['priority_answer'] = None

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

def get_initial_values():
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
        st.session_state['query_engine'] = PandasQueryEngine(
            df=st.session_state["case_dispatcher_soc_df"].drop(['case_notes'], axis=1), verbose=True)
    if "irf" not in st.session_state:
        st.session_state["irf"] = "Select an IRF..."

def initialize_countries():
    if "countries" not in st.session_state:
        st.session_state["countries"] = get_countries()
        st.session_state["countries_list"] = ["Select a country..."] + sorted(
            st.session_state["countries"]["name"].values.tolist()
        )
    else:
        st.session_state["countries_list"] = ["Select a country..."] + sorted(
            st.session_state["countries"]["name"].values.tolist()
        )
        if "country_list" not in st.session_state:
            st.session_state["country"] = "Select a country..."
        #
        # if st.session_state["country"] not in st.session_state["countries_list"]:
        #     st.session_state["country"] = "Select a country..."

def create_story(row):
    return (
        f"Case Number {row['irf_number']} involves suspect {row['suspect_id']} who was intercepted on {row['interview_date']} "
        f"and involves  {row['number_of_traffickers']} traffickers. "
        f"This suspect, identified as gender denoted by {row['gender']} aged {row['age']}, hails from {row['country']} and has been {'arrested' if row['arrested'] else 'not arrested'} so far. "
        f"The operations included "
        f"{'forced labor, ' if row['exploit_forced_labor'] else ''}"
        f"{'physical abuse, ' if row['exploit_physical_abuse'] else ''}"
        f"{'prostitution, ' if row['exploit_prostitution'] else ''}"
        f"{'sexual abuse, ' if row['exploit_sexual_abuse'] else ''}"
        f"{'debt bondage, ' if row['exploit_debt_bondage'] else ''}. "
        f"The case, filed under SF number {row['sf_number']}, has {row['number_of_victims']} victims. "
        f"Social media used by the suspect includes: {row['social_media']}. "
        f"This individual was identified as "
        f"{'host, ' if row['host'] else ''}"
        f"{'friend, ' if row['friend'] else ''}"
        f"{'recruiter, ' if row['recruiter'] else ''}"
        f"{'facilitator, ' if row['facilitator'] else ''}"
        f"{'transporter, ' if row['transporter'] else ''}"
        f"{'boss trafficker.' if row['boss_trafficker'] else ''} "
        f"The victim(s) "
        f"{'believes the suspect(s) trafficked many people, ' if row['pv_believes_definitely_trafficked_many'] else ''}"
        f"{'does not believe the suspect(s) are a trafficker, ' if row['pv_believes_not_a_trafficker'] else ''}"
        f"{'believes they trafficked some people, ' if row['pv_believes_trafficked_some'] else ''}"
        f"{'is definitely considered a trafficker by victims' if row['pv_believes_suspect_trafficker'] else ''}. "
        f"Economic and criminal indices in their operating country are indicated by resilience {row['resilience']}, criminal markets {row['criminal_markets']}, and government role (gov_rol) {row['gov_rol']} scores."
    )

def case_comparison():
    cases = []
    cases.append(Document(text=st.session_state['left_summary'].response))
    cases.append(Document(text=st.session_state['right_summary'].response))
    index = VectorStoreIndex.from_documents(cases)
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        llm=llm,
        memory=memory,
        system_prompt=(
            "A a career forensic analyst you have deep insight into crime and criminal activity especially human trafficking.  "
            "Your express goal is to investigate online and legal reports and extract pertinent factual detail."
        ),
    )
    prompt = """Assistant, I am handling two criminal cases related to human trafficking and 
    need guidance on which case should be prioritized to maximize the potential for arrests. 
    Could you provide a detailed summary highlighting the differences between the two cases? 
    Additionally, I would appreciate an analysis that includes the reasoning behind which 
    case should be prioritized based on the impact and potential outcomes."""
    st.session_state['priority_answer'] = chat_engine.chat(prompt)


def main():
    tab1, tab2 = st.tabs(["Evaluation", "Intuition test"])
    get_initial_values()
    initialize_countries()
    previous_country = st.session_state.get("previous_country", None)
    current_country_selection = st.selectbox(
        "Select a country",
        st.session_state["countries_list"],
        index=st.session_state["countries_list"].index(
            st.session_state.get("country", "Select a country...")
        ),
    )

    # Update the country selection and previous country in session state
    st.session_state["previous_country"] = st.session_state.get("country", None)
    st.session_state["country"] = current_country_selection

    operating_country_id = None
    if st.session_state["country"] != "Select a country...":
        filtered_countries = st.session_state["countries"][
            st.session_state["countries"]["name"] == st.session_state["country"]
            ].copy()
        if not filtered_countries.empty:
            operating_country_id = filtered_countries["id"].values[0]
            st.write("You selected:", st.session_state["country"])
            st.write(
                f"You selected country: {st.session_state['country']} with country_id: {operating_country_id}"
            )
            irf_list = list(set(st.session_state["case_dispatcher_soc_df"][
                                    st.session_state["case_dispatcher_soc_df"][
                                        "operating_country_id"] == operating_country_id]['irf_number']))
            irf_list.sort()

            # Ensure 'Select an IRF ...' is always the first item in the list
            st.session_state["irfs"] = ["Select an IRF..."] + irf_list

            # Reset the IRF selectbox if the country has changed
            if previous_country != st.session_state["country"]:
                st.session_state["irf"] = "Select an IRF..."

            with tab1:

                if st.session_state["country"] != "Select a country...":
                    # Compute the correct index for the current selection or default
                    irf_index = st.session_state["irfs"].index(st.session_state.get("irf", "Select an IRF..."))

                    selected_irf = st.selectbox(
                        "Select an IRF ...",
                        st.session_state["irfs"],
                        index=irf_index,
                    )
                    # Update the IRF selection in session state
                    st.session_state["irf"] = selected_irf

                if st.session_state["irf"] != "Select an IRF ...":
                    st.session_state["intuition_data"] = (
                        st.session_state["case_dispatcher_soc_df"]
                        .loc[
                        st.session_state["case_dispatcher_soc_df"]["irf_number"]
                        == st.session_state["irf"],
                        :,
                        ]
                        .drop_duplicates()
                    )


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
                        st.write(user_data.dtypes)
                        # Transform the user input data with all pipeline steps except the classifier
                        form_data_transformed = st.session_state["best_pipeline"][:-1].transform(
                            form_data
                        )
                        # Make a prediction using only the classifier

                        prediction = st.session_state["clf"].predict_proba(form_data_transformed)[
                            :, 1
                        ]
                        st.write("Prediction:", prediction)
                        st.write("Prediction:", form_data_transformed)

                        # Transform the model data with all pipeline steps except the classifier
                        st.session_state["model_data_transformed"] = st.session_state["model_data_transformed"].astype(
                            {col: 'int' for col in st.session_state["model_data_transformed"].select_dtypes(['bool']).columns})

                        # Initialize SHAP explainer with the model and the transformed model data
                        explainer = shap.Explainer(
                            st.session_state["clf"],
                            st.session_state["model_data_transformed"],
                            feature_names=st.session_state["case_dispatcher_model_cols"],
                        )

                        # Write debugging information about form_data_transformed


                        # Iterate over each row in form_data_transformed to calculate SHAP values and plot them
                        for index, row in form_data_transformed.iterrows():
                            # Reshape row to be a 2D array suitable for explainer
                            row_reshaped = row.values.reshape(1, -1)

                            # Calculate SHAP values for the current row
                            shap_values = explainer(row_reshaped, check_additivity=False)

                            # Plot SHAP values for the first output of the current row
                            fig, ax = plt.subplots()
                            # Selecting the first output's SHAP values; adjust index for different outputs as needed
                            shap.plots.waterfall(shap_values[0, :, 1],
                                                 max_display=10)  # Optionally limit the number of features displayed
                            st.pyplot(fig, bbox_inches="tight")

                    else:
                        st.error("Please select a valid country before predicting.")

            with tab2:
                st.write("Intuition test")
                st.write('Select two irfs for comparison:')
                if "selected_irf_left" not in st.session_state:
                    st.session_state["selected_irf_left"] = "Select an IRF..."
                if "selected_irf_right" not in st.session_state:
                    st.session_state["selected_irf_right"] = "Select an IRF..."


                if st.session_state["country"] != "Select a country...":
                    # Compute the correct index for the current selection or default


                    irf_index = st.session_state["irfs"].index(st.session_state.get("irf", "Select an IRF..."))
                    col1, col2 = st.columns(2)
                    with col1:
                        st.selectbox(
                            "Select one IRF ...",
                            st.session_state["irfs"],
                            index=irf_index,
                            on_change=left_callback,
                            key='selected_irf_left'
                        )
                    with col2:
                        st.selectbox(
                            "Select another IRF ...",
                            st.session_state["irfs"],
                            index=irf_index,
                            on_change=right_callback,
                            key='selected_irf_right'
                        )
                if st.button("Create stories:",) and st.session_state["selected_irf_left"] != "Select an IRF ..." and st.session_state["selected_irf_right"] != "Select an IRF ...":
                    st.session_state['left_documents'], st.session_state['left_stories'] = create_documents(st.session_state['entries_left'])
                    st.session_state['right_documents'], st.session_state['right_stories'] =  create_documents(st.session_state['entries_right'])
                    col1, col2 = st.columns(2)
                    with col1:
                        st.dataframe(st.session_state['entries_left'])
                        st.markdown(f"{st.session_state['selected_irf_left']}:{st.session_state['left_stories']}")
                    with col2:
                        st.dataframe(st.session_state['entries_right'])
                        st.markdown(f"{st.session_state['selected_irf_right']}:{st.session_state['right_stories']}")

                if st.button("Create case summaries:",) and st.session_state['left_stories'] and st.session_state['right_stories']:
                    st.session_state['left_summary'] = create_case_summary(st.session_state['left_documents'])
                    st.session_state['right_summary'] = create_case_summary(st.session_state['right_documents'])
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(st.session_state['left_summary'])
                    with col2:
                        st.markdown(st.session_state['right_summary'])

                if st.button("Priority call:",) and st.session_state['left_summary'] and st.session_state['right_summary']:
                    case_comparison()
                    st.markdown(f"Verdict: {st.session_state['priority_answer']}")

                if st.button("compare predictions:"):
                    st.write("## Prediction Comparison Dashboard")
                    st.write(
                        "This dashboard compares two different user inputs to predict outcomes and understand the contributing factors for each prediction.")

                    # Mock data for demonstration
                    # You would replace these with the actual form_data for each case
                    form_data_case1 = {"example": [1]}
                    form_data_case2 = {"example": [2]}

                    # Convert form data to DataFrame
                    user_data_case1 = pd.DataFrame(form_data_case1)
                    user_data_case2 = pd.DataFrame(form_data_case2)

                    # Display the input data types
                    st.write("### Data Types of Inputs")
                    st.write("Case 1 Input Types:", user_data_case1.dtypes)
                    st.write("Case 2 Input Types:", user_data_case2.dtypes)

                    # Transform input data
                    form_data_transformed_case1 = st.session_state["best_pipeline"][:-1].transform(form_data_case1)
                    form_data_transformed_case2 = st.session_state["best_pipeline"][:-1].transform(form_data_case2)

                    # Predict probabilities
                    prediction_case1 = st.session_state["clf"].predict_proba(form_data_transformed_case1)[:, 1]
                    prediction_case2 = st.session_state["clf"].predict_proba(form_data_transformed_case2)[:, 1]

                    # Display predictions
                    st.write("### Predictions")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("Prediction for Case 1:", prediction_case1)
                    with col2:
                        st.write("Prediction for Case 2:", prediction_case2)

                    # Initialize SHAP explainer with the model and transformed data
                    explainer = shap.Explainer(
                        st.session_state["clf"],
                        st.session_state["model_data_transformed"],
                        feature_names=st.session_state["case_dispatcher_model_cols"],
                    )

                    # Compare SHAP values
                    st.write("### SHAP Value Analysis")
                    for form_data_transformed, case_label in [(form_data_transformed_case1, "Case 1"),
                                                              (form_data_transformed_case2, "Case 2")]:
                        for index, row in form_data_transformed.iterrows():
                            row_reshaped = row.values.reshape(1, -1)
                            shap_values = explainer(row_reshaped, check_additivity=False)
                            fig, ax = plt.subplots()
                            shap.plots.waterfall(shap_values[0, :, 1], max_display=10)
                            with st.expander(f"SHAP Values for {case_label}"):
                                st.pyplot(fig, bbox_inches="tight")

                    st.write("### Narrative Summary")
                    st.write(
                        "The side-by-side comparison and SHAP value analysis allow us to visually and quantitatively understand the differences in predictions between the two cases. This can inform more nuanced decision-making based on model outputs.")
    else:
        st.error("Selected country not found in the list.")
        if previous_country != st.session_state["country"]:
            st.session_state["irf"] = "Select an IRF..."


if __name__ == "__main__":
    main()
