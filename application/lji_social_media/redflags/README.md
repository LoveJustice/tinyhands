## Original RedFlag Model (redflag_model.py)

### Overview
This script implements an advanced machine learning pipeline for predicting monitor scores using a stacked ensemble approach. The model combines polynomial features, feature selection, and multiple regression algorithms to create a robust prediction system.

### Key Components

#### Data Processing
- Utilizes pre-split data (train/holdout) from a previous data splitting script
- Works with predefined data columns specified in `claude_prompts.RED_FLAGS`
- Implements feature engineering through polynomial features (degree 2)
- Handles missing values using mean imputation
- Applies standard scaling to normalize features

#### Model Architecture
The pipeline consists of several key stages:
1. **Feature Processing**
   - Polynomial feature generation (degree 2)
   - Mean imputation for missing values
   - Standard scaling of features

2. **Feature Selection**
   - Recursive Feature Elimination (RFE)
   - Uses SVR with linear kernel as the base estimator
   - Selects top 10 most important features

3. **Stacked Ensemble**
   - First layer:
     - Gradient Boosting Regressor
     - Random Forest Regressor
   - Meta-learner:
     - Support Vector Regression (SVR)

### Hyperparameter Optimization
- Implements RandomizedSearchCV for hyperparameter tuning
- Optimizes parameters for both base models and meta-learner
- Parameters optimized include:
  - Number of estimators (100-500)
  - Learning rates (0.01-0.3)
  - Tree depths (3-10)
  - Minimum samples for splits and leaves
  - SVR parameters (C and epsilon)

### Model Evaluation
The script provides comprehensive evaluation through:
- Mean Squared Error (MSE)
- Root Mean Squared Error (RMSE)
- R-squared (R²) metrics
- Feature importance analysis using permutation importance
- Detailed holdout set predictions with ID mapping

### Feature Importance Analysis
- Calculates permutation importance for features
- Generates visualizations:
  - Complete feature importance plots
  - Top 20 features analysis
- Saves detailed CSV reports and visualizations

### Output and Artifacts
The script generates several outputs:
1. **Model Files**
   - Saved model pickle file (`models/final_{model_id}.pkl`)
   - Detailed metrics JSON (`results/metrics_{model_id}.json`)

2. **Predictions**
   - Holdout set predictions with original IDs
   - Saved as CSV (`results/holdout_predictions_{model_id}.csv`)

3. **Feature Importance Analysis**
   - CSV reports of feature importance
   - Visualization plots (all features and top 20)
   - Summary JSON files

### Usage
The script is designed to be run as a standalone Python program:
```bash
python redflag_model.py
```

### Dependencies
- pandas
- numpy
- scikit-learn
- scipy
- matplotlib (for visualizations)
- custom libraries (claude_prompts)

### Model Workflow
1. Loads split data from specified timestamp
2. Performs hyperparameter optimization on training data
3. Evaluates model on holdout set
4. Trains final model on complete dataset
5. Generates and saves feature importance analysis
6. Saves model and all relevant metrics

### Notes
- The model generates a unique identifier for each run
- All results are timestamped and saved with model ID
- Feature importance analysis is performed for both holdout and final models
- The pipeline is designed to handle the specific requirements of the RedFlag scoring system

## Simplified RedFlag Model (simplified_redflag_model.py)

### Overview
This script implements a streamlined version of the original RedFlag model, focusing on essential preprocessing and ensemble methods while removing some of the complexity of the original implementation. This version prioritizes robustness and interpretability over complex feature engineering.

### Key Differences from Original Model

#### Simplified Architecture
1. **Removed Components**
   - Eliminated polynomial feature generation
   - Removed Recursive Feature Elimination (RFE)
   - Replaced SVR with Gradient Boosting as final estimator

2. **Streamlined Pipeline**
   - Simpler preprocessing steps
   - More straightforward feature handling
   - Reduced hyperparameter search space

#### Feature Processing Comparison

| Original Model | Simplified Model |
|---------------|------------------|
| Polynomial Features | Basic Features Only |
| RFE Feature Selection | No Feature Selection |
| SVR Meta-learner | Gradient Boosting Meta-learner |
| Complex Feature Engineering | Basic Preprocessing |

### Advantages
1. **Computational Efficiency**
   - Faster training times due to simpler architecture
   - Reduced memory usage without polynomial features
   - More efficient hyperparameter optimization

2. **Maintainability**
   - Clearer code structure
   - Easier to debug and modify
   - More straightforward feature importance interpretation

3. **Robustness**
   - Less prone to overfitting
   - More stable across different datasets
   - Better handling of feature correlations

### Disadvantages
1. **Model Capacity**
   - May miss complex feature interactions
   - Potentially lower performance on highly nonlinear relationships
   - Less flexible in feature space exploration

2. **Feature Engineering**
   - No automated feature generation
   - Relies more on raw features
   - May require more manual feature engineering

### Key Components

#### Data Processing
- Uses same pre-split data structure as original model
- Implements basic preprocessing with mean imputation and standard scaling
- Maintains consistent handling of DATA_COLUMNS

#### Model Architecture
The simplified pipeline consists of:
1. **Feature Processing**
   - Mean imputation for missing values
   - Standard scaling of features

2. **Stacked Ensemble**
   - First layer:
     - Gradient Boosting Regressor
     - Random Forest Regressor
   - Meta-learner:
     - Gradient Boosting Regressor

