"""
Check the actual value ranges in the pone.0199920.s002.xlsx dataset
"""

import pandas as pd
import numpy as np

def check_dataset_ranges():
    """Check the actual ranges of values in the dataset"""
    
    print("📊 CHECKING DATASET VALUE RANGES")
    print("=" * 50)
    
    try:
        # Load the dataset
        df = pd.read_excel('../pone.0199920.s002.xlsx')
        print(f"✅ Dataset loaded: {df.shape}")
        
        # Check the key columns we need for sliders
        key_columns = {
            'CreatinineBaseline': 'Creatinine (mg/dL)',
            'CholesterolBaseline': 'Cholesterol (mg/dL)', 
            'TriglyceridesBaseline': 'Triglycerides (mg/dL)',
            'AgeBaseline': 'Age (years)',
            'eGFRBaseline': 'eGFR (mL/min/1.73m²)',
            'HgbA1C': 'HbA1c (%)',
            'sBPBaseline': 'Systolic BP (mmHg)',
            'dBPBaseline': 'Diastolic BP (mmHg)',
            'BMIBaseline': 'BMI (kg/m²)'
        }
        
        print(f"\n📋 ACTUAL DATASET RANGES:")
        print("=" * 50)
        
        for column, description in key_columns.items():
            if column in df.columns:
                values = df[column].dropna()
                
                if len(values) > 0:
                    min_val = values.min()
                    max_val = values.max()
                    mean_val = values.mean()
                    median_val = values.median()
                    std_val = values.std()
                    
                    print(f"\n🔍 {description}")
                    print(f"   Column: {column}")
                    print(f"   Count: {len(values)} values")
                    print(f"   Range: {min_val:.2f} - {max_val:.2f}")
                    print(f"   Mean: {mean_val:.2f}")
                    print(f"   Median: {median_val:.2f}")
                    print(f"   Std Dev: {std_val:.2f}")
                    
                    # Calculate percentiles for better slider ranges
                    p5 = values.quantile(0.05)
                    p95 = values.quantile(0.95)
                    print(f"   5th-95th percentile: {p5:.2f} - {p95:.2f}")
                    
                    # Check for outliers
                    q1 = values.quantile(0.25)
                    q3 = values.quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    outliers = values[(values < lower_bound) | (values > upper_bound)]
                    print(f"   Outliers: {len(outliers)} values")
                    
                else:
                    print(f"\n❌ {description}")
                    print(f"   Column: {column}")
                    print(f"   No valid data found")
            else:
                print(f"\n❌ {description}")
                print(f"   Column: {column}")
                print(f"   Column not found in dataset")
        
        # Generate recommended slider ranges
        print(f"\n🎯 RECOMMENDED SLIDER RANGES:")
        print("=" * 50)
        
        recommendations = {}
        
        for column, description in key_columns.items():
            if column in df.columns:
                values = df[column].dropna()
                if len(values) > 0:
                    min_val = values.min()
                    max_val = values.max()
                    p5 = values.quantile(0.05)
                    p95 = values.quantile(0.95)
                    
                    # Recommended range: extend slightly beyond 5th-95th percentile
                    recommended_min = max(0, p5 - (p95 - p5) * 0.1)
                    recommended_max = p95 + (p95 - p5) * 0.1
                    
                    # Round appropriately
                    if 'Creatinine' in column or 'HgbA1C' in column:
                        recommended_min = round(recommended_min, 1)
                        recommended_max = round(recommended_max, 1)
                        step = 0.1
                    else:
                        recommended_min = int(round(recommended_min))
                        recommended_max = int(round(recommended_max))
                        step = 1
                    
                    recommendations[column] = {
                        'description': description,
                        'min': recommended_min,
                        'max': recommended_max,
                        'step': step,
                        'actual_min': min_val,
                        'actual_max': max_val,
                        'p5': p5,
                        'p95': p95
                    }
                    
                    print(f"\n📊 {description}")
                    print(f"   Recommended Range: {recommended_min} - {recommended_max}")
                    print(f"   Step: {step}")
                    print(f"   Actual Range: {min_val:.2f} - {max_val:.2f}")
                    print(f"   95% Coverage: {p5:.2f} - {p95:.2f}")
        
        # Generate HTML slider updates
        print(f"\n🔧 HTML SLIDER UPDATES:")
        print("=" * 50)
        
        for column, rec in recommendations.items():
            slider_id = column.lower().replace('baseline', '') + 'slider'
            value_id = column.lower().replace('baseline', '') + 'value'
            
            print(f"\n<!-- {rec['description']} -->")
            print(f'<div class="slider-container">')
            print(f'    <label class="form-label">{rec["description"].split("(")[0].strip()}: <span id="{value_id}">150</span> {rec["description"].split("(")[1].replace(")", "")}</label>')
            print(f'    <input type="range" class="custom-slider" id="{slider_id}" min="{rec["min"]}" max="{rec["max"]}" step="{rec["step"]}" value="{(rec["min"] + rec["max"]) // 2}">')
            print(f'</div>')
        
        # Generate JavaScript updates
        print(f"\n💻 JAVASCRIPT BINDING UPDATES:")
        print("=" * 50)
        
        for column, rec in recommendations.items():
            slider_id = column.lower().replace('baseline', '') + 'slider'
            data_key = column.lower().replace('baseline', '')
            value_id = column.lower().replace('baseline', '') + 'value'
            
            if rec['step'] == 0.1:
                converter = 'parseFloat'
            else:
                converter = 'parseInt'
            
            print(f"this.bindSliderEvent('{slider_id}', '{data_key}', '{value_id}', (value) => {converter}(value));")
        
        return recommendations
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    recommendations = check_dataset_ranges()
