#!/usr/bin/env python3
"""
Start the FastAPI server with custom adapters
"""
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append('backend')

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting FastAPI server with custom adapters...")
    print("📡 Server will be available at: http://localhost:5000")
    print("📋 API docs at: http://localhost:5000/docs")
    print()
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )