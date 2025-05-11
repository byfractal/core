"""
Simplified FastAPI application for testing JWT authentication.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Optional
import secrets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import auth router only
from backend.api.auth_simple import auth_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="JWT Test API",
    description="API for testing JWT authentication",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    Used to verify the API is running.
    """
    return {"status": "ok"}

# Include JWT auth router
app.include_router(auth_router)

# Error handlers
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Handle generic exceptions."""
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"},
    )

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    # Create and save a JWT secret key if not already set
    jwt_secret_key = os.getenv("JWT_SECRET_KEY")
    if not jwt_secret_key:
        # Generate a secure random key
        jwt_secret_key = secrets.token_hex(32)
        print(f"Generated JWT_SECRET_KEY: {jwt_secret_key}")
        
        # Write to .env file if possible
        try:
            with open('.env', 'a') as f:
                f.write(f"\nJWT_SECRET_KEY={jwt_secret_key}\n")
            print("JWT_SECRET_KEY added to .env file")
        except:
            print("Could not write to .env file. Please add the JWT_SECRET_KEY manually.")
    
    uvicorn.run(
        "main_simple:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8080")),
        reload=os.getenv("DEBUG", "false").lower() == "true",
    ) 