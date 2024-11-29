import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import json


def load_latest_results():
    """Load the most recent results for each model"""
    # Get latest files for each model
    original = sorted(glob.glob("results/metrics_advanced_redflag_model_*.json"))[-1]
    simplified = sorted(glob.glob("results/metrics_stacking_model_*.json"))[-1]
    deep_learning = sorted(glob.glob("results/metrics_deep_learning_model_*.json"))[-1]

    model_files = {
        "Original Model": original,
        "Simplified Model": simplified,
        "Deep Learning Model": deep_learning,
    }

    # Load metrics
    metrics = {}
    for model_name, file_path in model_files.items():
        with open(file_path, "r") as f:
            data = json.load(f)
            metrics[model_name] = data["holdout_metrics"]

    return pd.DataFrame(metrics).T[["mse", "rmse", "r2"]]


def compare_models():
    """Compare the three models"""
    # Get performance metrics
    metrics_df = load_latest_results()

    # Create performance comparison plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    metrics = ["mse", "rmse", "r2"]

    for i, metric in enumerate(metrics):
        sns.barplot(data=metrics_df, y=metrics_df.index, x=metric, ax=axes[i])
        axes[i].set_title(f"{metric.upper()}")

    plt.tight_layout()

    # Print metrics table
    print("\nModel Performance on Holdout Set:")
    print("=" * 80)
    print(metrics_df.round(4))

    return metrics_df, fig


if __name__ == "__main__":
    metrics_df, fig = compare_models()
    plt.show()
