// Chat Accessibility Enhancements
class ChatAccessibility {
    constructor(chatInstance) {
        this.chat = chatInstance;
        this.speechSynthesis = window.speechSynthesis;
        this.speechRecognition = null;
        this.isListening = false;
        
        this.initAccessibilityFeatures();
    }
    
    initAccessibilityFeatures() {
        this.setupKeyboardNavigation();
        this.setupScreenReaderSupport();
        this.setupVoiceFeatures();
        this.setupFocusManagement();
    }
    
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to send message
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.chat.sendMessage();
            }
            
            // Escape to clear typing indicator
            if (e.key === 'Escape') {
                const typingIndicator = document.getElementById('typing-indicator');
                if (typingIndicator && typingIndicator.style.display !== 'none') {
                    this.chat.hideTypingIndicator();
                }
            }
            
            // Alt + C to clear chat (with confirmation)
            if (e.altKey && e.key === 'c') {
                e.preventDefault();
                this.chat.clearChat();
            }
            
            // Alt + V for voice input
            if (e.altKey && e.key === 'v') {
                e.preventDefault();
                this.startVoiceInput();
            }
            
            // Arrow keys for message navigation
            if (e.key === 'ArrowUp' && e.ctrlKey) {
                e.preventDefault();
                this.navigateToLastMessage();
            }
        });
    }
    
    setupScreenReaderSupport() {
        // Add ARIA labels and roles
        const chatContainer = document.querySelector('.chat-container');\n        if (chatContainer) {
            chatContainer.setAttribute('role', 'application');
            chatContainer.setAttribute('aria-label', 'Financial AI Chat Interface');
        }
        
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.setAttribute('role', 'log');
            chatMessages.setAttribute('aria-live', 'polite');
            chatMessages.setAttribute('aria-label', 'Chat messages');
        }
        
        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.setAttribute('aria-label', 'Type your financial question here');
            chatInput.setAttribute('aria-describedby', 'chat-help-text');
        }
        
        // Add help text
        this.addHelpText();
    }
    
    setupVoiceFeatures() {
        // Speech Recognition setup
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.speechRecognition = new SpeechRecognition();
            this.speechRecognition.continuous = false;
            this.speechRecognition.interimResults = false;
            this.speechRecognition.lang = 'en-IN';
            
            this.speechRecognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const chatInput = document.getElementById('chat-input');
                if (chatInput) {
                    chatInput.value = transcript;
                    this.announceToScreenReader(`Voice input received: ${transcript}`);\n                }
                this.isListening = false;
                this.updateVoiceButton();
            };
            
            this.speechRecognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.announceToScreenReader('Voice input failed. Please try again.');
                this.isListening = false;
                this.updateVoiceButton();
            };
            
            this.speechRecognition.onend = () => {
                this.isListening = false;
                this.updateVoiceButton();
            };
            
            this.addVoiceButton();
        }
        
        // Text-to-speech for AI responses
        if (this.speechSynthesis) {
            this.addSpeechToggle();
        }
    }
    
    setupFocusManagement() {
        // Ensure proper focus management
        document.addEventListener('click', (e) => {
            if (e.target.matches('.message-action')) {
                // Announce action to screen reader
                const action = e.target.title || e.target.getAttribute('aria-label');
                if (action) {
                    this.announceToScreenReader(`${action} activated`);
                }
            }
        });
    }
    
    addHelpText() {
        const chatInputContainer = document.querySelector('.chat-input-container');
        if (chatInputContainer && !document.getElementById('chat-help-text')) {
            const helpText = document.createElement('div');
            helpText.id = 'chat-help-text';
            helpText.className = 'sr-only'; // Screen reader only
            helpText.textContent = 'Use Ctrl+Enter to send message, Alt+V for voice input, Alt+C to clear chat';
            chatInputContainer.appendChild(helpText);
        }
    }
    
    addVoiceButton() {
        const inputWrapper = document.querySelector('.chat-input-wrapper');
        if (inputWrapper && !document.getElementById('voice-input-btn')) {
            const voiceButton = document.createElement('button');
            voiceButton.id = 'voice-input-btn';
            voiceButton.className = 'voice-btn';
            voiceButton.innerHTML = '<i class=\"fas fa-microphone\"></i>';
            voiceButton.setAttribute('aria-label', 'Start voice input');
            voiceButton.setAttribute('title', 'Voice input (Alt+V)');
            voiceButton.addEventListener('click', () => this.startVoiceInput());
            
            // Insert before send button
            const sendButton = document.getElementById('send-message');
            inputWrapper.insertBefore(voiceButton, sendButton);
        }
    }
    
    addSpeechToggle() {
        const chatHeader = document.querySelector('.section-header .header-actions');
        if (chatHeader && !document.getElementById('speech-toggle')) {
            const speechToggle = document.createElement('button');
            speechToggle.id = 'speech-toggle';
            speechToggle.className = 'btn btn-secondary';
            speechToggle.innerHTML = '<i class=\"fas fa-volume-up\"></i> Speech';
            speechToggle.setAttribute('aria-label', 'Toggle text-to-speech for AI responses');
            speechToggle.addEventListener('click', () => this.toggleSpeech());
            
            chatHeader.appendChild(speechToggle);
        }
    }
    
    startVoiceInput() {
        if (!this.speechRecognition) {
            this.announceToScreenReader('Voice input not available');
            return;
        }
        
        if (this.isListening) {
            this.speechRecognition.stop();
            return;
        }
        
        this.isListening = true;
        this.updateVoiceButton();
        this.announceToScreenReader('Listening for voice input...');
        
        try {
            this.speechRecognition.start();
        } catch (error) {
            console.error('Failed to start speech recognition:', error);
            this.isListening = false;
            this.updateVoiceButton();
            this.announceToScreenReader('Failed to start voice input');
        }
    }
    
    updateVoiceButton() {
        const voiceButton = document.getElementById('voice-input-btn');
        if (voiceButton) {
            const icon = voiceButton.querySelector('i');
            if (this.isListening) {
                icon.className = 'fas fa-microphone-slash';
                voiceButton.setAttribute('aria-label', 'Stop voice input');
                voiceButton.classList.add('listening');
            } else {
                icon.className = 'fas fa-microphone';
                voiceButton.setAttribute('aria-label', 'Start voice input');
                voiceButton.classList.remove('listening');
            }
        }
    }
    
    toggleSpeech() {
        const speechEnabled = localStorage.getItem('chat-speech-enabled') !== 'false';
        localStorage.setItem('chat-speech-enabled', (!speechEnabled).toString());
        
        const toggle = document.getElementById('speech-toggle');
        if (toggle) {
            const icon = toggle.querySelector('i');
            if (speechEnabled) {
                icon.className = 'fas fa-volume-mute';
                this.announceToScreenReader('Text-to-speech disabled');
            } else {
                icon.className = 'fas fa-volume-up';
                this.announceToScreenReader('Text-to-speech enabled');
            }
        }
    }
    
    speakMessage(text) {
        const speechEnabled = localStorage.getItem('chat-speech-enabled') !== 'false';
        if (!speechEnabled || !this.speechSynthesis || !text) return;
        
        // Clean text for speech
        const cleanText = text
            .replace(/<[^>]*>/g, '') // Remove HTML tags
            .replace(/₹/g, 'rupees ') // Convert currency symbol
            .replace(/%/g, ' percent') // Convert percentage
            .replace(/\*\*/g, '') // Remove markdown
            .replace(/\*/g, ''); // Remove markdown
        
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 0.8;
        
        // Use Indian English voice if available
        const voices = this.speechSynthesis.getVoices();
        const indianVoice = voices.find(voice => 
            voice.lang === 'en-IN' || 
            voice.name.includes('Indian') || 
            voice.name.includes('India')
        );
        
        if (indianVoice) {
            utterance.voice = indianVoice;
        }
        
        this.speechSynthesis.speak(utterance);
    }
    
    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'assertive');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        // Remove after announcement
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }
    
    navigateToLastMessage() {
        const messages = document.querySelectorAll('.message');
        const lastMessage = messages[messages.length - 1];
        if (lastMessage) {
            lastMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            lastMessage.focus();
        }
    }
    
    // Enhanced method to handle new AI messages
    handleNewAIMessage(messageText) {
        // Speak the message if enabled
        setTimeout(() => this.speakMessage(messageText), 500);
        
        // Announce to screen reader
        this.announceToScreenReader('AI response received');
    }
}

