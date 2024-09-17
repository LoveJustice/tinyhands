import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import RFE
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import spearmanr
import datetime
import uuid

data_columns = [
    "assure_prompt",
    "bypass_prompt",
    "callback_request_prompt",
    "false_organization_prompt",
    "gender_specific_prompt",
    "illegal_activities_prompt",
    "immediate_hiring_prompt",
    "language_switch_prompt",
    "multiple_provinces_prompt",
    "no_education_skilled_prompt",
    "no_location_prompt",
    "quick_money_prompt",
    "recruit_students_prompt",
    "suspicious_email_prompt",
    "target_specific_group_prompt",
    "unprofessional_writing_prompt",
    "unrealistic_hiring_number_prompt",
    "unusual_hours_prompt",
    "vague_description_prompt",
    "wrong_link_prompt",
]


def load_and_preprocess_data(file_path):
    model_data = pd.read_csv(file_path)
    model_data = model_data[~(model_data["monitor_score"] == "unknown")]
    mapping = {"yes": 1, "no": 0}
    df = model_data.replace(mapping)
    # df.loc[df.IDn == 572651, "monitor_score"] = 1
    return df[data_columns], df["monitor_score"]


def create_model_pipeline():
    return Pipeline(
        [
            (
                "features",
                ColumnTransformer(
                    [
                        ("num", SimpleImputer(strategy="mean"), data_columns),
                        (
                            "poly",
                            PolynomialFeatures(degree=2, include_bias=False),
                            data_columns,
                        ),
                    ]
                ),
            ),
            ("regressor", GradientBoostingRegressor(random_state=42)),
        ]
    )


def train_and_evaluate_model(X, y, pipeline):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    # X_train, X_test, y_train, y_test = (
    #     X[test_train == "train"],
    #     X[test_train == "test"],
    #     y[test_train == "train"],
    #     y[test_train == "test"],
    # )

    pipeline.fit(X_train, y_train)

    y_pred_train = pipeline.predict(X_train)
    y_pred_test = pipeline.predict(X_test)

    train_mse = mean_squared_error(y_train, y_pred_train)
    test_mse = mean_squared_error(y_test, y_pred_test)
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)

    print(f"Train MSE: {train_mse:.4f}, Test MSE: {test_mse:.4f}")
    print(f"Train R2: {train_r2:.4f}, Test R2: {test_r2:.4f}")

    return pipeline, X_test, y_test


from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import uniform, randint


def tune_hyperparameters(pipeline, X, y):
    param_distributions = {
        "regressor__gb__n_estimators": randint(100, 500),
        "regressor__gb__learning_rate": uniform(0.01, 0.3),
        "regressor__gb__max_depth": randint(3, 10),
        "regressor__gb__min_samples_split": randint(2, 20),
        "regressor__gb__min_samples_leaf": randint(1, 10),
        "regressor__rf__n_estimators": randint(100, 500),
        "regressor__rf__max_depth": randint(3, 20),
        "regressor__rf__min_samples_split": randint(2, 20),
        "regressor__rf__min_samples_leaf": randint(1, 10),
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
    )
    random_search.fit(X, y)

    print("Best parameters:", random_search.best_params_)
    print("Best cross-validation score:", -random_search.best_score_)

    return random_search.best_estimator_


def create_advanced_pipeline():
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
                            data_columns,
                        ),
                        (
                            "poly",
                            PolynomialFeatures(degree=2, include_bias=False),
                            data_columns,
                        ),
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
                    [
                        ("gb", GradientBoostingRegressor(random_state=42)),
                        ("rf", RandomForestRegressor(random_state=42)),
                    ],
                    final_estimator=SVR(),
                ),
            ),
        ]
    )


def generate_unique_filename(prefix="adverts_sample", extension="csv"):
    # Get current timestamp in ISO 8601 format
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Generate a short random string
    random_string = uuid.uuid4().hex[:6]

    # Combine components
    filename = f"{prefix}_{timestamp}_{random_string}.{extension}"

    return filename


def main():
    # file_path1 = "results/advert_flags.csv"
    file_path = "results/advert_flags.csv"
    advert_flags = pd.read_csv(file_path)
    advert_flags = advert_flags[~(advert_flags["monitor_score"] == "unknown")]
    # Create the results DataFrame
    results = pd.DataFrame(
        columns=[
            "advert",
            "group_id",
            "post_id",
            "monitor_score",
            "test_train",
        ],
        index=advert_flags.index,
    )

    X, y = load_and_preprocess_data(file_path)
    # pipeline = create_model_pipeline()
    # best_pipeline = tune_hyperparameters(pipeline, X, y)
    # trained_pipeline, X_test, y_test = train_and_evaluate_model(X, y, best_pipeline)
    # Populate the results DataFrame
    results["advert"] = advert_flags["advert"]
    results["group_id"] = advert_flags["group_id"]
    results["post_id"] = advert_flags["post_id"]
    results["monitor_score"] = advert_flags["monitor_score"]
    results["test_train"] = "train"

    # trained_pipeline, X_test, y_test = train_and_evaluate_model(X, y, pipeline)
    advanced_pipeline = create_advanced_pipeline()

    best_advanced_pipeline = tune_hyperparameters(advanced_pipeline, X, y)
    trained_pipeline, X_test, y_test = train_and_evaluate_model(
        X, y, best_advanced_pipeline
    )
    # Additional analysis can be added here
    results.loc[results.index.isin(X_test.index), "test_train"] = "test"
    new_model_predictions_test = trained_pipeline.predict(X_test)
    new_model_predictions_all = trained_pipeline.predict(X)

    results["model_predictions"] = new_model_predictions_all

    # Update old_model_predictions for both train and test

    # Assuming you have predictions from both models on the same test set
    mean_squared_error(y, advert_flags["monitor_score"])
    mse_new = mean_squared_error(y_test, new_model_predictions_test)

    mean_squared_error(y, new_model_predictions_all)
    mean_squared_error(y, advert_flags["monitor_score"])
    print(f"New model MSE: {mse_new}")

    # You can also compute R-squared for both models
    r2_new = r2_score(y_test, new_model_predictions_test)

    new_model_correlation = np.corrcoef(y_test, new_model_predictions_test)[0, 1]

    new_model_spearman_correlation, new_model_p_value = spearmanr(
        y_test, new_model_predictions_test
    )
    print(
        f"New model spearman : {new_model_spearman_correlation} with p-value {new_model_p_value}"
    )
    print(
        f"Old model spearman : {old_model_spearman_correlation} with p-value {old_model_p_value}"
    )

    print(f"New model R-squared: {r2_new}")

    unique_filename = generate_unique_filename(
        prefix="redflag_model_result", extension="csv"
    )
    results = results.set_index("post_id").loc[advert_flags["post_id"]].reset_index()
    results.to_csv(f"results/{unique_filename}")


if __name__ == "__main__":
    main()
