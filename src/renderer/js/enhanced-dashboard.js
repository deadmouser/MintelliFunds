/**
 * Enhanced Dashboard Controller
 * Advanced financial data visualizations, insight cards, and actionable recommendations
 */
class EnhancedDashboard {
    constructor(app) {
        this.app = app;
        this.charts = {};
        this.insights = [];
        this.anomalies = [];
        this.recommendations = [];
        this.analysisCache = new Map();
        
        this.init();
    }

    /**
     * Initialize the enhanced dashboard
     */
    init() {
        this.renderEnhancedDashboard();
        this.setupEventListeners();
        this.loadDashboardData();
        
        // Auto-refresh every 5 minutes
        setInterval(() => {
            this.refreshDashboardData();
        }, 300000);
    }

    /**
     * Render the enhanced dashboard interface
     */
    renderEnhancedDashboard() {
        const dashboardSection = document.getElementById('dashboard-section');
        if (!dashboardSection) return;

        // Keep existing summary cards but enhance them
        this.enhanceExistingSummaryCards();
        
        // Add new advanced analysis sections
        const advancedSections = document.createElement('div');
        advancedSections.className = 'advanced-dashboard-sections';
        advancedSections.innerHTML = `
            <!-- Financial Health Score -->
            <div class="card health-score-card">
                <div class="card-header">
                    <h3>Financial Health Score</h3>
                    <div class="health-score-legend">
                        <span class="score-range poor">0-40</span>
                        <span class="score-range fair">41-60</span>
                        <span class="score-range good">61-80</span>
                        <span class="score-range excellent">81-100</span>
                    </div>
                </div>
                <div class="card-body">
                    <div class="health-score-display">
                        <div class="score-circle" id="health-score-circle">
                            <div class="score-value" id="health-score-value">--</div>
                            <div class="score-label">Health Score</div>
                        </div>
                        <div class="score-breakdown">
                            <div class="score-factor">
                                <div class="factor-name">Savings Rate</div>
                                <div class="factor-score" id="savings-rate-score">--</div>
                                <div class="factor-bar">
                                    <div class="factor-progress" id="savings-rate-progress"></div>
                                </div>
                            </div>
                            <div class="score-factor">
                                <div class="factor-name">Debt-to-Income</div>
                                <div class="factor-score" id="debt-ratio-score">--</div>
                                <div class="factor-bar">
                                    <div class="factor-progress" id="debt-ratio-progress"></div>
                                </div>
                            </div>
                            <div class="score-factor">
                                <div class="factor-name">Emergency Fund</div>
                                <div class="factor-score" id="emergency-fund-score">--</div>
                                <div class="factor-bar">
                                    <div class="factor-progress" id="emergency-fund-progress"></div>
                                </div>
                            </div>
                            <div class="score-factor">
                                <div class="factor-name">Investment Diversity</div>
                                <div class="factor-score" id="diversity-score">--</div>
                                <div class="factor-bar">
                                    <div class="factor-progress" id="diversity-progress"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- AI Insights & Recommendations -->
            <div class="card insights-card">
                <div class="card-header">
                    <h3>AI-Powered Insights</h3>
                    <div class="insights-controls">
                        <select id="insights-filter">
                            <option value="all">All Insights</option>
                            <option value="alerts">Alerts</option>
                            <option value="opportunities">Opportunities</option>
                            <option value="recommendations">Recommendations</option>
                        </select>
                        <button id="refresh-insights" class="btn btn-secondary">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="insights-container" id="insights-container">
                        <div class="insights-loading">
                            <i class="fas fa-brain fa-pulse"></i>
                            <p>Analyzing your financial data...</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Advanced Analytics Grid -->
            <div class="analytics-grid">
                <div class="card chart-card">
                    <div class="card-header">
                        <h3>Cash Flow Analysis</h3>
                        <div class="chart-controls">
                            <select id="cashflow-period">
                                <option value="3m">3 Months</option>
                                <option value="6m" selected>6 Months</option>
                                <option value="1y">1 Year</option>
                            </select>
                        </div>
                    </div>
                    <div class="card-body">
                        <canvas id="cashflow-chart"></canvas>
                    </div>
                </div>

                <div class="card chart-card">
                    <div class="card-header">
                        <h3>Spending Patterns</h3>
                        <div class="chart-controls">
                            <button class="chart-type-btn active" data-type="category">By Category</button>
                            <button class="chart-type-btn" data-type="merchant">By Merchant</button>
                            <button class="chart-type-btn" data-type="time">By Time</button>
                        </div>
                    </div>
                    <div class="card-body">
                        <canvas id="spending-patterns-chart"></canvas>
                    </div>
                </div>

                <div class="card chart-card">
                    <div class="card-header">
                        <h3>Investment Performance</h3>
                        <div class="performance-metrics">
                            <div class="metric">
                                <div class="metric-value" id="portfolio-return">+12.5%</div>
                                <div class="metric-label">YTD Return</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value" id="portfolio-risk">Medium</div>
                                <div class="metric-label">Risk Level</div>
                            </div>
                        </div>
                    </div>
                    <div class="card-body">
                        <canvas id="investment-performance-chart"></canvas>
                    </div>
                </div>

                <div class="card anomaly-detection-card">
                    <div class="card-header">
                        <h3>Anomaly Detection</h3>
                        <div class="anomaly-stats">
                            <span class="anomaly-count" id="anomaly-count">0</span>
                            <span class="anomaly-label">unusual transactions</span>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="anomalies-list" id="anomalies-list">
                            <!-- Anomalies will be populated here -->
                        </div>
                    </div>
                </div>
            </div>

            <!-- Goal Progress & Projections -->
            <div class="goals-projections-section">
                <div class="card goals-card">
                    <div class="card-header">
                        <h3>Financial Goals</h3>
                        <button id="add-goal" class="btn btn-primary">
                            <i class="fas fa-plus"></i>
                            Add Goal
                        </button>
                    </div>
                    <div class="card-body">
                        <div class="goals-list" id="goals-list">
                            <!-- Goals will be populated here -->
                        </div>
                    </div>
                </div>

                <div class="card projections-card">
                    <div class="card-header">
                        <h3>Future Projections</h3>
                        <div class="projection-controls">
                            <select id="projection-scenario">
                                <option value="conservative">Conservative</option>
                                <option value="moderate" selected>Moderate</option>
                                <option value="aggressive">Aggressive</option>
                            </select>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="projections-grid">
                            <div class="projection-item">
                                <div class="projection-title">Net Worth (1 Year)</div>
                                <div class="projection-value" id="networth-projection">₹0</div>
                                <div class="projection-change positive" id="networth-change">+0%</div>
                            </div>
                            <div class="projection-item">
                                <div class="projection-title">Emergency Fund Goal</div>
                                <div class="projection-value" id="emergency-projection">₹0</div>
                                <div class="projection-timeline" id="emergency-timeline">0 months</div>
                            </div>
                            <div class="projection-item">
                                <div class="projection-title">Retirement Readiness</div>
                                <div class="projection-value" id="retirement-projection">0%</div>
                                <div class="projection-note" id="retirement-note">On track</div>
                            </div>
                        </div>
                        <canvas id="projections-chart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Actionable Recommendations -->
            <div class="card recommendations-card">
                <div class="card-header">
                    <h3>Personalized Recommendations</h3>
                    <div class="recommendations-filter">
                        <button class="filter-btn active" data-filter="all">All</button>
                        <button class="filter-btn" data-filter="urgent">Urgent</button>
                        <button class="filter-btn" data-filter="savings">Savings</button>
                        <button class="filter-btn" data-filter="investment">Investment</button>
                        <button class="filter-btn" data-filter="debt">Debt</button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="recommendations-list" id="recommendations-list">
                        <!-- Recommendations will be populated here -->
                    </div>
                </div>
            </div>
        `;

        // Insert after the existing dashboard grid
        const existingGrid = document.querySelector('.dashboard-grid');
        if (existingGrid) {
            existingGrid.parentNode.insertBefore(advancedSections, existingGrid.nextSibling);
        }
    }

