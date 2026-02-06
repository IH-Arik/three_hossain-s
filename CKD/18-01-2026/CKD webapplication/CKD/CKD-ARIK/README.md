# CKD Risk Prediction System

A comprehensive web application for predicting Chronic Kidney Disease (CKD) risk using machine learning models with SHAP explainability.

## 🎯 Project Overview

This system provides:
- **CKD Risk Prediction**: Binary classification (CKD Detected/No CKD Detected)
- **Probability Scoring**: Risk probability percentage (e.g., 87%)
- **SHAP Explanations**: Dynamic feature importance visualization
- **Ensemble Modeling**: Support for both traditional ML (PKL) and deep learning (H5) models

## 🏗️ Architecture

```
ckd-web-app/
│
├── backend/
│   ├── app.py                  # FastAPI main application
│   ├── utils/
│   │   ├── preprocess.py       # Data preprocessing pipeline
│   │   └── shap_utils.py       # SHAP explanation utilities
│   ├── models/                 # Model storage directory
│   │   ├── ckd_model.pkl       # Scikit-learn model (place your model here)
│   │   └── ckd_model.h5        # Keras model (optional, for ensemble)
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── index.html             # Main web page
│   ├── form.js                # JavaScript for API calls & visualization
│   └── style.css              # Custom styling
│
└── README.md                  # This file
```

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Place your trained models:**
   - Put your trained scikit-learn model as `models/ckd_model.pkl`
   - Optionally, place your Keras model as `models/ckd_model.h5`

4. **Start the FastAPI server:**
   ```bash
   python app.py
   ```
   
   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Open the frontend:**
   - Simply open `frontend/index.html` in your web browser
   - Or serve it with a web server for better CORS handling

2. **Access the application:**
   - Navigate to `http://localhost:8000` (if serving from backend)
   - Or open `index.html` directly

## 📊 Features & Functionality

### Input Attributes
The system collects the following patient attributes:

| Attribute | Type | Range | Description |
|-----------|------|-------|-------------|
| Age | Numeric | 0-120 | Patient age in years |
| Gender | Binary | 0/1 | 0: Female, 1: Male |
| Blood Pressure | Numeric | 60-200 | Systolic BP in mmHg |
| Creatinine | Numeric | 0.1-10 | Serum creatinine in mg/dL |
| eGFR | Numeric | 0-200 | Estimated glomerular filtration rate |
| HbA1c | Numeric | 3-15 | Glycated hemoglobin percentage |
| Diabetes | Binary | 0/1 | 0: No, 1: Yes |
| Hypertension | Binary | 0/1 | 0: No, 1: Yes |
| BMI | Numeric | 10-50 | Body mass index |
| Hemoglobin | Numeric | 5-20 | Hemoglobin in g/dL |
| Smoking | Binary | 0/1 | 0: No, 1: Yes |
| Family History | Binary | 0/1 | 0: No, 1: Yes |

### Prediction Output
- **CKD Status**: "CKD Detected" or "No CKD Detected"
- **Probability**: Risk percentage (0-100%)
- **Risk Level**: Low/Medium/High classification
- **SHAP Explanation**: Top 5 most influential features with visual chart

### API Endpoints

#### `POST /predict`
**Request Body:**
```json
{
  "age": 55,
  "gender": 1,
  "bp": 140,
  "creatinine": 2.1,
  "egfr": 32,
  "hba1c": 7.5,
  "diabetes": 1,
  "hypertension": 1,
  "bmi": 28.5,
  "hemoglobin": 11.2,
  "smoking": 0,
  "family_history": 1
}
```

**Response:**
```json
{
  "ckd": true,
  "probability": 0.87,
  "prediction": "CKD Detected",
  "shap": {
    "Creatinine": 0.42,
    "Egfr": -0.31,
    "Age": 0.18,
    "Diabetes": 0.15,
    "Bmi": 0.08
  }
}
```

#### `GET /health`
Check API and model status.

#### `GET /features`
Get feature descriptions and validation rules.

## 🔧 Technical Implementation

### Backend (FastAPI)
- **Framework**: FastAPI with automatic API documentation
- **Model Loading**: Joblib for PKL, TensorFlow/Keras for H5
- **Preprocessing**: Scikit-learn pipelines with imputation and scaling
- **SHAP**: TreeExplainer for tree models, KernelExplainer fallback
- **CORS**: Enabled for frontend integration

### Frontend (HTML/CSS/JavaScript)
- **UI Framework**: Bootstrap 5 with custom styling
- **Visualization**: Chart.js for SHAP bar charts
- **Validation**: Client-side input validation
- **Responsive**: Mobile-friendly design
- **Animations**: Smooth transitions and loading states

### Data Processing
- **Feature Order**: Strictly maintained to match training time
- **Preprocessing**: Median imputation + standard scaling for numeric features
- **Ensemble**: Averages predictions from ML and DL models (if both available)
- **SHAP**: Explains individual predictions with feature contributions

## 🏥 Medical Disclaimer

> ⚠️ **Important**: This tool is for research and educational purposes only. It is not a substitute for professional medical diagnosis, advice, or treatment. Always consult with qualified healthcare providers for medical concerns and decisions.

## 📋 Model Requirements

### Feature Order (CRITICAL)
The preprocessing pipeline expects features in this exact order:
1. age
2. gender
3. bp
4. creatinine
5. egfr
6. hba1c
7. diabetes
8. hypertension
9. bmi
10. hemoglobin
11. smoking
12. family_history

### Model Training
When training your models, ensure:
- Same feature order as listed above
- Similar preprocessing (median imputation, standard scaling)
- Binary classification target (0: No CKD, 1: CKD)
- Save preprocessing pipeline if possible for exact reproduction

## 🐳 Docker Deployment (Optional)

Create a `Dockerfile` in the backend directory:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ckd-api .
docker run -p 8000:8000 ckd-api
```

## 🌐 Deployment Options

- **Railway**: Easy deployment with GitHub integration
- **Render**: Free tier available for web services
- **VPS**: Full control with Docker or direct deployment
- **Heroku**: Requires buildpack configuration for TensorFlow

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is for educational and research purposes. Please ensure compliance with medical device regulations if used in clinical settings.

## 🆘 Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend allows frontend origin
2. **Model Loading**: Check file paths and model compatibility
3. **SHAP Errors**: Fallback to dummy values if SHAP fails
4. **Input Validation**: Ensure all fields are filled with valid ranges

### Debug Mode

Enable console logging in browser for detailed error information.

## 📞 Support

For technical issues:
- Check browser console for JavaScript errors
- Verify backend server is running on port 8000
- Ensure model files are correctly placed in `models/` directory

---

**© 2026 CKD Risk Prediction System | Powered by AI & Machine Learning**
