"""
Fix the H5 deep learning model to work with the EDCKD preprocessing
"""

import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import joblib

def fix_h5_model():
    """Retrain H5 model with proper EDCKD preprocessing"""
    
    print("=" * 60)
    print("🔧 FIXING H5 DEEP LEARNING MODEL")
    print("=" * 60)
    
    try:
        # Load and preprocess the dataset using exact EDCKD preprocessing
        from utils.edckd_preprocessor import create_edckd_preprocessor
        
        preprocessor = create_edckd_preprocessor()
        if not preprocessor.is_fitted:
            preprocessor.fit_from_dataset('../pone.0199920.s002.xlsx')
        
        # Load dataset
        df = pd.read_excel('../pone.0199920.s002.xlsx')
        
        # Apply EDCKD preprocessing
        features = (preprocessor.dataset_config['numerical_cols'] + 
                   preprocessor.dataset_config['binary_categorical_cols'] + 
                   preprocessor.dataset_config['non_binary_categorical_cols'])
        
        X = df[features]
        y = df['EventCKD35']
        
        # Apply preprocessing
        X_processed = preprocessor.preprocessor.transform(X)
        
        print(f"✅ Data loaded and preprocessed: {X_processed.shape}")
        print(f"🎯 CKD cases: {y.sum()} ({y.mean()*100:.1f}%)")
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed, y, test_size=0.2, stratify=y, random_state=42
        )
        
        print(f"📊 Train set: {X_train.shape}, Test set: {X_test.shape}")
        
        # Create improved deep learning model
        model = Sequential([
            Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(32, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(16, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            
            Dense(1, activation='sigmoid')
        ])
        
        # Compile with appropriate learning rate
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'AUC']
        )
        
        print("🏗️  Model architecture created")
        
        # Train with class weights to handle imbalance
        from sklearn.utils.class_weight import compute_class_weight
        class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
        class_weight_dict = dict(zip(np.unique(y_train), class_weights))
        
        print(f"⚖️  Class weights: {class_weight_dict}")
        
        # Train the model
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        )
        
        print("\n🚀 Training H5 model...")
        history = model.fit(
            X_train.astype(np.float32), y_train,
            epochs=100,
            batch_size=32,
            validation_split=0.2,
            callbacks=[early_stopping],
            class_weight=class_weight_dict,
            verbose=1
        )
        
        # Evaluate the model
        print("\n📊 Evaluating model...")
        loss, accuracy, auc = model.evaluate(X_test.astype(np.float32), y_test, verbose=0)
        print(f"   Test Loss: {loss:.4f}")
        print(f"   Test Accuracy: {accuracy:.4f}")
        print(f"   Test AUC: {auc:.4f}")
        
        # Test predictions
        y_pred_proba = model.predict(X_test.astype(np.float32), verbose=0)
        y_pred = (y_pred_proba >= 0.3).astype(int)  # Use same threshold as ensemble
        
        from sklearn.metrics import recall_score, precision_score
        sensitivity = recall_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        
        print(f"   Sensitivity: {sensitivity:.4f}")
        print(f"   Precision: {precision:.4f}")
        
        # Save the improved model
        model.save('models/ckd_model.h5')
        print("✅ Fixed H5 model saved")
        
        # Test with a sample prediction
        print("\n🧪 Testing sample prediction...")
        sample_input = X_test[0:1].astype(np.float32)
        sample_pred = model.predict(sample_input, verbose=0)[0][0]
        print(f"   Sample prediction: {sample_pred:.4f}")
        
        print("\n" + "=" * 60)
        print("🎉 H5 MODEL FIX COMPLETED")
        print("=" * 60)
        print("✅ Model retrained with EDCKD preprocessing")
        print("✅ Class weights applied for imbalance")
        print("✅ Optimized threshold alignment")
        print("✅ Ready for ensemble predictions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing H5 model: {e}")
        return False

if __name__ == "__main__":
    success = fix_h5_model()
    if success:
        print("\n🚀 Restart the backend to use the fixed H5 model")
    else:
        print("\n❌ Fix failed - check error messages above")
