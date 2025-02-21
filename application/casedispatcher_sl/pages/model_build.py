import io
import json
import os
from datetime import date, datetime
from pathlib import Path
from time import time

import altair as alt
import altair_saver
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import vl_convert
from googleapiclient.discovery import build
from oauth2client.client import OAuth2Credentials
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    auc,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.tree import export_text

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler

from libraries.case_dispatcher_model import get_cls_pipe
from libraries.google_lib import (
    attrdict_to_dict,
    get_file_id,
    get_dfs,
    get_gsheets,
    load_from_cloud,
    make_file_bytes,
    save_chart_to_cloud,
    save_to_cloud,
)

# Print version info
print(f"altair_saver version: {altair_saver.__version__}")
print(f"vl_convert version: {vl_convert.__version__}")

# Initialize Google Drive service credentials
case_dispatcher = st.secrets["case_dispatcher"]
access_token = case_dispatcher["access_token"]
creds_json = json.dumps(attrdict_to_dict(access_token))
credentials = OAuth2Credentials.from_json(creds_json)
drive_service = build("drive", "v3", credentials=credentials)


def check_grid_search_cv(
        soc_df: pd.DataFrame, gscv: str, cutoff_days: int
) -> tuple:
    """
    Run grid search cross-validation if enabled.

    Parameters:
        soc_df (pd.DataFrame): DataFrame containing case information.
        gscv (str): Flag ("On" to run grid search).
        cutoff_days (int): Number of days to use as cutoff.

    Returns:
        tuple: (best_model, feature_columns, X_validation, y_validation) if gscv is "On".
    """
    if gscv == "On":
        return full_gridsearch_pipe(soc_df, cutoff_days)
    return None, None, None, None


def remove_recent(soc_df: pd.DataFrame, cutoff_days: int) -> pd.DataFrame:
    """
    Eliminate cases more recent than the cutoff date.

    Parameters:
        soc_df (pd.DataFrame): DataFrame containing case information.
        cutoff_days (int): Days from today to use as the cutoff.

    Returns:
        pd.DataFrame: DataFrame with cases older than cutoff or that resulted in an arrest.
    """
    today = pd.Timestamp(date.today())
    soc_df["interview_date"] = pd.to_datetime(soc_df["interview_date"], errors="coerce")
    soc_df["days"] = (today - soc_df["interview_date"]).dt.days.fillna(-999).astype(int)
    return soc_df[(soc_df["days"] > cutoff_days) | (soc_df["arrested"] == 1)]


