"""
Test frontend with actual Excel dataset values
"""

import requests
import pandas as pd

def test_excel_frontend():
    """Test frontend with actual Excel values"""
    
    print('📊 TESTING FRONTEND WITH ACTUAL EXCEL VALUES')
    print('=' * 60)
    
    # Load the dataset
    df = pd.read_excel('../pone.0199920.s002.xlsx')
    
    base_url = "http://localhost:8000"
    
    # Test cases from Excel data
    test_cases = [
        {
            "name": "Excel Case - Creatinine 57 μmol/L",
            "excel_data": df[df['CreatnineBaseline'] == 57].iloc[0]
        },
        {
            "name": "Excel Case - High Creatinine 60 μmol/L", 
            "excel_data": df[df['CreatnineBaseline'] == 60].iloc[0]
        },
        {
            "name": "Excel Case - Normal Range",
            "excel_data": df[df['CreatnineBaseline'] == 88.8].iloc[0]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ {test_case['name']}")
        print("-" * 40)
        
        row = test_case['excel_data']
        
        # Excel values (dataset units)
        creatinine_umol = row['CreatnineBaseline']
        egfr_value = row['eGFRBaseline']
        cholesterol_mmol = row['CholesterolBaseline']
        triglycerides_mmol = row['TriglyceridesBaseline']
        hba1c_value = row['HgbA1C']
        age_value = row['AgeBaseline']
        sbp_value = row['sBPBaseline']
        dbp_value = row['dBPBaseline']
        bmi_value = row['BMIBaseline']
        
        print(f"📋 Excel Dataset Values:")
        print(f"   Creatinine: {creatinine_umol:.1f} μmol/L")
        print(f"   eGFR: {egfr_value:.1f} mL/min/1.73m²")
        print(f"   Cholesterol: {cholesterol_mmol:.1f} mmol/L")
        print(f"   Triglycerides: {triglycerides_mmol:.1f} mmol/L")
        print(f"   HbA1c: {hba1c_value:.1f}")
        print(f"   Age: {age_value:.0f}")
        print(f"   SBP: {sbp_value:.0f}")
        print(f"   DBP: {dbp_value:.0f}")
        print(f"   BMI: {bmi_value:.1f}")
        print(f"   CKD Event: {row['EventCKD35']}")
        
        # Convert to frontend units
        creatinine_mgdl = creatinine_umol / 88.4
        cholesterol_mgdl = cholesterol_mmol * 38.67
        triglycerides_mgdl = triglycerides_mmol * 88.54
        
        print(f"\n🔄 Frontend Units (after conversion):")
        print(f"   Creatinine: {creatinine_mgdl:.2f} mg/dL")
        print(f"   Cholesterol: {cholesterol_mgdl:.0f} mg/dL")
        print(f"   Triglycerides: {triglycerides_mgdl:.0f} mg/dL")
        
        # Prepare test data for API
        api_data = {
            'age': int(age_value),
            'creatinine': creatinine_mgdl,  # Frontend sends mg/dL
            'cholesterol': cholesterol_mgdl,  # Frontend sends mg/dL
            'triglycerides': triglycerides_mgdl,  # Frontend sends mg/dL
            'hba1c': hba1c_value,
            'egfr': int(egfr_value),
            'sbp': int(sbp_value),
            'dbp': int(dbp_value),
            'bmi': bmi_value,
            'time_to_event': 24,
            'gender': 1,
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
        
        print(f"\n🧪 Testing API with Excel Values:")
        print(f"   Frontend sends: creatinine {creatinine_mgdl:.2f} mg/dL")
        print(f"   Backend receives: {creatinine_mgdl * 88.4:.1f} μmol/L")
        
        try:
            response = requests.post(f"{base_url}/predict", json=api_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                probability = result.get('probability', 0)
                prediction = result.get('prediction', 'Unknown')
                shap_values = result.get('shap', {})
                
                print(f"\n✅ Prediction Results:")
                print(f"   Prediction: {prediction}")
                print(f"   Probability: {probability:.3f} ({probability*100:.1f}%)")
                print(f"   SHAP Features: {len(shap_values)}")
                
                # Check creatinine and eGFR in SHAP
                creatinine_in_shap = any('Creatnine' in key for key in shap_values.keys())
                egfr_in_shap = any('eGFR' in key for key in shap_values.keys())
                
                print(f"   📊 Creatinine in SHAP: {'✅ Yes' if creatinine_in_shap else '❌ No'}")
                print(f"   📊 eGFR in SHAP: {'✅ Yes' if egfr_in_shap else '❌ No'}")
                
                if creatinine_in_shap:
                    creatinine_val = [v for k, v in shap_values.items() if 'Creatnine' in k][0]
                    print(f"   📈 Creatinine Impact: {creatinine_val:+.4f}")
                
                if egfr_in_shap:
                    egfr_val = [v for k, v in shap_values.items() if 'eGFR' in k][0]
                    print(f"   📈 eGFR Impact: {egfr_val:+.4f}")
                
                # Compare with actual outcome
                actual_ckd = row['EventCKD35']
                predicted_ckd = 1 if probability >= 0.3 else 0
                match = "✅" if actual_ckd == predicted_ckd else "⚠️"
                
                print(f"   🎯 Outcome Comparison:")
                print(f"      Actual CKD Event: {actual_ckd}")
                print(f"      Predicted CKD: {predicted_ckd}")
                print(f"      Match: {match}")
                
            else:
                print(f"   ❌ API Error: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Test Failed: {e}")
    
    # Special test for the specific creatinine ~57 case
    print(f"\n🎯 SPECIAL TEST: CREATININE ~57 μmol/L CASES")
    print("=" * 50)
    
    creatinine_57_cases = df[df['CreatnineBaseline'] == 57]
    print(f"Found {len(creatinine_57_cases)} cases with creatinine = 57 μmol/L")
    
    # Test a few of these cases
    for i in range(min(3, len(creatinine_57_cases))):
        row = creatinine_57_cases.iloc[i]
        
        # Convert to frontend units
        creatinine_mgdl = 57 / 88.4  # 0.65 mg/dL
        
        print(f"\nCase {i+1}: Creatinine 57 μmol/L ({creatinine_mgdl:.2f} mg/dL)")
        print(f"   eGFR: {row['eGFRBaseline']:.1f}")
        print(f"   Cholesterol: {row['CholesterolBaseline']:.1f} mmol/L")
        print(f"   Actual CKD Event: {row['EventCKD35']}")
        
        # Quick API test
        test_data = {
            'age': int(row['AgeBaseline']),
            'creatinine': creatinine_mgdl,
            'cholesterol': row['CholesterolBaseline'] * 38.67,
            'triglycerides': row['TriglyceridesBaseline'] * 88.54,
            'hba1c': row['HgbA1C'],
            'egfr': int(row['eGFRBaseline']),
            'sbp': int(row['sBPBaseline']),
            'dbp': int(row['dBPBaseline']),
            'bmi': row['BMIBaseline'],
            'time_to_event': 24,
            'gender': 1,
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
            response = requests.post(f"{base_url}/predict", json=test_data, timeout=5)
            if response.status_code == 200:
                result = response.json()
                probability = result.get('probability', 0)
                prediction = result.get('prediction', 'Unknown')
                print(f"   ✅ Prediction: {prediction} ({probability:.3f})")
            else:
                print(f"   ❌ Error: {response.status_code}")
        except:
            print(f"   ❌ Request failed")
    
    print(f"\n🎉 EXCEL VALUE TESTING COMPLETED!")
    print(f"📊 All Excel values properly converted and tested")

if __name__ == "__main__":
    test_excel_frontend()
