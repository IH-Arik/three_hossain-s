"""
Exact preprocessing pipeline extracted from EDCKD.py
This matches the training preprocessing used for the PLoS ONE dataset
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, OrdinalEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline as ImbPipeline
import joblib
import os

class EDCKDPreprocessor:
    """
    Exact preprocessing pipeline from EDCKD.py for PLoS ONE dataset
    """
    
    def __init__(self):
        # Dataset configuration from EDCKD.py
        self.dataset_config = {
            'id_column': 'StudyID',
            'numerical_cols': ['AgeBaseline', 'CholesterolBaseline', 'TriglyceridesBaseline', 'HgbA1C', 'CreatnineBaseline', 'eGFRBaseline', 'sBPBaseline', 'dBPBaseline', 'BMIBaseline', 'TimeToEventMonths'],
            'binary_categorical_cols': ['Gender', 'HistoryDiabetes', 'HistoryCHD', 'HistoryVascular', 'HistorySmoking', 'HistoryHTN ', 'HistoryDLD', 'HistoryObesity', 'DLDmeds', 'DMmeds', 'HTNmeds', 'ACEIARB'],
            'non_binary_categorical_cols': ['Age.3.categories'],
            'target_col': 'EventCKD35',
            'standard_scale_cols': ['AgeBaseline', 'sBPBaseline', 'dBPBaseline', 'BMIBaseline'],
            'minmax_scale_cols': ['HgbA1C', 'eGFRBaseline'],
            'robust_scale_cols': ['CholesterolBaseline', 'TriglyceridesBaseline', 'CreatnineBaseline', 'TimeToEventMonths']
        }
        
        self.preprocessor = None
        self.is_fitted = False
        self.feature_names = None
        
        # Create the exact preprocessor from EDCKD.py
        self._create_preprocessor()
    
    def _create_preprocessor(self):
        """Create the exact preprocessor used in EDCKD.py"""
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num_standard', ImbPipeline([
                    ('imputer', SimpleImputer(strategy='mean')),
                    ('scaler', StandardScaler())
                ]), self.dataset_config['standard_scale_cols']),
                ('num_minmax', ImbPipeline([
                    ('imputer', SimpleImputer(strategy='mean')),
                    ('scaler', MinMaxScaler())
                ]), self.dataset_config['minmax_scale_cols']),
                ('num_robust', ImbPipeline([
                    ('imputer', SimpleImputer(strategy='mean')),
                    ('scaler', RobustScaler())
                ]), self.dataset_config['robust_scale_cols']),
                ('cat_binary', ImbPipeline([
                    ('imputer', SimpleImputer(strategy='most_frequent')),
                    ('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1))
                ]), self.dataset_config['binary_categorical_cols']),
                ('cat_non_binary', ImbPipeline([
                    ('imputer', SimpleImputer(strategy='most_frequent')),
                    ('encoder', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
                ]), self.dataset_config['non_binary_categorical_cols'])
            ],
            remainder='passthrough'
        )
    
    def fit_from_dataset(self, dataset_path):
        """
        Fit the preprocessor using the original PLoS ONE dataset
        This ensures exact match with training preprocessing
        """
        try:
            # Load the original dataset
            df = pd.read_excel(dataset_path)
            print(f"✅ Loaded dataset: {df.shape}")
            
            # Apply exact preprocessing from EDCKD.py
            df = self._apply_edckd_cleaning(df)
            
            # Prepare features
            features = (self.dataset_config['numerical_cols'] + 
                       self.dataset_config['binary_categorical_cols'] + 
                       self.dataset_config['non_binary_categorical_cols'])
            
            X = df[features]
            
            # Fit the preprocessor
            self.preprocessor.fit(X)
            
            # Get feature names after preprocessing
            feature_names = self.preprocessor.get_feature_names_out()
            
            # Clean feature names (remove prefixes like 'num_standard__', etc.)
            self.feature_names = []
            for name in feature_names:
                if '__' in name:
                    cleaned_name = name.split('__')[-1]
                else:
                    cleaned_name = name
                self.feature_names.append(cleaned_name)
            
            self.is_fitted = True
            
            print(f"✅ Preprocessor fitted successfully!")
            print(f"📊 Features after preprocessing: {len(self.feature_names)}")
            print(f"🔍 Feature names: {self.feature_names}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error fitting preprocessor: {e}")
            return False
    
    def _apply_edckd_cleaning(self, df):
        """Apply the exact data cleaning from EDCKD.py"""
        # Drop ID column
        if self.dataset_config['id_column'] in df.columns:
            df = df.drop(self.dataset_config['id_column'], axis=1)
        
        # Handle target variable (if present)
        if self.dataset_config['target_col'] in df.columns:
            df[self.dataset_config['target_col']] = df[self.dataset_config['target_col']].astype(int)
        
        # Clean object columns (for kidney_disease dataset handling)
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.strip()
                df[col] = df[col].replace('?', np.nan)
        
        # Convert numerical columns that might be stored as strings
        for col in self.dataset_config['numerical_cols']:
            if col in df.columns and df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def transform_web_input(self, data_dict):
        """
        Transform web form input using the fitted preprocessor
        This handles the conversion from web form to model input format
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transforming data")
        
        # Convert web input to DataFrame
        df = pd.DataFrame([data_dict])
        
        # Apply the same cleaning as training
        df = self._apply_edckd_cleaning(df)
        
        # Ensure all required features exist
        all_features = (self.dataset_config['numerical_cols'] + 
                       self.dataset_config['binary_categorical_cols'] + 
                       self.dataset_config['non_binary_categorical_cols'])
        
        for feature in all_features:
            if feature not in df.columns:
                if feature in self.dataset_config['numerical_cols']:
                    df[feature] = 0.0  # Default numeric value
                elif feature == 'Age.3.categories':
                    # Derive age category from age
                    age = data_dict.get('age', 50)
                    if age < 40:
                        df[feature] = 'young'
                    elif age < 65:
                        df[feature] = 'middle'
                    else:
                        df[feature] = 'old'
                else:
                    df[feature] = 0  # Default binary value
        
        # Reorder columns to match expected order
        df = df[all_features]
        
        # Apply preprocessing
        X_processed = self.preprocessor.transform(df)
        
        return X_processed
    
    def get_feature_names(self):
        """Get the feature names after preprocessing"""
        if self.feature_names is None:
            # Return approximate names if not fitted
            base_features = (self.dataset_config['numerical_cols'] + 
                           self.dataset_config['binary_categorical_cols'])
            # Add one-hot encoded age categories
            age_categories = ['Age.3.categories_1', 'Age.3.categories_2']
            return base_features + age_categories
        return self.feature_names
    
    def save_preprocessor(self, path):
        """Save the fitted preprocessor"""
        if self.is_fitted:
            joblib.dump({
                'preprocessor': self.preprocessor,
                'feature_names': self.feature_names,
                'dataset_config': self.dataset_config,
                'is_fitted': self.is_fitted
            }, path)
            print(f"✅ Preprocessor saved to {path}")
        else:
            print("❌ Cannot save unfitted preprocessor")
    
    def load_preprocessor(self, path):
        """Load a fitted preprocessor"""
        if os.path.exists(path):
            data = joblib.load(path)
            self.preprocessor = data['preprocessor']
            self.feature_names = data['feature_names']
            self.dataset_config = data['dataset_config']
            self.is_fitted = data['is_fitted']
            print(f"✅ Preprocessor loaded from {path}")
            return True
        else:
            print(f"❌ Preprocessor file not found: {path}")
            return False
    
    def get_web_form_mapping(self):
        """Get mapping from web form fields to dataset features"""
        return {
            'age': 'AgeBaseline',
            'cholesterol': 'CholesterolBaseline', 
            'triglycerides': 'TriglyceridesBaseline',
            'hba1c': 'HgbA1C',
            'creatinine': 'CreatnineBaseline',
            'egfr': 'eGFRBaseline',
            'sbp': 'sBPBaseline',
            'dbp': 'dBPBaseline',
            'bmi': 'BMIBaseline',
            'time_to_event': 'TimeToEventMonths',
            'gender': 'Gender',
            'diabetes': 'HistoryDiabetes',
            'chd': 'HistoryCHD',
            'vascular': 'HistoryVascular',
            'smoking': 'HistorySmoking',
            'htn': 'HistoryHTN ',
            'dld': 'HistoryDLD',
            'obesity': 'HistoryObesity',
            'dld_meds': 'DLDmeds',
            'dm_meds': 'DMmeds',
            'htn_meds': 'HTNmeds',
            'acei_arb': 'ACEIARB'
        }

# Convenience function to create and fit the preprocessor
def create_edckd_preprocessor(dataset_path=None):
    """
    Create and fit the EDCKD preprocessor
    
    Args:
        dataset_path: Path to the PLoS ONE dataset. If None, will try to find it.
    
    Returns:
        Fitted EDCKDPreprocessor instance
    """
    preprocessor = EDCKDPreprocessor()
    
    # Try to find the dataset if not provided
    if dataset_path is None:
        possible_paths = [
            '../pone.0199920.s002.xlsx',
            '../../pone.0199920.s002.xlsx',
            'pone.0199920.s002.xlsx'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                dataset_path = path
                break
    
    if dataset_path and os.path.exists(dataset_path):
        if preprocessor.fit_from_dataset(dataset_path):
            return preprocessor
    else:
        print("⚠️  Dataset not found. Preprocessor created but not fitted.")
        return preprocessor
