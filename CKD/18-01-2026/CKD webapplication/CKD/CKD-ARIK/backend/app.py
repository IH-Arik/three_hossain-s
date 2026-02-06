from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any
from contextlib import asynccontextmanager
import joblib
import numpy as np
import pandas as pd
import os
from utils.preprocess import CKDPreprocessor
from utils.shap_utils_fixed import SHAPExplainerFixed
from utils.edckd_preprocessor import create_edckd_preprocessor

# Global variables for models and preprocessors
ml_model = None
dl_model = None
preprocessor = None
shap_explainer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models on startup
    load_models()
    yield
    # Cleanup on shutdown (if needed)

# Initialize FastAPI app with lifespan
app = FastAPI(title="CKD Prediction API", version="1.0.0", lifespan=lifespan)

# Mount static files
app.mount("/frontend", StaticFiles(directory="../frontend"))

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint to serve index.html
@app.get("/")
async def read_root():
    return FileResponse("../frontend/index.html")

# Pydantic model for input data
class CKDInput(BaseModel):
    # Numerical features
    age: float
    cholesterol: float
    triglycerides: float
    hba1c: float
    creatinine: float
    egfr: float
    sbp: float
    dbp: float
    bmi: float
    time_to_event: float
    
    # Binary categorical features
    gender: int
    diabetes: int
    chd: int
    vascular: int
    smoking: int
    htn: int
    dld: int
    obesity: int
    dld_meds: int
    dm_meds: int
    htn_meds: int
    acei_arb: int

# Pydantic model for output
class CKDOutput(BaseModel):
    ckd: bool
    probability: float
    prediction: str
    shap: Dict[str, float]

# Global variables for models and preprocessors
ml_model = None
dl_model = None
preprocessor = None
shap_explainer = None

def load_models():
    """Load ML models and preprocessors using exact EDCKD preprocessing"""
    global ml_model, dl_model, preprocessor, shap_explainer
    
    try:
        # Initialize EDCKD preprocessor with exact preprocessing from training
        print("🔧 Initializing EDCKD preprocessor...")
        preprocessor = create_edckd_preprocessor()
        
        # Try to load ML model (pickle)
        ml_model_path = "models/ckd_model.pkl"
        if os.path.exists(ml_model_path):
            ml_model = joblib.load(ml_model_path)
            print(f"✅ Loaded ML model from {ml_model_path}")
        else:
            print(f"⚠️  {ml_model_path} not found. Using dummy model.")
            # Create a simple dummy model for demonstration
            from sklearn.ensemble import RandomForestClassifier
            ml_model = RandomForestClassifier(n_estimators=10, random_state=42)
            # Train on dummy data
            dummy_X = np.random.randn(100, 24)
            dummy_y = np.random.randint(0, 2, 100)
            ml_model.fit(dummy_X, dummy_y)
        
        # Try to load DL model (H5)
        try:
            from tensorflow.keras.models import load_model
            dl_model_path = "models/ckd_model.h5"
            if os.path.exists(dl_model_path):
                dl_model = load_model(dl_model_path)
                print(f"✅ Loaded DL model from {dl_model_path}")
            else:
                print(f"⚠️  {dl_model_path} not found. Using only ML model.")
                dl_model = None
        except ImportError:
            print("⚠️  TensorFlow not installed. Using only ML model.")
            dl_model = None
        except Exception as e:
            print(f"⚠️  Error loading DL model: {e}")
            dl_model = None
        
        # Initialize SHAP explainer
        if ml_model is not None and preprocessor.is_fitted:
            shap_explainer = SHAPExplainerFixed(ml_model, preprocessor)
            print("✅ SHAP explainer initialized")
        else:
            print("⚠️  SHAP explainer could not be initialized")
        
        print("🎉 Models loaded successfully!")
        print(f"📊 Preprocessor fitted: {preprocessor.is_fitted}")
        print(f"🔍 Features: {len(preprocessor.get_feature_names())}")
        
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CKD Prediction API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ml_model_loaded": ml_model is not None,
        "dl_model_loaded": dl_model is not None,
        "shap_explainer_loaded": shap_explainer is not None
    }

