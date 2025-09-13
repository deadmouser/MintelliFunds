// Dashboard Controller for Financial Data Visualization
class Dashboard {
    constructor(app) {
        this.app = app;
        this.charts = {};
        this.data = {};
        this.updateInterval = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupCharts();
    }

    setupEventListeners() {
        // Chart period selector
        const chartPeriod = document.getElementById('chart-period');
        if (chartPeriod) {
            chartPeriod.addEventListener('change', (e) => {
                this.updateChartPeriod(e.target.value);
            });
        }

        // Get more insights button
        const getInsightsBtn = document.getElementById('get-more-insights');
        if (getInsightsBtn) {
            getInsightsBtn.addEventListener('click', () => {
                this.generateMoreInsights();
            });
        }

        // Auto-refresh data every 5 minutes
        this.startAutoRefresh();
    }

    setupCharts() {
        // Initialize Chart.js charts
        this.initSpendingChart();
        this.initCategoryChart();
    }

    initSpendingChart() {
        const ctx = document.getElementById('spending-chart');
        if (!ctx) return;

        this.charts.spending = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Spending',
                    data: [],
                    borderColor: 'rgb(79, 70, 229)',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    tension: 0.4,
                    fill: true
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
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: (context) => {
                                return `Spending: ${this.app.formatCurrency(context.parsed.y)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '₹' + (value / 1000) + 'k';
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    initCategoryChart() {
        const ctx = document.getElementById('category-chart');
        if (!ctx) return;

        this.charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#f59e0b', // Food
                        '#3b82f6', // Transport
                        '#8b5cf6', // Shopping
                        '#ef4444', // Bills
                        '#10b981', // Entertainment
                        '#f97316', // Health
                        '#6366f1'  // Others
                    ],
                    borderWidth: 0,
                    hoverBorderWidth: 2,
                    hoverBorderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = this.app.formatCurrency(context.parsed);
                                const percentage = ((context.parsed / context.dataset.data.reduce((a, b) => a + b, 0)) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }

    async loadData() {
        try {
            // Load dashboard data from API
            const dashboardData = await this.app.apiRequest('/api/dashboard');
            this.data = dashboardData;
            
            // Update summary cards
            this.updateSummaryCards(dashboardData);
            
            // Load and update charts
            await this.loadChartData();
            
            // Load recent transactions
            await this.loadRecentTransactions();
            
            // Load AI insights
            await this.loadAIInsights();
            
            // Update last refresh time
            this.updateLastRefreshTime();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showErrorState();
        }
    }

    updateSummaryCards(data) {
        // Total Balance
        this.updateSummaryCard('total-balance', data.totalBalance || 0, 'balance-change', data.balanceChange);
        
        // Monthly Spending
        this.updateSummaryCard('monthly-spending', data.monthlySpending || 0, 'spending-change', data.spendingChange);
        
        // Savings Progress
        this.updateSavingsProgress(data.savingsProgress || 0, data.savingsGoal || 100000);
        
        // Investment Value
        this.updateSummaryCard('investment-value', data.investmentValue || 0, 'investment-change', data.investmentChange);
    }

    updateSummaryCard(elementId, amount, changeElementId, changePercent) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = this.app.formatCurrency(amount);
            
            // Animate the value change
            this.animateValueChange(element, amount);
        }
        
        // Update change indicator
        const changeElement = document.getElementById(changeElementId);
        if (changeElement && changePercent !== undefined) {
            const isPositive = changePercent > 0;
            const isNegative = changePercent < 0;
            
            changeElement.className = `change ${isPositive ? 'positive' : isNegative ? 'negative' : 'neutral'}`;
            changeElement.innerHTML = `
                <i class="fas fa-arrow-${isPositive ? 'up' : isNegative ? 'down' : 'right'}"></i>
                <span>${isPositive ? '+' : ''}${changePercent.toFixed(1)}% ${this.getChangeText(changeElementId)}</span>
            `;
        }
    }

    updateSavingsProgress(current, goal) {
        const progressElement = document.getElementById('savings-progress');
        const progressBarElement = document.getElementById('savings-progress-bar');
        const progressTextElement = document.getElementById('savings-percentage');
        
        if (progressElement) {
            progressElement.textContent = this.app.formatCurrency(current);
        }
        
        if (progressBarElement && progressTextElement) {
            const percentage = Math.min((current / goal) * 100, 100);
            
            // Animate progress bar
            setTimeout(() => {
                progressBarElement.style.width = `${percentage}%`;
            }, 100);
            
            progressTextElement.textContent = `${percentage.toFixed(1)}% of ${this.app.formatCurrency(goal)} goal`;
        }
    }

    getChangeText(changeElementId) {
        const textMap = {
            'balance-change': 'this month',
            'spending-change': 'vs last month',
            'investment-change': 'this month'
        };
        return textMap[changeElementId] || '';
    }

    animateValueChange(element, targetValue) {
        const currentValue = parseFloat(element.textContent.replace(/[₹,]/g, '')) || 0;
        const difference = targetValue - currentValue;
        const steps = 30;
        const stepValue = difference / steps;
        let currentStep = 0;
        
        const animate = () => {
            if (currentStep < steps) {
                const newValue = currentValue + (stepValue * currentStep);
                element.textContent = this.app.formatCurrency(newValue);
                currentStep++;
                requestAnimationFrame(animate);
            } else {
                element.textContent = this.app.formatCurrency(targetValue);
            }
        };
        
        animate();
    }

    async loadChartData() {
        try {
            // Load spending trend data
            const spendingData = await this.app.apiRequest('/api/spending-trend');
            this.updateSpendingChart(spendingData);
            
            // Load category data
            const categoryData = await this.app.apiRequest('/api/category-breakdown');
            this.updateCategoryChart(categoryData);
            
        } catch (error) {
            console.error('Error loading chart data:', error);
        }
    }

    updateSpendingChart(data) {
        if (!this.charts.spending || !data) return;
        
        const mockData = data || {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            spending: [12000, 15000, 13500, 18000]
        };
        
        this.charts.spending.data.labels = mockData.labels;
        this.charts.spending.data.datasets[0].data = mockData.spending;
        this.charts.spending.update('active');
    }

    updateCategoryChart(data) {
        if (!this.charts.category || !data) return;
        
        const mockData = data || {
            categories: ['Food & Dining', 'Transportation', 'Shopping', 'Bills & Utilities', 'Entertainment'],
            amounts: [12500, 8200, 15600, 8700, 5000]
        };
        
        this.charts.category.data.labels = mockData.categories;
        this.charts.category.data.datasets[0].data = mockData.amounts;
        this.charts.category.update('active');
    }

    async updateChartPeriod(period) {
        try {
            // Show loading state
            const chartCard = document.querySelector('.chart-card');
            if (chartCard) {
                chartCard.classList.add('loading');
            }
            
            // Fetch data for the selected period
            const spendingData = await this.app.apiRequest(`/api/spending-trend?period=${period}`);
            this.updateSpendingChart(spendingData);
            
            // Remove loading state
            if (chartCard) {
                chartCard.classList.remove('loading');
            }
            
        } catch (error) {
            console.error('Error updating chart period:', error);
            this.app.showNotification('Failed to update chart data', 'error');
        }
    }

    async loadRecentTransactions() {
        try {
            const response = await this.app.apiRequest('/api/transactions/recent?limit=5');
            const transactions = response.transactions || response;
            this.renderRecentTransactions(transactions);
        } catch (error) {
            console.error('Error loading recent transactions:', error);
            this.showTransactionsError();
        }
    }

    showTransactionsError() {
        const container = document.getElementById('recent-transactions');
        if (container) {
            container.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Unable to load recent transactions</p>
                    <button class="btn btn-sm btn-outline-primary" onclick="app.dashboard.loadRecentTransactions()">
                        <i class="fas fa-refresh"></i> Retry
                    </button>
                </div>
            `;
        }
    }

