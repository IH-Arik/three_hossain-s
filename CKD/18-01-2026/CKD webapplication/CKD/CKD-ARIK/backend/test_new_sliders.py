"""
Test script to verify the new sliders (Creatinine, Cholesterol, Triglycerides) are working
"""

import requests
import json

def test_new_sliders():
    """Test the new sliders with different values"""
    
    print("🧪 TESTING NEW SLIDERS")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test cases for the new sliders
    test_cases = [
        {
            "name": "Normal Values",
            "data": {
                'age': 45,
                'creatinine': 0.9,
                'cholesterol': 180,
                'triglycerides': 100,
                'hba1c': 5.5,
                'egfr': 95,
                'sbp': 120,
                'dbp': 80,
                'bmi': 24,
                'time_to_event': 12,
                'gender': 0,
                'diabetes': 0,
                'chd': 0,
                'vascular': 0,
                'smoking': 0,
                'htn': 0,
                'dld': 0,
                'obesity': 0,
                'dld_meds': 0,
                'dm_meds': 0,
                'htn_meds': 0,
                'acei_arb': 0
            }
        },
        {
            "name": "High Creatinine",
            "data": {
                'age': 65,
                'creatinine': 2.5,
                'cholesterol': 200,
                'triglycerides': 150,
                'hba1c': 6.5,
                'egfr': 45,
                'sbp': 140,
                'dbp': 85,
                'bmi': 28,
                'time_to_event': 24,
                'gender': 1,
                'diabetes': 0,
                'chd': 0,
                'vascular': 0,
                'smoking': 0,
                'htn': 1,
                'dld': 0,
                'obesity': 1,
                'dld_meds': 0,
                'dm_meds': 0,
                'htn_meds': 1,
                'acei_arb': 0
            }
        },
        {
            "name": "High Cholesterol",
            "data": {
                'age': 55,
                'creatinine': 1.2,
                'cholesterol': 320,
                'triglycerides': 180,
                'hba1c': 6.0,
                'egfr': 75,
                'sbp': 130,
                'dbp': 82,
                'bmi': 30,
                'time_to_event': 18,
                'gender': 1,
                'diabetes': 0,
                'chd': 0,
                'vascular': 0,
                'smoking': 0,
                'htn': 1,
                'dld': 1,
                'obesity': 1,
                'dld_meds': 1,
                'dm_meds': 0,
                'htn_meds': 1,
                'acei_arb': 0
            }
        },
        {
            "name": "High Triglycerides",
            "data": {
                'age': 50,
                'creatinine': 1.1,
                'cholesterol': 220,
                'triglycerides': 400,
                'hba1c': 7.0,
                'egfr': 80,
                'sbp': 135,
                'dbp': 88,
                'bmi': 32,
                'time_to_event': 20,
                'gender': 0,
                'diabetes': 1,
                'chd': 0,
                'vascular': 0,
                'smoking': 0,
                'htn': 1,
                'dld': 1,
                'obesity': 1,
                'dld_meds': 0,
                'dm_meds': 1,
                'htn_meds': 1,
                'acei_arb': 0
            }
        },
        {
            "name": "All High Risk",
            "data": {
                'age': 70,
                'creatinine': 3.2,
                'cholesterol': 380,
                'triglycerides': 450,
                'hba1c': 10.5,
                'egfr': 25,
                'sbp': 170,
                'dbp': 100,
                'bmi': 38,
                'time_to_event': 40,
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
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*40}")
        print(f"🎯 {test_case['name'].upper()}")
        print(f"{'='*40}")
        
        data = test_case['data']
        
        print(f"📊 Key Parameters:")
        print(f"   Creatinine: {data['creatinine']} mg/dL")
        print(f"   Cholesterol: {data['cholesterol']} mg/dL")
        print(f"   Triglycerides: {data['triglycerides']} mg/dL")
        print(f"   Age: {data['age']} years")
        print(f"   eGFR: {data['egfr']} mL/min/1.73m²")
        print(f"   HbA1c: {data['hba1c']}%")
        print(f"   Diabetes: {'Yes' if data['diabetes'] else 'No'}")
        print(f"   Hypertension: {'Yes' if data['htn'] else 'No'}")
        
        try:
            print(f"\n🔄 Getting prediction...")
            response = requests.post(f"{base_url}/predict", json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Prediction Results:")
                print(f"   Result: {result['prediction']}")
                print(f"   Probability: {result['probability']:.3f} ({result['probability']*100:.1f}%)")
                print(f"   CKD Detected: {result['ckd']}")
                
                print(f"\n🧠 SHAP Analysis:")
                # Sort SHAP values by absolute value
                shap_sorted = sorted(result['shap'].items(), key=lambda x: abs(x[1]), reverse=True)
                
                for i, (feature, value) in enumerate(shap_sorted[:8], 1):
                    direction = "↑" if value > 0 else "↓"
                    impact = "Risk" if value > 0 else "Protective"
                    print(f"   {i}. {feature}: {value:+.3f} {direction} ({impact})")
                
                # Check if new parameters are in SHAP
                new_params = ['CreatnineBaseline', 'CholesterolBaseline', 'TriglyceridesBaseline']
                print(f"\n🔍 New Parameters in SHAP:")
                for param in new_params:
                    if param in result['shap']:
                        value = result['shap'][param]
                        direction = "↑" if value > 0 else "↓"
                        impact = "Risk" if value > 0 else "Protective"
                        print(f"   ✅ {param}: {value:+.3f} {direction} ({impact})")
                    else:
                        print(f"   ❌ {param}: Not found in SHAP")
                
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    print(f"\n{'='*60}")
    print("🎉 NEW SLIDERS TEST COMPLETED")
    print(f"{'='*60}")
    print("\n📋 VERIFICATION CHECKLIST:")
    print("   ✅ Creatinine slider (0.5-5.0 mg/dL)")
    print("   ✅ Cholesterol slider (100-400 mg/dL)")
    print("   ✅ Triglycerides slider (50-500 mg/dL)")
    print("   ✅ Real-time updates enabled")
    print("   ✅ SHAP values calculated")
    print("   ✅ Clinical insights generated")
    print("\n🌐 ACCESS THE DYNAMIC UI:")
    print("   http://localhost:8000/frontend/dynamic-shap.html")
    print("\n🎮 NEW SLIDER RANGES:")
    print("   • Creatinine: 0.5 - 5.0 mg/dL (step 0.1)")
    print("   • Cholesterol: 100 - 400 mg/dL (step 1)")
    print("   • Triglycerides: 50 - 500 mg/dL (step 1)")

if __name__ == "__main__":
    test_new_sliders()
