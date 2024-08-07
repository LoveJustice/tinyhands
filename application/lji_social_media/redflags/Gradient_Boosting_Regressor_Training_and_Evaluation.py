import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV, cross_val_score
import numpy as np
from sklearn.preprocessing import PolynomialFeatures

# Load the dataset
file_path = "results/advert_comparison_cleaned.csv"
df = pd.read_csv(file_path)

# Define the independent and dependent variables
X = df[
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
y = df["Monitor Rating"]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train the Gradient Boosting Regressor
gb_model = GradientBoostingRegressor(random_state=42)
gb_model.fit(X_train, y_train)

# Make predictions
y_pred_gb = gb_model.predict(X_test)

# Calculate the correlation
correlation_gb = np.corrcoef(y_test, y_pred_gb)[0, 1]
print("Correlation for Gradient Boosting Regressor:", correlation_gb)

# Hyperparameter Tuning
param_grid_gb = {
    "n_estimators": [100, 200, 300],
    "learning_rate": [0.01, 0.1, 0.2],
    "max_depth": [3, 4, 5],
}
grid_search_gb = GridSearchCV(
    estimator=gb_model,
    param_grid=param_grid_gb,
    cv=5,
    scoring="neg_mean_squared_error",
    n_jobs=-1,
)
grid_search_gb.fit(X_train, y_train)

# Best parameters and score
best_params_gb = grid_search_gb.best_params_
best_score_gb = grid_search_gb.best_score_
print("Best parameters for Gradient Boosting Regressor:", best_params_gb)
print("Best cross-validation score:", best_score_gb)

# Train the best model
best_gb_model = GradientBoostingRegressor(**best_params_gb, random_state=42)
best_gb_model.fit(X_train, y_train)

# Make predictions with the best model
y_pred_best_gb = best_gb_model.predict(X_test)

# Calculate the correlation
correlation_best_gb = np.corrcoef(y_test, y_pred_best_gb)[0, 1]
print("Correlation for best Gradient Boosting Regressor:", correlation_best_gb)

# Cross-Validation
cross_val_scores_gb = cross_val_score(
    best_gb_model, X, y, cv=5, scoring="neg_mean_squared_error"
)
mean_cross_val_score_gb = np.mean(cross_val_scores_gb)
print(
    "Mean cross-validation score for best Gradient Boosting Regressor:",
    mean_cross_val_score_gb,
)

# Feature Engineering
poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
X_poly = poly.fit_transform(X)
X_train_poly, X_test_poly, y_train, y_test = train_test_split(
    X_poly, y, test_size=0.2, random_state=42
)
gb_model.fit(X_train_poly, y_train)
y_pred_poly_gb = gb_model.predict(X_test_poly)
correlation_poly_gb = np.corrcoef(y_test, y_pred_poly_gb)[0, 1]
print(
    "Correlation for Gradient Boosting Regressor with polynomial features:",
    correlation_poly_gb,
)


# Example of a single input (values must follow the structure of the training data)
single_input = np.array(
    [
        [
            0,  # "Recruiting young people who are still in school"
            0,  # "Paying more than the market rate for the skill level or type of job that they are hiring for"
            0,  # "Not mentioning any skill requirements"
            0,  # "Not mentioning the nature of the job"
            0,  # "Not mentioning the name or the location of the hiring business"
            0,  # "Paying the same salary for different job posts / positions"
            0,  # "Hiring for an organization (such as ESKOM) who has publicly stated that they don't advertise job posts on social media"
            0,  # "Recruiting specifically females for a job that male or female applicants would qualify for"
            0,  # "Unprofessional writing (poor grammar / spelling)"
            0,  # "Recruiting models"
            0,  # "Changing from English to other languages in the middle of the post"
            0,  # "Using a suspicious email address"
            0,  # "Advertising for positions in several promises (especially without detail)"
            1,  # "Looks Legit"
        ]
    ]
)

# Ensure the single input has the same structure as the training data
# Transform the input using the same preprocessing steps
single_input_transformed = poly.transform(single_input)

# Make a prediction using the trained model
prediction = best_gb_model.predict(single_input_transformed)

print("Prediction for the single input:", prediction)

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
import numpy as np

# Load the dataset
file_path = "../results/advert_comparison_cleaned.csv"
df = pd.read_csv(file_path)

# Define the independent and dependent variables
X = df[
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
y = df["Monitor Rating"]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create a pipeline with polynomial features and Gradient Boosting Regressor
pipeline = Pipeline(
    [
        ("poly_features", PolynomialFeatures(degree=2, include_bias=False)),
        ("regressor", GradientBoostingRegressor(random_state=42)),
    ]
)

# Train the model
pipeline.fit(X_train, y_train)

# Example of a single input (values must follow the structure of the training data)
single_input = np.array(
    [
        [
            1,  # "Recruiting young people who are still in school"
            1,  # "Paying more than the market rate for the skill level or type of job that they are hiring for"
            1,  # "Not mentioning any skill requirements"
            0,  # "Not mentioning the nature of the job"
            0,  # "Not mentioning the name or the location of the hiring business"
            0,  # "Paying the same salary for different job posts / positions"
            1,  # "Hiring for an organization (such as ESKOM) who has publicly stated that they don't advertise job posts on social media"
            0,  # "Recruiting specifically females for a job that male or female applicants would qualify for"
            0,  # "Unprofessional writing (poor grammar / spelling)"
            1,  # "Recruiting models"
            0,  # "Changing from English to other languages in the middle of the post"
            1,  # "Using a suspicious email address"
            1,  # "Advertising for positions in several promises (especially without detail)"
            0,  # "Looks Legit"
        ]
    ]
)

# Transform the single input to match the training data
single_input_transformed = pipeline.named_steps["poly_features"].transform(single_input)

# Make a prediction using the pipeline
prediction = pipeline.named_steps["regressor"].predict(single_input_transformed)

print("Prediction for the single input:", prediction)

df["Model Values"] = pipeline.predict(X)
df.to_csv("results/advert_comparison_with_regressor_predictions.csv", index=False)


file_path = "../results/adverts_za_sample_scored.csv"
df = pd.read_csv(file_path)

# Define the independent and dependent variables
X = df[
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
df.to_csv("results/advert_100_comparison_with_regressor_predictions.csv", index=False)
