import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
from sklearn.metrics import make_scorer, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score
from collections import Counter
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings("ignore")


def create_smote_pipeline(X_train, y_train, sampling_strategy="auto", k_neighbors=5):
    """
    Creates a SMOTE pipeline with proper scaling and validation

    Parameters:
    -----------
    X_train : array-like
        Training features
    y_train : array-like
        Training target values
    sampling_strategy : dict or str, default='auto'
        Sampling strategy for SMOTE
    k_neighbors : int, default=5
        Number of nearest neighbors to use for SMOTE

    Returns:
    --------
    X_resampled : array-like
        Resampled features
    y_resampled : array-like
        Resampled target values
    """
    # Scale features before SMOTE
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    # Initialize SMOTE
    smote = SMOTE(
        sampling_strategy=sampling_strategy, k_neighbors=k_neighbors, random_state=42
    )

    # Apply SMOTE
    X_resampled, y_resampled = smote.fit_resample(X_scaled, y_train)

    # Inverse transform features back to original scale
    X_resampled = scaler.inverse_transform(X_resampled)

    return X_resampled, y_resampled


def compare_distributions(y_orig, y_resampled):
    """
    Compare original and resampled class distributions
    """
    orig_dist = Counter(y_orig)
    resampled_dist = Counter(y_resampled)

    print("Original class distribution:")
    for k in sorted(orig_dist.keys()):
        print(f"Class {k}: {orig_dist[k]}")

    print("\nResampled class distribution:")
    for k in sorted(resampled_dist.keys()):
        print(f"Class {k}: {resampled_dist[k]}")


def evaluate_smote_impact(model, X_train, y_train, X_test, y_test):
    """
    Evaluate model performance with and without SMOTE
    """
    # Without SMOTE
    model_orig = model.fit(X_train, y_train)
    y_pred_orig = model_orig.predict(X_test)
    mse_orig = mean_squared_error(y_test, y_pred_orig)
    r2_orig = r2_score(y_test, y_pred_orig)

    # With SMOTE
    X_resampled, y_resampled = create_smote_pipeline(X_train, y_train)
    model_smote = model.fit(X_resampled, y_resampled)
    y_pred_smote = model_smote.predict(X_test)
    mse_smote = mean_squared_error(y_test, y_pred_smote)
    r2_smote = r2_score(y_test, y_pred_smote)

    results = {
        "original": {"mse": mse_orig, "rmse": np.sqrt(mse_orig), "r2": r2_orig},
        "smote": {"mse": mse_smote, "rmse": np.sqrt(mse_smote), "r2": r2_smote},
    }

    return results


def optimize_smote_parameters(model, X_train, y_train, cv=5):
    """
    Find optimal SMOTE parameters using cross-validation
    """
    best_score = float("-inf")
    best_params = {
        "k_neighbors": 5,  # Default value
        "sampling_strategy": "auto",  # Default value
    }

    # Parameter grid for SMOTE
    k_neighbors_range = [3, 5, 7, 9]

    # Create sampling strategy options
    # For ordinal targets, we'll try to balance up to different thresholds
    sampling_strategies = [
        "auto",
        # Balance all classes up to the median frequency
        {i: int(np.median([Counter(y_train)[j] for j in range(10)])) for i in range(7)},
        # Balance lower classes to match class 7's frequency
        {i: Counter(y_train)[7] for i in range(7)},
        # Custom strategy focusing on very underrepresented classes
        {i: max(Counter(y_train)[i] * 2, 15) for i in range(5)},
    ]

    for k in k_neighbors_range:
        for strategy in sampling_strategies:
            try:
                X_resampled, y_resampled = create_smote_pipeline(
                    X_train, y_train, sampling_strategy=strategy, k_neighbors=k
                )

                # Use cross-validation to evaluate
                scores = cross_val_score(
                    model,
                    X_resampled,
                    y_resampled,
                    cv=cv,
                    scoring=make_scorer(r2_score),
                )

                mean_score = np.mean(scores)

                if mean_score > best_score:
                    best_score = mean_score
                    best_params = {"k_neighbors": k, "sampling_strategy": strategy}
                    print(f"New best score: {mean_score:.4f} with k={k}")

            except ValueError as e:
                print(f"Skipping k={k}, strategy={strategy} due to: {str(e)}")
                continue

    if best_score == float("-inf"):
        print("Warning: No valid parameters found, using defaults")
        return best_params, 0.0

    return best_params, best_score


