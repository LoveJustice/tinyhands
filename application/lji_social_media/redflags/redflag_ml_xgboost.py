import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV, KFold
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import xgboost as xgb
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor,
)
import optuna
import shap
from scipy.stats import uniform, randint
import datetime
import uuid
import pickle
import warnings
import logging
from pathlib import Path
import libraries.claude_prompts as cp
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_COLUMNS = cp.RED_FLAGS


class AdvancedFeatureEngineering:
    """Advanced feature engineering pipeline"""

    def __init__(self):
        self.feature_stats = {}

    def create_interaction_features(self, df):
        """Create interaction features between important columns"""
        interactions = {}
        for i, col1 in enumerate(DATA_COLUMNS):
            for col2 in DATA_COLUMNS[i + 1 :]:
                interactions[f"{col1}_{col2}_interact"] = df[col1] * df[col2]
        return pd.DataFrame(interactions)

    def create_aggregate_features(self, df, group_col="group_id"):
        """Create aggregated features within groups"""
        aggs = {}
        for col in DATA_COLUMNS:
            group_stats = df.groupby(group_col)[col].agg(["mean", "std", "min", "max"])
            for stat in ["mean", "std", "min", "max"]:
                aggs[f"{col}_{group_col}_{stat}"] = df[group_col].map(group_stats[stat])
        return pd.DataFrame(aggs)


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

    # Advanced outlier detection
    for col in DATA_COLUMNS:
        model_data[col] = pd.to_numeric(model_data[col], errors="coerce")
        Q1 = model_data[col].quantile(0.25)
        Q3 = model_data[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        model_data[col] = model_data[col].clip(lower_bound, upper_bound)

    # Feature engineering
    fe = AdvancedFeatureEngineering()
    interaction_features = fe.create_interaction_features(model_data[DATA_COLUMNS])
    aggregate_features = fe.create_aggregate_features(model_data)

    # Combine all features
    enhanced_features = pd.concat(
        [model_data[DATA_COLUMNS], interaction_features, aggregate_features], axis=1
    )

    return enhanced_features, model_data["monitor_score"]


def create_advanced_pipeline():
    """Create an advanced stacking pipeline with XGBoost"""

    feature_pipeline = ColumnTransformer(
        transformers=[
            (
                "standard",
                Pipeline(
                    [
                        ("imputer", KNNImputer(n_neighbors=5)),
                        ("scaler", RobustScaler()),
                    ]
                ),
                DATA_COLUMNS,
            ),
            (
                "passthrough",
                "passthrough",
                [col for col in DATA_COLUMNS if col not in DATA_COLUMNS],
            ),
        ]
    )

    # Create base estimators
    estimators = [
        ("xgb1", xgb.XGBRegressor(tree_method="hist", random_state=42, n_jobs=-1)),
        ("xgb2", xgb.XGBRegressor(tree_method="hist", random_state=24, n_jobs=-1)),
        ("rf", RandomForestRegressor(n_jobs=-1, random_state=42)),
    ]

    stacking = StackingRegressor(
        estimators=estimators,
        final_estimator=xgb.XGBRegressor(
            tree_method="hist", random_state=42, n_jobs=-1
        ),
        cv=5,
        n_jobs=-1,
    )

    return Pipeline([("features", feature_pipeline), ("regressor", stacking)])


def objective(trial, X, y):
    """Optuna objective function with corrected parameter structure"""
    param_space = {
        # First XGBoost estimator
        "regressor__xgb1__n_estimators": trial.suggest_int(
            "xgb1_n_estimators", 100, 1000
        ),
        "regressor__xgb1__max_depth": trial.suggest_int("xgb1_max_depth", 3, 12),
        "regressor__xgb1__learning_rate": trial.suggest_float(
            "xgb1_learning_rate", 1e-3, 0.1, log=True
        ),
        "regressor__xgb1__subsample": trial.suggest_float("xgb1_subsample", 0.5, 1.0),
        "regressor__xgb1__colsample_bytree": trial.suggest_float(
            "xgb1_colsample_bytree", 0.5, 1.0
        ),
        "regressor__xgb1__min_child_weight": trial.suggest_int(
            "xgb1_min_child_weight", 1, 7
        ),
        "regressor__xgb1__gamma": trial.suggest_float(
            "xgb1_gamma", 1e-8, 1.0, log=True
        ),
        # Second XGBoost estimator
        "regressor__xgb2__n_estimators": trial.suggest_int(
            "xgb2_n_estimators", 100, 1000
        ),
        "regressor__xgb2__max_depth": trial.suggest_int("xgb2_max_depth", 3, 12),
        "regressor__xgb2__learning_rate": trial.suggest_float(
            "xgb2_learning_rate", 1e-3, 0.1, log=True
        ),
        "regressor__xgb2__subsample": trial.suggest_float("xgb2_subsample", 0.5, 1.0),
        "regressor__xgb2__colsample_bytree": trial.suggest_float(
            "xgb2_colsample_bytree", 0.5, 1.0
        ),
        # Random Forest estimator
        "regressor__rf__n_estimators": trial.suggest_int("rf_n_estimators", 100, 500),
        "regressor__rf__max_depth": trial.suggest_int("rf_max_depth", 3, 12),
        "regressor__rf__min_samples_split": trial.suggest_int(
            "rf_min_samples_split", 2, 10
        ),
        # Final estimator
        "regressor__final_estimator__n_estimators": trial.suggest_int(
            "final_n_estimators", 100, 500
        ),
        "regressor__final_estimator__max_depth": trial.suggest_int(
            "final_max_depth", 3, 8
        ),
        "regressor__final_estimator__learning_rate": trial.suggest_float(
            "final_learning_rate", 1e-3, 0.1, log=True
        ),
    }

    pipeline = create_advanced_pipeline()
    pipeline.set_params(**param_space)

    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    scores = []

    for train_idx, val_idx in cv.split(X):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_val)
        score = mean_squared_error(y_val, y_pred)
        scores.append(score)

    return np.mean(scores)


