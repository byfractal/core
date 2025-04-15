# Technical Security Implementation Details

This document provides technical implementation details of our security architecture. It's intended for developers and security engineers who need to understand or extend the security components.

## JWT Authentication Implementation

### Token Generation and Validation

The JWT tokens are created using the `PyJWT` library with the following characteristics:

1. **Token Structure**:
   ```python
   {
       "sub": "<user_id>",                 # Subject (user ID)
       "scopes": ["user", "admin"],        # Authorization scopes
       "exp": 1646753382,                  # Expiration timestamp
       "iat": 1646751582,                  # Issued at timestamp
       "jti": "550e8400-e29b-41d4-a716-446655440000", # Unique token ID
       "type": "access"                    # Token type
   }
   ```

2. **Token Creation Process**:
   ```python
   def create_token(subject: str, scopes: List[str], expires_delta: timedelta, token_type: TokenType) -> str:
       expires = datetime.utcnow() + expires_delta
       
       payload = {
           "sub": subject,
           "scopes": scopes,
           "exp": expires.timestamp(),
           "iat": datetime.utcnow().timestamp(),
           "jti": str(uuid4()),  # Unique identifier for the token
           "type": token_type.value,
       }
       
       return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
   ```

3. **Token Validation Process**:
   ```python
   def verify_jwt_token(token: str, token_type: TokenType) -> TokenData:
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
           
           # Check token type
           if token_data.type != token_type.value:
               raise HTTPException(...)
           
           # Check if blacklisted
           if token_data.jti in TOKEN_BLACKLIST:
               raise HTTPException(...)
           
           return token_data
           
       except jwt.ExpiredSignatureError:
           raise HTTPException(...)
       except jwt.JWTError:
           raise HTTPException(...)
   ```

### Token Blacklisting

We implement token blacklisting to invalidate tokens before their expiration:

```python
# In-memory blacklist (use Redis in production)
TOKEN_BLACKLIST = set()

def blacklist_token(token: str) -> None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_jti = payload.get("jti")
        if token_jti:
            TOKEN_BLACKLIST.add(token_jti)
    except jwt.PyJWTError:
        pass  # Ignore invalid tokens
```

In production, this should be implemented with Redis for distributed environments:

```python
import redis

# Initialize Redis client
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))

def blacklist_token(token: str) -> None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_jti = payload.get("jti")
        expiration = payload.get("exp")
        
        if token_jti and expiration:
            # Calculate TTL (expiry - current time)
            current_timestamp = datetime.utcnow().timestamp()
            ttl = max(0, int(expiration - current_timestamp))
            
            # Add to Redis with automatic expiration
            redis_client.set(f"blacklist:{token_jti}", "1", ex=ttl)
    except jwt.PyJWTError:
        pass

def is_token_blacklisted(jti: str) -> bool:
    return bool(redis_client.get(f"blacklist:{jti}"))
```

## Multi-Factor Authentication Implementation

Our MFA implementation uses Time-based One-Time Passwords (TOTP) with the PyOTP library:

1. **Secret Generation**:
   ```python
   def generate_mfa_secret() -> str:
       return pyotp.random_base32()
   ```

2. **TOTP Verification**:
   ```python
   def verify_totp_code(secret: str, code: str) -> bool:
       totp = pyotp.TOTP(secret)
       return totp.verify(code)
   ```

3. **QR Code Generation**:
   ```python
   def get_provisional_qr_code(secret: str, name: str, issuer: str) -> str:
       totp = pyotp.TOTP(secret)
       return totp.provisioning_uri(name=name, issuer_name=issuer)
   ```

## Role-Based Access Control Implementation

RBAC is implemented using FastAPI's dependency injection system:

1. **Role Enum**:
   ```python
   class Role(str, Enum):
       USER = "user"
       ADMIN = "admin"
       SUPERADMIN = "superadmin"
   ```

