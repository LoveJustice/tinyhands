import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor,
)
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import RFE
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import spearmanr, uniform, randint
import joblib
import datetime
import uuid

# Data columns
DATA_COLUMNS = [
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


def load_and_preprocess_data(file_path):
    """
    Load and preprocess the dataset from the provided file path.
    """
    model_data = pd.read_csv(file_path)
    model_data = model_data[
        (model_data["monitor_score"] != "unknown")
        & (~model_data["monitor_score"].isna())
    ]
    mapping = {"yes": 1, "no": 0}
    df = model_data.replace(mapping)
    return df[DATA_COLUMNS], df["monitor_score"]


def create_model_pipeline():
    """
    Create a simple model pipeline with polynomial features and gradient boosting regressor.
    """
    return Pipeline(
        [
            (
                "features",
                ColumnTransformer(
                    [
                        ("num", SimpleImputer(strategy="mean"), DATA_COLUMNS),
                        (
                            "poly",
                            PolynomialFeatures(degree=2, include_bias=False),
                            DATA_COLUMNS,
                        ),
                    ]
                ),
            ),
            ("regressor", GradientBoostingRegressor(random_state=42)),
        ]
    )


def train_and_evaluate_model(X, y, pipeline):
    """
    Train the model and evaluate it on train and test data.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline.fit(X_train, y_train)

    y_pred_train = pipeline.predict(X_train)
    y_pred_test = pipeline.predict(X_test)

    train_mse = mean_squared_error(y_train, y_pred_train)
    test_mse = mean_squared_error(y_test, y_pred_test)
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)

    print(f"Train MSE: {train_mse:.4f}, Test MSE: {test_mse:.4f}")
    print(f"Train R2: {train_r2:.4f}, Test R2: {test_r2:.4f}")

    return pipeline, X_test, y_test


def tune_hyperparameters(pipeline, X, y):
    """
    Tune the hyperparameters of the model pipeline.
    """
    param_distributions = {
        "regressor__gb__n_estimators": randint(100, 500),
        "regressor__gb__learning_rate": uniform(0.01, 0.3),
        "regressor__gb__max_depth": randint(3, 10),
        "regressor__gb__min_samples_split": randint(2, 20),
        "regressor__gb__min_samples_leaf": randint(1, 10),
    }

    random_search = RandomizedSearchCV(
        pipeline,
        param_distributions=param_distributions,
        n_iter=100,
        cv=5,
        scoring="neg_mean_squared_error",
        n_jobs=-1,
        random_state=42,
    )
    random_search.fit(X, y)

    print("Best parameters:", random_search.best_params_)
    print("Best cross-validation score:", -random_search.best_score_)

    return random_search.best_estimator_


def create_advanced_pipeline():
    """
    Create an advanced model pipeline with stacking and feature selection.
    """
    return Pipeline(
        [
            (
                "features",
                ColumnTransformer(
                    [
                        (
                            "num",
                            Pipeline(
                                [
                                    ("imputer", SimpleImputer(strategy="mean")),
                                    ("scaler", StandardScaler()),
                                ]
                            ),
                            DATA_COLUMNS,
                        ),
                        (
                            "poly",
                            PolynomialFeatures(degree=2, include_bias=False),
                            DATA_COLUMNS,
                        ),
                    ]
                ),
            ),
            (
                "feature_selection",
                RFE(estimator=SVR(kernel="linear"), n_features_to_select=10),
            ),
            (
                "regressor",
                StackingRegressor(
                    estimators=[
                        ("gb", GradientBoostingRegressor(random_state=42)),
                        ("rf", RandomForestRegressor(random_state=42)),
                    ],
                    final_estimator=SVR(),
                ),
            ),
        ]
    )


def generate_unique_filename(prefix="model", extension="pkl"):
    """
    Generate a unique filename using a prefix and extension.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    random_string = uuid.uuid4().hex[:6]
    filename = f"{prefix}_{timestamp}_{random_string}.{extension}"
    return filename


def save_model(model, filename):
    """
    Save the trained model to disk.
    """
    joblib.dump(model, filename)
    print(f"Model saved as {filename}")


def main():
    file_path = "results/advert_flags.csv"
    all_advert_flags = pd.read_csv(file_path)
    advert_flags = all_advert_flags[
        ~(
            (all_advert_flags["monitor_score"] == "unknown")
            | all_advert_flags["monitor_score"].isnull()
        )
    ]

    # Create the results DataFrame
    results = pd.DataFrame(
        columns=["advert", "group_id", "post_id", "monitor_score", "test_train"],
        index=advert_flags.index,
    )

    X, y = load_and_preprocess_data(file_path)
    advanced_pipeline = create_advanced_pipeline()

    # Hyperparameter tuning
    best_advanced_pipeline = tune_hyperparameters(advanced_pipeline, X, y)

    # Train and evaluate model
    trained_pipeline, X_test, y_test = train_and_evaluate_model(
        X, y, best_advanced_pipeline
    )

    # Save the trained model
    unique_model_filename = generate_unique_filename(prefix="redflag_model")
    save_model(trained_pipeline, unique_model_filename)

    # Make predictions on the entire dataset
    all_advert_flags["model_predictions"] = trained_pipeline.predict(
        all_advert_flags[DATA_COLUMNS].replace({"yes": 1, "no": 0})
    )

    # Populate the results DataFrame
    results["advert"] = advert_flags["advert"]
    results["group_id"] = advert_flags["group_id"]
    results["post_id"] = advert_flags["post_id"]
    results["monitor_score"] = advert_flags["monitor_score"]
    results["test_train"] = "train"
    results.loc[results.index.isin(X_test.index), "test_train"] = "test"
    results = (
        results.set_index("post_id").loc[all_advert_flags["post_id"]].reset_index()
    )
    results["model_predictions"] = all_advert_flags["model_predictions"]
    all_advert_flags.to_csv("results/all_advert_flags.csv", index=False)
    # Save the results
    unique_results_filename = generate_unique_filename(
        prefix="redflag_model_result", extension="csv"
    )
    results.to_csv(f"results/{unique_results_filename}", index=False)
    print(f"Results saved as {unique_results_filename}")


if __name__ == "__main__":
    main()