def train_test_val_split(
        sub_df: pd.DataFrame, test_size: float = 0.2
) -> tuple:
    """
    Split dataset into training and testing sets.

    Parameters:
        sub_df (pd.DataFrame): Input DataFrame.
        test_size (float, optional): Fraction for the test set. Default is 0.2.

    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    y = sub_df["arrested"]
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
            "case_id",
        ]
    )
    return train_test_split(X, y, test_size=test_size, random_state=42)


def full_gridsearch_pipe(
        soc_df: pd.DataFrame, cutoff_days: int = 90
) -> tuple:
    """
    Run grid search on a classifier pipeline.

    Parameters:
        soc_df (pd.DataFrame): DataFrame with case data.
        cutoff_days (int, optional): Cutoff for recency. Default is 90.

    Returns:
        tuple: (best_model, feature_columns, X_validation, y_validation)
    """
    sub_df = remove_recent(soc_df, cutoff_days)
    X_train, X_validation, y_train, y_validation = train_test_val_split(sub_df)
    cls_pipeline = get_cls_pipe()
    best_model = do_gridsearch(cls_pipeline, X_train, y_train)
    x_cols = list(X_validation.columns)
    return best_model, x_cols, X_validation, y_validation


def do_gridsearch(
        cls_pipeline: Pipeline, X_train: pd.DataFrame, y_train: pd.Series
) -> GridSearchCV:
    """
    Perform grid search cross-validation to find the best classifier.

    Parameters:
        cls_pipeline (Pipeline): Scikit-learn pipeline including a classifier.
        X_train (pd.DataFrame): Training features.
        y_train (pd.Series): Training labels.

    Returns:
        GridSearchCV: The grid search object after fitting.
    """
    search_space = [
        {
            "clf": [RandomForestClassifier(random_state=42)],
            "clf__bootstrap": [False, True],
            "clf__n_estimators": [10, 50, 100],
            "clf__max_depth": [10, 20, 30],
            "clf__max_features": [0.5, 0.6, 0.7],
            "clf__class_weight": ["balanced", None],
        }
    ]
    grid_search = GridSearchCV(cls_pipeline, search_space, cv=10, n_jobs=-1, verbose=1)
    print("Performing grid search with parameters:")
    print(search_space)
    t0 = time()
    best_model = grid_search.fit(X_train, y_train)
    print(f"Grid search done in {time() - t0:0.3f}s")
    best_parameters = best_model.best_estimator_.get_params()["clf"]
    print(f"Best score: {grid_search.best_score_:0.3f}")
    print("Best parameters set:")
    print(best_parameters)
    return best_model


def make_new_predictions(X: pd.DataFrame, soc_model: GridSearchCV) -> np.ndarray:
    """
    Generate prediction probabilities using an existing classifier.

    Parameters:
        X (pd.DataFrame): New case data.
        soc_model: Trained classifier model.

    Returns:
        np.ndarray: Array of probabilities for the positive class.
    """
    return soc_model.predict_proba(X)[:, 1]


def plot_roc_curve_altair(
        y_true: np.ndarray, model_predictions: list, model_names: list
) -> alt.Chart:
    """
    Plot ROC curves for multiple models using Altair.

    Parameters:
        y_true (np.ndarray): True binary labels.
        model_predictions (list): List of prediction probability arrays.
        model_names (list): Names corresponding to each model.

    Returns:
        alt.Chart: Combined ROC curve chart.
    """
    roc_data = pd.DataFrame()
    for predictions, model_name in zip(model_predictions, model_names):
        fpr, tpr, _ = roc_curve(y_true, predictions)
        roc_auc = auc(fpr, tpr)
        tmp_df = pd.DataFrame({
            "False Positive Rate": fpr,
            "True Positive Rate": tpr,
            "Model": model_name,
            "AUC": f"AUC = {roc_auc:.2f}",
        })
        roc_data = pd.concat([roc_data, tmp_df], ignore_index=True)

    base = alt.Chart(roc_data).encode(
        x=alt.X("False Positive Rate", title="False Positive Rate"),
        y=alt.Y("True Positive Rate", title="True Positive Rate"),
    )
    roc_lines = base.mark_line().encode(
        color=alt.Color("Model", legend=alt.Legend(title="Model")),
        tooltip=["Model", "AUC"],
    )
    auc_points = base.mark_text(dy=-5, align="right").encode(
        x=alt.value(1), y=alt.value(1), text="AUC", color=alt.Color("Model", legend=None)
    )
    baseline = alt.Chart(pd.DataFrame({"x": [0, 1], "y": [0, 1]})).mark_line(strokeDash=[5, 5]).encode(
        x="x", y="y"
    )
    final_chart = (roc_lines + auc_points + baseline).properties(
        width=600, height=400, title="Receiver Operating Characteristic"
    )

    # Ensure plots directory exists
    plots_path = Path("plots")
    plots_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = plots_path / f"roc_curve_{timestamp}.svg"
    try:
        altair_saver.save(final_chart, str(plot_filename), method="vlc")
        print(f"Chart saved successfully to {plot_filename}")
    except Exception as e:
        print(f"Error saving chart: {e}")

    return final_chart


def load_data() -> pd.DataFrame:
    """
    Load case data from Google Drive.

    Returns:
        pd.DataFrame: Loaded DataFrame.
    """
    file_name = "case_dispatcher_soc_df.pkl"
    st.write(f"Datafile name: {file_name}")
    file_id = get_file_id(file_name, drive_service)
    st.write(f"Datafile ID: {file_id}")
    data = load_from_cloud(drive_service, file_id)
    st.write(f"Datafile shape: {data.shape}")
    return data


def build_and_train_model(
        model_data: pd.DataFrame, cutoff_days: int
) -> tuple:
    """
    Build and train a model using grid search.

    Parameters:
        model_data (pd.DataFrame): Input case data.
        cutoff_days (int): Cutoff days for data filtering.

    Returns:
        tuple: (model, feature_names, X_validation, y_validation)
    """
    return full_gridsearch_pipe(model_data, cutoff_days)


def get_sorted_feature_importances(
        model: GridSearchCV, feature_names: list
) -> pd.DataFrame:
    """
    Get sorted feature importances from the trained model.

    Parameters:
        model (GridSearchCV): Trained model.
        feature_names (list): List of feature names.

    Returns:
        pd.DataFrame: DataFrame sorted by feature importance.
    """
    importances = model.best_estimator_.named_steps["clf"].feature_importances_
    importance_df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
    return importance_df.sort_values(by="Importance", ascending=False)


def create_feature_importance_chart(importance_df: pd.DataFrame) -> alt.Chart:
    """
    Create and save a feature importance chart.

    Parameters:
        importance_df (pd.DataFrame): DataFrame of feature importances.

    Returns:
        alt.Chart: The generated Altair chart.
    """
    chart_height = 20 * len(importance_df) + 100
    chart = alt.Chart(importance_df).mark_bar().encode(
        x=alt.X("Importance", sort=None),
        y=alt.Y("Feature", sort="-x", axis=alt.Axis(title="Feature")),
        tooltip=["Feature", "Importance"],
    ).properties(height=chart_height)

    plots_path = Path("plots")
    plots_path.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = plots_path / f"feature_importance_{timestamp}.svg"
    try:
        altair_saver.save(chart, str(plot_filename), method="vlc")
        print(f"Chart saved successfully to {plot_filename}")
    except Exception as e:
        print(f"Error saving chart: {e}")

    return chart


def display_feature_importances(model: GridSearchCV, feature_names: list) -> None:
    """
    Display feature importances using an Altair chart in Streamlit.

    Parameters:
        model (GridSearchCV): Trained model.
        feature_names (list): List of feature names.
    """
    importance_df = get_sorted_feature_importances(model, feature_names)
    st.markdown("## Feature Importances")
    chart_height = 20 * len(importance_df) + 100
    chart = alt.Chart(importance_df).mark_bar().encode(
        x=alt.X("Importance", sort=None),
        y=alt.Y("Feature", sort="-x", axis=alt.Axis(title="Feature")),
        tooltip=["Feature", "Importance"],
    ).properties(height=chart_height)
    st.altair_chart(chart, use_container_width=True)


def display_correlations(df: pd.DataFrame, selected_feature: str) -> None:
    """
    Display correlations between features and the target variable.

    Parameters:
        df (pd.DataFrame): DataFrame with features and target.
        selected_feature (str): Feature to compare correlations.
    """
    y = df["arrested"]
    X = df.drop(columns=["arrested"])
    st.markdown("## Correlation with Target")
    st.write(X.corrwith(y).get(selected_feature))
    st.markdown("## Correlation with Selected Feature")
    st.write(X.corr().get(selected_feature))


def display_first_tree_rules(model: GridSearchCV, feature_names: list) -> None:
    """
    Display rules from the first decision tree of the ensemble.

    Parameters:
        model (GridSearchCV): Trained model.
        feature_names (list): List of feature names.
    """
    tree = model.best_estimator_.named_steps["clf"].estimators_[0]
    tree_rules = export_text(tree, feature_names=feature_names)
    st.markdown("## First Decision Tree Rules")
    with st.expander("See First Decision Tree Rules"):
        st.text(tree_rules)


def save_model_to_cloud(model_obj, model_name: str, drive_service) -> str:
    """
    Save a model object to Google Drive.

    Parameters:
        model_obj: The model object to save.
        model_name (str): Name for the saved file.
        drive_service: Authorized Google Drive service.

    Returns:
        str: The file ID on Google Drive.
    """
    file_bytes = make_file_bytes(model_obj)
    file_metadata = {"name": model_name}
    return save_to_cloud(file_bytes, drive_service, file_metadata)


def main() -> None:
    cutoff_days = st.sidebar.slider("Select cutoff days", min_value=0, max_value=365, value=90)
    st.write(f"Cutoff days selected: {cutoff_days}")

    if st.button("Build model"):
        data = load_data()
        model, feature_names, X_validation, y_validation = build_and_train_model(data, cutoff_days)

        # Display feature importance
        display_feature_importances(model, feature_names)

        # Save models and validation data to cloud
        save_model_to_cloud(feature_names, "case_dispatcher_model_cols.pkl", drive_service)
        save_model_to_cloud(model, "case_dispatcher_model.pkl", drive_service)

        for df_obj, fname in zip([X_validation, y_validation], ["x_validation.pkl", "y_validation.pkl"]):
            file_bytes = make_file_bytes(df_obj)
            file_metadata = {"name": fname}
            file_id = save_to_cloud(file_bytes, drive_service, file_metadata)
            st.write(f"Saved {fname} to cloud with file_id: {file_id}")

        # Display correlations for a selected feature
        feature_to_correlate = st.selectbox(
            "Select a feature to see its correlation with the target", feature_names
        )
        # Uncomment the following line if you want to display correlations:
        # display_correlations(data[feature_names + ["arrested"]], feature_to_correlate)

        # Display first decision tree rules
        display_first_tree_rules(model, feature_names)

        # Create predictions on the validation set
        valid_features = X_validation[X_validation.columns.intersection(feature_names)]
        X_validation["rf_arrest_prediction"] = model.predict_proba(valid_features)[:, 1]
        predictions = X_validation["rf_arrest_prediction"]
        y_true = y_validation

        # Compute performance metrics
        roc_auc_rf = roc_auc_score(y_true, predictions)
        predictions_binary = (predictions >= 0.5).astype(int)
        accuracy_rf = accuracy_score(y_true, predictions_binary)
        precision_rf = precision_score(y_true, predictions_binary)
        recall_rf = recall_score(y_true, predictions_binary)
        f1_rf = f1_score(y_true, predictions_binary)

        # Plot ROC curve
        roc_chart = plot_roc_curve_altair(y_true, [predictions], ["Random Forest"])
        st.altair_chart(roc_chart, use_container_width=True)

        st.markdown("## Model Performance Metrics")
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
