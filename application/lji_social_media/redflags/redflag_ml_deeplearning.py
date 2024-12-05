import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import json
import datetime
import uuid
import pickle
import libraries.claude_prompts as cp
import logging
from pathlib import Path
import time
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_COLUMNS = cp.RED_FLAGS

# Add these imports at the top


def analyze_and_save_feature_importance(
    importance_values, feature_names, timestamp, model_id
):
    """
    Analyze and save feature importance results for all features.
    Matches the ensemble model's output format.
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
        ).sort_values("importance_mean", ascending=True)

        # Save complete results to CSV
        importance_df.to_csv(f"{analysis_dir}/{model_name}.csv", index=False)

        # Create and save plot with all features
        plt.figure(figsize=(12, max(8, len(feature_names) * 0.3)))

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
        top_20 = importance_df.tail(20)

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
        ranking_df.index = ranking_df.index + 1
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
            logger.info(f"\nDEBUG: Loading {split_type}")
            if isinstance(data, pd.DataFrame):
                logger.info(f"Shape: {data.shape}")
                logger.info(f"Columns: {data.columns.tolist()}")
                splits[split_type] = data.copy()
            elif isinstance(data, pd.Series):
                logger.info(f"Length: {len(data)}")
                splits[split_type] = data.copy()
            else:
                logger.info(f"Type: {type(data)}")
                splits[split_type] = pd.DataFrame(data, columns=DATA_COLUMNS)

    with open(f"data/splits/split_info_{timestamp}.json", "r") as f:
        split_info = json.load(f)

    return splits, split_info


class TabularDataset(Dataset):
    """Custom Dataset for tabular data"""

    def __init__(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        self.X = torch.FloatTensor(X.values)
        self.y = torch.FloatTensor(y.values) if y is not None else None

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        if self.y is not None:
            return self.X[idx], self.y[idx]
        return self.X[idx]


# [Previous DeepTabularRegressor and ResidualBlock classes remain unchanged]
class ResidualBlock(nn.Module):
    """Residual block with skip connections"""

    def __init__(self, input_dim: int, hidden_dim: int, dropout: float = 0.1):
        super().__init__()
        self.layer = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, input_dim),
            nn.LayerNorm(input_dim),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return x + self.layer(x)


class DeepTabularRegressor(nn.Module):
    """Advanced neural network for tabular data"""

    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int] = [256, 128, 64],
        num_residual_blocks: int = 2,
        dropout: float = 0.1,
    ):
        super().__init__()

        # Input layer with normalization
        self.input_norm = nn.LayerNorm(input_dim)

        # Initial embedding layer
        self.embedding = nn.Sequential(
            nn.Linear(input_dim, hidden_dims[0]),
            nn.LayerNorm(hidden_dims[0]),
            nn.ReLU(),
            nn.Dropout(dropout),
        )

        # Residual blocks
        self.residual_blocks = nn.ModuleList(
            [
                ResidualBlock(hidden_dims[0], hidden_dims[0] * 2, dropout)
                for _ in range(num_residual_blocks)
            ]
        )

        # Deep network layers
        layers = []
        for i in range(len(hidden_dims) - 1):
            layers.extend(
                [
                    nn.Linear(hidden_dims[i], hidden_dims[i + 1]),
                    nn.LayerNorm(hidden_dims[i + 1]),
                    nn.ReLU(),
                    nn.Dropout(dropout),
                ]
            )
        self.deep_layers = nn.Sequential(*layers)

        # Output layer
        self.output = nn.Sequential(
            nn.Linear(hidden_dims[-1], 1),
            nn.ReLU(),  # Ensure non-negative predictions for scores
        )

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.kaiming_normal_(module.weight)
            if module.bias is not None:
                nn.init.constant_(module.bias, 0)

    def forward(self, x):
        x = self.input_norm(x)
        x = self.embedding(x)

        # Apply residual blocks
        for block in self.residual_blocks:
            x = block(x)

        x = self.deep_layers(x)
        return self.output(x).squeeze()


class ModelTrainer:
    """Handles model training and evaluation"""

    def __init__(
        self,
        model: nn.Module,
        learning_rate: float = 1e-3,
        batch_size: int = 32,
        num_epochs: int = 100,
        early_stopping_patience: int = 10,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        self.model = model.to(device)
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.patience = early_stopping_patience
        self.device = device

        self.criterion = nn.MSELoss()
        self.optimizer = optim.AdamW(
            self.model.parameters(), lr=learning_rate, weight_decay=0.01
        )
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode="min", factor=0.5, patience=5, verbose=True
        )

    def train_epoch(self, train_loader: DataLoader) -> float:
        self.model.train()
        total_loss = 0

        for X, y in train_loader:
            X, y = X.to(self.device), y.to(self.device)

            self.optimizer.zero_grad()
            y_pred = self.model(X)
            loss = self.criterion(y_pred, y)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(train_loader)

    def validate(self, val_loader: DataLoader) -> float:
        self.model.eval()
        total_loss = 0

        with torch.no_grad():
            for X, y in val_loader:
                X, y = X.to(self.device), y.to(self.device)
                y_pred = self.model(X)
                loss = self.criterion(y_pred, y)
                total_loss += loss.item()

        return total_loss / len(val_loader)

    def train(
        self, train_loader: DataLoader, val_loader: DataLoader, return_best: bool = True
    ) -> Dict:
        best_loss = float("inf")
        best_model = None
        patience_counter = 0
        history = {"train_loss": [], "val_loss": []}

        for epoch in range(self.num_epochs):
            train_loss = self.train_epoch(train_loader)
            val_loss = self.validate(val_loader)

            history["train_loss"].append(train_loss)
            history["val_loss"].append(val_loss)

            self.scheduler.step(val_loss)

            if val_loss < best_loss:
                best_loss = val_loss
                if return_best:
                    best_model = self._get_model_copy()
                patience_counter = 0
            else:
                patience_counter += 1

            if epoch % 10 == 0:
                logger.info(
                    f"Epoch {epoch}: train_loss={train_loss:.4f}, "
                    f"val_loss={val_loss:.4f}"
                )

            if patience_counter >= self.patience:
                logger.info("Early stopping triggered")
                break

        if return_best and best_model is not None:
            self.model.load_state_dict(best_model)

        return history

    def _get_model_copy(self):
        return {k: v.cpu().clone() for k, v in self.model.state_dict().items()}


def make_json_serializable(obj):
    """Convert objects to JSON-serializable format"""
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


def save_metrics(metrics, filename):
    """Save metrics in JSON format"""
    serializable_metrics = make_json_serializable(metrics)
    logger.info(f"Saving metrics as {filename}")
    with open(filename, "w") as f:
        json.dump(serializable_metrics, f, indent=4)


def evaluate_model(model, X, y, dataset_name=""):
    """Evaluate model performance with consistent metrics"""
    model.eval()
    with torch.no_grad():
        X_tensor = torch.FloatTensor(X.values).to(next(model.parameters()).device)
        y_pred = model(X_tensor).cpu().numpy()

    mse = float(mean_squared_error(y, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y, y_pred))

    logger.info(f"\nModel performance on {dataset_name}:")
    logger.info(f"MSE: {mse:.4f}")
    logger.info(f"RMSE: {rmse:.4f}")
    logger.info(f"R²: {r2:.4f}")

    return {"mse": mse, "rmse": rmse, "r2": r2, "predictions": y_pred.tolist()}


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


def analyze_feature_importance(model, X, feature_names, timestamp, model_id):
    """Analyze feature importance using gradients"""
    model.eval()
    X_tensor = (
        torch.FloatTensor(X.values)
        .requires_grad_(True)
        .to(next(model.parameters()).device)
    )

    output = model(X_tensor)
    output.sum().backward()

    importance = X_tensor.grad.abs().mean(dim=0).cpu().numpy()

    importance_values = {
        "deep_learning_importance": {
            "values": importance,
            "mean": importance,
            "std": np.zeros_like(importance),  # For consistency with ensemble format
        }
    }

    return analyze_and_save_feature_importance(
        importance_values, feature_names, timestamp, model_id
    )


def main():
    """Main execution function with aligned methodology"""
    file_path = "results/advert_flags.csv"
    logger.info("Loading original data...")
    original_data = pd.read_csv(file_path)

    if "IDn" not in original_data.columns:
        raise ValueError("Original data must contain 'IDn' column")

    # Load the same splits as ensemble model
    splits_timestamp = "20241204_122617"
    splits, split_info = load_splits(splits_timestamp)

    # Generate unique model identifier
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    model_id = f"deep_learning_model_{timestamp}"

    # Initialize model
    model = DeepTabularRegressor(
        input_dim=len(DATA_COLUMNS),
        hidden_dims=[256, 128, 64],
        num_residual_blocks=2,
        dropout=0.1,
    ).to("cuda" if torch.cuda.is_available() else "cpu")

    # Train on training data
    train_dataset = TabularDataset(splits["X_train"], splits["y_train"])
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    trainer = ModelTrainer(model=model)
    trainer.train(train_loader, train_loader)

    # Evaluate on holdout set
    holdout_metrics = evaluate_model(
        model, splits["X_holdout"], splits["y_holdout"], "holdout set"
    )

    with torch.no_grad():
        holdout_predictions = (
            model(
                torch.FloatTensor(splits["X_holdout"].values).to(
                    next(model.parameters()).device
                )
            )
            .cpu()
            .numpy()
        )

    holdout_file = save_detailed_holdout_results(
        model,
        splits["X_holdout"],
        splits["y_holdout"],
        holdout_predictions,
        model_id,
        original_data,
    )

    # Calculate feature importance
    holdout_importance = analyze_feature_importance(
        model, splits["X_holdout"], DATA_COLUMNS, timestamp, f"{model_id}_holdout"
    )

    # Train final model on full dataset
    final_dataset = TabularDataset(splits["X_full"], splits["y_full"])
    final_loader = DataLoader(final_dataset, batch_size=32, shuffle=True)

    final_model = DeepTabularRegressor(
        input_dim=len(DATA_COLUMNS),
        hidden_dims=[256, 128, 64],
        num_residual_blocks=2,
        dropout=0.1,
    ).to("cuda" if torch.cuda.is_available() else "cpu")

    final_trainer = ModelTrainer(model=final_model)
    final_trainer.train(final_loader, final_loader)

    # Calculate final feature importance
    final_importance = analyze_feature_importance(
        final_model, splits["X_full"], DATA_COLUMNS, timestamp, f"{model_id}_final"
    )

    # Save final model
    model_filename = f"models/final_{model_id}.pt"
    logger.info(f"\nSaving final model as {model_filename}")
    torch.save(final_model.state_dict(), model_filename)

    # Save metrics and information
    metrics = {
        "model_id": model_id,
        "timestamp": timestamp,
        "holdout_metrics": holdout_metrics,
        "split_info": split_info,
        "model_parameters": {
            "hidden_dims": [256, 128, 64],
            "num_residual_blocks": 2,
            "dropout": 0.1,
        },
        "holdout_importance_summary": holdout_importance,
        "final_importance_summary": final_importance,
    }

    metrics_filename = f"results/metrics_{model_id}.json"
    save_metrics(metrics, metrics_filename)


if __name__ == "__main__":
    main()
