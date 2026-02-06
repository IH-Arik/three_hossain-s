import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import joblib

def create_ckd_dl_model(input_dim=24):
    """
    Create a deep learning model for CKD prediction
    Architecture designed for medical tabular data
    """
    model = Sequential([
        # Input layer
        Dense(128, activation='relu', input_shape=(input_dim,)),
        BatchNormalization(),
        Dropout(0.3),
        
        # Hidden layer 1
        Dense(64, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        
        # Hidden layer 2
        Dense(32, activation='relu'),
        BatchNormalization(),
        Dropout(0.2),
        
        # Hidden layer 3
        Dense(16, activation='relu'),
        BatchNormalization(),
        Dropout(0.2),
        
        # Output layer
        Dense(1, activation='sigmoid')
    ])
    
    # Compile the model
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy', 'AUC']
    )
    
    return model

def create_and_train_model():
    """
    Create and train a deep learning model for CKD prediction
    """
    print("Creating CKD Deep Learning Model...")
    
    # Create the model
    model = create_ckd_dl_model(input_dim=24)
    
    # Generate synthetic training data (since we don't have the original dataset)
    # In production, you should use the same training data as your Random Forest
    print("Generating synthetic training data...")
    
    # Create synthetic data that mimics medical patterns
    np.random.seed(42)
    n_samples = 1000
    
    # Generate features with realistic medical patterns
    X_train = np.random.randn(n_samples, 24)
    
    # Create patterns that make medical sense
    # Higher creatinine and lower eGFR -> higher CKD risk
    X_train[:, 4] = np.random.normal(1.2, 0.5, n_samples)  # creatinine
    X_train[:, 5] = np.random.normal(75, 25, n_samples)    # eGFR
    X_train[:, 3] = np.random.normal(6.5, 1.5, n_samples)  # HbA1c
    
    # Create target variable with medical logic
    y_train = np.zeros(n_samples)
    
    # CKD risk based on medical factors
    risk_score = (
        (X_train[:, 4] > 1.5) * 0.3 +      # high creatinine
        (X_train[:, 5] < 60) * 0.3 +       # low eGFR  
        (X_train[:, 3] > 7.0) * 0.2 +      # high HbA1c
        (X_train[:, 11] > 0.5) * 0.1 +     # diabetes
        (X_train[:, 15] > 0.5) * 0.1       # hypertension
    )
    
    y_train = (risk_score + np.random.normal(0, 0.1, n_samples)) > 0.5
    y_train = y_train.astype(int)
    
    print(f"Training data shape: {X_train.shape}")
    print(f"Target distribution: {np.bincount(y_train)}")
    
    # Train the model
    print("Training the deep learning model...")
    
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    )
    
    history = model.fit(
        X_train, y_train,
        epochs=100,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stopping],
        verbose=1
    )
    
    # Save the model
    model.save('models/ckd_model.h5')
    print("✓ Deep learning model saved as 'models/ckd_model.h5'")
    
    # Test the model
    print("\nTesting the model...")
    test_input = np.array([[
        55,    # age
        200,   # cholesterol
        150,   # triglycerides  
        6.5,   # hba1c
        1.2,   # creatinine
        90,    # egfr
        130,   # sbp
        80,    # dbp
        25,    # bmi
        12,    # time_to_event
        1,     # gender
        0,     # diabetes
        0,     # chd
        0,     # vascular
        0,     # smoking
        1,     # htn
        0,     # dld
        0,     # obesity
        0,     # dld_meds
        0,     # dm_meds
        1,     # htn_meds
        0,     # acei_arb
        0,     # age_category_1 (middle age)
        1      # age_category_2 (middle age)
    ]])
    
    prediction = model.predict(test_input)[0][0]
    print(f"Test prediction: {prediction:.4f}")
    
    return model, history

if __name__ == "__main__":
    try:
        model, history = create_and_train_model()
        print("\n✅ Deep learning model created successfully!")
        print("📁 Model saved as: backend/models/ckd_model.h5")
        print("🔄 Ready for ensemble predictions with Random Forest model")
        
    except Exception as e:
        print(f"❌ Error creating model: {e}")
        print("📝 Note: Make sure TensorFlow is installed: pip install tensorflow")
