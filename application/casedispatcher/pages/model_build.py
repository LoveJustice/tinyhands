import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import date
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from time import time
import streamlit as st
from sklearn.tree import export_text
from googleapiclient.discovery import build
import altair as alt
import io
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from datetime import datetime
import os
from oauth2client.client import OAuth2Credentials
from libraries.case_dispatcher_model import get_cls_pipe

# from .case_dispatcher_logging import setup_logger
import pickle
from pathlib import Path
import json
from libraries.google_lib import (
    make_file_bytes,
    save_to_cloud,
    get_gsheets,
    get_dfs,
    attrdict_to_dict,
    make_file_bytes,
    save_to_cloud,
    get_file_id,
    load_from_cloud,
    save_chart_to_cloud,
)
from sklearn.metrics import (
    roc_auc_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

case_dispatcher = st.secrets["case_dispatcher"]
access_token = case_dispatcher["access_token"]
toml_config_dict = attrdict_to_dict(access_token)
creds_json = json.dumps(toml_config_dict)
credentials = OAuth2Credentials.from_json(creds_json)
drive_service = build("drive", "v3", credentials=credentials)


def check_grid_search_cv(soc_df, gscv, cutoff_days):
    """Check to see if Grid Search CV is on, and if it is run Grid Search CV."""
    if gscv == "On":
        best_model, x_cols, X_Validation = full_gridsearch_pipe(soc_df, cutoff_days)
    return best_model, x_cols, X_Validation


def remove_recent(soc_df, cutoff_days):
    """
    Eliminates cases more recent than the cutoff date.

    Parameters:
        soc_df (pandas.DataFrame): A dataframe containing case information.
        cutoff_days (int): The number of days from the present to use as the cutoff point.

    Returns:
        pandas.DataFrame: A dataframe containing only cases that are older than the cutoff date or that resulted in an arrest.
    """
    # Get the current date and format it as a string
    today = pd.Timestamp(date.today())

    # Convert 'interview_date' to datetime, errors='coerce' will turn incorrect formats to NaT
    soc_df["interview_date"] = pd.to_datetime(soc_df["interview_date"], errors="coerce")

    # Calculate the number of days, with a default of -999 for NaT or missing values
    soc_df["days"] = (today - soc_df["interview_date"]).dt.days
    soc_df["days"].fillna(-999, inplace=True)
    soc_df["days"] = soc_df["days"].astype(int)

    # Create a new dataframe containing only cases that are older than the cutoff date or that resulted in an arrest
    sub_df = soc_df[(soc_df["days"] > cutoff_days) | (soc_df["arrested"] == 1)]

    return sub_df


def train_test_val_split(sub_df, te_size=0.2, val_size=0.1):
    """
    Splits dataset into training, testing, and validation sets.

    Parameters
    ----------
    sub_df : DataFrame
        The input DataFrame to split.
    te_size : float, optional
        The size of the test set, as a fraction of the input data. The default is 0.2.
    val_size : float, optional
        The size of the validation set, as a fraction of the training set. The default is 0.1.

    Returns
    -------
    tuple
        Four DataFrames, representing the training, validation, and testing sets.
    """
    # Save the 'Arrest' column as y

    y = sub_df.arrested

    # Remove certain columns from the DataFrame, except 'Arrest'
    X = sub_df.drop(
        columns=[
            "arrested",
            "sf_number",
            "days",
            "interview_date",
            "date_of_interception",
            "person_id",
            "case_notes",
            "social_media",
            "master_person_id",
            "irf_number",
            "operating_country_id",
            "country",
            "gender",
            "case_id",
        ]
    )

    # Split the data into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=te_size)

    # Return the training, validation, and testing sets
    return x_train, x_test, y_train, y_test


def full_gridsearch_pipe(soc_df, cutoff_days=90):
    sub_df = remove_recent(soc_df, cutoff_days)
    X_train, X_validation, y_train, y_validation = train_test_val_split(sub_df)

    cls_pipeline = get_cls_pipe()
    best_model = do_gridsearch(cls_pipeline, X_train, y_train)
    x_cols = list(X_validation.columns)
    return best_model, x_cols, X_validation, y_validation


def do_gridsearch(cls_pipeline, X_train, y_train):
    """
    Conduct grid search cross-validation on a classifier pipeline to find the best model.

    Args:
        cls_pipeline: A scikit-learn pipeline object containing a classifier.
        X_train (array-like): Training data.
        y_train (array-like): Training labels.

    Returns:
        sklearn.model_selection._search.GridSearchCV: The best model found by grid search.
    """
    # Define the parameter grid for the grid search
    search_space = [
        {
            "clf": [RandomForestClassifier(random_state=42)],
            "clf__bootstrap": [False, True],
            "clf__n_estimators": [10, 50, 100],
            #'clf__max_depth': [5, 10, 20, 30, 40, 50, None],
            "clf__max_depth": [10, 20, 30],
            #'clf__max_features': [0.5, 0.6, 0.7, 0.8, 1],
            "clf__max_features": [0.5, 0.6, 0.7],
            "clf__class_weight": ["balanced", None],
        }
    ]
    #'clf__class_weight': ["balanced",
    #                      "balanced_subsample", None]}]

    # Create a grid search object using the classifier pipeline and parameter grid
    grid_search = GridSearchCV(cls_pipeline, search_space, cv=10, n_jobs=-1, verbose=1)

    # Print the parameters being searched
    print("Performing grid search...")
    print("parameters:")
    print(search_space)

    # Start the timer and conduct the grid search
    t0 = time()
    best_model = grid_search.fit(X_train, y_train)
    print("done in %0.3fs" % (time() - t0))
    print()

    # Get the best parameters from the model
    best_parameters = best_model.best_estimator_.get_params()["clf"]

    # Print the best score and parameters found by the grid search
    print("Best score: %0.3f" % grid_search.best_score_)
    print("Best parameters set:")
    print(best_parameters)

    # Return the best model
    return best_model


def make_new_predictions(X, soc_model):
    """Use existing classifier algorithm on new cases without recalculating
    best fit."""

    return soc_model.predict_proba(X)[:, 1]


def plot_roc_curve_altair(y_true, model_predictions, model_names):
    """
    Plots the ROC curve for multiple models using Altair and calculates the AUC.

    Parameters:
    y_true (array): The true binary labels.
    model_predictions (list of arrays): A list containing the prediction probabilities from each model.
    model_names (list of str): Names of the models corresponding to the predictions.
    """

    # Prepare data for Altair
    roc_data = pd.DataFrame()

    for predictions, model_name in zip(model_predictions, model_names):
        fpr, tpr, _ = roc_curve(y_true, predictions)
        roc_auc = auc(fpr, tpr)
        tmp_df = pd.DataFrame(
            {
                "False Positive Rate": fpr,
                "True Positive Rate": tpr,
                "Model": model_name,
                "AUC": f" AUC = {roc_auc:.2f}",
            }
        )
        roc_data = pd.concat([roc_data, tmp_df], ignore_index=True)

    # Base chart with common encodings
    base = alt.Chart(roc_data).encode(
        x=alt.X("False Positive Rate", title="False Positive Rate"),
        y=alt.Y("True Positive Rate", title="True Positive Rate"),
    )

    # Line chart for each model
    roc_lines = base.mark_line().encode(
        color=alt.Color("Model", legend=alt.Legend(title="Model")),
        tooltip=["Model", "AUC"],
    )

    # Points to highlight the AUC on the chart
    auc_points = base.mark_text(dy=-5, align="right").encode(
        x=alt.value(1),  # Align the text at the end of the plot
        y=alt.value(1),
        text="AUC",
        color=alt.Color("Model", legend=None),
    )

    # Combine the charts
    final_chart = roc_lines + auc_points

    # Plot baseline (no skill classifier)
    baseline = (
        alt.Chart(pd.DataFrame({"x": [0, 1], "y": [0, 1]}))
        .mark_line(strokeDash=[5, 5])
        .encode(x="x", y="y")
    )

    return (final_chart + baseline).properties(
        width=600, height=400, title="Receiver Operating Characteristic"
    )


# Example usage:
# y_true = [actual binary labels]
# model_predictions = [list of prediction probabilities from each model]
# model_names = [list of model names]
# roc_chart = plot_roc_curve_altair(y_true, model_predictions, model_names)
# roc_chart.display()


def load_data():
    case_dispatcher_soc_file_name = f"case_dispatcher_soc_df.pkl"
    st.write(f"Datafile name: {case_dispatcher_soc_file_name}")
    case_dispatcher_soc_file_id = get_file_id(
        case_dispatcher_soc_file_name, drive_service
    )
    st.write(f"Datafile ID: {case_dispatcher_soc_file_id}")
    model_data = load_from_cloud(drive_service, case_dispatcher_soc_file_id)
    st.write(f"Datafile size: {model_data.shape}")
    return model_data


def build_and_train_model(model_data, day_limit):
    (
        model,
        feature_names,
        x_validation,
        y_validation,
    ) = full_gridsearch_pipe(model_data, day_limit)
    return (
        model,
        feature_names,
        x_validation,
        y_validation,
    )


def get_sorted_feature_importances(model, feature_names):
    feature_importances = model.best_estimator_.named_steps["clf"].feature_importances_
    importance_df = pd.DataFrame(
        {"Feature": feature_names, "Importance": feature_importances}
    )
    sorted_importance_df = importance_df.sort_values(by="Importance", ascending=False)
    return sorted_importance_df


def create_feature_importance_chart(importance_df):
    chart_height = 20 * len(importance_df) + 100
    chart = (
        alt.Chart(importance_df)
        .mark_bar()
        .encode(
            x=alt.X("Importance", sort=None),
            y=alt.Y("Feature", sort="-x", axis=alt.Axis(title="Feature")),
            tooltip=["Feature", "Importance"],
        )
        .properties(height=chart_height)
    )
    return chart


def display_feature_importances_and_save(
    model, feature_names, drive_service, file_metadata
):
    # Step 1: Extract and sort feature importances
    sorted_importance_df = get_sorted_feature_importances(model, feature_names)

    # Step 2: Create the chart
    chart = create_feature_importance_chart(sorted_importance_df)

    # Step 3: Save the chart to a BytesIO object
    chart_bytes = io.BytesIO()
    chart.save(chart_bytes, format="png")
    chart_bytes.seek(0)  # Rewind to the beginning of the BytesIO object

    # Step 4: Save the chart to Google Drive
    save_chart_to_cloud(chart_bytes, drive_service, file_metadata)


def display_feature_importances(model, feature_names):
    feature_importances = model.best_estimator_.named_steps["clf"].feature_importances_
    importance_df = pd.DataFrame(
        {"Feature": feature_names, "Importance": feature_importances}
    )

    # Sort values by Importance in descending order
    importance_df = importance_df.sort_values(by="Importance", ascending=False)

    st.markdown("## Feature Importances")

    # Determine the height of the chart dynamically based on the number of features
    # For example, 20 pixels per bar plus some extra space
    chart_height = 20 * len(importance_df) + 100

    # Create a horizontal bar chart using Altair
    chart = (
        alt.Chart(importance_df)
        .mark_bar()
        .encode(
            x=alt.X("Importance", sort=None),  # No sorting here; data is pre-sorted
            y=alt.Y(
                "Feature", sort="-x", axis=alt.Axis(title="Feature")
            ),  # Sort bars based on Importance
            tooltip=["Feature", "Importance"],  # Show tooltip on hover
        )
        .properties(height=chart_height)  # Set the dynamic height
    )

    st.altair_chart(chart, use_container_width=True)  # Display the chart in Streamlit


def display_correlations(df, selected_feature):
    y = df["arrested"]  # Your target variable
    X = df.drop(columns=["arrested"])  # Your features

    st.markdown("## Correlation with Target")
    correlations = X.corrwith(y)
    st.write(correlations.loc[selected_feature])

    st.markdown("## Correlation with Selected Feature")
    recruiter_correlations = X.corr()[selected_feature]
    st.write(recruiter_correlations)


def display_first_tree_rules(model, feature_names):
    tree = model.best_estimator_.named_steps["clf"].estimators_[0]
    tree_rules = export_text(tree, feature_names=feature_names)

    st.markdown("## First Decision Tree Rules")
    with st.expander("See First Decision Tree Rules"):
        st.text(tree_rules)


def save_model_to_cloud(model, model_name, drive_service):
    file_bytes = make_file_bytes(model)
    file_metadata = {"name": model_name}
    file_id = save_to_cloud(file_bytes, drive_service, file_metadata)
    return file_id


def main():
    # Create a slider for selecting cutoff_days
    cutoff_days = st.sidebar.slider(
        "Select cutoff days", min_value=0, max_value=365, value=90
    )

    # Display the selected value of cutoff_days
    st.write(f"Cutoff days selected: {cutoff_days}")

    if st.button("Build model"):
        case_dispatcher_soc_df = load_data()

        (
            case_dispatcher_model,
            case_dispatcher_model_cols,
            x_validation,
            y_validation,
        ) = build_and_train_model(case_dispatcher_soc_df, cutoff_days)
        # case_dispatcher_model_cols.sort()
        # Displaying feature importance
        display_feature_importances(case_dispatcher_model, case_dispatcher_model_cols)

        # st.write(f"Model columns: {case_dispatcher_model_cols}")

        file_id = save_model_to_cloud(
            case_dispatcher_model_cols, "case_dispatcher_model_cols.pkl", drive_service
        )
        file_id = save_model_to_cloud(
            case_dispatcher_model, "case_dispatcher_model.pkl", drive_service
        )
        file_bytes = make_file_bytes(x_validation)
        file_metadata = {"name": "x_validation.pkl"}
        file_id = save_to_cloud(file_bytes, drive_service, file_metadata)
        st.write(f"Save x_validation to cloud with file_id: {file_id}")

        file_bytes = make_file_bytes(y_validation)
        file_metadata = {"name": "y_validation.pkl"}
        file_id = save_to_cloud(file_bytes, drive_service, file_metadata)
        st.write(f"Save y_validation to cloud with file_id: {file_id}")

        # Allowing user to select a feature to see its correlation with the target
        feature_to_correlate = st.selectbox(
            "Select a feature to see its correlation with the target",
            case_dispatcher_model_cols,
        )

        # display_correlations(case_dispatcher_soc_df[case_dispatcher_model_cols], feature_to_correlate)

        # Displaying the rules of the first decision tree
        display_first_tree_rules(case_dispatcher_model, case_dispatcher_model_cols)

        x_validation["rf_arrest_prediction"] = case_dispatcher_model.predict_proba(
            x_validation[x_validation.columns.intersection(case_dispatcher_model_cols)]
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
