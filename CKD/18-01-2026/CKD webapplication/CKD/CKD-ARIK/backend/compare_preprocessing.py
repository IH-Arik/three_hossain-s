"""
Compare preprocessing between web input and training data
"""

import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from utils.edckd_preprocessor import create_edckd_preprocessor

def compare_preprocessing():
    """Compare web input preprocessing with training data preprocessing"""
    
    print("🔍 COMPARING PREPROCESSING METHODS")
    print("=" * 50)
    
    try:
        # Load preprocessor and model
        preprocessor = create_edckd_preprocessor()
        if not preprocessor.is_fitted:
            preprocessor.fit_from_dataset('../pone.0199920.s002.xlsx')
        
        model = load_model('models/ckd_model.h5')
        print("✅ Model and preprocessor loaded")
        
        # Load training data
        df = pd.read_excel('../pone.0199920.s002.xlsx')
        
        # Test with first training patient
        training_patient = df.iloc[0]
        print(f"\n📋 Training Patient {training_patient['StudyID']}:")
        print(f"   Actual CKD: {training_patient['EventCKD35']}")
        
        # Method 1: Direct preprocessing (like in debug_h5.py)
        features = (preprocessor.dataset_config['numerical_cols'] + 
                   preprocessor.dataset_config['binary_categorical_cols'] + 
                   preprocessor.dataset_config['non_binary_categorical_cols'])
        
        patient_data = {}
        for feature in features:
            if feature in training_patient:
                patient_data[feature] = training_patient[feature]
        
        patient_df = pd.DataFrame([patient_data])
        X_direct = preprocessor.preprocessor.transform(patient_df)
        
        # Method 2: Web input preprocessing (like in app.py)
        web_data = {
            'age': float(training_patient['AgeBaseline']),
            'cholesterol': float(training_patient['CholesterolBaseline']),
            'triglycerides': float(training_patient['TriglyceridesBaseline']),
            'hba1c': float(training_patient['HgbA1C']),
            'creatinine': float(training_patient['CreatnineBaseline']) / 88.4,  # Convert to mg/dL
            'egfr': float(training_patient['eGFRBaseline']),
            'sbp': float(training_patient['sBPBaseline']),
            'dbp': float(training_patient['dBPBaseline']),
            'bmi': float(training_patient['BMIBaseline']),
            'time_to_event': float(training_patient['TimeToEventMonths']),
            'gender': int(training_patient['Gender']),
            'diabetes': int(training_patient['HistoryDiabetes']),
            'chd': int(training_patient['HistoryCHD']),
            'vascular': int(training_patient['HistoryVascular']),
            'smoking': int(training_patient['HistorySmoking']),
            'htn': int(training_patient['HistoryHTN ']),
            'dld': int(training_patient['HistoryDLD']),
            'obesity': int(training_patient['HistoryObesity']),
            'dld_meds': int(training_patient['DLDmeds']),
            'dm_meds': int(training_patient['DMmeds']),
            'htn_meds': int(training_patient['HTNmeds']),
            'acei_arb': int(training_patient['ACEIARB'])
        }
        
        # Map web form fields to dataset features
        feature_mapping = preprocessor.get_web_form_mapping()
        model_data = {}
        
        for web_field, model_feature in feature_mapping.items():
            if web_field in web_data:
                # Convert creatinine from mg/dL to μmol/L (dataset units)
                if web_field == 'creatinine':
                    model_data[model_feature] = web_data[web_field] * 88.4
                else:
                    model_data[model_feature] = web_data[web_field]
        
        X_web = preprocessor.transform_web_input(model_data)
        
        # Compare the two methods
        print(f"\n📊 Direct preprocessing shape: {X_direct.shape}")
        print(f"📊 Web preprocessing shape: {X_web.shape}")
        
        print(f"\n🔍 Direct preprocessing sample: {X_direct[0][:5]}")
        print(f"🔍 Web preprocessing sample: {X_web[0][:5]}")
        
        # Check if they're the same
        difference = np.abs(X_direct - X_web).max()
        print(f"\n📏 Max difference: {difference:.10f}")
        
        if difference < 1e-10:
            print("✅ Preprocessing methods are identical")
        else:
            print("⚠️  Preprocessing methods differ")
        
        # Test predictions
        pred_direct = model.predict(X_direct.astype(np.float32), verbose=0)[0][0]
        pred_web = model.predict(X_web.astype(np.float32), verbose=0)[0][0]
        
        print(f"\n🤖 Direct prediction: {pred_direct:.6f}")
        print(f"🤖 Web prediction: {pred_web:.6f}")
        print(f"📏 Prediction difference: {abs(pred_direct - pred_web):.6f}")
        
        # Test with a few more patients
        print(f"\n🧪 Testing with 5 more patients...")
        for i in range(1, min(6, len(df))):
            patient = df.iloc[i]
            
            # Direct method
            patient_data = {}
            for feature in features:
                if feature in patient:
                    patient_data[feature] = patient[feature]
            patient_df = pd.DataFrame([patient_data])
            X_direct = preprocessor.preprocessor.transform(patient_df)
            pred_direct = model.predict(X_direct.astype(np.float32), verbose=0)[0][0]
            
            # Web method
            web_data = {
                'age': float(patient['AgeBaseline']),
                'creatinine': float(patient['CreatnineBaseline']) / 88.4,
                'egfr': float(patient['eGFRBaseline']),
                'gender': int(patient['Gender']),
                'htn': int(patient['HistoryHTN ']),
                # ... other fields would be filled in
            }
            
            # For simplicity, just test a few key fields
            feature_mapping = preprocessor.get_web_form_mapping()
            model_data = {}
            for web_field, model_feature in feature_mapping.items():
                if web_field in web_data:
                    if web_field == 'creatinine':
                        model_data[model_feature] = web_data[web_field] * 88.4
                    else:
                        model_data[model_feature] = web_data[web_field]
            
            # Fill missing fields with defaults
            for feature in features:
                if feature not in model_data:
                    if feature in preprocessor.dataset_config['numerical_cols']:
                        model_data[feature] = 0.0
                    elif feature == 'Age.3.categories':
                        model_data[feature] = 'middle'
                    else:
                        model_data[feature] = 0
            
            X_web = preprocessor.transform_web_input(model_data)
            pred_web = model.predict(X_web.astype(np.float32), verbose=0)[0][0]
            
            print(f"   Patient {patient['StudyID']}: Direct={pred_direct:.4f}, Web={pred_web:.4f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_preprocessing()
