import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error, r2_score
import optuna
import plotly.graph_objects as go
from typing import Dict, Tuple, List, Optional
import logging
from pathlib import Path
import datetime
import uuid
import pickle
import libraries.claude_prompts as cp
import time

# Add these imports at the top
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import os
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_COLUMNS = cp.RED_FLAGS


class TabularDataset(Dataset):
    """Custom Dataset for tabular data"""

    def __init__(self, X: np.ndarray, y: Optional[np.ndarray] = None):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y) if y is not None else None

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        if self.y is not None:
            return self.X[idx], self.y[idx]
        return self.X[idx]


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


def objective(trial: optuna.Trial, X: np.ndarray, y: np.ndarray) -> float:
    """Optuna objective function for hyperparameter optimization"""
    # Define hyperparameter space
    params = {
        "hidden_dims": [
            trial.suggest_int(f"hidden_dim_{i}", 32, 512)
            for i in range(trial.suggest_int("n_layers", 2, 4))
        ],
        "num_residual_blocks": trial.suggest_int("num_residual_blocks", 1, 4),
        "dropout": trial.suggest_float("dropout", 0.1, 0.5),
        "learning_rate": trial.suggest_float("learning_rate", 1e-4, 1e-2, log=True),
        "batch_size": trial.suggest_categorical("batch_size", [16, 32, 64, 128]),
    }

    # Cross-validation
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    scores = []

    for train_idx, val_idx in kf.split(X):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        # Create datasets and dataloaders
        train_dataset = TabularDataset(X_train, y_train)
        val_dataset = TabularDataset(X_val, y_val)
        train_loader = DataLoader(
            train_dataset, batch_size=params["batch_size"], shuffle=True
        )
        val_loader = DataLoader(val_dataset, batch_size=params["batch_size"])

        # Initialize and train model
        model = DeepTabularRegressor(
            input_dim=X.shape[1],
            hidden_dims=params["hidden_dims"],
            num_residual_blocks=params["num_residual_blocks"],
            dropout=params["dropout"],
        )

        trainer = ModelTrainer(
            model=model,
            learning_rate=params["learning_rate"],
            batch_size=params["batch_size"],
            num_epochs=50,  # Reduced for optimization
        )

        history = trainer.train(train_loader, val_loader)
        scores.append(min(history["val_loss"]))

    return np.mean(scores)


