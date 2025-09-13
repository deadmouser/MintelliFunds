// API Service Layer for Backend Integration
class APIService {
    constructor() {
        this.baseURL = 'http://localhost:3001'; // Your backend API URL
        this.authToken = null;
        this.retryCount = 3;
        this.timeout = 10000; // 10 seconds
        
        this.init();
    }

    init() {
        this.loadAuthToken();
        this.setupRequestInterceptors();
    }

    loadAuthToken() {
        try {
            const token = localStorage.getItem('financial-ai-auth-token');
            if (token) {
                this.authToken = token;
            }
        } catch (error) {
            console.error('Error loading auth token:', error);
        }
    }

    saveAuthToken(token) {
        try {
            this.authToken = token;
            localStorage.setItem('financial-ai-auth-token', token);
        } catch (error) {
            console.error('Error saving auth token:', error);
        }
    }

    clearAuthToken() {
        this.authToken = null;
        localStorage.removeItem('financial-ai-auth-token');
    }

    setupRequestInterceptors() {
        // Add any global request/response interceptors here
        // This could include authentication, logging, error handling, etc.
    }

    async makeRequest(endpoint, options = {}) {
        const {
            method = 'GET',
            data = null,
            headers = {},
            timeout = this.timeout,
            retries = this.retryCount
        } = options;

        const url = `${this.baseURL}${endpoint}`;
        
        const requestOptions = {
            method,
            headers: {
                'Content-Type': 'application/json',
                ...headers
            }
        };

        // Add authentication header
        if (this.authToken) {
            requestOptions.headers['Authorization'] = `Bearer ${this.authToken}`;
        }

        // Add request body for non-GET requests
        if (data && method !== 'GET') {
            requestOptions.body = JSON.stringify(data);
        }

        // Create abort controller for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        requestOptions.signal = controller.signal;

        try {
            const response = await this.executeWithRetry(url, requestOptions, retries);
            clearTimeout(timeoutId);
            return await this.handleResponse(response);
        } catch (error) {
            clearTimeout(timeoutId);
            throw this.handleError(error);
        }
    }

    async executeWithRetry(url, options, retries) {
        let lastError;
        
        for (let i = 0; i <= retries; i++) {
            try {
                return await fetch(url, options);
            } catch (error) {
                lastError = error;
                
                // Don't retry for certain error types
                if (error.name === 'AbortError' || error.status === 401) {
                    throw error;
                }
                
                // Wait before retrying (exponential backoff)
                if (i < retries) {
                    await this.delay(Math.pow(2, i) * 1000);
                }
            }
        }
        
        throw lastError;
    }

    async handleResponse(response) {
        if (!response.ok) {
            const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
            error.status = response.status;
            error.response = response;
            
            // Handle specific error codes
            if (response.status === 401) {
                this.clearAuthToken();
                // Redirect to login or show auth dialog
                this.handleUnauthorized();
            }
            
            throw error;
        }

        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return await response.text();
    }

    handleError(error) {
        console.error('API Request Error:', error);
        
        if (error.name === 'AbortError') {
            return new Error('Request timeout');
        }
        
        if (error.status) {
            switch (error.status) {
                case 400:
                    return new Error('Bad request - please check your input');
                case 401:
                    return new Error('Unauthorized - please log in again');
                case 403:
                    return new Error('Access forbidden');
                case 404:
                    return new Error('Resource not found');
                case 429:
                    return new Error('Too many requests - please try again later');
                case 500:
                    return new Error('Internal server error - please try again');
                default:
                    return new Error(`Server error: ${error.message}`);
            }
        }
        
        if (!navigator.onLine) {
            return new Error('No internet connection');
        }
        
        return error;
    }

