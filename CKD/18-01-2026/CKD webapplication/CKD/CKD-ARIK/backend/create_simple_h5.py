"""
Create a simple H5 model for testing
"""

import os
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam

def create_simple_h5():
    """Create a simple H5 model"""
    
    print("🔧 Creating simple H5 model...")
    
    try:
        # Create a simple model with correct input shape
        model = Sequential([
            Dense(64, activation='relu', input_shape=(22,)),  # 22 features
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
        
        # Ensure models directory exists
        os.makedirs('models', exist_ok=True)
        
        # Save model
        model_path = 'models/ckd_model.h5'
        model.save(model_path)
        print(f"✅ H5 model saved to {model_path}")
        
        # Test model with dummy data
        print("🧪 Testing model...")
        dummy_input = np.random.random((1, 22))
        test_pred = model.predict(dummy_input, verbose=0)
        print(f"Sample prediction: {test_pred[0][0]:.6f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating H5 model: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_simple_h5()
    if success:
        print("\n🎉 Simple H5 model created successfully!")
        print("🚀 Restart backend to use the H5 model")
    else:
        print("\n❌ Failed to create H5 model")
