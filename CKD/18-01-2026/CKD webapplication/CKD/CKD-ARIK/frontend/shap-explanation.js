/**
 * SHAP Explanation Module for CKD Prediction System
 * Publication-grade UI for individual patient risk factor analysis
 */

class SHAPExplanation {
    constructor() {
        this.currentData = null;
        this.chart = null;
        this.isInitialized = false;
    }

    /**
     * Initialize SHAP explanation with patient data and prediction results
     */
    initialize(patientData, predictionResult) {
        this.currentData = {
            patientId: patientData.patientId || `PAT-${Date.now()}`,
            age: patientData.age,
            egfr: patientData.egfr,
            creatinine: patientData.creatinine,
            hba1c: patientData.hba1c,
            riskProbability: predictionResult.probability,
            riskLevel: this.getRiskLevel(predictionResult.probability),
            shapValues: predictionResult.shap || {},
            patientData: this.formatPatientData(patientData),
            timestamp: new Date().toISOString()
        };

        this.updateUI();
        this.isInitialized = true;
    }

    /**
     * Get risk level based on probability
     */
    getRiskLevel(probability) {
        if (probability >= 0.7) return 'high';
        if (probability >= 0.3) return 'medium';
        return 'low';
    }

    /**
     * Format patient data for display
     */
    formatPatientData(patientData) {
        return {
            "Creatinine": patientData.creatinine,
            "eGFR": patientData.egfr,
            "Age": patientData.age,
            "HbA1c": patientData.hba1c,
            "Hypertension": patientData.htn,
            "Diabetes": patientData.diabetes,
            "BMI": patientData.bmi,
            "Cholesterol": patientData.cholesterol,
            "Triglycerides": patientData.triglycerides,
            "Smoking": patientData.smoking,
            "Gender": patientData.gender,
            "SBP": patientData.sbp,
            "DBP": patientData.dbp,
            "CHD": patientData.chd,
            "Vascular": patientData.vascular,
            "DLD": patientData.dld,
            "Obesity": patientData.obesity,
            "DLD_Meds": patientData.dld_meds,
            "DM_Meds": patientData.dm_meds,
            "HTN_Meds": patientData.htn_meds,
            "ACEI_ARB": patientData.acei_arb,
            "Time_to_Event": patientData.time_to_event
        };
    }

    /**
     * Update the UI with current data
     */
    updateUI() {
        if (!this.currentData) return;

        this.updatePatientInfo();
        this.updateRiskAssessment();
        this.updateShapFeatures();
        this.createShapChart();
        this.generateClinicalInsights();
    }

