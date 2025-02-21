
---

# Model Build Documentation

This document provides a comprehensive overview of the `model_build.py` file. It explains the code’s purpose, how it works, required dependencies, configuration details, deployment instructions, and guidance for future enhancements.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Dependencies](#dependencies)
- [Setup and Configuration](#setup-and-configuration)
- [Code Structure and Key Functions](#code-structure-and-key-functions)
- [Deployment and Execution](#deployment-and-execution)
- [Usage](#usage)
- [Customization and Future Work](#customization-and-future-work)
- [Troubleshooting](#troubleshooting)
- [Conclusion](#conclusion)

---

## Overview

`model_build.py` is a Python script designed to:

- **Load** case data from Google Drive.
- **Preprocess** data by filtering out recent cases based on a configurable cutoff date.
- **Split** data into training, testing, and validation sets.
- **Build** and **train** a machine learning model using a scikit-learn pipeline with a Random Forest classifier.
- **Optimize** the model via grid search cross-validation.
- **Evaluate** the model using metrics such as ROC-AUC, Accuracy, Precision, Recall, and F1 Score.
- **Visualize** model performance (ROC curves, feature importance charts, decision tree rules) using Altair and Streamlit.
- **Deploy** by saving trained models and related artifacts back to Google Drive.

This script is integrated with Streamlit, providing an interactive web interface for model building and evaluation.

---

## Features

- **Data Integration:**  
  Connects to Google Drive to load and save data using OAuth2 credentials.

- **Data Preprocessing:**  
  Filters out cases based on recency and splits the dataset into training and testing sets.

- **Model Training:**  
  Constructs a machine learning pipeline and uses grid search cross-validation to optimize a Random Forest classifier.

- **Evaluation Metrics:**  
  Computes key performance metrics and plots ROC curves to evaluate model performance.

- **Visualization:**  
  Displays feature importances and decision tree rules interactively using Altair and Streamlit.

- **Cloud Deployment:**  
  Saves trained model artifacts and validation data to Google Drive for reproducibility and future use.

---

## Dependencies

To run `model_build.py`, the following packages must be installed:

- **Python 3.7+**
- [Pandas](https://pandas.pydata.org/)
- [NumPy](https://numpy.org/)
- [scikit-learn](https://scikit-learn.org/)
- [Streamlit](https://streamlit.io/)
- [Altair](https://altair-viz.github.io/)
- [altair_saver](https://github.com/altair-viz/altair_saver)
- [vl_convert](https://github.com/datadesk/vl-convert)
- [Google API Python Client](https://developers.google.com/api-client-library/python)
- [oauth2client](https://github.com/google/oauth2client)
- [Matplotlib](https://matplotlib.org/)

Install the dependencies via pip:

```bash
pip install pandas numpy scikit-learn streamlit altair altair_saver vl_convert google-api-python-client oauth2client matplotlib
```

Additionally, this script relies on two local libraries:
- `libraries.case_dispatcher_model` (provides `get_cls_pipe`)
- `libraries.google_lib` (provides utilities such as `make_file_bytes`, `save_to_cloud`, `get_file_id`, etc.)

Ensure these are available in your project’s directory structure.

---

## Setup and Configuration

1. **Google Drive Credentials:**

   Configure your Google Drive credentials using Streamlit’s secrets management. For example, add a `secrets.toml` file with the following structure:

   ```toml
   [case_dispatcher]
   access_token = { 
       client_id = "YOUR_CLIENT_ID", 
       client_secret = "YOUR_CLIENT_SECRET", 
       refresh_token = "YOUR_REFRESH_TOKEN", 
       token_expiry = "YOUR_TOKEN_EXPIRY" 
   }
   ```

   The script uses these credentials to generate OAuth2 credentials for accessing Google Drive.

2. **Local Libraries:**

   Ensure that the following local libraries are in your project:
   - `libraries/case_dispatcher_model.py`
   - `libraries/google_lib.py`

3. **Directory Structure:**

   The script automatically creates a `plots` directory (if not already present) to store generated charts. Make sure your project has the necessary write permissions in the working directory.

---

## Code Structure and Key Functions

### Data Processing Functions

- **`remove_recent(soc_df, cutoff_days)`**  
  Filters out cases with an `interview_date` more recent than the cutoff days unless an arrest was recorded.

- **`train_test_val_split(sub_df, test_size=0.2)`**  
  Splits the data into training and testing sets, separating out the target variable (`arrested`).

### Model Training Functions

- **`do_gridsearch(cls_pipeline, X_train, y_train)`**  
  Executes grid search cross-validation over a parameter space for the Random Forest classifier.

- **`full_gridsearch_pipe(soc_df, cutoff_days=90)`**  
  Combines data filtering, splitting, and grid search to output the best model, feature names, and validation sets.

### Prediction and Evaluation Functions

- **`make_new_predictions(X, soc_model)`**  
  Uses the trained model to generate probability predictions for new data.

- **`plot_roc_curve_altair(y_true, model_predictions, model_names)`**  
  Generates and saves an interactive ROC curve plot using Altair.

### Visualization Functions

- **`display_feature_importances(model, feature_names)`**  
  Creates and displays a feature importance chart in the Streamlit interface.

- **`display_first_tree_rules(model, feature_names)`**  
  Extracts and shows the decision rules of the first tree from the Random Forest ensemble.

### Utility Functions

- **`load_data()`**  
  Loads the case data from Google Drive using the configured credentials.

- **`save_model_to_cloud(model_obj, model_name, drive_service)`**  
  Saves model artifacts (or other objects) to Google Drive.

### Main Function

- **`main()`**  
  Orchestrates the full workflow: loads data, builds the model, evaluates performance, and displays interactive charts and metrics in Streamlit.

---

## Deployment and Execution

### Running Locally

1. **Navigate to the project directory** where `model_build.py` is located.

2. **Run the Streamlit app:**

   ```bash
   streamlit run model_build.py
   ```

3. **Interact with the UI:**
   - Use the sidebar to set the cutoff days.
   - Click the "Build model" button to execute the entire pipeline.
   - View feature importances, ROC curves, decision tree rules, and performance metrics.

### Deploying to Production

- **Streamlit Cloud:**  
  Deploy directly using [Streamlit Cloud](https://streamlit.io/cloud) by connecting your GitHub repository.

- **Other Platforms:**  
  Use platforms like Heroku or your own server. Ensure that all environment variables (especially for Google Drive credentials) are properly configured in your deployment environment.

- **Environment Configuration:**  
  In production, verify that:
  - The `st.secrets` configuration is correctly set.
  - The required local libraries are accessible.
  - Write permissions exist for saving plots and model artifacts.

---

## Usage

- **Selecting Data Cutoff:**  
  Use the sidebar slider to choose the number of days for filtering out recent cases. This ensures only relevant data is used for training.

- **Building the Model:**  
  Click on the "Build model" button. This triggers:
  - Data loading from Google Drive.
  - Data preprocessing and splitting.
  - Model training with grid search optimization.
  - Evaluation and generation of performance metrics.

- **Viewing Results:**  
  The app displays:
  - Feature importance charts.
  - ROC curve plots.
  - Decision tree rules (from the first tree in the ensemble).
  - Key performance metrics (ROC-AUC, Accuracy, Precision, Recall, F1 Score).

- **Artifact Saving:**  
  After model building, the model, feature names, and validation datasets are saved back to Google Drive for future reference.

---

## Customization and Future Work

- **Parameter Adjustments:**  
  The grid search parameters in `do_gridsearch()` can be tuned further. Consider experimenting with additional hyperparameters or classifiers.

- **Extended Visualizations:**  
  You may integrate more sophisticated visualizations or dashboards to display other aspects of model performance.

- **Additional Models:**  
  Future enhancements could include multiple model types and ensemble strategies beyond Random Forest.

- **Logging and Monitoring:**  
  Integrate logging mechanisms (e.g., using Python’s `logging` module) to capture detailed run-time information.

---

## Troubleshooting

- **Credential Issues:**  
  Verify that the Google Drive credentials in `st.secrets` are valid and correctly configured.

- **Missing Modules:**  
  Ensure local libraries (`libraries.case_dispatcher_model` and `libraries.google_lib`) are in the correct paths relative to `model_build.py`.

- **Deployment Errors:**  
  Review the logs for detailed error messages. Confirm that all environment variables and permissions are properly set, especially for file writing and Google Drive access.

- **Data Format Issues:**  
  Check that your input data contains the expected columns (e.g., `interview_date`, `arrested`) and that date fields are in a parseable format.

---

## Conclusion

`model_build.py` provides an end-to-end solution for data loading, model building, evaluation, and deployment, all integrated within an interactive Streamlit interface. This documentation should enable future engineers to understand the architecture, configure the environment, and deploy the solution successfully. For further details, refer to inline comments and function docstrings within the code.

