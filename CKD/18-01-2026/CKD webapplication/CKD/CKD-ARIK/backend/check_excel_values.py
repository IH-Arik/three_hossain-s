"""
Check actual Excel dataset values for frontend testing
"""

import pandas as pd
import numpy as np

def check_excel_values():
    """Check actual values in the Excel dataset"""
    
    print('📊 ACTUAL DATASET VALUES FOR TESTING')
    print('=' * 50)
    
    # Load the dataset
    df = pd.read_excel('../pone.0199920.s002.xlsx')
    
    # Check creatinine values
    print('\n🔍 CREATININE VALUES:')
    creatinine_values = df['CreatnineBaseline'].dropna()
    print(f'   Min: {creatinine_values.min():.1f}')
    print(f'   Max: {creatinine_values.max():.1f}')
    print(f'   Mean: {creatinine_values.mean():.1f}')
    print(f'   Median: {creatinine_values.median():.1f}')
    print(f'   Sample values: {list(creatinine_values.head(10).round(1))}')
    
    # Check eGFR values
    print('\n🔍 eGFR VALUES:')
    egfr_values = df['eGFRBaseline'].dropna()
    print(f'   Min: {egfr_values.min():.1f}')
    print(f'   Max: {egfr_values.max():.1f}')
    print(f'   Mean: {egfr_values.mean():.1f}')
    print(f'   Median: {egfr_values.median():.1f}')
    print(f'   Sample values: {list(egfr_values.head(10).round(1))}')
    
    # Check Cholesterol values
    print('\n🔍 CHOLESTEROL VALUES:')
    cholesterol_values = df['CholesterolBaseline'].dropna()
    print(f'   Min: {cholesterol_values.min():.1f}')
    print(f'   Max: {cholesterol_values.max():.1f}')
    print(f'   Mean: {cholesterol_values.mean():.1f}')
    print(f'   Median: {cholesterol_values.median():.1f}')
    print(f'   Sample values: {list(cholesterol_values.head(10).round(1))}')
    
    # Find specific high creatinine values
    print('\n🎯 HIGH CREATININE CASES:')
    high_creatinine = df[df['CreatnineBaseline'] > 50]
    print(f'   Cases with creatinine > 50: {len(high_creatinine)}')
    if len(high_creatinine) > 0:
        print('   Sample high creatinine cases:')
        for i, row in high_creatinine.head(3).iterrows():
            print(f'     Creatinine: {row["CreatnineBaseline"]:.1f}, eGFR: {row["eGFRBaseline"]:.1f}, Cholesterol: {row["CholesterolBaseline"]:.1f}')
    
    # Find the specific case with creatinine ~57
    print('\n🎯 CREATININE ~57 CASES:')
    target_creatinine = df[(df['CreatnineBaseline'] >= 55) & (df['CreatnineBaseline'] <= 60)]
    if len(target_creatinine) > 0:
        print('   Found cases with creatinine ~57:')
        for i, row in target_creatinine.iterrows():
            print(f'     Creatinine: {row["CreatnineBaseline"]:.1f}')
            print(f'     eGFR: {row["eGFRBaseline"]:.1f}')
            print(f'     Cholesterol: {row["CholesterolBaseline"]:.1f}')
            print(f'     Age: {row["AgeBaseline"]}')
            print(f'     CKD Event: {row["EventCKD35"]}')
            print()
    else:
        print('   No cases found with creatinine ~57')
    
    # Create test cases with actual Excel values
    print('\n🧪 TEST CASES FROM EXCEL DATA:')
    print('-' * 40)
    
    # Test case 1: Normal values
    normal_case = df[(df['CreatnineBaseline'] >= 0.5) & (df['CreatnineBaseline'] <= 1.2)].iloc[0]
    print('\n1️⃣ NORMAL CASE (from Excel):')
    print(f'   Creatinine: {normal_case["CreatnineBaseline"]:.1f} μmol/L')
    print(f'   eGFR: {normal_case["eGFRBaseline"]:.1f}')
    print(f'   Cholesterol: {normal_case["CholesterolBaseline"]:.1f} mmol/L')
    print(f'   Age: {normal_case["AgeBaseline"]}')
    print(f'   CKD Event: {normal_case["EventCKD35"]}')
    
    # Convert to frontend units
    creatinine_mgdl = normal_case["CreatnineBaseline"] / 88.4
    cholesterol_mgdl = normal_case["CholesterolBaseline"] * 38.67
    print(f'   Frontend units:')
    print(f'   Creatinine: {creatinine_mgdl:.2f} mg/dL')
    print(f'   Cholesterol: {cholesterol_mgdl:.0f} mg/dL')
    
    # Test case 2: High creatinine case
    if len(high_creatinine) > 0:
        high_case = high_creatinine.iloc[0]
        print('\n2️⃣ HIGH CREATININE CASE (from Excel):')
        print(f'   Creatinine: {high_case["CreatnineBaseline"]:.1f} μmol/L')
        print(f'   eGFR: {high_case["eGFRBaseline"]:.1f}')
        print(f'   Cholesterol: {high_case["CholesterolBaseline"]:.1f} mmol/L')
        print(f'   Age: {high_case["AgeBaseline"]}')
        print(f'   CKD Event: {high_case["EventCKD35"]}')
        
        # Convert to frontend units
        creatinine_mgdl = high_case["CreatnineBaseline"] / 88.4
        cholesterol_mgdl = high_case["CholesterolBaseline"] * 38.67
        print(f'   Frontend units:')
        print(f'   Creatinine: {creatinine_mgdl:.2f} mg/dL')
        print(f'   Cholesterol: {cholesterol_mgdl:.0f} mg/dL')
    
    # Test case 3: Find case with creatinine ~57
    if len(target_creatinine) > 0:
        target_case = target_creatinine.iloc[0]
        print('\n3️⃣ CREATININE ~57 CASE (from Excel):')
        print(f'   Creatinine: {target_case["CreatnineBaseline"]:.1f} μmol/L')
        print(f'   eGFR: {target_case["eGFRBaseline"]:.1f}')
        print(f'   Cholesterol: {target_case["CholesterolBaseline"]:.1f} mmol/L')
        print(f'   Age: {target_case["AgeBaseline"]}')
        print(f'   CKD Event: {target_case["EventCKD35"]}')
        
        # Convert to frontend units
        creatinine_mgdl = target_case["CreatnineBaseline"] / 88.4
        cholesterol_mgdl = target_case["CholesterolBaseline"] * 38.67
        print(f'   Frontend units:')
        print(f'   Creatinine: {creatinine_mgdl:.2f} mg/dL')
        print(f'   Cholesterol: {cholesterol_mgdl:.0f} mg/dL')

if __name__ == "__main__":
    check_excel_values()
