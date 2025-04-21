# Backend API with Auth0 Authentication

This project is a secure FastAPI backend application with Auth0 authentication integration.

## Features

- **Authentication**: Auth0 integration with JWT validation and role-based access control
- **Security**: Rate limiting, input validation, and secure middleware
- **API Endpoints**: RESTful API endpoints for various functionalities
- **Modular Design**: Well-structured code with separation of concerns

## Getting Started

### Prerequisites

- Python 3.8 or higher
- [Poetry](https://python-poetry.org/) or pip for dependency management
- Redis (optional, for rate limiting)
- Auth0 account (for authentication)

### Installation

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd project-directory
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your specific configuration values.

### Running the Application

```bash
python -m backend.api.main
```

Or using uvicorn directly:

```bash
uvicorn backend.api.main:app --reload
```

The API will be available at http://localhost:8000

## Authentication with Auth0

This project uses Auth0 for authentication and authorization. For detailed setup instructions, see [AUTH0_SETUP.md](AUTH0_SETUP.md).

### Key Auth0 Features

- JWT token validation
- Role-based access control with permissions
- Authentication middleware for protected routes
- Auth0 Universal Login integration

## API Documentation

Once the server is running, API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── api/                  # API routes and endpoints
│   ├── main.py           # Main FastAPI application
│   ├── auth.py           # Authentication routes
│   └── ...               # Other API modules
├── security/             # Security-related modules
│   ├── auth.py           # JWT authentication
│   ├── auth0.py          # Auth0 integration
│   ├── encryption.py     # Data encryption utilities
│   ├── validation.py     # Input validation utilities
│   └── middlewares/      # Security middleware
│       ├── jwt.py        # JWT middleware
│       ├── auth0.py      # Auth0 middleware
│       ├── rate_limiter.py # Rate limiting middleware
│       └── input_validation.py # Input validation middleware
└── models/               # Data models and business logic
```

## Security Features

- **JWT Validation**: Secure validation of Auth0 JWT tokens
- **RBAC**: Role-based access control using Auth0 permissions
- **Rate Limiting**: Protection against brute-force attacks
- **Input Validation**: Prevents injection attacks and validates user inputs
- **Middleware Protection**: Multiple security layers for API endpoints

## License

[MIT License](LICENSE)

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Auth0](https://auth0.com/)
- [Python](https://www.python.org/)
