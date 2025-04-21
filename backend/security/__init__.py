"""
Security module for the application.

Note: Authentication has been migrated to Clerk.
Validation and encryption utilities have been moved to the utils package.
This module maintains imports for backwards compatibility.
"""

# Import validation and encryption utilities from utils for backward compatibility
from backend.utils.validation import (
    is_valid_email as validate_email,
    is_strong_password as validate_password,
    sanitize_html,
    is_valid_url as validate_url,
    is_valid_uuid as validate_uuid,
    is_valid_date as validate_date,
    is_valid_phone as validate_phone,
    # Add any other validation functions you need
)

from backend.utils.encryption import (
    Encryptor,
    encrypt_string as encrypt_data,
    decrypt_string as decrypt_data,
    secure_hash as hash_data,
    hmac_verify as verify_hash,
    # Add any other encryption functions you need
)

# Keep the auth module imports
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

# Remove Auth0 imports since they're deprecated
# Add Clerk imports here when implemented

from backend.security.middlewares import (
    # JWT middleware
    JWTMiddleware,
    add_jwt_middleware,
    
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
    
    # Encryption module exports (renamed from utils)
    "Encryptor", "encrypt_data", "decrypt_data", "hash_data", "verify_hash",
    
    # Validation module exports (renamed from utils)
    "validate_email", "validate_password", "sanitize_html", "validate_url",
    "validate_uuid", "validate_date", "validate_phone",
    
    # Middleware exports
    "JWTMiddleware", "add_jwt_middleware", 
    "RateLimitMiddleware", "add_rate_limit_middleware", "RateLimitStrategy",
    "InputValidationMiddleware", "add_input_validation_middleware", "InputValidationRule",
    "configure_security_middlewares",
]
