"""
Security middlewares for FastAPI applications.

This module provides security-related middleware for FastAPI applications, including:
- JWT authentication middleware
- Rate limiting middleware
- Input validation middleware

Note: Auth0 middleware has been deprecated as the project is migrating to Clerk.
"""

from backend.security.middlewares.jwt import (
    JWTMiddleware,
    add_jwt_middleware,
)

# Auth0 middleware removed as part of migration to Clerk
# Future Clerk middleware will be added here

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
    global_rate_period=60,  # 1 minute
    custom_rate_limits=None,
    input_validation_rules=None,
    public_paths=None,
    public_path_prefixes=None,
):
    """
    Configure and add all security middlewares to a FastAPI application.
    
    Args:
        app: The FastAPI application
        jwt_secret_key: Secret key for JWT validation
        redis_url: URL for Redis connection (for rate limiting)
        global_rate_limit: Global rate limit for all endpoints
        global_rate_period: Period for global rate limit in seconds
        custom_rate_limits: Dict of path patterns to custom rate limits
        input_validation_rules: List of input validation rules
        public_paths: List of paths that don't require authentication
        public_path_prefixes: List of path prefixes that don't require authentication
        
    Returns:
        The FastAPI application with middlewares added
        
    Note:
        Auth0 support has been removed. Integration with Clerk is planned.
    """
    # Add input validation middleware
    if input_validation_rules:
        app = add_input_validation_middleware(app, input_validation_rules)
    
    # Add rate limiting middleware
    if redis_url and (global_rate_limit or custom_rate_limits):
        app = add_rate_limit_middleware(
            app,
            redis_url=redis_url,
            rate_limit=global_rate_limit,
            rate_period=global_rate_period,
            custom_limits=custom_rate_limits
        )
    
    # Add authentication middleware (JWT)
    if jwt_secret_key:
        app = add_jwt_middleware(
            app, 
            secret_key=jwt_secret_key,
            public_paths=public_paths,
            public_path_prefixes=public_path_prefixes
        )
    
    return app

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
