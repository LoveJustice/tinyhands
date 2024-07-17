import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel

# Load your data
data = pd.read_csv("results/advert_comparison_2.csv")

data = data.drop(index=0)
data.columns = [col.replace("• ", "") for col in data.columns]
data = data.replace({"TRUE": 1, "FALSE": 0})
rename_dict = {"Unnamed: 0": "IDn", "Unnamed: 1": "advert"}
data.rename(columns=rename_dict, inplace=True)
list(data)

# Define your dependent and independent variables
columns = [
    "IDn",
    "Monitor Rating",
    "Recruiting young people who are still in school",
    "Paying more than the market rate for the skill level or type of job that they are hiring for",
    "Not mentioning any skill requirements",
    "Not mentioning the nature of the job",
    "Not mentioning the name or the location of the hiring business",
    "Paying the same salary for different job posts / positions",
    "Hiring for an organization (such as ESKOM) who has publicly stated that they don't advertise job posts on social media",
    "Recruiting specifically females for a job that male or female applicants would qualify for",
    "Unprofessional writing (poor grammar / spelling)",
    "Recruiting models",
    "Changing from English to other languages in the middle of the post",
    "Using a suspicious email address",
    "Advertising for positions in several promises (especially without detail)",
    "Looks Legit",
]

for col in columns:
    data[col] = data[col].astype(int)

data.to_csv("results/advert_comparison_cleaned.csv", index=False)
y = data["Monitor Rating"]
X = data[
    [
        "Recruiting young people who are still in school",
        "Paying more than the market rate for the skill level or type of job that they are hiring for",
        "Not mentioning any skill requirements",
        "Not mentioning the nature of the job",
        "Not mentioning the name or the location of the hiring business",
        "Paying the same salary for different job posts / positions",
        "Hiring for an organization (such as ESKOM) who has publicly stated that they don't advertise job posts on social media",
        "Recruiting specifically females for a job that male or female applicants would qualify for",
        "Unprofessional writing (poor grammar / spelling)",
        "Recruiting models",
        "Changing from English to other languages in the middle of the post",
        "Using a suspicious email address",
        "Advertising for positions in several promises (especially without detail)",
        "Looks Legit",
    ]
]

# Fit the ordinal regression model
model = OrderedModel(np.asarray(y), np.asarray(X), distr="logit")
result = model.fit(method="bfgs")

# Print the summary of the model
print(result.summary())


import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from statsmodels.miscmodels.ordinal_model import OrderedModel

# Load the dataset

file_path = "results/advert_comparison_cleaned.csv"
df = pd.read_csv(file_path)

# Prepare the dependent variable
y = df["Monitor Rating"]

# Prepare the independent variables (binary columns)


# Remove constant columns if any
X = df[columns].fillna(0)
# df[features].to_csv("results/advert_comparison_cleaned.csv", index=False)

constant_columns = [col for col in X.columns if X[col].nunique() <= 1]
X = X.drop(columns=constant_columns)

# Standardize the predictors
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Convert to pandas DataFrame for easier column manipulation
X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns)

# Fit the initial ordinal regression model without adding a constant
model = OrderedModel(y, X_scaled_df, distr="logit")
result = model.fit(method="bfgs")

# Identify predictors with p-value <= 0.3
significant_predictors_p3 = result.pvalues[result.pvalues <= 0.5].index

# Filter out threshold terms (terms with slashes like '8/9')
valid_predictors = [pred for pred in significant_predictors_p3 if "/" not in pred]

