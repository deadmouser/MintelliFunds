# Financial AI Assistant

An AI-powered financial management application built with Electron, featuring intelligent insights, privacy controls, and modern UI design.

## Features

### 🤖 AI-Powered Insights
- **Natural Language Chat**: Ask questions about your finances in plain English
- **Intelligent Analysis**: AI-driven spending patterns, budget recommendations, and financial insights
- **Personalized Recommendations**: Tailored advice based on your financial data
- **Automated Insights**: Proactive notifications about spending trends and opportunities

### 📊 Comprehensive Dashboard
- **Real-time Financial Overview**: Balance, spending, savings, and investment tracking
- **Interactive Charts**: Spending trends and category breakdowns with Chart.js
- **Recent Transactions**: Quick view of your latest financial activity
- **Progress Tracking**: Visual progress bars for savings goals and budgets

### 🔒 Privacy-First Design
- **Granular Privacy Controls**: Toggle access to specific data categories
- **Data Access Transparency**: Clear visibility into what data the AI can access
- **Local Data Processing**: Sensitive calculations happen on your device
- **Export Controls**: Full control over data export and sharing

### 💬 Conversational Interface
- **Natural Language Processing**: Chat with your AI financial assistant
- **Context-Aware Responses**: Remembers conversation context for better assistance
- **Quick Suggestions**: Pre-built query suggestions for common questions
- **Chat History**: Persistent conversation history with search capabilities

### 📱 Modern User Experience
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Dark/Light Themes**: Comfortable viewing in any environment
- **Keyboard Shortcuts**: Quick navigation with Ctrl+1-5
- **Smooth Animations**: Polished interactions and transitions

## Tech Stack

### Frontend
- **Electron**: Cross-platform desktop application framework
- **Vanilla JavaScript**: Modern ES6+ without framework dependencies
- **Chart.js**: Beautiful, responsive charts and graphs
- **CSS Custom Properties**: Modern styling with CSS variables
- **Font Awesome**: Comprehensive icon library

### Backend Integration Ready
- **REST API Support**: Full HTTP client with retry logic and error handling
- **Authentication**: JWT token management with automatic refresh
- **Mock Data**: Development-friendly with realistic sample data
- **Privacy Controls**: API endpoints for data access management

### AI Integration Points
- **Chat API**: Ready for integration with your AI model endpoints
- **Insight Generation**: Structured endpoints for automated financial insights
- **Context Management**: Conversation state management for better AI responses
- **Privacy-Aware**: AI requests respect user privacy settings

## Installation

### Prerequisites
- **Node.js** (v16 or higher)
- **npm** or **yarn**

### Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd financial-ai-app
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Build for production**
   ```bash
   npm run build
   ```

## Development

### Project Structure
```
financial-ai-app/
├── src/
│   ├── main.js              # Electron main process
│   ├── preload.js           # Secure IPC bridge
│   ├── renderer/            # Frontend application
│   │   ├── index.html       # Main HTML file
│   │   ├── styles.css       # Global styles
│   │   └── js/              # JavaScript modules
│   │       ├── app.js       # Main application controller
│   │       ├── dashboard.js # Dashboard functionality
│   │       ├── chat.js      # AI chat interface
│   │       └── privacy.js   # Privacy controls
│   └── services/            # Backend integration
│       └── apiService.js    # API client and mock data
├── assets/                  # Static assets (icons, images)
├── package.json             # Project dependencies
└── README.md               # This file
```

### Key Components

#### 1. Main Application (`app.js`)
- Navigation management
- Section routing
- Global event handling
- Notification system
- Data export functionality

#### 2. Dashboard (`dashboard.js`)
- Financial data visualization
- Chart management with Chart.js
- Summary card animations
- Auto-refresh functionality
- Privacy-aware data display

#### 3. AI Chat (`chat.js`)
- Message handling and display
- Typing indicators
- Chat history persistence
- Markdown formatting support
- Voice input ready (future)

#### 4. Privacy Controls (`privacy.js`)
- Data access toggles
- Privacy status indicators
- Audit logging
- GDPR compliance helpers
- Data deletion requests

#### 5. API Service (`apiService.js`)
- HTTP client with retry logic
- Authentication management
- Mock data for development
- Error handling and recovery
- Comprehensive endpoint coverage

### Development Mode Features

#### Mock Data
The application includes comprehensive mock data for development:
- **Dashboard metrics**: Realistic financial summaries
- **Transaction history**: Sample transactions with categories
- **AI responses**: Context-aware mock chat responses
- **Privacy settings**: Default privacy configurations

#### Live Reload
- Automatic application restart on code changes
- Hot reloading for CSS modifications
- DevTools integration in development mode

#### Error Handling
- Graceful fallbacks when APIs are unavailable
- User-friendly error messages
- Retry mechanisms for transient failures
- Offline mode support

