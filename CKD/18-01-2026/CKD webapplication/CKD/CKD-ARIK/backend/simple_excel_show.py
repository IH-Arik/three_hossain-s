"""
Simple Excel values display
"""

import pandas as pd

print('📊 EXCEL DATASET VALUES')
print('=' * 40)

# Load dataset
df = pd.read_excel('../pone.0199920.s002.xlsx')

print(f'Total records: {len(df)}')
print()

# First 5 records
print('FIRST 5 RECORDS:')
for i in range(5):
    row = df.iloc[i]
    creatinine = row['CreatnineBaseline']
    egfr = row['eGFRBaseline']
    cholesterol = row['CholesterolBaseline']
    triglycerides = row['TriglyceridesBaseline']
    age = row['AgeBaseline']
    
    print(f'Record {i+1}:')
    print(f'  Creatinine: {creatinine:.1f} μmol/L')
    print(f'  eGFR: {egfr:.1f}')
    print(f'  Cholesterol: {cholesterol:.1f} mmol/L')
    print(f'  Triglycerides: {triglycerides:.1f} mmol/L')
    print(f'  Age: {age}')
    print()

# Find creatinine 57
print('CREATININE 57 CASES:')
creatinine_57 = df[df['CreatnineBaseline'] == 57]
print(f'Found {len(creatinine_57)} cases with creatinine = 57 μmol/L')

if len(creatinine_57) > 0:
    sample = creatinine_57.iloc[0]
    print(f'Sample case:')
    print(f'  Creatinine: {sample[\"CreatnineBaseline\"]:.1f} μmol/L')
    print(f'  eGFR: {sample[\"eGFRBaseline\"]:.1f}')
    print(f'  Cholesterol: {sample[\"CholesterolBaseline\"]:.1f} mmol/L')
    print(f'  Triglycerides: {sample[\"TriglyceridesBaseline\"]:.1f} mmol/L')
    print(f'  Age: {sample[\"AgeBaseline\"]}')
    
    # Convert to frontend units
    creatinine_mgdl = 57 / 88.4
    cholesterol_mgdl = sample['CholesterolBaseline'] * 38.67
    triglycerides_mgdl = sample['TriglyceridesBaseline'] * 88.54
    
    print(f'  Frontend units:')
    print(f'    Creatinine: {creatinine_mgdl:.2f} mg/dL')
    print(f'    Cholesterol: {cholesterol_mgdl:.0f} mg/dL')
    print(f'    Triglycerides: {triglycerides_mgdl:.0f} mg/dL')

print()
print('RANGES:')
print(f'Creatinine: {df[\"CreatnineBaseline\"].min():.1f} - {df[\"CreatnineBaseline\"].max():.1f} μmol/L')
print(f'eGFR: {df[\"eGFRBaseline\"].min():.1f} - {df[\"eGFRBaseline\"].max():.1f}')
print(f'Cholesterol: {df[\"CholesterolBaseline\"].min():.1f} - {df[\"CholesterolBaseline\"].max():.1f} mmol/L')
print(f'Triglycerides: {df[\"TriglyceridesBaseline\"].min():.1f} - {df[\"TriglyceridesBaseline\"].max():.1f} mmol/L')