def optimize_hyperparameters(X, y, n_trials=100):
    """Optimize hyperparameters using Optuna"""
    logger.info("Starting hyperparameter optimization with Optuna...")

    study = optuna.create_study(direction="minimize")
    study.optimize(lambda trial: objective(trial, X, y), n_trials=n_trials)

    logger.info(f"Best trial MSE: {study.best_value:.4f}")
    logger.info("Best hyperparameters:")

    # Convert parameter names to match pipeline structure
    best_params = {}
    param_mapping = {
        "xgb1_": "regressor__xgb1__",
        "xgb2_": "regressor__xgb2__",
        "rf_": "regressor__rf__",
        "final_": "regressor__final_estimator__",
    }

    for param_name, value in study.best_params.items():
        for prefix, pipeline_prefix in param_mapping.items():
            if param_name.startswith(prefix):
                param_suffix = param_name[len(prefix) :]
                pipeline_param = f"{pipeline_prefix}{param_suffix}"
                best_params[pipeline_param] = value
                break

    for param, value in best_params.items():
        logger.info(f"{param}: {value}")

    return best_params


def train_final_model(X, y, best_params):
    """Train the final model with the best parameters"""
    logger.info("Training final model...")

    pipeline = create_advanced_pipeline()
    pipeline.set_params(**best_params)
    pipeline.fit(X, y)

    # Calculate performance metrics
    y_pred = pipeline.predict(X)
    metrics = {
        "MSE": mean_squared_error(y, y_pred),
        "RMSE": np.sqrt(mean_squared_error(y, y_pred)),
        "MAE": mean_absolute_error(y, y_pred),
        "R²": r2_score(y, y_pred),
    }

    logger.info("Final model performance:")
    for metric, value in metrics.items():
        logger.info(f"{metric}: {value:.4f}")

    return pipeline, metrics


def analyze_feature_importance(model, X):
    """Analyze feature importance using SHAP values for a stacked model"""
    logger.info("Calculating SHAP values for feature importance...")

    importance_results = {}

    # Get the stacking regressor
    stacking_regressor = model.named_steps["regressor"]

    # Analyze each base estimator from the named_estimators_ attribute
    for name, estimator in stacking_regressor.named_estimators_.items():
        if isinstance(estimator, xgb.XGBRegressor):
            # For XGBoost models
            try:
                # Ensure the model is fitted
                if hasattr(estimator, "feature_importances_"):
                    explainer = shap.TreeExplainer(estimator)
                    shap_values = explainer.shap_values(X)
                    importance_results[f"{name}_shap"] = pd.DataFrame(
                        {
                            "feature": X.columns,
                            "importance": np.abs(shap_values).mean(0),
                        }
                    ).sort_values("importance", ascending=False)

                    # Also get native feature importance
                    importance_results[f"{name}_native"] = pd.DataFrame(
                        {
                            "feature": X.columns,
                            "importance": estimator.feature_importances_,
                        }
                    ).sort_values("importance", ascending=False)
                else:
                    logger.warning(f"Estimator {name} is not fitted yet")

            except Exception as e:
                logger.warning(f"Could not calculate SHAP values for {name}: {str(e)}")
                # Fallback to native feature importance if available
                if hasattr(estimator, "feature_importances_"):
                    importance_results[f"{name}_native"] = pd.DataFrame(
                        {
                            "feature": X.columns,
                            "importance": estimator.feature_importances_,
                        }
                    ).sort_values("importance", ascending=False)

        elif isinstance(estimator, RandomForestRegressor):
            # For Random Forest
            if hasattr(estimator, "feature_importances_"):
                importance_results[f"{name}_native"] = pd.DataFrame(
                    {"feature": X.columns, "importance": estimator.feature_importances_}
                ).sort_values("importance", ascending=False)
            else:
                logger.warning(f"Random Forest estimator {name} is not fitted yet")

    # Get feature importance from final estimator
    try:
        final_estimator = stacking_regressor.final_estimator_
        if hasattr(final_estimator, "feature_importances_"):
            # For the final estimator, we can only get feature importance for the meta-features
            meta_features = stacking_regressor.transform(X)

            explainer = shap.TreeExplainer(final_estimator)
            final_shap_values = explainer.shap_values(meta_features)

            # Map meta-features back to original features
            meta_feature_importance = np.abs(final_shap_values).mean(0)
            importance_results["final_estimator"] = pd.DataFrame(
                {
                    "feature": [
                        f"meta_{i}" for i in range(len(meta_feature_importance))
                    ],
                    "importance": meta_feature_importance,
                }
            ).sort_values("importance", ascending=False)

    except Exception as e:
        logger.warning(f"Could not calculate SHAP values for final estimator: {str(e)}")

    # Calculate aggregate importance across all base models
    aggregate_importance = pd.DataFrame()

    for name, imp_df in importance_results.items():
        if not name.endswith("_native") and "final_estimator" not in name:
            if aggregate_importance.empty:
                aggregate_importance = imp_df.copy()
                aggregate_importance.columns = ["feature", "importance_sum"]
            else:
                aggregate_importance = aggregate_importance.merge(
                    imp_df, on="feature", suffixes=("_sum", "")
                )
                aggregate_importance["importance_sum"] += aggregate_importance[
                    "importance"
                ]
                aggregate_importance.drop("importance", axis=1, inplace=True)

    if not aggregate_importance.empty:
        importance_results["aggregate"] = aggregate_importance.sort_values(
            "importance_sum", ascending=False
        ).rename(columns={"importance_sum": "importance"})
    else:
        # Fallback to using native feature importance if SHAP analysis failed
        native_importance = pd.DataFrame()
        for name, imp_df in importance_results.items():
            if name.endswith("_native"):
                if native_importance.empty:
                    native_importance = imp_df.copy()
                    native_importance.columns = ["feature", "importance_sum"]
                else:
                    native_importance = native_importance.merge(
                        imp_df, on="feature", suffixes=("_sum", "")
                    )
                    native_importance["importance_sum"] += native_importance[
                        "importance"
                    ]
                    native_importance.drop("importance", axis=1, inplace=True)

        if not native_importance.empty:
            importance_results["aggregate"] = native_importance.sort_values(
                "importance_sum", ascending=False
            ).rename(columns={"importance_sum": "importance"})

    return importance_results


