"""
Utilities module for general-purpose functions and helpers.
Contains data validation, encryption, and other utility functions.
"""

from .validation import (
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
    sanitize_html,
    normalize_string,
    validate_and_normalize,
    strip_non_printable_chars,
    sanitize_filename,
    sanitize_sql_identifier,
    generate_secure_random_string,
    generate_secure_password
)

from .encryption import (
    Encryptor,
    encrypt_string,
    decrypt_string,
    secure_hash,
    hmac_sign,
    hmac_verify
) 