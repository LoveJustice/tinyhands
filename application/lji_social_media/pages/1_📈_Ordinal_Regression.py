import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from statsmodels.miscmodels.ordinal_model import OrderedModel
from sklearn.utils import resample


with st.expander("Click to reveal the original LJI sample adverts"):
    st.dataframe(
        st.session_state.comparison_data[
            ["Advert", "Monitor Rating"] + st.session_state.features
        ]
    )


if st.button("Build Ordinal Regression Model.."):
    # Prepare the dependent variable
    st.session_state["y"] = st.session_state.comparison_data["Monitor Rating"]

    # Prepare the independent variables (binary columns)
    X = st.session_state.comparison_data[st.session_state.features]

    # Remove constant columns if any
    constant_columns = [col for col in X.columns if X[col].nunique() <= 1]
    st.markdown(
        f"The following columns are CONSTANT and will be removed: {constant_columns}"
    )
    X = X.drop(columns=constant_columns)
    st.session_state["scaler_columns"] = X.columns
    # Standardize the predictors
    st.session_state["scaler"] = StandardScaler()
    X_scaled = st.session_state["scaler"].fit_transform(X)

    # Convert to pandas DataFrame for easier column manipulation
    st.session_state["X_scaled_df"] = pd.DataFrame(X_scaled, columns=X.columns)

    # Fit the initial ordinal regression model without adding a constant
    st.session_state["ordinal_regression_model"] = OrderedModel(
        st.session_state["y"], st.session_state["X_scaled_df"], distr="logit"
    )
    result = st.session_state["ordinal_regression_model"].fit(method="bfgs")

    # Identify predictors with p-value <= 0.5
    significant_predictors = result.pvalues[result.pvalues <= 0.5].index
    # Filter out threshold terms (terms with slashes like '8/9')
    st.session_state["valid_ordinal_predictors"] = [
        pred for pred in significant_predictors if "/" not in pred
    ]
    st.markdown(
        f"The following predictors are valid and significant at the 0.5 significance level: {st.session_state['valid_ordinal_predictors']}"
    )

if "valid_ordinal_predictors" in st.session_state:
    if st.button("Predict Monitor Ratings:"):
        # Refine the dataset to include only significant predictors
        st.session_state["X_refined"] = st.session_state["X_scaled_df"][
            st.session_state["valid_ordinal_predictors"]
        ]

        # Fit the refined ordinal regression model
        st.session_state["OR_model"] = OrderedModel(
            st.session_state["y"], st.session_state["X_refined"], distr="logit"
        )
        st.session_state["result_refined_p5"] = st.session_state["OR_model"].fit(
            method="bfgs"
        )

        # Predict probabilities for each row
        predicted_probs = st.session_state["OR_model"].predict(
            st.session_state["result_refined_p5"].params,
            exog=st.session_state["X_refined"],
        )

        # Choose the rating category with the highest probability for each row
        predicted_ratings = (
            np.argmax(predicted_probs, axis=1) + 1
        )  # +1 to match the original rating scale

        # Add the predicted ratings to the DataFrame
        st.session_state.comparison_data["OR Predicted Rating"] = predicted_ratings

if "OR Predicted Rating" in st.session_state.comparison_data.columns:
    with st.expander(
        "Click to reveal the ordinal regression predictions of Monitor Ratings"
    ):
        st.dataframe(
            st.session_state.comparison_data[
                ["Advert", "Monitor Rating", "OR Predicted Rating"]
            ]
        )

if "OR_model" in st.session_state:
    if st.button("Bootstrapping to estimate confidence intervals"):
        n_bootstraps = 1000
        bootstrap_preds = np.zeros(
            (n_bootstraps, len(st.session_state.comparison_data))
        )

        for i in range(n_bootstraps):
            try:
                # Resample the data
                print(i)
                X_resampled, y_resampled = resample(
                    st.session_state["X_refined"],
                    st.session_state["y"],
                    replace=True,
                    random_state=i,
                )

                # Check for constant columns in the resampled data
                if any(np.var(X_resampled, axis=0) == 0):
                    continue  # Skip if resampling introduces a constant column

                # Fit the model on the resampled data
                bootstrap_model = OrderedModel(y_resampled, X_resampled, distr="logit")
                bootstrap_result = bootstrap_model.fit(method="bfgs", disp=False)

                # Predict on the entire dataset
                bootstrap_probs = bootstrap_model.predict(
                    bootstrap_result.params, exog=st.session_state["X_refined"]
                )
                bootstrap_preds[i] = (
                    np.argmax(bootstrap_probs, axis=1) + 1
                )  # +1 to match the original rating scale

            except Exception as e:
                print(f"Exception at iteration {i}: {e}")
                continue  # Skip to the next iteration
        # Calculate the 95% confidence intervals
        lower_bounds = np.percentile(bootstrap_preds, 2.5, axis=0)
        upper_bounds = np.percentile(bootstrap_preds, 97.5, axis=0)

        # Add confidence intervals to the DataFrame
        st.session_state.comparison_data["OR Lower Bound"] = lower_bounds
        st.session_state.comparison_data["OR Upper Bound"] = upper_bounds

        # Save the DataFrame with predicted ratings and confidence intervals

    # Display the DataFrame with actual and predicted ratings and confidence intervals
if "OR Lower Bound" in st.session_state.comparison_data.columns:
    with st.expander("Click to reveal the predictions and confidence intervals"):
        st.dataframe(
            st.session_state.comparison_data[
                [
                    "Advert",
                    "Monitor Rating",
                    "OR Predicted Rating",
                    "OR Lower Bound",
                    "OR Upper Bound",
                ]
            ]
        )


# Display the list of standardized observations
if "OR_model" in st.session_state:
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
    for feature in st.session_state["scaler_columns"]:
        if feature in st.session_state["whatif_features"]:
            user_inputs[feature] = 1
        else:
            user_inputs[feature] = 0

    if st.button("Predict Rating"):
        if "scaler" not in st.session_state or not hasattr(
            st.session_state["scaler"], "mean_"
        ):
            st.error("Please build the Ordinal Regression Model first.")
        else:
            # Prepare input data
            input_data = pd.DataFrame([user_inputs])

            # Scale the input data using the same scaler used for training
            input_data_scaled = pd.DataFrame(
                st.session_state["scaler"].transform(input_data),
                columns=input_data.columns,
            )

            # Filter the input data to include only the valid predictors
            input_data_filtered = input_data_scaled[
                st.session_state["valid_ordinal_predictors"]
            ]

            # Use the model to predict probabilities
            predicted_probs = st.session_state["OR_model"].predict(
                st.session_state["result_refined_p5"].params,
                exog=input_data_filtered,
            )

            # Choose the rating category with the highest probability
            predicted_rating = (
                np.argmax(predicted_probs) + 1
            )  # +1 to match the original rating scale

            st.write(f"Predicted Rating: {predicted_rating}")
