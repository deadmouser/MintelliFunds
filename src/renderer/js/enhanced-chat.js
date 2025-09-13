/**
 * Enhanced Chat Interface
 * Advanced AI chat with context management, query suggestions, intent visualization, and session handling
 */
class EnhancedChatInterface {
    constructor(app) {
        this.app = app;
        this.messages = [];
        this.sessionContext = {
            activeTopics: [],
            userIntent: null,
            entities: {},
            conversationStage: 'introduction',
            lastQueryTime: null,
            contextRetentionTime: 900000, // 15 minutes
            maxContextMessages: 10
        };
        
        this.queryPatterns = {
            spending: {
                keywords: ['spend', 'expense', 'cost', 'bought', 'purchase', 'money'],
                entities: ['amount', 'category', 'date', 'merchant'],
                intents: ['spending_summary', 'category_analysis', 'spending_trends']
            },
            savings: {
                keywords: ['save', 'saving', 'goal', 'budget', 'target'],
                entities: ['amount', 'timeline', 'purpose'],
                intents: ['savings_progress', 'goal_setting', 'budget_advice']
            },
            investment: {
                keywords: ['invest', 'portfolio', 'stock', 'mutual fund', 'sip', 'return'],
                entities: ['amount', 'risk', 'timeline'],
                intents: ['investment_advice', 'portfolio_analysis', 'performance_review']
            },
            debt: {
                keywords: ['loan', 'debt', 'emi', 'credit card', 'payoff', 'interest'],
                entities: ['amount', 'rate', 'timeline'],
                intents: ['debt_strategy', 'payoff_plan', 'refinance_advice']
            },
            planning: {
                keywords: ['plan', 'future', 'retirement', 'tax', 'insurance'],
                entities: ['age', 'timeline', 'goals'],
                intents: ['financial_planning', 'retirement_planning', 'tax_planning']
            }
        };
        
        this.suggestionTemplates = {
            spending: [
                "What did I spend on groceries this month?",
                "Show me my largest expenses this week",
                "Compare my spending to last month",
                "Which category am I overspending on?"
            ],
            savings: [
                "How much should I save for an emergency fund?",
                "Am I on track with my savings goal?",
                "Help me create a budget to save ₹50,000",
                "What's the best way to increase my savings rate?"
            ],
            investment: [
                "Should I invest ₹10,000 this month?",
                "How is my portfolio performing?",
                "What's my investment risk profile?",
                "Suggest some good mutual funds"
            ],
            debt: [
                "What's the best strategy to pay off my debt?",
                "Should I prioritize credit card or loan payments?",
                "Calculate my debt-to-income ratio",
                "When will I be debt-free?"
            ],
            general: [
                "What's my net worth right now?",
                "Show me my financial health score",
                "What should I focus on financially?",
                "Give me a monthly financial summary"
            ]
        };
        
        this.init();
    }

    /**
     * Initialize the enhanced chat interface
     */
    init() {
        this.loadChatHistory();
        this.renderEnhancedChatInterface();
        this.setupEventListeners();
        this.startContextTimer();
        
        // Welcome message with capabilities
        if (this.messages.length === 0) {
            this.addSystemMessage('welcome');
        }
    }

