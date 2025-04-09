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
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import API routers
from backend.api.feedback import feedback_router
from backend.api.design import design_router
from backend.api.analysis import analysis_router

# Import security modules
from backend.security import (
    verify_password,
    get_password_hash,
    create_tokens,
    blacklist_token,
    refresh_access_token,
    generate_mfa_secret,
    get_totp_code,
    verify_totp_code,
    get_provisional_qr_code,
    User,
    Token,
    Role,
)
from backend.security.middlewares import configure_security_middlewares

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Create the main application
app = FastAPI(
    title="Design Insights API",
    description="API for UX/UI analysis and recommendation generation",
    version="0.1.0"
)

# Get security configuration from environment variables
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    # Generate a random secret key for development
    if os.getenv("ENVIRONMENT") == "production":
        raise ValueError("JWT_SECRET_KEY must be set in production")
    logger.warning("JWT_SECRET_KEY not set, generating a random key for development")
    JWT_SECRET_KEY = secrets.token_hex(32)

REDIS_URL = os.getenv("REDIS_URL")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Configure security middlewares
configure_security_middlewares(
    app=app,
    jwt_secret_key=JWT_SECRET_KEY,
    redis_url=REDIS_URL,
    global_rate_limit=100,  # 100 requests per window
    global_rate_limit_window=60,  # 60 seconds (1 minute)
    exclude_paths_from_auth=[
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
    ],
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with path prefixes
app.mount("/api/feedback", feedback_router)
app.mount("/api/design", design_router)
app.mount("/api/analysis", analysis_router)

# Authentication routes
@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate a user and get access tokens.
    
    This endpoint is used to obtain JWT tokens for API access.
    """
    # Note: In a real application, you would validate against a database
    # This is just a placeholder implementation for demonstration
    if form_data.username != "demo@example.com" or form_data.password != "Secure#123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create user with sample data
    user = User(
        id="user123",
        email="demo@example.com",
        username="demo",
        full_name="Demo User",
        roles=[Role.USER],
    )
    
    # Create tokens
    return create_tokens(user.id, [role.value for role in user.roles])

@app.post("/api/auth/logout")
async def logout(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/auth/login"))):
    """
    Logout by invalidating the current token.
    """
    blacklist_token(token)
    return {"message": "Successfully logged out"}

@app.post("/api/auth/refresh", response_model=Token)
async def refresh(refresh_token: str):
    """
    Get new access tokens using a refresh token.
    """
    try:
        return refresh_access_token(refresh_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/api/auth/mfa/generate")
async def generate_mfa(user_id: str):
    """
    Generate an MFA secret for a user.
    
    This would typically be part of the user profile setup.
    """
    # Note: In a real application, this would be stored in the user profile
    secret = generate_mfa_secret()
    
    return {
        "secret": secret,
        "qr_code_url": get_provisional_qr_code(secret, f"user_{user_id}", "DesignInsightsAPI"),
    }

@app.post("/api/auth/mfa/verify")
async def verify_mfa(user_id: str, secret: str, code: str):
    """
    Verify an MFA code.
    
    This would typically be part of the login flow.
    """
    if verify_totp_code(secret, code):
        return {"verified": True}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code",
        )

@app.get("/")
async def root():
    """
    Root endpoint that returns basic API information.
    """
    return {
        "status": "online",
        "service": "Design Insights API",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running correctly.
    """
    return {
        "status": "healthy",
        "timestamp": os.path.getmtime(__file__)
    }

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Handle HTTP exceptions and return a standardized error response.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
        headers=exc.headers,
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Handle general exceptions and return a standardized error response.
    
    Logs the exception for debugging.
    """
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "An internal server error occurred"},
    )

# Main entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 