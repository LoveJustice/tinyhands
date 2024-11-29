# common_utils.py

import os
import json
import pickle
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.inspection import permutation_importance
from typing import Dict, List, Optional, Tuple

# Import your custom prompts library
import libraries.claude_prompts as cp

DATA_COLUMNS = cp.RED_FLAGS  # Shared constant


def load_splits(timestamp: str) -> Tuple[Dict[str, pd.DataFrame], Dict]:
    """
    Load the train/holdout splits created by the data splitting script.
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
            splits[split_type] = data.copy()

    with open(f"data/splits/split_info_{timestamp}.json", "r") as f:
        split_info = json.load(f)

    return splits, split_info


def make_json_serializable(obj):
    """
    Convert objects to JSON-serializable types.
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
        return str(obj)


def save_metrics(metrics: Dict, filename: str):
    """
    Save metrics to a JSON file.
    """
    serializable_metrics = make_json_serializable(metrics)
    with open(filename, "w") as f:
        json.dump(serializable_metrics, f, indent=4)


def evaluate_model(
    model, X: pd.DataFrame, y: pd.Series, dataset_name: str = ""
) -> Dict:
    """
    Evaluate model performance and return metrics.
    """
    y_pred = model.predict(X)
    mse = float(mean_squared_error(y, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y, y_pred))

    print(f"\nModel performance on {dataset_name}:")
    print(f"MSE: {mse:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²: {r2:.4f}")

    return {
        "mse": mse,
        "rmse": rmse,
        "r2": r2,
        "predictions": y_pred.tolist(),
    }


def save_detailed_holdout_results(
    model,
    holdout_data: pd.DataFrame,
    y_holdout: pd.Series,
    predictions: np.ndarray,
    model_id: str,
    original_data: pd.DataFrame,
) -> str:
    """
    Save detailed holdout results with ID mapping.
    """
    results_df = pd.DataFrame()

    for col in DATA_COLUMNS:
        results_df[col] = holdout_data[col]

    results_df["actual_monitor_score"] = y_holdout
    results_df["predicted_score"] = predictions
    results_df["model_id"] = model_id
    results_df["IDn"] = original_data.loc[results_df.index, "IDn"]

    filename = f"results/holdout_predictions_{model_id}.csv"
    results_df.to_csv(filename, index=False)
    return filename


def analyze_and_save_feature_importance(
    importance_values: Dict[str, Dict],
    feature_names: List[str],
    timestamp: str,
    model_id: str,
    plot_top_n: Optional[int] = 20,
) -> Dict:
    """
    Analyze and save feature importance results.
    """
    analysis_dir = f"results/feature_importance_{model_id}_{timestamp}"
    os.makedirs(analysis_dir, exist_ok=True)

    importance_summary = {}

    for model_name, imp_data in importance_values.items():
        importance_df = pd.DataFrame(
            {
                "feature": feature_names,
                "importance_mean": imp_data.get(
                    "mean", imp_data.get("values")
                ).tolist(),
                "importance_std": imp_data.get(
                    "std", np.zeros_like(imp_data.get("values"))
                ).tolist(),
            }
        ).sort_values("importance_mean", ascending=True)

        importance_df.to_csv(f"{analysis_dir}/{model_name}.csv", index=False)

        # Plot all features
        plot_feature_importance(
            importance_df, model_name, analysis_dir, plot_type="all_features"
        )

        # Plot top N features
        plot_feature_importance(
            importance_df, model_name, analysis_dir, plot_type="top_n", top_n=plot_top_n
        )

        importance_summary[model_name] = {
            "features": importance_df["feature"].tolist(),
            "importance_values": importance_df["importance_mean"].tolist(),
            "std_values": importance_df["importance_std"].tolist(),
        }

    with open(f"{analysis_dir}/importance_summary.json", "w") as f:
        json.dump(importance_summary, f, indent=4)

    return importance_summary


def plot_feature_importance(
    importance_df: pd.DataFrame,
    model_name: str,
    analysis_dir: str,
    plot_type: str = "all_features",
    top_n: int = 20,
):
    """
    Helper function to plot feature importance.
    """
    if plot_type == "all_features":
        data = importance_df
        title_suffix = "All Features"
        filename_suffix = "all_features"
    elif plot_type == "top_n":
        data = importance_df.tail(top_n)
        title_suffix = f"Top {top_n} Features"
        filename_suffix = f"top_{top_n}"
    else:
        raise ValueError("Invalid plot_type. Choose 'all_features' or 'top_n'.")

    plt.figure(figsize=(12, max(8, len(data) * 0.3)))
    bars = plt.barh(
        y=range(len(data)),
        width=data["importance_mean"],
        xerr=data["importance_std"],
        capsize=5,
    )

    plt.yticks(range(len(data)), data["feature"], fontsize=8)
    plt.xlabel("Mean Importance")
    plt.title(f"Feature Importance - {title_suffix} - {model_name}")

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

    plt.grid(True, axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(
        f"{analysis_dir}/{model_name}_plot_{filename_suffix}.png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.close()
