// Enhanced Chart Visualizations
class EnhancedCharts {
    constructor(app) {
        this.app = app;
        this.charts = {};
        this.chartColors = {
            primary: '#4F46E5',
            secondary: '#10B981',
            accent: '#F59E0B',
            danger: '#EF4444',
            warning: '#F97316',
            info: '#3B82F6',
            success: '#22C55E',
            gradients: {
                blue: ['#4F46E5', '#7C3AED'],
                green: ['#10B981', '#059669'],
                orange: ['#F59E0B', '#D97706'],
                red: ['#EF4444', '#DC2626']
            }
        };
        this.init();
    }

    init() {
        this.createAdvancedSpendingChart();
        this.createEnhancedCategoryChart();
        this.createBudgetProgressChart();
        this.createSavingsGoalChart();
        this.createIncomeExpenseChart();
        this.createInvestmentPerformanceChart();
        this.setupChartInteractions();
    }

    createAdvancedSpendingChart() {
        const ctx = document.getElementById('spending-chart');
        if (!ctx) return;

        // Generate realistic spending data
        const spendingData = this.generateSpendingTrendData();
        
        this.charts.spending = new Chart(ctx, {
            type: 'line',
            data: {
                labels: spendingData.labels,
                datasets: [{
                    label: 'Daily Spending',
                    data: spendingData.daily,
                    borderColor: this.chartColors.primary,
                    backgroundColor: this.createGradient(ctx, this.chartColors.gradients.blue),
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#FFFFFF',
                    pointBorderColor: this.chartColors.primary,
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 8,
                }, {
                    label: 'Budget Limit',
                    data: spendingData.budget,
                    borderColor: this.chartColors.danger,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                    pointHoverRadius: 0
                }, {
                    label: '7-Day Average',
                    data: spendingData.average,
                    borderColor: this.chartColors.secondary,
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    fill: false,
                    pointRadius: 3,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                size: 12,
                                weight: '500'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        titleColor: '#FFFFFF',
                        bodyColor: '#FFFFFF',
                        borderColor: this.chartColors.primary,
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: true,
                        callbacks: {
                            title: (context) => {
                                return `${context[0].label}`;
                            },
                            label: (context) => {
                                const value = this.app.formatCurrency(context.parsed.y);
                                return `${context.dataset.label}: ${value}`;
                            },
                            afterBody: (context) => {
                                const currentSpending = context[0].parsed.y;
                                const budget = spendingData.budget[context[0].dataIndex];
                                const percentage = ((currentSpending / budget) * 100).toFixed(1);
                                return [`Budget Usage: ${percentage}%`];
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 11
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            callback: (value) => this.app.formatCurrency(value),
                            font: {
                                size: 11
                            }
                        }
                    }
                },
                elements: {
                    point: {
                        hoverBorderWidth: 3
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeInOutCubic'
                }
            }
        });
    }

    createEnhancedCategoryChart() {
        const ctx = document.getElementById('category-chart');
        if (!ctx) return;

        const categoryData = this.generateCategoryData();
        
        this.charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: categoryData.labels,
                datasets: [{
                    data: categoryData.amounts,
                    backgroundColor: [
                        this.chartColors.primary,
                        this.chartColors.secondary,
                        this.chartColors.accent,
                        this.chartColors.danger,
                        this.chartColors.warning,
                        this.chartColors.info
                    ],
                    borderWidth: 3,
                    borderColor: '#FFFFFF',
                    hoverBorderWidth: 4,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12,
                                weight: '500'
                            },
                            generateLabels: (chart) => {
                                const data = chart.data;
                                const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                
                                return data.labels.map((label, i) => {
                                    const value = data.datasets[0].data[i];
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return {
                                        text: `${label} (${percentage}%)`,
                                        fillStyle: data.datasets[0].backgroundColor[i],
                                        hidden: false,
                                        index: i,
                                        pointStyle: 'circle'
                                    };
                                });
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        titleColor: '#FFFFFF',
                        bodyColor: '#FFFFFF',
                        borderColor: this.chartColors.primary,
                        borderWidth: 1,
                        cornerRadius: 8,
                        callbacks: {
                            label: (context) => {
                                const value = this.app.formatCurrency(context.parsed);
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutCubic'
                }
            }
        });

        // Add center text
        this.addCenterText(ctx, categoryData);
    }

    createBudgetProgressChart() {
        const budgetContainer = document.querySelector('.budget-progress-container');
        if (!budgetContainer) {
            this.createBudgetProgressContainer();
        }

        const budgetData = this.generateBudgetData();
        this.renderBudgetProgress(budgetData);
    }

    createSavingsGoalChart() {
        const savingsContainer = document.querySelector('.savings-goal-container');
        if (!savingsContainer) {
            this.createSavingsGoalContainer();
        }

        const savingsData = this.generateSavingsData();
        this.renderSavingsGoal(savingsData);
    }

    createIncomeExpenseChart() {
        // Add income vs expense comparison chart
        const dashboardGrid = document.querySelector('.dashboard-grid');
        if (dashboardGrid && !document.getElementById('income-expense-chart')) {
            const chartCard = this.createChartCard('income-expense-chart', 'Income vs Expenses');
            dashboardGrid.appendChild(chartCard);

            const ctx = document.getElementById('income-expense-chart');
            const incomeExpenseData = this.generateIncomeExpenseData();

            this.charts.incomeExpense = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: incomeExpenseData.labels,
                    datasets: [{
                        label: 'Income',
                        data: incomeExpenseData.income,
                        backgroundColor: this.createGradient(ctx, this.chartColors.gradients.green),
                        borderColor: this.chartColors.secondary,
                        borderWidth: 2,
                        borderRadius: 8,
                        borderSkipped: false
                    }, {
                        label: 'Expenses',
                        data: incomeExpenseData.expenses,
                        backgroundColor: this.createGradient(ctx, this.chartColors.gradients.red),
                        borderColor: this.chartColors.danger,
                        borderWidth: 2,
                        borderRadius: 8,
                        borderSkipped: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                usePointStyle: true,
                                padding: 15
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.9)',
                            callbacks: {
                                label: (context) => {
                                    const value = this.app.formatCurrency(context.parsed.y);
                                    return `${context.dataset.label}: ${value}`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: (value) => this.app.formatCurrency(value)
                            }
                        }
                    },
                    animation: {
                        duration: 1500,
                        easing: 'easeInOutBack'
                    }
                }
            });
        }
    }

    createInvestmentPerformanceChart() {
        // Add investment performance tracking
        const dashboardGrid = document.querySelector('.dashboard-grid');
        if (dashboardGrid && !document.getElementById('investment-chart')) {
            const chartCard = this.createChartCard('investment-chart', 'Investment Performance');
            dashboardGrid.appendChild(chartCard);

            const ctx = document.getElementById('investment-chart');
            const investmentData = this.generateInvestmentData();

            this.charts.investment = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: investmentData.labels,
                    datasets: [{
                        label: 'Portfolio Value',
                        data: investmentData.values,
                        borderColor: this.chartColors.accent,
                        backgroundColor: this.createGradient(ctx, this.chartColors.gradients.orange),
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#FFFFFF',
                        pointBorderColor: this.chartColors.accent,
                        pointBorderWidth: 2,
                        pointRadius: 4
                    }, {
                        label: 'Invested Amount',
                        data: investmentData.invested,
                        borderColor: this.chartColors.info,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        borderDash: [3, 3],
                        fill: false,
                        pointRadius: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                usePointStyle: true,
                                padding: 15
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.9)',
                            callbacks: {
                                label: (context) => {
                                    const value = this.app.formatCurrency(context.parsed.y);
                                    return `${context.dataset.label}: ${value}`;
                                },
                                afterBody: (context) => {
                                    const current = context[0].parsed.y;
                                    const invested = investmentData.invested[context[0].dataIndex];
                                    const gain = current - invested;
                                    const percentage = ((gain / invested) * 100).toFixed(1);
                                    return [`Gain/Loss: ${this.app.formatCurrency(gain)} (${percentage}%)`];
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: (value) => this.app.formatCurrency(value)
                            }
                        }
                    },
                    animation: {
                        duration: 1800,
                        easing: 'easeInOutQuart'
                    }
                }
            });
        }
    }

    // Data generation methods
    generateSpendingTrendData() {
        const days = 30;
        const labels = [];
        const daily = [];
        const budget = [];
        const average = [];

        for (let i = days - 1; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }));

            const baseSpending = 1200;
            const variation = Math.random() * 800 - 400;
            const weekendBonus = date.getDay() === 0 || date.getDay() === 6 ? 300 : 0;
            
            daily.push(Math.max(0, baseSpending + variation + weekendBonus));
            budget.push(1500);
        }

        // Calculate 7-day moving average
        for (let i = 0; i < daily.length; i++) {
            const start = Math.max(0, i - 6);
            const slice = daily.slice(start, i + 1);
            const avg = slice.reduce((a, b) => a + b, 0) / slice.length;
            average.push(avg);
        }

        return { labels, daily, budget, average };
    }

    generateCategoryData() {
        return {
            labels: ['Food & Dining', 'Transportation', 'Shopping', 'Bills & Utilities', 'Entertainment', 'Healthcare'],
            amounts: [12500, 8200, 15600, 8700, 5400, 3200]
        };
    }

    generateBudgetData() {
        return [
            { category: 'Food', spent: 12500, budget: 15000, color: this.chartColors.primary },
            { category: 'Transport', spent: 8200, budget: 10000, color: this.chartColors.secondary },
            { category: 'Shopping', spent: 15600, budget: 12000, color: this.chartColors.danger },
            { category: 'Bills', spent: 8700, budget: 9000, color: this.chartColors.accent },
            { category: 'Entertainment', spent: 5400, budget: 8000, color: this.chartColors.info }
        ];
    }

    generateSavingsData() {
        return {
            current: 75000,
            target: 100000,
            monthly: 12000,
            months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            progress: [15000, 28000, 41000, 53000, 62000, 75000]
        };
    }

    generateIncomeExpenseData() {
        return {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            income: [85000, 87000, 90000, 88000, 92000, 95000],
            expenses: [65000, 72000, 68000, 75000, 71000, 73000]
        };
    }

    generateInvestmentData() {
        const months = 12;
        const labels = [];
        const values = [];
        const invested = [];
        
        let currentValue = 50000;
        let currentInvested = 50000;

        for (let i = 0; i < months; i++) {
            const date = new Date();
            date.setMonth(date.getMonth() - (months - 1 - i));
            labels.push(date.toLocaleDateString('en-IN', { month: 'short' }));

            // Simulate monthly investment and market growth
            currentInvested += 10000; // Monthly SIP
            currentValue = currentInvested * (0.95 + Math.random() * 0.3); // Market fluctuation

            values.push(Math.round(currentValue));
            invested.push(currentInvested);
        }

        return { labels, values, invested };
    }

    // Helper methods
    createGradient(ctx, colors) {
        const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, colors[0] + '80');
        gradient.addColorStop(1, colors[1] + '20');
        return gradient;
    }

    createChartCard(chartId, title) {
        const card = document.createElement('div');
        card.className = 'card chart-card';
        card.innerHTML = `
            <div class="card-header">
                <h3>${title}</h3>
            </div>
            <div class="card-body">
                <canvas id="${chartId}"></canvas>
            </div>
        `;
        return card;
    }

    addCenterText(ctx, data) {
        const total = data.amounts.reduce((a, b) => a + b, 0);
        const chart = this.charts.category;
        
        Chart.register({
            id: 'centerText',
            beforeDraw: (chart) => {
                const ctx = chart.ctx;
                const centerX = chart.chartArea.left + (chart.chartArea.right - chart.chartArea.left) / 2;
                const centerY = chart.chartArea.top + (chart.chartArea.bottom - chart.chartArea.top) / 2;
                
                ctx.save();
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.font = 'bold 18px Inter';
                ctx.fillStyle = '#1F2937';
                ctx.fillText('Total', centerX, centerY - 10);
                ctx.font = '14px Inter';
                ctx.fillText(this.app.formatCurrency(total), centerX, centerY + 10);
                ctx.restore();
            }
        });
    }

    createBudgetProgressContainer() {
        const dashboardGrid = document.querySelector('.dashboard-grid');
        if (dashboardGrid) {
            const container = document.createElement('div');
            container.className = 'card budget-progress-container';
            container.innerHTML = `
                <div class="card-header">
                    <h3>Budget Progress</h3>
                </div>
                <div class="card-body">
                    <div class="budget-items"></div>
                </div>
            `;
            dashboardGrid.appendChild(container);
        }
    }

    createSavingsGoalContainer() {
        const dashboardGrid = document.querySelector('.dashboard-grid');
        if (dashboardGrid) {
            const container = document.createElement('div');
            container.className = 'card savings-goal-container';
            container.innerHTML = `
                <div class="card-header">
                    <h3>Savings Goal</h3>
                </div>
                <div class="card-body">
                    <div class="savings-progress"></div>
                </div>
            `;
            dashboardGrid.appendChild(container);
        }
    }

    renderBudgetProgress(budgetData) {
        const container = document.querySelector('.budget-items');
        if (!container) return;

        container.innerHTML = budgetData.map(item => {
            const percentage = (item.spent / item.budget) * 100;
            const isOverBudget = percentage > 100;
            
            return `
                <div class="budget-item">
                    <div class="budget-header">
                        <span class="budget-category">${item.category}</span>
                        <span class="budget-amount ${isOverBudget ? 'over-budget' : ''}">
                            ${this.app.formatCurrency(item.spent)} / ${this.app.formatCurrency(item.budget)}
                        </span>
                    </div>
                    <div class="budget-progress-bar">
                        <div class="budget-progress-fill ${isOverBudget ? 'over-budget' : ''}" 
                             style="width: ${Math.min(percentage, 100)}%; background-color: ${item.color}">
                        </div>
                        ${isOverBudget ? `<div class="budget-overflow" style="width: ${percentage - 100}%"></div>` : ''}
                    </div>
                    <div class="budget-percentage ${isOverBudget ? 'over-budget' : ''}">
                        ${percentage.toFixed(1)}% ${isOverBudget ? 'over budget' : 'used'}
                    </div>
                </div>
            `;
        }).join('');
    }

    renderSavingsGoal(savingsData) {
        const container = document.querySelector('.savings-progress');
        if (!container) return;

        const percentage = (savingsData.current / savingsData.target) * 100;
        const remaining = savingsData.target - savingsData.current;

        container.innerHTML = `
            <div class="savings-summary">
                <div class="savings-current">
                    <span class="savings-label">Current Savings</span>
                    <span class="savings-value">${this.app.formatCurrency(savingsData.current)}</span>
                </div>
                <div class="savings-target">
                    <span class="savings-label">Target</span>
                    <span class="savings-value">${this.app.formatCurrency(savingsData.target)}</span>
                </div>
            </div>
            <div class="savings-progress-bar">
                <div class="savings-progress-fill" style="width: ${percentage}%"></div>
            </div>
            <div class="savings-details">
                <span class="savings-percentage">${percentage.toFixed(1)}% Complete</span>
                <span class="savings-remaining">${this.app.formatCurrency(remaining)} remaining</span>
            </div>
            <div class="savings-chart">
                <canvas id="savings-trend-chart"></canvas>
            </div>
        `;

        // Create mini savings trend chart
        setTimeout(() => this.createSavingsTrendChart(savingsData), 100);
    }

    createSavingsTrendChart(savingsData) {
        const ctx = document.getElementById('savings-trend-chart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: savingsData.months,
                datasets: [{
                    data: savingsData.progress,
                    borderColor: this.chartColors.secondary,
                    backgroundColor: this.createGradient(ctx, this.chartColors.gradients.green),
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => this.app.formatCurrency(context.parsed.y)
                        }
                    }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                elements: {
                    point: { hoverRadius: 6 }
                }
            }
        });
    }

    setupChartInteractions() {
        // Add chart period selector functionality
        const periodSelector = document.getElementById('chart-period');
        if (periodSelector) {
            periodSelector.addEventListener('change', (e) => {
                this.updateChartPeriod(e.target.value);
            });
        }

        // Add chart export functionality
        this.addChartExportButtons();
    }

    updateChartPeriod(period) {
        if (this.charts.spending) {
            const newData = this.generateSpendingTrendData(period);
            this.charts.spending.data.labels = newData.labels;
            this.charts.spending.data.datasets[0].data = newData.daily;
            this.charts.spending.data.datasets[1].data = newData.budget;
            this.charts.spending.data.datasets[2].data = newData.average;
            this.charts.spending.update('active');
        }
    }

    addChartExportButtons() {
        document.querySelectorAll('.chart-card .card-header').forEach(header => {
            if (!header.querySelector('.chart-export-btn')) {
                const exportBtn = document.createElement('button');
                exportBtn.className = 'chart-export-btn btn-icon';
                exportBtn.innerHTML = '<i class="fas fa-download"></i>';
                exportBtn.title = 'Export Chart';
                exportBtn.addEventListener('click', (e) => {
                    const canvas = header.parentElement.querySelector('canvas');
                    if (canvas) {
                        this.exportChart(canvas);
                    }
                });
                header.appendChild(exportBtn);
            }
        });
    }

    exportChart(canvas) {
        const link = document.createElement('a');
        link.download = `financial-chart-${Date.now()}.png`;
        link.href = canvas.toDataURL('image/png');
        link.click();
    }

    // Public methods for updating charts with real data
    updateSpendingChart(data) {
        if (this.charts.spending && data) {
            this.charts.spending.data.labels = data.labels;
            this.charts.spending.data.datasets[0].data = data.values;
            this.charts.spending.update();
        }
    }

    updateCategoryChart(data) {
        if (this.charts.category && data) {
            this.charts.category.data.labels = data.labels;
            this.charts.category.data.datasets[0].data = data.values;
            this.charts.category.update();
        }
    }

    // Cleanup method
    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        this.charts = {};
    }
}

// Export for use in main app
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedCharts;
}