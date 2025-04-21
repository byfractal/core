# Security

This directory contains application-specific security implementations.

## Organization Philosophy

Security code is organized following a functional approach:

- **Application-specific security implementations** are placed here
- **Low-level security utilities** are placed in the `utils/` directory

## Directories and Files

- `middlewares/` - Security middleware implementations:
  - `jwt.py` - JWT authentication middleware
  - `rate_limiter.py` - Rate limiting middleware  
  - `input_validation.py` - Input validation middleware
- `__init__.py` - Package exports and backward compatibility

## Migration to Clerk

The application is currently migrating from Auth0 to Clerk for authentication.
During this transition:

- Auth0 middleware has been removed
- Clerk integration will be added in the future

## Utils vs Security

This separation follows modern best practices:

- **Security/** - Application-specific implementations that depend on the application's context
- **Utils/** - Lower-level utilities that can be reused across different contexts

## Usage

Import security components directly:

```python
from backend.security import JWTMiddleware, add_jwt_middleware

# Add JWT authentication to FastAPI app
app = add_jwt_middleware(app, secret_key="your-secret-key")
``` 