# Check if there are any significant predictors
if valid_predictors:
    # Refine the dataset to include only significant predictors
    X_refined_p3 = X_scaled_df[valid_predictors]

    # Fit the refined ordinal regression model
    model_refined_p3 = OrderedModel(y, X_refined_p3, distr="logit")
    result_refined_p3 = model_refined_p3.fit(method="bfgs")

    # Print the summary of the refined model
    print(result_refined_p3.summary())

    # Predict probabilities for each row
    predicted_probs = model_refined_p3.predict(
        result_refined_p3.params, exog=X_refined_p3
    )

    # Choose the rating category with the highest probability for each row
    predicted_ratings = (
        np.argmax(predicted_probs, axis=1) + 1
    )  # +1 to match the original rating scale

    # Add the predicted ratings to the DataFrame
    df["Predicted Rating"] = predicted_ratings

    # Bootstrapping to estimate confidence intervals
    n_bootstraps = 1000
    bootstrap_preds = np.zeros((n_bootstraps, len(df)))

    for i in range(n_bootstraps):
        # Resample the data
        X_resampled, y_resampled = resample(X_refined_p3, y, random_state=i)

        # Fit the model on the resampled data
        bootstrap_model = OrderedModel(y_resampled, X_resampled, distr="logit")
        bootstrap_result = bootstrap_model.fit(method="bfgs", disp=False)

        # Predict on the entire dataset
        bootstrap_probs = bootstrap_model.predict(
            bootstrap_result.params, exog=X_refined_p3
        )
        bootstrap_preds[i] = (
            np.argmax(bootstrap_probs, axis=1) + 1
        )  # +1 to match the original rating scale

    # Display the DataFrame with predicted ratings
    predicted_ratings_df = df[["Monitor Rating", "Predicted Rating"]]
else:
    print("No predictors are significant at the 0.3 level.")

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from statsmodels.miscmodels.ordinal_model import OrderedModel
from sklearn.utils import resample

# Load the dataset
file_path = "results/advert_comparison_cleaned.csv"
df = pd.read_csv(file_path)
list(df)
# Prepare the dependent variable
y = df["Monitor Rating"]

# Prepare the independent variables (binary columns)
X = df.iloc[:, 6:]

# Remove constant columns if any
constant_columns = [col for col in X.columns if X[col].nunique() <= 1]
X = X.drop(columns=constant_columns)

# Standardize the predictors
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Convert to pandas DataFrame for easier column manipulation
X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns)

# Fit the initial ordinal regression model without adding a constant
model = OrderedModel(y, X_scaled_df, distr="logit")
result = model.fit(method="bfgs")

# Identify predictors with p-value <= 0.5
significant_predictors_p5 = result.pvalues[result.pvalues <= 0.5].index

# Filter out threshold terms (terms with slashes like '8/9')
valid_predictors = [pred for pred in significant_predictors_p5 if "/" not in pred]

# Check if there are any significant predictors
if valid_predictors:
    # Refine the dataset to include only significant predictors
    X_refined_p5 = X_scaled_df[valid_predictors]

    # Fit the refined ordinal regression model
    model_refined_p5 = OrderedModel(y, X_refined_p5, distr="logit")
    result_refined_p5 = model_refined_p5.fit(method="bfgs")

    # Predict probabilities for each row
    predicted_probs = model_refined_p5.predict(
        result_refined_p5.params, exog=X_refined_p5
    )

    # Choose the rating category with the highest probability for each row
    predicted_ratings = (
        np.argmax(predicted_probs, axis=1) + 1
    )  # +1 to match the original rating scale

    # Add the predicted ratings to the DataFrame
    df["Predicted Rating"] = predicted_ratings

    # Bootstrapping to estimate confidence intervals
    n_bootstraps = 1000
    bootstrap_preds = np.zeros((n_bootstraps, len(df)))

    for i in range(n_bootstraps):
        try:
            # Resample the data
            print(i)
            X_resampled, y_resampled = resample(
                X_refined_p5, y, replace=True, random_state=i
            )

            # Check for constant columns in the resampled data
            if any(np.var(X_resampled, axis=0) == 0):
                continue  # Skip if resampling introduces a constant column

            # Fit the model on the resampled data
            bootstrap_model = OrderedModel(y_resampled, X_resampled, distr="logit")
            bootstrap_result = bootstrap_model.fit(method="bfgs", disp=False)

            # Predict on the entire dataset
            bootstrap_probs = bootstrap_model.predict(
                bootstrap_result.params, exog=X_refined_p5
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
    df["Lower Bound"] = lower_bounds
    df["Upper Bound"] = upper_bounds

    # Save the DataFrame with predicted ratings and confidence intervals
    df.to_csv(
        "results/ordinal_regression_predicted_ratings_with_confidence_intervals.csv",
        index=False,
    )

    # Display the DataFrame with actual and predicted ratings and confidence intervals
    print(df[["Monitor Rating", "Predicted Rating", "Lower Bound", "Upper Bound"]])
else:
    print("No predictors are significant at the 0.5 level.")
