/**
 * Enhanced Privacy Controller
 * Provides advanced privacy management, audit trail tracking, and granular permission controls
 */
class EnhancedPrivacyController {
    constructor(app) {
        this.app = app;
        this.privacySettings = {
            transactions: { enabled: true, granular: { recent: true, historical: true, categories: true } },
            balances: { enabled: true, granular: { accounts: true, savings: true, trends: true } },
            investments: { enabled: true, granular: { portfolio: true, performance: true, recommendations: true } },
            epf: { enabled: true, granular: { balance: true, contributions: true, projections: true } },
            credit: { enabled: true, granular: { score: true, factors: true, history: true } },
            assets: { enabled: true, granular: { properties: true, vehicles: true, valuables: true } },
            liabilities: { enabled: true, granular: { loans: true, creditCards: true, other: true } },
            insights: { enabled: true, granular: { spending: true, savings: true, investments: true, debt: true } },
        };
        
        this.auditTrail = [];
        this.permissionCallbacks = [];
        
        this.init();
    }

    /**
     * Initialize the privacy controller
     */
    init() {
        this.loadPrivacySettings();
        this.renderEnhancedPrivacyControls();
        this.setupEventListeners();
        this.logAuditEvent('Privacy module initialized', 'system');
    }

    /**
     * Load saved privacy settings from local storage
     */
    loadPrivacySettings() {
        try {
            const savedSettings = localStorage.getItem('financial-ai-privacy-settings');
            if (savedSettings) {
                this.privacySettings = JSON.parse(savedSettings);
                this.logAuditEvent('Privacy settings loaded', 'system');
            }
            
            const savedAudit = localStorage.getItem('financial-ai-privacy-audit');
            if (savedAudit) {
                this.auditTrail = JSON.parse(savedAudit);
            }
        } catch (error) {
            console.error('Error loading privacy settings:', error);
            this.logAuditEvent('Error loading privacy settings', 'error');
        }
    }

    /**
     * Save privacy settings to local storage
     */
    savePrivacySettings() {
        try {
            localStorage.setItem('financial-ai-privacy-settings', JSON.stringify(this.privacySettings));
            localStorage.setItem('financial-ai-privacy-audit', JSON.stringify(this.auditTrail.slice(-100))); // Keep last 100 events
            
            // Notify the app of privacy changes
            if (this.app) {
                this.app.onPrivacySettingsChanged(this.privacySettings);
            }
            
            // Execute callbacks
            this.permissionCallbacks.forEach(callback => callback(this.privacySettings));
            
            this.updatePrivacyStatus();
        } catch (error) {
            console.error('Error saving privacy settings:', error);
            this.logAuditEvent('Error saving privacy settings', 'error');
        }
    }

    /**
     * Register a callback for privacy setting changes
     * @param {Function} callback - Function to call when privacy settings change
     */
    onPrivacyChange(callback) {
        if (typeof callback === 'function') {
            this.permissionCallbacks.push(callback);
        }
    }

    /**
     * Unregister a privacy change callback
     * @param {Function} callback - Function to remove
     */
    offPrivacyChange(callback) {
        this.permissionCallbacks = this.permissionCallbacks.filter(cb => cb !== callback);
    }

    /**
     * Check if a specific data category is accessible
     * @param {string} category - Main data category
     * @param {string} subcategory - Optional granular subcategory
     * @returns {boolean} - Whether access is granted
     */
    canAccess(category, subcategory = null) {
        if (!this.privacySettings[category]) {
            return false;
        }
        
        // First check if the main category is enabled
        if (!this.privacySettings[category].enabled) {
            return false;
        }
        
        // If subcategory is specified, check granular permission
        if (subcategory && 
            this.privacySettings[category].granular && 
            this.privacySettings[category].granular[subcategory] !== undefined) {
            return this.privacySettings[category].granular[subcategory];
        }
        
        return true;
    }

    /**
     * Log an event to the privacy audit trail
     * @param {string} action - Description of the action
     * @param {string} type - Type of event (toggle, access, system, error)
     * @param {Object} details - Additional event details
     */
    logAuditEvent(action, type = 'toggle', details = {}) {
        const event = {
            timestamp: new Date().toISOString(),
            action,
            type,
            details
        };
        
        this.auditTrail.push(event);
        
        // Keep audit trail from growing too large
        if (this.auditTrail.length > 1000) {
            this.auditTrail = this.auditTrail.slice(-1000);
        }
        
        // Update the audit UI if visible
        this.renderAuditTrail();
    }

