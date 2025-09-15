import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_validate, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, OrdinalEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import QuantileTransformer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, roc_auc_score, confusion_matrix, roc_curve, auc, classification_report
from sklearn.inspection import permutation_importance
from imblearn.over_sampling import BorderlineSMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import lightgbm as lgb
import xgboost as xgb
import catboost as cb
try:
    import shap
    SHAP_AVAILABLE = True
except Exception as e:
    print(f"SHAP import error: {e}. Continuing without SHAP.")
    SHAP_AVAILABLE = False
try:
    import lime.lime_tabular
    LIME_AVAILABLE = True
except Exception as e:
    print(f"LIME import error: {e}. Continuing without LIME.")
    LIME_AVAILABLE = False

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import joblib
from scipy.stats import randint, uniform, skew
import warnings
warnings.filterwarnings('ignore')

# Function to clean feature names
def clean_feature_names(feature_names):
    cleaned_names = []
    for name in feature_names:
        # Remove prefixes like 'num_standard__', 'cat_binary__', etc.
        if '__' in name:
            cleaned_name = name.split('__')[-1]
        else:
            cleaned_name = name
        cleaned_names.append(cleaned_name)
    return cleaned_names

# Enhanced outlier detection function
def detect_outliers(X, method='isolation_forest', contamination=0.1):
    """
    Detect outliers using IsolationForest or LocalOutlierFactor
    """
    if method == 'isolation_forest':
        detector = IsolationForest(contamination=contamination, random_state=42, n_jobs=-1)
    elif method == 'lof':
        detector = LocalOutlierFactor(n_neighbors=20, contamination=contamination, n_jobs=-1)
    else:
        return np.zeros(X.shape[0], dtype=bool)
    
    outlier_labels = detector.fit_predict(X)
    return outlier_labels == -1




def fallback_feature_selection(X, y, feature_names, dataset_name):
    # Uses multiple sklearn methods:
    # - Statistical feature selection (F-test)
    # - Mutual information selection
    # - Recursive Feature Elimination
    # - Combines results for robust selection
    print(f'\nFeature Selection for {dataset_name} (Fallback Method):')
    print(f'Starting with {X.shape[1]} features')
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif, RFE
        selector_f = SelectKBest(score_func=f_classif, k=min(15, X.shape[1]))
        X_f = selector_f.fit_transform(X, y)
        selected_f = selector_f.get_support()
        selector_mi = SelectKBest(score_func=mutual_info_classif, k=min(15, X.shape[1]))
        X_mi = selector_mi.fit_transform(X, y)
        selected_mi = selector_mi.get_support()
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        selector_rfe = RFE(estimator=rf, n_features_to_select=min(15, X.shape[1]))
        X_rfe = selector_rfe.fit_transform(X, y)
        selected_rfe = selector_rfe.get_support()
        combined_selection = selected_f.astype(int) + selected_mi.astype(int) + selected_rfe.astype(int)
        final_selection = combined_selection >= 2
        if np.sum(final_selection) < 5:
            final_selection = combined_selection >= 1
        selected_features = X[:, final_selection]
        selected_feature_names = [feature_names[i] for i in range(len(feature_names)) if final_selection[i]]
        print(f'Selected {len(selected_feature_names)} features out of {len(feature_names)}')
        print(f'Selected features: {selected_feature_names}')
        return selected_features, selected_feature_names, final_selection
    except Exception as e:
        print(f'Feature selection error: {e}. Using all features.')
        return X, feature_names, np.ones(X.shape[1], dtype=bool)


