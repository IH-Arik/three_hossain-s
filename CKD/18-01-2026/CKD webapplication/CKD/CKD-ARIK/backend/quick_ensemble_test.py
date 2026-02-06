import requests

def quick_ensemble_test():
    """Quick test to verify H5 model is working in ensemble"""
    
    print("🔍 QUICK ENSEMBLE TEST")
    print("=" * 30)
    
    # Test with moderate risk patient
    test_data = {
        'age': 55,
        'cholesterol': 200,
        'triglycerides': 150,
        'hba1c': 6.5,
        'creatinine': 1.2,
        'egfr': 90,
        'sbp': 130,
        'dbp': 80,
        'bmi': 25,
        'time_to_event': 12,
        'gender': 1,
        'diabetes': 0,
        'chd': 0,
        'vascular': 0,
        'smoking': 0,
        'htn': 1,
        'dld': 0,
        'obesity': 0,
        'dld_meds': 0,
        'dm_meds': 0,
        'htn_meds': 1,
        'acei_arb': 0
    }
    
    print("📋 Test Patient: Moderate risk profile")
    print("   - Age: 55, Creatinine: 1.2, eGFR: 90")
    print("   - Some hypertension, no diabetes")
    print()
    
    try:
        print("🔄 Sending request...")
        response = requests.post('http://localhost:8000/predict', json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Response received:")
            print(f"   Prediction: {result['prediction']}")
            print(f"   Probability: {result['probability']:.3f}")
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
    quick_ensemble_test()
