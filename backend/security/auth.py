"""
Authentication module providing core authentication and authorization functionality.

This module contains the main authentication logic, including functions for password 
hashing, JWT token creation and validation, and user authorization dependencies.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any, Union

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
import pyotp
import qrcode
from io import BytesIO
import base64
import os
import redis
from uuid import uuid4

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
REDIS_URL = os.getenv("REDIS_URL")

# Token blacklist with Redis (if available)
redis_client = None
if REDIS_URL:
    try:
        redis_client = redis.from_url(REDIS_URL)
    except:
        # Log the error but continue without Redis
        pass

# Authentication schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Enums
class TokenType(str, Enum):
    """Token types."""
    ACCESS = "access"
    REFRESH = "refresh"

class Role(str, Enum):
    """User roles."""
    USER = "user"
    ADMIN = "admin"

# Models
class User(BaseModel):
    """User model."""
    id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False
    roles: List[Role] = [Role.USER]
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None

class Token(BaseModel):
    """JWT token."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str

class TokenData(BaseModel):
    """JWT token data."""
    username: Optional[str] = None
    user_id: Optional[str] = None
    roles: List[Role] = []
    exp: Optional[int] = None
    type: TokenType = TokenType.ACCESS

# Password functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

# Token functions
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    
    expire = datetime.utcnow()
    if expires_delta:
        expire += expires_delta
    else:
        expire += timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": TokenType.ACCESS
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT refresh token."""
    to_encode = data.copy()
    
    expire = datetime.utcnow()
    if expires_delta:
        expire += expires_delta
    else:
        expire += timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": TokenType.REFRESH
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_tokens(data: Dict[str, Any]) -> Token:
    """Create both access and refresh tokens."""
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

def blacklist_token(token: str, expires_in: int) -> bool:
    """Add a token to the blacklist."""
    if redis_client:
        try:
            # Use token as key with a dummy value
            redis_client.setex(f"blacklist:{token}", expires_in, 1)
            return True
        except:
            # Log the error but continue
            pass
    
    # If Redis is not available, just return True
    # In production, you would want to use another method
    return True

def is_token_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted."""
    if redis_client:
        try:
            result = redis_client.get(f"blacklist:{token}")
            return result is not None
        except:
            # Log the error but continue
            pass
    
    # If Redis is not available, assume token is not blacklisted
    # In production, you would want to use another method
    return False

def refresh_access_token(refresh_token: str) -> Token:
    """Create a new access token using a refresh token."""
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify this is a refresh token
        if payload.get("type") != TokenType.REFRESH:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if token is blacklisted
        if is_token_blacklisted(refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract user data for new token
        user_data = {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "roles": payload.get("roles", [Role.USER])
        }
        
        # Create new access token
        access_token = create_access_token(user_data)
        
        return Token(
            access_token=access_token,
            token_type="bearer"
        )
        
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# MFA functions
def generate_mfa_secret() -> str:
    """Generate a new MFA secret key."""
    return pyotp.random_base32()

def get_totp_code(secret: str) -> str:
    """Generate a TOTP code from a secret."""
    totp = pyotp.TOTP(secret)
    return totp.now()

def verify_totp_code(code: str, secret: str) -> bool:
    """Verify a TOTP code against a secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def get_provisional_qr_code(secret: str, username: str, issuer: str = "YourApp") -> str:
    """Generate a QR code for MFA setup."""
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

# User dependency functions
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        username = payload.get("username")
        user_id = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
        
        # Check if token is blacklisted
        if is_token_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = TokenData(
            username=username,
            user_id=user_id,
            roles=payload.get("roles", [Role.USER]),
            exp=payload.get("exp"),
            type=payload.get("type", TokenType.ACCESS)
        )
        
        # In a real application, you would fetch the user from a database
        # For now, we'll just create a user object with the token data
        user = User(
            id=token_data.user_id,
            username=token_data.username,
            roles=token_data.roles,
            disabled=False
        )
        
        return user
        
    except jwt.JWTError:
        raise credentials_exception

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Get the current admin user."""
    if Role.ADMIN not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user 