# Enhanced preprocessing function
def preprocess_dataset(df, dataset_name, id_column, numerical_cols, binary_categorical_cols, non_binary_categorical_cols, target_col, standard_scale_cols, minmax_scale_cols, robust_scale_cols, quantile_transform_cols):
    print(f"\n{'='*50}")
    print(f"PREPROCESSING DATASET: {dataset_name}")
    print(f"{'='*50}")
    
    # Original dataset info
    print(f"\nOriginal dataset shape: {df.shape}")
    print(f"Original features: {list(df.columns)}")
    print(f"\nOriginal feature counts by type:")
    print(f"- Numerical features: {len(numerical_cols)}")
    print(f"- Binary categorical features: {len(binary_categorical_cols)}")
    print(f"- Non-binary categorical features: {len(non_binary_categorical_cols)}")
    
    # Drop ID column
    df = df.drop(id_column, axis=1)
    print(f"\nAfter dropping ID column: {df.shape}")
    
    # Handle target variable
    if dataset_name == 'kidney_disease':
        print(f"\nOriginal target distribution: {df[target_col].value_counts()}")
        df[target_col] = df[target_col].str.strip()
        df[target_col] = df[target_col].map({'ckd': 1, 'notckd': 0})
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.strip()
                df[col] = df[col].replace('?', np.nan)
        for col in numerical_cols:
            if col in df.columns and df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col], errors='coerce')
    else:
        df[target_col] = df[target_col].astype(int)
    
    print(f"\nTarget distribution after encoding: {df[target_col].value_counts()}")
    
    # Check missing values
    missing_values = df.isnull().sum()
    print(f"\nMissing values per feature:")
    for col, count in missing_values.items():
        if count > 0:
            print(f"- {col}: {count} ({count/len(df)*100:.1f}%)")
    
    features = numerical_cols + binary_categorical_cols + non_binary_categorical_cols
    X = df[features]
    y = df[target_col]
    
    print(f"\nFeatures selected for modeling: {len(features)}")
    print(f"Features: {features}")
    
    # Analyze skewness for numerical features before preprocessing
    print(f"\n{'='*50}")
    print(f"SKEWNESS ANALYSIS")
    print(f"{'='*50}")
    
    for col in numerical_cols:
        if col in X.columns:
            col_data = X[col].dropna()
            if len(col_data) > 0 and len(np.unique(col_data)) > 2:
                col_skew = abs(skew(col_data))
                print(f"- {col}: {col_skew:.3f} {'(highly skewed)' if col_skew > 1 else '(moderately skewed)' if col_skew > 0.5 else '(normal)'}")
    
    # Create enhanced preprocessor with IterativeImputer and QuantileTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num_standard', ImbPipeline([
                ('imputer', IterativeImputer(estimator=RandomForestRegressor(n_estimators=10, random_state=42), 
                                           max_iter=10, random_state=42)),
                ('scaler', StandardScaler())
            ]), standard_scale_cols),
            ('num_minmax', ImbPipeline([
                ('imputer', IterativeImputer(estimator=RandomForestRegressor(n_estimators=10, random_state=42), 
                                           max_iter=10, random_state=42)),
                ('scaler', MinMaxScaler())
            ]), minmax_scale_cols),
            ('num_robust', ImbPipeline([
                ('imputer', IterativeImputer(estimator=RandomForestRegressor(n_estimators=10, random_state=42), 
                                           max_iter=10, random_state=42)),
                ('scaler', RobustScaler())
            ]), robust_scale_cols),
            ('num_quantile', ImbPipeline([
                ('imputer', IterativeImputer(estimator=RandomForestRegressor(n_estimators=10, random_state=42), 
                                           max_iter=10, random_state=42)),
                ('scaler', QuantileTransformer(output_distribution='normal', random_state=42))
            ]), quantile_transform_cols),
            ('cat_binary', ImbPipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', OrdinalEncoder())
            ]), binary_categorical_cols),
            ('cat_non_binary', ImbPipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', OneHotEncoder(drop='first', sparse_output=False))
            ]), non_binary_categorical_cols)
        ],
        remainder='passthrough'
    )
    
    # Fit preprocessor to get feature names
    preprocessor.fit(X)
    feature_names = preprocessor.get_feature_names_out()
    cleaned_feature_names = clean_feature_names(feature_names)
    
    print(f"\n{'='*50}")
    print(f"PREPROCESSING CONFIGURATION")
    print(f"{'='*50}")
    print(f"- IterativeImputer (multivariate) for numerical features")
    print(f"- Standard scaled features: {len(standard_scale_cols)} {standard_scale_cols}")
    print(f"- MinMax scaled features: {len(minmax_scale_cols)} {minmax_scale_cols}")
    print(f"- Robust scaled features: {len(robust_scale_cols)} {robust_scale_cols}")
    print(f"- Quantile transformed features (skewed): {len(quantile_transform_cols)} {quantile_transform_cols}")
    print(f"- Binary categorical features (ordinal encoded): {len(binary_categorical_cols)}")
    print(f"- Non-binary categorical features (one-hot encoded): {len(non_binary_categorical_cols)}")
    
    # Show one-hot encoding expansion
    for col in non_binary_categorical_cols:
        unique_values = df[col].dropna().unique()
        print(f"- '{col}' expanded to {len(unique_values)-1} features (dropped first category)")
    
    print(f"\nTotal features after preprocessing: {len(feature_names)}")
    print(f"Original features: {len(features)}")
    print(f"Features added due to one-hot encoding: {len(feature_names) - len(features)}")
    
    # Show sample of transformed feature names
    print(f"\nSample of transformed feature names:")
    for i, name in enumerate(cleaned_feature_names[:10]):
        print(f"- {name}")
    if len(cleaned_feature_names) > 10:
        print(f"... and {len(cleaned_feature_names) - 10} more")
    
    return X, y, preprocessor, features

