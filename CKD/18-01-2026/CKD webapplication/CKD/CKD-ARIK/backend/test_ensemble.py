import requests

def test_ensemble():
    """Test ensemble with high-risk patient"""
    
    print("🔍 TESTING ENSEMBLE WITH HIGH-RISK PATIENT")
    print("=" * 50)
    
    # Test with high-risk patient
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
    
    print("📋 High-risk patient profile:")
    print("   - Age: 75 years")
    print("   - Creatinine: 4.5 mg/dL")
    print("   - eGFR: 25 mL/min/1.73m²")
    print("   - HbA1c: 11.5%")
    print("   - Multiple comorbidities")
    print()
    
    try:
        print("🔄 Sending request...")
        response = requests.post('http://localhost:8000/predict', json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Response received:")
            print(f"   Prediction: {result['prediction']}")
            print(f"   Probability: {result['probability']:.6f}")
            print(f"   CKD Detected: {result['ckd']}")
            print()
            print("🤖 Check backend logs for ensemble details:")
            print("   Look for: 'Ensemble: ML=X.XXX, DL=X.XXX, Final=X.XXX'")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_ensemble()
