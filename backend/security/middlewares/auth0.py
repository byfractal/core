"""
Auth0 middleware for FastAPI applications.
Provides integration with Auth0 authentication at the middleware level.
"""

from typing import List, Dict, Any, Optional, Callable
import json

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from backend.security.auth0 import validate_jwt, Auth0JWTError

# Paths that don't require authentication
PUBLIC_PATHS = [
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/auth/login",
    "/api/auth/callback",
    "/health",
    "/api/public",
]

# Path patterns that don't require authentication (for paths containing variables)
PUBLIC_PATH_PREFIXES = [
    "/static/",
    "/assets/",
]

class Auth0Middleware(BaseHTTPMiddleware):
    """
    Middleware for Auth0 authentication.
    
    This middleware validates the JWT token in the Authorization header
    for all non-public endpoints.
    """
    
    def __init__(
        self, 
        app: ASGIApp, 
        public_paths: Optional[List[str]] = None,
        public_path_prefixes: Optional[List[str]] = None,
        error_handler: Optional[Callable] = None,
    ):
        """
        Initialize the Auth0 middleware.
        
        Args:
            app: The FastAPI application
            public_paths: List of paths that don't require authentication
            public_path_prefixes: List of path prefixes that don't require authentication
            error_handler: Custom error handler function
        """
        super().__init__(app)
        self.public_paths = public_paths or PUBLIC_PATHS
        self.public_path_prefixes = public_path_prefixes or PUBLIC_PATH_PREFIXES
        self.error_handler = error_handler
        
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process the request through the middleware.
        
        Args:
            request: The incoming request
            call_next: Function to call the next middleware or endpoint
            
        Returns:
            The response from the route handler or an error response
        """
        # Skip validation for public paths
        path = request.url.path
        
        # Check if path is in public paths or starts with a public prefix
        if (path in self.public_paths or 
            any(path.startswith(prefix) for prefix in self.public_path_prefixes)):
            return await call_next(request)
            
        # Get the Authorization header
        auth_header = request.headers.get("Authorization", "")
        
        # If no Authorization header or not Bearer token, return 401
        if not auth_header or not auth_header.startswith("Bearer "):
            return self._handle_error(
                status_code=401,
                detail="Authorization header is missing or invalid"
            )
            
        # Extract the token
        token = auth_header.split(" ")[1]
        
        try:
            # Validate the token
            payload = await validate_jwt(token)
            
            # Store user info in request state for later use
            request.state.user = payload
            
            # Continue processing the request
            return await call_next(request)
            
        except Auth0JWTError as e:
            # Handle Auth0 JWT validation errors
            return self._handle_error(
                status_code=e.status_code,
                detail=e.error
            )
            
        except Exception as e:
            # Handle unexpected errors
            return self._handle_error(
                status_code=500,
                detail=f"Authentication error: {str(e)}"
            )
    
    def _handle_error(self, status_code: int, detail: str) -> JSONResponse:
        """
        Handle authentication errors.
        
        Args:
            status_code: HTTP status code
            detail: Error message
            
        Returns:
            JSON response with error details
        """
        if self.error_handler:
            return self.error_handler(status_code, detail)
            
        return JSONResponse(
            status_code=status_code,
            content={"detail": detail},
            headers={"WWW-Authenticate": "Bearer"}
        )

def add_auth0_middleware(
    app: FastAPI,
    public_paths: Optional[List[str]] = None,
    public_path_prefixes: Optional[List[str]] = None,
    error_handler: Optional[Callable] = None,
) -> FastAPI:
    """
    Add Auth0 middleware to a FastAPI application.
    
    Args:
        app: The FastAPI application
        public_paths: List of paths that don't require authentication
        public_path_prefixes: List of path prefixes that don't require authentication
        error_handler: Custom error handler function
        
    Returns:
        The FastAPI application with the middleware added
    """
    app.add_middleware(
        Auth0Middleware,
        public_paths=public_paths,
        public_path_prefixes=public_path_prefixes,
        error_handler=error_handler,
    )
    return app 