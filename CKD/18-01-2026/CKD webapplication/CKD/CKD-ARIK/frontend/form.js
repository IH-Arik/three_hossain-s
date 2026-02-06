// CKD Prediction Form JavaScript

class CKDPredictor {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.chart = null;
        this.initializeEventListeners();
    }

    resetForm() {
        this.form.reset();
        this.hideResults();
        this.hideError();
        
        // Reset SHAP button
        const shapBtn = document.getElementById('shapBtn');
        if (shapBtn) {
            shapBtn.disabled = true;
            shapBtn.innerHTML = '<i class="bi bi-brain me-2"></i> SHAP Analysis (Requires Prediction)';
        }
    }

    initializeEventListeners() {
        // Form submission
        document.getElementById('ckdForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmit();
        });

        // Input validation
        const inputs = document.querySelectorAll('input[type="number"], select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateInput(input));
            input.addEventListener('input', () => this.clearValidation(input));
        });
    }

    validateInput(input) {
        const value = parseFloat(input.value);
        const min = parseFloat(input.min);
        const max = parseFloat(input.max);
        
        if (isNaN(value) || value < min || value > max) {
            input.classList.add('is-invalid');
            this.showInvalidFeedback(input, `Value must be between ${min} and ${max}`);
            return false;
        }
        
        input.classList.remove('is-invalid');
        return true;
    }

    clearValidation(input) {
        input.classList.remove('is-invalid');
        const feedback = input.parentNode.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.remove();
        }
    }

    showInvalidFeedback(input, message) {
        this.clearValidation(input);
        
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = message;
        
        input.parentNode.appendChild(feedback);
    }

    async handleFormSubmit() {
        // Validate all inputs
        const inputs = document.querySelectorAll('input[required], select[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (input.type === 'number') {
                if (!this.validateInput(input)) {
                    isValid = false;
                }
            } else if (!input.value) {
                input.classList.add('is-invalid');
                isValid = false;
            }
        });

        if (!isValid) {
            this.showError('Please fill in all required fields with valid values.');
            return;
        }

        // Collect form data
        const formData = this.collectFormData();
        
        // Show loading state
        this.showLoading();
        
        try {
            // Make API call
            const response = await fetch(`${this.apiBaseUrl}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            // Update SHAP explanation if available
            if (window.shapExplanation && typeof window.updateSHAPExplanation === 'function') {
                const patientData = this.getFormData();
                window.updateSHAPExplanation(patientData, result);
                
                // Enable SHAP button
                const shapBtn = document.getElementById('shapBtn');
                if (shapBtn) {
                    shapBtn.disabled = false;
                    shapBtn.innerHTML = '<i class="bi bi-brain me-2"></i> SHAP Analysis';
                }
            }

            // Display results
            this.displayResults(result);
            
        } catch (error) {
            console.error('Prediction error:', error);
            this.showError('Failed to get prediction. Please check if the backend server is running and try again.');
        } finally {
            this.hideLoading();
        }
    }

    collectFormData() {
        const form = document.getElementById('ckdForm');
        const formData = new FormData(form);
        
        // Convert to numbers and create object
        const data = {
            age: parseFloat(formData.get('age')),
            gender: parseInt(formData.get('gender')),
            bp: parseFloat(formData.get('bp')),
            creatinine: parseFloat(formData.get('creatinine')),
            egfr: parseFloat(formData.get('egfr')),
            hba1c: parseFloat(formData.get('hba1c')),
            diabetes: parseInt(formData.get('diabetes')),
            hypertension: parseInt(formData.get('hypertension')),
            bmi: parseFloat(formData.get('bmi')),
            hemoglobin: parseFloat(formData.get('hemoglobin')),
            smoking: parseInt(formData.get('smoking')),
            family_history: parseInt(formData.get('family_history'))
        };
        
        return data;
    }

    showLoading() {
        document.getElementById('initialState').classList.add('d-none');
        document.getElementById('resultsCard').classList.add('d-none');
        document.getElementById('loadingState').classList.remove('d-none');
        
        // Disable submit button
        const submitBtn = document.getElementById('predictBtn');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';
    }

    hideLoading() {
        document.getElementById('loadingState').classList.add('d-none');
        
        // Enable submit button
        const submitBtn = document.getElementById('predictBtn');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-cpu me-2"></i>Predict CKD Risk';
    }

    displayResults(result) {
        // Hide initial state, show results
        document.getElementById('initialState').classList.add('d-none');
        document.getElementById('resultsCard').classList.remove('d-none');
        
        // Add fade-in animation
        document.getElementById('resultsCard').classList.add('fade-in');
        
        // Display prediction
        this.displayPrediction(result);
        
        // Display SHAP chart
        this.displaySHAPChart(result.shap);
    }

    displayPrediction(result) {
        const predictionBadge = document.getElementById('predictionBadge');
        const probabilityDisplay = document.getElementById('probabilityDisplay');
        const riskLevel = document.getElementById('riskLevel');
        
        // Set prediction badge
        if (result.ckd) {
            predictionBadge.className = 'badge bg-danger fs-6 p-3 mb-3';
            predictionBadge.textContent = result.prediction;
        } else {
            predictionBadge.className = 'badge bg-success fs-6 p-3 mb-3';
            predictionBadge.textContent = result.prediction;
        }
        
        // Set probability
        const probability = (result.probability * 100).toFixed(1);
        probabilityDisplay.textContent = `${probability}% Risk`;
        
        // Set risk level
        let riskText = '';
        let riskClass = '';
        
        if (result.probability < 0.3) {
            riskText = 'Low Risk';
            riskClass = 'risk-low';
        } else if (result.probability < 0.7) {
            riskText = 'Moderate Risk';
            riskClass = 'risk-medium';
        } else {
            riskText = 'High Risk';
            riskClass = 'risk-high';
        }
        
        riskLevel.textContent = riskText;
        riskLevel.className = riskClass;
        
        // Add success animation
        document.getElementById('resultsCard').classList.add('success-animation');
        setTimeout(() => {
            document.getElementById('resultsCard').classList.remove('success-animation');
        }, 500);
    }

    displaySHAPChart(shapData) {
        const ctx = document.getElementById('shapChart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.chart) {
            this.chart.destroy();
        }
        
        // Prepare data for chart
        const labels = Object.keys(shapData);
        const values = Object.values(shapData);
        
        // Create colors based on positive/negative values
        const colors = values.map(value => 
            value > 0 ? 'rgba(220, 53, 69, 0.8)' : 'rgba(25, 135, 84, 0.8)'
        );
        
        const borderColors = values.map(value => 
            value > 0 ? 'rgba(220, 53, 69, 1)' : 'rgba(25, 135, 84, 1)'
        );
        
        // Create new chart
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'SHAP Value',
                    data: values,
                    backgroundColor: colors,
                    borderColor: borderColors,
                    borderWidth: 2,
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.x;
                                const feature = context.label;
                                const direction = value > 0 ? 'increases' : 'decreases';
                                const magnitude = Math.abs(value).toFixed(3);
                                return `${feature}: ${direction} risk by ${magnitude}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'SHAP Value (Impact on CKD Risk)',
                            font: {
                                weight: 'bold'
                            }
                        },
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        zeroLineColor: 'rgba(0, 0, 0, 0.5)',
                        zeroLineWidth: 2
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Features',
                            font: {
                                weight: 'bold'
                            }
                        },
                        grid: {
                            display: false
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    showError(message) {
        // Create or update error alert
        let errorAlert = document.getElementById('errorAlert');
        
        if (!errorAlert) {
            errorAlert = document.createElement('div');
            errorAlert.id = 'errorAlert';
            errorAlert.className = 'alert alert-danger alert-dismissible fade show mt-3';
            errorAlert.role = 'alert';
            
            const form = document.getElementById('ckdForm');
            form.parentNode.insertBefore(errorAlert, form.nextSibling);
        }
        
        errorAlert.innerHTML = `
            <i class="bi bi-exclamation-triangle me-2"></i>
            <strong>Error:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (errorAlert) {
                errorAlert.remove();
            }
        }, 5000);
    }

    // Method to check API health
    async checkApiHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            if (response.ok) {
                const health = await response.json();
                console.log('API Health Status:', health);
                return true;
            }
            return false;
        } catch (error) {
            console.error('API Health Check Failed:', error);
            return false;
        }
    }
}

// Global function to open SHAP explanation
function openSHAPExplanation() {
    window.open('shap-explanation.html', '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const predictor = new CKDPredictor();
    
    // Check API health on page load
    predictor.checkApiHealth().then(isHealthy => {
        if (!isHealthy) {
            console.warn('Backend API is not running. Please start the backend server.');
        }
    });
    
    // Make predictor globally accessible for debugging
    window.ckdPredictor = predictor;
});

// Utility function to format numbers
function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

// Utility function to get risk level color
function getRiskLevelColor(probability) {
    if (probability < 0.3) return '#198754';  // Green
    if (probability < 0.7) return '#ffc107';  // Yellow
    return '#dc3545';  // Red
}
