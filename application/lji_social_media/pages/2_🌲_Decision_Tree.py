import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.utils import resample
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler

st.sidebar.radio("AI vendor", ["Anthropic", "OpenAI"], key="AI")


with st.expander("Click to reveal the original LJI sample adverts"):
    st.dataframe(
        st.session_state.comparison_data[
            ["Advert", "Monitor Rating"] + st.session_state.features
        ]
    )


if st.button("Build Decision Tree Model.."):
    # Prepare the dependent variable
    st.session_state["y"] = st.session_state.comparison_data["Monitor Rating"]

    # Prepare the independent variables (binary columns)
    X = st.session_state.comparison_data[st.session_state.features]

    # Remove constant columns if any
    constant_columns = [col for col in X.columns if X[col].nunique() <= 1]
    st.markdown(
        f"The following columns are CONSTANT and will be removed: {constant_columns}"
    )
    st.session_state["X"] = X.drop(columns=constant_columns)
    st.session_state["DT_columns"] = st.session_state["X"].columns
    X_train, X_test, y_train, y_test = train_test_split(
        st.session_state["X"], st.session_state["y"], test_size=0.2, random_state=42
    )

    # Define the parameter grid
    param_grid = {
        "max_depth": [2, 4, 6, 8, 10],
        "min_samples_split": [2, 5, 10],
        "min_samples_leaf": [1, 2, 4],
    }

    # Initialize the decision tree classifier
    dt = DecisionTreeClassifier(random_state=42)

    # Set up the grid search
    grid_search = GridSearchCV(
        estimator=dt, param_grid=param_grid, cv=5, n_jobs=-1, scoring="accuracy"
    )

    # Fit the grid search to the data
    grid_search.fit(X_train, y_train)

    st.session_state["DT_model"] = grid_search.best_estimator_

    # Predict ratings for all rows using the best estimator
    st.session_state.comparison_data["DT Predicted Rating"] = st.session_state[
        "DT_model"
    ].predict(st.session_state["X"])

if "DT Predicted Rating" in st.session_state.comparison_data.columns:
    with st.expander(
        "Click to reveal the Decision Tree predictions of Monitor Ratings"
    ):
        if "OR Predicted Rating" in st.session_state.comparison_data.columns:
            st.dataframe(
                st.session_state.comparison_data[
                    [
                        "Advert",
                        "Monitor Rating",
                        "OR Predicted Rating",
                        "DT Predicted Rating",
                    ]
                ]
            )
        else:
            st.dataframe(
                st.session_state.comparison_data[
                    ["Advert", "Monitor Rating", "DT Predicted Rating"]
                ]
            )

if "DT_model" in st.session_state:
    if st.button("Bootstrapping to estimate confidence intervals"):
        n_bootstraps = 1000
        bootstrap_preds = np.zeros(
            (n_bootstraps, len(st.session_state.comparison_data))
        )
        for i in range(n_bootstraps):
            # Resample the data
            X_resampled, y_resampled = resample(
                st.session_state["X"], st.session_state["y"], random_state=i
            )

            # Train the model on the resampled data
            st.session_state["DT_model"].fit(X_resampled, y_resampled)

            # Predict on the entire dataset
            bootstrap_preds[i] = st.session_state["DT_model"].predict(
                st.session_state["X"]
            )
        st.session_state.comparison_data["DT lower_bounds"] = np.percentile(
            bootstrap_preds, 2.5, axis=0
        )
        st.session_state.comparison_data["DT upper_bounds"] = np.percentile(
            bootstrap_preds, 97.5, axis=0
        )

# Add confidence intervals to the DataFrame

if "DT lower_bounds" in st.session_state.comparison_data.columns:
    with st.expander("Click to reveal the predictions and confidence intervals"):
        st.dataframe(
            st.session_state.comparison_data[
                [
                    "Advert",
                    "Monitor Rating",
                    "DT Predicted Rating",
                    "DT lower_bounds",
                    "DT upper_bounds",
                ]
            ]
        )


# Display the list of standardized observations
if "DT_model" in st.session_state:
    st.text_area(
        "Enter the text of an advert here...",
        key="advert_text",
        height=200,
        max_chars=5000,
    )
    st.multiselect(
        "Select one or more of the standardized observations from this list for a what if analysis",
        options=st.session_state["features"],
        key="whatif_features",
    )

if "whatif_features" in st.session_state and st.session_state["whatif_features"]:
    st.write("Enter values for the selected features:")

    # Create input fields for selected features
    user_inputs = {}
    for feature in st.session_state["DT_columns"]:
        if feature in st.session_state["whatif_features"]:
            user_inputs[feature] = 1
        else:
            user_inputs[feature] = 0

    if st.button("Predict Rating"):
        if "DT_model" not in st.session_state:
            st.error("Please build the Decision Tree Model first.")
        else:
            # Prepare input data
            input_data = pd.DataFrame([user_inputs])

            # Ensure input data has all the features the model was trained on
            for col in st.session_state["X"].columns:
                if col not in input_data.columns:
                    input_data[col] = 0  # or any appropriate default value

            # Reorder columns to match the training data
            input_data = input_data[st.session_state["X"].columns]

            # Use the model to predict the rating
            predicted_rating = st.session_state["DT_model"].predict(input_data)[0]

            st.write(f"Predicted Rating: {predicted_rating}")
