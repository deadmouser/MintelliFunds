# Financial AI Assistant Backend

A robust FastAPI backend for the Financial AI Assistant application, providing secure data access and privacy controls.

## 🏗️ Architecture

This backend follows a modular architecture with clear separation of concerns:

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── models/              # Pydantic data models
│   │   ├── requests.py      # Request/response models
│   │   └── data_models.py   # Financial data models
│   ├── routers/             # API route handlers
│   │   └── insights.py      # Main insights endpoint
│   └── services/            # Business logic services
│       ├── data_service.py  # Data loading and validation
│       └── privacy_service.py # Privacy filtering logic
├── data/                    # Mock JSON data files
├── requirements.txt         # Python dependencies
├── run_server.py           # Server startup script
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```bash
   python run_server.py
   ```

4. **Access the API:**
   - API Base URL: `http://localhost:8000`
   - Interactive Docs: `http://localhost:8000/docs`
   - Alternative Docs: `http://localhost:8000/redoc`

## 📡 API Endpoints

### Main Endpoint

#### `POST /api/insights`
The primary endpoint for processing financial queries with privacy controls.

**Request Body:**
```json
{
  "query": "What are my spending patterns this month?",
  "permissions": {
    "transactions": true,
    "assets": false,
    "liabilities": false,
    "epf_balance": false,
    "credit_score": false,
    "investments": true,
    "accounts": true,
    "spending_trends": true,
    "category_breakdown": true,
    "dashboard_insights": true
  }
}
```

**Response:**
```json
{
  "query": "What are my spending patterns this month?",
  "filtered_data": {
    "transactions": [...],
    "investments": [...],
    "accounts": [...],
    "spending_trends": [...],
    "category_breakdown": [...],
    "dashboard_insights": [...],
    "_metadata": {
      "total_categories": 10,
      "granted_categories": 5,
      "denied_categories": 5,
      "permissions_applied": {...}
    }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "status": "success"
}
```

### Utility Endpoints

#### `GET /api/health`
Health check endpoint to verify API status.

#### `GET /api/data/summary`
Get a summary of available financial data categories.

#### `GET /api/status`
Detailed API status information.

## 🔒 Privacy & Security Features

### Data Access Control
- **Granular Permissions**: Users can control access to specific data categories
- **Privacy Filtering**: Data is filtered based on user permissions before response
- **Audit Logging**: All data access is logged for transparency
- **No Data Leakage**: Denied categories return empty arrays, not null

### Supported Data Categories
- `transactions` - Transaction history
- `assets` - Personal assets and property
- `liabilities` - Debts and loans
- `epf_balance` - EPF/retirement balance
- `credit_score` - Credit score and factors
- `investments` - Investment portfolio
- `accounts` - Bank and financial accounts
- `spending_trends` - Spending pattern analysis
- `category_breakdown` - Spending by category
- `dashboard_insights` - AI-generated insights

## 📊 Mock Data

The backend includes comprehensive mock data for development and testing:

- **15 realistic transactions** across various categories
- **8 different asset types** with current values
- **5 liability accounts** including mortgage and credit cards
- **7 investment holdings** including stocks, ETFs, and crypto
- **6 bank accounts** with different types and balances
- **5 months of spending trends** with trend analysis
- **8 spending categories** with detailed breakdowns
- **6 AI insights** covering various financial aspects
- **EPF balance** with contribution history
- **Credit score** with detailed factor analysis

## 🛠️ Development

### Project Structure

#### Models (`app/models/`)
- **`requests.py`**: Pydantic models for API requests and responses
- **`data_models.py`**: Models for financial data structures

#### Services (`app/services/`)
- **`data_service.py`**: Handles data loading, validation, and caching
- **`privacy_service.py`**: Implements privacy filtering and permission validation

#### Routers (`app/routers/`)
- **`insights.py`**: Main API endpoint and health checks

### Key Features

#### Data Service
- **Lazy Loading**: Data is loaded on first request and cached
- **Validation**: Comprehensive data structure validation
- **Error Handling**: Graceful handling of missing or corrupted data files
- **Logging**: Detailed logging for debugging and monitoring

#### Privacy Service
- **Permission Mapping**: Maps frontend permissions to data categories
- **Access Control**: Filters data based on user permissions
- **Metadata**: Provides access statistics and permission summaries
- **Validation**: Ensures permission objects are properly structured

### Error Handling
- **HTTP Exceptions**: Proper HTTP status codes for different error types
- **Validation Errors**: Detailed validation error messages
- **Logging**: Comprehensive error logging for debugging
- **Graceful Degradation**: API continues to function even with data issues

## 🔧 Configuration

### Environment Variables
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level (default: info)
- `DATA_DIR`: Data directory path (default: data)

### CORS Configuration
The API is configured to allow cross-origin requests from any origin. In production, you should specify exact origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 🧪 Testing

### Manual Testing
Use the interactive API documentation at `http://localhost:8000/docs` to test endpoints.

### Example Test Request
```bash
curl -X POST "http://localhost:8000/api/insights" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are my spending patterns?",
    "permissions": {
      "transactions": true,
      "spending_trends": true,
      "category_breakdown": true,
      "assets": false,
      "liabilities": false,
      "epf_balance": false,
      "credit_score": false,
      "investments": false,
      "accounts": false,
      "dashboard_insights": false
    }
  }'
```

## 🚀 Production Deployment

### Using Uvicorn
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run_server.py"]
```

## 📝 API Integration

### Frontend Integration
The backend is designed to work seamlessly with the Electron frontend:

1. **CORS Enabled**: Allows requests from the frontend
2. **JSON API**: Simple JSON request/response format
3. **Error Handling**: Consistent error response format
4. **Privacy First**: Respects user privacy settings

### Example Frontend Integration
```javascript
const response = await fetch('http://localhost:8000/api/insights', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: userQuery,
    permissions: userPermissions
  })
});

const data = await response.json();
```

## 🔍 Monitoring & Logging

### Log Levels
- **INFO**: General application flow
- **WARNING**: Non-critical issues
- **ERROR**: Error conditions
- **DEBUG**: Detailed debugging information

### Key Metrics
- API request/response times
- Data loading performance
- Permission filtering statistics
- Error rates and types

## 🤝 Contributing

1. Follow the existing code structure
2. Add proper type hints and docstrings
3. Include error handling and logging
4. Test your changes thoroughly
5. Update documentation as needed

## 📄 License

This project is part of the Financial AI Assistant application and follows the same license terms.