# Enhanced datasets configuration with quantile transform columns
datasets = {
    'kidney_disease': {
        'path': '/kaggle/input/ckdisease/kidney_disease.csv',
        'id_column': 'id',
        'numerical_cols': ['age', 'bp', 'sg', 'al', 'su', 'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc'],
        'binary_categorical_cols': ['rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 'pe', 'ane'],
        'non_binary_categorical_cols': ['appet'],
        'target_col': 'classification',
        'standard_scale_cols': ['age', 'bp', 'hemo', 'sod', 'pot', 'pcv'],
        'minmax_scale_cols': ['sg', 'al', 'su'],
        'robust_scale_cols': ['wc', 'rc'],
        'quantile_transform_cols': ['bgr', 'bu', 'sc']  # Highly skewed features
    },
    'pone': {
        'path': '/kaggle/input/prone4911/pone.0199920.s002.xlsx',
        'id_column': 'StudyID',
        'numerical_cols': ['AgeBaseline', 'CholesterolBaseline', 'TriglyceridesBaseline', 'HgbA1C', 'CreatnineBaseline', 'eGFRBaseline', 'sBPBaseline', 'dBPBaseline', 'BMIBaseline', 'TimeToEventMonths'],
        'binary_categorical_cols': ['Gender', 'HistoryDiabetes', 'HistoryCHD', 'HistoryVascular', 'HistorySmoking', 'HistoryHTN ', 'HistoryDLD', 'HistoryObesity', 'DLDmeds', 'DMmeds', 'HTNmeds', 'ACEIARB'],
        'non_binary_categorical_cols': ['Age.3.categories'],
        'target_col': 'EventCKD35',
        'standard_scale_cols': ['AgeBaseline', 'sBPBaseline', 'dBPBaseline', 'BMIBaseline'],
        'minmax_scale_cols': ['HgbA1C', 'eGFRBaseline'],
        'robust_scale_cols': ['CreatnineBaseline'],
        'quantile_transform_cols': ['CholesterolBaseline', 'TriglyceridesBaseline', 'TimeToEventMonths']  # Highly skewed features
    }
}

# Initialize PDF
pdf_pages = PdfPages('enhanced_ckd_model_plots.pdf')

# Define Classifiers and Parameter Grids
classifiers = {
    'Logistic Regression': (LogisticRegression(random_state=42), {
        'classifier__C': uniform(0.1, 10),
        'classifier__solver': ['lbfgs', 'liblinear']
    }),
    'Random Forest': (RandomForestClassifier(random_state=42), {
        'classifier__n_estimators': randint(50, 200),
        'classifier__max_depth': [None, 10, 20],
        'classifier__min_samples_split': randint(2, 10)
    }),
    'LightGBM': (lgb.LGBMClassifier(random_state=42, verbose=-1), {
        'classifier__n_estimators': randint(50, 200),
        'classifier__learning_rate': uniform(0.01, 0.3),
        'classifier__max_depth': randint(3, 10)
    }),
    'XGBoost': (xgb.XGBClassifier(random_state=42, eval_metric='logloss'), {
        'classifier__n_estimators': randint(50, 200),
        'classifier__learning_rate': uniform(0.01, 0.3),
        'classifier__max_depth': randint(3, 10)
    }),
    'CatBoost': (cb.CatBoostClassifier(random_state=42, verbose=0), {
        'classifier__iterations': randint(50, 200),
        'classifier__learning_rate': uniform(0.01, 0.3),
        'classifier__depth': randint(4, 10)
    }),
    'Gradient Boosting': (GradientBoostingClassifier(random_state=42), {
        'classifier__n_estimators': randint(50, 200),
        'classifier__learning_rate': uniform(0.01, 0.3),
        'classifier__max_depth': randint(3, 10)
    }),
    'Naive Bayes': (GaussianNB(), {
        'classifier__var_smoothing': uniform(1e-9, 1e-7)
    }),
    'KNN': (KNeighborsClassifier(), {
        'classifier__n_neighbors': randint(3, 15),
        'classifier__weights': ['uniform', 'distance']
    }),
    'Extra Trees': (ExtraTreesClassifier(random_state=42), {
        'classifier__n_estimators': randint(50, 200),
        'classifier__max_depth': [None, 10, 20],
        'classifier__min_samples_split': randint(2, 10)
    }),
    'Decision Tree': (DecisionTreeClassifier(random_state=42), {
        'classifier__max_depth': [None, 10, 20],
        'classifier__min_samples_split': randint(2, 10)
    })
}

# Step 3: Process Each Dataset with Enhanced Preprocessing
for dataset_name, config in datasets.items():
    print(f"\n{'='*70}")
    print(f"PROCESSING DATASET: {dataset_name}")
    print(f"{'='*70}")
    
    try:
        if dataset_name == 'kidney_disease':
            df = pd.read_csv(config['path'])
        else:
            df = pd.read_excel(config['path'])
    except FileNotFoundError:
        print(f"Error: File {config['path']} not found.")
        continue
    
    X, y, preprocessor, features = preprocess_dataset(
        df, dataset_name, config['id_column'], config['numerical_cols'], config['binary_categorical_cols'],
        config['non_binary_categorical_cols'], config['target_col'], config['standard_scale_cols'],
        config['minmax_scale_cols'], config['robust_scale_cols'], config['quantile_transform_cols']
    )
    
    # Preprocess the entire dataset first
    X_preprocessed = preprocessor.fit_transform(X)
    feature_names = clean_feature_names(preprocessor.get_feature_names_out())
    
    print(f"\n{'='*50}")
    print(f"OUTLIER DETECTION")
    print(f"{'='*50}")
    
    # Detect outliers using IsolationForest
    outliers_isolation = detect_outliers(X_preprocessed, method='isolation_forest', contamination=0.1)
    outliers_lof = detect_outliers(X_preprocessed, method='lof', contamination=0.1)
    
    print(f"IsolationForest detected {np.sum(outliers_isolation)} outliers ({np.sum(outliers_isolation)/len(X_preprocessed)*100:.1f}%)")
    print(f"LocalOutlierFactor detected {np.sum(outliers_lof)} outliers ({np.sum(outliers_lof)/len(X_preprocessed)*100:.1f}%)")
    
    # Use IsolationForest results for outlier removal (you can modify this logic)
    outlier_mask = outliers_isolation
    
    # Remove outliers
    X_cleaned = X_preprocessed[~outlier_mask]
    y_cleaned = y.iloc[~outlier_mask].values
    
    print(f"Dataset shape after outlier removal: {X_cleaned.shape}")
    print(f"Removed {np.sum(outlier_mask)} outliers")
    
    print(f"\n{'='*50}")
    print(f"PREPROCESSING RESULTS")
    print(f"{'='*50}")
    print(f"Original dataset shape: {X_preprocessed.shape}")
    print(f"Cleaned dataset shape (outliers removed): {X_cleaned.shape}")
    print(f"Number of features after preprocessing: {len(feature_names)}")
    
    # Show feature expansion details
    original_features = len(features)
    new_features = len(feature_names) - original_features
    print(f"\nFeature expansion details:")
    print(f"- Original features: {original_features}")
    print(f"- Features after preprocessing: {len(feature_names)}")
    print(f"- New features added: {new_features}")
    
    # Show preprocessing method details
    print(f"\nPreprocessing method details:")
    print(f"- IterativeImputer used for multivariate imputation")
    print(f"- QuantileTransformer used for {len(config['quantile_transform_cols'])} highly skewed features")
    print(f"- IsolationForest removed {np.sum(outlier_mask)} outliers")
    
    # Apply BorderlineSMOTE to the cleaned preprocessed dataset
    borderlinesmote = BorderlineSMOTE(sampling_strategy='auto', random_state=42, kind='borderline-1')
    X_resampled, y_resampled = borderlinesmote.fit_resample(X_cleaned, y_cleaned)
    
    print(f"\n{'='*50}")
    print(f"BORDERLINESMOTE RESAMPLING")
    print(f"{'='*50}")
    print(f"Dataset shape before resampling: {X_cleaned.shape}")
    print(f"Dataset shape after resampling: {X_resampled.shape}")
    print(f"Original target distribution: {pd.Series(y_cleaned).value_counts()}")
    print(f"Resampled target distribution: {pd.Series(y_resampled).value_counts()}")
    
    # Train-test split after resampling
    X_train_resampled, X_test_preprocessed, y_train_resampled, y_test = train_test_split(
        X_resampled, y_resampled, test_size=0.2, random_state=42, stratify=y_resampled
    )
    print(f"\n{'='*50}")
    print(f"TRAIN-TEST SPLIT (AFTER RESAMPLING)")
    print(f"{'='*50}")
    print(f"Training set shape: {X_train_resampled.shape}")
    print(f"Test set shape: {X_test_preprocessed.shape}")
    print(f"Training target distribution: {pd.Series(y_train_resampled).value_counts()}")
    print(f"Test target distribution: {pd.Series(y_test).value_counts()}")
    
    # Original class distribution
    class_counts = pd.Series(y_cleaned).value_counts()
    print(f"\nOriginal Class Distribution ({dataset_name}):")
    print(class_counts)
    imbalance_ratio = class_counts[1] / class_counts[0] if 0 in class_counts else 1
    print(f"Imbalance Ratio (Positive/Negative): {imbalance_ratio:.2f}")
    
    plt.figure(figsize=(6, 4))
    sns.barplot(x=class_counts.index.map({0: 'Negative', 1: 'Positive'}), y=class_counts.values, palette=['#ef4444', '#3b82f6'])
    plt.title(f'Original Class Distribution ({dataset_name})')
    plt.xlabel('Class')
    plt.ylabel('Count')
    plt.savefig(pdf_pages, format='pdf', bbox_inches='tight')
    plt.close()
    
    # Resampled class distribution
    resampled_counts = pd.Series(y_resampled).value_counts()
    print(f"\nResampled Class Distribution ({dataset_name}):")
    print(resampled_counts)
    print(f"Resampled Imbalance Ratio: {resampled_counts[1]/resampled_counts[0]:.2f}")
    
    plt.figure(figsize=(6, 4))
    sns.barplot(x=resampled_counts.index.map({0: 'Negative', 1: 'Positive'}), y=resampled_counts.values, palette=['#ef4444', '#3b82f6'])
    plt.title(f'Resampled Class Distribution ({dataset_name})')
    plt.xlabel('Class')
    plt.ylabel('Count')
    plt.savefig(pdf_pages, format='pdf', bbox_inches='tight')
    plt.close()
    
    scoring = ['accuracy', 'f1', 'recall', 'precision', 'roc_auc']
    cv_results_list = []
    test_results_list = []
    roc_curves = []  # Store ROC curves for all models
    tuned_classifiers = {}
    
    for name, (clf, param_grid) in classifiers.items():
        pipeline = ImbPipeline([('classifier', clf)])
        search = RandomizedSearchCV(pipeline, param_distributions=param_grid, n_iter=10, cv=5, scoring='roc_auc', random_state=42, n_jobs=-1)
        try:
            search.fit(X_train_resampled, y_train_resampled)
            best_clf = search.best_estimator_
            tuned_classifiers[name] = best_clf
            cv_results = cross_validate(best_clf, X_train_resampled, y_train_resampled, cv=5, scoring=scoring)
            cv_results_list.append({
                'Model': name,
                'CV Accuracy': np.mean(cv_results['test_accuracy']),
                'CV F1': np.mean(cv_results['test_f1']),
                'CV Recall': np.mean(cv_results['test_recall']),
                'CV Precision': np.mean(cv_results['test_precision']),
                'CV ROC AUC': np.mean(cv_results['test_roc_auc'])
            })
            y_pred = best_clf.predict(X_test_preprocessed)
            y_prob = best_clf.predict_proba(X_test_preprocessed)[:, 1]
            test_results_list.append({
                'Model': name,
                'Test Accuracy': accuracy_score(y_test, y_pred),
                'Test F1': f1_score(y_test, y_pred),
                'Test Recall': recall_score(y_test, y_pred),
                'Test Precision': precision_score(y_test, y_pred),
                'Test MAE': mean_absolute_error(y_test, y_pred),
                'Test ROC AUC': roc_auc_score(y_test, y_prob)
            })
            fpr, tpr, _ = roc_curve(y_test, y_prob)
            roc_auc = auc(fpr, tpr)
            roc_curves.append((name, fpr, tpr, roc_auc))  # Store ROC curve data
            cm = confusion_matrix(y_test, y_pred)
            plt.figure(figsize=(6, 4))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                        xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
            plt.title(f'Confusion Matrix: {name} ({dataset_name})')
            plt.xlabel('Predicted')
            plt.ylabel('Actual')
            plt.savefig(pdf_pages, format='pdf', bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Error training {name} ({dataset_name}): {str(e)}")
            continue
    
    cv_results_df = pd.DataFrame(cv_results_list).sort_values(by='CV ROC AUC', ascending=False)
    print(f"\n{'='*50}")
    print(f"CROSS-VALIDATION RESULTS")
    print(f"{'='*50}")
    print(f"\nCross-Validation Results for All Classifiers ({dataset_name}):")
    print(cv_results_df)
    
    top_4_models = cv_results_df.head(4)['Model'].values
    print(f"\nTop 4 Models by CV ROC AUC ({dataset_name}):", top_4_models)
    
    # Create combined ROC curve plot for all models
    plt.figure(figsize=(12, 10))
    for name, fpr, tpr, roc_auc in roc_curves:
        plt.plot(fpr, tpr, label=f'{name} (AUC = {roc_auc:.3f})')
    
    # Plot the random classifier line
    plt.plot([0, 1], [0, 1], 'k--', lw=2, label='Random Classifier (AUC = 0.500)')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title(f'ROC Curves for All Models ({dataset_name})', fontsize=14)
    plt.legend(loc="lower right", fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.savefig(pdf_pages, format='pdf', bbox_inches='tight')
    plt.close()
    
    
    test_results_df = pd.DataFrame(test_results_list).sort_values(by='Test Accuracy', ascending=False)
    print(f"\n{'='*50}")
    print(f"TEST RESULTS")
    print(f"{'='*50}")
    print(f"\nTest Set Performance for All Models ({dataset_name}):")
    print(test_results_df)
    
    # Select best single model by highest Test Accuracy
    best_model_name = test_results_df.iloc[0]['Model']
    best_model = tuned_classifiers[best_model_name]
    print(f"\nBest Single Model (Highest Accuracy, {dataset_name}): {best_model_name}")
    
    best_model.fit(X_train_resampled, y_train_resampled)
    y_pred = best_model.predict(X_test_preprocessed)
    y_prob = best_model.predict_proba(X_test_preprocessed)[:, 1]
    
    print(f"\n{'='*50}")
    print(f"BEST MODEL PERFORMANCE")
    print(f"{'='*50}")
    print(f"\nTest Set Performance for Best Model ({best_model_name}, {dataset_name}):")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    print(f"Precision: {precision_score(y_test, y_pred):.2f}")
    print(f"Recall: {recall_score(y_test, y_pred):.2f}")
    print(f"F1-Score: {f1_score(y_test, y_pred):.2f}")
    print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
    print(f"ROC AUC: {roc_auc_score(y_test, y_prob):.2f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Negative', 'Positive']))
    
    # Create outlier detection visualization
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.scatter(range(len(outliers_isolation)), np.where(outliers_isolation, 1, 0), 
                c=['red' if x else 'blue' for x in outliers_isolation], alpha=0.6)
    plt.title(f'IsolationForest Outlier Detection ({dataset_name})')
    plt.xlabel('Sample Index')
    plt.ylabel('Outlier (1) / Normal (0)')
    
    plt.subplot(1, 2, 2)
    plt.scatter(range(len(outliers_lof)), np.where(outliers_lof, 1, 0), 
                c=['red' if x else 'blue' for x in outliers_lof], alpha=0.6)
    plt.title(f'LocalOutlierFactor Outlier Detection ({dataset_name})')
    plt.xlabel('Sample Index')
    plt.ylabel('Outlier (1) / Normal (0)')
    
    plt.tight_layout()
    plt.savefig(pdf_pages, format='pdf', bbox_inches='tight')
    plt.close()
    
    # Create skewness comparison plot for quantile-transformed features
    if config['quantile_transform_cols']:
        fig, axes = plt.subplots(2, len(config['quantile_transform_cols']), figsize=(15, 8))
        if len(config['quantile_transform_cols']) == 1:
            axes = axes.reshape(-1, 1)
        
        for i, col in enumerate(config['quantile_transform_cols']):
            if col in X.columns:
                # Original data
                original_data = X[col].dropna()
                axes[0, i].hist(original_data, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
                axes[0, i].set_title(f'Original {col}\nSkewness: {skew(original_data):.3f}')
                axes[0, i].set_xlabel('Value')
                axes[0, i].set_ylabel('Frequency')
                
                # Find the column index in transformed data
                col_index = None
                for j, fname in enumerate(feature_names):
                    if col in fname:
                        col_index = j
                        break
                
                if col_index is not None:
                    # Transformed data
                    transformed_data = X_cleaned[:, col_index]
                    axes[1, i].hist(transformed_data, bins=30, alpha=0.7, color='lightcoral', edgecolor='black')
                    axes[1, i].set_title(f'Quantile Transformed {col}\nSkewness: {skew(transformed_data):.3f}')
                    axes[1, i].set_xlabel('Value')
                    axes[1, i].set_ylabel('Frequency')
        
        plt.suptitle(f'Before/After Quantile Transformation ({dataset_name})', fontsize=16)
        plt.tight_layout()
        plt.savefig(pdf_pages, format='pdf', bbox_inches='tight')
        plt.close()
    
    shap_importance = None
    if SHAP_AVAILABLE:
        try:
            explainer = shap.KernelExplainer(lambda x: best_model.predict_proba(x), X_train_resampled[:100])
            shap_values = explainer.shap_values(X_test_preprocessed[:10])
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            plt.figure(figsize=(10, 6))
            shap.summary_plot(shap_values, X_test_preprocessed[:10], feature_names=feature_names, show=False)
            plt.title(f'SHAP Summary Plot (Best Model: {best_model_name}, {dataset_name})')
            plt.savefig(pdf_pages, format='pdf', bbox_inches='tight')
            plt.close()
            shap_importance = np.abs(shap_values).mean(axis=0)
            plt.figure(figsize=(10, 6))
            sns.barplot(x=shap_importance, y=feature_names, palette='Blues_r')
            plt.title(f'SHAP Feature Importance (Best Model: {best_model_name}, {dataset_name})')
            plt.xlabel('Mean Absolute SHAP Value')
            plt.ylabel('Feature')
            plt.savefig(pdf_pages, format='pdf', bbox_inches='tight')
            plt.close()
            print(f"\nSHAP Local Explanation for First Test Instance ({dataset_name}):")
            plt.figure()
            shap.force_plot(explainer.expected_value[1], shap_values[0], X_test_preprocessed[0],
                            feature_names=feature_names, matplotlib=True, show=False)
            plt.savefig(pdf_pages, format='pdf', bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"SHAP Error ({dataset_name}): {str(e)}")
    
    if shap_importance is None:
        print(f"Using permutation importance fallback ({dataset_name}).")
        perm = permutation_importance(best_model, X_test_preprocessed, y_test, n_repeats=10, random_state=42, n_jobs=-1)
        shap_importance = perm.importances_mean
        plt.figure(figsize=(10, 6))
        sns.barplot(x=shap_importance, y=feature_names, palette='Blues_r')
        plt.title(f'Permutation Feature Importance (Best Model: {best_model_name}, {dataset_name})')
        plt.xlabel('Mean Importance (Decrease in Score)')
        plt.ylabel('Feature')
        plt.savefig(pdf_pages, format='pdf', bbox_inches='tight')
        plt.close()
    
    if LIME_AVAILABLE:
        try:
            lime_explainer = lime.lime_tabular.LimeTabularExplainer(
                X_train_resampled, feature_names=feature_names, class_names=['Negative', 'Positive'], mode='classification'
            )
            print(f"\nLIME Local Explanation for First Test Instance ({dataset_name}):")
            exp = lime_explainer.explain_instance(X_test_preprocessed[0], best_model.predict_proba, num_features=10)
            fig = exp.as_pyplot_figure()
            plt.title(f'LIME Explanation (Best Model: {best_model_name}, {dataset_name})')
            plt.savefig(pdf_pages, format='pdf', bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"LIME Error ({dataset_name}): {str(e)}")
    else:
        print(f"LIME not available; skipping LIME explanations ({dataset_name}).")
    
    model_filename = f"{'enhanced_kd' if dataset_name == 'kidney_disease' else 'enhanced_pone'}_disease_prediction_model.pkl"
    joblib.dump(best_model, model_filename)
    print(f"\nBest model pipeline saved as '{model_filename}'")
    
    print(f"\n{'='*50}")
    print(f"FEATURE IMPORTANCE")
    print(f"{'='*50}")
    print(f"\nSHAP-Based Feature Importance ({dataset_name}):")
    shap_importance_df = pd.DataFrame({
        'Feature': feature_names,
        'SHAP Importance': shap_importance
    }).sort_values(by='SHAP Importance', ascending=False)
    print(shap_importance_df)
    
    top_feature = shap_importance_df.iloc[0]['Feature']
    print(f"\nInteresting Fact ({dataset_name}): The feature '{top_feature}' has the highest SHAP importance, "
          f"indicating it is a critical predictor for {'hemoglobin or hypertension' if dataset_name == 'kidney_disease' else 'creatinine or eGFR'}, "
          f"which are strongly associated with CKD.")
    
    print(f"\n{'='*50}")
    print(f"ENHANCED PREPROCESSING SUMMARY")
    print(f"{'='*50}")
    print(f"Dataset: {dataset_name}")
    print(f"- IterativeImputer (multivariate): Replaced SimpleImputer for better missing value handling")
    print(f"- QuantileTransformer: Applied to {len(config['quantile_transform_cols'])} highly skewed features")
    print(f"- IsolationForest: Detected and removed {np.sum(outlier_mask)} outliers ({np.sum(outlier_mask)/len(X_preprocessed)*100:.1f}%)")
    print(f"- BorderlineSMOTE: Balanced classes from {class_counts.to_dict()} to {resampled_counts.to_dict()}")
    print(f"- Best Model: {best_model_name} with {accuracy_score(y_test, y_pred):.2f} accuracy")

pdf_pages.close()
print(f"\n{'='*70}")
print("ENHANCED CONCLUSION")
print(f"{'='*70}")
print("Both datasets were processed using an enhanced ColumnTransformer and Pipeline with the following improvements:")
print("1. IterativeImputer (multivariate) replaced SimpleImputer for better missing value imputation using RandomForest estimator")
print("2. QuantileTransformer added for highly skewed features to normalize distributions")  
print("3. IsolationForest integrated for outlier detection and removal before training")
print("4. All other preprocessing steps maintained: attribute-wise encoding, scaling, and BorderlineSMOTE for class balancing")
print("5. RandomizedSearchCV tuned hyperparameters for 10 classifiers with comprehensive evaluation")
print("6. Enhanced visualizations include outlier detection plots and before/after skewness comparisons")
print("7. SHAP and LIME explanations generated with cleaned feature names and saved in 'enhanced_ckd_model_plots.pdf'")
print("8. Model pipelines saved as 'enhanced_kd_disease_prediction_model.pkl' and 'enhanced_pone_disease_prediction_model.pkl'")
print("The enhanced preprocessing pipeline provides more robust feature engineering and outlier handling for improved CKD prediction performance.")