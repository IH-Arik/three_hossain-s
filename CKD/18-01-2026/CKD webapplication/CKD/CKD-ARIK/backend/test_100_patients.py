import pandas as pd
import requests
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import time
import random

def test_100_patients():
    """Test the improved CKD prediction system on 100 random patients"""
    
    print("=" * 80)
    print("🏥 CKD PREDICTION SYSTEM - 100 PATIENT VALIDATION")
    print("📊 Testing Improved Model Performance")
    print("=" * 80)
    
    # Load the dataset
    try:
        df = pd.read_excel('../pone.0199920.s002.xlsx')
        print(f"✅ Dataset loaded: {df.shape}")
        print(f"🎯 Total CKD cases: {df['EventCKD35'].sum()} ({df['EventCKD35'].sum()/len(df)*100:.1f}%)")
        print()
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return
    
    # Sample 100 random patients (stratified to maintain CKD ratio)
    ckd_patients = df[df['EventCKD35'] == 1]
    non_ckd_patients = df[df['EventCKD35'] == 0]
    
    # Sample proportionally (about 11 CKD and 89 non-CKD for 100 total)
    n_ckd = min(11, len(ckd_patients))
    n_non_ckd = min(89, len(non_ckd_patients))
    
    sampled_ckd = ckd_patients.sample(n=n_ckd, random_state=42)
    sampled_non_ckd = non_ckd_patients.sample(n=n_non_ckd, random_state=42)
    
    test_df = pd.concat([sampled_ckd, sampled_non_ckd]).sample(frac=1, random_state=42)  # Shuffle
    
    print(f"🔬 Testing on {len(test_df)} patients:")
    print(f"   🔴 CKD cases: {len(sampled_ckd)}")
    print(f"   🟢 Non-CKD cases: {len(sampled_non_ckd)}")
    print()
    
    # Test configuration
    api_url = "http://localhost:8000/predict"
    
    # Storage for results
    results = {
        'patient_ids': [],
        'actual_ckd': [],
        'predicted_ckd': [],
        'probabilities': [],
        'prediction_times': [],
        'errors': []
    }
    
    print("🔄 Processing patients...")
    print("-" * 50)
    
    total_start_time = time.time()
    
    for idx, row in test_df.iterrows():
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
                
                # Show progress
                status = "✅" if actual_ckd == predicted_ckd else "❌"
                ckd_status = "CKD" if actual_ckd else "No CKD"
                pred_status = "CKD" if predicted_ckd else "No CKD"
                
                print(f"{status} Patient {patient_id}: {ckd_status} → {pred_status} ({probability:.3f}) [{request_time:.3f}s]")
                
            else:
                results['patient_ids'].append(patient_id)
                results['actual_ckd'].append(actual_ckd)
                results['predicted_ckd'].append(None)
                results['probabilities'].append(None)
                results['prediction_times'].append(None)
                results['errors'].append(f"HTTP {response.status_code}")
                print(f"❌ Patient {patient_id}: HTTP {response.status_code}")
                
        except Exception as e:
            results['patient_ids'].append(patient_id)
            results['actual_ckd'].append(actual_ckd)
            results['predicted_ckd'].append(None)
            results['probabilities'].append(None)
            results['prediction_times'].append(None)
            results['errors'].append(str(e))
            print(f"❌ Patient {patient_id}: {str(e)}")
    
    total_time = time.time() - total_start_time
    
    print("\n" + "=" * 80)
    print("📊 PERFORMANCE ANALYSIS - 100 PATIENTS")
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
        print(f"⏱️  TOTAL TIME: {total_time:.2f}s")
        print(f"⏱️  AVG TIME/PATIENT: {avg_time:.4f}s")
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
        
        # CKD-specific metrics
        ckd_actual = sum(actual_valid)
        ckd_predicted = sum(predicted_valid)
        ckd_correctly_detected = sum(1 for a, p in zip(actual_valid, predicted_valid) if a and p)
        
        print("🏥 CKD-SPECIFIC ANALYSIS:")
        print(f"   Actual CKD cases: {ckd_actual}")
        print(f"   Predicted CKD cases: {ckd_predicted}")
        print(f"   Correctly detected: {ckd_correctly_detected}")
        print(f"   CKD Detection Rate: {ckd_correctly_detected/ckd_actual*100:.1f}%")
        print()
        
        # Risk distribution analysis
        print("📊 RISK DISTRIBUTION:")
        low_risk = sum(1 for p in probabilities_valid if p < 0.3)
        medium_risk = sum(1 for p in probabilities_valid if 0.3 <= p < 0.7)
        high_risk = sum(1 for p in probabilities_valid if p >= 0.7)
        
        print(f"   Low risk (<30%): {low_risk} ({low_risk/len(probabilities_valid)*100:.1f}%)")
        print(f"   Medium risk (30-70%): {medium_risk} ({medium_risk/len(probabilities_valid)*100:.1f}%)")
        print(f"   High risk (≥70%): {high_risk} ({high_risk/len(probabilities_valid)*100:.1f}%)")
        print()
        
        # Performance assessment
        print("🏥 CLINICAL ASSESSMENT:")
        if accuracy >= 0.9:
            print("   🎉 EXCELLENT - High accuracy suitable for clinical use")
        elif accuracy >= 0.8:
            print("   👍 GOOD - Suitable for clinical research")
        elif accuracy >= 0.7:
            print("   🟡 MODERATE - Needs improvement")
        else:
            print("   🔴 POOR - Not recommended for clinical use")
        
        if recall >= 0.8:
            print("   ✅ HIGH SENSITIVITY - Excellent CKD detection")
        elif recall >= 0.6:
            print("   🟡 GOOD SENSITIVITY - Adequate CKD detection")
        else:
            print("   ❌ LOW SENSITIVITY - Poor CKD detection")
        
        if specificity >= 0.9:
            print("   ✅ HIGH SPECIFICITY - Excellent at ruling out CKD")
        elif specificity >= 0.8:
            print("   🟡 GOOD SPECIFICITY - Good at ruling out CKD")
        else:
            print("   ❌ LOW SPECIFICITY - Many false positives")
        
        # Comparison with original model
        print()
        print("📈 IMPROVEMENT COMPARISON:")
        print("   Original Model Sensitivity: ~24%")
        print(f"   Improved Model Sensitivity: {recall*100:.1f}%")
        print(f"   Improvement: +{(recall*100 - 24):.1f}%")
        
    else:
        print("❌ No valid predictions obtained")
    
    # Show detailed results for CKD cases
    print()
    print("=" * 80)
    print("🔍 CKD CASES DETAILED ANALYSIS")
    print("=" * 80)
    
    ckd_results = []
    for i, idx in enumerate(valid_results):
        if results['actual_ckd'][idx]:  # CKD cases
            patient_id = results['patient_ids'][idx]
            predicted = results['predicted_ckd'][idx]
            probability = results['probabilities'][idx]
            prediction_time = results['prediction_times'][idx]
            
            ckd_results.append({
                'patient_id': patient_id,
                'predicted': predicted,
                'probability': probability,
                'time': prediction_time
            })
    
    print(f"🎯 CKD Cases Analysis ({len(ckd_results)} total):")
    
    correctly_detected = 0
    for result in ckd_results:
        status = "✅ DETECTED" if result['predicted'] else "❌ MISSED"
        print(f"   Patient {result['patient_id']}: {status} (Risk: {result['probability']:.3f})")
        if result['predicted']:
            correctly_detected += 1
    
    print(f"\n   CKD Detection Rate: {correctly_detected}/{len(ckd_results)} ({correctly_detected/len(ckd_results)*100:.1f}%)")
    
    print()
    print("=" * 80)
    print("🎉 100 PATIENT VALIDATION COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_100_patients()