2. **Security Dependencies**:
   ```python
   # Get user with specific role requirements
   async def get_current_user(
       security_scopes: SecurityScopes,
       token: str = Depends(oauth2_scheme),
   ) -> User:
       # Verify token
       token_data = verify_jwt_token(token, TokenType.ACCESS)
       
       # Check scopes
       for scope in security_scopes.scopes:
           if scope not in token_data.scopes:
               raise HTTPException(...)
       
       # Get user (from database in real implementation)
       user = User(...)
       
       return user

   # Role-specific dependencies
   async def get_current_admin_user(
       current_user: User = Security(get_current_user, scopes=["admin"]),
   ) -> User:
       return current_user
   ```

3. **Usage in Routes**:
   ```python
   @router.get("/admin/dashboard")
   async def admin_dashboard(
       current_user: User = Depends(get_current_admin_user)
   ):
       # Only accessible to admin users
       return {"message": "Admin dashboard"}
   ```

## AES-256 Encryption Implementation

Our encryption implementation uses a two-tier key system for secure data encryption:

1. **Key Management**:
   ```python
   class EncryptionKeyManager:
       def __init__(self, master_key: str, keys_file: str):
           self.master_key = master_key
           self.keys_file = keys_file
           self.current_key_id = None
           self.keys = {}
           self._load_or_initialize_keys()
           
       def _load_or_initialize_keys(self):
           try:
               # Load existing keys
               with open(self.keys_file, "r") as f:
                   encrypted_keys = json.load(f)
                   
               # Decrypt the keys with the master key
               fernet = Fernet(self._derive_key_from_password(self.master_key))
               keys_data = json.loads(fernet.decrypt(encrypted_keys["data"].encode()).decode())
               
               self.keys = {k: b64decode(v) for k, v in keys_data["keys"].items()}
               self.current_key_id = keys_data["current_key_id"]
           except (FileNotFoundError, json.JSONDecodeError, InvalidToken):
               # Initialize new keys
               self._generate_new_key()
               self._save_keys()
       
       def _generate_new_key(self):
           # Generate a new encryption key
           key_id = str(uuid.uuid4())
           self.keys[key_id] = os.urandom(32)  # 256 bits
           self.current_key_id = key_id
           return key_id
           
       def _save_keys(self):
           # Encrypt all keys with the master key
           keys_data = {
               "current_key_id": self.current_key_id,
               "keys": {k: b64encode(v).decode() for k, v in self.keys.items()}
           }
           
           fernet = Fernet(self._derive_key_from_password(self.master_key))
           encrypted_data = fernet.encrypt(json.dumps(keys_data).encode())
           
           # Save to file
           with open(self.keys_file, "w") as f:
               json.dump({"data": encrypted_data.decode()}, f)
   ```

2. **Encryption and Decryption**:
   ```python
   def encrypt(self, data: str) -> Dict[str, str]:
       # Get the current key
       key_id = self.current_key_id
       key = self.keys[key_id]
       
       # Generate a random IV
       iv = os.urandom(16)
       
       # Create cipher components
       cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
       encryptor = cipher.encryptor()
       
       # Pad data
       padder = padding.PKCS7(algorithms.AES.block_size).padder()
       padded_data = padder.update(data.encode()) + padder.finalize()
       
       # Encrypt
       ciphertext = encryptor.update(padded_data) + encryptor.finalize()
       
       # Create and sign metadata
       metadata = {
           "kid": key_id,
           "iv": b64encode(iv).decode(),
           "ct": b64encode(ciphertext).decode(),
       }
       
       # Add authentication tag
       h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
       h.update(json.dumps(metadata).encode())
       metadata["tag"] = b64encode(h.finalize()).decode()
       
       return metadata
       
   def decrypt(self, encrypted_data: Dict[str, str]) -> str:
       # Extract metadata
       key_id = encrypted_data["kid"]
       iv = b64decode(encrypted_data["iv"])
       ciphertext = b64decode(encrypted_data["ct"])
       tag = b64decode(encrypted_data["tag"])
       
       # Verify key exists
       if key_id not in self.keys:
           raise ValueError(f"Unknown key ID: {key_id}")
       
       key = self.keys[key_id]
       
       # Verify authentication tag
       metadata_for_verification = {
           "kid": key_id,
           "iv": encrypted_data["iv"],
           "ct": encrypted_data["ct"],
       }
       
       h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
       h.update(json.dumps(metadata_for_verification).encode())
       try:
           h.verify(tag)
       except InvalidSignature:
           raise ValueError("Invalid authentication tag")
           
       # Decrypt
       cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
       decryptor = cipher.decryptor()
       padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
       
       # Unpad
       unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
       plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
       
       return plaintext.decode()
   ```

