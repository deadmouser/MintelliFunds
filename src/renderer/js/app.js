// Main application controller
class FinancialAIApp {
    constructor() {
        this.currentSection = 'dashboard';
        this.isLoading = false;
        this.privacySettings = {
            transactions: true,
            balances: true,
            investments: true,
            epf: true,
            credit: true,
            assets: true
        };
        
        // Initialize the application
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.hideLoadingScreen();
        
        // Initialize components
        this.dashboard = new Dashboard(this);
        this.chat = new ChatInterface(this);
        this.privacy = new PrivacyController(this);
    }

    setupEventListeners() {
        // Sidebar navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.navigateToSection(section);
            });
        });

        // Sidebar toggle (for mobile)
        const sidebarToggle = document.getElementById('sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                document.getElementById('sidebar').classList.toggle('collapsed');
            });
        }

        // View all links
        document.querySelectorAll('.view-all').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                if (section) {
                    this.navigateToSection(section);
                }
            });
        });

        // Refresh data button
        const refreshBtn = document.getElementById('refresh-data');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshAllData();
            });
        }

        // Listen for menu events from main process
        if (window.electronAPI) {
            window.electronAPI.onShowPrivacySettings(() => {
                this.navigateToSection('privacy');
            });

            window.electronAPI.onExportData((filePath) => {
                this.exportData(filePath);
            });
        }

        // Handle keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.navigateToSection('dashboard');
                        break;
                    case '2':
                        e.preventDefault();
                        this.navigateToSection('chat');
                        break;
                    case '3':
                        e.preventDefault();
                        this.navigateToSection('transactions');
                        break;
                    case '4':
                        e.preventDefault();
                        this.navigateToSection('insights');
                        break;
                    case '5':
                        e.preventDefault();
                        this.navigateToSection('privacy');
                        break;
                }
            }
        });
    }

    navigateToSection(section) {
        if (section === this.currentSection) return;

        // Update navigation state
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Update content sections
        document.querySelectorAll('.content-section').forEach(sec => {
            sec.classList.remove('active');
        });
        document.getElementById(`${section}-section`).classList.add('active');

        this.currentSection = section;

        // Load section-specific data if needed
        this.loadSectionData(section);
    }

    async loadSectionData(section) {
        try {
            switch(section) {
                case 'dashboard':
                    await this.dashboard.loadData();
                    break;
                case 'transactions':
                    await this.loadTransactions();
                    break;
                case 'insights':
                    await this.loadInsights();
                    break;
            }
        } catch (error) {
            console.error(`Error loading ${section} data:`, error);
            this.showNotification(`Failed to load ${section} data`, 'error');
        }
    }

    async loadInitialData() {
        try {
            this.setLoading(true);
            
            // Load dashboard data by default
            if (this.dashboard) {
                await this.dashboard.loadData();
            }
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('Failed to load initial data', 'error');
        } finally {
            this.setLoading(false);
        }
    }

    async refreshAllData() {
        try {
            this.setLoading(true);
            
            // Show refresh animation
            const refreshBtn = document.getElementById('refresh-data');
            if (refreshBtn) {
                const icon = refreshBtn.querySelector('i');
                icon.classList.add('fa-spin');
            }

            // Reload current section data
            await this.loadSectionData(this.currentSection);
            
            this.showNotification('Data refreshed successfully', 'success');
            
        } catch (error) {
            console.error('Error refreshing data:', error);
            this.showNotification('Failed to refresh data', 'error');
        } finally {
            this.setLoading(false);
            
            // Remove refresh animation
            const refreshBtn = document.getElementById('refresh-data');
            if (refreshBtn) {
                const icon = refreshBtn.querySelector('i');
                icon.classList.remove('fa-spin');
            }
        }
    }

    async loadTransactions() {
        const container = document.getElementById('transactions-list');
        if (!container) return;

        try {
            const transactions = await this.apiRequest('/api/transactions');
            this.renderTransactions(transactions, container);
        } catch (error) {
            console.error('Error loading transactions:', error);
            container.innerHTML = '<p class="text-center text-muted">Failed to load transactions</p>';
        }
    }

    async loadInsights() {
        const container = document.getElementById('insights-list');
        if (!container) return;

        try {
            const insights = await this.apiRequest('/api/insights');
            this.renderInsights(insights, container);
        } catch (error) {
            console.error('Error loading insights:', error);
            container.innerHTML = '<p class="text-center text-muted">Failed to load insights</p>';
        }
    }

    renderTransactions(transactions, container) {
        if (!transactions || transactions.length === 0) {
            container.innerHTML = '<p class="text-center text-muted">No transactions found</p>';
            return;
        }

        const html = transactions.map(transaction => `
            <div class="transaction-item">
                <div class="transaction-info">
                    <div class="transaction-icon" style="background-color: ${this.getCategoryColor(transaction.category)}">
                        <i class="${this.getCategoryIcon(transaction.category)}"></i>
                    </div>
                    <div class="transaction-details">
                        <h4>${transaction.description}</h4>
                        <p>${transaction.category} • ${transaction.account}</p>
                    </div>
                </div>
                <div class="transaction-amount">
                    <div class="amount ${transaction.amount < 0 ? 'negative' : 'positive'}">
                        ${window.electronAPI?.formatCurrency(Math.abs(transaction.amount)) || `₹${Math.abs(transaction.amount)}`}
                    </div>
                    <div class="date">${this.formatDate(transaction.date)}</div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    renderInsights(insights, container) {
        if (!insights || insights.length === 0) {
            container.innerHTML = '<p class="text-center text-muted">No insights available</p>';
            return;
        }

        const html = insights.map(insight => `
            <div class="insight-item">
                <div class="insight-type">${insight.type}</div>
                <div class="insight-text">${insight.text}</div>
                <div class="insight-actions">
                    <button class="btn btn-primary btn-sm" onclick="app.handleInsightAction('${insight.id}', 'view')">
                        <i class="fas fa-eye"></i>
                        View Details
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    getCategoryColor(category) {
        const colors = {
            'food': '#f59e0b',
            'transport': '#3b82f6',
            'shopping': '#8b5cf6',
            'bills': '#ef4444',
            'entertainment': '#10b981',
            'health': '#f97316',
            'education': '#6366f1',
            'investment': '#059669',
            'salary': '#10b981',
            'default': '#6b7280'
        };
        return colors[category?.toLowerCase()] || colors.default;
    }

    getCategoryIcon(category) {
        const icons = {
            'food': 'fas fa-utensils',
            'transport': 'fas fa-car',
            'shopping': 'fas fa-shopping-bag',
            'bills': 'fas fa-file-invoice-dollar',
            'entertainment': 'fas fa-film',
            'health': 'fas fa-heartbeat',
            'education': 'fas fa-graduation-cap',
            'investment': 'fas fa-chart-line',
            'salary': 'fas fa-money-bill-wave',
            'default': 'fas fa-circle'
        };
        return icons[category?.toLowerCase()] || icons.default;
    }

    async handleInsightAction(insightId, action) {
        try {
            switch(action) {
                case 'view':
                    // Implementation for viewing insight details
                    this.showNotification('Insight details opened', 'info');
                    break;
                case 'dismiss':
                    // Implementation for dismissing insights
                    this.showNotification('Insight dismissed', 'info');
                    break;
            }
        } catch (error) {
            console.error('Error handling insight action:', error);
            this.showNotification('Failed to handle insight action', 'error');
        }
    }

    async apiRequest(endpoint, method = 'GET', data = null) {
        if (window.electronAPI) {
            const response = await window.electronAPI.makeAPIRequest(endpoint, method, data);
            if (response.success) {
                return response.data;
            } else {
                throw new Error(response.error);
            }
        } else {
            // Fallback for development without Electron
            return this.getMockData(endpoint);
        }
    }

    getMockData(endpoint) {
        // Mock data for development
        const mockData = {
            '/api/dashboard': {
                totalBalance: 125000,
                monthlySpending: 45000,
                savingsProgress: 30000,
                savingsGoal: 100000,
                investmentValue: 85000,
                balanceChange: 8.5,
                spendingChange: -12.3,
                investmentChange: 15.2
            },
            '/api/transactions': [
                {
                    id: '1',
                    description: 'Grocery Shopping',
                    category: 'food',
                    account: 'HDFC Savings',
                    amount: -2500,
                    date: '2024-09-12T10:30:00Z'
                },
                {
                    id: '2',
                    description: 'Salary Credit',
                    category: 'salary',
                    account: 'HDFC Savings',
                    amount: 75000,
                    date: '2024-09-01T00:00:00Z'
                },
                {
                    id: '3',
                    description: 'Uber Ride',
                    category: 'transport',
                    account: 'HDFC Savings',
                    amount: -350,
                    date: '2024-09-11T18:45:00Z'
                }
            ],
            '/api/insights': [
                {
                    id: '1',
                    type: 'Spending Alert',
                    text: 'Your food expenses have increased by 25% this month compared to last month. Consider reviewing your dining habits.'
                },
                {
                    id: '2',
                    type: 'Savings Opportunity',
                    text: 'You could save ₹3,000 monthly by switching to a different mobile plan and canceling unused subscriptions.'
                }
            ]
        };

        return mockData[endpoint] || {};
    }

    setLoading(loading) {
        this.isLoading = loading;
        // Update UI loading states as needed
    }

    hideLoadingScreen() {
        setTimeout(() => {
            const loadingScreen = document.getElementById('loading-screen');
            if (loadingScreen) {
                loadingScreen.classList.add('hidden');
                setTimeout(() => {
                    loadingScreen.remove();
                }, 350);
            }
        }, 1000);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#3b82f6'};
            color: white;
            border-radius: 8px;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;

        // Add to DOM
        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    async exportData(filePath) {
        try {
            // Gather all data for export
            const exportData = {
                dashboard: await this.apiRequest('/api/dashboard'),
                transactions: await this.apiRequest('/api/transactions'),
                insights: await this.apiRequest('/api/insights'),
                privacySettings: this.privacySettings,
                exportDate: new Date().toISOString()
            };

            // In a real implementation, you would write this to the specified file
            console.log('Exporting data to:', filePath, exportData);
            this.showNotification('Data exported successfully', 'success');

        } catch (error) {
            console.error('Export error:', error);
            this.showNotification('Failed to export data', 'error');
        }
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            month: 'short',
            day: 'numeric'
        });
    }

    formatCurrency(amount) {
        if (window.electronAPI?.formatCurrency) {
            return window.electronAPI.formatCurrency(amount);
        }
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    }
}

// Add CSS for notifications
const notificationCSS = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;

const style = document.createElement('style');
style.textContent = notificationCSS;
document.head.appendChild(style);

// Initialize the application when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new FinancialAIApp();
});

// Make app available globally for debugging
window.app = app;