import shap
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

class SHAPExplainer:
    def __init__(self, model, preprocessor):
        self.model = model
        self.preprocessor = preprocessor
        self.explainer = None
        self.feature_names = preprocessor.get_feature_names()
        
        # Initialize SHAP explainer
        try:
            # Try TreeExplainer first (for tree-based models)
            self.explainer = shap.TreeExplainer(model)
        except:
            try:
                # Fallback to KernelExplainer
                # Use a small sample of background data
                background_data = np.random.randn(10, len(self.feature_names))
                self.explainer = shap.KernelExplainer(model.predict_proba, background_data)
            except Exception as e:
                print(f"Could not initialize SHAP explainer: {e}")
    
    def explain_prediction(self, data_dict: Dict) -> Dict[str, float]:
        """Generate SHAP values for a single prediction"""
        if self.explainer is None:
            # Return dummy values if SHAP fails
            return {feature: 0.0 for feature in self.feature_names[:5]}
        
        try:
            # Preprocess the input
            X_processed = self.preprocessor.transform(data_dict)
            
            print(f"🔍 SHAP Input shape: {X_processed.shape}")
            print(f"🔍 SHAP Feature names: {len(self.feature_names)}")
            
            # Generate SHAP values
            shap_values = self.explainer.shap_values(X_processed)
            
            # Handle different SHAP value formats
            if isinstance(shap_values, list):
                # For binary classification, take the positive class values
                if len(shap_values) == 2:
                    shap_values = shap_values[1]
                else:
                    shap_values = shap_values[0]
            
            # Ensure we have the right shape
            if len(shap_values.shape) > 1:
                shap_values = shap_values[0]
            
            print(f"🔍 SHAP values shape: {shap_values.shape}")
            
            # Create feature importance dictionary
            feature_importance = {}
            for i, feature_name in enumerate(self.feature_names):
                if i < len(shap_values):
                    feature_importance[feature_name] = float(shap_values[i])
            
            print(f"🔍 SHAP features returned: {len(feature_importance)}")
            print(f"🔍 Creatnine in SHAP: {'CreatnineBaseline' in feature_importance}")
            print(f"🔍 eGFR in SHAP: {'eGFRBaseline' in feature_importance}")
            
            return feature_importance
            
        except Exception as e:
            print(f"Error generating SHAP values: {e}")
            # Return dummy values if SHAP fails
            return {feature: 0.0 for feature in self.feature_names[:5]}
    
    def get_top_features(self, data_dict: Dict, top_k: int = 5) -> List[Tuple[str, float]]:
        """Get top k most important features"""
        feature_importance = self.explain_prediction(data_dict)
        
        # Sort by absolute importance
        sorted_features = sorted(
            feature_importance.items(), 
            key=lambda x: abs(x[1]), 
            reverse=True
        )
        
        return sorted_features[:top_k]
    
    def format_shap_for_frontend(self, data_dict: Dict, top_k: int = 5) -> Dict[str, float]:
        """Format SHAP values for frontend consumption"""
        top_features = self.get_top_features(data_dict, top_k)
        
        # Create dictionary with feature names as keys
        shap_dict = {}
        for feature_name, importance in top_features:
            # Format feature names for display
            display_name = feature_name.replace('_', ' ').title()
            shap_dict[display_name] = round(importance, 3)
        
        return shap_dict