### Hyperparameter Optimization
- Focused parameter space:
  - Number of estimators (100-500)
  - Learning rates (0.01-0.3)
  - Tree depths (3-10)
  - Simplified meta-learner parameters

### Enhanced Feature Importance Analysis
- Improved visualization capabilities
  - Dynamic figure sizing based on feature count
  - Better readability for large feature sets
  - Separate analysis for all features and top 20

### Output and Artifacts
Similar to original model but with enhanced debugging:
1. **Model Files**
   - Model pickle file (`models/final_{model_id}.pkl`)
   - Comprehensive metrics JSON
   - Detailed debugging information

2. **Analysis Outputs**
   - Enhanced feature importance visualizations
   - Detailed ranking reports in multiple formats
   - Improved CSV exports with proper ID handling

### Usage
```bash
python simplified_redflag_model.py
```

### Dependencies
Same as original model, excluding polynomial feature-related libraries.

### Model Workflow
1. Loads and validates split data
2. Performs streamlined hyperparameter optimization
3. Conducts holdout evaluation
4. Trains final model on complete dataset
5. Generates enhanced feature importance analysis
6. Saves model and metrics with improved debugging information

### Notes
- More robust ID handling throughout the pipeline
- Enhanced error checking and debugging output
- Improved visualization and reporting capabilities
- Better memory management for large datasets

### Recommendation for Use
The simplified model is recommended when:
- Quick iterations are needed
- Dataset size is large
- Interpretability is a priority
- Basic feature relationships are sufficient

The original model might be preferred when:
- Complex feature interactions are crucial
- Maximum model performance is required
- Computational resources are not a constraint

## Deep Learning RedFlag Model (redflag_ml_deeplearning.py)

### Overview
This script implements a neural network-based approach to the RedFlag prediction system, utilizing modern deep learning techniques including residual connections and advanced regularization. This version represents a significant departure from the traditional machine learning approaches used in the previous models.

### Key Differences from Previous Models

#### Architecture Comparison

| Feature | Original Model | Simplified Model | Deep Learning Model |
|---------|---------------|------------------|-------------------|
| Base Algorithm | Stacking with SVR | Stacking with GBM | Neural Network |
| Feature Engineering | Polynomial | Basic | Learned Representations |
| Feature Selection | RFE | None | Implicit through layers |
| Model Structure | Pipeline | Pipeline | Residual Network |

### Neural Network Architecture

1. **Input Layer**
   - Layer Normalization
   - Direct feature input

2. **Embedding Layer**
   - Initial dimensionality expansion
   - Normalization and ReLU activation
   - Dropout regularization

3. **Residual Blocks**
   - Skip connections for better gradient flow
   - Dual linear transformations
   - Layer normalization
   - Dropout for regularization

4. **Deep Network Layers**
   - Progressively reducing dimensions [256, 128, 64]
   - Layer normalization at each stage
   - ReLU activations
   - Dropout regularization

5. **Output Layer**
   - Single unit with ReLU activation
   - Ensures non-negative predictions

### Advantages

1. **Learning Capability**
   - Automatically discovers feature interactions
   - Can capture non-linear relationships
   - Learns hierarchical representations

2. **Flexibility**
   - Adaptable to different data distributions
   - Handles complex patterns
   - Scale-invariant through normalization

3. **Modern Architecture**
   - Residual connections prevent vanishing gradients
   - Layer normalization for stable training
   - Advanced regularization techniques

### Disadvantages

1. **Complexity**
   - More hyperparameters to tune
   - Requires more training data
   - Longer training time

2. **Resource Requirements**
   - GPU acceleration recommended
   - Higher memory usage
   - More computational intensity

3. **Interpretability**
   - Less transparent than traditional models
   - Feature importance through gradients
   - More complex to explain

### Training Process

1. **Data Handling**
   - Custom TabularDataset class
   - Mini-batch processing
   - GPU acceleration support

2. **Training Features**
   - Early stopping
   - Learning rate scheduling
   - Gradient clipping
   - AdamW optimizer with weight decay

### Model Evaluation
- Consistent metrics with previous models (MSE, RMSE, R²)
- Feature importance through gradient analysis
- Detailed holdout set evaluation

### Implementation Details

#### Key Components
```python
class DeepTabularRegressor(nn.Module):
    # Hidden dimensions: [256, 128, 64]
    # Residual blocks: 2
    # Dropout: 0.1
```

#### Training Parameters
- Batch size: 32
- Learning rate: 1e-3
- Early stopping patience: 10
- Weight decay: 0.01

### Usage
```bash
python redflag_ml_deeplearning.py
```

### Dependencies
- PyTorch
- Basic ML libraries (numpy, pandas)
- Standard data processing libraries
- CUDA support (optional but recommended)

### Recommendation for Use
The deep learning model is recommended when:
- Large amounts of training data are available
- GPU resources are accessible
- Complex, non-linear patterns are suspected
- Maximum predictive performance is prioritized over interpretability

### Integration with Existing Pipeline
- Uses same data splitting approach
- Compatible output format
- Consistent metric reporting
- Similar feature importance visualization

### Notes
- Requires more careful monitoring during training
- Benefits from GPU acceleration
- More sensitive to hyperparameter choices
- Provides alternative perspective on feature relationships

This implementation represents a modern deep learning approach to the RedFlag prediction problem, offering different tradeoffs compared to the traditional machine learning models. Its success depends heavily on data volume and computational resources available.
