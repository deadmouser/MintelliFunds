# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

MintelliFunds is an AI-powered financial management application built with a dual architecture:
- **Frontend**: Electron desktop application with vanilla JavaScript, Chart.js for visualizations
- **Backend**: FastAPI Python server with privacy-first AI integration using Google Generative AI

## Development Commands

### Frontend (Electron Application)
```bash
# Install dependencies
npm install

# Start development with hot reload
npm run dev

# Start production mode
npm start

# Build for distribution
npm run build

# Package without installer
npm run pack

# Build installers for all platforms
npm run dist

# Quick start using batch file (Windows)
start-app.bat
```

### Backend (FastAPI Server)
```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start development server
python run_server.py

# Alternative start method
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production deployment
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing
```bash
# Backend API testing
cd backend
python test_full_api.py          # Complete API test suite
python test_ai_integration.py     # AI-specific functionality tests
python test_nlp_analysis.py       # NLP and analysis testing

# Frontend testing (run with backend server active)
# Tests are integrated within the Electron app via mock data
```

## Architecture Overview

### High-Level Structure
```
MintelliFunds/
├── src/                         # Electron frontend application
│   ├── main.js                  # Electron main process & IPC
│   ├── preload.js               # Secure renderer-main bridge
│   └── renderer/                # Frontend UI components
│       ├── index.html           # Main application HTML
│       ├── styles.css           # Global styling
│       └── js/                  # JavaScript modules
│           ├── app.js           # Main application controller
│           ├── dashboard.js     # Financial data visualization
│           ├── chat.js          # AI chat interface
│           └── privacy.js       # Privacy controls
├── backend/                     # FastAPI backend server
│   ├── app/
│   │   ├── main.py              # FastAPI application entry
│   │   ├── models/              # Pydantic data models
│   │   ├── routers/             # API endpoint handlers
│   │   └── services/            # Business logic (data & privacy)
│   ├── data/                    # Mock JSON financial data
│   └── run_server.py            # Server startup script
├── assets/                      # Icons and static resources
└── package.json                 # Frontend dependencies
```

### Key Architectural Patterns

#### Frontend Architecture
- **Component-based**: Modular JavaScript classes (`Dashboard`, `ChatInterface`, `PrivacyController`)
- **Event-driven**: Centralized event handling through main `FinancialAIApp` class
- **Privacy-first**: All data rendering respects privacy settings with granular controls
- **IPC Communication**: Secure communication between Electron processes via preload script
- **Chart Integration**: Chart.js integration with real-time data updates and animations

#### Backend Architecture
- **Layered Architecture**: Clear separation between routers, services, and models
- **Privacy Service**: Dedicated service for filtering data based on user permissions
- **Data Service**: Centralized data loading, validation, and caching
- **Mock Data System**: Comprehensive mock data for all financial categories during development

#### Privacy-First Design
- **Granular Permissions**: 10 distinct data categories that users can individually control:
  - `transactions`, `assets`, `liabilities`, `epf_balance`, `credit_score`
  - `investments`, `accounts`, `spending_trends`, `category_breakdown`, `dashboard_insights`
- **Permission Filtering**: Backend filters all responses based on user privacy settings
- **No Data Leakage**: Denied categories return empty arrays, not null values
- **Audit Logging**: All data access attempts are logged with metadata

#### AI Integration Points
- **Main Insights Endpoint**: `/api/insights` processes queries with privacy-aware data filtering
- **Intent Detection**: NLP analysis determines user intent and routes to appropriate handlers
- **Context-Aware Responses**: AI maintains conversation context while respecting privacy boundaries
- **Google Generative AI**: Integration ready for production AI model deployment

## Development Patterns

### Frontend Development
- **Navigation**: Section-based routing with keyboard shortcuts (Ctrl+1-5)
- **Data Loading**: Centralized API requests through `app.apiRequest()` method
- **Error Handling**: Graceful degradation with user-friendly error messages
- **Mock Data**: Comprehensive mock data system for offline development
- **Chart Management**: Proper Chart.js lifecycle management with cleanup

### Backend Development
- **API Responses**: Consistent JSON response format with metadata
- **Error Handling**: HTTP status codes with detailed error messages
- **Data Validation**: Pydantic models for request/response validation
- **Privacy Filtering**: Automatic data filtering based on permission objects
- **Development Testing**: Multiple test scripts for different API aspects

### Privacy Implementation
```python
# Backend privacy filtering example
def filter_data_by_permissions(data: dict, permissions: dict) -> dict:
    filtered_data = {}
    for category, allowed in permissions.items():
        if allowed and category in data:
            filtered_data[category] = data[category]
        else:
            filtered_data[category] = []  # Empty array, not null
    return filtered_data
```

### AI Chat Integration
- **Message Processing**: Structured message handling with typing indicators
- **Context Management**: Conversation history with privacy-aware context
- **Response Formatting**: Markdown-like formatting for rich AI responses
- **Voice Input**: Ready for speech recognition integration

## API Integration Points

### Key Endpoints
- **POST /api/insights**: Main AI query endpoint with privacy controls
- **GET /api/dashboard**: Financial overview with privacy filtering
- **POST /api/chat**: AI chat interaction with context management
- **PUT /api/privacy/settings**: Privacy preference updates
- **GET /api/health**: System health and AI service status

### Frontend-Backend Communication
- **Electron IPC**: Secure communication via preload script
- **HTTP Client**: Retry logic with exponential backoff
- **Authentication**: JWT token management (ready for implementation)
- **Error Recovery**: Graceful handling of API failures with mock data fallback

## Privacy & Security Considerations

### Data Access Control
- All financial data access is controlled by user-defined permissions
- Backend validates and filters all responses based on privacy settings
- Frontend respects privacy settings for UI rendering and chart display
- Privacy settings are stored locally and synced with backend

### Security Measures
- **Context Isolation**: Electron renderer process isolated from Node.js APIs
- **Content Security Policy**: Strict CSP prevents XSS attacks  
- **Secure Preload**: Limited IPC bridge with specific exposed APIs
- **HTTPS Only**: All external API calls use secure connections

### Development vs Production
- **CORS**: Currently allows all origins for development (restrict in production)
- **Authentication**: Mock auth system (implement real auth for production)
- **Data Storage**: Local mock data (integrate with real financial APIs)
- **AI Integration**: Mock responses (connect to actual AI service)

## File Organization Notes

### Critical Files for AI Understanding
- `src/renderer/js/app.js`: Main application logic and navigation
- `backend/app/main.py`: FastAPI server entry point
- `backend/app/services/privacy_service.py`: Privacy filtering logic
- `src/renderer/js/dashboard.js`: Financial data visualization components
- `src/renderer/js/chat.js`: AI chat interface implementation

### Mock Data System
- `backend/data/`: Contains JSON files with realistic financial data
- Categories include transactions, investments, accounts, assets, liabilities
- All data respects Indian financial contexts (₹ currency, EPF, etc.)

### Configuration Files
- `package.json`: Frontend dependencies and build configuration
- `backend/requirements.txt`: Python dependencies including FastAPI and Google Generative AI
- `start-app.bat`: Windows quick-start script

## Development Workflow

1. **Start Backend**: `cd backend && python run_server.py`
2. **Start Frontend**: `npm run dev` (in root directory)
3. **Access Application**: Electron window opens automatically
4. **API Documentation**: Visit `http://localhost:8000/docs` for interactive API docs
5. **Testing**: Run test scripts in `backend/` directory to verify API functionality

The application is designed with modularity and privacy at its core, making it suitable for financial data handling while maintaining user control over data access.