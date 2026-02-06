"""
Check for creatinine column and understand the units
"""

import pandas as pd

def check_creatinine_column():
    """Check for creatinine column and understand the actual values"""
    
    print("🔍 CHECKING CREATININE COLUMN")
    print("=" * 40)
    
    try:
        # Load the dataset
        df = pd.read_excel('../pone.0199920.s002.xlsx')
        print(f"✅ Dataset loaded: {df.shape}")
        
        # Print all column names to find creatinine
        print(f"\n📋 ALL COLUMNS:")
        print("=" * 40)
        for i, col in enumerate(df.columns):
            print(f"{i+1:2d}. {col}")
        
        # Look for columns that might contain creatinine
        creatinine_columns = [col for col in df.columns if 'creat' in col.lower()]
        print(f"\n🔍 CREATININE-RELATED COLUMNS:")
        print("=" * 40)
        for col in creatinine_columns:
            print(f"• {col}")
            
            # Show sample values
            values = df[col].dropna().head(10)
            print(f"  Sample values: {values.tolist()}")
            
            # Show statistics
            all_values = df[col].dropna()
            if len(all_values) > 0:
                print(f"  Range: {all_values.min():.2f} - {all_values.max():.2f}")
                print(f"  Mean: {all_values.mean():.2f}")
                print(f"  Count: {len(all_values)}")
        
        # Check if values look like mg/dL or μmol/L
        if creatinine_columns:
            col = creatinine_columns[0]
            values = df[col].dropna()
            
            # Typical ranges:
            # mg/dL: 0.5 - 5.0
            # μmol/L: 50 - 450
            
            if values.max() > 50:
                print(f"\n💡 LIKELY UNITS: μmol/L (micromoles per liter)")
                print(f"   Typical range: 50-450 μmol/L")
                print(f"   To convert to mg/dL: divide by 88.4")
                
                # Show converted values
                converted = values / 88.4
                print(f"   Converted range: {converted.min():.2f} - {converted.max():.2f} mg/dL")
                print(f"   Converted mean: {converted.mean():.2f} mg/dL")
                
            else:
                print(f"\n💡 LIKELY UNITS: mg/dL (milligrams per deciliter)")
                print(f"   Typical range: 0.5-5.0 mg/dL")
        
        # Also check cholesterol and triglycerides units
        print(f"\n🔍 CHECKING CHOLESTEROL & TRIGLYCERIDES:")
        print("=" * 40)
        
        chol_col = 'CholesterolBaseline'
        trig_col = 'TriglyceridesBaseline'
        
        if chol_col in df.columns:
            chol_values = df[chol_col].dropna()
            print(f"Cholesterol: {chol_values.min():.2f} - {chol_values.max():.2f}")
            if chol_values.max() < 20:
                print(f"💡 LIKELY UNITS: mmol/L (multiply by 38.67 to get mg/dL)")
                print(f"   Converted: {chol_values.min()*38.67:.0f} - {chol_values.max()*38.67:.0f} mg/dL")
            else:
                print(f"💡 LIKELY UNITS: mg/dL")
        
        if trig_col in df.columns:
            trig_values = df[trig_col].dropna()
            print(f"Triglycerides: {trig_values.min():.2f} - {trig_values.max():.2f}")
            if trig_values.max() < 10:
                print(f"💡 LIKELY UNITS: mmol/L (multiply by 88.54 to get mg/dL)")
                print(f"   Converted: {trig_values.min()*88.54:.0f} - {trig_values.max()*88.54:.0f} mg/dL")
            else:
                print(f"💡 LIKELY UNITS: mg/dL")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_creatinine_column()
