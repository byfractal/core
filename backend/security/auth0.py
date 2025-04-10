"""
Auth0 authentication module for FastAPI applications.
Implements JWT validation, scopes verification, and user management.
"""

import os
import json
import time
import jwt
import requests
from typing import Dict, List, Optional, Set, Any, Callable, Union
from functools import wraps
import re

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator, EmailStr, Field

# Auth0 configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")
ALGORITHMS = ["RS256"]

# JWT validation cache
_jwks_cache = None
_jwks_cache_timestamp = 0
JWKS_CACHE_TTL = 86400  # 24 hours

# Set up security helper
security = HTTPBearer()

# Custom exception for Auth0 JWT errors
class Auth0JWTError(Exception):
    """Exception raised for Auth0 JWT validation errors."""
    
    def __init__(self, error: str, status_code: int = 401):
        self.error = error
        self.status_code = status_code
        super().__init__(self.error)

class Auth0User(BaseModel):
    """
    Auth0 user model.
    
    Contains user information extracted from the validated JWT token.
    """
    sub: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    
    @validator('sub')
    def validate_sub(cls, v):
        """Validate that sub is in the Auth0 format."""
        if not re.match(r'^auth0\|[a-zA-Z0-9]+$', v) and not re.match(r'^[a-zA-Z0-9]+\|[a-zA-Z0-9]+$', v):
            raise ValueError('Invalid Auth0 subject ID format')
        return v
        
    def has_permissions(self, required_permissions: List[str]) -> bool:
        """
        Check if the user has all the required permissions.
        
        Args:
            required_permissions: List of permissions to check
            
        Returns:
            True if the user has all required permissions, False otherwise
        """
        if not required_permissions:
            return True
            
        user_permissions = set(self.permissions)
        return all(perm in user_permissions for perm in required_permissions)

async def get_jwks():
    """
    Fetch the JSON Web Key Set (JWKS) from Auth0.
    
    Uses caching to avoid repeated requests.
    
    Returns:
        The JWKS as a dictionary
    """
    global _jwks_cache, _jwks_cache_timestamp
    
    current_time = time.time()
    
    # If we have a cached JWKS that's still valid, use it
    if _jwks_cache and (current_time - _jwks_cache_timestamp) < JWKS_CACHE_TTL:
        return _jwks_cache
    
    # Otherwise, fetch a new JWKS
    try:
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        response = requests.get(jwks_url)
        response.raise_for_status()
        
        # Update cache
        _jwks_cache = response.json()
        _jwks_cache_timestamp = current_time
        
        return _jwks_cache
        
    except requests.RequestException as e:
        raise Auth0JWTError(f"Failed to fetch JWKS: {str(e)}", 500)

async def validate_jwt(token: str) -> Dict[str, Any]:
    """
    Validate a JWT token from Auth0.
    
    Args:
        token: The JWT token to validate
        
    Returns:
        The decoded JWT payload
        
    Raises:
        Auth0JWTError: If the token is invalid
    """
    if not AUTH0_DOMAIN or not AUTH0_API_AUDIENCE:
        raise Auth0JWTError("Auth0 configuration missing", 500)
    
    try:
        # Get the JWKS
        jwks = await get_jwks()
        
        # Parse the token header
        unverified_header = jwt.get_unverified_header(token)
        
        # Find the key with the matching kid
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
                
        if not rsa_key:
            raise Auth0JWTError("Invalid key ID (kid)", 401)
        
        # Verify the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=AUTH0_API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise Auth0JWTError("Token has expired", 401)
    except jwt.JWTClaimsError:
        raise Auth0JWTError("Invalid claims (audience or issuer)", 401)
    except jwt.InvalidTokenError:
        raise Auth0JWTError("Invalid token", 401)
    except Exception as e:
        raise Auth0JWTError(f"Token validation failed: {str(e)}", 401)

async def get_token_from_header(auth: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract the JWT token from the Authorization header.
    
    Args:
        auth: The HTTP Authorization credentials
        
    Returns:
        The JWT token
    """
    return auth.credentials

async def get_current_user(token: str = Depends(get_token_from_header)) -> Auth0User:
    """
    Get the current user from the validated JWT token.
    
    Args:
        token: The JWT token
        
    Returns:
        The Auth0User object containing user information
        
    Raises:
        HTTPException: If the token is invalid
    """
    try:
        payload = await validate_jwt(token)
        
        # Extract user information
        user_data = {
            "sub": payload["sub"],
            "permissions": payload.get("permissions", [])
        }
        
        # Add optional fields if they exist
        for field in ["email", "name", "picture"]:
            if field in payload:
                user_data[field] = payload[field]
        
        return Auth0User(**user_data)
        
    except Auth0JWTError as e:
        raise HTTPException(status_code=e.status_code, detail=e.error)

def requires_auth(f):
    """
    Decorator to require authentication for a route.
    
    Usage:
        @app.get("/api/private")
        @requires_auth
        async def private(current_user: Auth0User = Depends(get_current_user)):
            return {"message": f"Hello, {current_user.name}!"}
    """
    @wraps(f)
    async def decorated(*args, **kwargs):
        return await f(*args, **kwargs)
    return decorated

def requires_scopes(required_permissions: List[str]):
    """
    Decorator to require specific permissions for a route.
    
    Args:
        required_permissions: List of permissions required for the route
        
    Usage:
        @app.get("/api/admin")
        @requires_scopes(["read:admin", "write:admin"])
        async def admin(current_user: Auth0User = Depends(get_current_user)):
            return {"message": "Admin access granted"}
    """
    def decorator(f):
        @wraps(f)
        async def decorated(current_user: Auth0User = Depends(get_current_user), *args, **kwargs):
            if not current_user.has_permissions(required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await f(current_user=current_user, *args, **kwargs)
        return decorated
    return decorator 