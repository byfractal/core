"""
Authentication router for the API.
Handles Auth0 authentication flow, callbacks, and user management.
"""

import os
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel

from backend.security.auth0 import (
    Auth0User,
    get_current_user,
    requires_auth,
    requires_scopes,
)

# Create the router
auth_router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Get Auth0 configuration from environment
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")
AUTH0_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")

# Response models
class UserProfile(BaseModel):
    """User profile response model."""
    sub: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    permissions: List[str] = []

class LoginResponse(BaseModel):
    """Login response with Auth0 login URL."""
    login_url: str

@auth_router.get("/login")
async def login():
    """
    Get the Auth0 login URL.
    
    Returns:
        Login URL for initiating the Auth0 authentication flow
    """
    if not all([AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CALLBACK_URL, AUTH0_AUDIENCE]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth0 configuration missing"
        )
    
    # Construct the Auth0 Universal Login URL
    login_url = (
        f"https://{AUTH0_DOMAIN}/authorize"
        f"?response_type=code"
        f"&client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
        f"&audience={AUTH0_AUDIENCE}"
        f"&scope=openid%20profile%20email"
    )
    
    return LoginResponse(login_url=login_url)

@auth_router.get("/callback")
async def auth_callback(code: str, state: Optional[str] = None):
    """
    Handle the Auth0 callback after user authentication.
    
    This endpoint is called by Auth0 after user authentication.
    It exchanges the authorization code for tokens and redirects to the application.
    
    Args:
        code: Authorization code from Auth0
        state: Optional state parameter for CSRF protection
        
    Returns:
        Redirect to the application with tokens
    """
    if not all([AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_CALLBACK_URL]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth0 configuration missing"
        )
    
    try:
        import requests
        
        # Exchange the authorization code for tokens
        token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
        token_payload = {
            "grant_type": "authorization_code",
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "code": code,
            "redirect_uri": AUTH0_CALLBACK_URL
        }
        
        # Make the token request
        token_response = requests.post(token_url, json=token_payload)
        token_data = token_response.json()
        
        if "error" in token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Auth0 error: {token_data.get('error_description', token_data['error'])}"
            )
        
        # Get the tokens
        access_token = token_data.get("access_token")
        id_token = token_data.get("id_token")
        
        # Redirect to frontend with tokens
        # In a real application, you might use secure cookies or another method
        # to transmit these tokens safely
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        redirect_url = f"{frontend_url}/auth-callback?access_token={access_token}&id_token={id_token}"
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )

@auth_router.get("/profile", response_model=UserProfile)
@requires_auth
async def get_profile(current_user: Auth0User = Depends(get_current_user)):
    """
    Get the user profile.
    
    This endpoint requires authentication.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        User profile information
    """
    return UserProfile(
        sub=current_user.sub,
        email=current_user.email,
        name=current_user.name,
        picture=current_user.picture,
        permissions=current_user.permissions
    )

@auth_router.get("/admin")
@requires_scopes(["read:admin"])
async def admin_route(current_user: Auth0User = Depends(get_current_user)):
    """
    Admin only route.
    
    This endpoint requires the "read:admin" permission.
    
    Args:
        current_user: The authenticated user with admin permissions
        
    Returns:
        Admin information
    """
    return {
        "message": "Admin access granted",
        "user": current_user.name or current_user.sub,
        "permissions": current_user.permissions
    }

@auth_router.get("/public")
async def public_route():
    """
    Public route that doesn't require authentication.
    
    Returns:
        Public information
    """
    return {
        "message": "This is a public endpoint"
    } 