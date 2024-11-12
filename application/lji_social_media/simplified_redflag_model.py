import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor,
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import uniform, randint
import datetime
import uuid
import pickle
import libraries.claude_prompts as cp

import datetime
import uuid


DATA_COLUMNS = cp.RED_FLAGS


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


def create_simple_pipeline():
    """
    Create a simplified model pipeline with basic preprocessing and stacking.
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
                        )
                    ]
                ),
            ),
            (
                "regressor",
                StackingRegressor(
                    estimators=[
                        ("gb", GradientBoostingRegressor(random_state=42)),
                        ("rf", RandomForestRegressor(random_state=42)),
                    ],
                    final_estimator=GradientBoostingRegressor(random_state=42),
                ),
            ),
        ]
    )


def find_best_hyperparameters(X, y):
    """
    Find the best hyperparameters using cross-validation on the entire dataset.
    """
    pipeline = create_simple_pipeline()

    param_distributions = {
        "regressor__gb__n_estimators": randint(100, 500),
        "regressor__gb__learning_rate": uniform(0.01, 0.3),
        "regressor__gb__max_depth": randint(3, 10),
        "regressor__rf__n_estimators": randint(100, 500),
        "regressor__rf__max_depth": randint(3, 10),
        "regressor__final_estimator__n_estimators": randint(100, 300),
        "regressor__final_estimator__learning_rate": uniform(0.01, 0.2),
    }

    random_search = RandomizedSearchCV(
        pipeline,
        param_distributions=param_distributions,
        n_iter=100,
        cv=5,  # 5-fold cross-validation
        scoring="neg_mean_squared_error",
        n_jobs=-1,
        random_state=42,
        verbose=1,
    )

    print("Starting hyperparameter search...")
    random_search.fit(X, y)

    print("\nBest parameters found:")
    for param, value in random_search.best_params_.items():
        print(f"{param}: {value}")
    print(f"\nBest cross-validation MSE: {-random_search.best_score_:.4f}")

    return random_search.best_params_


def train_final_model(X, y, best_params):
    """
    Train the final model on the entire dataset using the best hyperparameters.
    """
    print("\nTraining final model on entire dataset...")

    # Create a new pipeline with the best parameters
    final_pipeline = create_simple_pipeline()

    # Set the best parameters
    for param, value in best_params.items():
        param_path = param.split("__")
        current = final_pipeline.named_steps["regressor"]
        for path_part in param_path[1:-1]:
            if path_part in ["gb", "rf"]:
                current = dict(current.estimators)[path_part]
            elif path_part == "final_estimator":
                current = current.final_estimator
        setattr(current, param_path[-1], value)

    # Fit the model on the entire dataset
    final_pipeline.fit(X, y)

    # Calculate in-sample performance metrics
    y_pred = final_pipeline.predict(X)
    mse = mean_squared_error(y, y_pred)
    r2 = r2_score(y, y_pred)

    print(f"\nFinal model performance on full dataset:")
    print(f"MSE: {mse:.4f}")
    print(f"R²: {r2:.4f}")

    return final_pipeline


def main():
    """
    Main function to run the optimized pipeline.
    """
    file_path = "results/advert_flags.csv"
    print("Loading and preprocessing data...")
    advert_flags, y = load_and_preprocess_data(file_path)
    X = advert_flags[DATA_COLUMNS]

    # Find best hyperparameters using cross-validation
    best_params = find_best_hyperparameters(X, y)

    # Train final model on entire dataset using best parameters
    final_model = train_final_model(X, y, best_params)

    # Generate predictions for all data
    print("\nGenerating predictions...")
    advert_flags["model_predictions"] = final_model.predict(
        advert_flags[DATA_COLUMNS].replace({"yes": 1, "no": 0})
    )

    # Create results DataFrame
    results = pd.DataFrame(
        {
            "advert": advert_flags["advert"],
            "group_id": advert_flags["group_id"],
            "IDn": advert_flags["IDn"],
            "monitor_score": advert_flags["monitor_score"],
            "model_predictions": advert_flags["model_predictions"],
        }
    )

    # Save model and results with unique identifiers
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]

    # Save model
    model_filename = f"models/simplified_redflag_model_{timestamp}_{unique_id}.pkl"
    print(f"\nSaving model as {model_filename}")
    with open(model_filename, "wb") as f:
        pickle.dump(final_model, f)

    # Save results
    results_filename = (
        f"results/simplified_redflag_model_results_{timestamp}_{unique_id}.csv"
    )
    print(f"Saving results as {results_filename}")
    results.to_csv(results_filename, index=False)


if __name__ == "__main__":
    main()