## API Integration

### Backend Requirements
Your backend API should implement the following endpoints:

#### Core Endpoints
- `GET /api/dashboard` - Financial overview data
- `GET /api/transactions` - Transaction history with filtering
- `GET /api/insights` - AI-generated financial insights
- `POST /api/chat` - AI chat message processing
- `PUT /api/privacy/settings` - Privacy preference updates

#### Authentication
- `POST /api/auth/login` - User authentication
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - Session termination

#### Data Management
- `GET /api/accounts` - Account information
- `GET /api/investments` - Investment portfolio
- `GET /api/assets` - Assets and liabilities
- `POST /api/export` - Data export functionality

### Integration Steps
1. **Update API Base URL**: Modify `baseURL` in `apiService.js`
2. **Configure Authentication**: Implement your auth flow in `handleUnauthorized()`
3. **Map Endpoints**: Ensure your API matches the expected endpoint structure
4. **Test Integration**: Use the built-in health check functionality
5. **Deploy**: Build and distribute your Electron application

## Privacy & Security

### Data Privacy Features
- **Granular Controls**: Users can enable/disable access to specific data categories
- **Transparent Processing**: Clear indicators showing what data is being accessed
- **Local Storage**: Sensitive settings stored locally, not in the cloud
- **Audit Logging**: Complete history of privacy setting changes

### Security Measures
- **Context Isolation**: Renderer process is isolated from Node.js APIs
- **Content Security Policy**: Strict CSP prevents XSS attacks
- **Secure Preload**: Limited, secure bridge between main and renderer processes
- **HTTPS Only**: All external API calls use secure HTTPS connections

### GDPR Compliance
- **Right to Access**: Users can export all their data
- **Right to Deletion**: Data deletion request functionality
- **Data Portability**: JSON export format for easy data transfer
- **Consent Management**: Explicit consent for each data category

## Customization

### Theming
The application uses CSS custom properties for easy theming:
```css
:root {
  --primary-color: #4f46e5;
  --secondary-color: #10b981;
  --bg-primary: #ffffff;
  --text-primary: #1e293b;
}
```

### Adding New Features
1. **Create new JavaScript modules** in `src/renderer/js/`
2. **Add corresponding CSS** in `styles.css` or separate files
3. **Update navigation** in `app.js` if needed
4. **Add API endpoints** in `apiService.js`
5. **Update HTML structure** in `index.html`

### Chart Customization
Charts use Chart.js and can be customized in `dashboard.js`:
- **Colors**: Update color arrays in chart configurations
- **Types**: Change chart types (line, bar, doughnut, etc.)
- **Animations**: Modify animation settings for different effects
- **Tooltips**: Customize tooltip content and formatting

## Building for Production

### Electron Builder Configuration
The project uses Electron Builder for packaging:
```bash
# Package for current platform
npm run pack

# Build installers for all platforms
npm run dist

# Build for specific platform
npm run build:win    # Windows
npm run build:mac    # macOS
npm run build:linux  # Linux
```

### Distribution
- **Windows**: NSIS installer with auto-updater support
- **macOS**: DMG package with code signing
- **Linux**: AppImage for universal compatibility

## Performance Optimization

### Frontend Optimizations
- **Code Splitting**: Modular JavaScript architecture
- **Lazy Loading**: Charts and data loaded on demand
- **Caching**: API responses cached for better performance
- **Debouncing**: Search and input handling optimized

### Memory Management
- **Chart Cleanup**: Proper cleanup of Chart.js instances
- **Event Listeners**: Automatic cleanup on navigation
- **Image Optimization**: Compressed assets and lazy loading
- **Storage Limits**: Automatic cleanup of old chat history

## Contributing

### Development Workflow
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and test thoroughly
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Code Style
- **ES6+**: Use modern JavaScript features
- **Comments**: Document complex functions and algorithms
- **Naming**: Use descriptive variable and function names
- **Structure**: Follow the existing project organization

## Troubleshooting

### Common Issues

#### Application Won't Start
- Check Node.js version (v16+ required)
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check for port conflicts if running dev server

#### Charts Not Displaying
- Verify Chart.js is loaded: Check browser console for errors
- Check canvas element IDs match JavaScript references
- Ensure data is in the correct format for Chart.js

#### API Connection Issues
- Verify backend API is running and accessible
- Check CORS configuration on your backend
- Verify API endpoints match the expected structure
- Check browser network tab for failed requests

### Debug Mode
Enable debug logging by setting development mode:
```javascript
// In main.js
const isDevelopment = true; // Force development mode
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. **Check the documentation** above
2. **Search existing issues** in the repository
3. **Create a new issue** with detailed description
4. **Include logs and screenshots** when reporting bugs

---

**Built with ❤️ for the hackathon - showcasing AI-powered financial management with privacy-first design.**