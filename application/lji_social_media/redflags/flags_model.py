import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV, cross_val_score
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split

from sklearn.pipeline import Pipeline


# Load the dataset
file_path = "..results/advert_flags.csv"
advert_flags = pd.read_csv(file_path)
list(advert_flags)

advert_100_comparison_with_regressor_predictions = pd.read_csv(
    "../results/advert_100_comparison_with_regressor_predictions.csv"
)
list(advert_100_comparison_with_regressor_predictions)

model_data = advert_flags.merge(
    advert_100_comparison_with_regressor_predictions[["IDn", "monitor_score"]],
    left_on="id",
    right_on="IDn",
)
model_data = model_data.drop(columns=["IDn"])

list(model_data)
data_columns = [
    "assure_prompt",
    "bypass_prompt",
    "callback_request_prompt",
    "false_organization_prompt",
    "gender_specific_prompt",
    "illegal_activities_prompt",
    "immediate_hiring_prompt",
    "language_switch_prompt",
    "multiple_provinces_prompt",
    "no_education_skilled_prompt",
    "no_location_prompt",
    "quick_money_prompt",
    "recruit_students_prompt",
    "suspicious_email_prompt",
    "target_specific_group_prompt",
    "unprofessional_writing_prompt",
    "unrealistic_hiring_number_prompt",
    "unusual_hours_prompt",
    "vague_description_prompt",
    "wrong_link_prompt",
]

mapping = {"yes": 1, "no": 0}

# Apply the mapping to all columns
df = model_data.replace(mapping)
df.loc[df.id == 572651, "monitor_score"] = 1
X = df[data_columns]
y = df["monitor_score"]


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
X_test[[]].copy()

pd.DataFrame(pipeline.predict(X_test), columns=["modelB_predict"], index=X_test.index)

df = (
    advert_100_comparison_with_regressor_predictions[
        ["Model Values", "IDn", "monitor_score"]
    ]
    .merge(X_test, left_index=True, right_index=True)
    .merge(
        pd.DataFrame(
            pipeline.predict(X_test), columns=["modelB_predict"], index=X_test.index
        ),
        left_index=True,
        right_index=True,
    )
    .rename(columns={"Model Values": "modelA_predict"})
    .loc[:, ["monitor_score", "modelA_predict", "modelB_predict"]]
)

df["modelA_predict"].corr(df["monitor_score"])
df["modelB_predict"].corr(df["monitor_score"])
df["modelB_predict"].corr(df["monitor_score"], method="spearman")
df["modelA_predict"].corr(df["monitor_score"], method="spearman")


df = (
    advert_100_comparison_with_regressor_predictions[
        ["Model Values", "IDn", "monitor_score"]
    ]
    .merge(X_train, left_index=True, right_index=True)
    .merge(
        pd.DataFrame(
            pipeline.predict(X_train), columns=["modelB_predict"], index=X_train.index
        ),
        left_index=True,
        right_index=True,
    )
    .rename(columns={"Model Values": "modelA_predict"})
    .loc[:, ["monitor_score", "modelA_predict", "modelB_predict"]]
)
