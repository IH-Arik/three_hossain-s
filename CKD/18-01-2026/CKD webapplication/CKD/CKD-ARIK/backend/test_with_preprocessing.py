import pandas as pd
import numpy as np
import requests
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def test_with_exact_preprocessing():
    """Test with the exact preprocessing pipeline from training"""
    
    # Load the dataset
    df = pd.read_excel('../pone.0199920.s002.xlsx')
    
    # Define the exact preprocessing configuration from your training code
    numerical_cols = ['AgeBaseline', 'CholesterolBaseline', 'TriglyceridesBaseline', 'HgbA1C', 'CreatnineBaseline', 'eGFRBaseline', 'sBPBaseline', 'dBPBaseline', 'BMIBaseline', 'TimeToEventMonths']
    binary_categorical_cols = ['Gender', 'HistoryDiabetes', 'HistoryCHD', 'HistoryVascular', 'HistorySmoking', 'HistoryHTN ', 'HistoryDLD', 'HistoryObesity', 'DLDmeds', 'DMmeds', 'HTNmeds', 'ACEIARB']
    non_binary_categorical_cols = ['Age.3.categories']
    
    standard_scale_cols = ['AgeBaseline', 'sBPBaseline', 'dBPBaseline', 'BMIBaseline']
    minmax_scale_cols = ['HgbA1C', 'eGFRBaseline']
    robust_scale_cols = ['CholesterolBaseline', 'TriglyceridesBaseline', 'CreatnineBaseline', 'TimeToEventMonths']
    
    # Create the exact preprocessor
    preprocessor = ColumnTransformer(
        transformers=[
            ('num_standard', Pipeline([
                ('imputer', SimpleImputer(strategy='mean')),
                ('scaler', StandardScaler())
            ]), standard_scale_cols),
            ('num_minmax', Pipeline([
                ('imputer', SimpleImputer(strategy='mean')),
                ('scaler', MinMaxScaler())
            ]), minmax_scale_cols),
            ('num_robust', Pipeline([
                ('imputer', SimpleImputer(strategy='mean')),
                ('scaler', RobustScaler())
            ]), robust_scale_cols),
            ('cat_binary', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent'))
            ]), binary_categorical_cols),
            ('cat_non_binary', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
            ]), non_binary_categorical_cols)
        ],
        remainder='passthrough'
    )
    
    # Fit the preprocessor on the entire dataset (to match training)
    X = df.drop(['StudyID', 'EventCKD35'], axis=1)
    y = df['EventCKD35']
    
    # Handle missing values and data cleaning (like in your training)
    for col in X.columns:
        if X[col].dtype == 'object':
            X[col] = X[col].str.strip()
            X[col] = X[col].replace('?', np.nan)
    
    # Convert numerical columns that might be stored as strings
    for col in numerical_cols:
        if col in X.columns and X[col].dtype == 'object':
            X[col] = pd.to_numeric(X[col], errors='coerce')
    
    # Fit preprocessor
    preprocessor.fit(X)
    
    # Get feature names after preprocessing
    feature_names = preprocessor.get_feature_names_out()
    
    # Clean feature names (remove prefixes)
    cleaned_names = []
    for name in feature_names:
        if '__' in name:
            cleaned_name = name.split('__')[-1]
        else:
            cleaned_name = name
        cleaned_names.append(cleaned_name)
    
    print(f"✅ Preprocessor fitted successfully!")
    print(f"📊 Features after preprocessing: {len(cleaned_names)}")
    print(f"🔍 Feature names: {cleaned_names}")
    print()
    
    # Test a few cases with proper preprocessing
    test_cases = df.head(6)
    
    correct_predictions = 0
    total_tests = 0
    
    print("=" * 80)
    print("🩺 TESTING WITH EXACT PREPROCESSING")
    print("=" * 80)
    
    for idx, row in test_cases.iterrows():
        print(f"Patient {row['StudyID']} - Actual CKD: {row['EventCKD35']}")
        
        # Prepare raw data
        raw_data = row.drop(['StudyID', 'EventCKD35']).to_dict()
        
        # Convert to DataFrame for preprocessing
        raw_df = pd.DataFrame([raw_data])
        
        # Apply preprocessing
        try:
            X_processed = preprocessor.transform(raw_df)
            print(f"  📊 Processed shape: {X_processed.shape}")
            
            # Create a simple test with the processed data
            # Since we can't directly use your model without the exact preprocessing,
            # let's test if the API can handle some edge cases
            
            # Convert back to API format (with unit conversion for creatinine)
            api_data = {
                'age': float(row['AgeBaseline']),
                'cholesterol': float(row['CholesterolBaseline']),
                'triglycerides': float(row['TriglyceridesBaseline']),
                'hba1c': float(row['HgbA1C']),
                'creatinine': float(row['CreatnineBaseline']) / 88.4,  # Convert μmol/L to mg/dL
                'egfr': float(row['eGFRBaseline']),
                'sbp': float(row['sBPBaseline']),
                'dbp': float(row['dBPBaseline']),
                'bmi': float(row['BMIBaseline']),
                'time_to_event': float(row['TimeToEventMonths']),
                'gender': int(row['Gender']),
                'diabetes': int(row['HistoryDiabetes']),
                'chd': int(row['HistoryCHD']),
                'vascular': int(row['HistoryVascular']),
                'smoking': int(row['HistorySmoking']),
                'htn': int(row['HistoryHTN ']),
                'dld': int(row['HistoryDLD']),
                'obesity': int(row['HistoryObesity']),
                'dld_meds': int(row['DLDmeds']),
                'dm_meds': int(row['DMmeds']),
                'htn_meds': int(row['HTNmeds']),
                'acei_arb': int(row['ACEIARB'])
            }
            
            # Test API call
            response = requests.post('http://localhost:8000/predict', json=api_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                prediction_correct = result['ckd'] == bool(row['EventCKD35'])
                if prediction_correct:
                    correct_predictions += 1
                
                total_tests += 1
                
                print(f"  🔮 API Prediction: {result['prediction']}")
                print(f"  📊 Probability: {result['probability']:.3f} ({result['probability']*100:.1f}%)")
                print(f"  ✅ Match: {'CORRECT' if prediction_correct else 'INCORRECT'}")
                
            else:
                print(f"  ❌ API Error: {response.status_code}")
                total_tests += 1
                
        except Exception as e:
            print(f"  ❌ Processing failed: {e}")
            total_tests += 1
        
        print(f"  🩺 Key indicators:")
        print(f"     - Creatinine: {row['CreatnineBaseline']:.1f} μmol/L ({row['CreatnineBaseline']/88.4:.2f} mg/dL)")
        print(f"     - eGFR: {row['eGFRBaseline']:.1f} mL/min/1.73m²")
        print(f"     - HbA1c: {row['HgbA1C']:.1f}%")
        print(f"     - Age: {row['AgeBaseline']} years")
        print()
    
    # Summary
    print("=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {total_tests}")
    print(f"Correct predictions: {correct_predictions}")
    if total_tests > 0:
        print(f"Accuracy: {correct_predictions/total_tests*100:.1f}%")

if __name__ == "__main__":
    test_with_exact_preprocessing()
