# HCentric Interface Backend

Backend server for the HCentric UI Optimizer Chrome extension. This server provides API endpoints for authentication, feedback collection, design analysis, and UI optimization recommendations.

## 🚀 Setup

### Prerequisites

- Python 3.10+ 
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. Clone the repository (if not already done)
2. Set up a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Authentication
JWT_SECRET_KEY=your_secure_random_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
HOST=0.0.0.0
PORT=8080
DEBUG=true
CORS_ORIGINS=*

# OpenAI Configuration (for analysis)
OPENAI_API_KEY=your_openai_api_key
```

## 🚀 Running the Server

Use the provided script:

```bash
./run_server.sh
```

Or manually:

```bash
cd api
uvicorn main_simple:app --host 0.0.0.0 --port 8080
```

The API will be available at http://localhost:8080

## 🧪 Testing

Several test scripts are available in the `tests/` directory:

- `test_jwt_simple.py`: Tests JWT authentication
- `test_api_manual.py`: Tests basic API functionality
- `test_with_extension.py`: Tests endpoints used by the Chrome extension

Run tests with:

```bash
python tests/test_jwt_simple.py
```

## 📚 API Documentation

Once the server is running, visit http://localhost:8080/docs for the Swagger UI API documentation.

### Key Endpoints

#### Authentication

- `POST /api/auth/token`: Get JWT token with username/password
- `GET /api/auth/me`: Get current user information
- `GET /api/auth/public`: Public endpoint (no auth required)

#### Health Checks

- `GET /health`: Check API health status

#### Feedback

- `GET /api/feedback`: List all feedback
- `POST /api/feedback`: Create new feedback
- `GET /api/feedback/{feedback_id}`: Get specific feedback
- `PUT /api/feedback/{feedback_id}`: Update feedback
- `DELETE /api/feedback/{feedback_id}`: Delete feedback

#### Analysis

- `GET /api/analysis`: List all analyses
- `POST /api/analysis/generate`: Generate new analysis from feedback
- `GET /api/analysis/{analysis_id}`: Get specific analysis
- `DELETE /api/analysis/{analysis_id}`: Delete analysis

#### Design

- `POST /api/design/generate`: Generate design recommendations
- `POST /api/design/components/generate`: Generate UI components
- `POST /api/design/extract`: Extract UI components from website

## 🔒 Security

- JWT-based authentication
- Rate limiting options available
- CORS configuration for secure cross-origin requests

## 🛠️ Development

### Project Structure

```
backend/
├── api/               # API routers and endpoints
├── models/            # Data models and schemas
├── security/          # Authentication and security modules
├── services/          # Business logic and services
├── tests/             # Test scripts
├── utils/             # Utility functions
├── run_server.sh      # Server startup script
└── README.md          # This file
```

## 🤝 Contributing

1. Ensure all code follows the project's style and conventions
2. Add tests for new features
3. Update documentation as needed
4. Follow security best practices

## 📝 License

Copyright © 2023 HCentric 