    /**
     * Update the main toggle from granular permission state
     * @param {string} category - Category to update
     */
    updateMainToggleFromGranular(category) {
        if (!this.privacySettings[category] || !this.privacySettings[category].granular) {
            return;
        }
        
        // Check if any granular permission is enabled
        const hasEnabledGranular = Object.values(this.privacySettings[category].granular).some(value => value);
        
        // If no granular permissions are enabled, disable the main toggle
        if (!hasEnabledGranular) {
            this.privacySettings[category].enabled = false;
            
            // Update UI
            const mainToggle = document.getElementById(`${category}-toggle`);
            if (mainToggle) {
                mainToggle.checked = false;
            }
        }
    }

    /**
     * Render the enhanced privacy controls UI
     */
    renderEnhancedPrivacyControls() {
        const privacyContainer = document.querySelector('.privacy-controls');
        if (!privacyContainer) return;
        
        // Update existing toggles to match current settings
        for (const category in this.privacySettings) {
            const toggle = document.getElementById(`${category}-toggle`);
            if (toggle) {
                toggle.checked = this.privacySettings[category].enabled;
            }
        }
        
        // Add the advanced privacy panel
        const advancedPanel = document.createElement('div');
        advancedPanel.className = 'card privacy-card advanced-privacy-panel';
        advancedPanel.innerHTML = `
            <div class="card-header">
                <h3>Advanced Privacy Controls</h3>
                <p>Fine-tune exactly what data the AI can access</p>
            </div>
            <div class="card-body">
                <div class="advanced-privacy-tabs">
                    <div class="tab-header">
                        <button class="tab-btn active" data-tab="granular-permissions">Granular Permissions</button>
                        <button class="tab-btn" data-tab="audit-trail">Audit Trail</button>
                        <button class="tab-btn" data-tab="data-export">Data Export</button>
                    </div>
                    
                    <div class="tab-content">
                        <div class="tab-pane active" id="granular-permissions">
                            ${this.renderGranularPermissions()}
                        </div>
                        <div class="tab-pane" id="audit-trail">
                            <div class="audit-trail-container">
                                <div class="audit-controls">
                                    <select id="audit-filter">
                                        <option value="all">All Events</option>
                                        <option value="toggle">Permission Changes</option>
                                        <option value="access">Data Access</option>
                                        <option value="system">System Events</option>
                                        <option value="error">Errors</option>
                                    </select>
                                    <button id="clear-audit" class="btn btn-secondary">
                                        <i class="fas fa-trash"></i> Clear History
                                    </button>
                                </div>
                                <div class="audit-list" id="audit-list">
                                    <div class="audit-empty">No events recorded yet</div>
                                </div>
                            </div>
                        </div>
                        <div class="tab-pane" id="data-export">
                            <div class="data-export-controls">
                                <h4>Export Your Data</h4>
                                <p>Download a copy of your data for personal records or backup</p>
                                
                                <div class="export-options">
                                    <div class="export-format">
                                        <h5>Format</h5>
                                        <div class="radio-group">
                                            <label>
                                                <input type="radio" name="export-format" value="json" checked> JSON
                                            </label>
                                            <label>
                                                <input type="radio" name="export-format" value="csv"> CSV
                                            </label>
                                        </div>
                                    </div>
                                    
                                    <div class="export-categories">
                                        <h5>Data Categories</h5>
                                        <div class="checkbox-group">
                                            ${Object.keys(this.privacySettings).map(category => `
                                                <label>
                                                    <input type="checkbox" name="export-category" value="${category}" checked>
                                                    ${this.formatCategoryName(category)}
                                                </label>
                                            `).join('')}
                                        </div>
                                    </div>
                                </div>
                                
                                <button id="export-data-btn" class="btn btn-primary">
                                    <i class="fas fa-download"></i> Export Data
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add or replace the advanced panel
        const existingPanel = document.querySelector('.advanced-privacy-panel');
        if (existingPanel) {
            existingPanel.replaceWith(advancedPanel);
        } else {
            privacyContainer.appendChild(advancedPanel);
        }
        
        // Add GDPR compliance card
        const gdprCard = document.createElement('div');
        gdprCard.className = 'card privacy-card';
        gdprCard.innerHTML = `
            <div class="card-header">
                <h3>Data Rights & Compliance</h3>
                <p>Control your data in compliance with privacy regulations</p>
            </div>
            <div class="card-body">
                <div class="data-rights-options">
                    <div class="data-right-option">
                        <div class="option-icon">
                            <i class="fas fa-trash-alt"></i>
                        </div>
                        <div class="option-details">
                            <h4>Delete My Data</h4>
                            <p>Permanently remove selected categories of your data</p>
                            <button id="delete-data-btn" class="btn btn-danger">
                                Request Deletion
                            </button>
                        </div>
                    </div>
                    
                    <div class="data-right-option">
                        <div class="option-icon">
                            <i class="fas fa-file-alt"></i>
                        </div>
                        <div class="option-details">
                            <h4>Access Report</h4>
                            <p>Get a complete report of all your data and how it's used</p>
                            <button id="access-report-btn" class="btn btn-secondary">
                                Request Report
                            </button>
                        </div>
                    </div>
                    
                    <div class="data-right-option">
                        <div class="option-icon">
                            <i class="fas fa-user-shield"></i>
                        </div>
                        <div class="option-details">
                            <h4>Privacy Policy</h4>
                            <p>Review our detailed privacy and data handling practices</p>
                            <button id="privacy-policy-btn" class="btn btn-secondary">
                                View Policy
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        privacyContainer.appendChild(gdprCard);
        
        // Now that the UI is rendered, populate the audit trail
        this.renderAuditTrail();
    }

