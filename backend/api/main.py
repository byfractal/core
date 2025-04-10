"""
Main FastAPI application.
This is the entry point for the backend API.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Optional
import secrets

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import API routers
from backend.api.feedback import feedback_router
from backend.api.design import design_router
from backend.api.analysis import analysis_router
from backend.api.auth import auth_router

# Import security modules
from backend.security import (
    # Configure security middlewares
    configure_security_middlewares,
    
    # Auth0 modules if using Auth0
    Auth0User,
    get_auth0_user,
    requires_auth,
    requires_scopes,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Backend API",
    description="API for the application",
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

# Configure security middlewares
USE_AUTH0 = os.getenv("USE_AUTH0", "false").lower() == "true"

# Apply security middlewares based on configuration
configure_security_middlewares(
    app=app,
    use_auth0=USE_AUTH0,
    jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
    redis_url=os.getenv("REDIS_URL"),
    global_rate_limit=100,  # 100 requests per minute by default
    global_rate_period=60,  # 1 minute
    public_paths=[
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/auth/login",
        "/api/auth/callback",
        "/api/public",
        "/health",
    ],
)

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    Used to verify the API is running.
    """
    return {"status": "ok"}

# Include API routers
app.include_router(auth_router)
app.include_router(feedback_router)
app.include_router(design_router)
app.include_router(analysis_router)

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
    uvicorn.run(
        "backend.api.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "false").lower() == "true",
    ) 