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
    Calculate SHAP values for the model using both base estimators and final estimator.
    """
    shap_values = {}

    # Get the transformed feature data
    X_transformed = model.named_steps["features"].transform(X)

    # Calculate SHAP values for base estimators
    base_models = dict(model.named_steps["regressor"].estimators)
    for name, estimator in base_models.items():
        explainer = shap.TreeExplainer(estimator)
        shap_values[f"{name}_shap"] = {
            "values": explainer.shap_values(X_transformed),
            "explainer": explainer,
            "expected_value": explainer.expected_value,
        }

    # Calculate SHAP values for final estimator
    final_estimator = model.named_steps["regressor"].final_estimator
    final_explainer = shap.TreeExplainer(final_estimator)
    shap_values["final_estimator_shap"] = {
        "values": final_explainer.shap_values(X_transformed),
        "explainer": final_explainer,
        "expected_value": final_explainer.expected_value,
    }

    return shap_values, X_transformed


def analyze_and_save_shap_results(
    shap_values, X_transformed, feature_names, timestamp, model_id
):
    """
    Analyze SHAP values and save various visualizations and analyses.
    """
    # Create directory for SHAP analysis
    analysis_dir = f"results/shap_analysis_{model_id}_{timestamp}"
    os.makedirs(analysis_dir, exist_ok=True)

    shap_summary = {}

    for model_name, shap_data in shap_values.items():
        # Calculate mean absolute SHAP values for feature importance ranking
        mean_abs_shap = np.abs(shap_data["values"]).mean(axis=0)
        feature_importance = pd.DataFrame(
            {"feature": feature_names, "mean_abs_shap": mean_abs_shap}
        ).sort_values("mean_abs_shap", ascending=False)

        # Save feature importance rankings
        feature_importance.to_csv(
            f"{analysis_dir}/{model_name}_feature_importance.csv", index=False
        )

        # Generate and save SHAP summary plot
        plt.figure(figsize=(12, 8))
        shap.summary_plot(
            shap_data["values"], X_transformed, feature_names=feature_names, show=False
        )
        plt.tight_layout()
        plt.savefig(f"{analysis_dir}/{model_name}_summary_plot.png")
        plt.close()

        # Generate and save SHAP dependence plots for top features
        top_features = feature_importance.head(5)["feature"].tolist()
        for feature_idx, feature in enumerate(top_features):
            plt.figure(figsize=(10, 6))
            shap.dependence_plot(
                feature_idx,
                shap_data["values"],
                X_transformed,
                feature_names=feature_names,
                show=False,
            )
            plt.tight_layout()
            plt.savefig(f"{analysis_dir}/{model_name}_{feature}_dependence_plot.png")
            plt.close()

        # Store summary statistics
        shap_summary[model_name] = {
            "top_features": top_features,
            "mean_abs_shap": mean_abs_shap.tolist(),
            "expected_value": float(shap_data["expected_value"]),
        }

    # Save summary statistics
    with open(f"{analysis_dir}/shap_summary.json", "w") as f:
        json.dump(shap_summary, f, indent=4)

    return shap_summary


def evaluate_model(model, X, y, dataset_name=""):
    """
    Evaluate model performance and return metrics.
    """
    y_pred = model.predict(X)
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y, y_pred)

    print(f"\nModel performance on {dataset_name}:")
    print(f"MSE: {mse:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²: {r2:.4f}")

    return {"mse": mse, "rmse": rmse, "r2": r2, "predictions": y_pred}


def save_detailed_holdout_results(
    model, holdout_data, full_data, predictions, model_id
):
    """
    Save detailed holdout results including all features and predictions.
    """
    # Create results DataFrame with all required columns
    results_df = pd.DataFrame()
    results_df["IDn"] = holdout_data.index  # Assuming IDn is the index

    # Add all feature columns
    for col in DATA_COLUMNS:
        results_df[col] = holdout_data[col]

    # Add actual and predicted scores
    results_df["actual_monitor_score"] = full_data.loc[
        holdout_data.index, "monitor_score"
    ]
    results_df["predicted_score"] = predictions

    # Add model identifier
    results_df["model_id"] = model_id

    # Save to CSV
    filename = f"results/holdout_predictions_{model_id}.csv"
    results_df.to_csv(filename, index=False)
    return filename


def main():
    """
    Main function to handle train/holdout/full dataset workflow.
    """
    # Load data splits
    # splits_timestamp = input("Enter the timestamp of the data splits to use: ")
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

    # Save detailed holdout results
    holdout_predictions = initial_model.predict(splits["X_holdout"])
    holdout_file = save_detailed_holdout_results(
        initial_model,
        splits["X_holdout"],
        splits["X_full"],  # Full dataset for reference
        holdout_predictions,
        model_id,
    )
    print(f"\nDetailed holdout results saved to: {holdout_file}")

    # Calculate and save SHAP values for holdout evaluation
    print("\nCalculating SHAP values for holdout set...")
    holdout_shap_values, X_holdout_transformed = calculate_shap_values(
        initial_model, splits["X_holdout"], DATA_COLUMNS
    )

    holdout_shap_summary = analyze_and_save_shap_results(
        holdout_shap_values,
        X_holdout_transformed,
        DATA_COLUMNS,
        timestamp,
        f"{model_id}_holdout",
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

    # Calculate and save SHAP values for final model
    print("\nCalculating SHAP values for final model...")
    final_shap_values, X_final_transformed = calculate_shap_values(
        final_model, splits["X_full"], DATA_COLUMNS
    )

    final_shap_summary = analyze_and_save_shap_results(
        final_shap_values,
        X_final_transformed,
        DATA_COLUMNS,
        timestamp,
        f"{model_id}_final",
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
        "holdout_shap_summary": holdout_shap_summary,
        "final_shap_summary": final_shap_summary,
    }

    metrics_filename = f"results/metrics_{model_id}.json"
    print(f"Saving metrics as {metrics_filename}")
    with open(metrics_filename, "w") as f:
        json.dump(metrics, f, indent=4)


if __name__ == "__main__":
    main()
