import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from lightgbm import LGBMRegressor
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import RFE
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import uniform, randint
import libraries.model_tools as mt

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
    model_data = model_data.replace(mapping)
    for col in DATA_COLUMNS:
        model_data[col] = pd.to_numeric(model_data[col], errors="coerce")
        model_data = model_data.dropna(subset=[col])
        model_data[col] = model_data[col].astype(int)

    return model_data, model_data["monitor_score"]


def create_lightgbm_pipeline():
    """
    Create a model pipeline with LightGBM regressor.
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
            ("regressor", LGBMRegressor(random_state=42)),
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
    Tune the hyperparameters of the LightGBM model pipeline.
    """
    param_distributions = {
        "regressor__n_estimators": randint(100, 500),
        "regressor__learning_rate": uniform(0.01, 0.3),
        "regressor__max_depth": randint(3, 10),
        "regressor__num_leaves": randint(20, 50),
        "regressor__min_child_samples": randint(5, 30),
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


def main():
    file_path = "results/advert_flags.csv"
    advert_flags, y = load_and_preprocess_data(file_path)
    X = advert_flags[DATA_COLUMNS]

    lightgbm_pipeline = create_lightgbm_pipeline()

    # Hyperparameter tuning
    best_lightgbm_pipeline = tune_hyperparameters(lightgbm_pipeline, X, y)

    # Train and evaluate model
    trained_pipeline, X_test, y_test = train_and_evaluate_model(
        X, y, best_lightgbm_pipeline
    )

    # Save the trained model
    unique_model_filename = mt.generate_unique_filename(prefix="redflag_model")
    mt.save_model(trained_pipeline, unique_model_filename)

    # Make predictions on the entire dataset
    advert_flags["model_predictions"] = trained_pipeline.predict(
        advert_flags[DATA_COLUMNS]
    )

    # Save the results
    results = pd.DataFrame(
        {
            "IDn": advert_flags.index,
            "monitor_score": advert_flags["monitor_score"],
            "model_predictions": advert_flags["model_predictions"],
        }
    )
    unique_results_filename = mt.generate_unique_filename(
        prefix="redflag_model_result", extension="csv"
    )
    results.to_csv(f"results/{unique_results_filename}", index=False)
    print(f"Results saved as {unique_results_filename}")


if __name__ == "__main__":
    main()
