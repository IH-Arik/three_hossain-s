import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

class CKDPreprocessor:
    def __init__(self):
        # Initialize preprocessing components (matching training time exactly)
        self.numerical_cols = ['AgeBaseline', 'CholesterolBaseline', 'TriglyceridesBaseline', 'HgbA1C', 'CreatnineBaseline', 'eGFRBaseline', 'sBPBaseline', 'dBPBaseline', 'BMIBaseline', 'TimeToEventMonths']
        self.binary_categorical_cols = ['Gender', 'HistoryDiabetes', 'HistoryCHD', 'HistoryVascular', 'HistorySmoking', 'HistoryHTN ', 'HistoryDLD', 'HistoryObesity', 'DLDmeds', 'DMmeds', 'HTNmeds', 'ACEIARB']
        self.non_binary_categorical_cols = ['Age.3.categories']
        
        self.standard_scale_cols = ['AgeBaseline', 'sBPBaseline', 'dBPBaseline', 'BMIBaseline']
        self.minmax_scale_cols = ['HgbA1C', 'eGFRBaseline']
        self.robust_scale_cols = ['CholesterolBaseline', 'TriglyceridesBaseline', 'CreatnineBaseline', 'TimeToEventMonths']
        
        # Feature order (MUST match training time - will be set after preprocessing)
        self.feature_order = None
        self.preprocessor = None
        self.is_fitted = False
        
        # Create the preprocessor (matching your training pipeline)
        self._create_preprocessor()
    
    def _create_preprocessor(self):
        """Create the exact preprocessor used in training"""
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num_standard', Pipeline([
                    ('imputer', SimpleImputer(strategy='mean')),
                    ('scaler', StandardScaler())
                ]), self.standard_scale_cols),
                ('num_minmax', Pipeline([
                    ('imputer', SimpleImputer(strategy='mean')),
                    ('scaler', MinMaxScaler())
                ]), self.minmax_scale_cols),
                ('num_robust', Pipeline([
                    ('imputer', SimpleImputer(strategy='mean')),
                    ('scaler', RobustScaler())
                ]), self.robust_scale_cols),
                ('cat_binary', Pipeline([
                    ('imputer', SimpleImputer(strategy='most_frequent'))
                ]), self.binary_categorical_cols),
                ('cat_non_binary', Pipeline([
                    ('imputer', SimpleImputer(strategy='most_frequent')),
                    ('encoder', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
                ]), self.non_binary_categorical_cols)
            ],
            remainder='passthrough'
        )
    
    def fit(self, X_train):
        """Fit preprocessors on training data"""
        # Fit the preprocessor
        self.preprocessor.fit(X_train)
        
        # Get feature names after preprocessing
        feature_names = self.preprocessor.get_feature_names_out()
        
        # Clean feature names (remove prefixes like 'num_standard__', etc.)
        cleaned_names = []
        for name in feature_names:
            if '__' in name:
                cleaned_name = name.split('__')[-1]
            else:
                cleaned_name = name
            cleaned_names.append(cleaned_name)
        
        self.feature_order = cleaned_names
        self.is_fitted = True
        
        print(f"Preprocessor fitted with {len(cleaned_names)} features")
        return cleaned_names
    
    def transform(self, data_dict):
        """Transform new data using fitted preprocessors"""
        # Convert to DataFrame
        df = pd.DataFrame([data_dict])
        
        # Ensure all required features exist
        all_features = self.numerical_cols + self.binary_categorical_cols + self.non_binary_categorical_cols
        for feature in all_features:
            if feature not in df.columns:
                df[feature] = 0  # Default value
        
        # Add a default value for Age.3.categories (one of the 3 categories)
        # We'll map age to categories based on typical age groups
        age = data_dict.get('age', 55)
        if age < 40:
            age_category = 'young'
        elif age < 65:
            age_category = 'middle'
        else:
            age_category = 'old'
        
        df['Age.3.categories'] = age_category
        
        # Reorder columns to match expected order
        df = df[all_features]
        
        if not self.is_fitted:
            # If not fitted, do basic transformation
            return df.values
        
        # Apply the fitted preprocessor
        X_processed = self.preprocessor.transform(df)
        return X_processed
    
    def get_feature_names(self):
        """Get feature names in correct order"""
        if self.feature_order is None:
            # Return approximate feature names if not fitted
            base_features = self.numerical_cols + self.binary_categorical_cols
            # Add one-hot encoded age categories (assuming 3 categories -> 2 features)
            age_categories = ['Age.3.categories_1', 'Age.3.categories_2']
            return base_features + age_categories
        return self.feature_order
    
    def get_feature_mapping(self):
        """Get mapping from web form fields to model features"""
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
