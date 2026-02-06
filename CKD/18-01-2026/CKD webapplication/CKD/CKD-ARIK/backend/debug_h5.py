"""
Debug the H5 model to see why it's returning 0.000
"""

import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from utils.edckd_preprocessor import create_edckd_preprocessor

def debug_h5_model():
    """Debug the H5 model directly"""
    
    print("🔍 DEBUGGING H5 MODEL")
    print("=" * 40)
    
    try:
        # Load preprocessor and model
        preprocessor = create_edckd_preprocessor()
        if not preprocessor.is_fitted:
            preprocessor.fit_from_dataset('../pone.0199920.s002.xlsx')
        
        model = load_model('models/ckd_model.h5')
        print("✅ Model and preprocessor loaded")
        
        # Load test data
        df = pd.read_excel('../pone.0199920.s002.xlsx')
        
        # Test with a few patients
        test_patients = df.head(5)
        
        for idx, row in test_patients.iterrows():
            print(f"\n📋 Patient {row['StudyID']}:")
            print(f"   Actual CKD: {row['EventCKD35']}")
            
            # Prepare data
            features = (preprocessor.dataset_config['numerical_cols'] + 
                       preprocessor.dataset_config['binary_categorical_cols'] + 
                       preprocessor.dataset_config['non_binary_categorical_cols'])
            
            patient_data = {}
            for feature in features:
                if feature in row:
                    patient_data[feature] = row[feature]
            
            # Convert to DataFrame
            patient_df = pd.DataFrame([patient_data])
            
            # Apply preprocessing
            X_processed = preprocessor.preprocessor.transform(patient_df)
            print(f"   Processed shape: {X_processed.shape}")
            print(f"   Processed data type: {X_processed.dtype}")
            print(f"   Sample values: {X_processed[0][:5]}")
            
            # Test with different data types
            X_float32 = X_processed.astype(np.float32)
            X_float64 = X_processed.astype(np.float64)
            
            # Predictions
            pred_original = model.predict(X_processed, verbose=0)[0][0]
            pred_float32 = model.predict(X_float32, verbose=0)[0][0]
            pred_float64 = model.predict(X_float64, verbose=0)[0][0]
            
            print(f"   Original prediction: {pred_original:.6f}")
            print(f"   Float32 prediction: {pred_float32:.6f}")
            print(f"   Float64 prediction: {pred_float64:.6f}")
            
            # Check model weights
            print(f"   Model input shape: {model.input_shape}")
            print(f"   Model output shape: {model.output_shape}")
        
        # Test with synthetic data
        print("\n🧪 Testing with synthetic data...")
        synthetic_data = np.random.randn(1, 24).astype(np.float32)
        synthetic_pred = model.predict(synthetic_data, verbose=0)[0][0]
        print(f"   Synthetic prediction: {synthetic_pred:.6f}")
        
        # Test with extreme values
        print("\n🔥 Testing with extreme values...")
        extreme_data = np.ones((1, 24)) * 10.0  # High values
        extreme_pred = model.predict(extreme_data.astype(np.float32), verbose=0)[0][0]
        print(f"   Extreme prediction: {extreme_pred:.6f}")
        
        zero_data = np.zeros((1, 24))
        zero_pred = model.predict(zero_data.astype(np.float32), verbose=0)[0][0]
        print(f"   Zero prediction: {zero_pred:.6f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_h5_model()