    /**
     * Enhance existing summary cards with additional features
     */
    enhanceExistingSummaryCards() {
        const summaryCards = document.querySelectorAll('.summary-card');
        
        summaryCards.forEach((card, index) => {
            // Add trend indicators
            const cardBody = card.querySelector('.card-body');
            if (cardBody && !cardBody.querySelector('.trend-indicator')) {
                const trendIndicator = document.createElement('div');
                trendIndicator.className = 'trend-indicator';
                trendIndicator.innerHTML = `
                    <canvas class="trend-sparkline" width="60" height="20"></canvas>
                `;
                cardBody.appendChild(trendIndicator);
            }

            // Add click handler for detailed view
            card.addEventListener('click', () => {
                this.showDetailedView(this.getCardType(card));
            });

            // Add hover effects
            card.classList.add('enhanced-card');
        });
    }

    /**
     * Get card type based on its content
     */
    getCardType(card) {
        const title = card.querySelector('h3')?.textContent?.toLowerCase();
        if (title?.includes('balance')) return 'balance';
        if (title?.includes('spending')) return 'spending';
        if (title?.includes('savings')) return 'savings';
        if (title?.includes('investment')) return 'investment';
        return 'general';
    }

    /**
     * Load dashboard data and render visualizations
     */
    async loadDashboardData() {
        try {
            // Load data in parallel
            const [
                dashboardData,
                insightsData,
                anomaliesData,
                goalsData,
                projectionsData
            ] = await Promise.all([
                this.fetchDashboardData(),
                this.fetchInsights(),
                this.detectAnomalies(),
                this.fetchGoals(),
                this.calculateProjections()
            ]);

            // Update financial health score
            this.updateHealthScore(dashboardData);

            // Render insights
            this.renderInsights(insightsData);

            // Render anomalies
            this.renderAnomalies(anomaliesData);

            // Render goals
            this.renderGoals(goalsData);

            // Render projections
            this.renderProjections(projectionsData);

            // Create charts
            this.createAdvancedCharts(dashboardData);

            // Generate recommendations
            const recommendations = this.generateRecommendations(dashboardData);
            this.renderRecommendations(recommendations);

        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    /**
     * Update financial health score display
     */
    updateHealthScore(data) {
        // Calculate health score based on multiple factors
        const scores = {
            savingsRate: this.calculateSavingsRateScore(data.savingsRate || 15),
            debtRatio: this.calculateDebtRatioScore(data.debtToIncomeRatio || 30),
            emergencyFund: this.calculateEmergencyFundScore(data.emergencyFundMonths || 3),
            diversity: this.calculateDiversityScore(data.investmentDiversity || 60)
        };

        // Overall health score (weighted average)
        const overallScore = Math.round(
            (scores.savingsRate * 0.3 + 
             scores.debtRatio * 0.25 + 
             scores.emergencyFund * 0.25 + 
             scores.diversity * 0.2)
        );

        // Update UI
        this.updateScoreDisplay('health-score-value', overallScore);
        this.updateScoreDisplay('savings-rate-score', scores.savingsRate);
        this.updateScoreDisplay('debt-ratio-score', scores.debtRatio);
        this.updateScoreDisplay('emergency-fund-score', scores.emergencyFund);
        this.updateScoreDisplay('diversity-score', scores.diversity);

        // Update score circle
        this.animateScoreCircle(overallScore);

        // Update progress bars
        this.updateFactorProgress('savings-rate-progress', scores.savingsRate);
        this.updateFactorProgress('debt-ratio-progress', scores.debtRatio);
        this.updateFactorProgress('emergency-fund-progress', scores.emergencyFund);
        this.updateFactorProgress('diversity-progress', scores.diversity);
    }

    /**
     * Calculate individual health score components
     */
    calculateSavingsRateScore(savingsRate) {
        if (savingsRate >= 20) return 100;
        if (savingsRate >= 15) return 80;
        if (savingsRate >= 10) return 60;
        if (savingsRate >= 5) return 40;
        return 20;
    }

    calculateDebtRatioScore(debtRatio) {
        if (debtRatio <= 10) return 100;
        if (debtRatio <= 20) return 80;
        if (debtRatio <= 30) return 60;
        if (debtRatio <= 40) return 40;
        return 20;
    }

    calculateEmergencyFundScore(months) {
        if (months >= 6) return 100;
        if (months >= 4) return 80;
        if (months >= 3) return 60;
        if (months >= 1) return 40;
        return 20;
    }

    calculateDiversityScore(diversityPercentage) {
        if (diversityPercentage >= 80) return 100;
        if (diversityPercentage >= 60) return 80;
        if (diversityPercentage >= 40) return 60;
        if (diversityPercentage >= 20) return 40;
        return 20;
    }

    /**
     * Update score display elements
     */
    updateScoreDisplay(elementId, score) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = score;
            element.className = `score-value ${this.getScoreClass(score)}`;
        }
    }