def save_artifacts(model, metrics, feature_importance, results_df):
    """Save all model artifacts"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    base_path = Path("models")
    base_path.mkdir(exist_ok=True)

    # Save model
    model_path = base_path / f"xgboost_stack_model_{timestamp}_{unique_id}.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    # Save metrics
    metrics_df = pd.DataFrame([metrics])
    metrics_df.to_csv(base_path / f"metrics_{timestamp}_{unique_id}.csv", index=False)

    # Save feature importance
    feature_importance.to_csv(
        base_path / f"feature_importance_{timestamp}_{unique_id}.csv", index=False
    )

    # Save predictions
    results_df.to_csv(
        base_path / f"predictions_{timestamp}_{unique_id}.csv", index=False
    )

    logger.info(f"All artifacts saved with identifier: {timestamp}_{unique_id}")


def plot_feature_importance(importance_results, top_n=10):
    """Plot feature importance results"""
    import matplotlib.pyplot as plt

    n_models = len(importance_results)
    fig, axes = plt.subplots(n_models, 1, figsize=(10, 5 * n_models))

    if n_models == 1:
        axes = [axes]

    for ax, (name, imp_df) in zip(axes, importance_results.items()):
        top_features = imp_df.head(top_n)

        ax.barh(range(len(top_features)), top_features["importance"])
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features["feature"])
        ax.set_title(f"Top {top_n} Important Features - {name}")
        ax.set_xlabel("Importance Score")

    plt.tight_layout()
    return fig


def save_feature_importance_results(
    importance_results, base_path, timestamp, unique_id
):
    """Save feature importance results to files"""
    importance_path = base_path / f"feature_importance_{timestamp}_{unique_id}"
    importance_path.mkdir(exist_ok=True)

    # Save each importance DataFrame
    for name, imp_df in importance_results.items():
        imp_df.to_csv(importance_path / f"{name}_importance.csv", index=False)

    # Create and save visualization
    fig = plot_feature_importance(importance_results)
    fig.savefig(importance_path / "feature_importance_plot.png")
    plt.close(fig)


def main():
    """Main execution function"""
    logger.info("Starting the enhanced XGBoost pipeline...")

    # Load and preprocess data
    file_path = "results/advert_flags.csv"
    X, y = load_and_preprocess_data(file_path)

    # Optimize hyperparameters
    best_params = optimize_hyperparameters(X, y)

    # Train final model
    final_model, metrics = train_final_model(X, y, best_params)

    # Analyze feature importance
    importance_results = analyze_feature_importance(final_model, X)

    # Generate predictions
    predictions = final_model.predict(X)
    results_df = pd.DataFrame(
        {"actual": y, "predicted": predictions, "error": y - predictions}
    )

    # Save all artifacts
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    base_path = Path("models")
    base_path.mkdir(exist_ok=True)

    save_artifacts(final_model, metrics, importance_results["aggregate"], results_df)
    save_feature_importance_results(importance_results, base_path, timestamp, unique_id)

    logger.info("Pipeline completed successfully!")


if __name__ == "__main__":
    main()
