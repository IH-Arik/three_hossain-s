"""
Test script to demonstrate the SHAP explanation UI
"""

import requests
import json

def test_shap_ui():
    """Test the SHAP explanation UI with sample data"""
    
    print("🔍 TESTING SHAP EXPLANATION UI")
    print("=" * 50)
    
    # Sample patient data
    patient_data = {
        'age': 65,
        'cholesterol': 220,
        'triglycerides': 180,
        'hba1c': 7.2,
        'creatinine': 1.8,
        'egfr': 45,
        'sbp': 140,
        'dbp': 85,
        'bmi': 28.5,
        'time_to_event': 24,
        'gender': 1,
        'diabetes': 1,
        'chd': 0,
        'vascular': 0,
        'smoking': 0,
        'htn': 1,
        'dld': 1,
        'obesity': 1,
        'dld_meds': 1,
        'dm_meds': 1,
        'htn_meds': 1,
        'acei_arb': 1
    }
    
    print("📋 Sample Patient Data:")
    print(f"   Age: {patient_data['age']} years")
    print(f"   Creatinine: {patient_data['creatinine']} mg/dL")
    print(f"   eGFR: {patient_data['egfr']} mL/min/1.73m²")
    print(f"   HbA1c: {patient_data['hba1c']}%")
    print(f"   Diabetes: {'Yes' if patient_data['diabetes'] else 'No'}")
    print(f"   Hypertension: {'Yes' if patient_data['htn'] else 'No'}")
    print()
    
    try:
        print("🔄 Getting prediction from API...")
        response = requests.post('http://localhost:8000/predict', json=patient_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Prediction received:")
            print(f"   Result: {result['prediction']}")
            print(f"   Probability: {result['probability']:.3f}")
            print(f"   CKD Detected: {result['ckd']}")
            print()
            print("🧠 SHAP Values:")
            for feature, value in result['shap'].items():
                direction = "↑" if value > 0 else "↓"
                print(f"   {feature}: {value:+.3f} {direction}")
            print()
            print("🎯 INSTRUCTIONS:")
            print("1. Open the main application: http://localhost:8000/frontend/")
            print("2. Fill in the patient data above")
            print("3. Click 'Predict CKD Risk'")
            print("4. Click 'SHAP Analysis' button")
            print("5. View the publication-grade SHAP explanation")
            print()
            print("📊 SHAP Features Available:")
            print("   - Patient risk assessment")
            print("   - Top 8 risk factors with impact bars")
            print("   - Interactive SHAP contribution chart")
            print("   - Clinical insights and recommendations")
            print("   - Methodology explanation")
            print("   - Export options (JSON, Chart Image)")
            print("   - Publication-ready summary")
            print()
            print("🎉 SHAP UI is ready for testing!")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_shap_ui()
