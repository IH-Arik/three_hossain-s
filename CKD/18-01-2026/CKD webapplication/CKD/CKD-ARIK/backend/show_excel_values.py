"""
Show Excel values directly for testing
"""

import pandas as pd

print('📊 EXCEL DATASET VALUES - DIRECT ACCESS')
print('=' * 50)

# Load the dataset
df = pd.read_excel('../pone.0199920.s002.xlsx')

print(f'Total records: {len(df)}')
print()

# Show first 10 records with key values
print('🔍 FIRST 10 RECORDS FROM EXCEL:')
print('-' * 40)
for i in range(min(10, len(df))):
    row = df.iloc[i]
    print(f'Record {i+1}:')
    print(f'  Creatinine: {row["CreatnineBaseline"]:.1f} μmol/L')
    print(f'  eGFR: {row["eGFRBaseline"]:.1f}')
    print(f'  Cholesterol: {row["CholesterolBaseline"]:.1f} mmol/L')
    print(f'  Triglycerides: {row["TriglyceridesBaseline"]:.1f} mmol/L')
    print(f'  Age: {row["AgeBaseline"]}')
    print(f'  CKD Event: {row["EventCKD35"]}')
    print()

# Check specific values you mentioned
print('🎯 SPECIFIC VALUE RANGES:')
print('-' * 30)

# Creatinine ranges
print(f'Creatinine range: {df["CreatnineBaseline"].min():.1f} - {df["CreatnineBaseline"].max():.1f} μmol/L')

# Find records with specific creatinine values
target_values = [57, 60, 88.8, 100, 150]
for val in target_values:
    matches = df[df['CreatnineBaseline'] == val]
    if len(matches) > 0:
        print(f'Creatinine {val} μmol/L: {len(matches)} records found')
        sample = matches.iloc[0]
        print(f'  Sample: eGFR={sample["eGFRBaseline"]:.1f}, Cholesterol={sample["CholesterolBaseline"]:.1f} mmol/L')
    else:
        print(f'Creatinine {val} μmol/L: No records found')

print()
print('📋 CONVERT TO FRONTEND UNITS:')
print('-' * 30)

# Show conversion for first 5 records
for i in range(min(5, len(df))):
    row = df.iloc[i]
    creatinine_umol = row['CreatnineBaseline']
    creatinine_mgdl = creatinine_umol / 88.4
    cholesterol_mmol = row['CholesterolBaseline']
    cholesterol_mgdl = cholesterol_mmol * 38.67
    triglycerides_mmol = row['TriglyceridesBaseline']
    triglycerides_mgdl = triglycerides_mmol * 88.54
    
    print(f'Record {i+1}:')
    print(f'  Creatinine: {creatinine_umol:.1f} μmol/L → {creatinine_mgdl:.2f} mg/dL')
    print(f'  Cholesterol: {cholesterol_mmol:.1f} mmol/L → {cholesterol_mgdl:.0f} mg/dL')
    print(f'  Triglycerides: {triglycerides_mmol:.1f} mmol/L → {triglycerides_mgdl:.0f} mg/dL')
    print()

# Create test data with exact Excel values
print('🧪 EXACT EXCEL VALUES FOR FRONTEND TEST:')
print('-' * 40)

# Get some specific records
test_records = []
test_records.append(df[df['CreatnineBaseline'] == 57].iloc[0])  # 57 μmol/L
test_records.append(df[df['CreatnineBaseline'] == 60].iloc[0])  # 60 μmol/L
test_records.append(df.iloc[0])  # First record
test_records.append(df.iloc[10])  # 11th record

for i, row in enumerate(test_records):
    print(f'Test Case {i+1}:')
    print(f'  Excel Values:')
    print(f'    Creatinine: {row["CreatnineBaseline"]:.1f} μmol/L')
    print(f'    eGFR: {row["eGFRBaseline"]:.1f}')
    print(f'    Cholesterol: {row["CholesterolBaseline"]:.1f} mmol/L')
    print(f'    Triglycerides: {row["TriglyceridesBaseline"]:.1f} mmol/L')
    print(f'    HbA1c: {row["HgbA1C"]:.1f}')
    print(f'    Age: {row["AgeBaseline"]}')
    print(f'    SBP: {row["sBPBaseline"]}')
    print(f'    DBP: {row["dBPBaseline"]}')
    print(f'    BMI: {row["BMIBaseline"]}')
    print(f'  Frontend Units:')
    creatinine_mgdl = row['CreatnineBaseline'] / 88.4
    cholesterol_mgdl = row['CholesterolBaseline'] * 38.67
    triglycerides_mgdl = row['TriglyceridesBaseline'] * 88.54
    print(f'    Creatinine: {creatinine_mgdl:.2f} mg/dL')
    print(f'    Cholesterol: {cholesterol_mgdl:.0f} mg/dL')
    print(f'    Triglycerides: {triglycerides_mgdl:.0f} mg/dL')
    print(f'  API Test Data:')
    print(f'    {{')
    print(f'      \"age\": {int(row[\"AgeBaseline\"])},')
    print(f'      \"creatinine\": {creatinine_mgdl:.2f},')
    print(f'      \"cholesterol\": {cholesterol_mgdl:.0f},')
    print(f'      \"triglycerides\": {triglycerides_mgdl:.0f},')
    print(f'      \"hba1c\": {row[\"HgbA1C\"]},')
    print(f'      \"egfr\": {int(row[\"eGFRBaseline\"])},')
    print(f'      \"sbp\": {int(row[\"sBPBaseline\"])},')
    print(f'      \"dbp\": {int(row[\"dBPBaseline\"])},')
    print(f'      \"bmi\": {row[\"BMIBaseline\"]}')
    print(f'    }}')
    print()
