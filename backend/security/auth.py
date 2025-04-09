"""
Authentication and authorization module.
Implements JWT/OAuth2 with token rotation, MFA, and RBAC.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from uuid import uuid4

import jwt
import pyotp
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from passlib.context import CryptContext
from pydantic import BaseModel, Field, EmailStr, SecretStr

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is required")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
TOKEN_BLACKLIST = set()  # In-memory blacklist, use Redis in production

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token validation
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/auth/login",
    scopes={
        "user": "Regular user access",
        "admin": "Administrator access",
        "superadmin": "Super administrator access",
    },
)

# Role enumeration
class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

# Token type enumeration
class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

# User model
class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    disabled: bool = False
    roles: List[Role] = [Role.USER]
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None

# Token data model for JWT payload
class TokenData(BaseModel):
    sub: str
    scopes: List[str] = []
    exp: int
    iat: int
    jti: str
    type: TokenType

# Token response model
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

# MFA response models
class MFASecret(BaseModel):
    secret: str
    qr_code_url: str

class MFAVerify(BaseModel):
    code: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain text password matches the hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)

def create_token(subject: str, scopes: List[str], expires_delta: timedelta, token_type: TokenType) -> str:
    """
    Create a JWT token.
    
    Args:
        subject: Subject (usually user ID)
        scopes: List of permission scopes
        expires_delta: Token expiration time
        token_type: Type of token (access or refresh)
        
    Returns:
        JWT token as a string
    """
    expires = datetime.utcnow() + expires_delta
    
    # Create the JWT payload
    payload = {
        "sub": subject,
        "scopes": scopes,
        "exp": expires.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "jti": str(uuid4()),  # Unique identifier for the token
        "type": token_type.value,
    }
    
    # Create and return the token
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(subject: str, scopes: List[str]) -> str:
    """
    Create an access token.
    
    Args:
        subject: Subject (usually user ID)
        scopes: List of permission scopes
        
    Returns:
        Access token as a string
    """
    return create_token(
        subject=subject,
        scopes=scopes,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type=TokenType.ACCESS,
    )

def create_refresh_token(subject: str, scopes: List[str]) -> str:
    """
    Create a refresh token.
    
    Args:
        subject: Subject (usually user ID)
        scopes: List of permission scopes
        
    Returns:
        Refresh token as a string
    """
    return create_token(
        subject=subject,
        scopes=scopes,
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        token_type=TokenType.REFRESH,
    )

def create_tokens(subject: str, scopes: List[str]) -> Token:
    """
    Create both access and refresh tokens.
    
    Args:
        subject: Subject (usually user ID)
        scopes: List of permission scopes
        
    Returns:
        Token object with access and refresh tokens
    """
    return Token(
        access_token=create_access_token(subject, scopes),
        refresh_token=create_refresh_token(subject, scopes),
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

def blacklist_token(token: str) -> None:
    """
    Add a token to the blacklist to invalidate it.
    
    Args:
        token: JWT token to blacklist
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_jti = payload.get("jti")
        if token_jti:
            TOKEN_BLACKLIST.add(token_jti)
    except jwt.PyJWTError:
        pass  # Ignore invalid tokens

def verify_jwt_token(token: str, token_type: TokenType) -> TokenData:
    """
    Verify a JWT token.
    
    Args:
        token: JWT token to verify
        token_type: Expected token type
        
    Returns:
        TokenData object with the decoded payload
        
    Raises:
        HTTPException: If the token is invalid, expired, or has the wrong type
    """
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract token data
        token_data = TokenData(
            sub=payload.get("sub"),
            scopes=payload.get("scopes", []),
            exp=payload.get("exp"),
            iat=payload.get("iat"),
            jti=payload.get("jti"),
            type=payload.get("type"),
        )
        
        # Check if the token has the expected type
        if token_data.type != token_type.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type.value} token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if the token is blacklisted
        if token_data.jti in TOKEN_BLACKLIST:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return token_data
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

def refresh_access_token(refresh_token: str) -> Token:
    """
    Create new tokens using a refresh token.
    
    Args:
        refresh_token: Refresh token
        
    Returns:
        Token object with new access and refresh tokens
        
    Raises:
        HTTPException: If the refresh token is invalid
    """
    # Verify the refresh token
    token_data = verify_jwt_token(refresh_token, TokenType.REFRESH)
    
    # Blacklist the old refresh token
    blacklist_token(refresh_token)
    
    # Create new tokens
    return create_tokens(token_data.sub, token_data.scopes)

# Multi-Factor Authentication (MFA) functions
def generate_mfa_secret() -> str:
    """
    Generate a new MFA secret.
    
    Returns:
        Base32 encoded secret for TOTP
    """
    return pyotp.random_base32()

def get_totp_code(secret: str) -> str:
    """
    Get the current TOTP code for a secret.
    
    Args:
        secret: Base32 encoded secret
        
    Returns:
        Current TOTP code
    """
    totp = pyotp.TOTP(secret)
    return totp.now()

def verify_totp_code(secret: str, code: str) -> bool:
    """
    Verify a TOTP code against a secret.
    
    Args:
        secret: Base32 encoded secret
        code: TOTP code to verify
        
    Returns:
        True if the code is valid, False otherwise
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def get_provisional_qr_code(secret: str, name: str, issuer: str) -> str:
    """
    Get a QR code URI for a provisional TOTP setup.
    
    Args:
        secret: Base32 encoded secret
        name: Name for the TOTP account
        issuer: Issuer name
        
    Returns:
        URI for the QR code
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=name, issuer_name=issuer)

# Dependency functions for FastAPI
async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Dependency for getting the current user from a JWT token.
    
    Args:
        security_scopes: Security scopes required for the endpoint
        token: JWT token
        
    Returns:
        User object
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't have the required scopes
    """
    # Verify the token
    token_data = verify_jwt_token(token, TokenType.ACCESS)
    
    # Check if the user has the required scopes
    if security_scopes.scopes:
        for scope in security_scopes.scopes:
            if scope not in token_data.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not enough permissions. Required: {security_scopes.scope_str}",
                    headers={"WWW-Authenticate": f"Bearer scope=\"{security_scopes.scope_str}\""},
                )
    
    # In a real application, you would retrieve the user from the database
    # This is just a placeholder implementation for demonstration
    user = User(
        id=token_data.sub,
        email="user@example.com",
        username="user",
        roles=[Role(role) for role in token_data.scopes if role in [r.value for r in Role]],
    )
    
    return user

async def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=["user"]),
) -> User:
    """
    Dependency for getting the current active user.
    
    Args:
        current_user: Current user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If the user is disabled
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    return current_user

async def get_current_admin_user(
    current_user: User = Security(get_current_user, scopes=["admin"]),
) -> User:
    """
    Dependency for getting the current admin user.
    
    Args:
        current_user: Current user
        
    Returns:
        User object with admin privileges
    """
    return current_user

# Additional function for handling user authentication (would connect to a database in a real app)
async def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username and password.
    
    Args:
        username: Username or email
        password: Plain text password
        
    Returns:
        User object if authentication is successful, None otherwise
    """
    # In a real application, you would retrieve the user from the database
    # and verify the password hash
    
    # This is just a placeholder implementation for demonstration
    if username == "demo@example.com" and password == "Secure#123":
        return User(
            id="user123",
            email="demo@example.com",
            username="demo",
            full_name="Demo User",
            roles=[Role.USER],
        )
    
    return None
