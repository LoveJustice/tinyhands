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
    Ensures arrays are writeable and maintains DataFrame structure.
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
            print(f"\nDEBUG: Loading {split_type}")
            if isinstance(data, pd.DataFrame):
                print(f"Shape: {data.shape}")
                print(f"Columns: {data.columns.tolist()}")
                splits[split_type] = data.copy()
            elif isinstance(data, pd.Series):
                print(f"Length: {len(data)}")
                splits[split_type] = data.copy()
            else:
                print(f"Type: {type(data)}")
                splits[split_type] = pd.DataFrame(data, columns=DATA_COLUMNS)

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
    Analyze and save feature importance results for all features.
    """
    analysis_dir = f"results/feature_importance_{model_id}_{timestamp}"
    os.makedirs(analysis_dir, exist_ok=True)

    importance_summary = {}

    for model_name, imp_data in importance_values.items():
        # Create and save importance DataFrame with all features
        importance_df = pd.DataFrame(
            {
                "feature": feature_names,
                "importance_mean": imp_data["mean"],
                "importance_std": imp_data["std"],
            }
        ).sort_values(
            "importance_mean", ascending=True
        )  # Ascending for better bottom-to-top visualization

        # Save complete results to CSV
        importance_df.to_csv(f"{analysis_dir}/{model_name}.csv", index=False)

        # Create and save plot with all features
        plt.figure(
            figsize=(12, max(8, len(feature_names) * 0.3))
        )  # Dynamic figure size based on feature count

        # Create bar plot for all features
        bars = plt.barh(
            y=range(len(importance_df)),
            width=importance_df["importance_mean"],
            xerr=importance_df["importance_std"],
            capsize=5,
        )

        # Customize plot
        plt.yticks(range(len(importance_df)), importance_df["feature"], fontsize=8)
        plt.xlabel("Mean Importance")
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
                fontsize=8,
            )

        # Add grid for better readability
        plt.grid(True, axis="x", linestyle="--", alpha=0.7)

        plt.tight_layout()
        plt.savefig(
            f"{analysis_dir}/{model_name}_plot_all_features.png",
            bbox_inches="tight",
            dpi=300,
        )
        plt.close()

        # Create a separate plot for top 20 features
        plt.figure(figsize=(12, 10))
        top_20 = importance_df.tail(20)  # Get top 20 since we sorted ascending

        bars = plt.barh(
            y=range(len(top_20)),
            width=top_20["importance_mean"],
            xerr=top_20["importance_std"],
            capsize=5,
        )

        plt.yticks(range(len(top_20)), top_20["feature"])
        plt.xlabel("Mean Importance")
        plt.title(f"Top 20 Most Important Features - {model_name}")

        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(
                width,
                bar.get_y() + bar.get_height() / 2,
                f"{width:.4f}",
                ha="left",
                va="center",
            )

        plt.grid(True, axis="x", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(
            f"{analysis_dir}/{model_name}_plot_top_20.png", bbox_inches="tight", dpi=300
        )
        plt.close()

        # Store complete summary
        importance_summary[model_name] = {
            "features": importance_df["feature"].tolist(),
            "importance_values": importance_df["importance_mean"].tolist(),
            "std_values": importance_df["importance_std"].tolist(),
            "top_20_features": importance_df.tail(20)["feature"].tolist(),
            "top_20_values": importance_df.tail(20)["importance_mean"].tolist(),
        }

        # Save detailed feature ranking
        ranking_df = importance_df.reset_index(drop=True)
        ranking_df.index = ranking_df.index + 1  # Start ranking from 1
        ranking_df.to_csv(f"{analysis_dir}/{model_name}_feature_ranking.csv")

        # Save text summary
        with open(f"{analysis_dir}/{model_name}_feature_ranking.txt", "w") as f:
            f.write(f"Feature Importance Ranking for {model_name}\n")
            f.write("=" * 50 + "\n\n")
            for idx, row in ranking_df.iterrows():
                f.write(
                    f"{idx}. {row['feature']}: {row['importance_mean']:.4f} ± {row['importance_std']:.4f}\n"
                )

    # Save complete summary statistics
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
    model, holdout_data, y_holdout, predictions, model_id, original_data
):
    """
    Save detailed holdout results with correct ID mapping.

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
    original_data : DataFrame
        The original dataset containing the true IDn column
    """
    print("\nDEBUG: Data shapes before processing:")
    print(f"Holdout data shape: {holdout_data.shape}")
    print(f"Original data shape: {original_data.shape}")

    # Create results DataFrame from holdout data
    results_df = holdout_data.copy()

    # Debug current state
    print("\nDEBUG: Holdout data index sample:")
    print(holdout_data.index[:5])

    # Add feature columns
    results_df = pd.DataFrame()
    for col in DATA_COLUMNS:
        results_df[col] = holdout_data[col]

    # Add predictions and actual values
    results_df["actual_monitor_score"] = y_holdout
    results_df["predicted_score"] = predictions
    results_df["model_id"] = model_id

    # Add original IDn by using the same index
    # First verify that indices match between holdout_data and original_data
    common_indices = set(holdout_data.index).intersection(set(original_data.index))
    if len(common_indices) != len(holdout_data):
        print("\nWARNING: Not all holdout indices found in original data!")
        print(f"Expected {len(holdout_data)} matches, found {len(common_indices)}")

    # Get IDn for our holdout samples
    results_df["IDn"] = original_data.loc[results_df.index, "IDn"]

    print("\nDEBUG: Final results DataFrame info:")
    print(results_df.info())
    print("\nDEBUG: Sample of final results:")
    print(results_df.head())
    print("\nDEBUG: IDn sample in final results:")
    print(results_df["IDn"].head())

    # Verify no missing values
    null_counts = results_df.isnull().sum()
    if null_counts.any():
        print("\nWARNING: Found null values:")
        print(null_counts[null_counts > 0])

    # Save to CSV
    filename = f"results/holdout_predictions_{model_id}.csv"
    results_df.to_csv(filename, index=False)
    print(f"\nSaved detailed holdout results to: {filename}")
    return filename


def load_and_preprocess_data(file_path):
    """
    Load and preprocess the dataset while maintaining proper ID handling.
    """
    model_data = pd.read_csv(file_path)

    # Store original IDn before any processing
    original_idn = model_data["IDn"].copy()

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

    # Ensure IDn is preserved as a column, not an index
    model_data["IDn"] = original_idn[model_data.index]

    return model_data


def main():
    """
    Main function with corrected ID handling.
    """
    # Load original data with proper ID handling
    file_path = "results/advert_flags.csv"
    print("Loading original data...")
    original_data = pd.read_csv(file_path)

    # Ensure original_data has IDn as a column
    if "IDn" not in original_data.columns:
        raise ValueError("Original data must contain 'IDn' column")

    # Load splits
    splits_timestamp = "20241114_115648"
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

    holdout_predictions = initial_model.predict(splits["X_holdout"])
    holdout_file = save_detailed_holdout_results(
        initial_model,
        splits["X_holdout"],
        splits["y_holdout"],
        holdout_predictions,
        model_id,
        original_data,
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
