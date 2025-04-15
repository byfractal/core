# Security Checklist for Developers

This document provides a security checklist for developers working on the application. It outlines the security configurations, best practices, and requirements that must be followed to maintain the security of the application.

## Environment Setup

### Required Environment Variables

These environment variables must be set in production and development environments:

```
# JWT Authentication
JWT_SECRET_KEY=<strong random string of at least 32 chars>
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Encryption
MASTER_KEY=<strong random string of at least 32 chars>
ENCRYPTION_KEYS_FILE=encryption_keys.json

# Rate Limiting
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_DEFAULT=100
RATE_LIMIT_WINDOW_SECONDS=60

# CORS Settings
CORS_ORIGINS=https://your-app-domain.com,https://admin.your-app-domain.com
```

### Secret Key Generation

Use the following commands to generate secure random keys:

```bash
# For JWT_SECRET_KEY and MASTER_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

## Development Practices

### Authentication and Authorization

- [ ] Always use the provided authentication and authorization utilities
- [ ] Never create custom authentication mechanisms
- [ ] Use appropriate security scopes in route definitions
- [ ] Test access control with different user roles

Example of secure route definition:

```python
@router.get("/admin/users", response_model=List[UserResponse])
async def get_users(
    current_user: User = Security(get_current_admin_user)
):
    """Get all users. Requires admin privileges."""
    # Implementation...
```

### Input Validation

- [ ] Always use Pydantic models for request validation
- [ ] Define strict field constraints where applicable
- [ ] Add custom validators for complex validation rules
- [ ] Never trust client-provided data

Example of secure input validation:

```python
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator("password")
    def password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Password must contain at least one special character")
        return v
```

### Data Encryption

- [ ] Use the encryption utilities for any sensitive data
- [ ] Never store sensitive data in plaintext
- [ ] Don't hardcode encryption keys
- [ ] Rotate encryption keys periodically

Example of secure data encryption:

```python
from backend.security import encryption_manager

# Encrypt sensitive data
encrypted_data = encryption_manager.encrypt("sensitive information")

# Store encrypted data
user.credit_card = encrypted_data

# Later, decrypt data
decrypted_data = encryption_manager.decrypt(user.credit_card)
```

### Error Handling

- [ ] Use FastAPI's exception handlers
- [ ] Don't expose sensitive information in error messages
- [ ] Log errors appropriately
- [ ] Return appropriate HTTP status codes

Example of secure error handling:

```python
try:
    result = process_data(input_data)
    return result
except ValidationError:
    # Log the detailed error for internal debugging
    logger.error("Validation error", exc_info=True)
    # Return a generic error message to the client
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid input data"
    )
except DatabaseError:
    logger.error("Database error", exc_info=True)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An internal error occurred"
    )
```

### Database Access

- [ ] Use parameterized queries (SQLAlchemy)
- [ ] Don't use string concatenation for SQL
- [ ] Implement proper database connection pooling
- [ ] Minimize database privileges for application users

Example of secure database access:

```python
# GOOD: Using parameterized queries
result = await db.execute(
    select(User).where(User.email == email)
)

# BAD: Using string concatenation (NEVER DO THIS)
# result = await db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### File Operations

- [ ] Validate file paths
- [ ] Avoid path traversal vulnerabilities
- [ ] Set proper file permissions
- [ ] Limit file sizes and types

Example of secure file operations:

```python
from pathlib import Path
from backend.security import validate_path

def save_user_file(user_id: str, filename: str, content: bytes):
    # Validate the filename
    if not validate_path.is_safe_filename(filename):
        raise ValueError("Invalid filename")
    
    # Use path manipulation safely
    base_dir = Path("user_files")
    user_dir = base_dir / user_id
    user_dir.mkdir(exist_ok=True, parents=True)
    
    # Ensure we're still within the intended directory
    file_path = user_dir / filename
    if not str(file_path).startswith(str(base_dir)):
        raise ValueError("Path traversal detected")
    
    # Write the file
    with open(file_path, "wb") as f:
        f.write(content)
```

## Deployment Checklist

### Pre-Deployment

- [ ] Run security scans on code
- [ ] Check for dependency vulnerabilities
- [ ] Review security configurations
- [ ] Set up proper firewall rules

### Production Configuration

- [ ] Enable HTTPS with TLS 1.3
- [ ] Configure Content Security Policy
- [ ] Set up HTTP security headers
- [ ] Configure proper CORS settings

Example of Nginx security configuration:

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    # SSL Configuration
    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; font-src 'self'; connect-src 'self'" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Other configuration...
}
```

## Security Monitoring

### Logging

- [ ] Set up centralized logging (ELK stack, Grafana+Loki)
- [ ] Log security-relevant events
- [ ] Don't log sensitive information
- [ ] Implement log rotation

### Alerting

- [ ] Configure alerts for suspicious activities
- [ ] Set up monitoring for authentication failures
- [ ] Monitor for unusual API usage patterns
- [ ] Implement rate limiting alerts

## Security Incident Response

### Preparation

- [ ] Document incident response procedures
- [ ] Assign roles and responsibilities
- [ ] Set up communication channels
- [ ] Prepare incident templates

### Incident Handling

1. **Identification**: Detect and validate security incidents
2. **Containment**: Limit the damage of the incident
3. **Eradication**: Remove the cause of the incident
4. **Recovery**: Restore systems to normal operation
5. **Lessons Learned**: Document and improve from the incident 