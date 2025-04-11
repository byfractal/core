# Backend Structure

This document outlines the structure of the backend application after reorganization.

## Organizational Philosophy

The backend code is organized following these principles:

- **Functional separation** - Utilities are separated from domain-specific code
- **Reusability** - Common functions are placed in `utils/` regardless of domain
- **Domain specificity** - Application-specific implementations are grouped by domain (security, api, etc.)

## Directories

- `api/` - API endpoints and route handlers
- `archive/` - Reference code that might be useful in the future
- `data/` - Data files, including recommendations and cached data
- `docs/` - Backend-specific technical documentation
- `models/` - Data models and schemas
- `scripts/` - Utility scripts for maintenance, deployment and operations
- `security/` - Security-related code (auth, middlewares, etc.)
- `services/` - Business logic and service layer
- `tests/` - Test suites
- `utils/` - General utility functions for validation, encryption, etc.

## Organization of Security-related Code

Security-related code is split between two directories:

- `utils/` contains **low-level security utilities** like:
  - `encryption.py` - Generic encryption/decryption functions
  - `validation.py` - Input validation functions

- `security/` contains **application-specific security implementations** like:
  - Middlewares (rate limiting, input validation)
  - Authentication logic
  - Authorization policies

This separation follows modern framework best practices, allowing reuse of utilities while keeping application-specific security logic organized.

## Key Files

- `requirements.txt` - Python dependencies
- `SECURITY_IMPLEMENTATION.md` - Documentation of security implementations
- `STRUCTURE.md` - This file, documenting the project structure

## Migration Notes

- Authentication has been migrated from Auth0 to Clerk
- Validation and encryption utilities have been moved from security/ to utils/
- Recommendations data files have been consolidated in data/

## Development Guidelines

1. Keep utility functions in utils/ directory
2. Store all data files in data/ directory 
3. Use services/ for business logic implementation
4. Implement API endpoints in api/ directory
5. Add tests for all new functionality in tests/ 