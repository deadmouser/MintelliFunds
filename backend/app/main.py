"""
Main FastAPI application for Financial AI Assistant Backend
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn
from datetime import datetime

from .routers import insights, transactions, accounts, investments, privacy, chat, dashboard
from .services.data_service import DataService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Financial AI Assistant API",
    description="Backend API for AI-powered financial management application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(insights.router)
app.include_router(transactions.router)
app.include_router(accounts.router)
app.include_router(investments.router)
app.include_router(privacy.router)
app.include_router(chat.router)
app.include_router(dashboard.router)

# Initialize data service
data_service = DataService()


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Financial AI Assistant API...")
    
    try:
        # Load and validate data on startup
        logger.info("Loading financial data...")
        data = data_service.load_all_data()
        
        if data_service.validate_data_structure(data):
            logger.info("Financial data loaded and validated successfully")
        else:
            logger.error("Data validation failed on startup")
            
    except Exception as e:
        logger.error(f"Failed to load data on startup: {str(e)}")
        # Don't fail startup, but log the error


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Financial AI Assistant API...")


@app.get("/")
async def root():
    """
    Root endpoint with API information
    
    Returns:
        JSON response with API information
    """
    return {
        "message": "Financial AI Assistant API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "endpoints": {
            "insights": "/api/insights",
            "health": "/api/health",
            "data_summary": "/api/data/summary",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/api/status")
async def api_status():
    """
    API status endpoint
    
    Returns:
        JSON response with detailed API status
    """
    try:
        data_summary = data_service.get_data_summary()
        
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data_status": "loaded" if data_summary else "not_loaded",
            "data_categories": len(data_summary),
            "uptime": "running"
        }
    except Exception as e:
        logger.error(f"Error getting API status: {str(e)}")
        return {
            "status": "degraded",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": str(e)
        }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler for unexpected errors"""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