def main(model, X_train, y_train, X_test, y_test):
    """
    Main function to run SMOTE enhancement analysis
    """
    print("Step 1: Original Data Distribution")
    print("---------------------------------")
    print("Original feature shape:", X_train.shape)
    print("Original target distribution:")
    print(pd.Series(y_train).value_counts().sort_index())

    print("\nStep 2: Optimizing SMOTE Parameters")
    print("---------------------------------")
    best_params, best_cv_score = optimize_smote_parameters(model, X_train, y_train)
    print(f"Best parameters: {best_params}")
    print(f"Best cross-validation R² score: {best_cv_score:.4f}")

    print("\nStep 3: Applying SMOTE with Optimal Parameters")
    print("---------------------------------")
    try:
        X_resampled, y_resampled = create_smote_pipeline(
            X_train,
            y_train,
            sampling_strategy=best_params["sampling_strategy"],
            k_neighbors=best_params["k_neighbors"],
        )
        print("Resampled feature shape:", X_resampled.shape)
        print("\nClass distribution comparison:")
        compare_distributions(y_train, y_resampled)

        print("\nStep 4: Evaluating Impact")
        print("---------------------------------")
        results = evaluate_smote_impact(model, X_train, y_train, X_test, y_test)

        print("\nResults without SMOTE:")
        print(f"MSE: {results['original']['mse']:.4f}")
        print(f"RMSE: {results['original']['rmse']:.4f}")
        print(f"R²: {results['original']['r2']:.4f}")

        print("\nResults with SMOTE:")
        print(f"MSE: {results['smote']['mse']:.4f}")
        print(f"RMSE: {results['smote']['rmse']:.4f}")
        print(f"R²: {results['smote']['r2']:.4f}")

    except Exception as e:
        print(f"Error applying SMOTE: {str(e)}")
        # Return original data if SMOTE fails
        results = {
            "original": {
                "mse": mean_squared_error(
                    y_test, model.fit(X_train, y_train).predict(X_test)
                ),
                "rmse": np.sqrt(
                    mean_squared_error(
                        y_test, model.fit(X_train, y_train).predict(X_test)
                    )
                ),
                "r2": r2_score(y_test, model.fit(X_train, y_train).predict(X_test)),
            },
            "smote": None,
        }
        X_resampled, y_resampled = X_train, y_train

    return {
        "best_params": best_params,
        "best_cv_score": best_cv_score,
        "evaluation_results": results,
        "resampled_data": (X_resampled, y_resampled),
    }


def main(model, X_train, y_train, X_test, y_test):
    """
    Main function to run SMOTE enhancement analysis
    """
    print("Step 1: Original Data Distribution")
    print("---------------------------------")
    print("Original feature shape:", X_train.shape)
    print("Original target distribution:")
    print(pd.Series(y_train).value_counts().sort_index())

    print("\nStep 2: Optimizing SMOTE Parameters")
    print("---------------------------------")
    best_params, best_cv_score = optimize_smote_parameters(model, X_train, y_train)
    print(f"Best parameters: {best_params}")
    print(f"Best cross-validation R² score: {best_cv_score:.4f}")

    print("\nStep 3: Applying SMOTE with Optimal Parameters")
    print("---------------------------------")
    X_resampled, y_resampled = create_smote_pipeline(
        X_train,
        y_train,
        sampling_strategy=best_params["sampling_strategy"],
        k_neighbors=best_params["k_neighbors"],
    )
    print("Resampled feature shape:", X_resampled.shape)
    print("\nClass distribution comparison:")
    compare_distributions(y_train, y_resampled)

    print("\nStep 4: Evaluating Impact")
    print("---------------------------------")
    results = evaluate_smote_impact(model, X_train, y_train, X_test, y_test)

    print("\nResults without SMOTE:")
    print(f"MSE: {results['original']['mse']:.4f}")
    print(f"RMSE: {results['original']['rmse']:.4f}")
    print(f"R²: {results['original']['r2']:.4f}")

    print("\nResults with SMOTE:")
    print(f"MSE: {results['smote']['mse']:.4f}")
    print(f"RMSE: {results['smote']['rmse']:.4f}")
    print(f"R²: {results['smote']['r2']:.4f}")

    return {
        "best_params": best_params,
        "best_cv_score": best_cv_score,
        "evaluation_results": results,
        "resampled_data": (X_resampled, y_resampled),
    }
