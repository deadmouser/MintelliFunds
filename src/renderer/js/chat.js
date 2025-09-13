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
                <div class="message-time">${timeString}</div>
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
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');

        // Handle currency amounts
        formatted = formatted.replace(/₹(\d+(?:,\d{3})*)/g, '<span class="currency">₹$1</span>');

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
}

// Add custom CSS for chat enhancements
const chatCSS = `
    .currency {
        font-weight: 600;
        color: var(--primary-color);
    }
    
    .message-text code {
        background-color: var(--bg-tertiary);
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Monaco', 'Menlo', monospace;
        font-size: 0.85em;
    }
    
    .chat-messages::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-messages::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
        border-radius: 3px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb {
        background: var(--border-medium);
        border-radius: 3px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb:hover {
        background: var(--border-dark);
    }
`;

const chatStyle = document.createElement('style');
chatStyle.textContent = chatCSS;
document.head.appendChild(chatStyle);