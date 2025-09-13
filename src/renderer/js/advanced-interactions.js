// Advanced Interactions Handler
class AdvancedInteractions {
    constructor(app) {
        this.app = app;
        this.searchIndex = new Map();
        this.filters = {
            active: {},
            available: {}
        };
        this.sortState = {
            column: null,
            direction: 'asc'
        };
        this.keyboardShortcuts = {};
        
        this.init();
    }

    init() {
        this.setupGlobalSearch();
        this.setupAdvancedFilters();
        this.setupKeyboardNavigation();
        this.setupDragAndDrop();
        this.setupSortableColumns();
        this.setupQuickActions();
        this.setupContextMenus();
        this.setupBulkOperations();
    }

    // Global Search Functionality
    setupGlobalSearch() {
        this.createGlobalSearchBar();
        this.buildSearchIndex();
        this.setupSearchShortcuts();
    }

    createGlobalSearchBar() {
        const header = document.querySelector('.section-header');
        if (header && !document.getElementById('global-search')) {
            const searchContainer = document.createElement('div');
            searchContainer.className = 'global-search-container';
            searchContainer.innerHTML = `
                <div class="search-input-wrapper">
                    <input type="text" id="global-search" placeholder="Search transactions, insights, or ask AI..." />
                    <div class="search-suggestions" id="search-suggestions"></div>
                    <button class="search-btn" id="search-btn">
                        <i class="fas fa-search"></i>
                    </button>
                    <button class="search-clear" id="search-clear" style="display: none;">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="search-filters" id="search-filters">
                    <button class="filter-chip" data-filter="transactions">Transactions</button>
                    <button class="filter-chip" data-filter="insights">Insights</button>
                    <button class="filter-chip" data-filter="categories">Categories</button>
                    <button class="filter-chip" data-filter="dates">This Month</button>
                </div>
            `;
            
            header.appendChild(searchContainer);
            this.bindSearchEvents();
        }
    }