    /**
     * Render granular permission controls for each category
     * @returns {string} HTML string for granular permission controls
     */
    renderGranularPermissions() {
        let html = '<div class="granular-permissions-list">';
        
        for (const category in this.privacySettings) {
            if (this.privacySettings[category].granular) {
                html += `
                    <div class="granular-category ${!this.privacySettings[category].enabled ? 'disabled' : ''}">
                        <div class="category-header">
                            <h4>${this.formatCategoryName(category)}</h4>
                            <div class="category-toggle">
                                <label class="switch">
                                    <input type="checkbox" data-category="${category}" class="category-main-toggle" 
                                        ${this.privacySettings[category].enabled ? 'checked' : ''}>
                                    <span class="slider round"></span>
                                </label>
                            </div>
                        </div>
                        <div class="subcategory-list">
                `;
                
                for (const subcategory in this.privacySettings[category].granular) {
                    html += `
                        <div class="subcategory-item">
                            <div class="subcategory-name">${this.formatSubcategoryName(subcategory)}</div>
                            <div class="subcategory-toggle">
                                <label class="switch">
                                    <input type="checkbox" 
                                        data-category="${category}" 
                                        data-subcategory="${subcategory}" 
                                        class="subcategory-toggle"
                                        ${this.privacySettings[category].granular[subcategory] ? 'checked' : ''}
                                        ${!this.privacySettings[category].enabled ? 'disabled' : ''}>
                                    <span class="slider round"></span>
                                </label>
                            </div>
                        </div>
                    `;
                }
                
                html += `
                        </div>
                    </div>
                `;
            }
        }
        
        html += '</div>';
        return html;
    }

