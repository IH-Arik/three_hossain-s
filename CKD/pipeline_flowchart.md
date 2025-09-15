# CKD Prediction Pipeline Flowchart

## Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                START                                            │
└─────────────────────┬───────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        1. DATA LOADING                                         │
│  ┌─────────────────┐    ┌─────────────────┐                                   │
│  │ Kidney Disease  │    │   PONE Dataset  │                                   │
│  │   (CSV File)    │    │   (Excel File)  │                                   │
│  └─────────────────┘    └─────────────────┘                                   │
└─────────────────────┬───────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        2. DATA PREPROCESSING                                   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    preprocess_dataset()                                 │   │
│  │                                                                         │   │
│  │  • Drop ID column                                                      │   │
│  │  • Handle target variable encoding                                     │   │
│  │  • Clean missing values ('?' → NaN)                                   │   │
│  │  • Convert data types                                                  │   │
│  │  • Analyze skewness                                                    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        3. COLUMN TRANSFORMER                                    │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    ColumnTransformer                                    │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │   Standard      │  │    MinMax       │  │    Robust       │        │   │
│  │  │   Scaled        │  │    Scaled       │  │    Scaled       │        │   │
│  │  │   Features      │  │    Features     │  │    Features     │        │   │
│  │  │                 │  │                 │  │                 │        │   │
│  │  │ • age, bp       │  │ • sg, al, su    │  │ • wc, rc        │        │   │
│  │  │ • hemo, sod     │  │                 │  │                 │        │   │
│  │  │ • pot, pcv      │  │                 │  │                 │        │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │   Quantile      │  │   Binary        │  │   Non-Binary    │        │   │
│  │  │   Transformed   │  │   Categorical   │  │   Categorical   │        │   │
│  │  │   Features      │  │   (Ordinal)     │  │   (One-Hot)     │        │   │
│  │  │                 │  │                 │  │                 │        │   │
│  │  │ • bgr, bu, sc   │  │ • rbc, pc, pcc  │  │ • appet         │        │   │
│  │  │ (Highly Skewed) │  │ • ba, htn, dm   │  │                 │        │   │
│  │  │                 │  │ • cad, pe, ane  │  │                 │        │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │   │
│  │                                                                         │   │
│  │  Each pipeline: IterativeImputer → Scaler/Transformer                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        4. OUTLIER DETECTION                                     │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    detect_outliers()                                   │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐              ┌─────────────────┐                  │   │
│  │  │ IsolationForest │              │ LocalOutlier    │                  │   │
│  │  │                 │              │ Factor (LOF)    │                  │   │
│  │  │ • contamination │              │                 │                  │   │
│  │  │   = 0.1         │              │ • n_neighbors   │                  │   │
│  │  │ • random_state  │              │   = 20          │                  │   │
│  │  │   = 42          │              │ • contamination │                  │   │
│  │  │                 │              │   = 0.1         │                  │   │
│  │  └─────────────────┘              └─────────────────┘                  │   │
│  │                                                                         │   │
│  │  → Remove outliers from dataset                                        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        5. CLASS BALANCING                                       │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    BorderlineSMOTE                                     │   │
│  │                                                                         │   │
│  │  • sampling_strategy = 'auto'                                          │   │
│  │  • random_state = 42                                                   │   │
│  │  • kind = 'borderline-1'                                               │   │
│  │                                                                         │   │
│  │  → Balance minority and majority classes                               │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        6. TRAIN-TEST SPLIT                                      │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    train_test_split()                                  │   │
│  │                                                                         │   │
│  │  • test_size = 0.2 (20%)                                               │   │
│  │  • random_state = 42                                                   │   │
│  │  • stratify = y_resampled                                              │   │
│  │                                                                         │   │
│  │  → X_train_resampled, X_test_preprocessed                              │   │
│  │  → y_train_resampled, y_test                                           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        7. MODEL TRAINING & HYPERPARAMETER TUNING                │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    RandomizedSearchCV                                  │   │
│  │                                                                         │   │
│  │  For each of 10 classifiers:                                           │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │ Logistic        │  │ Random Forest   │  │ LightGBM        │        │   │
│  │  │ Regression      │  │                 │  │                 │        │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │ XGBoost         │  │ CatBoost        │  │ Gradient        │        │   │
│  │  │                 │  │                 │  │ Boosting        │        │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │   │
│  │  │ Naive Bayes     │  │ KNN             │  │ Extra Trees     │        │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐                                                    │   │
│  │  │ Decision Tree   │                                                    │   │
│  │  └─────────────────┘                                                    │   │
│  │                                                                         │   │
│  │  • n_iter = 10 (hyperparameter combinations)                           │   │
│  │  • cv = 5 (5-fold cross-validation)                                    │   │
│  │  • scoring = 'roc_auc'                                                 │   │
│  │  • n_jobs = -1 (parallel processing)                                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        8. MODEL EVALUATION                                      │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    cross_validate()                                    │   │
│  │                                                                         │   │
│  │  Metrics:                                                               │   │
│  │  • accuracy, f1, recall, precision, roc_auc                            │   │
│  │                                                                         │   │
│  │  → CV Results for all models                                           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    Test Set Evaluation                                 │   │
│  │                                                                         │   │
│  │  • Best model selected by highest Test Accuracy                        │   │
│  │  • Confusion Matrix                                                    │   │
│  │  • ROC Curves                                                          │   │
│  │  • Classification Report                                               │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        9. FEATURE IMPORTANCE & EXPLAINABILITY                   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    SHAP Analysis (if available)                        │   │
│  │                                                                         │   │
│  │  • KernelExplainer                                                     │   │
│  │  • Summary plot                                                        │   │
│  │  • Feature importance plot                                             │   │
│  │  • Force plot (local explanation)                                      │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    LIME Analysis (if available)                        │   │
│  │                                                                         │   │
│  │  • LimeTabularExplainer                                                │   │
│  │  • Local explanation for test instances                                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    Permutation Importance (fallback)                   │   │
│  │                                                                         │   │
│  │  • Used if SHAP is not available                                       │   │
│  │  • Feature importance ranking                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        10. VISUALIZATION & REPORTING                            │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    Generate Plots                                      │   │
│  │                                                                         │   │
│  │  • Class distribution (original & resampled)                           │   │
│  │  • Outlier detection plots                                             │   │
│  │  • Before/after quantile transformation                                │   │
│  │  • Confusion matrices for all models                                   │   │
│  │  • ROC curves for all models                                           │   │
│  │  • Feature importance plots                                            │   │
│  │  • SHAP/LIME explanation plots                                         │   │
│  │                                                                         │   │
│  │  → Save all plots to 'enhanced_ckd_model_plots.pdf'                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        11. MODEL PERSISTENCE                                    │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    Save Best Model                                     │   │
│  │                                                                         │   │
│  │  • enhanced_kd_disease_prediction_model.pkl                            │   │
│  │  • enhanced_pone_disease_prediction_model.pkl                          │   │
│  │                                                                         │   │
│  │  → Using joblib.dump()                                                 │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                END                                              │
└─────────────────────────────────────────────────────────────────────────────────┘