    renderRecentTransactions(transactions) {
        const container = document.getElementById('recent-transactions');
        if (!container) return;
        
        if (!transactions || transactions.length === 0) {
            container.innerHTML = '<p class="text-center text-muted">No recent transactions</p>';
            return;
        }
        
        const html = transactions.slice(0, 5).map(transaction => `
            <div class="transaction-item">
                <div class="transaction-info">
                    <div class="transaction-icon" style="background-color: ${this.app.getCategoryColor(transaction.category)}">
                        <i class="${this.app.getCategoryIcon(transaction.category)}"></i>
                    </div>
                    <div class="transaction-details">
                        <h4>${transaction.description}</h4>
                        <p>${transaction.category} • ${this.app.formatDate(transaction.date)}</p>
                    </div>
                </div>
                <div class="transaction-amount">
                    <div class="amount ${transaction.amount < 0 ? 'negative' : 'positive'}">
                        ${transaction.amount < 0 ? '-' : '+'}${this.app.formatCurrency(Math.abs(transaction.amount))}
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }

    async loadAIInsights() {
        try {
            const response = await this.app.apiRequest('/api/insights/dashboard');
            const insights = response.insights || response;
            this.renderAIInsights(insights);
        } catch (error) {
            console.error('Error loading AI insights:', error);
            this.showInsightsError();
        }
    }

    showInsightsError() {
        const container = document.getElementById('ai-insights');
        if (container) {
            container.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Unable to load AI insights</p>
                    <button class="btn btn-sm btn-outline-primary" onclick="app.dashboard.loadAIInsights()">
                        <i class="fas fa-refresh"></i> Retry
                    </button>
                </div>
            `;
        }
    }

