/**
 * Session Management Component
 * Handles conversation history, context display, and session control interfaces
 */
class SessionManager {
    constructor(app) {
        this.app = app;
        this.sessions = [];
        this.currentSession = null;
        this.sessionStorage = 'financial-ai-sessions';
        this.maxSessions = 50;
        
        this.init();
    }

    /**
     * Initialize session management
     */
    init() {
        this.loadSessions();
        this.createCurrentSession();
        this.setupGlobalSessionListener();
    }

    /**
     * Load sessions from local storage
     */
    loadSessions() {
        try {
            const savedSessions = localStorage.getItem(this.sessionStorage);
            if (savedSessions) {
                this.sessions = JSON.parse(savedSessions);
                // Clean up old sessions
                this.cleanupOldSessions();
            }
        } catch (error) {
            console.error('Error loading sessions:', error);
            this.sessions = [];
        }
    }

    /**
     * Save sessions to local storage
     */
    saveSessions() {
        try {
            localStorage.setItem(this.sessionStorage, JSON.stringify(this.sessions));
        } catch (error) {
            console.error('Error saving sessions:', error);
        }
    }

    /**
     * Create a new session for the current app instance
     */
    createCurrentSession() {
        this.currentSession = {
            id: this.generateSessionId(),
            timestamp: Date.now(),
            userAgent: navigator.userAgent,
            interactions: [],
            context: {},
            duration: 0,
            lastActivity: Date.now()
        };
        
        this.sessions.unshift(this.currentSession);
        this.saveSessions();
    }

    /**
     * Log user interaction
     */
    logInteraction(type, data) {
        if (!this.currentSession) return;

        const interaction = {
            id: this.generateInteractionId(),
            type,
            data,
            timestamp: Date.now()
        };

        this.currentSession.interactions.push(interaction);
        this.currentSession.lastActivity = Date.now();
        this.currentSession.duration = Date.now() - this.currentSession.timestamp;
        
        // Keep only recent interactions
        if (this.currentSession.interactions.length > 100) {
            this.currentSession.interactions = this.currentSession.interactions.slice(-100);
        }
        
        this.saveSessions();
    }

    /**
     * Update session context
     */
    updateContext(key, value) {
        if (!this.currentSession) return;

        this.currentSession.context[key] = value;
        this.saveSessions();
    }

