"""
Security module for the application.

This module provides security-related functionality, including:
- Authentication and authorization (JWT, OAuth2, MFA)
- Encryption (AES-256, key rotation)
- Input validation and sanitization
- Security middlewares (rate limiting, input validation, JWT validation)
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

from backend.security.encryption import (
    # High-level encryption
    Encryptor,
    encrypt_string,
    decrypt_string,
    
    # Low-level encryption
    AES256Cipher,
    EncryptionKeyManager,
    
    # Cryptographic primitives
    secure_hash,
    hmac_sign,
    hmac_verify,
)

from backend.security.validation import (
    # Validation functions
    is_valid_email,
    is_strong_password,
    is_valid_url,
    is_valid_uuid,
    is_valid_date,
    is_within_length,
    is_numeric,
    is_alpha,
    is_alphanumeric,
    is_valid_phone,
    
    # Sanitization functions
    sanitize_html,
    normalize_string,
    strip_non_printable_chars,
    sanitize_filename,
    sanitize_sql_identifier,
    
    # Generator functions
    generate_secure_random_string,
    generate_secure_password,
    
    # Utility functions
    validate_and_normalize,
)

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

__all__ = [
    # Auth module
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "create_refresh_token",
    "create_tokens",
    "blacklist_token",
    "refresh_access_token",
    "generate_mfa_secret",
    "get_totp_code",
    "verify_totp_code",
    "get_provisional_qr_code",
    "User",
    "Token",
    "TokenData",
    "Role",
    "TokenType",
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
    
    # Encryption module
    "Encryptor",
    "encrypt_string",
    "decrypt_string",
    "AES256Cipher",
    "EncryptionKeyManager",
    "secure_hash",
    "hmac_sign",
    "hmac_verify",
    
    # Validation module
    "is_valid_email",
    "is_strong_password",
    "is_valid_url",
    "is_valid_uuid",
    "is_valid_date",
    "is_within_length",
    "is_numeric",
    "is_alpha",
    "is_alphanumeric",
    "is_valid_phone",
    "sanitize_html",
    "normalize_string",
    "strip_non_printable_chars",
    "sanitize_filename",
    "sanitize_sql_identifier",
    "generate_secure_random_string",
    "generate_secure_password",
    "validate_and_normalize",
    
    # Middleware modules
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
]
