import pandas as pd
from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor,
)
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import RFE
from sklearn.svm import SVR
from scipy.stats import uniform, randint
import datetime
import pickle

# Add to your existing imports
from libraries import smote_enhancement as se
import libraries.claude_prompts as cp

# Import shared utilities
from libraries.common_utils import (
    load_splits,
    evaluate_model,
    save_detailed_holdout_results,
    analyze_and_save_feature_importance,
    DATA_COLUMNS,
    save_metrics,
)

DATA_COLUMNS = cp.RED_FLAGS


def create_advanced_pipeline():
    """
    Create an advanced model pipeline with polynomial features, feature selection, and stacking.
    """
    return Pipeline(
        [
            (
                "features",
                ColumnTransformer(
                    [
                        (
                            "poly",
                            Pipeline(
                                [
                                    ("imputer", SimpleImputer(strategy="mean")),
                                    (
                                        "poly_features",
                                        PolynomialFeatures(
                                            degree=2, include_bias=False
                                        ),
                                    ),
                                    ("scaler", StandardScaler()),
                                ]
                            ),
                            DATA_COLUMNS,
                        )
                    ]
                ),
            ),
            (
                "feature_selection",
                RFE(estimator=SVR(kernel="linear"), n_features_to_select=10),
            ),
            (
                "regressor",
                StackingRegressor(
                    estimators=[
                        ("gb", GradientBoostingRegressor(random_state=42)),
                        ("rf", RandomForestRegressor(random_state=42)),
                    ],
                    final_estimator=SVR(),
                ),
            ),
        ]
    )


def find_best_hyperparameters(X_train, y_train):
    """
    Find the best hyperparameters using cross-validation on training data.
    """
    pipeline = create_advanced_pipeline()

    param_distributions = {
        "regressor__gb__n_estimators": randint(100, 500),
        "regressor__gb__learning_rate": uniform(0.01, 0.3),
        "regressor__gb__max_depth": randint(3, 10),
        "regressor__gb__min_samples_split": randint(2, 20),
        "regressor__gb__min_samples_leaf": randint(1, 10),
        "regressor__rf__n_estimators": randint(100, 500),
        "regressor__rf__max_depth": randint(3, 10),
        "regressor__final_estimator__C": uniform(0.1, 10),
        "regressor__final_estimator__epsilon": uniform(0.01, 0.1),
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


def calculate_feature_importance(model, X, feature_names):
    """
    Calculate feature importance using permutation importance.
    """
    from sklearn.inspection import permutation_importance

    importance_values = {}

    r = permutation_importance(
        model, X, model.predict(X), n_repeats=10, random_state=42, n_jobs=-1
    )

    importance_values["full_pipeline_importance"] = {
        "values": r.importances,
        "mean": r.importances_mean,
        "std": r.importances_std,
    }

    return importance_values, X


def main():
    """
    Main function to run the advanced model pipeline with proper evaluation.
    """
    # Load original data
    file_path = "results/advert_flags.csv"
    print("Loading original data...")
    original_data = pd.read_csv(file_path)

    # Load splits
    splits_timestamp = "20241114_115648"
    splits, split_info = load_splits(splits_timestamp)
    # Initialize metrics dictionary early

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    model_id = f"advanced_redflag_model_{timestamp}"
    metrics = {"model_id": model_id, "timestamp": timestamp, "split_info": split_info}
    print("\n=== Evaluating SMOTE Enhancement ===")
    smote_results = se.main(
        create_advanced_pipeline(),  # Your model
        splits["X_train"],
        splits["y_train"],
        splits["X_holdout"],
        splits["y_holdout"],
    )

    # If SMOTE improved performance, use the enhanced data
    if (
        smote_results["evaluation_results"]["smote"]["r2"]
        > smote_results["evaluation_results"]["original"]["r2"]
    ):
        print("\nSMOTE improved performance - using SMOTE-enhanced data")
        X_train_enhanced, y_train_enhanced = smote_results["resampled_data"]

        # Update training data
        splits["X_train"] = X_train_enhanced
        splits["y_train"] = y_train_enhanced

        # Also save the SMOTE parameters for reproducibility
        print("Best SMOTE parameters:", smote_results["best_params"])

        # Add SMOTE info to metrics
        metrics["smote_params"] = smote_results["best_params"]
        metrics["smote_improvement"] = {
            "original_r2": smote_results["evaluation_results"]["original"]["r2"],
            "smote_r2": smote_results["evaluation_results"]["smote"]["r2"],
        }
    else:
        print("\nSMOTE did not improve performance - using original data")
    # Generate unique model identifier
    print("\n=== Training Initial Model on Training Data ===")
    best_params = find_best_hyperparameters(splits["X_train"], splits["y_train"])

    # Train initial model
    initial_model = create_advanced_pipeline()
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

    print("\nCalculating feature importance for holdout set...")
    holdout_importance, X_holdout_transformed = calculate_feature_importance(
        initial_model, splits["X_holdout"], DATA_COLUMNS
    )

    holdout_importance_summary = analyze_and_save_feature_importance(
        holdout_importance, DATA_COLUMNS, timestamp, f"{model_id}_holdout"
    )

    print("\n=== Training Final Model on Full Dataset ===")
    final_model = create_advanced_pipeline()
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

    print("\nCalculating feature importance for final model...")
    final_importance, X_final_transformed = calculate_feature_importance(
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

    # Save metrics
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
