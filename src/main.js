const { app, BrowserWindow, Menu, ipcMain, dialog } = require('electron');
const path = require('path');

// Enable live reload for development
if (process.argv.includes('--dev')) {
    require('electron-reload')(__dirname, {
        electron: path.join(__dirname, '..', 'node_modules', '.bin', 'electron'),
        hardResetMethod: 'exit'
    });
}

class FinancialAIApp {
    constructor() {
        this.mainWindow = null;
        this.isDevelopment = process.argv.includes('--dev');
    }

    createWindow() {
        // Create the browser window
        this.mainWindow = new BrowserWindow({
            width: 1400,
            height: 900,
            minWidth: 800,
            minHeight: 600,
            webPreferences: {
                nodeIntegration: false,
                contextIsolation: true,
                enableRemoteModule: false,
                preload: path.join(__dirname, 'preload.js')
            },
            titleBarStyle: 'default',
            icon: path.join(__dirname, '..', 'assets', 'icon.png'),
            show: false // Don't show until ready
        });

        // Load the app
        this.mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));

        // Show window when ready to prevent visual flash
        this.mainWindow.once('ready-to-show', () => {
            this.mainWindow.show();
            
            // Open DevTools in development
            if (this.isDevelopment) {
                this.mainWindow.webContents.openDevTools();
            }
        });

        // Handle window closed
        this.mainWindow.on('closed', () => {
            this.mainWindow = null;
        });

        // Security: Prevent new window creation
        this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
            require('electron').shell.openExternal(url);
            return { action: 'deny' };
        });
    }

    createMenu() {
        const template = [
            {
                label: 'File',
                submenu: [
                    {
                        label: 'Export Data',
                        accelerator: 'CmdOrCtrl+E',
                        click: () => {
                            this.handleExportData();
                        }
                    },
                    { type: 'separator' },
                    {
                        label: 'Exit',
                        accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                        click: () => {
                            app.quit();
                        }
                    }
                ]
            },
            {
                label: 'View',
                submenu: [
                    { role: 'reload' },
                    { role: 'forceReload' },
                    { role: 'toggleDevTools' },
                    { type: 'separator' },
                    { role: 'resetZoom' },
                    { role: 'zoomIn' },
                    { role: 'zoomOut' },
                    { type: 'separator' },
                    { role: 'togglefullscreen' }
                ]
            },
            {
                label: 'Privacy',
                submenu: [
                    {
                        label: 'Data Settings',
                        click: () => {
                            this.mainWindow.webContents.send('show-privacy-settings');
                        }
                    },
                    {
                        label: 'Clear Cache',
                        click: async () => {
                            const session = this.mainWindow.webContents.session;
                            await session.clearCache();
                            await session.clearStorageData();
                        }
                    }
                ]
            },
            {
                label: 'Help',
                submenu: [
                    {
                        label: 'About',
                        click: () => {
                            dialog.showMessageBox(this.mainWindow, {
                                type: 'info',
                                title: 'About Financial AI Assistant',
                                message: 'Financial AI Assistant v1.0.0',
                                detail: 'AI-powered financial management with privacy controls.'
                            });
                        }
                    }
                ]
            }
        ];

        const menu = Menu.buildFromTemplate(template);
        Menu.setApplicationMenu(menu);
    }

    setupIPC() {
        // Handle API requests from renderer
        ipcMain.handle('api-request', async (event, { endpoint, method, data }) => {
            try {
                // This will be implemented to communicate with your backend API
                const response = await this.makeAPIRequest(endpoint, method, data);
                return { success: true, data: response };
            } catch (error) {
                return { success: false, error: error.message };
            }
        });

        // Handle privacy settings updates
        ipcMain.handle('update-privacy-settings', async (event, settings) => {
            try {
                // Store privacy settings and notify backend
                await this.updatePrivacySettings(settings);
                return { success: true };
            } catch (error) {
                return { success: false, error: error.message };
            }
        });

        // Handle chat messages
        ipcMain.handle('send-chat-message', async (event, message) => {
            try {
                // Send to AI model API
                const response = await this.sendToAI(message);
                return { success: true, response };
            } catch (error) {
                return { success: false, error: error.message };
            }
        });
    }

    async makeAPIRequest(endpoint, method = 'GET', data = null) {
        const { net } = require('electron');
        const baseURL = 'http://localhost:8000';
        const url = `${baseURL}${endpoint}`;
        
        try {
            console.log(`API Request: ${method} ${endpoint}`, data);
            
            return new Promise((resolve, reject) => {
                const request = net.request({
                    method: method,
                    url: url
                });
                
                request.setHeader('Content-Type', 'application/json');
                request.setHeader('Accept', 'application/json');
                
                if (data && method !== 'GET') {
                    const bodyData = JSON.stringify(data);
                    request.write(bodyData);
                }
                
                request.on('response', (response) => {
                    let responseData = '';
                    
                    response.on('data', (chunk) => {
                        responseData += chunk;
                    });
                    
                    response.on('end', () => {
                        try {
                            if (response.statusCode >= 200 && response.statusCode < 300) {
                                const jsonData = JSON.parse(responseData);
                                resolve(jsonData);
                            } else {
                                throw new Error(`HTTP ${response.statusCode}: ${response.statusMessage}`);
                            }
                        } catch (parseError) {
                            console.error('Response parsing error:', parseError);
                            resolve(this.getMockResponse(endpoint, method, data));
                        }
                    });
                });
                
                request.on('error', (error) => {
                    console.error(`Network error for ${endpoint}:`, error.message);
                    resolve(this.getMockResponse(endpoint, method, data));
                });
                
                request.end();
            });
            
        } catch (error) {
            console.error(`API Request failed for ${endpoint}:`, error.message);
            return this.getMockResponse(endpoint, method, data);
        }
    }

    async updatePrivacySettings(settings) {
        // Store privacy settings locally and sync with backend
        console.log('Privacy settings updated:', settings);
        
        // This will integrate with your backend API
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({ success: true });
            }, 200);
        });
    }

    async sendToAI(message) {
        try {
            console.log('Sending to AI:', message);
            
            const response = await this.makeAPIRequest('/api/chat', 'POST', {
                message: message,
                context: {}
            });
            
            return {
                text: response.response || response.text || `AI response for: "${message}"`,
                timestamp: response.timestamp || new Date().toISOString()
            };
            
        } catch (error) {
            console.error('AI request failed:', error);
            
            // Fallback AI response
            return {
                text: `I understand you're asking about: "${message}". I'm currently offline, but I can help you analyze your financial data when connected to the server.`,
                timestamp: new Date().toISOString()
            };
        }
    }

    getMockResponse(endpoint, method, data) {
        const mockResponses = {
            '/api/dashboard': {
                total_balance: 125000,
                monthly_spending: 45000,
                savings_progress: 30000,
                savings_goal: 100000,
                investment_value: 85000,
                net_worth: 165000,
                balance_change: 8.5,
                spending_change: -12.3,
                investment_change: 15.2,
                timestamp: new Date().toISOString()
            },
            '/api/transactions': [
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
                }
            ],
            '/api/health': {
                status: 'healthy',
                timestamp: new Date().toISOString(),
                message: 'Mock health check - backend not connected'
            }
        };
        
        return mockResponses[endpoint] || {
            message: 'Mock response for development',
            endpoint,
            method,
            data,
            timestamp: new Date().toISOString()
        };
    }

    async handleExportData() {
        const result = await dialog.showSaveDialog(this.mainWindow, {
            title: 'Export Financial Data',
            defaultPath: 'financial-data.json',
            filters: [
                { name: 'JSON Files', extensions: ['json'] },
                { name: 'CSV Files', extensions: ['csv'] }
            ]
        });

        if (!result.canceled) {
            // Export data logic will be implemented here
            this.mainWindow.webContents.send('export-data', result.filePath);
        }
    }

    initialize() {
        // Handle app ready
        app.whenReady().then(() => {
            this.createWindow();
            this.createMenu();
            this.setupIPC();

            app.on('activate', () => {
                if (BrowserWindow.getAllWindows().length === 0) {
                    this.createWindow();
                }
            });
        });

        // Handle all windows closed
        app.on('window-all-closed', () => {
            if (process.platform !== 'darwin') {
                app.quit();
            }
        });

        // Security: Prevent navigation to external URLs
        app.on('web-contents-created', (event, contents) => {
            contents.on('will-navigate', (navigationEvent, navigationUrl) => {
                const parsedUrl = new URL(navigationUrl);
                
                if (parsedUrl.origin !== 'file://') {
                    navigationEvent.preventDefault();
                }
            });
        });
    }
}

// Initialize the application
const financialApp = new FinancialAIApp();
financialApp.initialize();