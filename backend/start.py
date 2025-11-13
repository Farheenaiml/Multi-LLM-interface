#!/usr/bin/env python3
"""
Startup script for the Multi-LLM Broadcast Workspace backend
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Start the FastAPI server"""
    try:
        import uvicorn
        from main import app
        
        # Get configuration from environment
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8080"))
        reload = os.getenv("RELOAD", "true").lower() == "true"
        log_level = os.getenv("LOG_LEVEL", "info").lower()
        
        logger.info(f"Starting Multi-LLM Broadcast Workspace backend on {host}:{port}")
        logger.info(f"Reload: {reload}, Log Level: {log_level}")
        
        # Start the server
        if reload:
            # Use import string for reload mode
            uvicorn.run(
                "main:app",
                host=host,
                port=port,
                reload=reload,
                log_level=log_level,
                access_log=True
            )
        else:
            # Use app object for production mode
            uvicorn.run(
                app,
                host=host,
                port=port,
                reload=False,
                log_level=log_level,
                access_log=True
            )
        
    except ImportError as e:
        logger.error(f"Missing dependencies: {e}")
        logger.error("Please install requirements: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()