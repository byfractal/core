"""
Security module for the application.

This module provides security-related functionality, including:
- Authentication and authorization (JWT, OAuth2, MFA, Auth0)
- Encryption (AES-256, key rotation)
- Input validation and sanitization
- Security middlewares (rate limiting, input validation, JWT validation, Auth0)
"""

from backend.security.auth import (
    # Authentication and authorization functions
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    create_tokens,
    blacklist_token,
    refresh_access_token,
    
    # MFA functions
    generate_mfa_secret,
    get_totp_code,
    verify_totp_code,
    get_provisional_qr_code,
    
    # Models
    User,
    Token,
    TokenData,
    Role,
    TokenType,
    
    # Dependencies
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
)

from backend.security.auth0 import (
    # Auth0 authentication functions
    validate_jwt,
    get_current_user as get_auth0_user,
    
    # Auth0 models
    Auth0User,
    Auth0JWTError,
    
    # Auth0 decorators
    requires_auth,
    requires_scopes,
)

from backend.security.encryption import (
    # Encryption utilities
    EncryptionKeyManager,
    encrypt_data,
    decrypt_data,
    hash_data,
    verify_hash,
    generate_secure_key,
    generate_secure_token,
)

from backend.security.validation import (
    # Validation utilities
    validate_email,
    validate_password,
    sanitize_input,
    sanitize_html,
    validate_url,
    validate_uuid,
    validate_date,
    validate_phone,
    validate_ip_address,
)

from backend.security.middlewares import (
    # JWT middleware
    JWTMiddleware,
    add_jwt_middleware,
    
    # Auth0 middleware
    Auth0Middleware,
    add_auth0_middleware,
    
    # Rate limiting middleware
    RateLimitMiddleware,
    add_rate_limit_middleware,
    RateLimitStrategy,
    
    # Input validation middleware
    InputValidationMiddleware,
    add_input_validation_middleware,
    InputValidationRule,
    
    # Middleware configuration function
    configure_security_middlewares,
)

__all__ = [
    # Auth module exports
    "verify_password", "get_password_hash", "create_access_token", "create_refresh_token",
    "create_tokens", "blacklist_token", "refresh_access_token", "generate_mfa_secret",
    "get_totp_code", "verify_totp_code", "get_provisional_qr_code", "User", "Token", 
    "TokenData", "Role", "TokenType", "get_current_user", "get_current_active_user", 
    "get_current_admin_user",
    
    # Auth0 module exports
    "validate_jwt", "get_auth0_user", "Auth0User", "Auth0JWTError", "requires_auth", 
    "requires_scopes",
    
    # Encryption module exports
    "EncryptionKeyManager", "encrypt_data", "decrypt_data", "hash_data", "verify_hash",
    "generate_secure_key", "generate_secure_token",
    
    # Validation module exports
    "validate_email", "validate_password", "sanitize_input", "sanitize_html", "validate_url",
    "validate_uuid", "validate_date", "validate_phone", "validate_ip_address",
    
    # Middleware exports
    "JWTMiddleware", "add_jwt_middleware", "Auth0Middleware", "add_auth0_middleware",
    "RateLimitMiddleware", "add_rate_limit_middleware", "RateLimitStrategy",
    "InputValidationMiddleware", "add_input_validation_middleware", "InputValidationRule",
    "configure_security_middlewares",
]