    updateLastRefreshTime() {
        const refreshElement = document.getElementById('last-refresh-time');
        if (refreshElement) {
            const now = new Date();
            const timeString = now.toLocaleTimeString('en-IN', {
                hour: '2-digit',
                minute: '2-digit'
            });
            refreshElement.textContent = `Last updated: ${timeString}`;
            refreshElement.style.opacity = '0.7';
            refreshElement.style.fontSize = '0.8rem';
        }
    }

    renderAIInsights(insights) {
        const container = document.getElementById('ai-insights');
        if (!container) return;
        
        if (!insights || insights.length === 0) {
            container.innerHTML = `
                <div class="no-insights">
                    <i class="fas fa-lightbulb"></i>
                    <p>No insights available. Click "Get More Insights" to generate personalized recommendations.</p>
                </div>
            `;
            return;
        }
        
        const html = insights.slice(0, 3).map(insight => `
            <div class="insight-item mini">
                <div class="insight-type">${insight.type}</div>
                <div class="insight-text">${insight.text}</div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }

    async generateMoreInsights() {
        const button = document.getElementById('get-more-insights');
        const originalText = button.innerHTML;
        
        try {
            // Show loading state
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            button.disabled = true;
            
            // Generate new insights
            const insights = await this.app.apiRequest('/api/generate-insights', 'POST');
            
            // Update insights display
            this.renderAIInsights(insights);
            
            // Show success message
            this.app.showNotification('New insights generated!', 'success');
            
        } catch (error) {
            console.error('Error generating insights:', error);
            this.app.showNotification('Failed to generate insights', 'error');
        } finally {
            // Restore button state
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }

    updateDataVisibility() {
        // Update dashboard elements based on privacy settings
        const privacySettings = this.app.privacySettings;
        
        // Hide/show summary cards based on privacy settings
        this.toggleElementVisibility('total-balance', privacySettings.balances, 'balances');
        this.toggleElementVisibility('monthly-spending', privacySettings.transactions, 'transactions');
        this.toggleElementVisibility('investment-value', privacySettings.investments, 'investments');
        
        // Update charts
        if (!privacySettings.transactions) {
            this.hideChart('spending-chart', 'transactions');
            this.hideChart('category-chart', 'transactions');
        } else {
            this.showChart('spending-chart');
            this.showChart('category-chart');
        }
        
        // Update recent transactions
        if (!privacySettings.transactions) {
            this.hideTransactions();
        } else {
            this.loadRecentTransactions();
        }
    }

    toggleElementVisibility(elementId, isVisible, category) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const card = element.closest('.summary-card');
        if (card) {
            if (isVisible) {
                card.classList.remove('privacy-hidden');
                card.classList.add('privacy-visible');
            } else {
                card.classList.add('privacy-hidden');
                card.classList.remove('privacy-visible');
            }
        }
    }

    hideChart(chartId, category) {
        const chartElement = document.getElementById(chartId);
        if (chartElement) {
            chartElement.style.display = 'none';
            const container = chartElement.closest('.card-body');
            if (container) {
                this.app.privacy.showPrivacyMessage(container, category);
            }
        }
    }

    showChart(chartId) {
        const chartElement = document.getElementById(chartId);
        if (chartElement) {
            chartElement.style.display = 'block';
            const container = chartElement.closest('.card-body');
            if (container) {
                const privacyMessage = container.querySelector('.privacy-message');
                if (privacyMessage) {
                    privacyMessage.remove();
                }
            }
        }
    }

    hideTransactions() {
        const container = document.getElementById('recent-transactions');
        if (container) {
            container.innerHTML = `
                <div class="privacy-message">
                    <div class="privacy-message-content">
                        <i class="fas fa-eye-slash"></i>
                        <h4>Transactions Hidden</h4>
                        <p>Enable transaction access in Privacy Settings to view recent transactions.</p>
                    </div>
                </div>
            `;
        }
    }

    startAutoRefresh() {
        // Refresh dashboard data every 5 minutes
        this.updateInterval = setInterval(() => {
            if (this.app.currentSection === 'dashboard') {
                this.loadData();
            }
        }, 5 * 60 * 1000);
    }

    stopAutoRefresh() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    showErrorState() {
        const summaryCards = document.querySelectorAll('.summary-card .amount');
        summaryCards.forEach(card => {
            card.textContent = 'Error loading data';
            card.style.color = 'var(--danger-color)';
        });
    }

    // Export dashboard data
    exportDashboardData() {
        const exportData = {
            summary: this.data,
            charts: {
                spending: this.charts.spending?.data,
                category: this.charts.category?.data
            },
            exportDate: new Date().toISOString()
        };

        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `dashboard-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
    }

    // Cleanup when component is destroyed
    destroy() {
        this.stopAutoRefresh();
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        this.charts = {};
    }
}

// Dashboard-specific CSS
const dashboardCSS = `
    .chart-card.loading {
        opacity: 0.6;
        pointer-events: none;
    }
    
    .chart-card.loading::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 30px;
        height: 30px;
        margin: -15px 0 0 -15px;
        border: 3px solid rgba(79, 70, 229, 0.3);
        border-top: 3px solid var(--primary-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    .insight-item.mini {
        padding: var(--spacing-md);
        margin-bottom: var(--spacing-sm);
        background: var(--bg-tertiary);
        border-radius: var(--radius-md);
        border-left: 3px solid var(--primary-color);
    }
    
    .insight-item.mini .insight-type {
        font-size: 0.7rem;
        margin-bottom: var(--spacing-xs);
    }
    
    .insight-item.mini .insight-text {
        font-size: 0.875rem;
        line-height: 1.4;
        margin-bottom: 0;
    }
    
    .no-insights {
        text-align: center;
        padding: var(--spacing-xl);
        color: var(--text-muted);
    }
    
    .no-insights i {
        font-size: 2rem;
        margin-bottom: var(--spacing-md);
        opacity: 0.5;
    }
    
    .summary-card.privacy-hidden {
        opacity: 0.3;
        filter: blur(2px);
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .transaction-item {
        animation: fadeInUp 0.3s ease;
    }
`;

const dashboardStyle = document.createElement('style');
dashboardStyle.textContent = dashboardCSS;
document.head.appendChild(dashboardStyle);