// Add accessibility CSS
const accessibilityCSS = `
    /* Screen reader only content */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }
    
    /* Voice input button */
    .voice-btn {
        background: none;
        border: 1px solid var(--border-medium);
        color: var(--text-secondary);
        padding: var(--spacing-sm);
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: all var(--transition-fast);
        margin-right: var(--spacing-xs);
    }
    
    .voice-btn:hover {
        border-color: var(--primary-color);
        color: var(--primary-color);
        background: rgba(79, 70, 229, 0.1);
    }
    
    .voice-btn.listening {
        background: var(--primary-color);
        color: white;
        animation: pulse 1s ease-in-out infinite;
    }
    
    /* Focus indicators */
    .message:focus {
        outline: 2px solid var(--primary-color);
        outline-offset: 2px;
    }
    
    .message-action:focus {
        outline: 2px solid var(--primary-color);
        outline-offset: 1px;
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        .message {
            border: 1px solid var(--border-dark);
        }
        
        .currency, .percentage-highlight {
            border-width: 2px;
        }
        
        .text-highlight {
            background: var(--text-primary);
            color: var(--bg-primary);
        }
    }
    
    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
        .animate-currency,
        .emoji-large,
        .message {
            animation: none !important;
        }
        
        .typing-dot {
            animation: none !important;
        }
    }
`;

// Inject accessibility CSS
const accessibilityStyle = document.createElement('style');
accessibilityStyle.textContent = accessibilityCSS;
document.head.appendChild(accessibilityStyle);

// Initialize accessibility when chat is ready
document.addEventListener('DOMContentLoaded', () => {
    if (window.app && window.app.chat) {
        window.app.chatAccessibility = new ChatAccessibility(window.app.chat);
        
        // Hook into AI message handling
        const originalAddMessage = window.app.chat.addMessage;
        window.app.chat.addMessage = function(text, type, timestamp) {
            originalAddMessage.call(this, text, type, timestamp);
            
            if (type === 'ai' && window.app.chatAccessibility) {
                window.app.chatAccessibility.handleNewAIMessage(text);
            }
        };
    }
});

// Export for other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatAccessibility;
}