# Utilities

This directory contains utility functions and helpers used across the application.

## Organization Philosophy

The utilities are organized based on the **functional approach** rather than domain-specific categorization:

- General-purpose utility functions belong here, even if related to security concerns
- Application-specific security implementations belong in the `security/` directory

This separation follows modern frameworks' best practices (Django, FastAPI, Flask) where low-level utilities are kept separate from domain-specific implementations.

## Files

- `validation.py` - Input validation and sanitization utilities (used throughout the application)
- `encryption.py` - Core encryption and security-related utilities (used by both security and non-security modules)
- `__init__.py` - Package exports

## Security vs Utils

- **Utils**: Lower-level, reusable functions with minimal dependencies
- **Security**: Higher-level implementations specific to the application's security requirements

## Usage

Import these utilities directly from the package:

```python
from backend.utils import is_valid_email, encrypt_string

if is_valid_email(user_email):
    encrypted_data = encrypt_string(sensitive_data)
```

These utilities provide core functionality for data validation, security, and general-purpose operations used throughout the application. 