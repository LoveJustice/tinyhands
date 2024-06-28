import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler

# Load the dataset
file_path = "results/advert_comparison_cleaned.csv"  # Update the path if necessary
df = pd.read_csv(file_path)

# Prepare the dependent variable
y = df["Monitor Rating"]

# Prepare the independent variables (binary columns)
X = df.iloc[:, 6:]

# Remove constant columns if any
constant_columns = [col for col in X.columns if X[col].nunique() <= 1]
X = X.drop(columns=constant_columns)

# Standardize the predictors
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# Define the parameter grid
param_grid = {
    "max_depth": [2, 4, 6, 8, 10],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
}

# Initialize the decision tree classifier
dt = DecisionTreeClassifier(random_state=42)

# Set up the grid search
grid_search = GridSearchCV(
    estimator=dt, param_grid=param_grid, cv=5, n_jobs=-1, scoring="accuracy"
)

# Fit the grid search to the data
grid_search.fit(X_train, y_train)

# Get the best parameters and the best estimator
best_params = grid_search.best_params_
best_estimator = grid_search.best_estimator_

# Evaluate the best estimator on the test set
y_pred_best = best_estimator.predict(X_test)
accuracy_best = accuracy_score(y_test, y_pred_best)
conf_matrix_best = confusion_matrix(y_test, y_pred_best)
class_report_best = classification_report(y_test, y_pred_best)

print("Best Parameters:", best_params)
print(f"Accuracy: {accuracy_best}")
print("Confusion Matrix:")
print(conf_matrix_best)
print("Classification Report:")
print(class_report_best)

df["Predicted Rating"] = best_estimator.predict(X_scaled)

# Save the DataFrame with predicted ratings
df.to_csv("predicted_ratings.csv", index=False)

# Display the DataFrame with actual and predicted ratings
print(df[["Monitor Rating", "Predicted Rating"]])

# ====================================================================================
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.utils import resample
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler

# Load the dataset
file_path = "results/advert_comparison_cleaned.csv"  # Update the path if necessary
df = pd.read_csv(file_path)

# Prepare the dependent variable
y = df["Monitor Rating"]

# Prepare the independent variables (binary columns)
X = df.iloc[:, 6:]

# Remove constant columns if any
constant_columns = [col for col in X.columns if X[col].nunique() <= 1]
X = X.drop(columns=constant_columns)

# Standardize the predictors
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# Define the parameter grid
param_grid = {
    "max_depth": [2, 4, 6, 8, 10],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
}

# Initialize the decision tree classifier
dt = DecisionTreeClassifier(random_state=42)

# Set up the grid search
grid_search = GridSearchCV(
    estimator=dt, param_grid=param_grid, cv=5, n_jobs=-1, scoring="accuracy"
)

# Fit the grid search to the data
grid_search.fit(X_train, y_train)

# Get the best estimator
best_estimator = grid_search.best_estimator_

# Predict ratings for all rows using the best estimator
df["Predicted Rating"] = best_estimator.predict(X_scaled)

# Bootstrapping to estimate confidence intervals
n_bootstraps = 1000
bootstrap_preds = np.zeros((n_bootstraps, len(df)))

for i in range(n_bootstraps):
    # Resample the data
    X_resampled, y_resampled = resample(X_scaled, y, random_state=i)

    # Train the model on the resampled data
    best_estimator.fit(X_resampled, y_resampled)

    # Predict on the entire dataset
    bootstrap_preds[i] = best_estimator.predict(X_scaled)

# Calculate the 95% confidence intervals
lower_bounds = np.percentile(bootstrap_preds, 2.5, axis=0)
upper_bounds = np.percentile(bootstrap_preds, 97.5, axis=0)

# Add confidence intervals to the DataFrame
df["Lower Bound"] = lower_bounds
df["Upper Bound"] = upper_bounds

# Save the DataFrame with predicted ratings and confidence intervals
df.to_csv(
    "results/decision_tree_predicted_ratings_with_confidence_intervals.csv", index=False
)

# Display the DataFrame with actual and predicted ratings and confidence intervals
print(df[["Monitor Rating", "Predicted Rating", "Lower Bound", "Upper Bound"]])