    /**
     * Render the audit trail in the UI
     */
    renderAuditTrail() {
        const auditList = document.getElementById('audit-list');
        if (!auditList) return;
        
        const filter = document.getElementById('audit-filter')?.value || 'all';
        
        // Filter events based on selected filter
        const filteredEvents = filter === 'all' 
            ? this.auditTrail 
            : this.auditTrail.filter(event => event.type === filter);
        
        if (filteredEvents.length === 0) {
            auditList.innerHTML = '<div class="audit-empty">No events matching the selected filter</div>';
            return;
        }
        
        // Sort events newest to oldest
        const sortedEvents = [...filteredEvents].sort((a, b) => 
            new Date(b.timestamp) - new Date(a.timestamp)
        );
        
        // Generate HTML for each event
        auditList.innerHTML = sortedEvents.map(event => {
            const date = new Date(event.timestamp);
            const formattedDate = date.toLocaleDateString('en-IN', {
                day: 'numeric',
                month: 'short',
                year: 'numeric'
            });
            const formattedTime = date.toLocaleTimeString('en-IN', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            
            return `
                <div class="audit-item audit-type-${event.type}">
                    <div class="audit-icon">
                        <i class="fas ${this.getAuditIcon(event.type)}"></i>
                    </div>
                    <div class="audit-content">
                        <div class="audit-action">${event.action}</div>
                        <div class="audit-details">
                            ${Object.entries(event.details).map(([key, value]) => 
                                `<span class="audit-detail"><strong>${key}:</strong> ${value}</span>`
                            ).join(' ')}
                        </div>
                    </div>
                    <div class="audit-time">
                        <div class="audit-date">${formattedDate}</div>
                        <div class="audit-time-value">${formattedTime}</div>
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * Get the appropriate icon for audit event type
     * @param {string} type - Audit event type
     * @returns {string} - Font Awesome icon class
     */
    getAuditIcon(type) {
        switch (type) {
            case 'toggle': return 'fa-toggle-on';
            case 'access': return 'fa-eye';
            case 'system': return 'fa-cog';
            case 'error': return 'fa-exclamation-triangle';
            default: return 'fa-info-circle';
        }
    }

    /**
     * Format a category name for display
     * @param {string} category - Category key
     * @returns {string} - Formatted category name
     */
    formatCategoryName(category) {
        const names = {
            transactions: 'Transaction History',
            balances: 'Account Balances',
            investments: 'Investment Portfolio',
            epf: 'EPF & Retirement',
            credit: 'Credit Information',
            assets: 'Assets & Property',
            liabilities: 'Loans & Liabilities',
            insights: 'AI-Generated Insights'
        };
        
        return names[category] || category.charAt(0).toUpperCase() + category.slice(1);
    }

    /**
     * Format a subcategory name for display
     * @param {string} subcategory - Subcategory key
     * @returns {string} - Formatted subcategory name
     */
    formatSubcategoryName(subcategory) {
        const names = {
            recent: 'Recent Transactions',
            historical: 'Historical Data',
            categories: 'Category Analysis',
            accounts: 'Account Details',
            savings: 'Savings Goals',
            trends: 'Balance Trends',
            portfolio: 'Portfolio Details',
            performance: 'Performance Metrics',
            recommendations: 'Investment Recommendations',
            balance: 'EPF Balance',
            contributions: 'Contribution History',
            projections: 'Retirement Projections',
            score: 'Credit Score',
            factors: 'Score Factors',
            history: 'Credit History',
            properties: 'Real Estate',
            vehicles: 'Vehicles & Assets',
            valuables: 'Valuables & Collections',
            loans: 'Loans & Mortgages',
            creditCards: 'Credit Cards',
            other: 'Other Debts',
            spending: 'Spending Insights',
            savings: 'Savings Insights',
            investments: 'Investment Insights',
            debt: 'Debt Management'
        };
        
        return names[subcategory] || subcategory.charAt(0).toUpperCase() + subcategory.slice(1);
    }

    /**
     * Update the privacy status indicator in the sidebar
     */
    updatePrivacyStatus() {
        const statusEl = document.querySelector('.privacy-status span');
        if (!statusEl) return;
        
        // Count how many main categories are enabled
        const enabledCount = Object.values(this.privacySettings)
            .filter(setting => setting.enabled)
            .length;
            
        const totalCount = Object.keys(this.privacySettings).length;
        
        if (enabledCount === 0) {
            statusEl.textContent = 'Maximum Privacy (All Disabled)';
            statusEl.previousElementSibling.className = 'fas fa-lock';
        } else if (enabledCount === totalCount) {
            statusEl.textContent = 'All Data Accessible';
            statusEl.previousElementSibling.className = 'fas fa-lock-open';
        } else {
            statusEl.textContent = `${enabledCount} of ${totalCount} Categories Enabled`;
            statusEl.previousElementSibling.className = 'fas fa-shield-alt';
        }
    }

    /**
     * Set up event listeners for privacy controls
     */
    setupEventListeners() {
        // Main category toggles
        document.querySelectorAll('[id$="-toggle"]').forEach(toggle => {
            const category = toggle.id.replace('-toggle', '');
            
            toggle.addEventListener('change', (e) => {
                if (this.privacySettings[category]) {
                    this.privacySettings[category].enabled = e.target.checked;
                    
                    // Update UI for granular permissions
                    this.updateGranularUI(category);
                    
                    this.logAuditEvent(
                        `${this.formatCategoryName(category)} access ${e.target.checked ? 'enabled' : 'disabled'}`,
                        'toggle',
                        { category, enabled: e.target.checked }
                    );
                    
                    this.savePrivacySettings();
                }
            });
        });
        
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tabId = e.target.dataset.tab;
                
                // Update active tab button
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                
                // Update active tab pane
                document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');
            });
        });
        
        // Granular permission toggles (delegation)
        document.addEventListener('change', (e) => {
            // Main category toggles within granular permissions
            if (e.target.classList.contains('category-main-toggle')) {
                const category = e.target.dataset.category;
                this.privacySettings[category].enabled = e.target.checked;
                
                // Update all subcategory toggles
                this.updateGranularUI(category);
                
                this.logAuditEvent(
                    `${this.formatCategoryName(category)} access ${e.target.checked ? 'enabled' : 'disabled'}`,
                    'toggle',
                    { category, enabled: e.target.checked }
                );
                
                this.savePrivacySettings();
            }
            
            // Subcategory toggles
            if (e.target.classList.contains('subcategory-toggle')) {
                const category = e.target.dataset.category;
                const subcategory = e.target.dataset.subcategory;
                
                this.privacySettings[category].granular[subcategory] = e.target.checked;
                
                this.logAuditEvent(
                    `${this.formatSubcategoryName(subcategory)} access ${e.target.checked ? 'enabled' : 'disabled'}`,
                    'toggle',
                    { 
                        category: this.formatCategoryName(category), 
                        subcategory: this.formatSubcategoryName(subcategory), 
                        enabled: e.target.checked 
                    }
                );
                
                // Update main toggle if needed
                this.updateMainToggleFromGranular(category);
                
                this.savePrivacySettings();
            }
            
            // Audit filter change
            if (e.target.id === 'audit-filter') {
                this.renderAuditTrail();
            }
        });
        
        // Button click handlers (delegation)
        document.addEventListener('click', (e) => {
            // Clear audit trail
            if (e.target.id === 'clear-audit' || e.target.closest('#clear-audit')) {
                this.auditTrail = [];
                localStorage.removeItem('financial-ai-privacy-audit');
                this.renderAuditTrail();
            }
            
            // Export data
            if (e.target.id === 'export-data-btn' || e.target.closest('#export-data-btn')) {
                this.handleDataExport();
            }
            
            // Delete data request
            if (e.target.id === 'delete-data-btn' || e.target.closest('#delete-data-btn')) {
                this.showDeleteDataModal();
            }
            
            // Access report request
            if (e.target.id === 'access-report-btn' || e.target.closest('#access-report-btn')) {
                this.requestAccessReport();
            }
            
            // Privacy policy
            if (e.target.id === 'privacy-policy-btn' || e.target.closest('#privacy-policy-btn')) {
                this.showPrivacyPolicy();
            }
        });
    }

    /**
     * Update the UI for granular permissions when main toggle changes
     * @param {string} category - Category to update
     */
    updateGranularUI(category) {
        const isEnabled = this.privacySettings[category].enabled;
        const categoryEl = document.querySelector(`.granular-category h4:contains("${this.formatCategoryName(category)}")`).closest('.granular-category');
        
        if (categoryEl) {
            if (isEnabled) {
                categoryEl.classList.remove('disabled');
            } else {
                categoryEl.classList.add('disabled');
            }
            
            // Update subcategory toggles
            categoryEl.querySelectorAll('.subcategory-toggle').forEach(toggle => {
                toggle.disabled = !isEnabled;
            });
        }
        
        // Also update the main toggle in the basic privacy panel
        const mainToggle = document.getElementById(`${category}-toggle`);
        if (mainToggle) {
            mainToggle.checked = isEnabled;
        }
    }

    /**
     * Handle data export functionality
     */
    handleDataExport() {
        // Get selected format
        const format = document.querySelector('input[name="export-format"]:checked').value;
        
        // Get selected categories
        const categories = Array.from(document.querySelectorAll('input[name="export-category"]:checked'))
            .map(input => input.value);
        
        if (categories.length === 0) {
            this.app.showNotification('Please select at least one data category to export', 'warning');
            return;
        }
        
        this.logAuditEvent(
            `Data export requested`,
            'access',
            { format, categories: categories.join(', ') }
        );
        
        // In a real implementation, this would call the backend
        // For now, we'll simulate an export with dummy data
        this.simulateDataExport(format, categories);
    }

    /**
     * Simulate data export (for demonstration)
     * @param {string} format - Export format (json/csv)
     * @param {Array} categories - Categories to export
     */
    simulateDataExport(format, categories) {
        // Show loading indicator
        this.app.setLoading(true);
        
        setTimeout(() => {
            this.app.setLoading(false);
            
            // Show success notification
            this.app.showNotification(`Your data export is ready (${format.toUpperCase()}, ${categories.length} categories)`, 'success');
            
            // In a real implementation, this would trigger a download
            console.log(`Exporting data: format=${format}, categories=${categories.join(',')}`);
            
            // Log the export in audit trail
            this.logAuditEvent(
                `Data export completed`,
                'access',
                { format, categories: categories.length }
            );
            
            this.savePrivacySettings();
        }, 1500);
    }

    /**
     * Show delete data confirmation modal
     */
    showDeleteDataModal() {
        // Create modal HTML
        const modal = document.createElement('div');
        modal.className = 'modal delete-data-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Delete My Data</h3>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <p class="warning-text">
                        <i class="fas fa-exclamation-triangle"></i>
                        This action cannot be undone. Selected data will be permanently deleted.
                    </p>
                    
                    <div class="deletion-options">
                        <h4>Select data categories to delete:</h4>
                        <div class="checkbox-group">
                            ${Object.keys(this.privacySettings).map(category => `
                                <label>
                                    <input type="checkbox" name="delete-category" value="${category}">
                                    ${this.formatCategoryName(category)}
                                </label>
                            `).join('')}
                        </div>
                    </div>
                    
                    <div class="deletion-confirmation">
                        <label>
                            <input type="checkbox" id="deletion-confirm">
                            I understand this is permanent and cannot be reversed
                        </label>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary close-modal">Cancel</button>
                    <button class="btn btn-danger" id="confirm-deletion" disabled>Delete Selected Data</button>
                </div>
            </div>
        `;
        
        // Add to document
        document.body.appendChild(modal);
        
        // Show modal
        setTimeout(() => modal.classList.add('visible'), 10);
        
        // Setup event listeners
        modal.querySelector('.close-modal').addEventListener('click', () => {
            modal.classList.remove('visible');
            setTimeout(() => modal.remove(), 300);
        });
        
        // Enable/disable delete button based on confirmation checkbox
        const confirmCheck = modal.querySelector('#deletion-confirm');
        const deleteBtn = modal.querySelector('#confirm-deletion');
        
        confirmCheck.addEventListener('change', () => {
            deleteBtn.disabled = !confirmCheck.checked;
        });
        
        // Handle deletion confirmation
        deleteBtn.addEventListener('click', () => {
            const categoriesToDelete = Array.from(modal.querySelectorAll('input[name="delete-category"]:checked'))
                .map(input => input.value);
                
            if (categoriesToDelete.length === 0) {
                this.app.showNotification('Please select at least one data category to delete', 'warning');
                return;
            }
            
            // Log the deletion request
            this.logAuditEvent(
                `Data deletion requested`,
                'access',
                { categories: categoriesToDelete.join(', ') }
            );
            
            // Close modal
            modal.classList.remove('visible');
            setTimeout(() => modal.remove(), 300);
            
            // Show processing message
            this.app.setLoading(true);
            this.app.showNotification('Processing data deletion request...', 'info');
            
            // Simulate processing time
            setTimeout(() => {
                this.app.setLoading(false);
                this.app.showNotification('Data deletion request submitted successfully', 'success');
                
                // Log completion
                this.logAuditEvent(
                    `Data deletion request processed`,
                    'system',
                    { categories: categoriesToDelete.length }
                );
                
                this.savePrivacySettings();
            }, 2000);
        });
    }

    /**
     * Request access report
     */
    requestAccessReport() {
        this.logAuditEvent(
            `Access report requested`,
            'access',
            { type: 'full' }
        );
        
        // Show processing message
        this.app.setLoading(true);
        this.app.showNotification('Generating your data access report...', 'info');
        
        // Simulate processing time
        setTimeout(() => {
            this.app.setLoading(false);
            this.app.showNotification('Your data access report is ready for download', 'success');
            
            // Log completion
            this.logAuditEvent(
                `Access report generated`,
                'system',
                { format: 'PDF' }
            );
            
            this.savePrivacySettings();
        }, 2000);
    }

    /**
     * Show privacy policy modal
     */
    showPrivacyPolicy() {
        // Create modal HTML
        const modal = document.createElement('div');
        modal.className = 'modal privacy-policy-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Privacy Policy</h3>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="privacy-policy-content">
                        <h4>Financial AI Assistant Privacy Policy</h4>
                        <p class="last-updated">Last Updated: September 2025</p>
                        
                        <h5>1. Introduction</h5>
                        <p>Financial AI Assistant is committed to protecting your privacy and ensuring the security of your personal and financial information. This policy explains how we collect, use, disclose, and safeguard your data.</p>
                        
                        <h5>2. Data Collection</h5>
                        <p>We collect the following types of information:</p>
                        <ul>
                            <li>Account information and balances</li>
                            <li>Transaction history</li>
                            <li>Investment portfolio details</li>
                            <li>Credit information</li>
                            <li>Assets and liabilities</li>
                            <li>User preferences and settings</li>
                        </ul>
                        
                        <h5>3. Data Usage</h5>
                        <p>Your data is used to:</p>
                        <ul>
                            <li>Provide financial insights and recommendations</li>
                            <li>Generate visualizations and reports</li>
                            <li>Power AI-driven conversation features</li>
                            <li>Improve our services and user experience</li>
                        </ul>
                        
                        <h5>4. Data Protection</h5>
                        <p>We implement strict security measures including:</p>
                        <ul>
                            <li>End-to-end encryption for all data transmission</li>
                            <li>Secure local storage with industry-standard encryption</li>
                            <li>Granular permission controls for all data categories</li>
                            <li>Regular security audits and updates</li>
                        </ul>
                        
                        <h5>5. Your Rights</h5>
                        <p>You have the right to:</p>
                        <ul>
                            <li>Access your personal data</li>
                            <li>Correct inaccurate data</li>
                            <li>Delete your data</li>
                            <li>Export your data</li>
                            <li>Restrict processing of your data</li>
                            <li>Object to data processing</li>
                        </ul>
                        
                        <h5>6. Contact Information</h5>
                        <p>For any privacy-related inquiries or concerns, please contact our Data Protection Officer at privacy@financialai-example.com</p>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary close-modal">Close</button>
                </div>
            </div>
        `;
        
        // Add to document
        document.body.appendChild(modal);
        
        // Show modal
        setTimeout(() => modal.classList.add('visible'), 10);
        
        // Setup event listeners
        const closeButtons = modal.querySelectorAll('.close-modal');
        closeButtons.forEach(button => {
            button.addEventListener('click', () => {
                modal.classList.remove('visible');
                setTimeout(() => modal.remove(), 300);
            });
        });
    }
}

// Add a helper method to Element.prototype for jQuery-like :contains selector
if (!Element.prototype.matches) {
    Element.prototype.matches = Element.prototype.msMatchesSelector || Element.prototype.webkitMatchesSelector;
}

if (document.querySelectorAll && !document.querySelector(':contains(test)')) {
    // Add custom :contains selector
    document.querySelector = (function(querySelector) {
        return function(selector) {
            if (selector.includes(':contains(')) {
                const match = selector.match(/:contains\((.*?)\)/);
                if (match) {
                    const text = match[1].replace(/["']/g, '');
                    const newSelector = selector.replace(/:contains\((.*?)\)/, '');
                    const elements = querySelector.call(this, newSelector);
                    
                    // Filter elements by text content
                    for (let i = 0; i < elements.length; i++) {
                        if (elements[i].textContent.includes(text)) {
                            return elements[i];
                        }
                    }
                    
                    return null;
                }
            }
            
            return querySelector.call(this, selector);
        };
    })(document.querySelector);
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedPrivacyController;
} else {
    window.EnhancedPrivacyController = EnhancedPrivacyController;
}