    /**
     * Animate score circle
     */
    animateScoreCircle(score) {
        const circle = document.getElementById('health-score-circle');
        if (!circle) return;

        const circumference = 2 * Math.PI * 40; // radius = 40
        const offset = circumference - (score / 100) * circumference;

        // Add SVG circle if not exists
        if (!circle.querySelector('svg')) {
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('width', '120');
            svg.setAttribute('height', '120');
            svg.style.position = 'absolute';
            svg.style.top = '0';
            svg.style.left = '0';

            const backgroundCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            backgroundCircle.setAttribute('cx', '60');
            backgroundCircle.setAttribute('cy', '60');
            backgroundCircle.setAttribute('r', '40');
            backgroundCircle.setAttribute('fill', 'none');
            backgroundCircle.setAttribute('stroke', '#e5e7eb');
            backgroundCircle.setAttribute('stroke-width', '6');

            const progressCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            progressCircle.setAttribute('cx', '60');
            progressCircle.setAttribute('cy', '60');
            progressCircle.setAttribute('r', '40');
            progressCircle.setAttribute('fill', 'none');
            progressCircle.setAttribute('stroke', this.getScoreColor(score));
            progressCircle.setAttribute('stroke-width', '6');
            progressCircle.setAttribute('stroke-linecap', 'round');
            progressCircle.setAttribute('stroke-dasharray', circumference);
            progressCircle.setAttribute('stroke-dashoffset', offset);
            progressCircle.setAttribute('transform', 'rotate(-90 60 60)');
            progressCircle.style.transition = 'stroke-dashoffset 1s ease-in-out';

            svg.appendChild(backgroundCircle);
            svg.appendChild(progressCircle);
            circle.appendChild(svg);
        }
    }

