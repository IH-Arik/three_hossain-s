"""
Create H5 model directly in models directory
"""

import os
import sys
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

def create_simple_h5_model():
    """Create a simple H5 model for testing"""
    
    print("🔧 Creating H5 model...")
    
    try:
        # Load and prepare data
        df = pd.read_excel('../pone.0199920.s002.xlsx')
        
        # Prepare features
        feature_columns = [
            'AgeBaseline', 'HistoryDiabetes', 'HistoryCHD', 'HistoryVascular',
            'HistorySmoking', 'HistoryHTN', 'HistoryDLD', 'HistoryObesity',
            'DLDmeds', 'DMmeds', 'HTNmeds', 'ACEIARB',
            'CholesterolBaseline', 'TriglyceridesBaseline', 'HgbA1C',
            'CreatnineBaseline', 'eGFRBaseline', 'sBPBaseline', 'dBPBaseline',
            'BMIBaseline'
        ]
        
        X = df[feature_columns].fillna(df[feature_columns].mean())
        y = df['EventCKD35']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Create model
        model = Sequential([
            Dense(64, activation='relu', input_shape=(X_train_scaled.shape[1],)),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dropout(0.3),
            Dense(16, activation='relu'),
            Dropout(0.2),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'AUC']
        )
        
        # Train model
        print("📊 Training model...")
        early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        
        model.fit(
            X_train_scaled, y_train,
            validation_split=0.2,
            epochs=50,
            batch_size=32,
            callbacks=[early_stopping],
            verbose=0
        )
        
        # Ensure models directory exists
        os.makedirs('models', exist_ok=True)
        
        # Save model
        model_path = 'models/ckd_model.h5'
        model.save(model_path)
        print(f"✅ H5 model saved to {model_path}")
        
        # Test model
        print("🧪 Testing model...")
        test_pred = model.predict(X_test_scaled[:5])
        print(f"Sample predictions: {test_pred.flatten()[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating H5 model: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_simple_h5_model()
    if success:
        print("\n🎉 H5 model created successfully!")
        print("🚀 Restart backend to use the H5 model")
    else:
        print("\n❌ Failed to create H5 model")