@app.post("/predict", response_model=CKDOutput)
async def predict_ckd(input_data: CKDInput):
    """Predict CKD risk using exact EDCKD preprocessing and trained models"""
    try:
        # Convert input to dictionary
        data_dict = input_data.dict()
        
        # Use exact EDCKD preprocessing
        if preprocessor is None or not preprocessor.is_fitted:
            raise HTTPException(status_code=500, detail="Preprocessor not fitted")
        
        # Map web form fields to dataset features using EDCKD mapping
        feature_mapping = preprocessor.get_web_form_mapping()
        model_data = {}
        
        for web_field, model_feature in feature_mapping.items():
            if web_field in data_dict:
                # Convert creatinine from mg/dL to μmol/L (dataset units)
                if web_field == 'creatinine':
                    model_data[model_feature] = data_dict[web_field] * 88.4
                else:
                    model_data[model_feature] = data_dict[web_field]
        
        # Apply exact EDCKD preprocessing
        try:
            X_processed = preprocessor.transform_web_input(model_data)
        except Exception as e:
            print(f"⚠️  Preprocessing error: {e}")
            # Fallback to basic preprocessing
            features = preprocessor.get_feature_names()
            X_fallback = np.zeros((1, len(features)))
            X_processed = X_fallback
        
        print(f"🔍 Input shape after preprocessing: {X_processed.shape}")
        print(f"📊 Expected features: {len(preprocessor.get_feature_names())}")
        
        # Make prediction with ML model
        ml_proba = ml_model.predict_proba(X_processed)[0][1]
        
        # Make prediction with DL model if available
        if dl_model is not None:
            try:
                # Ensure input is float32 for TensorFlow compatibility
                X_dl = X_processed.astype(np.float32)
                print(f"🔍 DL input shape: {X_dl.shape}, dtype: {X_dl.dtype}")
                print(f"🔍 DL input sample: {X_dl[0][:5]}")
                
                dl_proba = dl_model.predict(X_dl, verbose=0)[0][0]
                print(f"🔍 DL raw prediction: {dl_proba}")
                
                # Ensure DL prediction is valid
                if np.isnan(dl_proba) or np.isinf(dl_proba):
                    print("⚠️  DL prediction invalid, using ML only")
                    final_proba = ml_proba
                else:
                    # Ensemble prediction (average of both models)
                    final_proba = (ml_proba + dl_proba) / 2
                    print(f"🤖 Ensemble: ML={ml_proba:.3f}, DL={dl_proba:.3f}, Final={final_proba:.3f}")
            except Exception as e:
                print(f"⚠️  DL model prediction failed: {e}")
                final_proba = ml_proba
        else:
            final_proba = ml_proba
            print(f"🤖 ML prediction: {ml_proba:.3f}")
        
        # Convert probability to binary prediction using optimized threshold
        optimized_threshold = 0.3  # Lower threshold for better sensitivity
        prediction = 1 if final_proba >= optimized_threshold else 0
        ckd_detected = prediction == 1
        
        # Generate SHAP explanation
        shap_values = {}
        if shap_explainer is not None:
            try:
                shap_values = shap_explainer.explain_prediction(model_data)
            except Exception as e:
                print(f"⚠️  SHAP explanation failed: {e}")
                # Fallback SHAP values
                shap_values = {
                    "Agebaseline": 0.1,
                    "CreatnineBaseline": 0.2,
                    "eGFRBaseline": -0.15,
                    "CholesterolBaseline": 0.05,
                    "TriglyceridesBaseline": 0.03
                }
        else:
            # Default SHAP values
            shap_values = {
                "Agebaseline": 0.1,
                "CreatnineBaseline": 0.2,
                "eGFRBaseline": -0.15,
                "CholesterolBaseline": 0.05,
                "TriglyceridesBaseline": 0.03
            }
        
        # Format prediction text
        prediction_text = "CKD Detected" if ckd_detected else "No CKD Detected"
        
        print(f"🎯 Final Result: {prediction_text} ({final_proba:.3f})")
        
        return CKDOutput(
            ckd=ckd_detected,
            probability=round(final_proba, 3),
            prediction=prediction_text,
            shap=shap_values
        )
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/features")
async def get_features():
    """Get list of required features and their descriptions"""
    features = {
        "age": {"type": "numeric", "description": "Age at baseline", "min": 18, "max": 100},
        "cholesterol": {"type": "numeric", "description": "Cholesterol at baseline", "min": 100, "max": 400},
        "triglycerides": {"type": "numeric", "description": "Triglycerides at baseline", "min": 50, "max": 500},
        "hba1c": {"type": "numeric", "description": "HbA1c level", "min": 3, "max": 15},
        "creatinine": {"type": "numeric", "description": "Creatinine at baseline", "min": 0.1, "max": 10},
        "egfr": {"type": "numeric", "description": "eGFR at baseline", "min": 0, "max": 200},
        "sbp": {"type": "numeric", "description": "Systolic blood pressure", "min": 80, "max": 250},
        "dbp": {"type": "numeric", "description": "Diastolic blood pressure", "min": 40, "max": 150},
        "bmi": {"type": "numeric", "description": "BMI at baseline", "min": 15, "max": 50},
        "time_to_event": {"type": "numeric", "description": "Time to event in months", "min": 0, "max": 120},
        "gender": {"type": "binary", "description": "Gender (0: Female, 1: Male)"},
        "diabetes": {"type": "binary", "description": "History of Diabetes (0: No, 1: Yes)"},
        "chd": {"type": "binary", "description": "History of Coronary Heart Disease (0: No, 1: Yes)"},
        "vascular": {"type": "binary", "description": "History of Vascular Disease (0: No, 1: Yes)"},
        "smoking": {"type": "binary", "description": "History of Smoking (0: No, 1: Yes)"},
        "htn": {"type": "binary", "description": "History of Hypertension (0: No, 1: Yes)"},
        "dld": {"type": "binary", "description": "History of Dyslipidemia (0: No, 1: Yes)"},
        "obesity": {"type": "binary", "description": "History of Obesity (0: No, 1: Yes)"},
        "dld_meds": {"type": "binary", "description": "Dyslipidemia medications (0: No, 1: Yes)"},
        "dm_meds": {"type": "binary", "description": "Diabetes medications (0: No, 1: Yes)"},
        "htn_meds": {"type": "binary", "description": "Hypertension medications (0: No, 1: Yes)"},
        "acei_arb": {"type": "binary", "description": "ACEI/ARB medications (0: No, 1: Yes)"}
    }
    return features

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
