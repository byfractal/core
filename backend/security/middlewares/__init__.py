"""
Security middlewares for FastAPI applications.

This module provides security-related middleware for FastAPI applications, including:
- JWT authentication middleware
- Rate limiting middleware
- Input validation middleware
"""

from backend.security.middlewares.jwt import (
    JWTMiddleware,
    add_jwt_middleware,
)

from backend.security.middlewares.rate_limiter import (
    RateLimitMiddleware,
    RateLimitStrategy,
    FixedWindowStrategy,
    SlidingWindowStrategy,
    RateLimitConfig,
    add_rate_limit_middleware,
)

from backend.security.middlewares.input_validation import (
    InputValidationMiddleware,
    InputValidationRule,
    add_input_validation_middleware,
)

def configure_security_middlewares(
    app,
    jwt_secret_key=None,
    redis_url=None,
    global_rate_limit=None,
    global_rate_limit_window=None,
    exclude_paths_from_auth=None,
    exclude_paths_from_rate_limit=None,
    validation_rules=None,
):
    """
    Configure all security middlewares for a FastAPI application.
    
    Args:
        app: FastAPI application
        jwt_secret_key: Secret key for JWT authentication
        redis_url: Redis URL for rate limiting
        global_rate_limit: Maximum requests per window
        global_rate_limit_window: Time window in seconds
        exclude_paths_from_auth: Paths to exclude from JWT authentication
        exclude_paths_from_rate_limit: Paths to exclude from rate limiting
        validation_rules: List of input validation rules
    """
    # Configure JWT middleware if JWT secret key is provided
    if jwt_secret_key:
        public_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh-token",
            "/health",
        ]
        
        if exclude_paths_from_auth:
            public_paths.extend(exclude_paths_from_auth)
        
        add_jwt_middleware(
            app=app,
            secret_key=jwt_secret_key,
            public_paths=public_paths,
        )
    
    # Configure rate limiting middleware if Redis URL is provided
    if redis_url and global_rate_limit and global_rate_limit_window:
        # Default path limits for sensitive endpoints
        path_limits = {
            "/api/auth/login": (10, 60),  # 10 requests per minute
            "/api/auth/register": (5, 60),  # 5 requests per minute
            "/api/auth/refresh-token": (10, 60),  # 10 requests per minute
        }
        
        # Method limits for POST/PUT/DELETE
        method_limits = {
            "POST": (100, 60),  # 100 POST requests per minute
            "PUT": (100, 60),  # 100 PUT requests per minute
            "DELETE": (50, 60),  # 50 DELETE requests per minute
        }
        
        exclude_paths = exclude_paths_from_rate_limit or []
        
        add_rate_limit_middleware(
            app=app,
            redis_url=redis_url,
            global_limit=global_rate_limit,
            global_window_seconds=global_rate_limit_window,
            path_limits=path_limits,
            method_limits=method_limits,
        )
    
    # Configure input validation middleware
    add_input_validation_middleware(
        app=app,
        rules=validation_rules,
        max_body_size=10 * 1024 * 1024,  # 10MB
        max_url_length=2048,
        block_on_validation_error=True,
    )

__all__ = [
    "JWTMiddleware",
    "add_jwt_middleware",
    "RateLimitMiddleware",
    "RateLimitStrategy",
    "FixedWindowStrategy",
    "SlidingWindowStrategy", 
    "RateLimitConfig",
    "add_rate_limit_middleware",
    "InputValidationMiddleware",
    "InputValidationRule",
    "add_input_validation_middleware",
    "configure_security_middlewares",
]
