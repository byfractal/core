"""
JWT authentication middleware for FastAPI applications.
Handles token validation and user authentication at the middleware level.
"""

import time
from typing import Callable, Dict, Optional

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from backend.security.auth import TokenType, verify_jwt_token

# Paths that don't require authentication
PUBLIC_PATHS = [
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/refresh-token",
    "/health",
]

# Path patterns that don't require authentication (for paths containing variables)
PUBLIC_PATH_PREFIXES = [
    "/static/",
    "/assets/",
]

class JWTMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT authentication in FastAPI applications.
    
    Validates JWT tokens for all requests except those to public paths.
    Extracts user information and adds it to the request state.
    """
    
    def __init__(
        self, 
        app: ASGIApp, 
        secret_key: str,
        public_paths: Optional[list] = None,
        public_path_prefixes: Optional[list] = None,
        auth_header_prefix: str = "Bearer",
    ):
        """
        Initialize the JWT middleware.
        
        Args:
            app: ASGI application
            secret_key: Secret key used to decode JWT tokens
            public_paths: List of paths that don't require authentication
            public_path_prefixes: List of path prefixes that don't require authentication
            auth_header_prefix: Prefix for the Authorization header
        """
        super().__init__(app)
        self.secret_key = secret_key
        self.public_paths = public_paths or PUBLIC_PATHS
        self.public_path_prefixes = public_path_prefixes or PUBLIC_PATH_PREFIXES
        self.auth_header_prefix = auth_header_prefix
    
    def is_path_public(self, path: str) -> bool:
        """
        Check if a path is public (doesn't require authentication).
        
        Args:
            path: Request path
            
        Returns:
            True if the path is public, False otherwise
        """
        if path in self.public_paths:
            return True
        
        for prefix in self.public_path_prefixes:
            if path.startswith(prefix):
                return True
        
        return False
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process the request and validate JWT token.
        
        Args:
            request: Incoming request
            call_next: Next middleware or endpoint
            
        Returns:
            Response from the next middleware or endpoint
        """
        # Skip authentication for public paths
        if self.is_path_public(request.url.path):
            return await call_next(request)
        
        # Get the authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header is missing"},
                headers={"WWW-Authenticate": self.auth_header_prefix},
            )
        
        # Check the authorization header format
        auth_parts = auth_header.split()
        if len(auth_parts) != 2 or auth_parts[0] != self.auth_header_prefix:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authorization header format"},
                headers={"WWW-Authenticate": self.auth_header_prefix},
            )
        
        token = auth_parts[1]
        
        try:
            # Verify the token
            token_data = verify_jwt_token(token, TokenType.ACCESS)
            
            # Add user information to request state
            request.state.user_id = token_data.sub
            request.state.scopes = token_data.scopes
            request.state.token_jti = token_data.jti
            
            # Process the request
            return await call_next(request)
            
        except Exception as e:
            # Handle token validation errors
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": str(e)},
                headers={"WWW-Authenticate": self.auth_header_prefix},
            )

def add_jwt_middleware(
    app: FastAPI, 
    secret_key: str,
    public_paths: Optional[list] = None,
    public_path_prefixes: Optional[list] = None,
) -> None:
    """
    Add JWT middleware to a FastAPI application.
    
    Args:
        app: FastAPI application
        secret_key: Secret key used to decode JWT tokens
        public_paths: List of paths that don't require authentication
        public_path_prefixes: List of path prefixes that don't require authentication
    """
    app.add_middleware(
        JWTMiddleware,
        secret_key=secret_key,
        public_paths=public_paths,
        public_path_prefixes=public_path_prefixes,
    )
