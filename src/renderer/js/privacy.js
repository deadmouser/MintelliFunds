// Privacy Controller for Data Access Management
class PrivacyController {
    constructor(app) {
        this.app = app;
        this.settings = {
            transactions: true,
            balances: true,
            investments: true,
            epf: true,
            credit: true,
            assets: true
        };
        
        this.init();
    }

    init() {
        this.loadPrivacySettings();
        this.setupEventListeners();
        this.updatePrivacyStatus();
    }

    setupEventListeners() {
        // Toggle switches
        const toggles = document.querySelectorAll('.privacy-toggle input[type="checkbox"]');
        toggles.forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                this.handleToggleChange(e.target);
            });
        });

        // Privacy status indicator
        this.updatePrivacyStatusIndicator();
    }

    async handleToggleChange(toggle) {
        const category = this.getCategoryFromToggleId(toggle.id);
        const isEnabled = toggle.checked;
        
        try {
            // Show loading state
            this.setToggleLoading(toggle, true);
            
            // Update local settings
            this.settings[category] = isEnabled;
            
            // Sync with main process and backend
            await this.syncPrivacySettings();
            
            // Update UI
            this.updatePrivacyStatus();
            this.updateDataVisibility(category, isEnabled);
            
            // Show notification
            const action = isEnabled ? 'enabled' : 'disabled';
            const categoryName = this.getCategoryDisplayName(category);
            this.app.showNotification(`${categoryName} access ${action}`, 'info');
            
        } catch (error) {
            console.error('Error updating privacy setting:', error);
            
            // Revert toggle state
            toggle.checked = !isEnabled;
            this.settings[category] = !isEnabled;
            
            this.app.showNotification('Failed to update privacy setting', 'error');
        } finally {
            this.setToggleLoading(toggle, false);
        }
    }

    getCategoryFromToggleId(toggleId) {
        const idMap = {
            'transactions-toggle': 'transactions',
            'balances-toggle': 'balances',
            'investments-toggle': 'investments',
            'epf-toggle': 'epf',
            'credit-toggle': 'credit',
            'assets-toggle': 'assets'
        };
        return idMap[toggleId] || toggleId.replace('-toggle', '');
    }

    getCategoryDisplayName(category) {
        const nameMap = {
            'transactions': 'Transaction Data',
            'balances': 'Account Balances',
            'investments': 'Investment Portfolio',
            'epf': 'EPF & Retirement',
            'credit': 'Credit Score',
            'assets': 'Assets & Liabilities'
        };
        return nameMap[category] || category;
    }

    setToggleLoading(toggle, loading) {
        const toggleSwitch = toggle.closest('.privacy-toggle');
        if (loading) {
            toggleSwitch.classList.add('loading');
            toggle.disabled = true;
        } else {
            toggleSwitch.classList.remove('loading');
            toggle.disabled = false;
        }
    }

    async syncPrivacySettings() {
        if (window.electronAPI) {
            const response = await window.electronAPI.updatePrivacySettings(this.settings);
            if (!response.success) {
                throw new Error(response.error);
            }
        }
        
        // Save locally
        this.savePrivacySettings();
        
        // Update app settings
        this.app.privacySettings = { ...this.settings };
    }

    updatePrivacyStatus() {
        const enabledCount = Object.values(this.settings).filter(Boolean).length;
        const totalCount = Object.keys(this.settings).length;
        
        // Update sidebar status
        const privacyStatus = document.querySelector('.privacy-status span');
        if (privacyStatus) {
            if (enabledCount === totalCount) {
                privacyStatus.textContent = 'Full Access';
            } else if (enabledCount === 0) {
                privacyStatus.textContent = 'No Access';
            } else {
                privacyStatus.textContent = `${enabledCount}/${totalCount} Categories`;
            }
        }

        // Update privacy status color
        const privacyStatusContainer = document.querySelector('.privacy-status');
        if (privacyStatusContainer) {
            privacyStatusContainer.className = 'privacy-status';
            if (enabledCount === 0) {
                privacyStatusContainer.classList.add('no-access');
            } else if (enabledCount < totalCount) {
                privacyStatusContainer.classList.add('partial-access');
            } else {
                privacyStatusContainer.classList.add('full-access');
            }
        }
    }

    updatePrivacyStatusIndicator() {
        // Update the privacy status indicator in the dashboard
        const dashboardPrivacyIndicator = document.getElementById('privacy-indicator');
        if (dashboardPrivacyIndicator) {
            const enabledCategories = Object.entries(this.settings)
                .filter(([_, enabled]) => enabled)
                .map(([category]) => this.getCategoryDisplayName(category));
            
            dashboardPrivacyIndicator.innerHTML = `
                <div class="privacy-summary">
                    <h4>Data Access Status</h4>
                    <p>${enabledCategories.length} out of ${Object.keys(this.settings).length} categories enabled</p>
                    <div class="enabled-categories">
                        ${enabledCategories.map(cat => `<span class="category-tag">${cat}</span>`).join('')}
                    </div>
                </div>
            `;
        }
    }

    updateDataVisibility(category, isEnabled) {
        // Update visibility of data based on privacy settings
        const dataElements = document.querySelectorAll(`[data-privacy-category="${category}"]`);
        
        dataElements.forEach(element => {
            if (isEnabled) {
                element.classList.remove('privacy-hidden');
                element.classList.add('privacy-visible');
            } else {
                element.classList.remove('privacy-visible');
                element.classList.add('privacy-hidden');
            }
        });

        // Update charts and data displays
        this.updateChartVisibility(category, isEnabled);
        
        // Refresh data if needed
        if (this.app.currentSection === 'dashboard') {
            this.app.dashboard?.updateDataVisibility();
        }
    }

    updateChartVisibility(category, isEnabled) {
        // Hide/show specific chart elements based on privacy settings
        const chartMap = {
            'transactions': ['spending-chart', 'category-chart'],
            'balances': ['balance-trend-chart'],
            'investments': ['investment-chart', 'portfolio-chart'],
            'assets': ['net-worth-chart']
        };

        const chartsToUpdate = chartMap[category] || [];
        
        chartsToUpdate.forEach(chartId => {
            const chartElement = document.getElementById(chartId);
            if (chartElement) {
                if (isEnabled) {
                    chartElement.style.display = 'block';
                } else {
                    chartElement.style.display = 'none';
                    // Show privacy message
                    this.showPrivacyMessage(chartElement.parentElement, category);
                }
            }
        });
    }

    showPrivacyMessage(container, category) {
        const categoryName = this.getCategoryDisplayName(category);
        const message = document.createElement('div');
        message.className = 'privacy-message';
        message.innerHTML = `
            <div class="privacy-message-content">
                <i class="fas fa-eye-slash"></i>
                <h4>Data Hidden for Privacy</h4>
                <p>${categoryName} is currently disabled. Enable it in Privacy Settings to view this data.</p>
                <button class="btn btn-primary btn-sm" onclick="app.privacy.enableCategory('${category}')">
                    <i class="fas fa-unlock"></i>
                    Enable ${categoryName}
                </button>
            </div>
        `;
        
        // Replace chart with privacy message
        const existingMessage = container.querySelector('.privacy-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        container.appendChild(message);
    }

    async enableCategory(category) {
        const toggle = document.getElementById(`${category}-toggle`);
        if (toggle) {
            toggle.checked = true;
            await this.handleToggleChange(toggle);
        }
    }

    loadPrivacySettings() {
        try {
            const saved = localStorage.getItem('financial-ai-privacy-settings');
            if (saved) {
                const savedSettings = JSON.parse(saved);
                this.settings = { ...this.settings, ...savedSettings };
            }
            
            // Apply settings to toggles
            Object.entries(this.settings).forEach(([category, enabled]) => {
                const toggle = document.getElementById(`${category}-toggle`);
                if (toggle) {
                    toggle.checked = enabled;
                }
            });
            
        } catch (error) {
            console.error('Error loading privacy settings:', error);
        }
    }

    savePrivacySettings() {
        try {
            localStorage.setItem('financial-ai-privacy-settings', JSON.stringify(this.settings));
        } catch (error) {
            console.error('Error saving privacy settings:', error);
        }
    }

    // Bulk privacy controls
    enableAllCategories() {
        Object.keys(this.settings).forEach(category => {
            this.settings[category] = true;
            const toggle = document.getElementById(`${category}-toggle`);
            if (toggle) {
                toggle.checked = true;
            }
        });
        
        this.syncPrivacySettings();
        this.updateAllDataVisibility();
        this.app.showNotification('All categories enabled', 'success');
    }

    disableAllCategories() {
        if (confirm('Are you sure you want to disable access to all financial data? This will hide all insights and analytics.')) {
            Object.keys(this.settings).forEach(category => {
                this.settings[category] = false;
                const toggle = document.getElementById(`${category}-toggle`);
                if (toggle) {
                    toggle.checked = false;
                }
            });
            
            this.syncPrivacySettings();
            this.updateAllDataVisibility();
            this.app.showNotification('All categories disabled', 'info');
        }
    }

    resetToDefaults() {
        const defaultSettings = {
            transactions: true,
            balances: true,
            investments: true,
            epf: true,
            credit: true,
            assets: true
        };
        
        Object.entries(defaultSettings).forEach(([category, enabled]) => {
            this.settings[category] = enabled;
            const toggle = document.getElementById(`${category}-toggle`);
            if (toggle) {
                toggle.checked = enabled;
            }
        });
        
        this.syncPrivacySettings();
        this.updateAllDataVisibility();
        this.app.showNotification('Privacy settings reset to defaults', 'info');
    }

    updateAllDataVisibility() {
        Object.entries(this.settings).forEach(([category, enabled]) => {
            this.updateDataVisibility(category, enabled);
        });
        this.updatePrivacyStatus();
        this.updatePrivacyStatusIndicator();
    }

    // Privacy audit and logging
    getPrivacyAuditLog() {
        const auditData = {
            currentSettings: this.settings,
            lastModified: localStorage.getItem('financial-ai-privacy-last-modified') || new Date().toISOString(),
            settingsHistory: JSON.parse(localStorage.getItem('financial-ai-privacy-history') || '[]'),
            accessLog: this.getDataAccessLog()
        };
        
        return auditData;
    }

    logPrivacyChange(category, oldValue, newValue) {
        try {
            const history = JSON.parse(localStorage.getItem('financial-ai-privacy-history') || '[]');
            const changeLog = {
                timestamp: new Date().toISOString(),
                category,
                oldValue,
                newValue,
                userAgent: navigator.userAgent
            };
            
            history.push(changeLog);
            
            // Keep only last 100 changes
            const recentHistory = history.slice(-100);
            
            localStorage.setItem('financial-ai-privacy-history', JSON.stringify(recentHistory));
            localStorage.setItem('financial-ai-privacy-last-modified', changeLog.timestamp);
            
        } catch (error) {
            console.error('Error logging privacy change:', error);
        }
    }

    getDataAccessLog() {
        // This would integrate with your analytics/audit system
        return {
            apiCalls: 0, // Number of API calls made
            dataQueries: 0, // Number of data queries
            aiInteractions: 0, // Number of AI chat interactions
            lastAccess: new Date().toISOString()
        };
    }

    exportPrivacyData() {
        const privacyData = {
            settings: this.settings,
            audit: this.getPrivacyAuditLog(),
            exportDate: new Date().toISOString(),
            appVersion: window.electronAPI?.getAppVersion() || '1.0.0'
        };

        const dataStr = JSON.stringify(privacyData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `financial-ai-privacy-${new Date().toISOString().split('T')[0]}.json`;
        link.click();

        this.app.showNotification('Privacy data exported', 'success');
    }

    // GDPR compliance helpers
    getDataCategories() {
        return Object.entries(this.settings).map(([category, enabled]) => ({
            category,
            displayName: this.getCategoryDisplayName(category),
            enabled,
            description: this.getCategoryDescription(category),
            dataTypes: this.getDataTypesForCategory(category)
        }));
    }

    getCategoryDescription(category) {
        const descriptions = {
            'transactions': 'Transaction history including amounts, dates, merchants, and categories',
            'balances': 'Current and historical account balance information',
            'investments': 'Investment portfolio data including holdings, performance, and allocations',
            'epf': 'Employee Provident Fund and retirement account information',
            'credit': 'Credit score, credit history, and creditworthiness data',
            'assets': 'Asset and liability information including property, loans, and net worth calculations'
        };
        return descriptions[category] || 'Financial data category';
    }

    getDataTypesForCategory(category) {
        const dataTypes = {
            'transactions': ['Transaction amounts', 'Merchant names', 'Transaction dates', 'Categories', 'Account information'],
            'balances': ['Account balances', 'Balance history', 'Account types'],
            'investments': ['Holdings', 'Portfolio value', 'Asset allocation', 'Investment performance'],
            'epf': ['EPF balance', 'Contribution history', 'Retirement projections'],
            'credit': ['Credit score', 'Credit history', 'Credit utilization'],
            'assets': ['Property values', 'Loan balances', 'Asset categories', 'Net worth calculations']
        };
        return dataTypes[category] || [];
    }

    // Data retention controls
    requestDataDeletion(categories = null) {
        const categoriesToDelete = categories || Object.keys(this.settings);
        
        const message = categories 
            ? `Delete data for: ${categories.map(c => this.getCategoryDisplayName(c)).join(', ')}?`
            : 'Delete all financial data? This action cannot be undone.';
            
        if (confirm(message)) {
            // This would integrate with your backend to actually delete the data
            console.log('Data deletion requested for categories:', categoriesToDelete);
            this.app.showNotification('Data deletion request submitted', 'info');
            
            // Log the deletion request
            this.logDataDeletionRequest(categoriesToDelete);
        }
    }

    logDataDeletionRequest(categories) {
        const deletionLog = {
            timestamp: new Date().toISOString(),
            categories,
            requestId: this.generateRequestId(),
            status: 'pending'
        };
        
        const deletionHistory = JSON.parse(localStorage.getItem('financial-ai-deletion-requests') || '[]');
        deletionHistory.push(deletionLog);
        localStorage.setItem('financial-ai-deletion-requests', JSON.stringify(deletionHistory));
    }

    generateRequestId() {
        return 'req_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
}

// Privacy-related CSS
const privacyCSS = `
    .privacy-hidden {
        display: none !important;
    }
    
    .privacy-visible {
        display: block !important;
    }
    
    .privacy-message {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: var(--spacing-2xl);
        background: var(--bg-tertiary);
        border-radius: var(--radius-lg);
        text-align: center;
    }
    
    .privacy-message-content {
        max-width: 300px;
    }
    
    .privacy-message-content i {
        font-size: 3rem;
        color: var(--text-light);
        margin-bottom: var(--spacing-md);
    }
    
    .privacy-message-content h4 {
        margin-bottom: var(--spacing-sm);
        color: var(--text-primary);
    }
    
    .privacy-message-content p {
        margin-bottom: var(--spacing-lg);
        color: var(--text-secondary);
        line-height: 1.5;
    }
    
    .privacy-toggle.loading {
        opacity: 0.6;
        pointer-events: none;
    }
    
    .privacy-status.no-access {
        color: var(--danger-color);
    }
    
    .privacy-status.partial-access {
        color: var(--warning-color);
    }
    
    .privacy-status.full-access {
        color: var(--secondary-color);
    }
    
    .category-tag {
        display: inline-block;
        padding: 2px 8px;
        margin: 2px;
        background: var(--primary-color);
        color: white;
        border-radius: var(--radius-sm);
        font-size: 0.75rem;
    }
    
    .privacy-summary {
        padding: var(--spacing-md);
        background: var(--bg-tertiary);
        border-radius: var(--radius-md);
        margin-bottom: var(--spacing-md);
    }
    
    .enabled-categories {
        margin-top: var(--spacing-sm);
    }
`;

const privacyStyle = document.createElement('style');
privacyStyle.textContent = privacyCSS;
document.head.appendChild(privacyStyle);