import streamlit as st
import json
from googleapiclient.discovery import build
from sklearn.tree import export_text
from oauth2client.client import OAuth2Credentials
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)
from pages.model_build import display_feature_importances, plot_roc_curve_altair
from libraries.google_lib import (
    attrdict_to_dict,
    get_file_id,
    load_from_cloud,
    load_model_and_columns
)
case_dispatcher = st.secrets["case_dispatcher"]
access_token = case_dispatcher["access_token"]
toml_config_dict = attrdict_to_dict(access_token)
creds_json = json.dumps(toml_config_dict)
credentials = OAuth2Credentials.from_json(creds_json)
drive_service = build("drive", "v3", credentials=credentials)

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
        tree = st.session_state['case_dispatcher_model'].best_estimator_.named_steps["clf"].estimators_[0]
        tree_rules = export_text(tree, feature_names=st.session_state["case_dispatcher_model_cols"])
        st.text(tree_rules)

    with st.expander("See feature importances:"):
        display_feature_importances(st.session_state["case_dispatcher_model"],
                                    st.session_state["case_dispatcher_model_cols"])

    x_validation_id = get_file_id(
        'x_validation.pkl', drive_service
    )
    x_validation = load_from_cloud(drive_service=drive_service, file_id=x_validation_id)
    y_validation_id = get_file_id(
        'y_validation.pkl', drive_service
    )
    y_validation = load_from_cloud(drive_service=drive_service, file_id=y_validation_id)

    x_validation["rf_arrest_prediction"] = st.session_state["case_dispatcher_model"].predict_proba(
        x_validation[x_validation.columns.intersection(st.session_state["case_dispatcher_model_cols"])]
    )[:, 1]
    y_true = y_validation
    predictions_rf = x_validation["rf_arrest_prediction"]

    # Calculating ROC-AUC scores
    roc_auc_rf = roc_auc_score(y_true, predictions_rf)

    # Applying a threshold of 0.5 to convert probabilities to binary predictions
    predictions_rf_binary = (predictions_rf >= 0.5).astype(int)
    # Calculating other performance metrics
    accuracy_rf = accuracy_score(y_true, predictions_rf_binary)
    precision_rf = precision_score(y_true, predictions_rf_binary)
    recall_rf = recall_score(y_true, predictions_rf_binary)
    f1_rf = f1_score(y_true, predictions_rf_binary)

    model_predictions = [x_validation["rf_arrest_prediction"]]
    model_names = ["Random Forest"]

    # Plotting the ROC curve
    roc_chart = plot_roc_curve_altair(y_true, model_predictions, model_names)

    # st.pyplot(fig)  # Display the plot in the Streamlit app
    # Display the Altair chart in the Streamlit app
    st.altair_chart(roc_chart, use_container_width=True)
    # Use Markdown for headings
    st.markdown("## Model Performance Metrics")

    # Use Streamlit's metric function for a dashboard-like display
    col1, col2 = st.columns(2)
    with col1:
        st.metric("ROC-AUC Score", f"{roc_auc_rf:.3f}")
        st.metric("Accuracy", f"{accuracy_rf:.3f}")

    with col2:
        st.metric("Precision", f"{precision_rf:.3f}")
        st.metric("Recall", f"{recall_rf:.3f}")

    st.metric("F1 Score", f"{f1_rf:.3f}")

if __name__ == "__main__":
    main()