    /**
     * Create session management UI
     */
    createSessionUI() {
        const sessionModal = document.createElement('div');
        sessionModal.className = 'modal session-modal';
        sessionModal.innerHTML = `
            <div class="modal-content session-modal-content">
                <div class="modal-header">
                    <h3>Session History</h3>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="session-tabs">
                        <button class="session-tab active" data-tab="current">Current Session</button>
                        <button class="session-tab" data-tab="history">Session History</button>
                        <button class="session-tab" data-tab="analytics">Analytics</button>
                    </div>
                    
                    <div class="session-tab-content">
                        <!-- Current Session Tab -->
                        <div class="session-tab-pane active" id="current-session">
                            <div class="session-info-card">
                                <div class="session-info-header">
                                    <h4>Current Session</h4>
                                    <div class="session-duration">
                                        <i class="fas fa-clock"></i>
                                        <span id="current-session-duration">0m</span>
                                    </div>
                                </div>
                                <div class="session-stats-grid">
                                    <div class="session-stat">
                                        <div class="stat-value" id="interactions-count">0</div>
                                        <div class="stat-label">Interactions</div>
                                    </div>
                                    <div class="session-stat">
                                        <div class="stat-value" id="sections-visited">0</div>
                                        <div class="stat-label">Sections</div>
                                    </div>
                                    <div class="session-stat">
                                        <div class="stat-value" id="queries-made">0</div>
                                        <div class="stat-label">Queries</div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="current-interactions">
                                <h4>Recent Activity</h4>
                                <div class="interactions-timeline" id="interactions-timeline">
                                    <!-- Timeline items will be populated here -->
                                </div>
                            </div>
                        </div>
                        
                        <!-- Session History Tab -->
                        <div class="session-tab-pane" id="session-history">
                            <div class="session-history-controls">
                                <select id="history-filter">
                                    <option value="all">All Sessions</option>
                                    <option value="today">Today</option>
                                    <option value="week">This Week</option>
                                    <option value="month">This Month</option>
                                </select>
                                <button id="clear-history" class="btn btn-danger">
                                    <i class="fas fa-trash"></i>
                                    Clear History
                                </button>
                            </div>
                            
                            <div class="sessions-list" id="sessions-list">
                                <!-- Session history items will be populated here -->
                            </div>
                        </div>
                        
                        <!-- Analytics Tab -->
                        <div class="session-tab-pane" id="session-analytics">
                            <div class="analytics-grid">
                                <div class="analytics-card">
                                    <h4>Usage Patterns</h4>
                                    <canvas id="usage-patterns-chart" width="300" height="150"></canvas>
                                </div>
                                <div class="analytics-card">
                                    <h4>Feature Usage</h4>
                                    <div class="feature-usage-list" id="feature-usage-list">
                                        <!-- Feature usage stats will be populated here -->
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary close-modal">Close</button>
                    <button class="btn btn-primary" id="export-session-data">
                        <i class="fas fa-download"></i>
                        Export Data
                    </button>
                </div>
            </div>
        `;

        // Add styles
        if (!document.querySelector('#session-manager-styles')) {
            const style = document.createElement('style');
            style.id = 'session-manager-styles';
            style.textContent = `
                .session-modal-content {
                    max-width: 800px;
                    width: 90%;
                }

                .session-tabs {
                    display: flex;
                    border-bottom: 1px solid var(--border-color);
                    margin-bottom: 2rem;
                }

                .session-tab {
                    padding: 1rem 1.5rem;
                    border: none;
                    background: none;
                    color: var(--text-secondary);
                    cursor: pointer;
                    border-bottom: 2px solid transparent;
                    transition: all 0.3s ease;
                }

                .session-tab:hover {
                    color: var(--text-primary);
                }

                .session-tab.active {
                    color: var(--primary-color);
                    border-bottom-color: var(--primary-color);
                }

                .session-tab-pane {
                    display: none;
                }

                .session-tab-pane.active {
                    display: block;
                }

                .session-info-card {
                    background: var(--bg-secondary);
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                }

                .session-info-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 1.5rem;
                }

                .session-duration {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    color: var(--text-secondary);
                }

                .session-stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                    gap: 1rem;
                }

                .session-stat {
                    text-align: center;
                    padding: 1rem;
                    background: var(--bg-primary);
                    border-radius: 8px;
                }

                .stat-value {
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: var(--primary-color);
                }

                .stat-label {
                    font-size: 0.8rem;
                    color: var(--text-secondary);
                    margin-top: 0.5rem;
                }

                .interactions-timeline {
                    max-height: 300px;
                    overflow-y: auto;
                }

                .timeline-item {
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    padding: 1rem 0;
                    border-bottom: 1px solid var(--border-color);
                }

                .timeline-icon {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 0.9rem;
                    flex-shrink: 0;
                }

                .timeline-content {
                    flex: 1;
                }

                .timeline-action {
                    font-weight: 500;
                    color: var(--text-primary);
                }

                .timeline-details {
                    font-size: 0.8rem;
                    color: var(--text-secondary);
                    margin-top: 0.3rem;
                }

                .timeline-time {
                    font-size: 0.8rem;
                    color: var(--text-secondary);
                }

                .session-history-controls {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 1.5rem;
                }

                .session-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 1rem;
                    background: var(--bg-secondary);
                    border-radius: 8px;
                    margin-bottom: 0.8rem;
                    transition: all 0.3s ease;
                    cursor: pointer;
                }

                .session-item:hover {
                    background: var(--bg-tertiary);
                    transform: translateX(4px);
                }

                .session-details h5 {
                    margin: 0 0 0.5rem 0;
                    color: var(--text-primary);
                }

                .session-meta {
                    font-size: 0.8rem;
                    color: var(--text-secondary);
                }

                .session-stats {
                    text-align: right;
                    font-size: 0.8rem;
                    color: var(--text-secondary);
                }

                .analytics-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 2rem;
                }

                .analytics-card {
                    background: var(--bg-secondary);
                    padding: 1.5rem;
                    border-radius: 12px;
                }

                .analytics-card h4 {
                    margin: 0 0 1rem 0;
                    color: var(--text-primary);
                }

                .feature-usage-list {
                    display: flex;
                    flex-direction: column;
                    gap: 0.8rem;
                }

                .feature-usage-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 0.8rem;
                    background: var(--bg-primary);
                    border-radius: 6px;
                }

                .feature-name {
                    font-weight: 500;
                    color: var(--text-primary);
                }

                .feature-count {
                    font-weight: 600;
                    color: var(--primary-color);
                }
            `;
            document.head.appendChild(style);
        }

        return sessionModal;
    }