## Rate Limiting Implementation

Our rate limiting middleware implements both fixed window and sliding window strategies:

1. **Rate Limit Strategy Interface**:
   ```python
   class RateLimitStrategy:
       """Base class for rate limit strategies."""
       
       async def is_rate_limited(self, key: str) -> Tuple[bool, int]:
           """
           Check if a key is rate limited.
           
           Args:
               key: The key to check
               
           Returns:
               Tuple of (is_limited, retry_after_seconds)
           """
           raise NotImplementedError()
   ```

2. **Fixed Window Strategy**:
   ```python
   class FixedWindowStrategy(RateLimitStrategy):
       def __init__(self, redis_client, max_requests: int, window_seconds: int):
           self.redis = redis_client
           self.max_requests = max_requests
           self.window_seconds = window_seconds
           
       async def is_rate_limited(self, key: str) -> Tuple[bool, int]:
           # Get current window key
           timestamp = int(time.time())
           window_key = f"{key}:{timestamp // self.window_seconds}"
           
           # Increment counter for this window
           count = await self.redis.incr(window_key)
           
           # Set expiration if this is a new window
           if count == 1:
               await self.redis.expire(window_key, self.window_seconds)
               
           # Check if rate limited
           if count > self.max_requests:
               # Calculate time until next window
               next_window = (timestamp // self.window_seconds + 1) * self.window_seconds
               retry_after = next_window - timestamp
               return True, retry_after
               
           return False, 0
   ```

3. **Sliding Window Strategy**:
   ```python
   class SlidingWindowStrategy(RateLimitStrategy):
       def __init__(self, redis_client, max_requests: int, window_seconds: int):
           self.redis = redis_client
           self.max_requests = max_requests
           self.window_seconds = window_seconds
           
       async def is_rate_limited(self, key: str) -> Tuple[bool, int]:
           # Get current timestamp
           now = time.time()
           window_start = now - self.window_seconds
           
           # Add the current request to the sorted set with timestamp as score
           await self.redis.zadd(key, {str(now): now})
           
           # Remove requests outside the current window
           await self.redis.zremrangebyscore(key, 0, window_start)
           
           # Set expiration for the key
           await self.redis.expire(key, self.window_seconds)
           
           # Count requests in the current window
           count = await self.redis.zcard(key)
           
           # Check if rate limited
           if count > self.max_requests:
               # Get the oldest timestamp in the window
               oldest = await self.redis.zrange(key, 0, 0, withscores=True)
               if oldest:
                   _, oldest_time = oldest[0]
                   retry_after = int(self.window_seconds - (now - oldest_time))
                   return True, max(1, retry_after)
               return True, self.window_seconds
               
           return False, 0
   ```

4. **Middleware Implementation**:
   ```python
   class RateLimitMiddleware(BaseHTTPMiddleware):
       def __init__(
           self,
           app: ASGIApp,
           strategy: RateLimitStrategy,
           key_func: Callable[[Request], str] = None,
           status_code: int = status.HTTP_429_TOO_MANY_REQUESTS,
           exclude_paths: List[str] = None
       ):
           super().__init__(app)
           self.strategy = strategy
           self.key_func = key_func or self._default_key_func
           self.status_code = status_code
           self.exclude_paths = exclude_paths or []
           
       async def dispatch(
           self, request: Request, call_next: RequestResponseEndpoint
       ) -> Response:
           # Check if path is excluded
           if any(request.url.path.startswith(path) for path in self.exclude_paths):
               return await call_next(request)
               
           # Get rate limit key
           key = self.key_func(request)
           
           # Check if rate limited
           is_limited, retry_after = await self.strategy.is_rate_limited(key)
           
           if is_limited:
               return JSONResponse(
                   status_code=self.status_code,
                   content={
                       "detail": "Too many requests",
                       "retry_after": retry_after
                   },
                   headers={"Retry-After": str(retry_after)}
               )
               
           # Process the request
           return await call_next(request)
           
       def _default_key_func(self, request: Request) -> str:
           # Default: IP-based rate limiting
           forwarded = request.headers.get("X-Forwarded-For")
           ip = forwarded.split(",")[0] if forwarded else request.client.host
           return f"ratelimit:{ip}:{request.url.path}"
   ```

