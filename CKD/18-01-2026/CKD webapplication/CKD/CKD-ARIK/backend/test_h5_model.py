import requests
import json

def test_h5_model():
    """Test if the H5 deep learning model is working in the ensemble"""
    
    print("🔍 TESTING H5 DEEP LEARNING MODEL")
    print("=" * 50)
    
    # Test with a high-risk patient
    test_data = {
        'age': 75,
        'cholesterol': 300,
        'triglycerides': 400,
        'hba1c': 11.5,
        'creatinine': 4.5,
        'egfr': 25,
        'sbp': 180,
        'dbp': 110,
        'bmi': 38,
        'time_to_event': 36,
        'gender': 1,
        'diabetes': 1,
        'chd': 1,
        'vascular': 1,
        'smoking': 1,
        'htn': 1,
        'dld': 1,
        'obesity': 1,
        'dld_meds': 1,
        'dm_meds': 1,
        'htn_meds': 1,
        'acei_arb': 1
    }
    
    print("📋 Test Patient: High-risk CKD profile")
    print("   - Age: 75 years")
    print("   - Creatinine: 4.5 mg/dL")
    print("   - eGFR: 25 mL/min/1.73m²")
    print("   - HbA1c: 11.5%")
    print("   - Multiple comorbidities")
    print()
    
    try:
        print("🔄 Sending prediction request...")
        response = requests.post('http://localhost:8000/predict', json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response Received:")
            print(f"   Prediction: {result['prediction']}")
            print(f"   Probability: {result['probability']:.3f}")
            print(f"   CKD Detected: {result['ckd']}")
            print()
            print("🤖 ENSEMBLE STATUS:")
            print("   Check the backend server logs for details:")
            print("   - Look for: 'Ensemble: ML=X.XXX, DL=X.XXX, Final=X.XXX'")
            print("   - If H5 model works: Both ML and DL values shown")
            print("   - If H5 model fails: 'DL model prediction failed' message")
            print()
            print("📊 SHAP Values:")
            for feature, value in result['shap'].items():
                print(f"   {feature}: {value:.3f}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print()
    print("=" * 50)
    print("🔧 H5 MODEL STATUS CHECK")
    print("=" * 50)
    
    # Check if H5 model file exists and is loadable
    try:
        from tensorflow.keras.models import load_model
        import os
        
        h5_path = "models/ckd_model.h5"
        if os.path.exists(h5_path):
            print(f"✅ H5 file found: {h5_path}")
            
            try:
                model = load_model(h5_path)
                print(f"✅ H5 model loaded successfully")
                print(f"   Model type: {type(model).__name__}")
                
                # Try to get model summary
                try:
                    print(f"   Model input shape: {model.input_shape}")
                    print(f"   Model output shape: {model.output_shape}")
                except:
                    print("   Could not get model shapes")
                
            except Exception as e:
                print(f"❌ H5 model loading failed: {e}")
        else:
            print(f"❌ H5 file not found: {h5_path}")
            
    except ImportError:
        print("❌ TensorFlow not installed - H5 model cannot be used")
    
    print()
    print("📋 HEALTH CHECK:")
    try:
        health_response = requests.get('http://localhost:8000/health', timeout=5)
        if health_response.status_code == 200:
            health = health_response.json()
            print(f"   ML Model Loaded: {health['ml_model_loaded']}")
            print(f"   DL Model Loaded: {health['dl_model_loaded']}")
            print(f"   SHAP Explainer: {health['shap_explainer_loaded']}")
            
            if health['dl_model_loaded']:
                print("✅ H5 model is active in ensemble")
            else:
                print("❌ H5 model is not loaded")
        else:
            print("❌ Health check failed")
    except Exception as e:
        print(f"❌ Health check error: {e}")

if __name__ == "__main__":
    test_h5_model()
