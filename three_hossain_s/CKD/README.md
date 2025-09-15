# 🏥 Chronic Kidney Disease (CKD) Prediction Pipeline

A comprehensive machine learning pipeline for **CKD detection** and **prognosis** using hybrid clinical decision support.

## 📋 Overview

This pipeline implements a novel **hybrid approach** that combines:
- **Detection Model**: Diagnoses current CKD status (present/absent)
- **Prognosis Model**: Predicts future CKD risk over time
- **Clinical Decision Support**: Integrates both models for comprehensive patient assessment

## 🎯 Key Features

### ✅ **Dual-Dataset Architecture**
- **Kidney Dataset** (400 patients): Clinical features for CKD detection
- **Clinical Dataset** (491 patients): Longitudinal data for prognosis

### ✅ **Comprehensive Model Suite**
- **13 Detection Models**: Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost, etc.
- **2 Survival Models**: Cox Proportional Hazards + Random Survival Forest
- **Cross-Validation**: 5-fold stratified CV for robust evaluation

### ✅ **Clinical Preprocessing**
- **Clinically-aware imputation**: Normal ranges for lab values
- **Feature engineering**: Urea-creatinine ratio, anemia flags, metabolic syndrome
- **Outlier handling**: Clinically impossible values capped appropriately
- **Class imbalance**: BorderlineSMOTE for realistic representation

### ✅ **Advanced Evaluation**
- **Detection metrics**: ROC-AUC, PR-AUC, Brier Score, Calibration curves
- **Prognosis metrics**: Concordance index, time-dependent Brier score
- **Cross-validation**: Stratified CV with mean ± std reporting

### ✅ **Explainability Suite**
- **SHAP**: Global feature importance and interaction plots
- **LIME**: Local explanations for individual patients
- **Surrogate trees**: Clinician-friendly decision rules

## 🚀 Quick Start

### Prerequisites
```bash
pip install pandas numpy scikit-learn imblearn lightgbm xgboost catboost shap lime matplotlib seaborn joblib openpyxl scikit-survival lifelines
```

### Dataset Setup
Place your datasets in the project directory:
- `kidney_disease.csv` - CKD detection dataset
- `pone.0199920.s002.xlsx` - Clinical prognosis dataset

### Run Pipeline
```python
# Execute cells in order:
# 1. Install dependencies (Cells 0-3)
# 2. Import libraries (Cell 5)
# 3. Load datasets (Cell 7)
# 4. Preprocess data (Cells 9, 11)
# 5. Train models (Cells 13, 15)
# 6. Hybrid prediction (Cell 17)
# 7. Evaluation & explainability (Cells 19-27)
```

## 📊 Pipeline Architecture

```
Patient Data
    ↓
┌─────────────────────────────────────┐
│           Detection Model           │
│        (Kidney Dataset)             │
│     Current CKD Status?             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│         Clinical Decision           │
│                                     │
│  CKD Present? → Risk = 100%         │
│  CKD Absent? → Prognosis Model      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│         Prognosis Model             │
│       (Clinical Dataset)            │
│    Future CKD Risk (60 months)      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│        Final Decision               │
│   Detection + Prognosis Result      │
└─────────────────────────────────────┘
```

## 🔬 Methodology

### Detection Model (Kidney Dataset)
- **Target**: Binary classification (CKD present/absent)
- **Features**: 27 clinical features (age, creatinine, hemoglobin, etc.)
- **Preprocessing**: StandardScaler + OneHotEncoder + BorderlineSMOTE
- **Models**: 13 classifiers with cross-validation
- **Best Model**: Selected by CV AUC score

### Prognosis Model (Clinical Dataset)
- **Target**: Survival analysis (time-to-event + event status)
- **Features**: 25 clinical features (BMI, comorbidities, lab values)
- **Models**: Cox Proportional Hazards + Random Survival Forest
- **Evaluation**: Concordance index, survival curves

