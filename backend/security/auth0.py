"""
Auth0 authentication integration module.

This module provides functions and dependencies for integrating with Auth0's authentication service.
"""

from typing import Dict, List, Optional
import os
from functools import wraps

import jwt
from jwt.algorithms import RSAAlgorithm
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import requests

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "your-tenant.auth0.com")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE", "https://api.example.com")
ALGORITHMS = ["RS256"]

token_auth_scheme = HTTPBearer()

# Cache for Auth0 public key
_jwks_cache = {"keys": None, "last_updated": None}

# Auth0 User model
class Auth0User(BaseModel):
    """Auth0 user profile information."""
    sub: str
    nickname: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    email: Optional[str] = None
    email_verified: Optional[bool] = None
    
    # Custom claims
    permissions: List[str] = []
    roles: List[str] = []

def get_auth0_public_key(token: str) -> Dict:
    """Fetch Auth0 public key to verify JWT tokens."""
    from datetime import datetime, timedelta
    import json
    
    # Check if we need to refresh the JWKS cache
    if _jwks_cache["keys"] is None or _jwks_cache["last_updated"] is None or \
            datetime.now() - _jwks_cache["last_updated"] > timedelta(hours=24):
        
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        
        try:
            jwks_response = requests.get(jwks_url)
            jwks_response.raise_for_status()
            _jwks_cache["keys"] = jwks_response.json()["keys"]
            _jwks_cache["last_updated"] = datetime.now()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching Auth0 public key: {str(e)}"
            )
    
    # Get the kid from the token header
    try:
        token_header = jwt.get_unverified_header(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Find the matching key
    rsa_key = {}
    for key in _jwks_cache["keys"]:
        if key["kid"] == token_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
            break
    
    if not rsa_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find appropriate key",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    return rsa_key

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(token_auth_scheme)) -> Auth0User:
    """Validate the Auth0 JWT token and extract the user information."""
    token = credentials.credentials
    
    try:
        # Get the public key
        rsa_key = get_auth0_public_key(token)
        
        # Decode and validate the token
        payload = jwt.decode(
            token,
            RSAAlgorithm.from_jwk(rsa_key),
            algorithms=ALGORITHMS,
            audience=AUTH0_API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        
        # Extract permissions and roles from custom claims
        permissions = payload.get("permissions", [])
        roles = payload.get("https://example.com/roles", [])
        
        # Create the user object
        user = Auth0User(
            sub=payload["sub"],
            nickname=payload.get("nickname"),
            name=payload.get("name"),
            picture=payload.get("picture"),
            email=payload.get("email"),
            email_verified=payload.get("email_verified"),
            permissions=permissions,
            roles=roles
        )
        
        return user
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.JWTClaimsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect claims: please check the audience and issuer",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to validate token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )

# Decorator for authentication
def requires_auth(func):
    """Decorator to require authentication for an endpoint."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        """Wrapper function that injects the authenticated user."""
        # The user will be validated by the dependency
        return await func(*args, **kwargs)
    return wrapper

# Scopes and permissions helpers
def requires_scopes(required_scopes: List[str]):
    """Decorator to check if user has the required scopes/permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: Auth0User = Depends(get_current_user), **kwargs):
            for scope in required_scopes:
                if scope not in user.permissions:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Missing required scope: {scope}",
                    )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator

def requires_roles(required_roles: List[str]):
    """Decorator to check if user has the required roles."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: Auth0User = Depends(get_current_user), **kwargs):
            for role in required_roles:
                if role not in user.roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Missing required role: {role}",
                    )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator 