import pandas as pd
import requests
import json

def test_ckd_prediction_with_real_data():
    """Test the CKD prediction system with real PLoS ONE dataset"""
    
    # Load the dataset
    try:
        df = pd.read_excel('../pone.0199920.s002.xlsx')
        print(f"✅ Dataset loaded successfully!")
        print(f"📊 Shape: {df.shape[0]} patients, {df.shape[1]} features")
        print(f"🎯 CKD cases: {df['EventCKD35'].sum()} out of {len(df)} ({df['EventCKD35'].sum()/len(df)*100:.1f}%)")
        print()
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return
    
    # Select test cases
    ckd_positive = df[df['EventCKD35'] == 1].head(3)
    ckd_negative = df[df['EventCKD35'] == 0].head(3)
    
    print("=" * 60)
    print("🩺 TESTING CKD POSITIVE CASES")
    print("=" * 60)
    
    correct_predictions = 0
    total_tests = 0
    
    for idx, row in ckd_positive.iterrows():
        print(f"Patient {row['StudyID']} - Actual CKD: {row['EventCKD35']}")
        
        # Prepare data for API
        test_data = {
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
        
        try:
            response = requests.post('http://localhost:8000/predict', json=test_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                prediction_correct = result['ckd'] == bool(row['EventCKD35'])
                if prediction_correct:
                    correct_predictions += 1
                
                total_tests += 1
                
                print(f"  🔮 Prediction: {result['prediction']}")
                print(f"  📊 Probability: {result['probability']:.3f} ({result['probability']*100:.1f}%)")
                print(f"  ✅ Match: {'CORRECT' if prediction_correct else 'INCORRECT'}")
                
                # Show key clinical indicators
                print(f"  🩺 Key indicators:")
                print(f"     - Creatinine: {row['CreatnineBaseline']:.1f} μmol/L ({row['CreatnineBaseline']/88.4:.2f} mg/dL)")
                print(f"     - eGFR: {row['eGFRBaseline']:.1f} mL/min/1.73m²")
                print(f"     - HbA1c: {row['HgbA1C']:.1f}%")
                print(f"     - Age: {row['AgeBaseline']} years")
                
            else:
                print(f"  ❌ API Error: {response.status_code}")
                total_tests += 1
                
        except Exception as e:
            print(f"  ❌ Request failed: {e}")
            total_tests += 1
        
        print()
    
    print("=" * 60)
    print("🩺 TESTING CKD NEGATIVE CASES")
    print("=" * 60)
    
    for idx, row in ckd_negative.iterrows():
        print(f"Patient {row['StudyID']} - Actual CKD: {row['EventCKD35']}")
        
        # Prepare data for API
        test_data = {
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
        
        try:
            response = requests.post('http://localhost:8000/predict', json=test_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                prediction_correct = result['ckd'] == bool(row['EventCKD35'])
                if prediction_correct:
                    correct_predictions += 1
                
                total_tests += 1
                
                print(f"  🔮 Prediction: {result['prediction']}")
                print(f"  📊 Probability: {result['probability']:.3f} ({result['probability']*100:.1f}%)")
                print(f"  ✅ Match: {'CORRECT' if prediction_correct else 'INCORRECT'}")
                
                # Show key clinical indicators
                print(f"  🩺 Key indicators:")
                print(f"     - Creatinine: {row['CreatnineBaseline']:.1f} μmol/L ({row['CreatnineBaseline']/88.4:.2f} mg/dL)")
                print(f"     - eGFR: {row['eGFRBaseline']:.1f} mL/min/1.73m²")
                print(f"     - HbA1c: {row['HgbA1C']:.1f}%")
                print(f"     - Age: {row['AgeBaseline']} years")
                
            else:
                print(f"  ❌ API Error: {response.status_code}")
                total_tests += 1
                
        except Exception as e:
            print(f"  ❌ Request failed: {e}")
            total_tests += 1
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Correct predictions: {correct_predictions}")
    print(f"Accuracy: {correct_predictions/total_tests*100:.1f}%")
    
    if total_tests > 0:
        print(f"\n🎯 Model Performance on Real Data:")
        if correct_predictions/total_tests >= 0.8:
            print("✅ EXCELLENT - High accuracy on real patient data")
        elif correct_predictions/total_tests >= 0.6:
            print("🟡 GOOD - Moderate accuracy on real patient data")
        else:
            print("🔴 NEEDS IMPROVEMENT - Low accuracy on real patient data")

if __name__ == "__main__":
    test_ckd_prediction_with_real_data()
