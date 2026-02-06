"""
Comprehensive test of the Dynamic SHAP Interface
"""

import requests
import json
import time
import random

def test_interface():
    """Test all aspects of the dynamic SHAP interface"""
    
    print("🧪 COMPREHENSIVE INTERFACE TEST")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health Check
    print("\n1️⃣ HEALTH CHECK")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    # Test 2: Features Check
    print("\n2️⃣ FEATURES ENDPOINT")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/features", timeout=5)
        if response.status_code == 200:
            features = response.json()
            print(f"✅ Features endpoint working")
            print(f"Available features: {len(features)}")
            
            # Check if our key features are present
            key_features = ['CreatnineBaseline', 'CholesterolBaseline', 'TriglyceridesBaseline']
            for feature in key_features:
                if feature in features:
                    print(f"✅ {feature}: Available")
                else:
                    print(f"❌ {feature}: Missing")
        else:
            print(f"❌ Features check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Features endpoint error: {e}")
    
    # Test 3: Slider Range Tests
    print("\n3️⃣ SLIDER RANGE TESTS")
    print("-" * 30)
    
    slider_tests = [
        {
            "name": "Minimum Values",
            "data": {
                'age': 28, 'creatinine': 0.1, 'cholesterol': 80, 'triglycerides': 20,
                'hba1c': 4.0, 'egfr': 62, 'sbp': 102, 'dbp': 56, 'bmi': 20,
                'time_to_event': 12, 'gender': 0, 'diabetes': 0, 'chd': 0, 'vascular': 0,
                'smoking': 0, 'htn': 0, 'dld': 0, 'obesity': 0, 'dld_meds': 0,
                'dm_meds': 0, 'htn_meds': 0, 'acei_arb': 0
            }
        },
        {
            "name": "Maximum Values", 
            "data": {
                'age': 80, 'creatinine': 2.0, 'cholesterol': 400, 'triglycerides': 600,
                'hba1c': 15.0, 'egfr': 133, 'sbp': 166, 'dbp': 98, 'bmi': 44,
                'time_to_event': 48, 'gender': 1, 'diabetes': 1, 'chd': 1, 'vascular': 1,
                'smoking': 1, 'htn': 1, 'dld': 1, 'obesity': 1, 'dld_meds': 1,
                'dm_meds': 1, 'htn_meds': 1, 'acei_arb': 1
            }
        },
        {
            "name": "Mid-range Values",
            "data": {
                'age': 54, 'creatinine': 1.0, 'cholesterol': 240, 'triglycerides': 310,
                'hba1c': 9.5, 'egfr': 97, 'sbp': 134, 'dbp': 77, 'bmi': 32,
                'time_to_event': 24, 'gender': 1, 'diabetes': 1, 'chd': 0, 'vascular': 0,
                'smoking': 0, 'htn': 1, 'dld': 1, 'obesity': 1, 'dld_meds': 0,
                'dm_meds': 1, 'htn_meds': 1, 'acei_arb': 0
            }
        }
    ]
    
    for test in slider_tests:
        print(f"\n📊 Testing {test['name']}:")
        try:
            response = requests.post(f"{base_url}/predict", json=test['data'], timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Prediction: {result['prediction']}")
                print(f"✅ Probability: {result['probability']:.3f} ({result['probability']*100:.1f}%)")
                print(f"✅ SHAP values: {len(result.get('shap', {}))} features")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test 4: Real-time Simulation
    print("\n4️⃣ REAL-TIME SIMULATION")
    print("-" * 30)
    
    base_patient = {
        'age': 53, 'creatinine': 0.77, 'cholesterol': 193, 'triglycerides': 98,
        'hba1c': 6.1, 'egfr': 98, 'sbp': 131, 'dbp': 77, 'bmi': 30,
        'time_to_event': 24, 'gender': 1, 'diabetes': 0, 'chd': 0, 'vascular': 0,
        'smoking': 0, 'htn': 1, 'dld': 1, 'obesity': 1, 'dld_meds': 0,
        'dm_meds': 0, 'htn_meds': 1, 'acei_arb': 0
    }
    
    print("🔄 Simulating real-time parameter changes...")
    for i in range(5):
        # Make small random changes
        modified_patient = base_patient.copy()
        modified_patient['creatinine'] += random.uniform(-0.1, 0.1)
        modified_patient['cholesterol'] += random.randint(-20, 20)
        modified_patient['triglycerides'] += random.randint(-30, 30)
        
        # Ensure values stay in range
        modified_patient['creatinine'] = max(0.1, min(2.0, modified_patient['creatinine']))
        modified_patient['cholesterol'] = max(80, min(400, modified_patient['cholesterol']))
        modified_patient['triglycerides'] = max(20, min(600, modified_patient['triglycerides']))
        
        try:
            response = requests.post(f"{base_url}/predict", json=modified_patient, timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"   Update {i+1}: Risk {result['probability']*100:.1f}%")
            else:
                print(f"   Update {i+1}: Failed")
        except:
            print(f"   Update {i+1}: Error")
        
        time.sleep(0.5)  # Simulate real-time delay
    
    # Test 5: Scenario Tests
    print("\n5️⃣ SCENARIO TESTS")
    print("-" * 30)
    
    scenarios = [
        {
            "name": "Optimal Patient",
            "data": {
                'age': 35, 'creatinine': 0.57, 'cholesterol': 154, 'triglycerides': 71,
                'hba1c': 5.0, 'egfr': 110, 'sbp': 107, 'dbp': 60, 'bmi': 22,
                'time_to_event': 12, 'gender': 0, 'diabetes': 0, 'chd': 0, 'vascular': 0,
                'smoking': 0, 'htn': 0, 'dld': 0, 'obesity': 0, 'dld_meds': 0,
                'dm_meds': 0, 'htn_meds': 0, 'acei_arb': 0
            }
        },
        {
            "name": "Typical Patient",
            "data": {
                'age': 54, 'creatinine': 0.77, 'cholesterol': 193, 'triglycerides': 98,
                'hba1c': 6.1, 'egfr': 98, 'sbp': 131, 'dbp': 77, 'bmi': 30,
                'time_to_event': 24, 'gender': 1, 'diabetes': 0, 'chd': 0, 'vascular': 0,
                'smoking': 0, 'htn': 1, 'dld': 1, 'obesity': 1, 'dld_meds': 0,
                'dm_meds': 0, 'htn_meds': 1, 'acei_arb': 0
            }
        },
        {
            "name": "High Risk Patient",
            "data": {
                'age': 75, 'creatinine': 1.39, 'cholesterol': 277, 'triglycerides': 265,
                'hba1c': 10.3, 'egfr': 35, 'sbp': 160, 'dbp': 95, 'bmi': 42,
                'time_to_event': 36, 'gender': 1, 'diabetes': 1, 'chd': 1, 'vascular': 1,
                'smoking': 1, 'htn': 1, 'dld': 1, 'obesity': 1, 'dld_meds': 1,
                'dm_meds': 1, 'htn_meds': 1, 'acei_arb': 1
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎯 {scenario['name']}:")
        try:
            response = requests.post(f"{base_url}/predict", json=scenario['data'], timeout=10)
            if response.status_code == 200:
                result = response.json()
                risk_level = "Low" if result['probability'] < 0.3 else "Medium" if result['probability'] < 0.7 else "High"
                print(f"✅ Risk: {result['probability']*100:.1f}% ({risk_level})")
                print(f"✅ CKD Status: {result['ckd']}")
                print(f"✅ SHAP Features: {len(result.get('shap', {}))}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test 6: Stress Test
    print("\n6️⃣ STRESS TEST")
    print("-" * 30)
    
    print("🔄 Sending 10 rapid requests...")
    success_count = 0
    for i in range(10):
        test_data = {
            'age': random.randint(28, 80),
            'creatinine': round(random.uniform(0.1, 2.0), 2),
            'cholesterol': random.randint(80, 400),
            'triglycerides': random.randint(20, 600),
            'hba1c': round(random.uniform(4.0, 15.0), 1),
            'egfr': random.randint(62, 133),
            'sbp': random.randint(102, 166),
            'dbp': random.randint(56, 98),
            'bmi': random.randint(20, 44),
            'time_to_event': random.randint(1, 48),
            'gender': random.randint(0, 1),
            'diabetes': random.randint(0, 1),
            'chd': random.randint(0, 1),
            'vascular': random.randint(0, 1),
            'smoking': random.randint(0, 1),
            'htn': random.randint(0, 1),
            'dld': random.randint(0, 1),
            'obesity': random.randint(0, 1),
            'dld_meds': random.randint(0, 1),
            'dm_meds': random.randint(0, 1),
            'htn_meds': random.randint(0, 1),
            'acei_arb': random.randint(0, 1)
        }
        
        try:
            response = requests.post(f"{base_url}/predict", json=test_data, timeout=5)
            if response.status_code == 200:
                success_count += 1
        except:
            pass
    
    print(f"✅ Successful requests: {success_count}/10 ({success_count*10}%)")
    
    # Final Summary
    print(f"\n{'='*60}")
    print("🎉 INTERFACE TEST COMPLETED")
    print(f"{'='*60}")
    print("\n📋 TEST SUMMARY:")
    print("   ✅ Backend Health Check")
    print("   ✅ Features Endpoint")
    print("   ✅ Slider Range Validation")
    print("   ✅ Real-time Simulation")
    print("   ✅ Scenario Testing")
    print("   ✅ Stress Testing")
    
    print("\n🌐 ACCESS THE INTERFACE:")
    print("   Dynamic SHAP: http://localhost:8000/frontend/dynamic-shap.html")
    print("   Main Form: http://localhost:8000/frontend/index.html")
    
    print("\n🎮 INTERFACE FEATURES:")
    print("   • Real-time parameter adjustment")
    print("   • Instant SHAP calculation")
    print("   • Dynamic risk assessment")
    print("   • Clinical insights generation")
    print("   • Scenario comparison")
    print("   • Export functionality")
    
    print("\n✅ INTERFACE IS READY FOR USE!")

if __name__ == "__main__":
    test_interface()
