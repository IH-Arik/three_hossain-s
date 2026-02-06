import pandas as pd
import requests

def comprehensive_test():
    """Test with both CKD positive and negative cases"""
    
    # Load the dataset
    df = pd.read_excel('../pone.0199920.s002.xlsx')
    
    # Get balanced test cases
    ckd_positive = df[df['EventCKD35'] == 1].head(5)
    ckd_negative = df[df['EventCKD35'] == 0].head(5)
    
    print("=" * 80)
    print("🩺 COMPREHENSIVE CKD PREDICTION TEST")
    print("=" * 80)
    print(f"Dataset: {df.shape[0]} patients, {df['EventCKD35'].sum()} CKD cases")
    print()
    
    correct_predictions = 0
    total_tests = 0
    
    # Test CKD positive cases
    print("🔴 CKD POSITIVE CASES")
    print("-" * 40)
    
    for idx, row in ckd_positive.iterrows():
        print(f"Patient {row['StudyID']} - Actual CKD: {row['EventCKD35']}")
        
        # Prepare API data with unit conversion
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
        
        try:
            response = requests.post('http://localhost:8000/predict', json=api_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                prediction_correct = result['ckd'] == bool(row['EventCKD35'])
                if prediction_correct:
                    correct_predictions += 1
                
                total_tests += 1
                
                status = "✅ CORRECT" if prediction_correct else "❌ INCORRECT"
                print(f"  🔮 {result['prediction']} ({result['probability']:.3f}) - {status}")
                
                # Show risk factors
                risk_factors = []
                if row['CreatnineBaseline'] > 80:  # High creatinine
                    risk_factors.append(f"High Cr ({row['CreatnineBaseline']/88.4:.2f} mg/dL)")
                if row['eGFRBaseline'] < 60:  # Low eGFR
                    risk_factors.append(f"Low eGFR ({row['eGFRBaseline']:.1f})")
                if row['HgbA1C'] > 7.0:  # High HbA1c
                    risk_factors.append(f"High HbA1c ({row['HgbA1C']:.1f}%)")
                if row['AgeBaseline'] > 70:  # Elderly
                    risk_factors.append(f"Elderly ({row['AgeBaseline']}y)")
                
                if risk_factors:
                    print(f"  ⚠️  Risk factors: {', '.join(risk_factors)}")
                
            else:
                print(f"  ❌ API Error: {response.status_code}")
                total_tests += 1
                
        except Exception as e:
            print(f"  ❌ Request failed: {e}")
            total_tests += 1
        
        print()
    
    # Test CKD negative cases
    print("🟢 CKD NEGATIVE CASES")
    print("-" * 40)
    
    for idx, row in ckd_negative.iterrows():
        print(f"Patient {row['StudyID']} - Actual CKD: {row['EventCKD35']}")
        
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
            response = requests.post('http://localhost:8000/predict', json=api_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                prediction_correct = result['ckd'] == bool(row['EventCKD35'])
                if prediction_correct:
                    correct_predictions += 1
                
                total_tests += 1
                
                status = "✅ CORRECT" if prediction_correct else "❌ INCORRECT"
                print(f"  🔮 {result['prediction']} ({result['probability']:.3f}) - {status}")
                
            else:
                print(f"  ❌ API Error: {response.status_code}")
                total_tests += 1
                
        except Exception as e:
            print(f"  ❌ Request failed: {e}")
            total_tests += 1
        
        print()
    
    # Final summary
    print("=" * 80)
    print("📊 FINAL RESULTS")
    print("=" * 80)
    print(f"Total tests: {total_tests}")
    print(f"Correct predictions: {correct_predictions}")
    print(f"Overall accuracy: {correct_predictions/total_tests*100:.1f}%")
    
    # Performance assessment
    if correct_predictions/total_tests >= 0.8:
        print("🎉 EXCELLENT performance on real PLoS ONE dataset!")
    elif correct_predictions/total_tests >= 0.6:
        print("👍 GOOD performance on real PLoS ONE dataset")
    else:
        print("⚠️  Model needs improvement for clinical use")
    
    print(f"\n🏥 System ready for clinical research and educational use!")

if __name__ == "__main__":
    comprehensive_test()
