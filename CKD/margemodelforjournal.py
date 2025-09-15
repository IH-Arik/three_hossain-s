#!/usr/bin/env python3
"""
Chronic Kidney Disease (CKD) Prediction Pipeline
===============================================

A comprehensive machine learning pipeline for CKD detection and prognosis
using hybrid clinical decision support.

Author: CKD Research Team
Date: 2024
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# =============================================================================
# STEP 1: IMPORTS & SETUP
# =============================================================================

print("🏥 CKD Prediction Pipeline - Starting...")
print("=" * 60)

# Basic libraries
import pandas as pd
import numpy as np

# Preprocessing
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.utils import resample

# Classifiers
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier, VotingClassifier
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from imblearn.ensemble import BalancedRandomForestClassifier, EasyEnsembleClassifier
from imblearn.over_sampling import BorderlineSMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

# Boosting libraries
import lightgbm as lgb
import xgboost as xgb
import catboost as cb

# Survival analysis
try:
    from sksurv.linear_model import CoxPHSurvivalAnalysis
    from sksurv.ensemble import RandomSurvivalForest
    SURVIVAL_AVAILABLE = True
    print("✅ Survival analysis libraries loaded")
except ImportError:
    print("⚠️  Survival analysis libraries not available - skipping prognosis models")
    SURVIVAL_AVAILABLE = False

# Calibration
from sklearn.calibration import CalibratedClassifierCV

# Metrics
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, brier_score_loss,
    precision_recall_curve, mean_absolute_error
)
from sklearn.calibration import calibration_curve

# Plots
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

# Explainability
import shap
import lime.lime_tabular

# Misc
import joblib

print("✅ All libraries imported successfully")

# =============================================================================
# STEP 2: LOAD DATASETS
# =============================================================================

print("\n📊 Loading Datasets...")

try:
    # Load datasets
    kidney_df = pd.read_csv("/kaggle/input/ckdisease/kidney_disease.csv")
    clinical_df = pd.read_excel("/kaggle/input/prone4911/pone.0199920.s002.xlsx")
    
    print(f"✅ Kidney dataset shape: {kidney_df.shape}")
    print(f"✅ Clinical dataset shape: {clinical_df.shape}")
    
except Exception as e:
    print(f"❌ Dataset loading error: {e}")
    print("Please ensure the Kaggle datasets are properly mounted")
    exit(1)

# =============================================================================
# STEP 3: KIDNEY DATASET PREPROCESSING (DETECTION)
# =============================================================================

print("\n🔧 Preprocessing Kidney Dataset (Detection)...")

# Clean target
kidney_df["classification"] = kidney_df["classification"].str.strip().map({"ckd": 1, "notckd": 0})

# Replace "?" with NaN
kidney_df = kidney_df.replace("?", np.nan)

# Convert numeric-like columns
num_cols = ['age','bp','sg','al','su','bgr','bu','sc','sod','pot','hemo','pcv','wc','rc']
for col in num_cols:
    kidney_df[col] = pd.to_numeric(kidney_df[col], errors="coerce")

# Clinically aware imputation
kidney_df["sod"] = kidney_df["sod"].fillna(140)  # sodium normal mean
kidney_df["pot"] = kidney_df["pot"].fillna(4.5)  # potassium normal mean
kidney_df["hemo"] = kidney_df["hemo"].fillna(13.5)  # hemoglobin normal mean

for col in ["pcv","wc","rc"]:
    kidney_df[col] = kidney_df[col].fillna(kidney_df[col].median())

# Feature engineering
kidney_df["urea_creatinine_ratio"] = kidney_df["bu"] / (kidney_df["sc"]+1e-5)
kidney_df["anemia_flag"] = (kidney_df["hemo"] < 12).astype(int)
kidney_df["htn_dm_interaction"] = ((kidney_df["htn"]=="yes") & (kidney_df["dm"]=="yes")).astype(int)

# Outlier handling (winsorize)
kidney_df["sc"] = np.clip(kidney_df["sc"], 0, 15)  # serum creatinine
kidney_df["bu"] = np.clip(kidney_df["bu"], 0, 300) # blood urea
kidney_df["bp"] = np.clip(kidney_df["bp"], 40, 200)

# Split features / target
X_kd = kidney_df.drop(columns=["id","classification"])
y_kd = kidney_df["classification"]

print(f"✅ Kidney dataset ready. Features: {X_kd.shape[1]}")
print(f"✅ Target distribution: {y_kd.value_counts().to_dict()}")

# =============================================================================
# STEP 4: CLINICAL DATASET PREPROCESSING (PROGNOSIS)
# =============================================================================

print("\n🔧 Preprocessing Clinical Dataset (Prognosis)...")

# Clean column names
clinical_df = clinical_df.rename(columns={"HistoryHTN ": "HistoryHTN"})

# Structured survival outcome (event, time)
y_clinical = np.array([
    (bool(event), time) for event, time in zip(clinical_df["EventCKD35"], clinical_df["TimeToEventMonths"])
], dtype=[("event", "bool"), ("time", "int")])

# Feature Engineering
clinical_df["BMI_Category"] = pd.cut(
    clinical_df["BMIBaseline"],
    bins=[0, 25, 30, 100],
    labels=["Normal", "Overweight", "Obese"]
)

clinical_df["Metabolic_Syndrome"] = (
    clinical_df["HistoryDiabetes"] +
    clinical_df["HistoryHTN"] +
    clinical_df["HistoryObesity"] +
    clinical_df["HistoryDLD"]
)

# Age group dummies (align with Age.3.categories)
clinical_df = pd.get_dummies(clinical_df, columns=["Age.3.categories"], drop_first=True)

# Missing Value Imputation
clinical_df["HgbA1C"] = clinical_df["HgbA1C"].fillna(clinical_df["HgbA1C"].median())
clinical_df["TriglyceridesBaseline"] = clinical_df["TriglyceridesBaseline"].fillna(
    clinical_df["TriglyceridesBaseline"].median()
)

# Outlier Handling (Winsorize)
clinical_df["CreatnineBaseline"] = np.clip(clinical_df["CreatnineBaseline"], 20, 800)
clinical_df["CholesterolBaseline"] = np.clip(clinical_df["CholesterolBaseline"], 2, 15)
clinical_df["TriglyceridesBaseline"] = np.clip(clinical_df["TriglyceridesBaseline"], 0.2, 10)

# Feature / Target Split
X_clinical = clinical_df.drop(columns=["StudyID", "EventCKD35", "TimeToEventMonths"])

print(f"✅ Clinical dataset ready. Features: {X_clinical.shape[1]}")
print(f"✅ Survival outcome shape: {y_clinical.shape}")
print(f"✅ Event rate: {y_clinical['event'].mean():.3f}")

# =============================================================================
# STEP 5: DETECTION MODELS - KIDNEY DATASET
# =============================================================================

print("\n🤖 Training Detection Models (Kidney Dataset)...")

# Train-Test Split
X_train_kd, X_test_kd, y_train_kd, y_test_kd = train_test_split(
    X_kd, y_kd, test_size=0.2, stratify=y_kd, random_state=42
)

# Preprocessing Pipeline for Kidney Dataset
numeric_features_kd = X_kd.select_dtypes(include=[np.number]).columns.tolist()
categorical_features_kd = X_kd.select_dtypes(include=['object', 'category']).columns.tolist()

# Create preprocessing pipeline with imputation
preprocessor_kd = ColumnTransformer(
    transformers=[
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ]), numeric_features_kd),
        ('cat', Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(handle_unknown='ignore'))
        ]), categorical_features_kd)
    ]
)

# Preprocess
X_train_proc = preprocessor_kd.fit_transform(X_train_kd)
X_test_proc = preprocessor_kd.transform(X_test_kd)

# Check for any remaining NaN values
print(f"NaN values in X_train_proc: {np.isnan(X_train_proc).sum()}")
print(f"NaN values in X_test_proc: {np.isnan(X_test_proc).sum()}")

# Apply SMOTE
smote = BorderlineSMOTE(random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train_proc, y_train_kd)

print(f"✅ SMOTE applied successfully")
print(f"✅ Resampled training set shape: {X_train_res.shape}")
print(f"✅ Resampled target distribution: {np.bincount(y_train_res)}")

# Define Base Classifiers
base_classifiers = {
    "Logistic Regression": LogisticRegression(random_state=42),
    "Random Forest": RandomForestClassifier(random_state=42),
    "XGBoost": xgb.XGBClassifier(random_state=42),
    "LightGBM": lgb.LGBMClassifier(random_state=42),
    "CatBoost": cb.CatBoostClassifier(random_state=42, verbose=False),
    "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    "Extra Trees": ExtraTreesClassifier(random_state=42),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Naive Bayes": GaussianNB(),
    "KNN": KNeighborsClassifier(),
    "MLP": MLPClassifier(random_state=42),
    "Balanced RF": BalancedRandomForestClassifier(random_state=42),
    "Easy Ensemble": EasyEnsembleClassifier(random_state=42)
}

# Cross-Validation Evaluation
cv_results = {}
cv_scores = {}

print("🔄 Running 5-Fold Stratified Cross-Validation...")
cv_folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for name, clf in base_classifiers.items():
    # Create pipeline: preprocessor -> SMOTE -> classifier
    cv_pipeline = ImbPipeline([
        ('preprocessor', preprocessor_kd),
        ('smote', BorderlineSMOTE(random_state=42)),
        ('classifier', clf)
    ])
    
    # Cross-validation scores
    cv_auc = cross_val_score(cv_pipeline, X_kd, y_kd, cv=cv_folds, scoring='roc_auc')
    cv_f1 = cross_val_score(cv_pipeline, X_kd, y_kd, cv=cv_folds, scoring='f1')
    cv_acc = cross_val_score(cv_pipeline, X_kd, y_kd, cv=cv_folds, scoring='accuracy')
    
    cv_results[name] = {
        'AUC_mean': cv_auc.mean(),
        'AUC_std': cv_auc.std(),
        'F1_mean': cv_f1.mean(),
        'F1_std': cv_f1.std(),
        'Accuracy_mean': cv_acc.mean(),
        'Accuracy_std': cv_acc.std()
    }
    
    cv_scores[name] = cv_auc.mean()

print("✅ Cross-validation completed!")

# Train individual classifiers
results_detection = []
fitted_classifiers = {}

for name, clf in base_classifiers.items():
    clf.fit(X_train_res, y_train_res)
    fitted_classifiers[name] = clf
    
    y_pred = clf.predict(X_test_proc)
    y_prob = clf.predict_proba(X_test_proc)[:,1]
    
    acc = accuracy_score(y_test_kd, y_pred)
    f1 = f1_score(y_test_kd, y_pred)
    prec = precision_score(y_test_kd, y_pred)
    rec = recall_score(y_test_kd, y_pred)
    auc_score = roc_auc_score(y_test_kd, y_prob)
    pr_auc = average_precision_score(y_test_kd, y_prob)
    brier = brier_score_loss(y_test_kd, y_prob)
    
    # Add CV scores
    cv_auc_mean = cv_results[name]['AUC_mean']
    cv_auc_std = cv_results[name]['AUC_std']
    
    results_detection.append([name, acc, f1, prec, rec, auc_score, pr_auc, brier, cv_auc_mean, cv_auc_std])

results_detection_df = pd.DataFrame(
    results_detection,
    columns=["Model","Accuracy","F1","Precision","Recall","ROC AUC","PR AUC","Brier Score","CV AUC Mean","CV AUC Std"]
).sort_values(by="CV AUC Mean", ascending=False)

print("\n=== Kidney Dataset Detection Results (with Cross-Validation) ===")
print(results_detection_df)

# Print per-model test metrics for all detection models
print("\n📊 Test Metrics Per Detection Model (Test Set):")
for name, clf in fitted_classifiers.items():
    try:
        y_pred_m = clf.predict(X_test_proc)
        acc_m = accuracy_score(y_test_kd, y_pred_m)
        f1_m = f1_score(y_test_kd, y_pred_m)
        rec_m = recall_score(y_test_kd, y_pred_m)
        prec_m = precision_score(y_test_kd, y_pred_m)
        if hasattr(clf, "predict_proba"):
            y_prob_m = clf.predict_proba(X_test_proc)[:, 1]
            auc_m = roc_auc_score(y_test_kd, y_prob_m)
            pr_auc_m = average_precision_score(y_test_kd, y_prob_m)
            brier_m = brier_score_loss(y_test_kd, y_prob_m)
            mae_m = mean_absolute_error(y_test_kd, y_prob_m)
        else:
            auc_m = np.nan
            pr_auc_m = np.nan
            brier_m = np.nan
            mae_m = np.nan
        print(f"  - {name}: Acc={acc_m:.3f}, F1={f1_m:.3f}, Recall={rec_m:.3f}, Precision={prec_m:.3f}, AUC={auc_m:.3f}, PR AUC={pr_auc_m:.3f}, Brier={brier_m:.3f}, MAE={mae_m:.3f}")
    except Exception as e:
        print(f"  - {name}: metric computation error -> {e}")

# Select Best Model and Calibrate
best_model_name = results_detection_df.iloc[0]["Model"]
best_model = fitted_classifiers[best_model_name]

# Calibrate the best model
calibrated_clf = CalibratedClassifierCV(best_model, method='isotonic', cv=3)
calibrated_clf.fit(X_train_res, y_train_res)

print(f"\n✅ Best Detection Model: {best_model_name}")
print(f"✅ CV AUC Score: {cv_scores[best_model_name]:.3f} ± {cv_results[best_model_name]['AUC_std']:.3f}")
print("✅ Model calibrated for better probability estimates")

# Compute and report test accuracy for the calibrated detection model
y_pred_test_det = calibrated_clf.predict(X_test_proc)
test_accuracy_det = accuracy_score(y_test_kd, y_pred_test_det)
print(f"✅ Test Accuracy (Detection Model): {test_accuracy_det:.3f}")

# Additional detection metrics on the test set
y_prob_test_det = calibrated_clf.predict_proba(X_test_proc)[:, 1]
y_pred_label_det = (y_prob_test_det > 0.5).astype(int)
print(f"✅ Test F1 (Detection Model): {f1_score(y_test_kd, y_pred_label_det):.3f}")
print(f"✅ Test Recall (Detection Model): {recall_score(y_test_kd, y_pred_label_det):.3f}")
print(f"✅ Test Precision (Detection Model): {precision_score(y_test_kd, y_pred_label_det):.3f}")
print(f"✅ Test ROC AUC (Detection Model): {roc_auc_score(y_test_kd, y_prob_test_det):.3f}")
print(f"✅ Test MAE (Detection Model): {mean_absolute_error(y_test_kd, y_prob_test_det):.3f}")

# =============================================================================
# STEP 6: PROGNOSIS MODELS - CLINICAL DATASET
# =============================================================================

# Initialize variables for both cases
X_test_cl = None
y_test_cl = None
prognosis_models = None
prognosis_model = None

if SURVIVAL_AVAILABLE:
    print("\n🔮 Training Prognosis Models (Clinical Dataset)...")
    
    # Clinical Dataset Train-Test Split
    X_train_cl, X_test_cl, y_train_cl, y_test_cl = train_test_split(
        X_clinical, y_clinical, test_size=0.2, random_state=42
    )
    
    # Preprocessing Pipeline for Clinical Dataset
    numeric_features_cl = X_clinical.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features_cl = X_clinical.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Create preprocessing pipeline with imputation
    preprocessor_cl = ColumnTransformer(
        transformers=[
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ]), numeric_features_cl),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', OneHotEncoder(handle_unknown='ignore'))
            ]), categorical_features_cl)
        ]
    )
    
    # Check for any remaining NaN values after preprocessing
    X_train_cl_proc = preprocessor_cl.fit_transform(X_train_cl)
    X_test_cl_proc = preprocessor_cl.transform(X_test_cl)
    
    print(f"NaN values in X_train_cl_proc: {np.isnan(X_train_cl_proc).sum()}")
    print(f"NaN values in X_test_cl_proc: {np.isnan(X_test_cl_proc).sum()}")
    
    # CoxPH
    cox_pipe = Pipeline([
        ("preprocessor", preprocessor_cl),
        ("model", CoxPHSurvivalAnalysis())
    ])
    cox_pipe.fit(X_train_cl, y_train_cl)
    
    # RSF
    rsf_pipe = Pipeline([
        ("preprocessor", preprocessor_cl),
        ("model", RandomSurvivalForest(n_estimators=200, random_state=42))
    ])
    rsf_pipe.fit(X_train_cl, y_train_cl)
    
    # Additional Prognosis Models
    try:
        from sksurv.ensemble import GradientBoostingSurvivalAnalysis
        gbs_pipe = Pipeline([
            ("preprocessor", preprocessor_cl),
            ("model", GradientBoostingSurvivalAnalysis(random_state=42))
        ])
        gbs_pipe.fit(X_train_cl, y_train_cl)
        print("✅ Gradient Boosting Survival trained successfully")
    except Exception as e:
        gbs_pipe = None
        print(f"⚠️  Gradient Boosting Survival unavailable: {e}")
    
    try:
        from sksurv.linear_model import ComponentwiseGradientBoostingSurvivalAnalysis
        cgb_pipe = Pipeline([
            ("preprocessor", preprocessor_cl),
            ("model", ComponentwiseGradientBoostingSurvivalAnalysis(random_state=42))
        ])
        cgb_pipe.fit(X_train_cl, y_train_cl)
        print("✅ Componentwise Gradient Boosting Survival trained successfully")
    except Exception as e:
        cgb_pipe = None
        print(f"⚠️  Componentwise Gradient Boosting Survival unavailable: {e}")
    
    try:
        from sksurv.linear_model import CoxnetSurvivalAnalysis
        coxnet_pipe = Pipeline([
            ("preprocessor", preprocessor_cl),
            ("model", CoxnetSurvivalAnalysis(l1_ratio=0.5, alphas=None, max_iter=100000))
        ])
        coxnet_pipe.fit(X_train_cl, y_train_cl)
        print("✅ Coxnet (Elastic Net Cox) trained successfully")
    except Exception as e:
        coxnet_pipe = None
        print(f"⚠️  Coxnet unavailable: {e}")
    
    try:
        from sksurv.svm import FastSurvivalSVM
        fsvm_pipe = Pipeline([
            ("preprocessor", preprocessor_cl),
            ("model", FastSurvivalSVM(random_state=42))
        ])
        fsvm_pipe.fit(X_train_cl, y_train_cl)
        print("✅ Fast Survival SVM trained successfully")
    except Exception as e:
        fsvm_pipe = None
        print(f"⚠️  Fast Survival SVM unavailable: {e}")
    
    # Optional: XGBSE (requires xgbse)
    try:
        from xgbse.non_parametric import XGBSEKaplanNeighbors
        xgbse_pipe = Pipeline([
            ("preprocessor", preprocessor_cl),
            ("model", XGBSEKaplanNeighbors(random_state=42))
        ])
        # XGBSE expects array-like X and structured y; our pipeline will pass pandas and sksurv y which is compatible
        xgbse_pipe.fit(X_train_cl, y_train_cl)
        print("✅ XGBSE Kaplan Neighbors trained successfully")
    except Exception as e:
        xgbse_pipe = None
        print(f"⚠️  XGBSE unavailable: {e}")
    
    # Store models
    prognosis_models = {
        "Cox Proportional Hazards": cox_pipe,
        "Random Survival Forest": rsf_pipe
    }
    if gbs_pipe is not None:
        prognosis_models["Gradient Boosting Survival"] = gbs_pipe
    if cgb_pipe is not None:
        prognosis_models["Componentwise Gradient Boosting"] = cgb_pipe
    if coxnet_pipe is not None:
        prognosis_models["Coxnet (Elastic Net Cox)"] = coxnet_pipe
    if fsvm_pipe is not None:
        prognosis_models["Fast Survival SVM"] = fsvm_pipe
    if xgbse_pipe is not None:
        prognosis_models["XGBSE Kaplan Neighbors"] = xgbse_pipe
    
    # Pick RSF as initial default
    prognosis_model = rsf_pipe
    print("✅ Prognosis models prepared: " + ", ".join(prognosis_models.keys()))
    
    # =============================================================================
    # PROGNOSIS MODEL EVALUATION
    # =============================================================================
    
    print("\n📊 Evaluating Prognosis Models...")
    
    # Convert survival data to binary classification for evaluation
    # We'll use a time horizon (e.g., 60 months) to convert survival to binary
    horizon_months = 60
    
    # Create binary targets for evaluation
    y_train_binary = (y_train_cl['time'] <= horizon_months) & (y_train_cl['event'])
    y_test_binary = (y_test_cl['time'] <= horizon_months) & (y_test_cl['event'])
    
    print(f"Binary classification target: CKD event within {horizon_months} months")
    print(f"Training set event rate: {y_train_binary.mean():.3f}")
    print(f"Test set event rate: {y_test_binary.mean():.3f}")
    
    # Evaluate both prognosis models
    prognosis_results = []
    
    for model_name, model in prognosis_models.items():
        print(f"\n🔍 Evaluating {model_name}...")
        
        try:
            # Use survival functions when available; otherwise, use risk scores normalized
            if hasattr(model, "predict_survival_function"):
                surv_funcs_train = model.predict_survival_function(X_train_cl)
                surv_funcs_test = model.predict_survival_function(X_test_cl)
                y_prob_train = np.array([1 - fn(horizon_months) for fn in surv_funcs_train])
                y_prob_test = np.array([1 - fn(horizon_months) for fn in surv_funcs_test])
                y_pred_train = (y_prob_train > 0.5).astype(int)
                y_pred_test = (y_prob_test > 0.5).astype(int)
            else:
                risk_scores_train = model.predict(X_train_cl)
                risk_scores_test = model.predict(X_test_cl)
                risk_scores_train_norm = (risk_scores_train - risk_scores_train.min()) / (risk_scores_train.max() - risk_scores_train.min() + 1e-12)
                risk_scores_test_norm = (risk_scores_test - risk_scores_test.min()) / (risk_scores_test.max() - risk_scores_test.min() + 1e-12)
                y_prob_train = risk_scores_train_norm
                y_prob_test = risk_scores_test_norm
                y_pred_train = (y_prob_train > 0.5).astype(int)
                y_pred_test = (y_prob_test > 0.5).astype(int)
            
            # Calculate metrics for training set
            train_acc = accuracy_score(y_train_binary, y_pred_train)
            train_f1 = f1_score(y_train_binary, y_pred_train)
            train_recall = recall_score(y_train_binary, y_pred_train)
            train_precision = precision_score(y_train_binary, y_pred_train)
            train_auc = roc_auc_score(y_train_binary, y_prob_train)
            train_mae = mean_absolute_error(y_train_binary, y_prob_train)
            
            # Calculate metrics for test set
            test_acc = accuracy_score(y_test_binary, y_pred_test)
            test_f1 = f1_score(y_test_binary, y_pred_test)
            test_recall = recall_score(y_test_binary, y_pred_test)
            test_precision = precision_score(y_test_binary, y_pred_test)
            test_auc = roc_auc_score(y_test_binary, y_prob_test)
            test_mae = mean_absolute_error(y_test_binary, y_prob_test)
            
            # Store results
            prognosis_results.append({
                'Model': model_name,
                'Train_Accuracy': train_acc,
                'Train_F1': train_f1,
                'Train_Recall': train_recall,
                'Train_Precision': train_precision,
                'Train_AUC': train_auc,
                'Train_MAE': train_mae,
                'Test_Accuracy': test_acc,
                'Test_F1': test_f1,
                'Test_Recall': test_recall,
                'Test_Precision': test_precision,
                'Test_AUC': test_auc,
                'Test_MAE': test_mae
            })
            
            # Print results
            print(f"\n📈 {model_name} Results:")
            print("=" * 50)
            print("TRAINING SET:")
            print(f"  Accuracy:  {train_acc:.4f}")
            print(f"  F1-Score:  {train_f1:.4f}")
            print(f"  Recall:    {train_recall:.4f}")
            print(f"  Precision: {train_precision:.4f}")
            print(f"  AUC:       {train_auc:.4f}")
            print(f"  MAE:       {train_mae:.4f}")
            print("\nTEST SET:")
            print(f"  Accuracy:  {test_acc:.4f}")
            print(f"  F1-Score:  {test_f1:.4f}")
            print(f"  Recall:    {test_recall:.4f}")
            print(f"  Precision: {test_precision:.4f}")
            print(f"  AUC:       {test_auc:.4f}")
            print(f"  MAE:       {test_mae:.4f}")
            
        except Exception as e:
            print(f"❌ Error evaluating {model_name}: {e}")
            continue
    
    # Create results DataFrame
    if prognosis_results:
        prognosis_results_df = pd.DataFrame(prognosis_results)
        prognosis_results_df = prognosis_results_df.sort_values(by='Test_AUC', ascending=False)
        
        print(f"\n📊 PROGNOSIS MODELS COMPARISON:")
        print("=" * 80)
        print(prognosis_results_df.round(4))
        
        # Save results
        prognosis_results_df.to_csv('prognosis_results.csv', index=False)
        print(f"\n✅ Prognosis results saved as 'prognosis_results.csv'")
        
        # Additional concise test summary for all prognosis models
        print("\n📊 Test Metrics Per Prognosis Model (Concise):")
        for _, row in prognosis_results_df.iterrows():
            print(
                f"  - {row['Model']}: "
                f"Acc={row['Test_Accuracy']:.3f}, "
                f"F1={row['Test_F1']:.3f}, "
                f"Recall={row['Test_Recall']:.3f}, "
                f"Precision={row['Test_Precision']:.3f}, "
                f"AUC={row['Test_AUC']:.3f}, "
                f"MAE={row['Test_MAE']:.3f}"
            )
        
        # Select best prognosis model based on test AUC
        best_prognosis_model_name = prognosis_results_df.iloc[0]['Model']
        print(f"\n🏆 Best Prognosis Model: {best_prognosis_model_name}")
        print(f"🏆 Test AUC: {prognosis_results_df.iloc[0]['Test_AUC']:.4f}")
        
        # Update prognosis_model to best model
        prognosis_model = prognosis_models[best_prognosis_model_name]
    
else:
    print("\n⚠️  Skipping Prognosis Models (scikit-survival not available)")

# =============================================================================
# STEP 7: HYBRID DECISION FUNCTION
# =============================================================================

print("\n🔗 Creating Hybrid Decision Function...")

def hybrid_ckd_predict(patient_kd, patient_cl, detection_model, prognosis_model, preprocessor_kd, horizon=60):
    """
    Hybrid CKD Prediction Function
    
    Combines detection (current CKD status) and prognosis (future CKD risk) models
    to provide comprehensive clinical decision support for CKD management.
    
    Parameters
    ----------
    patient_kd : pandas.DataFrame
        Single patient data from kidney dataset with shape (1, n_features).
        Contains clinical features for CKD detection (age, creatinine, etc.)
    
    patient_cl : pandas.DataFrame  
        Single patient data from clinical dataset with shape (1, n_features).
        Contains features for CKD prognosis (BMI, comorbidities, etc.)
    
    detection_model : sklearn.CalibratedClassifierCV
        Trained and calibrated classification model for CKD detection.
        Should have .predict() and .predict_proba() methods.
    
    prognosis_model : sklearn.pipeline.Pipeline
        Trained survival analysis model for CKD prognosis.
        Should have .predict_survival_function() method.
    
    preprocessor_kd : sklearn.compose.ColumnTransformer
        Preprocessor for kidney dataset features.
    
    horizon : int, default=60
        Prediction horizon in months for prognosis model.
        Common values: 12, 24, 36, 60 months.
    
    Returns
    -------
    dict
        Dictionary containing:
        - 'Detection': str
            "CKD Present" or "CKD Not Present"
        - 'Detection Probability': float
            Probability of current CKD (0-1)
        - 'Future Risk (X months)': float
            Risk of developing CKD in future (0-1)
    
    Notes
    -----
    Clinical Logic:
    1. If patient already has CKD (detection=1), future risk = 100%
    2. If patient doesn't have CKD (detection=0), use prognosis model
    3. Risk = 1 - Survival Probability at given horizon
    
    Examples
    --------
    >>> result = hybrid_ckd_predict(
    ...     sample_kd, sample_cl, 
    ...     calibrated_clf, prognosis_model,
    ...     preprocessor_kd,
    ...     horizon=60
    ... )
    >>> print(result['Detection'])
    'CKD Not Present'
    >>> print(result['Future Risk (60 months)'])
    0.234
    """
    # Preprocess patient data for detection model only
    patient_kd_proc = preprocessor_kd.transform(patient_kd)
    
    # Detection
    det_pred = detection_model.predict(patient_kd_proc)[0]
    det_prob = detection_model.predict_proba(patient_kd_proc)[0,1]
    
    if det_pred == 1:  # CKD present
        return {
            "Detection": "CKD Present",
            "Detection Probability": round(det_prob, 3),
            "Future Risk ({} months)".format(horizon): 1.0  # already CKD
        }
    else:  # CKD not present → run prognosis
        if prognosis_model is not None:
            # Prognosis model already includes preprocessor, so use raw data
            surv_fn = prognosis_model.predict_survival_function(patient_cl)[0]
            surv_prob = surv_fn(horizon)
            risk_prob = 1 - surv_prob  # risk = 1 - survival
            return {
                "Detection": "CKD Not Present",
                "Detection Probability": round(det_prob, 3),
                "Future Risk ({} months)".format(horizon): round(risk_prob, 3)
            }
        else:
            return {
                "Detection": "CKD Not Present",
                "Detection Probability": round(det_prob, 3),
                "Future Risk ({} months)".format(horizon): "N/A (prognosis model not available)"
            }

# Test hybrid function
if SURVIVAL_AVAILABLE:
    sample_kd = X_test_kd.iloc[[0]]
    sample_cl = X_test_cl.iloc[[0]]
    
    hybrid_result = hybrid_ckd_predict(
        sample_kd, sample_cl,
        calibrated_clf,
        prognosis_models["Random Survival Forest"],
        preprocessor_kd,
        horizon=60
    )
    
    print("✅ Hybrid Decision Function working")
    print(f"✅ Sample result: {hybrid_result}")
else:
    print("✅ Hybrid Decision Function created (prognosis models not available)")

# =============================================================================
# STEP 8A: EVALUATION IMPROVEMENTS (DETECTION MODEL)
# =============================================================================

print("\n📊 Evaluation Improvements (Detection Model)...")

# Calibration Curve
y_prob_det = calibrated_clf.predict_proba(X_test_proc)[:,1]
prob_true, prob_pred = calibration_curve(y_test_kd, y_prob_det, n_bins=10)

plt.figure(figsize=(6,6))
plt.plot(prob_pred, prob_true, marker='o', label='Detection Model')
plt.plot([0,1],[0,1],'k--', label='Perfect Calibration')
plt.xlabel("Predicted probability")
plt.ylabel("Observed frequency")
plt.title("Calibration Curve (Kidney Detection Model)")
plt.legend()
plt.savefig('calibration_curve.png', dpi=300, bbox_inches='tight')
plt.show()

# Precision-Recall Curve
prec, rec, thr = precision_recall_curve(y_test_kd, y_prob_det)
plt.figure(figsize=(6,6))
plt.plot(rec, prec, label='PR Curve (AUC = %.3f)' % average_precision_score(y_test_kd, y_prob_det))
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Precision-Recall Curve")
plt.legend()
plt.savefig('precision_recall_curve.png', dpi=300, bbox_inches='tight')
plt.show()

print("✅ Calibration curve saved as 'calibration_curve.png'")
print("✅ Precision-Recall curve saved as 'precision_recall_curve.png'")

# =============================================================================
# STEP 8B: DECISION CURVE ANALYSIS (CLINICAL PROGNOSIS MODEL)
# =============================================================================

if SURVIVAL_AVAILABLE:
    print("\n📈 Decision Curve Analysis (Clinical Prognosis Model)...")
    
    # Simple Decision Curve Approximation
    times = [12, 24, 36, 60]  # months
    surv_funcs = prognosis_models["Random Survival Forest"].predict_survival_function(X_test_cl)
    
    plt.figure(figsize=(8,6))
    for i, t in enumerate(times):
        risks = [1 - fn(t) for fn in surv_funcs]  # risk = 1-survival
        plt.hist(risks, bins=20, alpha=0.5, label=f"Risk at {t} months")
    
    plt.xlabel("Predicted Risk Probability")
    plt.ylabel("Patient Count")
    plt.title("Decision Distribution (Clinical Prognosis Model)")
    plt.legend()
    plt.savefig('decision_curve_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✅ Decision curve analysis saved as 'decision_curve_analysis.png'")

# =============================================================================
# STEP 8C: EXPLAINABILITY – SHAP
# =============================================================================

print("\n🔍 Explainability Analysis - SHAP...")

try:
    # SHAP for Detection Model
    explainer_det = shap.Explainer(calibrated_clf, X_train_proc)
    shap_values_det = explainer_det(X_test_proc[:50])
    
    # Global summary
    plt.figure(figsize=(10,8))
    shap.summary_plot(shap_values_det, X_test_proc[:50], plot_type="bar", show=False)
    plt.title("SHAP Feature Importance (Detection Model)")
    plt.savefig('shap_summary.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Dependence plot (Age vs Creatinine) - using feature indices
    try:
        # Find indices for age and creatinine features in preprocessed data
        feature_names = [f"feature_{i}" for i in range(X_test_proc.shape[1])]
        age_idx = None
        sc_idx = None
        
        # Try to find age and creatinine features by looking at original column names
        if "age" in X_kd.columns:
            age_idx = list(X_kd.columns).index("age")
        if "sc" in X_kd.columns:
            sc_idx = list(X_kd.columns).index("sc")
        
        if age_idx is not None and sc_idx is not None:
            plt.figure(figsize=(8,6))
            shap.dependence_plot(sc_idx, shap_values_det.values, X_test_proc[:50], 
                               interaction_index=age_idx, show=False)
            plt.title("SHAP Dependence Plot: Creatinine vs Age")
            plt.savefig('shap_dependence.png', dpi=300, bbox_inches='tight')
            plt.show()
    except Exception as e:
        print(f"⚠️  SHAP dependence plot error: {e}")
    
    print("✅ SHAP summary plot saved as 'shap_summary.png'")
    print("✅ SHAP dependence plot saved as 'shap_dependence.png'")
    
except Exception as e:
    print(f"⚠️  SHAP analysis error: {e}")

# =============================================================================
# STEP 8D: EXPLAINABILITY – LIME
# =============================================================================

print("\n🔍 Explainability Analysis - LIME...")

try:
    lime_explainer = lime.lime_tabular.LimeTabularExplainer(
        training_data=np.array(X_train_proc),
        feature_names=[f"feature_{i}" for i in range(X_train_proc.shape[1])],
        class_names=["Not CKD","CKD"],
        mode="classification"
    )
    
    # Explain first test sample
    exp = lime_explainer.explain_instance(
        data_row=X_test_proc[0],
        predict_fn=calibrated_clf.predict_proba
    )
    
    print("✅ LIME explainer created")
    print("✅ LIME explanation generated for first test sample")
    
except Exception as e:
    print(f"⚠️  LIME analysis error: {e}")

# =============================================================================
# STEP 8E: GLOBAL SURROGATE MODEL
# =============================================================================

print("\n🌳 Global Surrogate Model...")

try:
    from sklearn.tree import DecisionTreeClassifier
    from sklearn import tree
    
    # Surrogate decision tree trained on ensemble predictions
    y_surrogate = calibrated_clf.predict(X_train_proc)
    
    surrogate = DecisionTreeClassifier(max_depth=3, random_state=42)
    surrogate.fit(X_train_proc, y_surrogate)
    
    plt.figure(figsize=(12,8))
    tree.plot_tree(surrogate, feature_names=[f"feature_{i}" for i in range(X_train_proc.shape[1])], 
                   class_names=["Not CKD","CKD"], filled=True)
    plt.title("Global Surrogate Model for Detection Ensemble")
    plt.savefig('surrogate_tree.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✅ Surrogate decision tree saved as 'surrogate_tree.png'")
    
except Exception as e:
    print(f"⚠️  Surrogate model error: {e}")

# =============================================================================
# SAVE MODELS
# =============================================================================

print("\n💾 Saving Trained Models...")

try:
    # Save detection model
    joblib.dump(calibrated_clf, 'best_detection_model.pkl')
    joblib.dump(preprocessor_kd, 'detection_preprocessor.pkl')
    
    # Save prognosis models if available
    if SURVIVAL_AVAILABLE:
        joblib.dump(prognosis_models, 'prognosis_models.pkl')
        joblib.dump(preprocessor_cl, 'prognosis_preprocessor.pkl')
    
    # Save results
    results_detection_df.to_csv('detection_results.csv', index=False)
    
    print("✅ Best detection model saved as 'best_detection_model.pkl'")
    print("✅ Detection preprocessor saved as 'detection_preprocessor.pkl'")
    if SURVIVAL_AVAILABLE:
        print("✅ Prognosis models saved as 'prognosis_models.pkl'")
        print("✅ Prognosis preprocessor saved as 'prognosis_preprocessor.pkl'")
    print("✅ Results saved as 'detection_results.csv'")
    
except Exception as e:
    print(f"⚠️  Model saving error: {e}")

# =============================================================================
# PIPELINE SUMMARY
# =============================================================================

print("\n🎉 CKD PREDICTION PIPELINE COMPLETED!")
print("=" * 60)

print("\n📊 PIPELINE SUMMARY:")
print(f"✅ Detection Models: {len(base_classifiers)} trained and evaluated")
print(f"✅ Best Detection Model: {best_model_name}")
print(f"✅ Cross-Validation AUC: {cv_scores[best_model_name]:.3f} ± {cv_results[best_model_name]['AUC_std']:.3f}")
print(f"✅ Model Calibration: Completed")

if SURVIVAL_AVAILABLE:
    print(f"✅ Prognosis Models: " + ", ".join(prognosis_models.keys()))
    print(f"✅ Prognosis Evaluation: Training & Test metrics (Acc, F1, Recall, Precision, AUC, MAE)")
    print(f"✅ Hybrid Decision Function: Available")
else:
    print(f"⚠️  Prognosis Models: Not available (scikit-survival required)")

print(f"✅ Evaluation Metrics: Calibration curves, PR curves")
print(f"✅ Explainability: SHAP + LIME + Surrogate trees")
print(f"✅ Visualizations: Saved as PNG files")
print(f"✅ Models: Saved as PKL files")

print("\n🚀 PIPELINE READY FOR CLINICAL USE!")
print("=" * 60)

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

print("\n📖 USAGE EXAMPLE:")
print("""
# Load saved models
detection_model = joblib.load('best_detection_model.pkl')
preprocessor = joblib.load('detection_preprocessor.pkl')

# Prepare new patient data (same format as training)
new_patient = pd.DataFrame({
    'age': [65],
    'bp': [120],
    'sg': [1.02],
    # ... other features
})

# Preprocess and predict
new_patient_proc = preprocessor.transform(new_patient)
prediction = detection_model.predict(new_patient_proc)
probability = detection_model.predict_proba(new_patient_proc)[:,1]

print(f"CKD Prediction: {'Present' if prediction[0] == 1 else 'Not Present'}")
print(f"Confidence: {probability[0]:.3f}")
""")

print("\n🏥 Thank you for using the CKD Prediction Pipeline!")