    bindSearchEvents() {
        const searchInput = document.getElementById('global-search');
        const searchBtn = document.getElementById('search-btn');
        const searchClear = document.getElementById('search-clear');
        const searchSuggestions = document.getElementById('search-suggestions');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearchInput(e.target.value);
            });

            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch(e.target.value);
                } else if (e.key === 'Escape') {
                    this.clearSearch();
                } else if (e.key === 'ArrowDown') {
                    this.navigateSuggestions('down');
                } else if (e.key === 'ArrowUp') {
                    this.navigateSuggestions('up');
                }
            });

            searchInput.addEventListener('focus', () => {
                searchSuggestions.style.display = 'block';
            });

            document.addEventListener('click', (e) => {
                if (!e.target.closest('.search-input-wrapper')) {
                    searchSuggestions.style.display = 'none';
                }
            });
        }

        if (searchBtn) {
            searchBtn.addEventListener('click', () => {
                this.performSearch(searchInput.value);
            });
        }

        if (searchClear) {
            searchClear.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // Filter chips
        document.querySelectorAll('.filter-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                this.toggleFilter(e.target.dataset.filter);
                e.target.classList.toggle('active');
            });
        });
    }

    buildSearchIndex() {
        // Index transactions
        this.indexTransactions();
        
        // Index insights
        this.indexInsights();
        
        // Index categories
        this.indexCategories();
    }

    indexTransactions() {
        // Mock transaction indexing
        const transactions = [
            { id: 1, description: 'Grocery shopping at Walmart', category: 'food', amount: 2500 },
            { id: 2, description: 'Uber ride to office', category: 'transport', amount: 150 },
            { id: 3, description: 'Netflix subscription', category: 'entertainment', amount: 499 },
            { id: 4, description: 'Electricity bill payment', category: 'bills', amount: 1200 }
        ];

        transactions.forEach(transaction => {
            const searchText = `${transaction.description} ${transaction.category}`.toLowerCase();
            this.searchIndex.set(`transaction-${transaction.id}`, {
                type: 'transaction',
                data: transaction,
                searchText: searchText
            });
        });
    }

    indexInsights() {
        const insights = [
            { id: 1, text: 'Your food expenses increased by 15% this month', category: 'spending' },
            { id: 2, text: 'Great job! You saved ₹5,000 more than planned', category: 'savings' },
            { id: 3, text: 'Consider switching to a cheaper mobile plan', category: 'optimization' }
        ];

        insights.forEach(insight => {
            const searchText = `${insight.text} ${insight.category}`.toLowerCase();
            this.searchIndex.set(`insight-${insight.id}`, {
                type: 'insight',
                data: insight,
                searchText: searchText
            });
        });
    }

    indexCategories() {
        const categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Bills & Utilities', 
            'Entertainment', 'Healthcare', 'Investment', 'Savings'
        ];

        categories.forEach((category, index) => {
            this.searchIndex.set(`category-${index}`, {
                type: 'category',
                data: { name: category },
                searchText: category.toLowerCase()
            });
        });
    }

    handleSearchInput(query) {
        const searchClear = document.getElementById('search-clear');
        if (query.length > 0) {
            searchClear.style.display = 'block';
            this.showSuggestions(query);
        } else {
            searchClear.style.display = 'none';
            this.hideSuggestions();
        }
    }

    showSuggestions(query) {
        const suggestions = this.findSuggestions(query);
        const suggestionsContainer = document.getElementById('search-suggestions');
        
        if (suggestions.length > 0) {
            suggestionsContainer.innerHTML = suggestions.map((suggestion, index) => `
                <div class="search-suggestion ${index === 0 ? 'selected' : ''}" data-index="${index}">
                    <div class="suggestion-icon">
                        <i class="fas fa-${this.getSuggestionIcon(suggestion.type)}"></i>
                    </div>
                    <div class="suggestion-content">
                        <div class="suggestion-title">${this.highlightMatch(suggestion.title, query)}</div>
                        <div class="suggestion-type">${suggestion.type}</div>
                    </div>
                </div>
            `).join('');
            
            suggestionsContainer.style.display = 'block';
            this.bindSuggestionEvents();
        } else {
            this.hideSuggestions();
        }
    }

    findSuggestions(query) {
        const results = [];
        const queryLower = query.toLowerCase();
        
        this.searchIndex.forEach((item, key) => {
            if (item.searchText.includes(queryLower)) {
                results.push({
                    key: key,
                    type: item.type,
                    title: this.getSuggestionTitle(item),
                    data: item.data
                });
            }
        });
        
        return results.slice(0, 5); // Limit to 5 suggestions
    }

    getSuggestionTitle(item) {
        switch (item.type) {
            case 'transaction':
                return item.data.description;
            case 'insight':
                return item.data.text;
            case 'category':
                return item.data.name;
            default:
                return 'Unknown';
        }
    }

    getSuggestionIcon(type) {
        const icons = {
            transaction: 'exchange-alt',
            insight: 'lightbulb',
            category: 'tags'
        };
        return icons[type] || 'search';
    }

    highlightMatch(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    performSearch(query) {
        if (!query.trim()) return;
        
        // Add to search history
        this.addToSearchHistory(query);
        
        // Show search results
        this.displaySearchResults(query);
        
        // Clear suggestions
        this.hideSuggestions();
    }

    clearSearch() {
        const searchInput = document.getElementById('global-search');
        const searchClear = document.getElementById('search-clear');
        
        searchInput.value = '';
        searchClear.style.display = 'none';
        this.hideSuggestions();
        this.clearSearchResults();
    }

    // Advanced Filters
    setupAdvancedFilters() {
        this.createAdvancedFilterPanel();
        this.initializeFilters();
    }

    createAdvancedFilterPanel() {
        const filterPanel = document.createElement('div');
        filterPanel.className = 'advanced-filter-panel';
        filterPanel.id = 'advanced-filters';
        filterPanel.innerHTML = `
            <div class="filter-header">
                <h3>Advanced Filters</h3>
                <button class="filter-close" id="close-filters">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="filter-content">
                <div class="filter-group">
                    <label>Date Range</label>
                    <div class="date-range-inputs">
                        <input type="date" id="filter-date-from" />
                        <span>to</span>
                        <input type="date" id="filter-date-to" />
                    </div>
                </div>
                <div class="filter-group">
                    <label>Amount Range</label>
                    <div class="amount-range-inputs">
                        <input type="number" id="filter-amount-min" placeholder="Min amount" />
                        <input type="number" id="filter-amount-max" placeholder="Max amount" />
                    </div>
                </div>
                <div class="filter-group">
                    <label>Categories</label>
                    <div class="category-checkboxes" id="category-filters">
                        <!-- Populated dynamically -->
                    </div>
                </div>
                <div class="filter-actions">
                    <button class="btn btn-primary" id="apply-filters">Apply Filters</button>
                    <button class="btn btn-secondary" id="clear-filters">Clear All</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(filterPanel);
        this.bindFilterEvents();
    }

    bindFilterEvents() {
        const closeBtn = document.getElementById('close-filters');
        const applyBtn = document.getElementById('apply-filters');
        const clearBtn = document.getElementById('clear-filters');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.hideAdvancedFilters();
            });
        }
        
        if (applyBtn) {
            applyBtn.addEventListener('click', () => {
                this.applyAdvancedFilters();
            });
        }
        
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearAllFilters();
            });
        }
    }

    // Keyboard Navigation
    setupKeyboardNavigation() {
        this.registerShortcuts();
        this.setupFocusManagement();
        this.setupAccessibilityFeatures();
    }

    registerShortcuts() {
        // Global shortcuts
        this.keyboardShortcuts = {
            'Ctrl+K': () => this.focusSearch(),
            'Ctrl+/': () => this.showShortcutsHelp(),
            'Ctrl+N': () => this.createNewTransaction(),
            'Ctrl+F': () => this.showAdvancedFilters(),
            'Escape': () => this.handleEscape(),
            'Ctrl+1': () => this.switchToSection('dashboard'),
            'Ctrl+2': () => this.switchToSection('chat'),
            'Ctrl+3': () => this.switchToSection('transactions'),
            'Tab': (e) => this.handleTabNavigation(e),
            'Shift+Tab': (e) => this.handleTabNavigation(e, true)
        };

        document.addEventListener('keydown', (e) => {
            const shortcut = this.getShortcutString(e);
            if (this.keyboardShortcuts[shortcut]) {
                e.preventDefault();
                this.keyboardShortcuts[shortcut](e);
            }
        });
    }

    getShortcutString(event) {
        const parts = [];
        if (event.ctrlKey) parts.push('Ctrl');
        if (event.altKey) parts.push('Alt');
        if (event.shiftKey) parts.push('Shift');
        parts.push(event.key);
        return parts.join('+');
    }

    focusSearch() {
        const searchInput = document.getElementById('global-search');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    showShortcutsHelp() {
        const modal = this.app.modal.show({
            title: 'Keyboard Shortcuts',
            content: this.generateShortcutsHelp(),
            size: 'medium'
        });
    }

    generateShortcutsHelp() {
        return `
            <div class="shortcuts-help">
                <div class="shortcut-section">
                    <h4>Navigation</h4>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>1</kbd> <span>Dashboard</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>2</kbd> <span>AI Chat</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>3</kbd> <span>Transactions</span>
                    </div>
                </div>
                <div class="shortcut-section">
                    <h4>Search & Filter</h4>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>K</kbd> <span>Focus Search</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>F</kbd> <span>Advanced Filters</span>
                    </div>
                </div>
                <div class="shortcut-section">
                    <h4>Actions</h4>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>N</kbd> <span>New Transaction</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Escape</kbd> <span>Close/Cancel</span>
                    </div>
                    <div class="shortcut-item">
                        <kbd>Ctrl</kbd> + <kbd>/</kbd> <span>Show Help</span>
                    </div>
                </div>
            </div>
        `;
    }

    // Drag and Drop
    setupDragAndDrop() {
        this.setupTransactionDragDrop();
        this.setupCategoryDragDrop();
        this.setupFileDragDrop();
    }

    setupTransactionDragDrop() {
        // Enable dragging of transaction items
        document.addEventListener('dragstart', (e) => {
            if (e.target.closest('.transaction-item')) {
                const transactionId = e.target.closest('.transaction-item').dataset.transactionId;
                e.dataTransfer.setData('text/plain', transactionId);
                e.dataTransfer.setData('application/x-transaction', transactionId);
                e.target.classList.add('dragging');
            }
        });

        document.addEventListener('dragend', (e) => {
            e.target.classList.remove('dragging');
            document.querySelectorAll('.drag-over').forEach(el => {
                el.classList.remove('drag-over');
            });
        });
    }

    setupCategoryDragDrop() {
        // Setup category drop zones
        document.querySelectorAll('.category-zone').forEach(zone => {
            zone.addEventListener('dragover', (e) => {
                e.preventDefault();
                zone.classList.add('drag-over');
            });

            zone.addEventListener('dragleave', (e) => {
                zone.classList.remove('drag-over');
            });

            zone.addEventListener('drop', (e) => {
                e.preventDefault();
                const transactionId = e.dataTransfer.getData('application/x-transaction');
                const newCategory = zone.dataset.category;
                
                if (transactionId && newCategory) {
                    this.updateTransactionCategory(transactionId, newCategory);
                }
                
                zone.classList.remove('drag-over');
            });
        });
    }

    setupFileDragDrop() {
        const dropZone = document.createElement('div');
        dropZone.className = 'file-drop-zone';
        dropZone.innerHTML = `
            <div class="drop-content">
                <i class="fas fa-cloud-upload-alt"></i>
                <p>Drop files here to import transactions</p>
                <small>Supports CSV, Excel, and PDF files</small>
            </div>
        `;

        document.body.appendChild(dropZone);

        document.addEventListener('dragover', (e) => {
            e.preventDefault();
            if (this.hasFiles(e.dataTransfer)) {
                dropZone.classList.add('active');
            }
        });

        document.addEventListener('dragleave', (e) => {
            if (!document.elementFromPoint(e.clientX, e.clientY)) {
                dropZone.classList.remove('active');
            }
        });

        document.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('active');
            
            if (e.dataTransfer.files.length > 0) {
                this.handleFileUpload(e.dataTransfer.files);
            }
        });
    }

    hasFiles(dataTransfer) {
        return dataTransfer.types.includes('Files');
    }

    handleFileUpload(files) {
        Array.from(files).forEach(file => {
            if (this.isValidFileType(file)) {
                this.processUploadedFile(file);
            } else {
                this.app.showNotification(`Unsupported file type: ${file.name}`, 'error');
            }
        });
    }

    isValidFileType(file) {
        const validTypes = [
            'text/csv',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/pdf'
        ];
        return validTypes.includes(file.type);
    }

    // Sortable Columns
    setupSortableColumns() {
        document.querySelectorAll('.sortable-header').forEach(header => {
            header.addEventListener('click', (e) => {
                const column = e.target.dataset.column;
                this.sortByColumn(column);
            });
        });
    }

    sortByColumn(column) {
        const newDirection = this.sortState.column === column && this.sortState.direction === 'asc' ? 'desc' : 'asc';
        
        this.sortState = {
            column: column,
            direction: newDirection
        };

        this.updateSortIndicators();
        this.applySorting();
    }

    updateSortIndicators() {
        document.querySelectorAll('.sort-indicator').forEach(indicator => {
            indicator.remove();
        });

        const activeHeader = document.querySelector(`[data-column="${this.sortState.column}"]`);
        if (activeHeader) {
            const indicator = document.createElement('i');
            indicator.className = `fas fa-sort-${this.sortState.direction === 'asc' ? 'up' : 'down'} sort-indicator`;
            activeHeader.appendChild(indicator);
        }
    }

    // Quick Actions
    setupQuickActions() {
        this.createQuickActionBar();
        this.setupQuickActionShortcuts();
    }

    createQuickActionBar() {
        const quickActions = document.createElement('div');
        quickActions.className = 'quick-action-bar';
        quickActions.innerHTML = `
            <div class="quick-actions">
                <button class="quick-action" data-action="new-transaction" title="New Transaction (Ctrl+N)">
                    <i class="fas fa-plus"></i>
                </button>
                <button class="quick-action" data-action="search" title="Search (Ctrl+K)">
                    <i class="fas fa-search"></i>
                </button>
                <button class="quick-action" data-action="filter" title="Filters (Ctrl+F)">
                    <i class="fas fa-filter"></i>
                </button>
                <button class="quick-action" data-action="export" title="Export Data">
                    <i class="fas fa-download"></i>
                </button>
                <button class="quick-action" data-action="help" title="Help (Ctrl+/)">
                    <i class="fas fa-question-circle"></i>
                </button>
            </div>
        `;

        document.body.appendChild(quickActions);
        this.bindQuickActionEvents();
    }

    bindQuickActionEvents() {
        document.querySelectorAll('.quick-action').forEach(action => {
            action.addEventListener('click', (e) => {
                const actionType = e.target.closest('.quick-action').dataset.action;
                this.executeQuickAction(actionType);
            });
        });
    }

    executeQuickAction(action) {
        switch (action) {
            case 'new-transaction':
                this.createNewTransaction();
                break;
            case 'search':
                this.focusSearch();
                break;
            case 'filter':
                this.showAdvancedFilters();
                break;
            case 'export':
                this.exportData();
                break;
            case 'help':
                this.showShortcutsHelp();
                break;
        }
    }

    // Context Menus
    setupContextMenus() {
        document.addEventListener('contextmenu', (e) => {
            if (e.target.closest('.transaction-item')) {
                e.preventDefault();
                this.showTransactionContextMenu(e, e.target.closest('.transaction-item'));
            } else if (e.target.closest('.chart-card')) {
                e.preventDefault();
                this.showChartContextMenu(e, e.target.closest('.chart-card'));
            }
        });

        // Hide context menu on click outside
        document.addEventListener('click', () => {
            this.hideContextMenu();
        });
    }

    showTransactionContextMenu(event, transactionElement) {
        const menu = this.createContextMenu([
            { label: 'Edit Transaction', action: 'edit', icon: 'edit' },
            { label: 'Duplicate', action: 'duplicate', icon: 'copy' },
            { label: 'Change Category', action: 'category', icon: 'tags' },
            { label: 'Add Note', action: 'note', icon: 'sticky-note' },
            { separator: true },
            { label: 'Delete', action: 'delete', icon: 'trash', danger: true }
        ]);

        this.positionContextMenu(menu, event);
        this.bindContextMenuActions(menu, transactionElement);
    }

    createContextMenu(items) {
        const menu = document.createElement('div');
        menu.className = 'context-menu';
        
        menu.innerHTML = items.map(item => {
            if (item.separator) {
                return '<div class="context-menu-separator"></div>';
            }
            
            return `
                <div class="context-menu-item ${item.danger ? 'danger' : ''}" data-action="${item.action}">
                    <i class="fas fa-${item.icon}"></i>
                    <span>${item.label}</span>
                </div>
            `;
        }).join('');

        document.body.appendChild(menu);
        return menu;
    }

    // Bulk Operations
    setupBulkOperations() {
        this.createBulkActionBar();
        this.setupSelectionHandlers();
    }

    createBulkActionBar() {
        const bulkBar = document.createElement('div');
        bulkBar.className = 'bulk-action-bar';
        bulkBar.innerHTML = `
            <div class="bulk-info">
                <span id="selected-count">0</span> items selected
            </div>
            <div class="bulk-actions">
                <button class="bulk-action" data-action="categorize">
                    <i class="fas fa-tags"></i> Categorize
                </button>
                <button class="bulk-action" data-action="export">
                    <i class="fas fa-download"></i> Export
                </button>
                <button class="bulk-action" data-action="delete">
                    <i class="fas fa-trash"></i> Delete
                </button>
                <button class="bulk-action" data-action="clear" id="clear-selection">
                    <i class="fas fa-times"></i> Clear
                </button>
            </div>
        `;

        document.body.appendChild(bulkBar);
        this.bindBulkActionEvents();
    }

    // Utility Methods
    switchToSection(sectionName) {
        const section = document.querySelector(`[data-section="${sectionName}"]`);
        if (section) {
            section.click();
        }
    }

    handleEscape() {
        // Close any open modals, dropdowns, or panels
        this.hideAdvancedFilters();
        this.hideContextMenu();
        this.clearSearch();
        
        // Clear any active selections
        this.clearSelections();
    }

    hideSuggestions() {
        const suggestions = document.getElementById('search-suggestions');
        if (suggestions) {
            suggestions.style.display = 'none';
        }
    }

    hideAdvancedFilters() {
        const panel = document.getElementById('advanced-filters');
        if (panel) {
            panel.classList.remove('active');
        }
    }

    hideContextMenu() {
        document.querySelectorAll('.context-menu').forEach(menu => {
            menu.remove();
        });
    }

    clearSelections() {
        document.querySelectorAll('.selected').forEach(item => {
            item.classList.remove('selected');
        });
        this.updateBulkActionBar(0);
    }

    updateBulkActionBar(count) {
        const bulkBar = document.querySelector('.bulk-action-bar');
        const countElement = document.getElementById('selected-count');
        
        if (countElement) {
            countElement.textContent = count;
        }
        
        if (bulkBar) {
            bulkBar.style.display = count > 0 ? 'flex' : 'none';
        }
    }

    // Public API methods
    performGlobalSearch(query) {
        return this.performSearch(query);
    }

    addFilter(type, value) {
        this.filters.active[type] = value;
        this.applyFilters();
    }

    removeFilter(type) {
        delete this.filters.active[type];
        this.applyFilters();
    }

    exportData(format = 'csv') {
        // Implementation for data export
        this.app.showNotification(`Exporting data as ${format.toUpperCase()}...`, 'info');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (window.app) {
        window.app.interactions = new AdvancedInteractions(window.app);
    }
});

// Export for other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdvancedInteractions;
}