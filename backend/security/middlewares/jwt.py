"""
JWT authentication middleware for FastAPI.

This module provides middleware for JWT token authentication in FastAPI applications.
"""

from typing import List, Optional, Callable, Dict, Any
import re
import jwt
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

class JWTMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT authentication.
    
    This middleware validates JWT tokens in the Authorization header.
    """
    
    def __init__(
        self,
        app,
        secret_key: str,
        algorithm: str = "HS256",
        auth_header_name: str = "Authorization",
        auth_header_prefix: str = "Bearer",
        token_field_name: str = "access_token",
        public_paths: Optional[List[str]] = None,
        public_path_prefixes: Optional[List[str]] = None,
        auth_error_handler: Optional[Callable[[Request, Exception], Response]] = None,
    ):
        """
        Initialize the JWT middleware.
        
        Args:
            app: The FastAPI application
            secret_key: Secret key for JWT validation
            algorithm: Algorithm for JWT validation
            auth_header_name: Name of the authorization header
            auth_header_prefix: Prefix for the token in the authorization header
            token_field_name: Name of the token field in the query parameters or cookies
            public_paths: List of paths that don't require authentication
            public_path_prefixes: List of path prefixes that don't require authentication
            auth_error_handler: Optional function to handle authentication errors
        """
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.auth_header_name = auth_header_name
        self.auth_header_prefix = auth_header_prefix
        self.token_field_name = token_field_name
        self.public_paths = public_paths or []
        self.public_path_prefixes = public_path_prefixes or []
        self.auth_error_handler = auth_error_handler or self.default_auth_error_handler
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Process a request and validate JWT token.
        
        Args:
            request: The incoming request
            call_next: The next middleware in the chain
            
        Returns:
            The response
        """
        # Check if the path is public
        if self.is_public_path(request.url.path):
            return await call_next(request)
        
        # Get the token from the request
        token = self.get_token(request)
        if not token:
            return self.auth_error_handler(request, Exception("Missing authentication token"))
        
        # Validate the token
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            request.state.user = payload
            return await call_next(request)
        except jwt.ExpiredSignatureError:
            return self.auth_error_handler(request, Exception("Token has expired"))
        except jwt.InvalidTokenError:
            return self.auth_error_handler(request, Exception("Invalid token"))
        except Exception as e:
            return self.auth_error_handler(request, e)
    
    def get_token(self, request: Request) -> Optional[str]:
        """
        Get the token from the request.
        
        Args:
            request: The incoming request
            
        Returns:
            The token or None if not found
        """
        # Check the authorization header
        if self.auth_header_name in request.headers:
            auth_header = request.headers[self.auth_header_name]
            if auth_header.startswith(f"{self.auth_header_prefix} "):
                return auth_header[len(f"{self.auth_header_prefix} "):]
        
        # Check query parameters
        token = request.query_params.get(self.token_field_name)
        if token:
            return token
        
        # Check cookies
        if self.token_field_name in request.cookies:
            return request.cookies[self.token_field_name]
        
        return None
    
    def is_public_path(self, path: str) -> bool:
        """
        Check if a path is public.
        
        Args:
            path: The path to check
            
        Returns:
            True if the path is public, False otherwise
        """
        # Check exact matches
        if path in self.public_paths:
            return True
        
        # Check prefixes
        for prefix in self.public_path_prefixes:
            if path.startswith(prefix):
                return True
        
        # Check regex patterns
        for public_path in self.public_paths:
            if public_path.startswith("^") and re.match(public_path, path):
                return True
        
        return False
    
    def default_auth_error_handler(self, request: Request, exc: Exception) -> Response:
        """
        Default handler for authentication errors.
        
        Args:
            request: The incoming request
            exc: The exception
            
        Returns:
            A JSON response with the error details
        """
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"}
        )

def add_jwt_middleware(
    app,
    secret_key: str,
    algorithm: str = "HS256",
    auth_header_name: str = "Authorization",
    auth_header_prefix: str = "Bearer",
    token_field_name: str = "access_token",
    public_paths: Optional[List[str]] = None,
    public_path_prefixes: Optional[List[str]] = None,
    auth_error_handler: Optional[Callable[[Request, Exception], Response]] = None,
) -> Any:
    """
    Add JWT middleware to a FastAPI application.
    
    Args:
        app: The FastAPI application
        secret_key: Secret key for JWT validation
        algorithm: Algorithm for JWT validation
        auth_header_name: Name of the authorization header
        auth_header_prefix: Prefix for the token in the authorization header
        token_field_name: Name of the token field in the query parameters or cookies
        public_paths: List of paths that don't require authentication
        public_path_prefixes: List of path prefixes that don't require authentication
        auth_error_handler: Optional function to handle authentication errors
        
    Returns:
        The FastAPI application with middleware added
    """
    app.add_middleware(
        JWTMiddleware,
        secret_key=secret_key,
        algorithm=algorithm,
        auth_header_name=auth_header_name,
        auth_header_prefix=auth_header_prefix,
        token_field_name=token_field_name,
        public_paths=public_paths,
        public_path_prefixes=public_path_prefixes,
        auth_error_handler=auth_error_handler,
    )
    
    return app 