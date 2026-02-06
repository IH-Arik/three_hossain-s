import pandas as pd
import requests
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report
import time

def test_full_dataset():
    """Test the CKD prediction system on the entire PLoS ONE dataset"""
    
    print("=" * 80)
    print("🏥 COMPREHENSIVE CKD PREDICTION SYSTEM TEST")
    print("📊 Testing on Full PLoS ONE Dataset")
    print("=" * 80)
    
    # Load the dataset
    try:
        df = pd.read_excel('../pone.0199920.s002.xlsx')
        print(f"✅ Dataset loaded successfully!")
        print(f"📊 Total patients: {len(df)}")
        print(f"🎯 CKD cases: {df['EventCKD35'].sum()} ({df['EventCKD35'].sum()/len(df)*100:.1f}%)")
        print(f"🟢 Non-CKD cases: {len(df) - df['EventCKD35'].sum()} ({(len(df) - df['EventCKD35'].sum())/len(df)*100:.1f}%)")
        print()
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return
    
    # Test configuration
    api_url = "http://localhost:8000/predict"
    batch_size = 10  # Process in batches to avoid overwhelming the API
    max_patients = len(df)  # Test all patients
    
    # Limit to first max_patients if specified
    test_df = df.head(max_patients)
    
    print(f"🔬 Testing {len(test_df)} patients...")
    print(f"⏱️  Batch size: {batch_size}")
    print()
    
    # Storage for results
    results = {
        'patient_ids': [],
        'actual_ckd': [],
        'predicted_ckd': [],
        'probabilities': [],
        'prediction_times': [],
        'errors': []
    }
    
    # Process in batches
    total_batches = (len(test_df) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(test_df))
        batch_df = test_df.iloc[start_idx:end_idx]
        
        print(f"🔄 Processing batch {batch_num + 1}/{total_batches} (patients {start_idx + 1}-{end_idx})")
        
        batch_start_time = time.time()
        
        for idx, row in batch_df.iterrows():
            patient_id = row['StudyID']
            actual_ckd = bool(row['EventCKD35'])
            
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
                request_start_time = time.time()
                response = requests.post(api_url, json=api_data, timeout=10)
                request_time = time.time() - request_start_time
                
                if response.status_code == 200:
                    result = response.json()
                    predicted_ckd = result['ckd']
                    probability = result['probability']
                    
                    # Store results
                    results['patient_ids'].append(patient_id)
                    results['actual_ckd'].append(actual_ckd)
                    results['predicted_ckd'].append(predicted_ckd)
                    results['probabilities'].append(probability)
                    results['prediction_times'].append(request_time)
                    
                else:
                    results['patient_ids'].append(patient_id)
                    results['actual_ckd'].append(actual_ckd)
                    results['predicted_ckd'].append(None)
                    results['probabilities'].append(None)
                    results['prediction_times'].append(None)
                    results['errors'].append(f"HTTP {response.status_code}")
                    
            except Exception as e:
                results['patient_ids'].append(patient_id)
                results['actual_ckd'].append(actual_ckd)
                results['predicted_ckd'].append(None)
                results['probabilities'].append(None)
                results['prediction_times'].append(None)
                results['errors'].append(str(e))
        
        batch_time = time.time() - batch_start_time
        print(f"   ✅ Batch completed in {batch_time:.2f}s")
    
    print()
    print("=" * 80)
    print("📊 PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    # Calculate metrics
    valid_results = [i for i, pred in enumerate(results['predicted_ckd']) if pred is not None]
    
    if valid_results:
        actual_valid = [results['actual_ckd'][i] for i in valid_results]
        predicted_valid = [results['predicted_ckd'][i] for i in valid_results]
        probabilities_valid = [results['probabilities'][i] for i in valid_results]
        
        # Basic metrics
        accuracy = accuracy_score(actual_valid, predicted_valid)
        precision = precision_score(actual_valid, predicted_valid, zero_division=0)
        recall = recall_score(actual_valid, predicted_valid, zero_division=0)
        f1 = f1_score(actual_valid, predicted_valid, zero_division=0)
        
        # ROC AUC
        try:
            auc = roc_auc_score(actual_valid, probabilities_valid)
        except:
            auc = 0.0
        
        # Confusion matrix
        cm = confusion_matrix(actual_valid, predicted_valid)
        tn, fp, fn, tp = cm.ravel()
        
        # Additional metrics
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        # Timing metrics
        valid_times = [t for t in results['prediction_times'] if t is not None]
        avg_time = np.mean(valid_times) if valid_times else 0
        
        print(f"📈 VALID PREDICTIONS: {len(valid_results)}/{len(test_df)} ({len(valid_results)/len(test_df)*100:.1f}%)")
        print(f"❌ ERRORS: {len(results['errors'])}")
        print()
        print("🎯 CLASSIFICATION METRICS:")
        print(f"   Accuracy: {accuracy:.4f} ({accuracy*100:.1f}%)")
        print(f"   Precision: {precision:.4f} ({precision*100:.1f}%)")
        print(f"   Recall (Sensitivity): {recall:.4f} ({recall*100:.1f}%)")
        print(f"   F1-Score: {f1:.4f}")
        print(f"   ROC AUC: {auc:.4f}")
        print(f"   Specificity: {specificity:.4f} ({specificity*100:.1f}%)")
        print()
        print("🔢 CONFUSION MATRIX:")
        print(f"   True Negatives: {tn}")
        print(f"   False Positives: {fp}")
        print(f"   False Negatives: {fn}")
        print(f"   True Positives: {tp}")
        print()
        print(f"⏱️  PERFORMANCE:")
        print(f"   Average prediction time: {avg_time:.4f}s")
        print(f"   Total successful predictions: {len(valid_results)}")
        
        # Risk distribution analysis
        print()
        print("📊 RISK DISTRIBUTION ANALYSIS:")
        low_risk = sum(1 for p in probabilities_valid if p < 0.3)
        medium_risk = sum(1 for p in probabilities_valid if 0.3 <= p < 0.7)
        high_risk = sum(1 for p in probabilities_valid if p >= 0.7)
        
        print(f"   Low risk (<30%): {low_risk} ({low_risk/len(probabilities_valid)*100:.1f}%)")
        print(f"   Medium risk (30-70%): {medium_risk} ({medium_risk/len(probabilities_valid)*100:.1f}%)")
        print(f"   High risk (≥70%): {high_risk} ({high_risk/len(probabilities_valid)*100:.1f}%)")
        
        # Performance assessment
        print()
        print("🏥 CLINICAL ASSESSMENT:")
        if accuracy >= 0.8:
            print("   🎉 EXCELLENT - High accuracy suitable for clinical decision support")
        elif accuracy >= 0.7:
            print("   👍 GOOD - Suitable for clinical research and educational use")
        elif accuracy >= 0.6:
            print("   🟡 MODERATE - Needs improvement for clinical use")
        else:
            print("   🔴 POOR - Not recommended for clinical use")
        
        if recall >= 0.8:
            print("   ✅ HIGH SENSITIVITY - Good at detecting CKD cases")
        elif recall >= 0.6:
            print("   🟡 MODERATE SENSITIVITY - May miss some CKD cases")
        else:
            print("   ❌ LOW SENSITIVITY - Poor CKD detection")
        
        if specificity >= 0.8:
            print("   ✅ HIGH SPECIFICITY - Good at ruling out CKD")
        elif specificity >= 0.6:
            print("   🟡 MODERATE SPECIFICITY - Some false positives")
        else:
            print("   ❌ LOW SPECIFICITY - Many false positives")
        
    else:
        print("❌ No valid predictions obtained")
    
    # Show some example predictions
    print()
    print("=" * 80)
    print("🔍 SAMPLE PREDICTIONS")
    print("=" * 80)
    
    sample_size = min(10, len(valid_results))
    sample_indices = valid_results[:sample_size]
    
    for i, idx in enumerate(sample_indices):
        patient_id = results['patient_ids'][idx]
        actual = results['actual_ckd'][idx]
        predicted = results['predicted_ckd'][idx]
        probability = results['probabilities'][idx]
        prediction_time = results['prediction_times'][idx]
        
        status = "✅ CORRECT" if actual == predicted else "❌ INCORRECT"
        
        print(f"Patient {patient_id}: {status}")
        print(f"  Actual: {'CKD' if actual else 'No CKD'}")
        print(f"  Predicted: {'CKD' if predicted else 'No CKD'} ({probability:.3f})")
        print(f"  Time: {prediction_time:.4f}s")
        print()
    
    print("=" * 80)
    print("🎉 FULL DATASET TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_full_dataset()