    handleUnauthorized() {
        // Implement authentication flow
        // This could show a login modal or redirect to login page
        console.log('User unauthorized - implement auth flow');
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Dashboard API endpoints
    async getDashboardData() {
        return await this.makeRequest('/api/dashboard');
    }

    async getSpendingTrend(period = '1m') {
        return await this.makeRequest(`/api/spending-trend?period=${period}`);
    }

    async getCategoryBreakdown() {
        return await this.makeRequest('/api/category-breakdown');
    }

    async getRecentTransactions(limit = 10) {
        return await this.makeRequest(`/api/transactions/recent?limit=${limit}`);
    }

    async getDashboardInsights() {
        return await this.makeRequest('/api/insights/dashboard');
    }

    async generateInsights() {
        return await this.makeRequest('/api/insights/generate', { method: 'POST' });
    }

    // Transaction API endpoints
    async getTransactions(filters = {}) {
        const queryParams = new URLSearchParams(filters).toString();
        return await this.makeRequest(`/api/transactions?${queryParams}`);
    }

    async getTransactionById(id) {
        return await this.makeRequest(`/api/transactions/${id}`);
    }

    async createTransaction(transactionData) {
        return await this.makeRequest('/api/transactions', {
            method: 'POST',
            data: transactionData
        });
    }

    async updateTransaction(id, transactionData) {
        return await this.makeRequest(`/api/transactions/${id}`, {
            method: 'PUT',
            data: transactionData
        });
    }

    async deleteTransaction(id) {
        return await this.makeRequest(`/api/transactions/${id}`, {
            method: 'DELETE'
        });
    }

    // AI Chat API endpoints
    async sendChatMessage(message, context = {}) {
        return await this.makeRequest('/api/chat', {
            method: 'POST',
            data: { message, context }
        });
    }

    async getChatHistory(limit = 50) {
        return await this.makeRequest(`/api/chat/history?limit=${limit}`);
    }

    async clearChatHistory() {
        return await this.makeRequest('/api/chat/history', {
            method: 'DELETE'
        });
    }

    // Privacy API endpoints
    async getPrivacySettings() {
        return await this.makeRequest('/api/privacy/settings');
    }

    async updatePrivacySettings(settings) {
        return await this.makeRequest('/api/privacy/settings', {
            method: 'PUT',
            data: settings
        });
    }

    async getDataCategories() {
        return await this.makeRequest('/api/privacy/categories');
    }

    async requestDataDeletion(categories) {
        return await this.makeRequest('/api/privacy/delete', {
            method: 'POST',
            data: { categories }
        });
    }

    // Account/Profile API endpoints
    async getUserProfile() {
        return await this.makeRequest('/api/user/profile');
    }

    async updateUserProfile(profileData) {
        return await this.makeRequest('/api/user/profile', {
            method: 'PUT',
            data: profileData
        });
    }

    async getAccountSettings() {
        return await this.makeRequest('/api/user/settings');
    }

    async updateAccountSettings(settings) {
        return await this.makeRequest('/api/user/settings', {
            method: 'PUT',
            data: settings
        });
    }

    // Financial Data API endpoints
    async getAccounts() {
        return await this.makeRequest('/api/accounts');
    }

    async getAccountBalance(accountId) {
        return await this.makeRequest(`/api/accounts/${accountId}/balance`);
    }

    async getInvestments() {
        return await this.makeRequest('/api/investments');
    }

    async getInvestmentPerformance(investmentId) {
        return await this.makeRequest(`/api/investments/${investmentId}/performance`);
    }

    async getAssets() {
        return await this.makeRequest('/api/assets');
    }

    async getLiabilities() {
        return await this.makeRequest('/api/liabilities');
    }

    async getNetWorth() {
        return await this.makeRequest('/api/net-worth');
    }

    async getCreditScore() {
        return await this.makeRequest('/api/credit-score');
    }

    async getEPFDetails() {
        return await this.makeRequest('/api/epf');
    }

    // Budget API endpoints
    async getBudgets() {
        return await this.makeRequest('/api/budgets');
    }

    async createBudget(budgetData) {
        return await this.makeRequest('/api/budgets', {
            method: 'POST',
            data: budgetData
        });
    }

    async updateBudget(budgetId, budgetData) {
        return await this.makeRequest(`/api/budgets/${budgetId}`, {
            method: 'PUT',
            data: budgetData
        });
    }

    async deleteBudget(budgetId) {
        return await this.makeRequest(`/api/budgets/${budgetId}`, {
            method: 'DELETE'
        });
    }

    // Analytics API endpoints
    async getSpendingAnalytics(period = '1m') {
        return await this.makeRequest(`/api/analytics/spending?period=${period}`);
    }

    async getIncomeAnalytics(period = '1m') {
        return await this.makeRequest(`/api/analytics/income?period=${period}`);
    }

    async getSavingsAnalytics() {
        return await this.makeRequest('/api/analytics/savings');
    }

    async getInvestmentAnalytics() {
        return await this.makeRequest('/api/analytics/investments');
    }

    // Export API endpoints
    async exportData(format = 'json', categories = []) {
        return await this.makeRequest('/api/export', {
            method: 'POST',
            data: { format, categories }
        });
    }

    async getExportHistory() {
        return await this.makeRequest('/api/export/history');
    }

    // Notification API endpoints
    async getNotifications() {
        return await this.makeRequest('/api/notifications');
    }

    async markNotificationRead(notificationId) {
        return await this.makeRequest(`/api/notifications/${notificationId}/read`, {
            method: 'PUT'
        });
    }

    async getNotificationSettings() {
        return await this.makeRequest('/api/notifications/settings');
    }

    async updateNotificationSettings(settings) {
        return await this.makeRequest('/api/notifications/settings', {
            method: 'PUT',
            data: settings
        });
    }

    // Health check
    async healthCheck() {
        return await this.makeRequest('/api/health');
    }

    // Mock data fallback (for development without backend)
    getMockData(endpoint) {
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
            '/api/spending-trend': {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                spending: [12000, 15000, 13500, 18000]
            },
            '/api/category-breakdown': {
                categories: ['Food & Dining', 'Transportation', 'Shopping', 'Bills & Utilities', 'Entertainment'],
                amounts: [12500, 8200, 15600, 8700, 5000]
            },
            '/api/transactions/recent': [
                {
                    id: '1',
                    description: 'Grocery Shopping',
                    category: 'food',
                    account: 'HDFC Savings',
                    amount: -2500,
                    date: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
                },
                {
                    id: '2',
                    description: 'Salary Credit',
                    category: 'salary',
                    account: 'HDFC Savings',
                    amount: 75000,
                    date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
                },
                {
                    id: '3',
                    description: 'Uber Ride',
                    category: 'transport',
                    account: 'HDFC Savings',
                    amount: -350,
                    date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
                }
            ],
            '/api/insights/dashboard': [
                {
                    id: '1',
                    type: 'Spending Alert',
                    text: 'Your food expenses have increased by 25% this month.'
                },
                {
                    id: '2',
                    type: 'Savings Opportunity',
                    text: 'You could save ₹3,000 monthly by optimizing subscriptions.'
                }
            ]
        };

        // Handle parameterized endpoints
        if (endpoint.includes('/api/spending-trend?period=')) {
            return mockData['/api/spending-trend'];
        }
        if (endpoint.includes('/api/transactions/recent?limit=')) {
            return mockData['/api/transactions/recent'];
        }

        return mockData[endpoint] || { message: 'Mock data not available for ' + endpoint };
    }

    // Development mode check
    isDevelopmentMode() {
        return !window.electronAPI || process.env.NODE_ENV === 'development';
    }
}

// Create global API service instance
const apiService = new APIService();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIService;
} else {
    window.apiService = apiService;
}