### Hybrid Integration
```python
def hybrid_ckd_predict(patient_kd, patient_cl, detection_model, prognosis_model, horizon=60):
    """
    Combines detection and prognosis for comprehensive clinical decision support.
    
    Clinical Logic:
    1. If CKD present → Future risk = 100%
    2. If CKD absent → Use prognosis model for future risk
    3. Return detection + prognosis results
    """
```

## 📈 Results & Performance

### Detection Model Performance
- **Best Model**: [Selected by CV AUC]
- **CV AUC Score**: [Mean ± Std]
- **Calibration**: Isotonic regression for probability calibration

### Prognosis Model Performance
- **CoxPH**: Interpretable hazard ratios
- **Random Survival Forest**: Non-linear interactions
- **C-index**: Concordance index for discrimination

### Clinical Utility
- **Decision Support**: Combines immediate diagnosis + future risk
- **Explainability**: SHAP + LIME + Surrogate trees
- **Calibration**: Clinically interpretable probabilities

## 🛠️ Technical Details

### Dependencies
```
pandas>=1.3.0
numpy>=1.21.0
scikit-learn>=1.0.0
imbalanced-learn>=0.8.0
lightgbm>=3.2.0
xgboost>=1.5.0
catboost>=1.0.0
shap>=0.40.0
lime>=0.2.0
matplotlib>=3.5.0
seaborn>=0.11.0
scikit-survival>=0.17.0
lifelines>=0.27.0
```

### File Structure
```
CKD/
├── journal-based-ckd.ipynb    # Main pipeline notebook
├── ckd.py                     # Python script version
├── README.md                  # This file
├── kidney_disease.csv         # Detection dataset
└── pone.0199920.s002.xlsx     # Prognosis dataset
```

## 🔍 Explainability Features

### SHAP Analysis
- **Global importance**: Feature rankings across all patients
- **Interaction plots**: Age × Creatinine interactions
- **Summary plots**: Comprehensive feature analysis

### LIME Explanations
- **Local explanations**: Individual patient risk breakdown
- **Feature contributions**: Why specific predictions were made
- **Clinical interpretability**: Easy-to-understand explanations

### Surrogate Models
- **Decision trees**: Black-box ensemble → interpretable rules
- **Clinical rules**: Simple if-then logic for clinicians
- **Global patterns**: Overall model behavior summary

## 📚 Clinical Applications

### Primary Care
- **Screening**: Identify patients at risk for CKD
- **Monitoring**: Track CKD progression over time
- **Prevention**: Early intervention strategies

### Nephrology
- **Diagnosis**: Confirm CKD presence and stage
- **Prognosis**: Predict disease progression
- **Treatment**: Personalized management plans

### Research
- **Risk factors**: Identify key predictors
- **Biomarkers**: Discover new diagnostic markers
- **Interventions**: Test prevention strategies

## 🎓 Research Impact

### Novel Contributions
1. **Hybrid Architecture**: First to combine detection + prognosis
2. **Clinical Integration**: Mirrors real-world decision making
3. **Comprehensive Evaluation**: Beyond accuracy metrics
4. **Explainable AI**: Clinician-friendly interpretations

### Publication Quality
- **Methodology**: Rigorous ML pipeline with CV
- **Clinical Relevance**: Grounded in medical practice
- **Reproducibility**: Complete code and documentation
- **Innovation**: Novel hybrid approach

## 🤝 Contributing

### Issues & Bugs
- Report issues via GitHub issues
- Include error messages and data samples
- Provide system information

### Feature Requests
- Suggest new models or metrics
- Propose clinical improvements
- Request additional explainability features

### Code Contributions
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new functions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

For questions, suggestions, or collaborations:
- **Email**: [Your Email]
- **GitHub**: [Your GitHub Profile]
- **Research**: [Your Research Profile]

## 🙏 Acknowledgments

- **Datasets**: Kidney disease dataset, Clinical prognosis dataset
- **Libraries**: scikit-learn, scikit-survival, SHAP, LIME
- **Clinical Advisors**: [Clinical collaborators]
- **Research Community**: Open source ML community

---

**🏥 Built for Clinical Decision Support | 🔬 Research-Grade ML Pipeline | 📊 Publication-Ready Results**
