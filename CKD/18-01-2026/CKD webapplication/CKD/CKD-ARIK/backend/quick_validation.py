import pandas as pd
import requests
import numpy as np

def quick_validation():
    """Quick validation of the improved model"""
    
    print("🔍 QUICK VALIDATION OF IMPROVED MODEL")
    print("=" * 50)
    
    # Load dataset
    df = pd.read_excel('../pone.0199920.s002.xlsx')
    
    # Test 20 random patients
    test_df = df.sample(n=20, random_state=42)
    
    correct = 0
    total = 0
    
    for idx, row in test_df.iterrows():
        # Prepare API data
        api_data = {
            'age': float(row['AgeBaseline']),
            'cholesterol': float(row['CholesterolBaseline']),
            'triglycerides': float(row['TriglyceridesBaseline']),
            'hba1c': float(row['HgbA1C']),
            'creatinine': float(row['CreatnineBaseline']) / 88.4,
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
            response = requests.post('http://localhost:8000/predict', json=api_data, timeout=5)
            if response.status_code == 200:
                result = response.json()
                actual = bool(row['EventCKD35'])
                predicted = result['ckd']
                
                if actual == predicted:
                    correct += 1
                
                total += 1
                
                status = "✅" if actual == predicted else "❌"
                print(f"{status} Patient {row['StudyID']}: Actual={actual}, Predicted={predicted} ({result['probability']:.3f})")
            
        except Exception as e:
            print(f"❌ Error with patient {row['StudyID']}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 QUICK VALIDATION RESULTS:")
    print(f"Accuracy: {correct}/{total} ({correct/total*100:.1f}%)")
    
    if correct/total >= 0.8:
        print("🎉 EXCELLENT - Model fix successful!")
    elif correct/total >= 0.6:
        print("👍 GOOD - Significant improvement achieved")
    else:
        print("⚠️  Needs further tuning")

if __name__ == "__main__":
    quick_validation()