    /**
     * Update factor progress bars
     */
    updateFactorProgress(elementId, score) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.width = `${score}%`;
            element.style.backgroundColor = this.getScoreColor(score);
            element.style.transition = 'width 1s ease-in-out';
        }
    }

    /**
     * Get score-based CSS class
     */
    getScoreClass(score) {
        if (score >= 81) return 'excellent';
        if (score >= 61) return 'good';
        if (score >= 41) return 'fair';
        return 'poor';
    }

    /**
     * Get score-based color
     */
    getScoreColor(score) {
        if (score >= 81) return '#10b981';
        if (score >= 61) return '#3b82f6';
        if (score >= 41) return '#f59e0b';
        return '#ef4444';
    }

    /**
     * Render AI insights
     */
    renderInsights(insights) {
        const container = document.getElementById('insights-container');
        if (!container) return;

        if (!insights || insights.length === 0) {
            container.innerHTML = `
                <div class="no-insights">
                    <i class="fas fa-lightbulb"></i>
                    <p>No insights available yet. Keep using the app to get personalized recommendations!</p>
                </div>
            `;
            return;
        }

        container.innerHTML = insights.map(insight => `
            <div class="insight-card insight-${insight.type}">
                <div class="insight-icon">
                    <i class="fas ${this.getInsightIcon(insight.type)}"></i>
                </div>
                <div class="insight-content">
                    <div class="insight-title">${insight.title}</div>
                    <div class="insight-description">${insight.description}</div>
                    <div class="insight-impact">
                        <span class="impact-label">Potential Impact:</span>
                        <span class="impact-value">${insight.impact}</span>
                    </div>
                </div>
                <div class="insight-actions">
                    <button class="insight-action-btn primary" onclick="enhancedDashboard.executeInsightAction('${insight.id}', 'apply')">
                        ${insight.actionLabel || 'Apply'}
                    </button>
                    <button class="insight-action-btn secondary" onclick="enhancedDashboard.executeInsightAction('${insight.id}', 'dismiss')">
                        Dismiss
                    </button>
                </div>
            </div>
        `).join('');
    }

    /**
     * Get icon for insight type
     */
    getInsightIcon(type) {
        const icons = {
            alert: 'fa-exclamation-triangle',
            opportunity: 'fa-lightbulb',
            recommendation: 'fa-star',
            achievement: 'fa-trophy',
            warning: 'fa-exclamation-circle'
        };
        return icons[type] || 'fa-info-circle';
    }

    /**
     * Render detected anomalies
     */
    renderAnomalies(anomalies) {
        const container = document.getElementById('anomalies-list');
        const countElement = document.getElementById('anomaly-count');
        
        if (countElement) {
            countElement.textContent = anomalies.length;
        }

        if (!container) return;

        if (anomalies.length === 0) {
            container.innerHTML = `
                <div class="no-anomalies">
                    <i class="fas fa-check-circle"></i>
                    <p>No unusual transactions detected</p>
                </div>
            `;
            return;
        }

        container.innerHTML = anomalies.map(anomaly => `
            <div class="anomaly-item severity-${anomaly.severity}">
                <div class="anomaly-info">
                    <div class="anomaly-amount">₹${anomaly.amount.toLocaleString()}</div>
                    <div class="anomaly-description">${anomaly.description}</div>
                    <div class="anomaly-date">${this.formatDate(anomaly.date)}</div>
                </div>
                <div class="anomaly-score">
                    <span class="anomaly-severity">${anomaly.severity}</span>
                    <span class="anomaly-confidence">${anomaly.confidence}% sure</span>
                </div>
                <div class="anomaly-actions">
                    <button class="anomaly-action-btn" onclick="enhancedDashboard.reviewAnomaly('${anomaly.id}')">
                        Review
                    </button>
                </div>
            </div>
        `).join('');
    }

    /**
     * Create advanced charts
     */
    async createAdvancedCharts(data) {
        // Cash Flow Chart
        this.createCashFlowChart(data.cashFlow);
        
        // Spending Patterns Chart
        this.createSpendingPatternsChart(data.spendingPatterns);
        
        // Investment Performance Chart
        this.createInvestmentChart(data.investmentPerformance);
        
        // Projections Chart
        this.createProjectionsChart(data.projections);
        
        // Update trend sparklines in summary cards
        this.updateTrendSparklines(data.trends);
    }

    /**
     * Create cash flow chart
     */
    createCashFlowChart(cashFlowData) {
        const ctx = document.getElementById('cashflow-chart');
        if (!ctx) return;

        if (this.charts.cashFlow) {
            this.charts.cashFlow.destroy();
        }

        this.charts.cashFlow = new Chart(ctx, {
            type: 'line',
            data: {
                labels: cashFlowData.labels,
                datasets: [{
                    label: 'Income',
                    data: cashFlowData.income,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true
                }, {
                    label: 'Expenses',
                    data: cashFlowData.expenses,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    fill: true
                }, {
                    label: 'Net Cash Flow',
                    data: cashFlowData.net,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: false,
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ₹' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * Setup event listeners for dashboard interactions
     */
    setupEventListeners() {
        // Insights filter
        const insightsFilter = document.getElementById('insights-filter');
        if (insightsFilter) {
            insightsFilter.addEventListener('change', (e) => {
                this.filterInsights(e.target.value);
            });
        }

        // Refresh insights
        const refreshInsights = document.getElementById('refresh-insights');
        if (refreshInsights) {
            refreshInsights.addEventListener('click', () => {
                this.refreshInsights();
            });
        }

        // Chart controls
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('chart-type-btn')) {
                this.handleChartTypeChange(e.target);
            }
            
            if (e.target.classList.contains('filter-btn')) {
                this.handleRecommendationsFilter(e.target);
            }
        });

        // Chart period changes
        const cashflowPeriod = document.getElementById('cashflow-period');
        if (cashflowPeriod) {
            cashflowPeriod.addEventListener('change', (e) => {
                this.updateCashFlowChart(e.target.value);
            });
        }

        // Add goal button
        const addGoalBtn = document.getElementById('add-goal');
        if (addGoalBtn) {
            addGoalBtn.addEventListener('click', () => {
                this.showAddGoalModal();
            });
        }

        // Projection scenario change
        const projectionScenario = document.getElementById('projection-scenario');
        if (projectionScenario) {
            projectionScenario.addEventListener('change', (e) => {
                this.updateProjections(e.target.value);
            });
        }
    }

    /**
     * Mock data fetching methods (to be replaced with real API calls)
     */
    async fetchDashboardData() {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 800));
        
        return {
            savingsRate: 18,
            debtToIncomeRatio: 25,
            emergencyFundMonths: 4,
            investmentDiversity: 75,
            cashFlow: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                income: [80000, 80000, 85000, 80000, 80000, 82000],
                expenses: [55000, 60000, 58000, 62000, 59000, 61000],
                net: [25000, 20000, 27000, 18000, 21000, 21000]
            },
            spendingPatterns: {
                categories: ['Food', 'Transport', 'Entertainment', 'Shopping', 'Bills'],
                amounts: [15000, 8000, 5000, 12000, 18000]
            },
            investmentPerformance: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                portfolio: [100000, 102000, 98000, 105000, 108000, 112000],
                benchmark: [100000, 101000, 99000, 102000, 104000, 106000]
            },
            trends: {
                balance: [120000, 122000, 119000, 125000, 128000, 130000],
                spending: [55000, 60000, 58000, 62000, 59000, 61000],
                savings: [25000, 27000, 24000, 28000, 30000, 32000],
                investment: [85000, 87000, 84000, 88000, 91000, 95000]
            }
        };
    }

    async fetchInsights() {
        await new Promise(resolve => setTimeout(resolve, 600));
        
        return [
            {
                id: 'insight-1',
                type: 'opportunity',
                title: 'Optimize Your Subscriptions',
                description: 'You have 3 unused subscriptions costing ₹2,400 monthly. Cancel them to boost your savings rate.',
                impact: '₹28,800 annually',
                actionLabel: 'Review Subscriptions'
            },
            {
                id: 'insight-2',
                type: 'alert',
                title: 'Food Expenses Trending Up',
                description: 'Your food expenses increased by 25% this month. Consider meal planning to control costs.',
                impact: 'Save ₹5,000 monthly',
                actionLabel: 'Create Budget'
            },
            {
                id: 'insight-3',
                type: 'recommendation',
                title: 'Investment Rebalancing',
                description: 'Your portfolio is 75% equity. Consider rebalancing for your moderate risk profile.',
                impact: 'Reduce volatility by 15%',
                actionLabel: 'Rebalance Now'
            }
        ];
    }

    async detectAnomalies() {
        await new Promise(resolve => setTimeout(resolve, 400));
        
        return [
            {
                id: 'anomaly-1',
                amount: 25000,
                description: 'Large grocery purchase at SuperMart',
                date: '2024-09-12',
                severity: 'medium',
                confidence: 85
            },
            {
                id: 'anomaly-2',
                amount: 15000,
                description: 'Unusual ATM withdrawal',
                date: '2024-09-10',
                severity: 'high',
                confidence: 92
            }
        ];
    }

    async fetchGoals() {
        await new Promise(resolve => setTimeout(resolve, 300));
        
        return [
            {
                id: 'goal-1',
                name: 'Emergency Fund',
                target: 500000,
                current: 300000,
                deadline: '2024-12-31',
                category: 'savings'
            },
            {
                id: 'goal-2',
                name: 'Vacation Fund',
                target: 100000,
                current: 45000,
                deadline: '2024-10-15',
                category: 'lifestyle'
            }
        ];
    }

    async calculateProjections() {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        return {
            netWorth: {
                current: 1250000,
                oneYear: 1450000,
                change: 16
            },
            emergencyFund: {
                target: 500000,
                current: 300000,
                monthsToGoal: 8
            },
            retirement: {
                readiness: 65,
                note: 'On track for comfortable retirement'
            }
        };
    }

    /**
     * Action handlers
     */
    executeInsightAction(insightId, action) {
        console.log(`Executing ${action} for insight ${insightId}`);
        
        if (action === 'apply') {
            this.app.showNotification('Insight action applied successfully!', 'success');
        } else if (action === 'dismiss') {
            this.app.showNotification('Insight dismissed', 'info');
            // Remove insight from UI
            const insightCard = document.querySelector(`[onclick*="${insightId}"]`)?.closest('.insight-card');
            if (insightCard) {
                insightCard.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => insightCard.remove(), 300);
            }
        }
    }

    reviewAnomaly(anomalyId) {
        console.log(`Reviewing anomaly ${anomalyId}`);
        this.app.showNotification('Opening anomaly review...', 'info');
    }

    showDetailedView(cardType) {
        console.log(`Showing detailed view for ${cardType}`);
        this.app.showNotification(`Opening detailed ${cardType} analysis...`, 'info');
    }

    /**
     * Utility methods
     */
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'short'
        });
    }

    showError(message) {
        this.app.showNotification(message, 'error');
    }

    async refreshDashboardData() {
        console.log('Refreshing dashboard data...');
        await this.loadDashboardData();
        this.app.showNotification('Dashboard refreshed', 'success');
    }

    // Additional methods would continue here for handling all the dashboard functionality
    // This includes chart creation, goal management, projections, etc.
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedDashboard;
} else {
    window.EnhancedDashboard = EnhancedDashboard;
}