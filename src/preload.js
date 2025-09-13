const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // API communication
    makeAPIRequest: (endpoint, method, data) => 
        ipcRenderer.invoke('api-request', { endpoint, method, data }),
    
    // Privacy settings
    updatePrivacySettings: (settings) => 
        ipcRenderer.invoke('update-privacy-settings', settings),
    
    // AI chat
    sendChatMessage: (message) => 
        ipcRenderer.invoke('send-chat-message', message),
    
    // Menu actions
    onShowPrivacySettings: (callback) => 
        ipcRenderer.on('show-privacy-settings', callback),
    
    onExportData: (callback) => 
        ipcRenderer.on('export-data', callback),
    
    // Remove listeners
    removeAllListeners: (channel) => 
        ipcRenderer.removeAllListeners(channel),
    
    // App info
    getAppVersion: () => require('../../package.json').version,
    
    // Utility functions
    formatCurrency: (amount, currency = 'INR') => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },
    
    formatDate: (date) => {
        return new Date(date).toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    },
    
    formatDateTime: (date) => {
        return new Date(date).toLocaleString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
});

// Expose a limited set of Node.js functionality
contextBridge.exposeInMainWorld('nodeAPI', {
    platform: process.platform,
    version: process.version,
    env: {
        NODE_ENV: process.env.NODE_ENV
    }
});