## Input Validation Middleware

Our input validation middleware provides protection against common attack vectors:

```python
class InputValidationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        validation_rules: List[InputValidationRule] = None,
        log_violations: bool = True,
        block_violations: bool = True
    ):
        super().__init__(app)
        self.validation_rules = validation_rules or self._default_validation_rules()
        self.log_violations = log_violations
        self.block_violations = block_violations
        
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip validation for non-JSON requests
        content_type = request.headers.get("Content-Type", "")
        if "application/json" not in content_type and request.method in ("POST", "PUT", "PATCH"):
            return await call_next(request)
            
        # Cache original request body
        body = await request.body()
        
        # Reconstruct request with cached body
        async def receive():
            return {"type": "http.request", "body": body}
            
        request._receive = receive
        
        # Validate request body
        try:
            body_str = body.decode()
            if body_str:
                violations = self._validate_content(body_str)
                if violations:
                    if self.log_violations:
                        logger.warning(
                            f"Input validation violation: {violations} in request to {request.url.path}"
                        )
                    if self.block_violations:
                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={"detail": "Invalid input detected"}
                        )
        except UnicodeDecodeError:
            # Not a text payload, skip validation
            pass
            
        # Process the request
        return await call_next(request)
        
    def _validate_content(self, content: str) -> List[str]:
        """
        Check content against all validation rules.
        
        Args:
            content: The content to validate
            
        Returns:
            List of violation descriptions (empty if no violations)
        """
        violations = []
        
        for rule in self.validation_rules:
            if rule.pattern.search(content):
                violations.append(rule.description)
                
        return violations
        
    def _default_validation_rules(self) -> List[InputValidationRule]:
        """
        Default validation rules.
        """
        return [
            InputValidationRule(
                pattern=re.compile(SQL_INJECTION_PATTERNS[0], re.IGNORECASE),
                description="SQL injection attempt detected"
            ),
            InputValidationRule(
                pattern=re.compile(XSS_PATTERNS[0], re.IGNORECASE),
                description="Cross-site scripting attempt detected"
            ),
            # Add more rules...
        ]
```

## JWT Middleware Implementation

The JWT middleware automatically validates JWT tokens for all protected routes:

```python
class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        secret_key: str,
        algorithm: str = "HS256",
        exclude_paths: List[str] = None,
        token_prefix: str = "Bearer"
    ):
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.exclude_paths = exclude_paths or []
        self.token_prefix = token_prefix
        
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Check if path is public
        if self._is_path_excluded(request.url.path):
            return await call_next(request)
            
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Parse token
        token_parts = auth_header.split()
        if len(token_parts) != 2 or token_parts[0] != self.token_prefix:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authentication credentials"},
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        token = token_parts[1]
        
        # Validate token
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            
            # Check token type
            if payload.get("type") != TokenType.ACCESS.value:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
                
            # Check if token is blacklisted
            jti = payload.get("jti")
            if jti in TOKEN_BLACKLIST:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
                
            # Add user info to request state
            request.state.user_id = payload.get("sub")
            request.state.scopes = payload.get("scopes", [])
            
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token has expired"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        except (jwt.JWTError, HTTPException) as e:
            detail = "Invalid token" if isinstance(e, jwt.JWTError) else e.detail
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": detail},
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Process the request
        return await call_next(request)
        
    def _is_path_excluded(self, path: str) -> bool:
        """
        Check if a path is excluded from JWT validation.
        """
        # Check exact matches
        if path in PUBLIC_PATHS:
            return True
            
        # Check prefixes
        for prefix in PUBLIC_PATH_PREFIXES:
            if path.startswith(prefix):
                return True
                
        return False
```

