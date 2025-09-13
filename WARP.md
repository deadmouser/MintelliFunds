# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Common Commands

### Development
```bash
# Start development with hot reload and DevTools
npm run dev

# Install dependencies
npm install

# Start production build
npm start
```

### Building & Distribution
```bash
# Package for current platform (creates executable)
npm run pack

# Build distributables for all platforms
npm run dist

# Build for Windows only
npm run build

# Quick start (auto-installs dependencies)
run.bat    # Windows batch file
```

### Debugging & Testing
```bash
# Start with DevTools open
npm run dev

# Manual dependency check
npm install --production

# Check Electron version
npx electron --version
```

## Architecture Overview

### Application Structure
This is an **Electron-based financial AI assistant** with a multi-layered architecture:

**Main Process (`src/main.js`)**:
- Handles window management, IPC communication, and OS integration
- Implements security measures (context isolation, CSP)
- Manages menu system and privacy controls
- Contains placeholder API integration points for backend

**Renderer Process (`src/renderer/`)**:
- Vanilla JavaScript frontend with modular component architecture
- Chart.js for financial visualizations
- Privacy-first design with granular data controls
- Responsive design with dark/light themes

**Services Layer (`src/services/`)**:
- `apiService.js` - Comprehensive REST API client with retry logic, auth management, and mock data fallback
- Handles all backend communication with structured endpoints

### Key Components

**Dashboard System** (`dashboard.js`):
- Real-time financial overview with summary cards
- Interactive Chart.js visualizations (spending trends, category breakdowns)
- Automatic refresh and privacy-aware data loading

**AI Chat Interface** (`chat.js`):
- Natural language processing for financial queries
- Context-aware conversation management
- Typing indicators and message persistence
- Suggestion-based interaction patterns

**Privacy Controller** (`privacy.js`):
- Granular data access controls (transactions, balances, investments, etc.)
- GDPR compliance features
- Local preference storage with backend synchronization

**Mobile-Responsive Navigation** (`mobile-nav.js`):
- Collapsible sidebar for mobile devices
- Touch-friendly interaction patterns

### Security Architecture
- **Context Isolation**: Renderer process isolated from Node.js APIs
- **Preload Script**: Secure IPC bridge with limited API exposure
- **CSP**: Content Security Policy prevents XSS attacks
- **Privacy-First**: Granular data access controls with user consent

### Data Flow
1. **Frontend** makes requests through component controllers
2. **API Service** handles HTTP communication with retry logic and auth
3. **Main Process** can intercept requests for additional security/processing
4. **Backend Integration** ready via comprehensive endpoint mapping
5. **Mock Data** fallback enables development without backend

### File Organization
```
src/
├── main.js              # Electron main process & security
├── preload.js           # Secure IPC bridge
├── renderer/
│   ├── index.html       # Single-page application shell
│   ├── styles.css       # Global styles & theme system
│   ├── css/             # Modular stylesheets
│   └── js/              # Component controllers
└── services/
    └── apiService.js    # Backend integration layer
```

## Development Patterns

### Component Architecture
Each major feature is implemented as a class-based controller:
- `FinancialAIApp` - Main application controller & navigation
- `Dashboard` - Financial data visualization & metrics
- `ChatInterface` - AI conversation management
- `PrivacyController` - Data access permissions

### API Integration Points
The application is **backend-ready** with mock data fallback:
- All endpoints defined in `apiService.js`
- Authentication token management built-in
- Retry logic with exponential backoff
- Privacy settings respect throughout API calls

### Privacy Implementation
Data access is controlled through:
- Toggle-based permissions for data categories
- API requests filtered based on user preferences
- Local storage of privacy settings
- Audit logging for compliance

### Theme System
Uses CSS custom properties for consistent theming:
- Dark/light mode toggle
- Responsive breakpoints
- Component-level theme inheritance

## Integration Requirements

### Backend API Expected Endpoints
The frontend expects a REST API with these endpoints:
- `GET /api/dashboard` - Financial overview metrics
- `POST /api/chat` - AI chat message processing  
- `GET /api/transactions` - Transaction history with filtering
- `PUT /api/privacy/settings` - Privacy preference updates
- `GET /api/insights/dashboard` - AI-generated insights

### Authentication Flow
- JWT token management via `apiService.js`
- Automatic token refresh with fallback to login
- Secure token storage in localStorage

### Chart.js Integration
Financial visualizations use Chart.js with:
- Custom color schemes matching app theme
- Responsive canvas sizing
- Real-time data updates
- Interactive tooltips with Indian currency formatting

## Environment Notes
- **Node.js 16+** required for Electron compatibility
- **Windows-optimized** with `run.bat` for easy startup
- **Development mode** includes hot reload and DevTools
- **Production builds** create platform-specific installers

## Privacy & Security Considerations
- All external API calls use HTTPS only
- User data never exposed to Node.js context from renderer
- Granular consent management for data categories
- Local processing for sensitive calculations
- Export controls for data portability compliance