#!/usr/bin/env python3
"""
Startup script for the Financial AI Assistant Backend
"""
import uvicorn
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    # Change to the backend directory
    os.chdir(backend_dir)
    
    print("🚀 Starting Financial AI Assistant Backend...")
    print("📍 Backend directory:", backend_dir)
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 API documentation: http://localhost:8000/docs")
    print("🔍 Alternative docs: http://localhost:8000/redoc")
    print("-" * 50)
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
