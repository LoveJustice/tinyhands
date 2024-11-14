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
import shap
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import libraries.claude_prompts as cp

DATA_COLUMNS = cp.RED_FLAGS


def load_splits(timestamp):
    """
    Load the train/holdout splits created by the data splitting script.
    Ensures arrays are writeable for scikit-learn compatibility.
    """
    splits = {}
    for split_type in [
        "X_train",
        "X_holdout",
        "y_train",
        "y_holdout",
        "X_full",
        "y_full",
    ]:
        with open(f"data/splits/{split_type}_{timestamp}.pkl", "rb") as f:
            data = pickle.load(f)
            # Convert to numpy array and ensure it's writeable
            if isinstance(data, pd.DataFrame):
                splits[split_type] = data.copy()
            elif isinstance(data, pd.Series):
                splits[split_type] = data.copy()
            else:
                splits[split_type] = np.array(data, copy=True)

    with open(f"data/splits/split_info_{timestamp}.json", "r") as f:
        split_info = json.load(f)

    return splits, split_info


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


def find_best_hyperparameters(X_train, y_train):
    """
    Find the best hyperparameters using cross-validation on training data.
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
        cv=5,
        scoring="neg_mean_squared_error",
        n_jobs=-1,
        random_state=42,
        verbose=1,
    )

    print("Starting hyperparameter search on training data...")
    random_search.fit(X_train, y_train)

    print("\nBest parameters found:")
    for param, value in random_search.best_params_.items():
        print(f"{param}: {value}")
    print(f"\nBest cross-validation MSE: {-random_search.best_score_:.4f}")

    return random_search.best_params_


def calculate_shap_values(model, X, feature_names):
    """
    Calculate feature importance for stacking model using permutation importance
    focusing on the full pipeline only since individual components are not directly accessible.
    """
    print("Using permutation importance for feature analysis...")

    importance_values = {}

    # Calculate only for full pipeline as individual components are not separately accessible
    try:
        from sklearn.inspection import permutation_importance

        print("Calculating importance for full pipeline...")
        r = permutation_importance(
            model,
            X,
            model.predict(X),
            n_repeats=10,
            random_state=42,
            n_jobs=-1,  # Use all available cores
        )

        importance_values["full_pipeline_importance"] = {
            "values": r.importances,
            "mean": r.importances_mean,
            "std": r.importances_std,
        }
        print("Full pipeline importance calculation completed.")

    except Exception as e:
        print(f"Warning: Could not calculate importance for full pipeline: {str(e)}")

    return importance_values, X


def analyze_and_save_feature_importance(
    importance_values, feature_names, timestamp, model_id
):
    """
    Analyze and save feature importance results.
    """
    analysis_dir = f"results/feature_importance_{model_id}_{timestamp}"
    os.makedirs(analysis_dir, exist_ok=True)

    importance_summary = {}

    for model_name, imp_data in importance_values.items():
        # Create and save importance DataFrame
        importance_df = pd.DataFrame(
            {
                "feature": feature_names,
                "importance_mean": imp_data["mean"],
                "importance_std": imp_data["std"],
            }
        ).sort_values("importance_mean", ascending=False)

        # Save to CSV
        importance_df.to_csv(f"{analysis_dir}/{model_name}.csv", index=False)

        # Create and save plot - using plt directly instead of seaborn
        plt.figure(figsize=(12, 8))
        top_10 = importance_df.head(10)

        # Create bar plot
        bars = plt.barh(
            y=range(len(top_10)),
            width=top_10["importance_mean"],
            xerr=top_10["importance_std"],
            capsize=5,
        )

        # Customize plot
        plt.yticks(range(len(top_10)), top_10["feature"])
        plt.xlabel("Mean Importance")
        plt.ylabel("Feature")
        plt.title(f"Feature Importance - {model_name}")

        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(
                width,
                bar.get_y() + bar.get_height() / 2,
                f"{width:.4f}",
                ha="left",
                va="center",
                fontsize=10,
            )

        plt.tight_layout()
        plt.savefig(
            f"{analysis_dir}/{model_name}_plot.png", bbox_inches="tight", dpi=300
        )
        plt.close()

        # Store summary
        importance_summary[model_name] = {
            "top_features": importance_df.head(5)["feature"].tolist(),
            "importance_values": importance_df.head(5)["importance_mean"].tolist(),
            "std_values": importance_df.head(5)["importance_std"].tolist(),
        }

    # Save summary statistics
    with open(f"{analysis_dir}/importance_summary.json", "w") as f:
        json.dump(importance_summary, f, indent=4)

    return importance_summary


def evaluate_model(model, X, y, dataset_name=""):
    """
    Evaluate model performance and return metrics with JSON-serializable values.
    """
    y_pred = model.predict(X)
    mse = float(mean_squared_error(y, y_pred))  # Convert to float
    rmse = float(np.sqrt(mse))  # Convert to float
    r2 = float(r2_score(y, y_pred))  # Convert to float

    print(f"\nModel performance on {dataset_name}:")
    print(f"MSE: {mse:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²: {r2:.4f}")

    return {
        "mse": mse,
        "rmse": rmse,
        "r2": r2,
        "predictions": y_pred.tolist(),  # Convert to list
    }


def make_json_serializable(obj):
    """
    Convert a nested structure of NumPy arrays and other objects into JSON-serializable types.
    """
    if isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, (np.ndarray, np.generic)):
        return obj.tolist()
    elif isinstance(obj, (int, float, str, bool)):
        return obj
    elif obj is None:
        return None
    else:
        return str(obj)  # Convert any other types to string


def save_metrics(metrics, filename):
    """
    Save metrics to JSON file after ensuring all values are JSON-serializable.
    """
    serializable_metrics = make_json_serializable(metrics)

    print(f"Saving metrics as {filename}")
    with open(filename, "w") as f:
        json.dump(serializable_metrics, f, indent=4)


def save_detailed_holdout_results(
    model, holdout_data, y_holdout, predictions, model_id
):
    """
    Save detailed holdout results including all features and predictions.

    Parameters:
    -----------
    model : sklearn Pipeline
        The trained model
    holdout_data : DataFrame
        The holdout feature data
    y_holdout : Series
        The actual target values for holdout data
    predictions : array-like
        Model predictions for holdout data
    model_id : str
        Unique identifier for the model
    """
    # Create results DataFrame with all required columns
    results_df = pd.DataFrame()

    # Add IDn if it exists in holdout_data
    if "IDn" in holdout_data.columns:
        results_df["IDn"] = holdout_data["IDn"]
    elif isinstance(holdout_data.index, pd.Index):
        results_df["IDn"] = holdout_data.index

    # Add all feature columns
    for col in DATA_COLUMNS:
        results_df[col] = holdout_data[col]

    # Add actual and predicted scores
    results_df["actual_monitor_score"] = y_holdout
    results_df["predicted_score"] = predictions

    # Add model identifier
    results_df["model_id"] = model_id

    # Save to CSV
    filename = f"results/holdout_predictions_{model_id}.csv"
    results_df.to_csv(filename, index=False)
    print(f"\nSaved detailed holdout results to: {filename}")
    return filename


def main():
    """
    Main function to handle train/holdout/full dataset workflow.
    """
    # Load data splits
    splits_timestamp = "20241114_115648"  # or use input() for manual entry
    splits, split_info = load_splits(splits_timestamp)

    # Generate unique model identifier
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    model_id = f"stacking_model_{timestamp}"

    print("\n=== Training Initial Model on Training Data ===")
    # Find best hyperparameters using training data only
    best_params = find_best_hyperparameters(splits["X_train"], splits["y_train"])

    # Train model on training data
    initial_model = create_simple_pipeline()
    for param, value in best_params.items():
        param_path = param.split("__")
        current = initial_model.named_steps["regressor"]
        for path_part in param_path[1:-1]:
            if path_part in ["gb", "rf"]:
                current = dict(current.estimators)[path_part]
            elif path_part == "final_estimator":
                current = current.final_estimator
        setattr(current, param_path[-1], value)

    initial_model.fit(splits["X_train"], splits["y_train"])

    print("\n=== Evaluating on Holdout Set ===")
    # Evaluate on holdout set
    holdout_metrics = evaluate_model(
        initial_model, splits["X_holdout"], splits["y_holdout"], "holdout set"
    )

    # Save detailed holdout results
    holdout_predictions = initial_model.predict(splits["X_holdout"])
    holdout_file = save_detailed_holdout_results(
        initial_model,
        splits["X_holdout"],
        splits["y_holdout"],
        holdout_predictions,
        model_id,
    )
    print(f"\nDetailed holdout results saved to: {holdout_file}")

    # Calculate feature importance for holdout evaluation
    print("\nCalculating feature importance for holdout set...")
    holdout_importance, X_holdout_transformed = calculate_shap_values(
        initial_model, splits["X_holdout"], DATA_COLUMNS
    )

    holdout_importance_summary = analyze_and_save_feature_importance(
        holdout_importance, DATA_COLUMNS, timestamp, f"{model_id}_holdout"
    )

    print("\n=== Training Final Model on Full Dataset ===")
    # Train final model on full dataset
    final_model = create_simple_pipeline()
    for param, value in best_params.items():
        param_path = param.split("__")
        current = final_model.named_steps["regressor"]
        for path_part in param_path[1:-1]:
            if path_part in ["gb", "rf"]:
                current = dict(current.estimators)[path_part]
            elif path_part == "final_estimator":
                current = current.final_estimator
        setattr(current, param_path[-1], value)

    final_model.fit(splits["X_full"], splits["y_full"])

    # Calculate feature importance for final model
    print("\nCalculating feature importance for final model...")
    final_importance, X_final_transformed = calculate_shap_values(
        final_model, splits["X_full"], DATA_COLUMNS
    )

    final_importance_summary = analyze_and_save_feature_importance(
        final_importance, DATA_COLUMNS, timestamp, f"{model_id}_final"
    )

    # Save final model
    model_filename = f"models/final_{model_id}.pkl"
    print(f"\nSaving final model as {model_filename}")
    with open(model_filename, "wb") as f:
        pickle.dump(final_model, f)

    # Save all metrics and information
    metrics = {
        "model_id": model_id,
        "timestamp": timestamp,
        "holdout_metrics": holdout_metrics,
        "split_info": split_info,
        "best_parameters": best_params,
        "holdout_importance_summary": holdout_importance_summary,
        "final_importance_summary": final_importance_summary,
    }

    metrics_filename = f"results/metrics_{model_id}.json"
    save_metrics(metrics, metrics_filename)


if __name__ == "__main__":
    main()
