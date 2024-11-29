import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import make_scorer, mean_squared_error, r2_score
from scipy import stats
from imblearn.over_sampling import SMOTE, ADASYN
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict


def analyze_feature_distributions(X, feature_names):
    """Analyze and visualize feature distributions and sparsity"""

    # Calculate basic statistics
    stats_df = pd.DataFrame(
        {
            "feature": feature_names,
            "count": [X[col].sum() for col in feature_names],
            "sparsity": [1 - (X[col].sum() / len(X)) for col in feature_names],
            "unique_values": [len(X[col].unique()) for col in feature_names],
        }
    )

    # Sort by sparsity
    stats_df = stats_df.sort_values("sparsity", ascending=False)

    # Create visualizations
    plt.figure(figsize=(15, 10))
    sns.barplot(data=stats_df, x="sparsity", y="feature")
    plt.title("Feature Sparsity Analysis")
    plt.tight_layout()
    plt.savefig("feature_sparsity.png")
    plt.close()

    # Create feature presence heatmap
    presence_matrix = X[feature_names].astype(bool).astype(int)
    plt.figure(figsize=(20, 10))
    sns.heatmap(
        presence_matrix.iloc[:50],  # Show first 50 samples
        xticklabels=feature_names,
        yticklabels=False,
        cmap="YlOrRd",
    )
    plt.title("Feature Presence Patterns (First 50 Samples)")
    plt.tight_layout()
    plt.savefig("feature_patterns.png")
    plt.close()

    return stats_df


def analyze_feature_importance(X, y, feature_names):
    """Analyze feature importance and correlation with target"""

    correlations = pd.DataFrame(
        {
            "feature": feature_names,
            "correlation": [abs(X[col].corr(y)) for col in feature_names],
            "mutual_info": mutual_info_regression(X, y),
        }
    ).sort_values("correlation", ascending=False)

    # Visualize correlations
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=correlations, x="correlation", y="mutual_info")
    for i, row in correlations.iterrows():
        plt.annotate(row["feature"], (row["correlation"], row["mutual_info"]))
    plt.title("Feature Importance Analysis")
    plt.tight_layout()
    plt.savefig("feature_importance.png")
    plt.close()

    return correlations


def evaluate_balancing_strategies(X, y, feature_names, model):
    """Evaluate different balancing strategies"""

    results = defaultdict(dict)

    # Original baseline
    base_scores = cross_val_score(model, X, y, cv=5, scoring="r2")
    results["baseline"] = {
        "mean_score": base_scores.mean(),
        "std_score": base_scores.std(),
    }

    # Strategy 1: Remove very sparse features
    sparse_threshold = 0.95  # Features present in less than 5% of samples
    sparse_features = [
        f for f in feature_names if (1 - X[f].sum() / len(X)) > sparse_threshold
    ]
    X_no_sparse = X.drop(columns=sparse_features)
    scores = cross_val_score(model, X_no_sparse, y, cv=5, scoring="r2")
    results["remove_sparse"] = {
        "mean_score": scores.mean(),
        "std_score": scores.std(),
        "removed_features": sparse_features,
    }

    # Strategy 2: SMOTE
    try:
        smote = SMOTE(random_state=42)
        X_smote, y_smote = smote.fit_resample(X, y)
        scores = cross_val_score(model, X_smote, y_smote, cv=5, scoring="r2")
        results["smote"] = {"mean_score": scores.mean(), "std_score": scores.std()}
    except Exception as e:
        results["smote"] = {"error": str(e)}

    # Strategy 3: ADASYN
    try:
        adasyn = ADASYN(random_state=42)
        X_adasyn, y_adasyn = adasyn.fit_resample(X, y)
        scores = cross_val_score(model, X_adasyn, y_adasyn, cv=5, scoring="r2")
        results["adasyn"] = {"mean_score": scores.mean(), "std_score": scores.std()}
    except Exception as e:
        results["adasyn"] = {"error": str(e)}

    # Strategy 4: Feature grouping (example with semantic grouping)
    feature_groups = {
        "location_related": [
            "drop_off_at_secure_location_prompt",
            "no_location_prompt",
            "multiple_provinces_prompt",
        ],
        "communication": [
            "callback_request_prompt",
            "suspicious_email_prompt",
            "language_switch_prompt",
        ],
        "hiring_process": [
            "immediate_hiring_prompt",
            "requires_references",
            "unrealistic_hiring_number_prompt",
        ],
        "targeting": [
            "gender_specific_prompt",
            "target_specific_group_prompt",
            "recruit_students_prompt",
        ],
        "job_details": [
            "vague_description_prompt",
            "unusual_hours_prompt",
            "overseas_prompt",
        ],
    }

    X_grouped = X.copy()
    for group_name, features in feature_groups.items():
        X_grouped[group_name] = X[features].sum(axis=1)
        X_grouped = X_grouped.drop(columns=features)

    scores = cross_val_score(model, X_grouped, y, cv=5, scoring="r2")
    results["feature_grouping"] = {
        "mean_score": scores.mean(),
        "std_score": scores.std(),
        "groups": feature_groups,
    }

    return results


def visualize_results(results):
    """Visualize comparison of different strategies"""

    # Prepare data for plotting
    strategies = []
    means = []
    stds = []

    for strategy, metrics in results.items():
        if "mean_score" in metrics:
            strategies.append(strategy)
            means.append(metrics["mean_score"])
            stds.append(metrics["std_score"])

    # Create comparison plot
    plt.figure(figsize=(12, 6))
    bars = plt.bar(strategies, means)
    plt.errorbar(strategies, means, yerr=stds, fmt="none", color="black", capsize=5)

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.3f}",
            ha="center",
            va="bottom",
        )

    plt.title("Performance Comparison of Different Strategies")
    plt.ylabel("R² Score")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("strategy_comparison.png")
    plt.close()


def main_analysis(X, y, feature_names, model):
    """Run complete analysis pipeline"""

    print("1. Analyzing Feature Distributions...")
    distribution_stats = analyze_feature_distributions(X, feature_names)
    print("\nFeature Statistics:")
    print(distribution_stats)

    print("\n2. Analyzing Feature Importance...")
    importance_analysis = analyze_feature_importance(X, y, feature_names)
    print("\nFeature Importance:")
    print(importance_analysis)

    print("\n3. Evaluating Balancing Strategies...")
    strategy_results = evaluate_balancing_strategies(X, y, feature_names, model)
    print("\nStrategy Results:")
    for strategy, results in strategy_results.items():
        print(f"\n{strategy}:")
        print(results)

    print("\n4. Visualizing Results...")
    visualize_results(strategy_results)

    return {
        "distribution_stats": distribution_stats,
        "importance_analysis": importance_analysis,
        "strategy_results": strategy_results,
    }