## Security Middleware Integration with FastAPI

All security middlewares are integrated with FastAPI through a unified setup function:

```python
def configure_security_middlewares(
    app: FastAPI,
    jwt_secret_key: str = None,
    redis_url: str = None,
    global_rate_limit: int = None,
    global_rate_limit_window: int = None,
    exclude_paths: List[str] = None,
    validate_input: bool = True,
    log_violations: bool = True,
    block_violations: bool = True
) -> FastAPI:
    """
    Configure security middlewares for a FastAPI application.
    
    Args:
        app: FastAPI application
        jwt_secret_key: JWT secret key
        redis_url: Redis URL for rate limiting and token blacklisting
        global_rate_limit: Maximum number of requests per window
        global_rate_limit_window: Window size in seconds
        exclude_paths: Paths to exclude from security middlewares
        validate_input: Whether to validate input
        log_violations: Whether to log validation violations
        block_violations: Whether to block validation violations
        
    Returns:
        FastAPI application with security middlewares
    """
    # Use default values or environment variables if not provided
    jwt_secret_key = jwt_secret_key or os.getenv("JWT_SECRET_KEY")
    redis_url = redis_url or os.getenv("REDIS_URL")
    global_rate_limit = global_rate_limit or int(os.getenv("RATE_LIMIT_DEFAULT", "100"))
    global_rate_limit_window = global_rate_limit_window or int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    exclude_paths = exclude_paths or []
    
    # Add JWT middleware
    if jwt_secret_key:
        app.add_middleware(
            JWTMiddleware,
            secret_key=jwt_secret_key,
            exclude_paths=exclude_paths + PUBLIC_PATHS
        )
    
    # Add rate limiting middleware
    if redis_url and global_rate_limit:
        redis_client = aioredis.from_url(redis_url)
        strategy = FixedWindowStrategy(
            redis_client,
            max_requests=global_rate_limit,
            window_seconds=global_rate_limit_window
        )
        app.add_middleware(
            RateLimitMiddleware,
            strategy=strategy,
            exclude_paths=exclude_paths
        )
    
    # Add input validation middleware
    if validate_input:
        app.add_middleware(
            InputValidationMiddleware,
            log_violations=log_violations,
            block_violations=block_violations
        )
    
    return app
```

## Usage in Fast API Application

Here's how all security components are integrated into a FastAPI application:

```python
from backend.security import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    configure_security_middlewares,
    encryption_manager,
)

app = FastAPI(title="Secure API")

# Configure security middlewares
app = configure_security_middlewares(
    app=app,
    global_rate_limit=100,
    global_rate_limit_window=60,
    validate_input=True
)

# Authentication routes
@app.post("/api/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access and refresh tokens
    token = create_tokens(
        user.id,
        [role.value for role in user.roles]
    )
    
    return token

@app.post("/api/auth/refresh-token")
async def refresh_token(refresh_token: str):
    # Refresh the access token
    new_tokens = refresh_access_token(refresh_token)
    return new_tokens

# Protected routes
@app.get("/api/users/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    return current_user

@app.get("/api/admin/users", response_model=List[User])
async def get_all_users(
    current_user: User = Depends(get_current_admin_user)
):
    # Admin-only endpoint
    return [...]  # Get users from database

# Example of encrypting sensitive data
@app.post("/api/users/payment-info")
async def save_payment_info(
    payment_info: PaymentInfo,
    current_user: User = Depends(get_current_active_user)
):
    # Encrypt the credit card number
    encrypted_card = encryption_manager.encrypt(payment_info.credit_card)
    
    # Save to database
    # ...
    
    return {"status": "saved"}
```

## Conclusion

This document provides the technical implementation details of our security architecture. These implementations follow industry best practices and provide a robust foundation for protecting the application against common security threats.

For any questions or concerns about these implementations, please contact the security team. 