    /**
     * Show session management UI
     */
    showSessionUI() {
        const existingModal = document.querySelector('.session-modal');
        if (existingModal) {
            existingModal.remove();
        }

        const modal = this.createSessionUI();
        document.body.appendChild(modal);

        // Show modal
        setTimeout(() => modal.classList.add('visible'), 10);

        // Setup event listeners
        this.setupSessionUIListeners(modal);

        // Populate data
        this.populateCurrentSessionData();
        this.populateSessionHistory();
        this.populateAnalytics();

        // Start real-time updates
        this.startSessionUIUpdates(modal);
    }

    /**
     * Setup event listeners for session UI
     */
    setupSessionUIListeners(modal) {
        // Close modal
        modal.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', () => {
                modal.classList.remove('visible');
                setTimeout(() => modal.remove(), 300);
            });
        });

        // Tab switching
        modal.querySelectorAll('.session-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabId = e.target.dataset.tab;
                
                // Update active tab
                modal.querySelectorAll('.session-tab').forEach(t => t.classList.remove('active'));
                e.target.classList.add('active');
                
                // Update active tab pane
                modal.querySelectorAll('.session-tab-pane').forEach(pane => pane.classList.remove('active'));
                modal.getElementById(tabId === 'current' ? 'current-session' : 
                                   tabId === 'history' ? 'session-history' : 'session-analytics').classList.add('active');
            });
        });

        // History filter
        const historyFilter = modal.querySelector('#history-filter');
        if (historyFilter) {
            historyFilter.addEventListener('change', () => {
                this.populateSessionHistory();
            });
        }

        // Clear history
        const clearHistoryBtn = modal.querySelector('#clear-history');
        if (clearHistoryBtn) {
            clearHistoryBtn.addEventListener('click', () => {
                if (confirm('Are you sure you want to clear all session history? This cannot be undone.')) {
                    this.clearSessionHistory();
                }
            });
        }

        // Export session data
        const exportBtn = modal.querySelector('#export-session-data');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportSessionData();
            });
        }
    }

    /**
     * Populate current session data
     */
    populateCurrentSessionData() {
        if (!this.currentSession) return;

        // Update duration
        const duration = Math.floor((Date.now() - this.currentSession.timestamp) / 60000);
        const durationEl = document.getElementById('current-session-duration');
        if (durationEl) durationEl.textContent = `${duration}m`;

        // Update stats
        const interactions = this.currentSession.interactions;
        
        const interactionsCount = document.getElementById('interactions-count');
        if (interactionsCount) interactionsCount.textContent = interactions.length;

        const sectionsVisited = new Set(interactions.filter(i => i.type === 'navigation').map(i => i.data.section));
        const sectionsEl = document.getElementById('sections-visited');
        if (sectionsEl) sectionsEl.textContent = sectionsVisited.size;

        const queriesCount = interactions.filter(i => i.type === 'chat' || i.type === 'search').length;
        const queriesEl = document.getElementById('queries-made');
        if (queriesEl) queriesEl.textContent = queriesCount;

        // Update timeline
        this.populateInteractionsTimeline();
    }

    /**
     * Populate interactions timeline
     */
    populateInteractionsTimeline() {
        const timeline = document.getElementById('interactions-timeline');
        if (!timeline || !this.currentSession) return;

        const recentInteractions = this.currentSession.interactions.slice(-10).reverse();

        timeline.innerHTML = recentInteractions.map(interaction => {
            const timeAgo = this.getTimeAgo(interaction.timestamp);
            const icon = this.getInteractionIcon(interaction.type);
            const iconColor = this.getInteractionIconColor(interaction.type);

            return `
                <div class="timeline-item">
                    <div class="timeline-icon" style="background: ${iconColor}; color: white;">
                        <i class="fas ${icon}"></i>
                    </div>
                    <div class="timeline-content">
                        <div class="timeline-action">${this.getInteractionDescription(interaction)}</div>
                        <div class="timeline-details">${this.getInteractionDetails(interaction)}</div>
                    </div>
                    <div class="timeline-time">${timeAgo}</div>
                </div>
            `;
        }).join('');
    }

    /**
     * Get interaction icon
     */
    getInteractionIcon(type) {
        const icons = {
            navigation: 'fa-compass',
            chat: 'fa-comment',
            search: 'fa-search',
            click: 'fa-mouse-pointer',
            export: 'fa-download',
            privacy: 'fa-shield-alt',
            insight: 'fa-lightbulb'
        };
        return icons[type] || 'fa-circle';
    }

    /**
     * Get interaction icon color
     */
    getInteractionIconColor(type) {
        const colors = {
            navigation: '#3b82f6',
            chat: '#10b981',
            search: '#f59e0b',
            click: '#6b7280',
            export: '#8b5cf6',
            privacy: '#ef4444',
            insight: '#f59e0b'
        };
        return colors[type] || '#6b7280';
    }

    /**
     * Get interaction description
     */
    getInteractionDescription(interaction) {
        switch (interaction.type) {
            case 'navigation':
                return `Visited ${interaction.data.section}`;
            case 'chat':
                return 'Asked AI assistant';
            case 'search':
                return 'Performed search';
            case 'click':
                return `Clicked ${interaction.data.element}`;
            case 'export':
                return 'Exported data';
            case 'privacy':
                return 'Updated privacy settings';
            case 'insight':
                return 'Viewed insight';
            default:
                return 'Unknown action';
        }
    }

    /**
     * Get interaction details
     */
    getInteractionDetails(interaction) {
        switch (interaction.type) {
            case 'navigation':
                return `Section: ${interaction.data.section}`;
            case 'chat':
                return interaction.data.query ? `Query: "${interaction.data.query.substring(0, 50)}..."` : 'Chat interaction';
            case 'search':
                return `Search: "${interaction.data.term}"`;
            case 'click':
                return interaction.data.details || '';
            default:
                return JSON.stringify(interaction.data).substring(0, 50);
        }
    }

    /**
     * Setup global session listener
     */
    setupGlobalSessionListener() {
        // Listen for navigation changes
        document.addEventListener('click', (e) => {
            if (e.target.dataset.section) {
                this.logInteraction('navigation', { section: e.target.dataset.section });
            } else if (e.target.closest('.nav-item')) {
                const navItem = e.target.closest('.nav-item');
                const section = navItem.dataset.section;
                if (section) {
                    this.logInteraction('navigation', { section });
                }
            }
        });

        // Listen for form submissions (search, chat, etc.)
        document.addEventListener('submit', (e) => {
            if (e.target.id === 'chat-form' || e.target.closest('#chat-form')) {
                const query = e.target.querySelector('input, textarea')?.value;
                this.logInteraction('chat', { query });
            }
        });
    }

    /**
     * Utility methods
     */
    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    generateInteractionId() {
        return `interaction_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
    }

    getTimeAgo(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return new Date(timestamp).toLocaleDateString();
    }

    cleanupOldSessions() {
        // Remove sessions older than 30 days
        const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
        this.sessions = this.sessions.filter(session => session.timestamp > thirtyDaysAgo);
        
        // Keep only the most recent sessions
        if (this.sessions.length > this.maxSessions) {
            this.sessions = this.sessions.slice(0, this.maxSessions);
        }
    }

    populateSessionHistory() {
        // Implementation for session history population
    }

    populateAnalytics() {
        // Implementation for analytics population
    }

    startSessionUIUpdates(modal) {
        // Real-time updates for current session
        const updateInterval = setInterval(() => {
            if (document.body.contains(modal)) {
                this.populateCurrentSessionData();
            } else {
                clearInterval(updateInterval);
            }
        }, 30000); // Update every 30 seconds
    }

    clearSessionHistory() {
        this.sessions = [this.currentSession].filter(Boolean);
        this.saveSessions();
        this.populateSessionHistory();
        this.app.showNotification('Session history cleared', 'success');
    }

    exportSessionData() {
        const exportData = {
            sessions: this.sessions,
            exportDate: new Date().toISOString(),
            totalSessions: this.sessions.length
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
            type: 'application/json' 
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `session-data-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        this.app.showNotification('Session data exported successfully', 'success');
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SessionManager;
} else {
    window.SessionManager = SessionManager;
}