    /**
     * Load chat history from local storage
     */
    loadChatHistory() {
        try {
            const savedMessages = localStorage.getItem('financial-ai-chat-history');
            if (savedMessages) {
                this.messages = JSON.parse(savedMessages);
            }
            
            const savedContext = localStorage.getItem('financial-ai-session-context');
            if (savedContext) {
                const context = JSON.parse(savedContext);
                // Only restore context if it's recent
                if (Date.now() - context.lastQueryTime < this.sessionContext.contextRetentionTime) {
                    this.sessionContext = { ...this.sessionContext, ...context };
                }
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    /**
     * Save chat history and context
     */
    saveChatState() {
        try {
            // Keep only recent messages
            const recentMessages = this.messages.slice(-50);
            localStorage.setItem('financial-ai-chat-history', JSON.stringify(recentMessages));
            
            // Update context timestamp
            this.sessionContext.lastQueryTime = Date.now();
            localStorage.setItem('financial-ai-session-context', JSON.stringify(this.sessionContext));
        } catch (error) {
            console.error('Error saving chat state:', error);
        }
    }

    /**
     * Render the enhanced chat interface
     */
    renderEnhancedChatInterface() {
        const chatSection = document.getElementById('chat-section');
        if (!chatSection) return;

        // Replace the existing chat interface with enhanced version
        chatSection.innerHTML = `
            <div class="section-header">
                <h1>AI Financial Assistant</h1>
                <div class="header-actions">
                    <div class="chat-controls">
                        <button id="toggle-context" class="btn btn-secondary" title="Toggle context panel">
                            <i class="fas fa-brain"></i>
                            Context
                        </button>
                        <button id="export-chat" class="btn btn-secondary" title="Export chat history">
                            <i class="fas fa-download"></i>
                            Export
                        </button>
                        <button id="clear-chat" class="btn btn-secondary" title="Clear chat history">
                            <i class="fas fa-trash"></i>
                            Clear
                        </button>
                    </div>
                </div>
            </div>

            <div class="enhanced-chat-container">
                <!-- Context Panel -->
                <div class="context-panel" id="context-panel">
                    <div class="context-header">
                        <h3>Conversation Context</h3>
                        <button id="close-context" class="close-btn">×</button>
                    </div>
                    
                    <div class="context-content">
                        <div class="context-section">
                            <h4>Active Topics</h4>
                            <div class="active-topics" id="active-topics">
                                <div class="no-topics">No active topics yet</div>
                            </div>
                        </div>
                        
                        <div class="context-section">
                            <h4>Detected Intent</h4>
                            <div class="current-intent" id="current-intent">
                                <div class="no-intent">Ask me something to get started!</div>
                            </div>
                        </div>
                        
                        <div class="context-section">
                            <h4>Key Entities</h4>
                            <div class="extracted-entities" id="extracted-entities">
                                <div class="no-entities">No entities detected</div>
                            </div>
                        </div>
                        
                        <div class="context-section">
                            <h4>Session Stats</h4>
                            <div class="session-stats" id="session-stats">
                                <div class="stat-item">
                                    <span class="stat-label">Messages:</span>
                                    <span class="stat-value" id="message-count">0</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Session Duration:</span>
                                    <span class="stat-value" id="session-duration">0m</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Topics Discussed:</span>
                                    <span class="stat-value" id="topics-count">0</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Main Chat Area -->
                <div class="main-chat-area">
                    <!-- Intent Indicator -->
                    <div class="intent-indicator" id="intent-indicator" style="display: none;">
                        <div class="intent-content">
                            <i class="fas fa-lightbulb"></i>
                            <span class="intent-text">I think you're asking about...</span>
                            <button class="intent-close">×</button>
                        </div>
                    </div>

                    <!-- Chat Messages -->
                    <div class="chat-messages enhanced-messages" id="chat-messages">
                        <!-- Messages will be populated here -->
                    </div>
                    
                    <!-- Smart Suggestions -->
                    <div class="smart-suggestions" id="smart-suggestions">
                        <div class="suggestions-header">
                            <h4>Smart Suggestions</h4>
                            <div class="suggestion-categories">
                                <button class="category-btn active" data-category="general">General</button>
                                <button class="category-btn" data-category="spending">Spending</button>
                                <button class="category-btn" data-category="savings">Savings</button>
                                <button class="category-btn" data-category="investment">Investment</button>
                                <button class="category-btn" data-category="debt">Debt</button>
                            </div>
                        </div>
                        <div class="suggestions-content" id="suggestions-content">
                            <!-- Dynamic suggestions will be populated here -->
                        </div>
                    </div>

                    <!-- Enhanced Input Area -->
                    <div class="enhanced-chat-input">
                        <div class="input-enhancements">
                            <div class="typing-feedback" id="typing-feedback" style="display: none;">
                                <i class="fas fa-brain"></i>
                                <span>Analyzing your query...</span>
                            </div>
                            
                            <div class="entity-highlights" id="entity-highlights" style="display: none;">
                                <div class="highlight-label">Detected:</div>
                                <div class="highlights-list" id="highlights-list">
                                    <!-- Dynamic entity highlights -->
                                </div>
                            </div>
                        </div>
                        
                        <div class="chat-input-wrapper">
                            <div class="input-container">
                                <textarea id="chat-input" 
                                    placeholder="Ask me anything about your finances... (Try: 'What did I spend on food this month?')" 
                                    rows="1"></textarea>
                                <div class="input-actions">
                                    <button id="voice-input" class="input-btn" title="Voice input (coming soon)" disabled>
                                        <i class="fas fa-microphone"></i>
                                    </button>
                                    <button id="send-message" class="input-btn send-btn" title="Send message">
                                        <i class="fas fa-paper-plane"></i>
                                    </button>
                                </div>
                            </div>
                        </div>

                        <div class="input-status">
                            <div id="typing-indicator" class="typing-indicator" style="display: none;">
                                <span></span><span></span><span></span>
                            </div>
                            <div class="character-count" id="character-count">0/1000</div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Populate existing messages
        this.renderMessages();
        this.updateSuggestions('general');
        this.updateContextPanel();
    }

    /**
     * Render all messages in the chat
     */
    renderMessages() {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;

        messagesContainer.innerHTML = this.messages.map(message => this.renderMessage(message)).join('');
        this.scrollToBottom();
    }

    /**
     * Render a single message
     * @param {Object} message - Message object
     * @returns {string} HTML string for the message
     */
    renderMessage(message) {
        const timeAgo = this.getTimeAgo(message.timestamp);
        
        if (message.type === 'system') {
            return this.renderSystemMessage(message);
        }

        const isUser = message.type === 'user';
        const messageClass = isUser ? 'user-message' : 'ai-message';
        
        let messageContent = '';
        
        if (isUser) {
            messageContent = `
                <div class="message ${messageClass}">
                    <div class="message-content">
                        <div class="message-text">${this.escapeHtml(message.text)}</div>
                        ${message.entities ? this.renderEntities(message.entities) : ''}
                        <div class="message-time">${timeAgo}</div>
                    </div>
                    <div class="message-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                </div>
            `;
        } else {
            messageContent = `
                <div class="message ${messageClass}">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-text">${this.formatAIResponse(message.text)}</div>
                        ${message.insights ? this.renderInsights(message.insights) : ''}
                        ${message.actions ? this.renderActions(message.actions) : ''}
                        <div class="message-time">${timeAgo}</div>
                        <div class="message-actions">
                            <button class="message-action-btn" onclick="enhancedChat.rateMessage('${message.id}', 'up')">
                                <i class="fas fa-thumbs-up"></i>
                            </button>
                            <button class="message-action-btn" onclick="enhancedChat.rateMessage('${message.id}', 'down')">
                                <i class="fas fa-thumbs-down"></i>
                            </button>
                            <button class="message-action-btn" onclick="enhancedChat.copyMessage('${message.id}')">
                                <i class="fas fa-copy"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }
        
        return messageContent;
    }

    /**
     * Render system messages (welcome, status updates, etc.)
     * @param {Object} message - System message object
     * @returns {string} HTML string for system message
     */
    renderSystemMessage(message) {
        if (message.subtype === 'welcome') {
            return `
                <div class="system-message welcome-message">
                    <div class="welcome-content">
                        <div class="welcome-header">
                            <i class="fas fa-robot"></i>
                            <h3>Welcome to your Financial AI Assistant!</h3>
                        </div>
                        <div class="welcome-body">
                            <p>I'm here to help you understand your finances better. I can:</p>
                            <ul class="capabilities-list">
                                <li><i class="fas fa-chart-line"></i> Analyze your spending patterns and trends</li>
                                <li><i class="fas fa-target"></i> Help you set and track financial goals</li>
                                <li><i class="fas fa-lightbulb"></i> Provide personalized financial insights</li>
                                <li><i class="fas fa-calculator"></i> Assist with budgeting and planning</li>
                                <li><i class="fas fa-shield-alt"></i> Respect your privacy preferences</li>
                            </ul>
                            <div class="welcome-suggestion">
                                <p>Try asking me:</p>
                                <div class="sample-queries">
                                    <button class="sample-query" onclick="enhancedChat.sendSampleQuery('What\\'s my spending pattern this month?')">
                                        "What's my spending pattern this month?"
                                    </button>
                                    <button class="sample-query" onclick="enhancedChat.sendSampleQuery('Help me save ₹50,000 for vacation')">
                                        "Help me save ₹50,000 for vacation"
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        return `
            <div class="system-message">
                <div class="system-content">
                    <i class="fas fa-info-circle"></i>
                    <span>${message.text}</span>
                </div>
            </div>
        `;
    }

    /**
     * Render detected entities for a message
     * @param {Object} entities - Extracted entities
     * @returns {string} HTML string for entities
     */
    renderEntities(entities) {
        if (!entities || Object.keys(entities).length === 0) return '';
        
        const entityTags = Object.entries(entities).map(([type, values]) => {
            const valueList = Array.isArray(values) ? values : [values];
            return valueList.map(value => `
                <span class="entity-tag entity-${type}" title="${type}">
                    ${value}
                </span>
            `).join('');
        }).join('');
        
        return `<div class="message-entities">${entityTags}</div>`;
    }

    /**
     * Render AI insights section
     * @param {Array} insights - Array of insight objects
     * @returns {string} HTML string for insights
     */
    renderInsights(insights) {
        if (!insights || insights.length === 0) return '';
        
        const insightsList = insights.map(insight => `
            <div class="insight-item insight-${insight.type}">
                <div class="insight-icon">
                    <i class="fas ${this.getInsightIcon(insight.type)}"></i>
                </div>
                <div class="insight-content">
                    <div class="insight-title">${insight.title}</div>
                    <div class="insight-description">${insight.description}</div>
                    ${insight.value ? `<div class="insight-value">${insight.value}</div>` : ''}
                </div>
            </div>
        `).join('');
        
        return `
            <div class="message-insights">
                <div class="insights-header">Key Insights</div>
                <div class="insights-list">${insightsList}</div>
            </div>
        `;
    }

    /**
     * Render suggested actions for a message
     * @param {Array} actions - Array of action objects
     * @returns {string} HTML string for actions
     */
    renderActions(actions) {
        if (!actions || actions.length === 0) return '';
        
        const actionButtons = actions.map(action => `
            <button class="action-btn action-${action.type}" 
                onclick="enhancedChat.executeAction('${action.type}', ${JSON.stringify(action.params).replace(/"/g, '&quot;')})">
                <i class="fas ${action.icon || 'fa-arrow-right'}"></i>
                ${action.label}
            </button>
        `).join('');
        
        return `
            <div class="message-actions-panel">
                <div class="actions-header">Suggested Actions</div>
                <div class="actions-list">${actionButtons}</div>
            </div>
        `;
    }

    /**
     * Update smart suggestions based on category or context
     * @param {string} category - Suggestion category
     */
    updateSuggestions(category) {
        const suggestionsContainer = document.getElementById('suggestions-content');
        if (!suggestionsContainer) return;

        const suggestions = this.suggestionTemplates[category] || this.suggestionTemplates.general;
        
        // Add context-aware suggestions if available
        const contextualSuggestions = this.getContextualSuggestions();
        const allSuggestions = [...contextualSuggestions, ...suggestions].slice(0, 8);
        
        suggestionsContainer.innerHTML = allSuggestions.map(suggestion => `
            <button class="suggestion-btn" onclick="enhancedChat.sendSampleQuery('${suggestion.replace(/'/g, '\\\')}')">
                ${suggestion}
            </button>
        `).join('');

        // Update category buttons
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.category === category);
        });
    }

    /**
     * Get contextual suggestions based on conversation history
     * @returns {Array} Array of contextual suggestion strings
     */
    getContextualSuggestions() {
        const suggestions = [];
        
        // Suggest follow-up questions based on recent topics
        if (this.sessionContext.activeTopics.includes('spending')) {
            suggestions.push("Break down my spending by week");
            suggestions.push("Which merchant did I spend most at?");
        }
        
        if (this.sessionContext.activeTopics.includes('savings')) {
            suggestions.push("How can I increase my savings rate?");
            suggestions.push("What percentage of income should I save?");
        }
        
        // Suggest based on detected entities
        if (this.sessionContext.entities.amount) {
            suggestions.push(`Compare this to my average spending`);
        }
        
        if (this.sessionContext.entities.category) {
            suggestions.push(`Show trends for this category`);
        }
        
        return suggestions.slice(0, 3); // Limit contextual suggestions
    }

    /**
     * Update the context panel with current session information
     */
    updateContextPanel() {
        // Update active topics
        const topicsContainer = document.getElementById('active-topics');
        if (topicsContainer) {
            if (this.sessionContext.activeTopics.length === 0) {
                topicsContainer.innerHTML = '<div class="no-topics">No active topics yet</div>';
            } else {
                const topicTags = this.sessionContext.activeTopics.map(topic => `
                    <span class="topic-tag topic-${topic}">
                        <i class="fas ${this.getTopicIcon(topic)}"></i>
                        ${topic}
                    </span>
                `).join('');
                topicsContainer.innerHTML = topicTags;
            }
        }

        // Update current intent
        const intentContainer = document.getElementById('current-intent');
        if (intentContainer) {
            if (!this.sessionContext.userIntent) {
                intentContainer.innerHTML = '<div class="no-intent">Ask me something to get started!</div>';
            } else {
                intentContainer.innerHTML = `
                    <div class="intent-display">
                        <div class="intent-type">${this.sessionContext.userIntent}</div>
                        <div class="intent-confidence">Confidence: High</div>
                    </div>
                `;
            }
        }

        // Update extracted entities
        const entitiesContainer = document.getElementById('extracted-entities');
        if (entitiesContainer) {
            const entityEntries = Object.entries(this.sessionContext.entities);
            if (entityEntries.length === 0) {
                entitiesContainer.innerHTML = '<div class="no-entities">No entities detected</div>';
            } else {
                const entityTags = entityEntries.map(([type, value]) => `
                    <span class="entity-display entity-${type}">
                        <span class="entity-type">${type}:</span>
                        <span class="entity-value">${Array.isArray(value) ? value.join(', ') : value}</span>
                    </span>
                `).join('');
                entitiesContainer.innerHTML = entityTags;
            }
        }

        // Update session stats
        this.updateSessionStats();
    }

    /**
     * Update session statistics
     */
    updateSessionStats() {
        const messageCountEl = document.getElementById('message-count');
        const durationEl = document.getElementById('session-duration');
        const topicsCountEl = document.getElementById('topics-count');

        if (messageCountEl) {
            messageCountEl.textContent = this.messages.filter(m => m.type !== 'system').length;
        }

        if (durationEl) {
            const duration = this.sessionContext.lastQueryTime ? 
                Date.now() - (this.sessionContext.lastQueryTime - this.sessionContext.contextRetentionTime) : 0;
            const minutes = Math.floor(duration / 60000);
            durationEl.textContent = `${minutes}m`;
        }

        if (topicsCountEl) {
            topicsCountEl.textContent = this.sessionContext.activeTopics.length;
        }
    }

    /**
     * Analyze user input for intent and entities
     * @param {string} text - User input text
     * @returns {Object} Analysis results
     */
    analyzeUserInput(text) {
        const lowerText = text.toLowerCase();
        const words = lowerText.split(/\s+/);
        
        let detectedIntent = null;
        let confidence = 0;
        const entities = {};
        
        // Intent classification
        for (const [category, pattern] of Object.entries(this.queryPatterns)) {
            const keywordMatches = pattern.keywords.filter(keyword => 
                lowerText.includes(keyword)
            ).length;
            
            const score = keywordMatches / pattern.keywords.length;
            if (score > confidence) {
                confidence = score;
                detectedIntent = category;
            }
        }
        
        // Entity extraction
        this.extractEntities(text, entities);
        
        return {
            intent: detectedIntent,
            confidence,
            entities,
            category: detectedIntent
        };
    }

    /**
     * Extract entities from text (simplified version)
     * @param {string} text - Input text
     * @param {Object} entities - Entities object to populate
     */
    extractEntities(text, entities) {
        // Amount extraction
        const amountRegex = /₹?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)/g;
        const amounts = [...text.matchAll(amountRegex)].map(match => match[1]);
        if (amounts.length > 0) {
            entities.amount = amounts;
        }

        // Date extraction (simplified)
        const dateRegex = /(?:this|last|next)?\s*(week|month|year|today|yesterday)/gi;
        const dates = [...text.matchAll(dateRegex)].map(match => match[0]);
        if (dates.length > 0) {
            entities.date = dates;
        }

        // Category extraction
        const categories = ['food', 'transport', 'entertainment', 'shopping', 'bills', 'groceries', 'dining'];
        const detectedCategories = categories.filter(cat => 
            text.toLowerCase().includes(cat)
        );
        if (detectedCategories.length > 0) {
            entities.category = detectedCategories;
        }

        // Goal/purpose extraction
        const goalRegex = /(vacation|emergency|house|car|wedding|retirement|education)/gi;
        const goals = [...text.matchAll(goalRegex)].map(match => match[1]);
        if (goals.length > 0) {
            entities.purpose = goals;
        }
    }

    /**
     * Send a message and get AI response
     * @param {string} text - User message text
     */
    async sendMessage(text) {
        if (!text.trim()) return;

        // Analyze user input
        const analysis = this.analyzeUserInput(text);
        
        // Create user message
        const userMessage = {
            id: this.generateMessageId(),
            type: 'user',
            text: text.trim(),
            timestamp: Date.now(),
            entities: analysis.entities,
            intent: analysis.intent
        };

        // Add user message
        this.messages.push(userMessage);

        // Update session context
        this.updateSessionContext(analysis);

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Get AI response (mock for now)
            const aiResponse = await this.getAIResponse(text, analysis);
            
            // Create AI message
            const aiMessage = {
                id: this.generateMessageId(),
                type: 'ai',
                text: aiResponse.text,
                timestamp: Date.now(),
                insights: aiResponse.insights,
                actions: aiResponse.actions
            };

            // Add AI message
            this.messages.push(aiMessage);

        } catch (error) {
            console.error('Error getting AI response:', error);
            
            const errorMessage = {
                id: this.generateMessageId(),
                type: 'ai',
                text: "I'm sorry, I'm having trouble processing your request right now. Please try again in a moment.",
                timestamp: Date.now()
            };

            this.messages.push(errorMessage);
        }

        // Hide typing indicator
        this.hideTypingIndicator();

        // Re-render messages and update UI
        this.renderMessages();
        this.updateContextPanel();
        this.saveChatState();

        // Update suggestions based on context
        if (analysis.intent) {
            this.updateSuggestions(analysis.intent);
        }
    }

    /**
     * Mock AI response generator (to be replaced with real AI integration)
     * @param {string} text - User input text
     * @param {Object} analysis - Input analysis results
     * @returns {Object} AI response object
     */
    async getAIResponse(text, analysis) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

        const responses = {
            spending: {
                text: "Based on your transaction data, I can see some interesting spending patterns. Your food expenses have increased by 15% this month compared to last month. The largest single expense was ₹2,500 at a grocery store.",
                insights: [
                    {
                        type: 'trend',
                        title: 'Spending Increase',
                        description: 'Food expenses up 15% this month',
                        value: '+₹3,200'
                    },
                    {
                        type: 'alert',
                        title: 'Unusual Purchase',
                        description: 'Large grocery purchase detected',
                        value: '₹2,500'
                    }
                ],
                actions: [
                    {
                        type: 'view_details',
                        label: 'View Detailed Breakdown',
                        icon: 'fa-chart-bar',
                        params: { category: 'food', period: 'month' }
                    },
                    {
                        type: 'set_budget',
                        label: 'Set Food Budget',
                        icon: 'fa-target',
                        params: { category: 'food' }
                    }
                ]
            },
            savings: {
                text: "Great question! Based on your income and current expenses, I recommend saving 20% of your monthly income. For your ₹50,000 goal, you could reach it in 8 months by saving ₹6,250 per month.",
                insights: [
                    {
                        type: 'goal',
                        title: 'Savings Target',
                        description: 'Monthly amount needed for your goal',
                        value: '₹6,250/month'
                    },
                    {
                        type: 'timeline',
                        title: 'Timeline',
                        description: 'Expected time to reach goal',
                        value: '8 months'
                    }
                ],
                actions: [
                    {
                        type: 'create_goal',
                        label: 'Create Savings Goal',
                        icon: 'fa-bullseye',
                        params: { amount: 50000, timeline: 8 }
                    },
                    {
                        type: 'setup_auto_save',
                        label: 'Setup Auto-Save',
                        icon: 'fa-cog',
                        params: { amount: 6250 }
                    }
                ]
            },
            investment: {
                text: "Your current portfolio shows a balanced approach with 60% equity and 40% debt funds. The performance has been solid with 12.5% returns this year. Consider increasing your SIP amount as your income grows.",
                insights: [
                    {
                        type: 'performance',
                        title: 'Portfolio Returns',
                        description: 'Annual return rate',
                        value: '12.5%'
                    },
                    {
                        type: 'allocation',
                        title: 'Asset Allocation',
                        description: 'Current portfolio mix',
                        value: '60% Equity, 40% Debt'
                    }
                ],
                actions: [
                    {
                        type: 'rebalance',
                        label: 'Rebalance Portfolio',
                        icon: 'fa-balance-scale',
                        params: { suggested: 'moderate' }
                    },
                    {
                        type: 'increase_sip',
                        label: 'Increase SIP Amount',
                        icon: 'fa-arrow-up',
                        params: { current: 5000 }
                    }
                ]
            },
            default: {
                text: "I understand you're asking about your finances. Let me help you with that! Could you be more specific about what aspect you'd like to know more about?",
                insights: [
                    {
                        type: 'general',
                        title: 'Financial Health',
                        description: 'Overall financial status',
                        value: 'Good'
                    }
                ],
                actions: [
                    {
                        type: 'financial_summary',
                        label: 'Get Financial Summary',
                        icon: 'fa-chart-pie',
                        params: {}
                    }
                ]
            }
        };

        return responses[analysis.intent] || responses.default;
    }

    /**
     * Update session context based on user input analysis
     * @param {Object} analysis - Input analysis results
     */
    updateSessionContext(analysis) {
        // Update active topics
        if (analysis.intent && !this.sessionContext.activeTopics.includes(analysis.intent)) {
            this.sessionContext.activeTopics.push(analysis.intent);
            // Keep only recent topics
            if (this.sessionContext.activeTopics.length > 5) {
                this.sessionContext.activeTopics = this.sessionContext.activeTopics.slice(-5);
            }
        }

        // Update user intent
        this.sessionContext.userIntent = analysis.intent;

        // Merge entities
        Object.entries(analysis.entities).forEach(([key, value]) => {
            if (this.sessionContext.entities[key]) {
                // Merge with existing entities
                const existing = Array.isArray(this.sessionContext.entities[key]) ? 
                    this.sessionContext.entities[key] : [this.sessionContext.entities[key]];
                const newValues = Array.isArray(value) ? value : [value];
                this.sessionContext.entities[key] = [...existing, ...newValues].slice(-3); // Keep recent
            } else {
                this.sessionContext.entities[key] = value;
            }
        });

        // Update timestamp
        this.sessionContext.lastQueryTime = Date.now();
    }

    /**
     * Set up event listeners for enhanced chat interface
     */
    setupEventListeners() {
        // Send message
        const sendBtn = document.getElementById('send-message');
        const chatInput = document.getElementById('chat-input');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                const text = chatInput.value.trim();
                if (text) {
                    this.sendMessage(text);
                    chatInput.value = '';
                    this.updateCharacterCount();
                    this.hideEntityHighlights();
                }
            });
        }

        // Enter key to send
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendBtn.click();
                }
            });

            // Real-time analysis while typing
            let analysisTimeout;
            chatInput.addEventListener('input', (e) => {
                this.updateCharacterCount();
                
                // Debounced analysis
                clearTimeout(analysisTimeout);
                analysisTimeout = setTimeout(() => {
                    const text = e.target.value.trim();
                    if (text.length > 10) {
                        this.showTypingFeedback();
                        const analysis = this.analyzeUserInput(text);
                        this.showEntityHighlights(analysis.entities);
                        this.showIntentIndicator(analysis.intent);
                    } else {
                        this.hideTypingFeedback();
                        this.hideEntityHighlights();
                        this.hideIntentIndicator();
                    }
                }, 500);
            });

            // Auto-resize textarea
            chatInput.addEventListener('input', () => {
                this.autoResizeTextarea(chatInput);
            });
        }

        // Context panel toggle
        const toggleContextBtn = document.getElementById('toggle-context');
        const contextPanel = document.getElementById('context-panel');
        const closeContextBtn = document.getElementById('close-context');

        if (toggleContextBtn) {
            toggleContextBtn.addEventListener('click', () => {
                contextPanel.classList.toggle('visible');
            });
        }

        if (closeContextBtn) {
            closeContextBtn.addEventListener('click', () => {
                contextPanel.classList.remove('visible');
            });
        }

        // Clear chat
        const clearChatBtn = document.getElementById('clear-chat');
        if (clearChatBtn) {
            clearChatBtn.addEventListener('click', () => {
                this.clearChatHistory();
            });
        }

        // Export chat
        const exportChatBtn = document.getElementById('export-chat');
        if (exportChatBtn) {
            exportChatBtn.addEventListener('click', () => {
                this.exportChatHistory();
            });
        }

        // Suggestion categories
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const category = e.target.dataset.category;
                this.updateSuggestions(category);
            });
        });

        // Intent indicator close
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('intent-close')) {
                this.hideIntentIndicator();
            }
        });
    }

    /**
     * Show typing feedback
     */
    showTypingFeedback() {
        const feedbackEl = document.getElementById('typing-feedback');
        if (feedbackEl) {
            feedbackEl.style.display = 'flex';
        }
    }

    /**
     * Hide typing feedback
     */
    hideTypingFeedback() {
        const feedbackEl = document.getElementById('typing-feedback');
        if (feedbackEl) {
            feedbackEl.style.display = 'none';
        }
    }

    /**
     * Show entity highlights
     * @param {Object} entities - Detected entities
     */
    showEntityHighlights(entities) {
        const highlightsContainer = document.getElementById('entity-highlights');
        const highlightsList = document.getElementById('highlights-list');
        
        if (Object.keys(entities).length > 0) {
            const highlights = Object.entries(entities).map(([type, values]) => {
                const valueList = Array.isArray(values) ? values : [values];
                return valueList.map(value => `
                    <span class="highlight-item highlight-${type}">
                        <span class="highlight-type">${type}</span>
                        <span class="highlight-value">${value}</span>
                    </span>
                `).join('');
            }).join('');
            
            highlightsList.innerHTML = highlights;
            highlightsContainer.style.display = 'flex';
        } else {
            this.hideEntityHighlights();
        }
    }

    /**
     * Hide entity highlights
     */
    hideEntityHighlights() {
        const highlightsContainer = document.getElementById('entity-highlights');
        if (highlightsContainer) {
            highlightsContainer.style.display = 'none';
        }
    }

    /**
     * Show intent indicator
     * @param {string} intent - Detected intent
     */
    showIntentIndicator(intent) {
        if (!intent) return;

        const indicator = document.getElementById('intent-indicator');
        const intentText = document.querySelector('.intent-text');
        
        if (indicator && intentText) {
            intentText.textContent = `I think you're asking about ${intent}...`;
            indicator.style.display = 'block';
            
            // Auto-hide after 3 seconds
            setTimeout(() => this.hideIntentIndicator(), 3000);
        }
    }

    /**
     * Hide intent indicator
     */
    hideIntentIndicator() {
        const indicator = document.getElementById('intent-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    /**
     * Update character count display
     */
    updateCharacterCount() {
        const input = document.getElementById('chat-input');
        const counter = document.getElementById('character-count');
        
        if (input && counter) {
            const count = input.value.length;
            counter.textContent = `${count}/1000`;
            counter.classList.toggle('limit-warning', count > 800);
            counter.classList.toggle('limit-exceeded', count > 1000);
        }
    }

    /**
     * Auto-resize textarea based on content
     * @param {HTMLTextAreaElement} textarea - Textarea element
     */
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.style.display = 'block';
        }
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
    }

    /**
     * Send a sample query
     * @param {string} query - Pre-written query to send
     */
    sendSampleQuery(query) {
        const input = document.getElementById('chat-input');
        if (input) {
            input.value = query;
            this.autoResizeTextarea(input);
            this.updateCharacterCount();
            document.getElementById('send-message').click();
        }
    }

    /**
     * Execute an action button
     * @param {string} actionType - Type of action to execute
     * @param {Object} params - Action parameters
     */
    executeAction(actionType, params) {
        console.log('Executing action:', actionType, params);
        
        // Show loading state
        this.app.setLoading(true);
        
        // Simulate action execution
        setTimeout(() => {
            this.app.setLoading(false);
            
            switch (actionType) {
                case 'view_details':
                    this.app.showNotification('Detailed analysis view would open here', 'info');
                    break;
                case 'set_budget':
                    this.app.showNotification('Budget setting interface would open here', 'info');
                    break;
                case 'create_goal':
                    this.app.showNotification('Savings goal created successfully!', 'success');
                    break;
                default:
                    this.app.showNotification(`Action "${actionType}" executed`, 'success');
            }
        }, 1000);
    }

    /**
     * Rate a message (thumbs up/down)
     * @param {string} messageId - ID of message to rate
     * @param {string} rating - 'up' or 'down'
     */
    rateMessage(messageId, rating) {
        const message = this.messages.find(m => m.id === messageId);
        if (message) {
            message.rating = rating;
            this.saveChatState();
            this.app.showNotification(`Thank you for your feedback!`, 'success');
        }
    }

    /**
     * Copy message to clipboard
     * @param {string} messageId - ID of message to copy
     */
    copyMessage(messageId) {
        const message = this.messages.find(m => m.id === messageId);
        if (message) {
            navigator.clipboard.writeText(message.text).then(() => {
                this.app.showNotification('Message copied to clipboard', 'success');
            });
        }
    }

    /**
     * Clear chat history
     */
    clearChatHistory() {
        if (confirm('Are you sure you want to clear your chat history? This action cannot be undone.')) {
            this.messages = [];
            this.sessionContext = {
                activeTopics: [],
                userIntent: null,
                entities: {},
                conversationStage: 'introduction',
                lastQueryTime: null,
                contextRetentionTime: 900000,
                maxContextMessages: 10
            };
            
            localStorage.removeItem('financial-ai-chat-history');
            localStorage.removeItem('financial-ai-session-context');
            
            // Add fresh welcome message
            this.addSystemMessage('welcome');
            
            this.renderMessages();
            this.updateContextPanel();
            this.updateSuggestions('general');
            
            this.app.showNotification('Chat history cleared', 'success');
        }
    }

    /**
     * Export chat history
     */
    exportChatHistory() {
        const exportData = {
            messages: this.messages,
            sessionContext: this.sessionContext,
            exportDate: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
            type: 'application/json' 
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `financial-ai-chat-export-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        
        this.app.showNotification('Chat history exported successfully', 'success');
    }

    /**
     * Start context cleanup timer
     */
    startContextTimer() {
        setInterval(() => {
            const now = Date.now();
            
            // Clear old entities and topics if context is stale
            if (this.sessionContext.lastQueryTime && 
                now - this.sessionContext.lastQueryTime > this.sessionContext.contextRetentionTime) {
                
                this.sessionContext.activeTopics = [];
                this.sessionContext.entities = {};
                this.sessionContext.userIntent = null;
                this.updateContextPanel();
            }
        }, 60000); // Check every minute
    }

    /**
     * Add system message
     * @param {string} type - Type of system message
     */
    addSystemMessage(type) {
        const message = {
            id: this.generateMessageId(),
            type: 'system',
            subtype: type,
            text: '',
            timestamp: Date.now()
        };
        
        this.messages.push(message);
    }

    /**
     * Generate unique message ID
     * @returns {string} Unique message ID
     */
    generateMessageId() {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Scroll to bottom of chat
     */
    scrollToBottom() {
        const messagesContainer = document.getElementById('chat-messages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    /**
     * Get time ago string for message timestamp
     * @param {number} timestamp - Message timestamp
     * @returns {string} Time ago string
     */
    getTimeAgo(timestamp) {
        const now = Date.now();
        const diff = now - timestamp;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return new Date(timestamp).toLocaleDateString();
    }

    /**
     * Get icon for insight type
     * @param {string} type - Insight type
     * @returns {string} Font Awesome icon class
     */
    getInsightIcon(type) {
        const icons = {
            trend: 'fa-trending-up',
            alert: 'fa-exclamation-triangle',
            goal: 'fa-bullseye',
            timeline: 'fa-calendar-alt',
            performance: 'fa-chart-line',
            allocation: 'fa-pie-chart',
            general: 'fa-info-circle'
        };
        return icons[type] || 'fa-lightbulb';
    }

    /**
     * Get icon for topic
     * @param {string} topic - Topic name
     * @returns {string} Font Awesome icon class
     */
    getTopicIcon(topic) {
        const icons = {
            spending: 'fa-credit-card',
            savings: 'fa-piggy-bank',
            investment: 'fa-chart-line',
            debt: 'fa-file-invoice-dollar',
            planning: 'fa-calendar-alt'
        };
        return icons[topic] || 'fa-comment';
    }

    /**
     * Format AI response text with markdown support
     * @param {string} text - Raw AI response text
     * @returns {string} Formatted HTML
     */
    formatAIResponse(text) {
        // Simple markdown formatting
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedChatInterface;
} else {
    window.EnhancedChatInterface = EnhancedChatInterface;
}