    /**
     * Update patient information display
     */
    updatePatientInfo() {
        const elements = {
            'patientId': this.currentData.patientId,
            'patientAge': this.currentData.age,
            'patientEgfr': this.currentData.egfr,
            'patientCreatinine': this.currentData.creatinine,
            'patientHba1c': this.currentData.hba1c
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    /**
     * Update risk assessment display
     */
    updateRiskAssessment() {
        const riskBadge = document.getElementById('riskBadge');
        const riskProbability = document.getElementById('riskProbability');

        if (riskBadge) {
            riskBadge.className = `risk-badge risk-${this.currentData.riskLevel}`;
            
            const riskIcons = {
                high: '<i class="fas fa-exclamation-triangle"></i> High Risk',
                medium: '<i class="fas fa-exclamation-circle"></i> Medium Risk',
                low: '<i class="fas fa-shield-alt"></i> Low Risk'
            };
            
            riskBadge.innerHTML = riskIcons[this.currentData.riskLevel];
        }

        if (riskProbability) {
            riskProbability.textContent = `${(this.currentData.riskProbability * 100).toFixed(1)}%`;
        }
    }

    /**
     * Update SHAP features display
     */
    updateShapFeatures() {
        const container = document.getElementById('shapFeatures');
        if (!container) return;

        container.innerHTML = '';

        // Sort features by absolute SHAP value and get top 8
        const sortedFeatures = Object.entries(this.currentData.shapValues)
            .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
            .slice(0, 8);

        sortedFeatures.forEach(([feature, shapValue], index) => {
            const featureDiv = this.createFeatureElement(feature, shapValue, index);
            container.appendChild(featureDiv);
        });
    }

    /**
     * Create individual feature element
     */
    createFeatureElement(feature, shapValue, index) {
        const featureDiv = document.createElement('div');
        featureDiv.className = 'feature-item';

        const isPositive = shapValue > 0;
        const impactClass = isPositive ? 'impact-positive' : 'impact-negative';
        const impactIcon = isPositive ? 'fa-arrow-up' : 'fa-arrow-down';
        const impactText = isPositive ? 'Increases Risk' : 'Decreases Risk';

        const patientValue = this.currentData.patientData[feature] || 'N/A';
        const formattedValue = this.formatValue(patientValue);

        const featureIcons = ['heartbeat', 'kidney', 'user', 'chart-line', 'pills', 'weight'];
        const icon = featureIcons[index % featureIcons.length];

        featureDiv.innerHTML = `
            <div class="feature-name">
                <i class="fas fa-${icon}"></i>
                ${this.formatFeatureName(feature)}
            </div>
            <div class="feature-value">Patient Value: ${formattedValue}</div>
            <div class="feature-impact">
                <span class="impact-value ${isPositive ? 'text-danger' : 'text-primary'}">
                    <i class="fas ${impactIcon}"></i> ${impactText}
                </span>
                <div class="impact-bar">
                    <div class="impact-fill ${impactClass}" style="width: ${Math.abs(shapValue) * 100}%"></div>
                </div>
                <span class="impact-value">${shapValue.toFixed(3)}</span>
            </div>
        `;

        return featureDiv;
    }

    /**
     * Format feature name for display
     */
    formatFeatureName(feature) {
        const nameMap = {
            'CreatnineBaseline': 'Creatinine',
            'eGFRBaseline': 'eGFR',
            'AgeBaseline': 'Age',
            'HgbA1C': 'HbA1c',
            'HistoryHTN': 'Hypertension',
            'HistoryDiabetes': 'Diabetes',
            'BMIBaseline': 'BMI',
            'CholesterolBaseline': 'Cholesterol',
            'TriglyceridesBaseline': 'Triglycerides',
            'HistorySmoking': 'Smoking',
            'Gender': 'Gender',
            'sBPBaseline': 'Systolic BP',
            'dBPBaseline': 'Diastolic BP',
            'HistoryCHD': 'Coronary Disease',
            'HistoryVascular': 'Vascular Disease',
            'HistoryDLD': 'Lipid Disorder',
            'HistoryObesity': 'Obesity',
            'DLDmeds': 'Lipid Meds',
            'DMmeds': 'Diabetes Meds',
            'HTNmeds': 'Hypertension Meds',
            'ACEIARB': 'ACEI/ARB',
            'TimeToEventMonths': 'Time to Event'
        };

        return nameMap[feature] || feature;
    }

    /**
     * Format value for display
     */
    formatValue(value) {
        if (typeof value === 'number') {
            if (Number.isInteger(value)) {
                return value.toString();
            }
            return value.toFixed(1);
        }
        if (typeof value === 'boolean') {
            return value ? 'Yes' : 'No';
        }
        return value || 'N/A';
    }

    /**
     * Create SHAP chart
     */
    createShapChart() {
        const canvas = document.getElementById('shapChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        // Destroy existing chart if it exists
        if (this.chart) {
            this.chart.destroy();
        }

        // Sort features by SHAP value
        const sortedFeatures = Object.entries(this.currentData.shapValues)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);

        const labels = sortedFeatures.map(([feature]) => this.formatFeatureName(feature));
        const values = sortedFeatures.map(([, value]) => value);
        const colors = values.map(value => 
            value > 0 ? 'rgba(255, 107, 107, 0.8)' : 'rgba(72, 219, 251, 0.8)'
        );

        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'SHAP Value',
                    data: values,
                    backgroundColor: colors,
                    borderColor: colors.map(color => color.replace('0.8', '1')),
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed.y;
                                const direction = value > 0 ? 'Increases' : 'Decreases';
                                return `${direction} CKD risk: ${Math.abs(value).toFixed(3)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'SHAP Value (Risk Impact)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Clinical Features'
                        }
                    }
                }
            }
        });
    }

    /**
     * Generate clinical insights
     */
    generateClinicalInsights() {
        const container = document.getElementById('clinicalInsights');
        if (!container) return;

        container.innerHTML = '';

        const insights = this.generateInsights();
        
        insights.forEach(insight => {
            const insightDiv = document.createElement('div');
            insightDiv.className = 'insight-item';
            insightDiv.innerHTML = `<i class="fas fa-info-circle"></i> ${insight}`;
            container.appendChild(insightDiv);
        });
    }

    /**
     * Generate insights based on top features
     */
    generateInsights() {
        const insights = [];
        const topFeatures = Object.entries(this.currentData.shapValues)
            .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
            .slice(0, 3);

        const insightGenerators = {
            'CreatnineBaseline': (value, patientValue) => {
                if (value > 0) {
                    return `Elevated creatinine (${patientValue} mg/dL) is the strongest risk factor. Consider renal function monitoring and potential nephrology referral.`;
                }
                return `Normal creatinine level (${patientValue} mg/dL) suggests preserved renal function.`;
            },
            'eGFRBaseline': (value, patientValue) => {
                if (value < 0) {
                    return `Reduced eGFR (${patientValue} mL/min/1.73m²) indicates decreased kidney function. Regular monitoring of renal function is recommended.`;
                }
                return `Normal eGFR (${patientValue} mL/min/1.73m²) suggests adequate kidney function.`;
            },
            'AgeBaseline': (value, patientValue) => {
                if (value > 0) {
                    return `Advanced age (${patientValue} years) contributes to CKD risk. Age-related kidney function decline should be considered in management.`;
                }
                return `Age (${patientValue} years) is not a significant risk factor.`;
            },
            'HgbA1C': (value, patientValue) => {
                if (value > 0) {
                    return `Poor glycemic control (HbA1c ${patientValue}%) increases CKD risk. Intensive diabetes management may slow progression.`;
                }
                return `Good glycemic control (HbA1c ${patientValue}%) helps reduce CKD risk.`;
            },
            'HistoryHTN': (value, patientValue) => {
                if (value > 0 && patientValue) {
                    return `Hypertension is a significant risk factor. Strict blood pressure control (<130/80 mmHg) is recommended for renal protection.`;
                }
                return `Blood pressure status is favorable for kidney health.`;
            },
            'HistoryDiabetes': (value, patientValue) => {
                if (value > 0 && patientValue) {
                    return `Diabetes mellitus is a major contributor to CKD risk. Comprehensive diabetes management is essential.`;
                }
                return `Diabetes status is not contributing significantly to CKD risk.`;
            }
        };

        topFeatures.forEach(([feature, shapValue]) => {
            const generator = insightGenerators[feature];
            if (generator) {
                const patientValue = this.currentData.patientData[feature];
                const insight = generator(shapValue, patientValue);
                if (insight) insights.push(insight);
            }
        });

        // Add general recommendation
        const riskPercent = (this.currentData.riskProbability * 100).toFixed(1);
        const recommendations = {
            high: 'Immediate medical evaluation and intervention recommended. Consider nephrology referral.',
            medium: 'Regular monitoring and risk factor modification advised. Follow-up in 3-6 months recommended.',
            low: 'Continue routine medical care with periodic kidney function assessment.'
        };

        insights.push(`Overall CKD risk is ${riskPercent}%. ${recommendations[this.currentData.riskLevel]}`);

        return insights;
    }

    /**
     * Export data as JSON
     */
    exportData() {
        const exportData = {
            patient: this.currentData,
            model: 'CKD Prediction Ensemble',
            methodology: 'SHAP (SHapley Additive exPlanations)',
            timestamp: new Date().toISOString(),
            version: '1.0.0'
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.download = `shap-analysis-${this.currentData.patientId}.json`;
        link.href = url;
        link.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Export chart as image
     */
    exportChart() {
        const canvas = document.getElementById('shapChart');
        if (!canvas) return;

        const url = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.download = `shap-chart-${this.currentData.patientId}.png`;
        link.href = url;
        link.click();
    }

    /**
     * Generate publication-ready summary
     */
    generatePublicationSummary() {
        if (!this.currentData) return '';

        const topFeatures = Object.entries(this.currentData.shapValues)
            .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
            .slice(0, 5);

        const summary = `
Patient ${this.currentData.patientId} Analysis Summary
===============================================
Risk Assessment: ${(this.currentData.riskProbability * 100).toFixed(1)}% (${this.currentData.riskLevel} risk)
Key Risk Factors:
${topFeatures.map(([feature, value], index) => 
    `${index + 1}. ${this.formatFeatureName(feature)}: ${value > 0 ? '+' : ''}${value.toFixed(3)}`
).join('\n')}

Clinical Interpretation:
${this.generateInsights().join('\n')}

Methodology: SHAP (SHapley Additive exPlanations) applied to ensemble CKD prediction model
Model: Random Forest + Deep Learning ensemble trained on PLoS ONE dataset (n=491)
Date: ${new Date().toLocaleDateString()}
        `.trim();

        return summary;
    }

    /**
     * Print publication-ready summary
     */
    printSummary() {
        const summary = this.generatePublicationSummary();
        console.log(summary);
        return summary;
    }
}

// Global instance
window.shapExplanation = new SHAPExplanation();

// Integration with main form
window.updateSHAPExplanation = function(patientData, predictionResult) {
    window.shapExplanation.initialize(patientData, predictionResult);
};

// Export functions for global access
window.exportSHAPData = function() {
    window.shapExplanation.exportData();
};

window.exportSHAPChart = function() {
    window.shapExplanation.exportChart();
};

window.printSHAPSummary = function() {
    return window.shapExplanation.printSummary();
};
