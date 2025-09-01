#!/usr/bin/env python3
"""
Start the backend server
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting Repostr Backend Server...")
    print("📍 Server will be available at: http://127.0.0.1:8000")
    print("📖 API docs will be available at: http://127.0.0.1:8000/docs")
    print("🔄 Auto-reload is enabled for development")
    print()
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )