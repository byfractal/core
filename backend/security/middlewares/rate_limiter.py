"""
Rate limiting middleware for FastAPI applications.
Protects against brute-force attacks and API abuse.
Uses Redis for distributed rate limiting across multiple instances.
"""

import time
from typing import Callable, Dict, Optional, Union, List, Tuple

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

import asyncio
import aioredis

# Rate limit strategies
class RateLimitStrategy:
    """Base class for rate limit strategies."""
    
    async def is_rate_limited(self, key: str) -> Tuple[bool, int]:
        """
        Check if a key is rate limited.
        
        Args:
            key: The key to check
            
        Returns:
            Tuple containing:
                - Whether the key is rate limited
                - Time remaining (in seconds) until the limit resets
        """
        raise NotImplementedError()
    
    async def increment(self, key: str) -> None:
        """
        Increment the counter for a key.
        
        Args:
            key: The key to increment
        """
        raise NotImplementedError()

class FixedWindowStrategy(RateLimitStrategy):
    """
    Fixed window rate limiting strategy.
    
    Allows a fixed number of requests in a time window.
    """
    
    def __init__(
        self, 
        redis: aioredis.Redis, 
        window_seconds: int, 
        max_requests: int
    ):
        """
        Initialize the fixed window strategy.
        
        Args:
            redis: Redis client
            window_seconds: Time window in seconds
            max_requests: Maximum number of requests allowed in the window
        """
        self.redis = redis
        self.window_seconds = window_seconds
        self.max_requests = max_requests
    
    async def is_rate_limited(self, key: str) -> Tuple[bool, int]:
        """
        Check if a key is rate limited using a fixed window.
        
        Args:
            key: The key to check
            
        Returns:
            Tuple containing:
                - Whether the key is rate limited
                - Time remaining (in seconds) until the limit resets
        """
        # Get the current count and TTL
        count = await self.redis.get(key)
        if count is None:
            return False, 0
        
        count = int(count)
        ttl = await self.redis.ttl(key)
        
        # Check if the count exceeds the limit
        if count >= self.max_requests:
            return True, ttl
        
        return False, 0
    
    async def increment(self, key: str) -> None:
        """
        Increment the counter for a key.
        
        Args:
            key: The key to increment
        """
        # Increment the counter, creating it if it doesn't exist
        await self.redis.incr(key)
        
        # Set the expiration if it's a new key
        ttl = await self.redis.ttl(key)
        if ttl == -1:
            await self.redis.expire(key, self.window_seconds)

class SlidingWindowStrategy(RateLimitStrategy):
    """
    Sliding window rate limiting strategy.
    
    More precise than fixed window, but more expensive.
    Counts requests in the last N seconds.
    """
    
    def __init__(
        self, 
        redis: aioredis.Redis, 
        window_seconds: int, 
        max_requests: int
    ):
        """
        Initialize the sliding window strategy.
        
        Args:
            redis: Redis client
            window_seconds: Time window in seconds
            max_requests: Maximum number of requests allowed in the window
        """
        self.redis = redis
        self.window_seconds = window_seconds
        self.max_requests = max_requests
    
    async def is_rate_limited(self, key: str) -> Tuple[bool, int]:
        """
        Check if a key is rate limited using a sliding window.
        
        Args:
            key: The key to check
            
        Returns:
            Tuple containing:
                - Whether the key is rate limited
                - Time remaining (in seconds) until the limit resets
        """
        # Get the current timestamp
        now = int(time.time())
        
        # Remove expired entries
        await self.redis.zremrangebyscore(key, 0, now - self.window_seconds)
        
        # Count the number of requests in the window
        count = await self.redis.zcard(key)
        
        # Check if the count exceeds the limit
        if count >= self.max_requests:
            # Get the oldest timestamp in the set
            oldest = await self.redis.zrange(key, 0, 0, withscores=True)
            if oldest:
                # Calculate the time until the oldest entry expires
                _, timestamp = oldest[0]
                reset_time = int(timestamp) + self.window_seconds - now
                return True, max(0, reset_time)
            
            return True, self.window_seconds
        
        return False, 0
    
    async def increment(self, key: str) -> None:
        """
        Add the current timestamp to the sorted set for a key.
        
        Args:
            key: The key to increment
        """
        # Add the current timestamp to the sorted set
        now = int(time.time())
        await self.redis.zadd(key, {str(now): now})
        
        # Set the expiration if it's a new key
        ttl = await self.redis.ttl(key)
        if ttl == -1:
            await self.redis.expire(key, self.window_seconds * 2)  # Extra buffer

class RateLimitConfig:
    """Configuration for a rate limit rule."""
    
    def __init__(
        self,
        limit: int,
        window_seconds: int,
        strategy: str = "fixed",
        key_func: Callable[[Request], str] = None,
    ):
        """
        Initialize the rate limit configuration.
        
        Args:
            limit: Maximum number of requests allowed
            window_seconds: Time window in seconds
            strategy: Rate limiting strategy ("fixed" or "sliding")
            key_func: Function to extract the rate limit key from a request
        """
        self.limit = limit
        self.window_seconds = window_seconds
        self.strategy = strategy
        self.key_func = key_func or self._default_key_func
    
    @staticmethod
    def _default_key_func(request: Request) -> str:
        """
        Default function to extract the rate limit key from a request.
        Uses the client's IP address.
        
        Args:
            request: The request
            
        Returns:
            Rate limit key
        """
        # Get the client's IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0]
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ratelimit:{ip}"

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting in FastAPI applications.
    
    Limits the number of requests from a client within a time window.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        redis_url: str,
        global_rate_limit: Optional[RateLimitConfig] = None,
        path_rate_limits: Optional[Dict[str, RateLimitConfig]] = None,
        prefix_rate_limits: Optional[Dict[str, RateLimitConfig]] = None,
        method_rate_limits: Optional[Dict[str, RateLimitConfig]] = None,
    ):
        """
        Initialize the rate limit middleware.
        
        Args:
            app: ASGI application
            redis_url: Redis connection URL
            global_rate_limit: Rate limit applied to all requests
            path_rate_limits: Rate limits for specific paths
            prefix_rate_limits: Rate limits for path prefixes
            method_rate_limits: Rate limits for specific HTTP methods
        """
        super().__init__(app)
        self.redis_url = redis_url
        self.redis = None
        self.global_rate_limit = global_rate_limit
        self.path_rate_limits = path_rate_limits or {}
        self.prefix_rate_limits = prefix_rate_limits or {}
        self.method_rate_limits = method_rate_limits or {}
        self.strategies = {}
    
    async def initialize(self) -> None:
        """Initialize the Redis connection and strategies."""
        if self.redis is None:
            self.redis = await aioredis.from_url(self.redis_url, decode_responses=True)
    
    def get_strategy(self, config: RateLimitConfig) -> RateLimitStrategy:
        """
        Get or create a rate limiting strategy for a configuration.
        
        Args:
            config: Rate limit configuration
            
        Returns:
            Rate limiting strategy
        """
        key = f"{config.strategy}:{config.window_seconds}:{config.limit}"
        
        if key not in self.strategies:
            if config.strategy == "sliding":
                self.strategies[key] = SlidingWindowStrategy(
                    self.redis, config.window_seconds, config.limit
                )
            else:
                self.strategies[key] = FixedWindowStrategy(
                    self.redis, config.window_seconds, config.limit
                )
        
        return self.strategies[key]
    
    def get_config_for_request(self, request: Request) -> Optional[RateLimitConfig]:
        """
        Get the rate limit configuration for a request.
        
        Args:
            request: The request
            
        Returns:
            Rate limit configuration or None if no configuration applies
        """
        path = request.url.path
        method = request.method
        
        # Check for exact path match
        if path in self.path_rate_limits:
            return self.path_rate_limits[path]
        
        # Check for path prefix match
        for prefix, config in self.prefix_rate_limits.items():
            if path.startswith(prefix):
                return config
        
        # Check for method match
        if method in self.method_rate_limits:
            return self.method_rate_limits[method]
        
        # Fall back to global rate limit
        return self.global_rate_limit
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process the request and apply rate limiting.
        
        Args:
            request: Incoming request
            call_next: Next middleware or endpoint
            
        Returns:
            Response from the next middleware or endpoint
        """
        await self.initialize()
        
        # Get the rate limit configuration for the request
        config = self.get_config_for_request(request)
        if config is None:
            return await call_next(request)
        
        # Get the rate limit key
        key = config.key_func(request)
        
        # Get the rate limiting strategy
        strategy = self.get_strategy(config)
        
        # Check if the request is rate limited
        is_limited, reset_after = await strategy.is_rate_limited(key)
        if is_limited:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests",
                    "reset_after": reset_after,
                },
                headers={"Retry-After": str(reset_after)},
            )
        
        # Increment the counter
        await strategy.increment(key)
        
        # Process the request
        response = await call_next(request)
        
        return response

def add_rate_limit_middleware(
    app: FastAPI,
    redis_url: str,
    global_limit: Optional[int] = None,
    global_window_seconds: Optional[int] = None,
    path_limits: Optional[Dict[str, Tuple[int, int]]] = None,
    prefix_limits: Optional[Dict[str, Tuple[int, int]]] = None,
    method_limits: Optional[Dict[str, Tuple[int, int]]] = None,
) -> None:
    """
    Add rate limit middleware to a FastAPI application.
    
    Args:
        app: FastAPI application
        redis_url: Redis connection URL
        global_limit: Rate limit applied to all requests
        global_window_seconds: Time window in seconds for global rate limit
        path_limits: Rate limits for specific paths (path -> (limit, window_seconds))
        prefix_limits: Rate limits for path prefixes (prefix -> (limit, window_seconds))
        method_limits: Rate limits for specific HTTP methods (method -> (limit, window_seconds))
    """
    # Create rate limit configurations
    global_rate_limit = None
    if global_limit and global_window_seconds:
        global_rate_limit = RateLimitConfig(global_limit, global_window_seconds)
    
    path_rate_limits = {}
    if path_limits:
        for path, (limit, window) in path_limits.items():
            path_rate_limits[path] = RateLimitConfig(limit, window)
    
    prefix_rate_limits = {}
    if prefix_limits:
        for prefix, (limit, window) in prefix_limits.items():
            prefix_rate_limits[prefix] = RateLimitConfig(limit, window)
    
    method_rate_limits = {}
    if method_limits:
        for method, (limit, window) in method_limits.items():
            method_rate_limits[method] = RateLimitConfig(limit, window)
    
    # Add the middleware
    app.add_middleware(
        RateLimitMiddleware,
        redis_url=redis_url,
        global_rate_limit=global_rate_limit,
        path_rate_limits=path_rate_limits,
        prefix_rate_limits=prefix_rate_limits,
        method_rate_limits=method_rate_limits,
    )
