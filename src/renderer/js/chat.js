// Chat Interface for AI Assistant
class ChatInterface {
    constructor(app) {
        this.app = app;
        this.messages = [];
        this.isTyping = false;
        this.messageId = 0;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadChatHistory();
    }

    setupEventListeners() {
        // Chat input handling
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-message');
        
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            chatInput.addEventListener('input', () => {
                this.handleInputChange();
            });
        }

        if (sendButton) {
            sendButton.addEventListener('click', () => {
                this.sendMessage();
            });
        }

        // Suggestion buttons
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const message = e.target.dataset.message || e.target.textContent;
                this.sendSuggestionMessage(message);
            });
        });

        // Clear chat button
        const clearChatBtn = document.getElementById('clear-chat');
        if (clearChatBtn) {
            clearChatBtn.addEventListener('click', () => {
                this.clearChat();
            });
        }
    }

    handleInputChange() {
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-message');
        
        if (chatInput && sendButton) {
            const hasText = chatInput.value.trim().length > 0;
            sendButton.disabled = !hasText || this.isTyping;
        }
    }

    async sendMessage() {
        const chatInput = document.getElementById('chat-input');
        if (!chatInput) return;

        const message = chatInput.value.trim();
        if (!message || this.isTyping) return;

        // Clear input
        chatInput.value = '';
        this.handleInputChange();

        // Add user message to chat
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to AI assistant
            const response = await this.sendToAI(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add AI response
            this.addMessage(response.text, 'ai');
            
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'ai');
        }
    }

    sendSuggestionMessage(message) {
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.value = message;
            this.sendMessage();
        }
    }

    addMessage(text, type, timestamp = new Date()) {
        const messageData = {
            id: ++this.messageId,
            text,
            type,
            timestamp
        };

        this.messages.push(messageData);
        this.renderMessage(messageData);
        this.scrollToBottom();
        this.saveChatHistory();
    }

    renderMessage(messageData) {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;

        const messageElement = document.createElement('div');
        messageElement.className = `message ${messageData.type}-message`;
        messageElement.dataset.messageId = messageData.id;

        const avatarClass = messageData.type === 'ai' ? 'fa-robot' : 'fa-user';
        const timeString = this.formatMessageTime(messageData.timestamp);

        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${avatarClass}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${this.formatMessageText(messageData.text)}</div>
                <div class="message-footer">
                    <div class="message-time">${timeString}</div>
                    ${messageData.type === 'ai' ? `
                        <div class="message-actions">
                            <button class="message-action" title="Copy message" onclick="app.chat.copyMessage('${messageData.id}')">
                                <i class="fas fa-copy"></i>
                            </button>
                            <button class="message-action" title="Thumbs up" onclick="app.chat.reactToMessage('${messageData.id}', 'like')">
                                <i class="fas fa-thumbs-up"></i>
                            </button>
                            <button class="message-action" title="Thumbs down" onclick="app.chat.reactToMessage('${messageData.id}', 'dislike')">
                                <i class="fas fa-thumbs-down"></i>
                            </button>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        // Add animation
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(20px)';
        chatMessages.appendChild(messageElement);

        // Trigger animation
        requestAnimationFrame(() => {
            messageElement.style.transition = 'all 0.3s ease';
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        });
    }

    formatMessageText(text) {
        // Handle markdown-like formatting for AI responses
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong class="text-highlight">$1</strong>')
            .replace(/\*(.*?)\*/g, '<em class="text-italic">$1</em>')
            .replace(/`(.*?)`/g, '<code class="code-snippet">$1</code>')
            .replace(/\n/g, '<br>');

        // Handle currency amounts with enhanced animation
        formatted = formatted.replace(/₹([\d,]+(?:\.\d{2})?)/g, '<span class="currency animate-currency">₹$1</span>');
        
        // Handle percentage highlights with color coding
        formatted = formatted.replace(/([+\-]?\d+(?:\.\d+)?%)/g, (match, p1) => {
            const isPositive = !p1.startsWith('-');
            const colorClass = isPositive ? 'percentage-positive' : 'percentage-negative';
            return `<span class="percentage-highlight ${colorClass}">${p1}</span>`;
        });
        
        // Handle bullet points with better spacing
        formatted = formatted.replace(/^• (.+)$/gm, '<div class="bullet-point"><span class="bullet">•</span><span class="bullet-text">$1</span></div>');
        
        // Handle numbered lists
        formatted = formatted.replace(/^(\d+)\. (.+)$/gm, '<div class="numbered-point"><span class="number">$1.</span><span class="number-text">$2</span></div>');
        
        // Handle emoji enhancements with categories
        formatted = formatted.replace(/(✅|❌|⚠️|ℹ️)/g, '<span class="emoji-large status">$1</span>');
        formatted = formatted.replace(/(💰|💸|💳|💎)/g, '<span class="emoji-large money">$1</span>');
        formatted = formatted.replace(/(📊|📈|📉|📋)/g, '<span class="emoji-large chart">$1</span>');
        formatted = formatted.replace(/(🎯|🏆|⭐|🔥)/g, '<span class="emoji-large goal">$1</span>');
        
        // Add contextual emojis for financial terms
        formatted = formatted.replace(/\b(profit|gain|increase|growth)\b/gi, '$1 <span class="emoji-large trend-up">📈</span>');
        formatted = formatted.replace(/\b(loss|debt|expense|decline|drop)\b/gi, '$1 <span class="emoji-large trend-down">📉</span>');
        formatted = formatted.replace(/\b(saving|savings|save)\b/gi, '$1 <span class="emoji-large savings">🏦</span>');
        formatted = formatted.replace(/\b(investment|invest|portfolio)\b/gi, '$1 <span class="emoji-large investment">💼</span>');
        formatted = formatted.replace(/\b(budget|budgeting)\b/gi, '$1 <span class="emoji-large budget">📊</span>');
        formatted = formatted.replace(/\b(goal|target|achievement)\b/gi, '$1 <span class="emoji-large goal">🎯</span>');
        
        // Handle links (if any)
        formatted = formatted.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" class="message-link" target="_blank" rel="noopener noreferrer">$1</a>');
        
        // Handle special formatting for recommendations
        formatted = formatted.replace(/\*\*Recommendation:\*\* (.*?)$/gm, '<div class="recommendation"><span class="rec-label">💡 Recommendation:</span> <span class="rec-text">$1</span></div>');
        
        // Handle key insights formatting
        formatted = formatted.replace(/\*\*Key Insights:\*\*/g, '<div class="insights-header"><span class="insights-icon">🔍</span> <strong>Key Insights:</strong></div>');
        
        return formatted;
    }

    formatMessageTime(timestamp) {
        const now = new Date();
        const messageTime = new Date(timestamp);
        const diffMinutes = Math.floor((now - messageTime) / (1000 * 60));

        if (diffMinutes < 1) {
            return 'Just now';
        } else if (diffMinutes < 60) {
            return `${diffMinutes}m ago`;
        } else if (diffMinutes < 1440) {
            const hours = Math.floor(diffMinutes / 60);
            return `${hours}h ago`;
        } else {
            return messageTime.toLocaleDateString('en-IN', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }

    showTypingIndicator() {
        this.isTyping = true;
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.style.display = 'flex';
            typingIndicator.innerHTML = `
                <div class="typing-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="typing-dots">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
                <span class="typing-text">AI is thinking...</span>
            `;
        }
        
        // Disable send button
        this.handleInputChange();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.style.display = 'none';
        }
        
        // Re-enable send button
        this.handleInputChange();
    }

    scrollToBottom() {
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    async sendToAI(message) {
        if (window.electronAPI) {
            const response = await window.electronAPI.sendChatMessage(message);
            if (response.success) {
                return response.response;
            } else {
                throw new Error(response.error);
            }
        } else {
            // Mock AI response for development
            return this.generateMockAIResponse(message);
        }
    }

    generateMockAIResponse(message) {
        const responses = {
            'spending': {
                text: `Based on your recent transactions, here's your spending breakdown:\n\n**This Month:**\n• Food & Dining: ₹12,500 (28%)\n• Transportation: ₹8,200 (18%)\n• Shopping: ₹15,600 (35%)\n• Bills & Utilities: ₹8,700 (19%)\n\n**Key Insights:**\n• Your shopping expenses are 35% higher than last month\n• Consider setting a monthly budget of ₹40,000 to stay on track\n• You're spending efficiently on essential categories like food and bills`,
                timestamp: new Date().toISOString()
            },
            'vacation': {
                text: `Let me analyze your finances for a ₹50,000 vacation:\n\n**Current Financial Status:**\n• Available Balance: ₹1,25,000\n• Monthly Savings: ₹30,000\n• Emergency Fund: ₹45,000\n\n**Recommendation:** ✅ **You can afford this vacation!**\n\nAfter the vacation expense, you'll have:\n• Remaining Balance: ₹75,000\n• Emergency fund remains intact\n• Suggested timeline: Plan for next month to maintain healthy savings\n\n**Pro tip:** Consider booking during off-peak season to save 20-30%`,
                timestamp: new Date().toISOString()
            },
            'save': {
                text: `Here are personalized money-saving strategies based on your spending patterns:\n\n**Immediate Opportunities (Save ₹5,200/month):**\n• Switch to a cheaper mobile plan: **₹800/month**\n• Cancel unused subscriptions: **₹1,200/month**\n• Cook more meals at home: **₹3,200/month**\n\n**Medium-term Strategies:**\n• Set up automatic transfers to savings account\n• Use cashback credit cards for regular expenses\n• Review and negotiate insurance premiums\n\n**Goal:** With these changes, you could increase your monthly savings to **₹35,200** - that's 42% more than current!`,
                timestamp: new Date().toISOString()
            },
            'investment': {
                text: `Here's your current investment performance analysis:\n\n**Portfolio Summary:**\n• Total Value: ₹85,000 (+15.2% this month)\n• Monthly SIP: ₹10,000\n• Asset Allocation: 70% Equity, 30% Debt\n\n**Performance Highlights:**\n• **Equity Funds:** +18.5% returns (beating market by 3%)\n• **Debt Funds:** +7.2% stable returns\n• **Best Performer:** Technology Sector Fund (+24%)\n\n**Recommendations:**\n• Continue current SIP - you're on track!\n• Consider increasing SIP by ₹2,000 when salary increments\n• Your risk profile matches your allocation perfectly`,
                timestamp: new Date().toISOString()
            },
            'default': {
                text: `I understand you're asking about "${message}". Let me help you with that!\n\nBased on your financial data, I can provide insights on:\n• **Spending Analysis** - Track where your money goes\n• **Budget Planning** - Set and achieve financial goals\n• **Investment Advice** - Optimize your portfolio\n• **Savings Opportunities** - Find ways to save more\n• **Bill Management** - Never miss a payment\n\nWhat specific aspect would you like me to analyze for you?`,
                timestamp: new Date().toISOString()
            }
        };

        const lowerMessage = message.toLowerCase();
        
        if (lowerMessage.includes('spending') || lowerMessage.includes('expenses')) {
            return responses.spending;
        } else if (lowerMessage.includes('vacation') || lowerMessage.includes('afford')) {
            return responses.vacation;
        } else if (lowerMessage.includes('save') || lowerMessage.includes('saving')) {
            return responses.save;
        } else if (lowerMessage.includes('investment') || lowerMessage.includes('portfolio')) {
            return responses.investment;
        } else {
            return responses.default;
        }
    }

    clearChat() {
        if (confirm('Are you sure you want to clear the chat history? This action cannot be undone.')) {
            this.messages = [];
            const chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {
                // Keep only the initial welcome message
                const welcomeMessage = chatMessages.querySelector('.ai-message');
                chatMessages.innerHTML = '';
                if (welcomeMessage) {
                    chatMessages.appendChild(welcomeMessage);
                }
            }
            this.saveChatHistory();
            this.app.showNotification('Chat cleared successfully', 'info');
        }
    }

    loadChatHistory() {
        try {
            const savedChat = localStorage.getItem('financial-ai-chat-history');
            if (savedChat) {
                this.messages = JSON.parse(savedChat);
                
                // Render saved messages (skip the welcome message)
                this.messages.forEach(message => {
                    if (message.type !== 'welcome') {
                        this.renderMessage(message);
                    }
                });
                
                if (this.messages.length > 0) {
                    this.scrollToBottom();
                }
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    saveChatHistory() {
        try {
            // Only save recent messages (last 50) to prevent storage bloat
            const recentMessages = this.messages.slice(-50);
            localStorage.setItem('financial-ai-chat-history', JSON.stringify(recentMessages));
        } catch (error) {
            console.error('Error saving chat history:', error);
        }
    }

    // Public methods for integration with other components
    addInsightMessage(insight) {
        const message = `💡 **New Insight:** ${insight.text}`;
        this.addMessage(message, 'ai');
    }

    addTransactionAlert(transaction) {
        const amount = this.app.formatCurrency(Math.abs(transaction.amount));
        const message = `🔔 **Transaction Alert:** ${transaction.description} - ${amount} from ${transaction.account}`;
        this.addMessage(message, 'ai');
    }

    // Method to handle voice input (future enhancement)
    startVoiceInput() {
        if ('webkitSpeechRecognition' in window) {
            const recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-IN';

            recognition.onstart = () => {
                this.app.showNotification('Listening...', 'info');
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const chatInput = document.getElementById('chat-input');
                if (chatInput) {
                    chatInput.value = transcript;
                    this.sendMessage();
                }
            };

            recognition.onerror = () => {
                this.app.showNotification('Voice recognition error', 'error');
            };

            recognition.start();
        } else {
            this.app.showNotification('Voice input not supported', 'error');
        }
    }

    // Export chat history
    exportChatHistory() {
        const chatData = {
            messages: this.messages,
            exportDate: new Date().toISOString(),
            totalMessages: this.messages.length
        };

        const dataStr = JSON.stringify(chatData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `financial-ai-chat-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
    }

    // Get chat statistics
    getChatStats() {
        const stats = {
            totalMessages: this.messages.length,
            userMessages: this.messages.filter(m => m.type === 'user').length,
            aiMessages: this.messages.filter(m => m.type === 'ai').length,
            firstMessage: this.messages.length > 0 ? this.messages[0].timestamp : null,
            lastMessage: this.messages.length > 0 ? this.messages[this.messages.length - 1].timestamp : null
        };

        return stats;
    }

    // Message interaction methods
    copyMessage(messageId) {
        const message = this.messages.find(m => m.id == messageId);
        if (message) {
            navigator.clipboard.writeText(message.text).then(() => {
                this.app.showNotification('Message copied to clipboard', 'success');
            }).catch(() => {
                this.app.showNotification('Failed to copy message', 'error');
            });
        }
    }

    reactToMessage(messageId, reaction) {
        const message = this.messages.find(m => m.id == messageId);
        if (message) {
            if (!message.reactions) message.reactions = {};
            message.reactions[reaction] = (message.reactions[reaction] || 0) + 1;
            
            // Update message display
            const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
            if (messageElement) {
                const actionBtn = messageElement.querySelector(`.message-action[onclick*="${reaction}"]`);
                if (actionBtn) {
                    actionBtn.classList.add('reacted');
                    setTimeout(() => actionBtn.classList.remove('reacted'), 300);
                }
            }
            
            this.app.showNotification(
                reaction === 'like' ? 'Thanks for the feedback! 👍' : 'Thanks for the feedback, I\'ll try to improve! 👎', 
                'info'
            );
        }
    }

    // Enhanced message sending with better UX
    async sendMessageWithDelay(message) {
        // Add user message immediately
        this.addMessage(message, 'user');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Simulate realistic typing delay based on message length
        const typingDelay = Math.min(Math.max(message.length * 50, 1000), 3000);
        
        try {
            await new Promise(resolve => setTimeout(resolve, typingDelay));
            const response = await this.sendToAI(message);
            
            this.hideTypingIndicator();
            
            // Add AI response with typewriter effect
            this.addMessageWithTypewriter(response.text, 'ai');
            
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'ai');
        }
    }

    // Add message with typewriter effect
    addMessageWithTypewriter(text, type, speed = 30) {
        const messageData = {
            id: ++this.messageId,
            text: '',
            type,
            timestamp: new Date()
        };

        this.messages.push(messageData);
        this.renderMessage(messageData);
        
        // Typewriter effect
        let charIndex = 0;
        const typeInterval = setInterval(() => {
            if (charIndex < text.length) {
                messageData.text += text[charIndex];
                const messageElement = document.querySelector(`[data-message-id="${messageData.id}"] .message-text`);
                if (messageElement) {
                    messageElement.innerHTML = this.formatMessageText(messageData.text);
                }
                charIndex++;
                this.scrollToBottom();
            } else {
                clearInterval(typeInterval);
                this.saveChatHistory();
            }
        }, speed);
    }
}

// Add custom CSS for chat enhancements
const chatCSS = `
    /* Enhanced message formatting */
    .currency {
        font-weight: 600;
        color: var(--primary-color);
        display: inline-block;
        padding: 2px 6px;
        background: rgba(79, 70, 229, 0.1);
        border-radius: var(--radius-sm);
        border: 1px solid rgba(79, 70, 229, 0.2);
    }
    
    .animate-currency {
        animation: currencyPulse 0.6s ease;
    }
    
    @keyframes currencyPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .text-highlight {
        background: linear-gradient(120deg, transparent 0%, rgba(79, 70, 229, 0.2) 50%, transparent 100%);
        padding: 2px 4px;
        border-radius: var(--radius-sm);
        font-weight: 600;
    }
    
    .text-italic {
        color: var(--text-secondary);
        font-style: italic;
    }
    
    .code-snippet {
        background-color: var(--bg-tertiary);
        padding: 4px 8px;
        border-radius: var(--radius-md);
        font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
        font-size: 0.85em;
        border: 1px solid var(--border-light);
        color: var(--primary-color);
    }
    
    .bullet-point {
        display: flex;
        align-items: flex-start;
        margin: var(--spacing-xs) 0;
    }
    
    .bullet {
        color: var(--primary-color);
        font-weight: bold;
        margin-right: var(--spacing-sm);
        margin-top: 2px;
    }
    
    .emoji-large {
        font-size: 1.2em;
        display: inline-block;
        animation: emojiPop 0.3s ease;
    }
    
    @keyframes emojiPop {
        0% { transform: scale(0.8); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    .percentage-highlight {
        font-weight: 600;
        padding: 2px 6px;
        border-radius: var(--radius-sm);
        display: inline-block;
        border: 1px solid;
        transition: all var(--transition-fast);
    }
    
    .percentage-positive {
        background: rgba(16, 185, 129, 0.1);
        color: var(--secondary-color);
        border-color: rgba(16, 185, 129, 0.2);
    }
    
    .percentage-negative {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        border-color: rgba(239, 68, 68, 0.2);
    }
    
    .bullet-text {
        flex: 1;
        padding-left: var(--spacing-xs);
    }
    
    .numbered-point {
        display: flex;
        align-items: flex-start;
        margin: var(--spacing-xs) 0;
    }
    
    .number {
        color: var(--primary-color);
        font-weight: bold;
        margin-right: var(--spacing-sm);
        min-width: 20px;
    }
    
    .number-text {
        flex: 1;
    }
    
    /* Enhanced emoji categories */
    .emoji-large.status {
        filter: drop-shadow(0 0 4px rgba(0, 0, 0, 0.2));
    }
    
    .emoji-large.money {
        animation: emojiPop 0.4s ease, moneyShine 2s ease-in-out infinite;
    }
    
    .emoji-large.chart {
        animation: emojiPop 0.3s ease, chartPulse 3s ease-in-out infinite;
    }
    
    .emoji-large.goal {
        animation: emojiPop 0.3s ease, goalGlow 2s ease-in-out infinite alternate;
    }
    
    .emoji-large.trend-up {
        color: var(--secondary-color);
        animation: trendUp 0.6s ease;
    }
    
    .emoji-large.trend-down {
        color: #ef4444;
        animation: trendDown 0.6s ease;
    }
    
    @keyframes moneyShine {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.2) hue-rotate(15deg); }
    }
    
    @keyframes chartPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    @keyframes goalGlow {
        0% { filter: drop-shadow(0 0 2px rgba(255, 215, 0, 0.5)); }
        100% { filter: drop-shadow(0 0 6px rgba(255, 215, 0, 0.8)); }
    }
    
    @keyframes trendUp {
        0% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0); }
    }
    
    @keyframes trendDown {
        0% { transform: translateY(0); }
        50% { transform: translateY(5px); }
        100% { transform: translateY(0); }
    }
    
    /* Message link styling */
    .message-link {
        color: var(--primary-color);
        text-decoration: none;
        border-bottom: 1px dashed var(--primary-color);
        transition: all var(--transition-fast);
    }
    
    .message-link:hover {
        background: rgba(79, 70, 229, 0.1);
        border-bottom-style: solid;
    }
    
    /* Recommendation styling */
    .recommendation {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.1), rgba(16, 185, 129, 0.1));
        border: 1px solid rgba(79, 70, 229, 0.2);
        border-radius: var(--radius-md);
        padding: var(--spacing-sm) var(--spacing-md);
        margin: var(--spacing-sm) 0;
        animation: fadeInUp 0.5s ease;
    }
    
    .rec-label {
        color: var(--primary-color);
        font-weight: 600;
        display: inline-block;
        margin-bottom: var(--spacing-xs);
    }
    
    .rec-text {
        color: var(--text-primary);
    }
    
    /* Insights header styling */
    .insights-header {
        background: var(--bg-tertiary);
        border-left: 4px solid var(--primary-color);
        padding: var(--spacing-sm) var(--spacing-md);
        margin: var(--spacing-sm) 0;
        border-radius: var(--radius-sm);
    }
    
    .insights-icon {
        margin-right: var(--spacing-xs);
    }
    
    /* Enhanced message layout */
    .message-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: var(--spacing-xs);
        opacity: 0.7;
        transition: opacity var(--transition-fast);
    }
    
    .message:hover .message-footer {
        opacity: 1;
    }
    
    .message-actions {
        display: flex;
        gap: var(--spacing-xs);
        opacity: 0;
        transition: opacity var(--transition-fast);
    }
    
    .message:hover .message-actions {
        opacity: 1;
    }
    
    .message-action {
        background: none;
        border: none;
        color: var(--text-light);
        cursor: pointer;
        padding: 4px;
        border-radius: 50%;
        transition: all var(--transition-fast);
        font-size: 0.75rem;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .message-action:hover {
        color: var(--primary-color);
        background: rgba(79, 70, 229, 0.1);
        transform: scale(1.1);
    }
    
    .message-action.reacted {
        animation: reactionPulse 0.3s ease;
        color: var(--primary-color);
    }
    
    @keyframes reactionPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.3); }
        100% { transform: scale(1); }
    }
    
    /* Enhanced typing indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        padding: var(--spacing-md);
        background: var(--bg-tertiary);
        border-radius: var(--radius-lg);
        margin-bottom: var(--spacing-md);
        animation: fadeInUp 0.3s ease;
    }
    
    .typing-avatar {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: var(--primary-color);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        animation: pulse 2s ease-in-out infinite;
    }
    
    .typing-dots {
        display: flex;
        gap: 3px;
    }
    
    .typing-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--primary-color);
        animation: typingDots 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    .typing-dot:nth-child(3) { animation-delay: 0s; }
    
    @keyframes typingDots {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1.2);
            opacity: 1;
        }
    }
    
    .typing-text {
        font-size: 0.75rem;
        color: var(--text-muted);
        font-style: italic;
    }
    
    /* Enhanced scrollbar */
    .chat-messages::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-messages::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
        border-radius: 4px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb {
        background: var(--border-medium);
        border-radius: 4px;
        transition: background var(--transition-fast);
    }
    
    .chat-messages::-webkit-scrollbar-thumb:hover {
        background: var(--primary-color);
    }
    
    /* Message animations */
    .message {
        animation: messageSlideIn 0.4s ease;
    }
    
    @keyframes messageSlideIn {
        0% {
            opacity: 0;
            transform: translateY(20px) scale(0.95);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    /* Enhanced suggestion buttons */
    .suggestion-btn {
        position: relative;
        overflow: hidden;
    }
    
    .suggestion-btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s ease;
    }
    
    .suggestion-btn:hover::before {
        left: 100%;
    }
`;

const chatStyle = document.createElement('style');
chatStyle.textContent = chatCSS;
document.head.appendChild(chatStyle);