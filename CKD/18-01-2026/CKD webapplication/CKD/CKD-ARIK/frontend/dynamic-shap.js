/**
 * Dynamic SHAP Explanation System
 * Real-time CKD risk analysis with interactive controls
 */

class DynamicSHAPSystem {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.currentData = this.getDefaultPatientData();
        this.chart = null;
        this.updateInterval = null;
        this.isUpdating = false;
        this.realtimeMode = false;
        this.predictionHistory = [];
        this.maxHistoryLength = 50;
        
        this.initialize();
    }
    
    initialize() {
        this.bindEvents();
        this.initializeChart();
        this.startRealTimeMonitoring();
        this.loadInitialData();
        this.checkForExcelData();
    }
    
    getDefaultPatientData() {
        return {
            age: 53,
            cholesterol: 193,  // 5.0 mmol/L * 38.67
            triglycerides: 98,  // 1.1 mmol/L * 88.54
            hba1c: 6.1,
            creatinine: 0.77,  // 68 μmol/L / 88.4
            egfr: 98,
            sbp: 131,
            dbp: 77,
            bmi: 30,
            time_to_event: 24,
            gender: 1,
            diabetes: 0,
            chd: 0,
            vascular: 0,
            smoking: 0,
            htn: 1,
            dld: 1,
            obesity: 1,
            dld_meds: 0,
            dm_meds: 0,
            htn_meds: 1,
            acei_arb: 0
        };
    }
    
    bindEvents() {
        // Slider events with real-time updates
        this.bindSliderEvent('ageSlider', 'age', 'ageValue', (value) => parseInt(value));
        this.bindSliderEvent('creatinineSlider', 'creatinine', 'creatinineValue', (value) => parseFloat(value));
        this.bindSliderEvent('egfrSlider', 'egfr', 'egfrValue', (value) => parseInt(value));
        this.bindSliderEvent('hba1cSlider', 'hba1c', 'hba1cValue', (value) => parseFloat(value));
        this.bindSliderEvent('sbpSlider', 'sbp', 'sbpValue', (value) => parseInt(value));
        this.bindSliderEvent('dbpSlider', 'dbp', 'dbpValue', (value) => parseInt(value));
        this.bindSliderEvent('bmiSlider', 'bmi', 'bmiValue', (value) => parseFloat(value));
        this.bindSliderEvent('cholesterolSlider', 'cholesterol', 'cholesterolValue', (value) => parseInt(value));
        this.bindSliderEvent('triglyceridesSlider', 'triglycerides', 'triglyceridesValue', (value) => parseInt(value));
        
        // Toggle events
        this.bindToggleEvent('diabetesToggle', 'diabetes');
        this.bindToggleEvent('htnToggle', 'htn');
        this.bindToggleEvent('smokingToggle', 'smoking');
        this.bindToggleEvent('chdToggle', 'chd');
        this.bindToggleEvent('vascularToggle', 'vascular');
        this.bindToggleEvent('dldToggle', 'dld');
        this.bindToggleEvent('obesityToggle', 'obesity');
        
        // Control buttons
        document.getElementById('updateBtn')?.addEventListener('click', () => this.updatePrediction());
        document.getElementById('randomizeBtn')?.addEventListener('click', () => this.randomizePatient());
        document.getElementById('realtimeToggle')?.addEventListener('change', (e) => this.toggleRealTime(e.target.checked));
        document.getElementById('exportBtn')?.addEventListener('click', () => this.exportAnalysis());
        
        // Scenario buttons
        document.querySelectorAll('.scenario-btn').forEach(btn => {
            btn.addEventListener('click', () => this.loadScenario(btn.dataset.scenario));
        });
    }
    
    bindSliderEvent(sliderId, dataKey, valueId, converter) {
        const slider = document.getElementById(sliderId);
        const valueDisplay = document.getElementById(valueId);
        
        if (slider && valueDisplay) {
            slider.addEventListener('input', (e) => {
                const value = converter(e.target.value);
                valueDisplay.textContent = converter === parseFloat ? value.toFixed(1) : value;
                this.currentData[dataKey] = value;
                
                // Real-time update if enabled
                if (this.realtimeMode) {
                    this.debounceUpdate();
                }
            });
        }
    }
    
    bindToggleEvent(toggleId, dataKey) {
        const toggle = document.getElementById(toggleId);
        if (toggle) {
            toggle.addEventListener('change', (e) => {
                this.currentData[dataKey] = e.target.checked ? 1 : 0;
                
                // Real-time update if enabled
                if (this.realtimeMode) {
                    this.debounceUpdate();
                }
            });
        }
    }
    
    initializeChart() {
        const ctx = document.getElementById('dynamicShapChart');
        if (!ctx) return;
        
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'SHAP Value',
                    data: [],
                    backgroundColor: [],
                    borderColor: [],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                },
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
                        },
                        grid: {
                            color: 'rgba(255,255,255,0.1)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Clinical Features'
                        },
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
    
    startRealTimeMonitoring() {
        // Monitor for real-time updates every 3 seconds
        this.updateInterval = setInterval(() => {
            if (this.realtimeMode && !this.isUpdating) {
                this.simulateRealTimeVariation();
            }
        }, 3000);
    }
    
    simulateRealTimeVariation() {
        // Add small physiological variations
        const variations = {
            creatinine: (Math.random() - 0.5) * 0.1,
            egfr: (Math.random() - 0.5) * 2,
            hba1c: (Math.random() - 0.5) * 0.2,
            sbp: (Math.random() - 0.5) * 5,
            dbp: (Math.random() - 0.5) * 3,
            cholesterol: (Math.random() - 0.5) * 10,
            triglycerides: (Math.random() - 0.5) * 15
        };
        
        let hasChanges = false;
        Object.entries(variations).forEach(([key, variation]) => {
            const oldValue = this.currentData[key];
            const newValue = Math.max(0, oldValue + variation);
            
            if (Math.abs(newValue - oldValue) > 0.01) {
                this.currentData[key] = newValue;
                this.updateControlDisplay(key, newValue);
                hasChanges = true;
            }
        });
        
        if (hasChanges) {
            this.debounceUpdate();
            this.addInsight('Physiological variation detected', 'info');
        }
    }
    
    updateControlDisplay(key, value) {
        const displayMap = {
            creatinine: 'creatinineValue',
            egfr: 'egfrValue',
            hba1c: 'hba1cValue',
            sbp: 'sbpValue',
            dbp: 'dbpValue',
            cholesterol: 'cholesterolValue',
            triglycerides: 'triglyceridesValue'
        };
        
        const displayId = displayMap[key];
        if (displayId) {
            const element = document.getElementById(displayId);
            if (element) {
                element.textContent = typeof value === 'number' && value % 1 !== 0 ? value.toFixed(1) : value;
            }
        }
    }
    
    debounceUpdate() {
        clearTimeout(this.updateTimeout);
        this.updateTimeout = setTimeout(() => {
            this.updatePrediction();
        }, 500);
    }
    
    async updatePrediction() {
        if (this.isUpdating) return;
        
        this.isUpdating = true;
        this.showLoading(true);
        
        try {
            // Call API for prediction
            const result = await this.callAPI();
            
            // Update displays
            this.updateRiskDisplay(result);
            this.updateSHAPFeatures(result);
            this.updateChart(result);
            this.updateClinicalInsights(result);
            
            // Add to history
            this.addToHistory(result);
            
            this.addInsight('Analysis updated successfully', 'success');
            
        } catch (error) {
            console.error('Update failed:', error);
            this.addInsight('Error: Unable to update analysis', 'error');
        } finally {
            this.isUpdating = false;
            this.showLoading(false);
        }
    }
    
    async callAPI() {
        // Convert units before sending to API
        const apiData = {...this.currentData};
        
        // Convert mg/dL to dataset units
        apiData.creatinine = apiData.creatinine * 88.4;  // mg/dL to μmol/L
        apiData.cholesterol = apiData.cholesterol / 38.67;  // mg/dL to mmol/L
        apiData.triglycerides = apiData.triglycerides / 88.54;  // mg/dL to mmol/L
        
        const response = await fetch(`${this.apiBaseUrl}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(apiData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    updateRiskDisplay(result) {
        const percentage = Math.round(result.probability * 100);
        const pointerPosition = result.probability * 100;
        
        // Update risk meter
        const pointer = document.getElementById('riskPointer');
        if (pointer) {
            pointer.style.left = pointerPosition + '%';
        }
        
        // Update percentage
        const percentageDisplay = document.getElementById('riskPercentage');
        if (percentageDisplay) {
            percentageDisplay.textContent = percentage + '%';
        }
        
        // Update risk level
        let riskLevel = 'Low Risk';
        let riskClass = 'text-success';
        
        if (result.probability >= 0.7) {
            riskLevel = 'High Risk';
            riskClass = 'text-danger';
        } else if (result.probability >= 0.3) {
            riskLevel = 'Medium Risk';
            riskClass = 'text-warning';
        }
        
        const riskLevelDisplay = document.getElementById('riskLevel');
        if (riskLevelDisplay) {
            riskLevelDisplay.textContent = riskLevel;
            riskLevelDisplay.className = riskClass;
        }
        
        // Animate the change
        this.animateValue('riskPercentage', this.lastPercentage || 0, percentage, 1000);
        this.lastPercentage = percentage;
    }
    
    updateSHAPFeatures(result) {
        const container = document.getElementById('shapFeatures');
        if (!container || !result.shap) return;
        
        container.innerHTML = '';
        
        // Update feature count
        const featureCount = document.getElementById('featureCount');
        if (featureCount) {
            featureCount.textContent = `${Object.keys(result.shap).length} features`;
        }
        
        // Sort features by absolute SHAP value
        const sortedFeatures = Object.entries(result.shap)
            .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));
        
        sortedFeatures.forEach(([feature, shapValue], index) => {
            const featureCard = this.createFeatureCard(feature, shapValue, index);
            container.appendChild(featureCard);
        });
    }
    
    createFeatureCard(feature, shapValue, index) {
        const card = document.createElement('div');
        card.className = 'feature-card animate__animated animate__fadeInUp';
        card.style.animationDelay = (index * 0.1) + 's';
        
        const isPositive = shapValue > 0;
        const patientValue = this.getPatientValue(feature);
        const formattedFeature = this.formatFeatureName(feature);
        
        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div>
                    <h6 class="mb-1">${formattedFeature}</h6>
                    <small class="text-muted">Value: ${patientValue}</small>
                </div>
                <div class="text-end">
                    <div class="fw-bold text-${isPositive ? 'danger' : 'info'}">
                        ${isPositive ? '↑' : '↓'} ${Math.abs(shapValue).toFixed(3)}
                    </div>
                    <small class="text-muted">${isPositive ? 'Risk' : 'Protective'}</small>
                </div>
            </div>
            <div class="progress" style="height: 8px;">
                <div class="progress-bar ${isPositive ? 'bg-danger' : 'bg-info'}" 
                     style="width: ${Math.abs(shapValue) * 100}%"></div>
            </div>
        `;
        
        // Add click interaction
        card.addEventListener('click', () => this.showFeatureDetails(feature, shapValue, patientValue));
        
        return card;
    }
    
    updateChart(result) {
        if (!this.chart || !result.shap) return;
        
        const labels = Object.keys(result.shap).map(feature => this.formatFeatureName(feature));
        const values = Object.values(result.shap);
        const colors = values.map(value => 
            value > 0 ? 'rgba(255, 107, 107, 0.8)' : 'rgba(72, 219, 251, 0.8)'
        );
        
        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = values;
        this.chart.data.datasets[0].backgroundColor = colors;
        this.chart.data.datasets[0].borderColor = colors.map(color => color.replace('0.8', '1'));
        
        this.chart.update('active');
    }
    
    updateClinicalInsights(result) {
        const insights = this.generateInsights(result);
        const container = document.getElementById('clinicalInsights');
        
        if (container) {
            container.innerHTML = insights.map(insight => `
                <div class="alert alert-${insight.type} d-flex align-items-center" role="alert">
                    <i class="fas fa-${insight.icon} me-2"></i>
                    <div>${insight.message}</div>
                </div>
            `).join('');
        }
    }
    
    generateInsights(result) {
        const insights = [];
        const topFeatures = Object.entries(result.shap)
            .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
            .slice(0, 3);
        
        // Generate insights based on top features
        topFeatures.forEach(([feature, value]) => {
            const patientValue = this.getPatientValue(feature);
            const formattedFeature = this.formatFeatureName(feature);
            
            if (feature.toLowerCase().includes('creatinine') && value > 0) {
                insights.push({
                    type: 'warning',
                    icon: 'exclamation-triangle',
                    message: `Elevated creatinine (${patientValue} mg/dL) significantly increases CKD risk. Consider renal function monitoring.`
                });
            } else if (feature.toLowerCase().includes('egfr') && value < 0) {
                insights.push({
                    type: 'info',
                    icon: 'info-circle',
                    message: `Normal eGFR (${patientValue} mL/min/1.73m²) is protective for kidney health.`
                });
            } else if (feature.toLowerCase().includes('age') && value > 0) {
                insights.push({
                    type: 'info',
                    icon: 'user',
                    message: `Age (${patientValue} years) contributes to CKD risk. Regular screening recommended.`
                });
            } else if (feature.toLowerCase().includes('hba1c') && value > 0) {
                insights.push({
                    type: 'warning',
                    icon: 'tint',
                    message: `Elevated HbA1c (${patientValue}%) increases CKD risk. Intensive diabetes management advised.`
                });
            }
        });
        
        // Add overall risk assessment
        if (result.probability >= 0.7) {
            insights.push({
                type: 'danger',
                icon: 'exclamation-triangle',
                message: `High CKD risk (${(result.probability * 100).toFixed(1)}%). Immediate medical evaluation recommended.`
            });
        } else if (result.probability >= 0.3) {
            insights.push({
                type: 'warning',
                icon: 'exclamation-circle',
                message: `Moderate CKD risk (${(result.probability * 100).toFixed(1)}%). Regular monitoring advised.`
            });
        } else {
            insights.push({
                type: 'success',
                icon: 'check-circle',
                message: `Low CKD risk (${(result.probability * 100).toFixed(1)}%). Continue routine care.`
            });
        }
        
        return insights;
    }
    
    addToHistory(result) {
        this.predictionHistory.push({
            timestamp: new Date().toISOString(),
            data: {...this.currentData},
            result: {...result}
        });
        
        // Keep only recent history
        if (this.predictionHistory.length > this.maxHistoryLength) {
            this.predictionHistory.shift();
        }
        
        this.updateHistoryDisplay();
    }
    
    updateHistoryDisplay() {
        const container = document.getElementById('historyDisplay');
        if (!container) return;
        
        const recentHistory = this.predictionHistory.slice(-5);
        container.innerHTML = recentHistory.map((entry, index) => `
            <div class="history-item">
                <small class="text-muted">${new Date(entry.timestamp).toLocaleTimeString()}</small>
                <div>Risk: ${(entry.result.probability * 100).toFixed(1)}%</div>
            </div>
        `).join('');
    }
    
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
            'sBPBaseline': 'Systolic BP',
            'dBPBaseline': 'Diastolic BP',
            'HistoryCHD': 'Coronary Disease',
            'HistoryVascular': 'Vascular Disease',
            'HistoryDLD': 'Lipid Disorder',
            'HistoryObesity': 'Obesity',
            'DLDmeds': 'Lipid Meds',
            'DMmeds': 'Diabetes Meds',
            'HTNmeds': 'Hypertension Meds',
            'ACEIARB': 'ACEI/ARB'
        };
        
        return nameMap[feature] || feature;
    }
    
    getPatientValue(feature) {
        const valueMap = {
            'CreatnineBaseline': this.currentData.creatinine?.toFixed(1) + ' mg/dL',
            'eGFRBaseline': this.currentData.egfr + ' mL/min/1.73m²',
            'AgeBaseline': this.currentData.age + ' years',
            'HgbA1C': this.currentData.hba1c?.toFixed(1) + '%',
            'HistoryHTN': this.currentData.htn ? 'Yes' : 'No',
            'HistoryDiabetes': this.currentData.diabetes ? 'Yes' : 'No',
            'BMIBaseline': this.currentData.bmi?.toFixed(1) + ' kg/m²',
            'CholesterolBaseline': this.currentData.cholesterol + ' mg/dL',
            'TriglyceridesBaseline': this.currentData.triglycerides + ' mg/dL',
            'HistorySmoking': this.currentData.smoking ? 'Yes' : 'No',
            'sBPBaseline': this.currentData.sbp + ' mmHg',
            'dBPBaseline': this.currentData.dbp + ' mmHg',
            'HistoryCHD': this.currentData.chd ? 'Yes' : 'No',
            'HistoryVascular': this.currentData.vascular ? 'Yes' : 'No',
            'HistoryDLD': this.currentData.dld ? 'Yes' : 'No',
            'HistoryObesity': this.currentData.obesity ? 'Yes' : 'No',
            'DLDmeds': this.currentData.dld_meds ? 'Yes' : 'No',
            'DMmeds': this.currentData.dm_meds ? 'Yes' : 'No',
            'HTNmeds': this.currentData.htn_meds ? 'Yes' : 'No',
            'ACEIARB': this.currentData.acei_arb ? 'Yes' : 'No'
        };
        
        return valueMap[feature] || 'N/A';
    }
    
    showFeatureDetails(feature, shapValue, patientValue) {
        // Create modal or expandable section with detailed information
        console.log('Feature details:', { feature, shapValue, patientValue });
        // Implementation would go here
    }
    
    animateValue(elementId, start, end, duration) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = start + (end - start) * progress;
            element.textContent = Math.round(current) + '%';
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            if (show) {
                overlay.classList.remove('d-none');
            } else {
                overlay.classList.add('d-none');
            }
        }
    }
    
    addInsight(message, type = 'info') {
        const stream = document.getElementById('insightStream');
        if (!stream) return;
        
        const insight = document.createElement('div');
        insight.className = `insight-item alert-${type} animate__animated animate__fadeInLeft`;
        insight.innerHTML = `
            <div class="d-flex justify-content-between">
                <small class="text-muted">${new Date().toLocaleTimeString()}</small>
                <button class="btn-close btn-close-white btn-sm" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
            <div>${message}</div>
        `;
        
        stream.insertBefore(insight, stream.firstChild);
        
        // Keep only last 10 insights
        while (stream.children.length > 10) {
            stream.removeChild(stream.lastChild);
        }
    }
    
    toggleRealTime(enabled) {
        this.realtimeMode = enabled;
        this.addInsight(`Real-time monitoring ${enabled ? 'enabled' : 'disabled'}`, 'info');
    }
    
    randomizePatient() {
        // Generate random patient data with realistic ranges from dataset
        this.currentData = {
            age: Math.floor(Math.random() * 52) + 28,  // 28-80 years (5th-95th percentile)
            cholesterol: Math.floor(Math.random() * 277) + 86,  // 86-363 mg/dL (converted from dataset)
            triglycerides: Math.floor(Math.random() * 486) + 66,  // 66-552 mg/dL (converted from dataset)
            hba1c: Math.random() * 5.33 + 5.0,  // 5.0-10.33% (5th-95th percentile)
            creatinine: Math.random() * 1.32 + 0.07,  // 0.07-1.39 mg/dL (converted from dataset)
            egfr: Math.floor(Math.random() * 59) + 67,  // 67-126 mL/min/1.73m² (5th-95th percentile)
            sbp: Math.floor(Math.random() * 54) + 107,  // 107-161 mmHg (5th-95th percentile)
            dbp: Math.floor(Math.random() * 35) + 60,  // 60-95 mmHg (5th-95th percentile)
            bmi: Math.floor(Math.random() * 20) + 22,  // 22-42 kg/m² (5th-95th percentile)
            time_to_event: Math.floor(Math.random() * 47) + 1,
            gender: Math.random() > 0.5 ? 1 : 0,
            diabetes: Math.random() > 0.88 ? 1 : 0,  // ~12% prevalence in dataset
            chd: Math.random() > 0.95 ? 1 : 0,
            vascular: Math.random() > 0.95 ? 1 : 0,
            smoking: Math.random() > 0.5 ? 1 : 0,
            htn: Math.random() > 0.3 ? 1 : 0,
            dld: Math.random() > 0.3 ? 1 : 0,
            obesity: Math.random() > 0.4 ? 1 : 0,
            dld_meds: Math.random() > 0.7 ? 1 : 0,
            dm_meds: Math.random() > 0.88 ? 1 : 0,
            htn_meds: Math.random() > 0.3 ? 1 : 0,
            acei_arb: Math.random() > 0.7 ? 1 : 0
        };
        
        // Update all controls
        this.updateAllControls();
        
        // Update analysis
        this.updatePrediction();
        
        this.addInsight('Random patient profile generated', 'info');
    }
    
    updateAllControls() {
        // Update sliders
        this.updateSlider('ageSlider', 'ageValue', this.currentData.age);
        this.updateSlider('creatinineSlider', 'creatinineValue', this.currentData.creatinine);
        this.updateSlider('egfrSlider', 'egfrValue', this.currentData.egfr);
        this.updateSlider('hba1cSlider', 'hba1cValue', this.currentData.hba1c);
        this.updateSlider('sbpSlider', 'sbpValue', this.currentData.sbp);
        this.updateSlider('dbpSlider', 'dbpValue', this.currentData.dbp);
        this.updateSlider('bmiSlider', 'bmiValue', this.currentData.bmi);
        this.updateSlider('cholesterolSlider', 'cholesterolValue', this.currentData.cholesterol);
        this.updateSlider('triglyceridesSlider', 'triglyceridesValue', this.currentData.triglycerides);
        
        // Update toggles
        this.updateToggle('diabetesToggle', this.currentData.diabetes);
        this.updateToggle('htnToggle', this.currentData.htn);
        this.updateToggle('smokingToggle', this.currentData.smoking);
        this.updateToggle('chdToggle', this.currentData.chd);
        this.updateToggle('vascularToggle', this.currentData.vascular);
        this.updateToggle('dldToggle', this.currentData.dld);
        this.updateToggle('obesityToggle', this.currentData.obesity);
    }
    
    updateSlider(sliderId, valueId, value) {
        const slider = document.getElementById(sliderId);
        const valueDisplay = document.getElementById(valueId);
        
        if (slider && valueDisplay) {
            slider.value = value;
            valueDisplay.textContent = typeof value === 'number' && value % 1 !== 0 ? value.toFixed(1) : value;
        }
    }
    
    updateToggle(toggleId, value) {
        const toggle = document.getElementById(toggleId);
        if (toggle) {
            toggle.checked = value === 1;
        }
    }
    
    loadScenario(scenarioName) {
        const scenarios = {
            optimal: {
                age: 35, 
                cholesterol: 154,  // 4.0 mmol/L * 38.67
                triglycerides: 71,  // 0.8 mmol/L * 88.54
                hba1c: 5.0,
                creatinine: 0.57,  // 50 μmol/L / 88.4
                egfr: 110, 
                sbp: 107, 
                dbp: 60, 
                bmi: 22,
                diabetes: 0, chd: 0, vascular: 0, smoking: 0, htn: 0,
                dld: 0, obesity: 0, dld_meds: 0, dm_meds: 0, htn_meds: 0, acei_arb: 0
            },
            typical: {
                age: 54, 
                cholesterol: 193,  // 5.0 mmol/L * 38.67
                triglycerides: 98,  // 1.1 mmol/L * 88.54
                hba1c: 6.1,
                creatinine: 0.77,  // 68 μmol/L / 88.4
                egfr: 98, 
                sbp: 131, 
                dbp: 77, 
                bmi: 30,
                diabetes: 0, chd: 0, vascular: 0, smoking: 0, htn: 1,
                dld: 1, obesity: 1, dld_meds: 0, dm_meds: 0, htn_meds: 1, acei_arb: 0
            },
            highRisk: {
                age: 75, 
                cholesterol: 277,  // 7.2 mmol/L * 38.67
                triglycerides: 265,  // 3.0 mmol/L * 88.54
                hba1c: 10.3,
                creatinine: 1.39,  // 123 μmol/L / 88.4
                egfr: 35, 
                sbp: 160, 
                dbp: 95, 
                bmi: 42,
                diabetes: 1, chd: 1, vascular: 1, smoking: 1, htn: 1,
                dld: 1, obesity: 1, dld_meds: 1, dm_meds: 1, htn_meds: 1, acei_arb: 1
            }
        };
        
        const scenario = scenarios[scenarioName];
        if (scenario) {
            Object.assign(this.currentData, scenario);
            this.updateAllControls();
            this.updatePrediction();
            this.addInsight(`Loaded ${scenarioName} scenario`, 'success');
        }
    }
    
    exportAnalysis() {
        const exportData = {
            patient: this.currentData,
            prediction: this.lastResult,
            history: this.predictionHistory,
            timestamp: new Date().toISOString(),
            version: '2.0.0'
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.download = `dynamic-shap-analysis-${Date.now()}.json`;
        link.href = url;
        link.click();
        URL.revokeObjectURL(url);
        
        this.addInsight('Analysis exported successfully', 'success');
    }
    
    loadInitialData() {
        // Load initial data and update
        setTimeout(() => {
            this.updatePrediction();
        }, 1000);
    }
    
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        if (this.updateTimeout) {
            clearTimeout(this.updateTimeout);
        }
    }
    
    checkForExcelData() {
        // Check if Excel data was passed from Excel Input page
        const excelData = localStorage.getItem('excelData');
        if (excelData) {
            try {
                const data = JSON.parse(excelData);
                this.loadExcelData(data);
                // Clear the stored data
                localStorage.removeItem('excelData');
                console.log('✅ Excel data loaded from Excel Input page');
            } catch (error) {
                console.error('Error loading Excel data:', error);
            }
        }
    }
    
    loadExcelData(data) {
        // Update current data with Excel values
        Object.assign(this.currentData, data);
        
        // Update all UI controls
        this.updateAllControls();
        
        // Show notification
        this.showNotification('Excel values loaded successfully!', 'success');
        
        // Trigger prediction
        this.updatePrediction();
    }
    
    showNotification(message, type = 'info') {
        // Create a simple notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
}

// Global instance
let dynamicSHAP;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    dynamicSHAP = new DynamicSHAPSystem();
    
    // Make globally accessible
    window.dynamicSHAP = dynamicSHAP;
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'r':
                    e.preventDefault();
                    dynamicSHAP.randomizePatient();
                    break;
                case 'u':
                    e.preventDefault();
                    dynamicSHAP.updatePrediction();
                    break;
                case 'e':
                    e.preventDefault();
                    dynamicSHAP.exportAnalysis();
                    break;
            }
        }
    });
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (dynamicSHAP) {
        dynamicSHAP.destroy();
    }
});