def train_final_model(
    X: np.ndarray,
    y: np.ndarray,
    best_params: Dict,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> Tuple[DeepTabularRegressor, Dict, Dict]:
    """Train the final model with the best parameters and progress monitoring"""
    start_time = datetime.datetime.now()
    logger.info(f"Starting model training at {start_time}")

    # Setup hidden dimensions
    i = 0
    hidden_dims = []
    while f"hidden_dim_{i}" in best_params:
        hidden_dims.append(best_params[f"hidden_dim_{i}"])
        i += 1

    logger.info("-" * 50)
    logger.info("Model Configuration:")
    logger.info(f"Input Features: {X.shape[1]}")
    logger.info(f"Training Samples: {X.shape[0]}")
    logger.info(f"Hidden Dimensions: {hidden_dims}")
    logger.info(f"Residual Blocks: {best_params['num_residual_blocks']}")
    logger.info(f"Batch Size: {best_params['batch_size']}")
    logger.info(f"Learning Rate: {best_params['learning_rate']}")
    logger.info(f"Device: {device}")
    logger.info("-" * 50)

    # Initialize model
    model = DeepTabularRegressor(
        input_dim=X.shape[1],
        hidden_dims=hidden_dims,
        num_residual_blocks=best_params["num_residual_blocks"],
        dropout=best_params["dropout"],
    ).to(device)

    # Setup data
    dataset = TabularDataset(X, y)
    dataloader = DataLoader(
        dataset,
        batch_size=best_params["batch_size"],
        shuffle=True,
        num_workers=0,  # Disable multiprocessing
    )

    class MonitoredModelTrainer(ModelTrainer):
        def train_epoch(self, train_loader: DataLoader) -> float:
            self.model.train()
            total_loss = 0
            start_time = time.time()

            for batch_idx, (X, y) in enumerate(train_loader):
                X, y = X.to(self.device), y.to(self.device)

                self.optimizer.zero_grad()
                y_pred = self.model(X)
                loss = self.criterion(y_pred, y)

                loss.backward()
                self.optimizer.step()

                total_loss += loss.item()

                if (batch_idx + 1) % 2 == 0:  # Log every 2 batches
                    progress = (batch_idx + 1) / len(train_loader) * 100
                    elapsed = time.time() - start_time
                    logger.info(
                        f"Progress: {progress:.1f}% | "
                        f"Loss: {loss.item():.4f} | "
                        f"Time: {elapsed:.2f}s"
                    )

            return total_loss / len(train_loader)

        def train(
            self,
            train_loader: DataLoader,
            val_loader: DataLoader,
            return_best: bool = True,
        ) -> Dict:
            history = {"train_loss": [], "val_loss": [], "lr": [], "epoch_times": []}
            best_loss = float("inf")
            best_model = None
            patience_counter = 0

            for epoch in range(self.num_epochs):
                epoch_start = time.time()
                logger.info(f"\nEpoch {epoch + 1}/{self.num_epochs}")
                logger.info("-" * 30)

                train_loss = self.train_epoch(train_loader)
                val_loss = self.validate(val_loader)
                epoch_time = time.time() - epoch_start

                history["train_loss"].append(train_loss)
                history["val_loss"].append(val_loss)
                history["lr"].append(self.optimizer.param_groups[0]["lr"])
                history["epoch_times"].append(epoch_time)

                logger.info(
                    f"Epoch {epoch + 1} Summary:\n"
                    f"Train Loss: {train_loss:.4f}\n"
                    f"Val Loss: {val_loss:.4f}\n"
                    f"Learning Rate: {self.optimizer.param_groups[0]['lr']:.6f}\n"
                    f"Epoch Time: {epoch_time:.2f}s"
                )

                if val_loss < best_loss:
                    best_loss = val_loss
                    if return_best:
                        best_model = self._get_model_copy()
                    patience_counter = 0
                    logger.info("✓ New best model saved")
                else:
                    patience_counter += 1
                    logger.info(f"! No improvement for {patience_counter} epochs")

                self.scheduler.step(val_loss)

                if patience_counter >= self.patience:
                    logger.info("\nEarly stopping triggered!")
                    break

            if return_best and best_model is not None:
                self.model.load_state_dict(best_model)

            return history

    # Train model
    trainer = MonitoredModelTrainer(
        model=model,
        learning_rate=best_params["learning_rate"],
        batch_size=best_params["batch_size"],
    )

    logger.info("Starting training...")
    history = trainer.train(dataloader, dataloader, return_best=False)

    model.eval()
    with torch.no_grad():
        X_tensor = torch.FloatTensor(X).to(device)
        predictions = model(X_tensor).cpu().numpy()

    # Create results DataFrame
    results_df = pd.DataFrame(
        {"actual": y, "predicted": predictions, "error": y - predictions}
    )

    metrics = {
        "mse": mean_squared_error(y, predictions),
        "rmse": np.sqrt(mean_squared_error(y, predictions)),
        "r2": r2_score(y, predictions),
    }

    # Final summary
    end_time = datetime.datetime.now()
    training_duration = end_time - start_time

    logger.info("\nTraining Complete!")
    logger.info("-" * 50)
    logger.info(f"Total training time: {training_duration}")
    logger.info(f"Final Metrics:")
    for metric_name, metric_value in metrics.items():
        logger.info(f"{metric_name.upper()}: {metric_value:.4f}")
    logger.info("-" * 50)

    return model, metrics, history, results_df  # Added results_df to return


def save_artifacts(
    model: nn.Module,
    scaler: StandardScaler,
    metrics: Dict,
    history: Dict,
    best_params: Dict,
    results_df: pd.DataFrame,  # Added results_df parameter
):
    """Save model artifacts"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    base_path = Path("models/deep_learning")
    base_path.mkdir(parents=True, exist_ok=True)

    # Save model
    torch.save(model.state_dict(), base_path / f"model_{timestamp}_{unique_id}.pt")

    # Save scaler
    with open(base_path / f"scaler_{timestamp}_{unique_id}.pkl", "wb") as f:
        pickle.dump(scaler, f)

    # Save metrics and parameters
    results = {"metrics": metrics, "history": history, "parameters": best_params}
    with open(base_path / f"results_{timestamp}_{unique_id}.pkl", "wb") as f:
        pickle.dump(results, f)

    # Save predictions
    results_df.to_csv(
        base_path / f"predictions_{timestamp}_{unique_id}.csv", index=False
    )

    logger.info(f"Artifacts saved with identifier: {timestamp}_{unique_id}")


def load_and_preprocess_data(file_path):
    """Enhanced data loading and preprocessing"""
    logger.info("Loading and preprocessing data...")

    model_data = pd.read_csv(file_path)
    model_data = model_data[
        (model_data["monitor_score"] != "unknown")
        & (~model_data["monitor_score"].isna())
    ]

    # Enhanced preprocessing
    mapping = {"yes": 1, "no": 0}
    model_data = model_data.replace(mapping)

    return model_data[DATA_COLUMNS].values, model_data["monitor_score"].values


def main():
    """Main execution function"""
    logger.info("Starting deep learning pipeline...")

    # Load and preprocess data
    file_path = "results/advert_flags.csv"
    X, y = load_and_preprocess_data(file_path)

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Optimize hyperparameters
    logger.info("Starting hyperparameter optimization...")
    study = optuna.create_study(direction="minimize")
    study.optimize(lambda trial: objective(trial, X_scaled, y), n_trials=50)

    # Train final model
    logger.info("Training final model...")
    model, metrics, history, results_df = train_final_model(
        X_scaled, y, study.best_params
    )  # Updated to receive results_df

    # Save artifacts
    save_artifacts(
        model, scaler, metrics, history, study.best_params, results_df
    )  # Added results_df

    logger.info("Pipeline completed successfully!")
    logger.info(f"Final metrics: {metrics}")


if __name__ == "__main__":
    main()
