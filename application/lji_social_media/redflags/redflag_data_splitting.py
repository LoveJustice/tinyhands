import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import pickle
import datetime
import os
import json
import libraries.claude_prompts as cp

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

    return model_data


def create_data_splits(file_path):
    """
    Create and save train/holdout splits for model comparison.
    """
    # Load data

    print("Loading and preprocessing data...")
    data = load_and_preprocess_data(file_path)

    # Split features and target
    X = data[DATA_COLUMNS]
    y = data["monitor_score"]

    # Create train-holdout split
    X_train, X_holdout, y_train, y_holdout = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Create directories if they don't exist
    os.makedirs("data/splits", exist_ok=True)

    # Save splits
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    split_info = {
        "timestamp": timestamp,
        "train_size": len(X_train),
        "holdout_size": len(X_holdout),
        "total_size": len(X),
        "features": list(DATA_COLUMNS),
        "random_state": 42,
        "holdout_fraction": 0.2,
    }

    # Save data splits
    splits = {
        "X_train": X_train,
        "X_holdout": X_holdout,
        "y_train": y_train,
        "y_holdout": y_holdout,
        "X_full": X,
        "y_full": y,
    }

    for name, data in splits.items():
        filename = f"data/splits/{name}_{timestamp}.pkl"
        with open(filename, "wb") as f:
            pickle.dump(data, f)

    # Save split info
    with open(f"data/splits/split_info_{timestamp}.json", "w") as f:
        json.dump(split_info, f, indent=4)

    print("\nData splits created and saved:")
    print(f"Training set size: {len(X_train)}")
    print(f"Holdout set size: {len(X_holdout)}")
    print(f"Full dataset size: {len(X)}")
    print(f"\nFiles saved with timestamp: {timestamp}")

    return timestamp


def load_data_splits(timestamp):
    """
    Load saved data splits for model training and evaluation.
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
            splits[split_type] = pickle.load(f)

    with open(f"data/splits/split_info_{timestamp}.json", "r") as f:
        split_info = json.load(f)

    return splits, split_info


def main():
    """
    Create initial data splits to be used across all model comparisons.
    """
    file_path = "results/new_presence.csv"
    timestamp = create_data_splits(file_path)
    print("\nTo use these splits in your modeling scripts, load them using:")
    print(f"splits, split_info = load_data_splits('{timestamp}')")


if __name__ == "__main__":
    main()