## Key Features of the Pipeline:

### 1. **Robust Preprocessing**
- **IterativeImputer**: Multivariate imputation using RandomForest
- **Multiple Scalers**: Standard, MinMax, Robust scaling based on data characteristics
- **QuantileTransformer**: For highly skewed features
- **Smart Encoding**: Ordinal for binary, One-hot for multi-class categorical

### 2. **Advanced Outlier Handling**
- **IsolationForest**: Primary outlier detection
- **LocalOutlierFactor**: Secondary validation
- **Configurable contamination**: 10% outlier threshold

### 3. **Class Balancing**
- **BorderlineSMOTE**: Advanced SMOTE variant for better synthetic sample generation
- **Maintains data integrity**: Only balances classes, doesn't change feature distributions

### 4. **Comprehensive Model Evaluation**
- **10 Different Algorithms**: From simple to complex
- **Hyperparameter Tuning**: RandomizedSearchCV with 10 iterations
- **5-Fold Cross-Validation**: Robust performance estimation
- **Multiple Metrics**: Accuracy, F1, Recall, Precision, ROC-AUC

### 5. **Explainable AI**
- **SHAP**: Global and local explanations
- **LIME**: Local interpretable explanations
- **Permutation Importance**: Fallback method
- **Feature Importance Ranking**: Understanding model decisions

### 6. **Production Ready**
- **Model Persistence**: Saved models for deployment
- **Comprehensive Logging**: Detailed progress tracking
- **Visualization**: PDF report with all plots
- **Error Handling**: Graceful degradation if optional libraries unavailable

## Dataset-Specific Configurations:

### Kidney Disease Dataset:
- **Features**: 14 numerical + 9 binary categorical + 1 non-binary categorical
- **Target**: CKD vs Not-CKD classification
- **Special Handling**: String cleaning, '?' to NaN conversion

### PONE Dataset:
- **Features**: 10 numerical + 12 binary categorical + 1 non-binary categorical  
- **Target**: EventCKD35 prediction
- **Special Handling**: Direct integer conversion

This pipeline provides a complete, production-ready solution for CKD prediction with robust preprocessing, comprehensive evaluation, and explainable results.

