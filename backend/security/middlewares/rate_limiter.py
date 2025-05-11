"""
Redis-based rate limiting middleware for FastAPI.
This module provides a middleware for rate limiting API requests using Redis.
"""

import time
import asyncio
from typing import Callable, Dict, Optional, Union
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RateLimiter:
    """
    Redis-based rate limiting middleware for FastAPI.
    
    This middleware limits the number of requests by client IP address.
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        redis_host: Optional[str] = None,
        redis_port: Optional[int] = None,
        redis_password: Optional[str] = None,
        redis_db: Optional[int] = None,
        requests: int = 100,
        period: int = 60,
        headers: bool = True,
    ):
        """
        Initialize the rate limiter.
        
        Args:
            redis_url: Redis URL (overrides other Redis params if provided)
            redis_host: Redis host
            redis_port: Redis port
            redis_password: Redis password
            redis_db: Redis database number
            requests: Maximum number of requests allowed per period
            period: Time period in seconds
            headers: Whether to add rate limit headers to responses
        """
        # Get settings from environment variables if not provided
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self.redis_host = redis_host or os.getenv("REDIS_HOST", "localhost")
        self.redis_port = redis_port or int(os.getenv("REDIS_PORT", "6379"))
        self.redis_password = redis_password or os.getenv("REDIS_PASSWORD", "")
        self.redis_db = redis_db or int(os.getenv("REDIS_DB", "0"))
        self.requests = requests or int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.period = period or int(os.getenv("RATE_LIMIT_PERIOD", "60"))
        self.headers = headers
        
        # Initialize Redis connection
        self.redis_pool = None
    
    async def _get_redis_pool(self) -> redis.ConnectionPool:
        """Get or create Redis connection pool."""
        if self.redis_pool is None:
            if self.redis_url:
                self.redis_pool = redis.ConnectionPool.from_url(self.redis_url)
            else:
                self.redis_pool = redis.ConnectionPool(
                    host=self.redis_host,
                    port=self.redis_port,
                    password=self.redis_password,
                    db=self.redis_db,
                    decode_responses=True
                )
        return self.redis_pool
    
    async def _check_rate_limit(self, client_id: str) -> Dict[str, Union[int, bool]]:
        """
        Check if the client has exceeded the rate limit.
        
        Args:
            client_id: Client identifier (usually IP address)
            
        Returns:
            Dictionary with rate limit information
        """
        pool = await self._get_redis_pool()
        async with redis.Redis(connection_pool=pool) as r:
            # Current timestamp
            now = int(time.time())
            
            # Create a Redis key for this client
            key = f"rate_limit:{client_id}"
            
            # Create a sliding window of requests
            pipe = r.pipeline()
            await pipe.zremrangebyscore(key, 0, now - self.period)
            await pipe.zadd(key, {now: now})
            await pipe.expire(key, self.period)
            await pipe.zcard(key)
            results = await pipe.execute()
            
            # Get the number of requests in the current window
            request_count = results[3]
            
            return {
                "limit": self.requests,
                "remaining": max(0, self.requests - request_count),
                "reset": now + self.period,
                "allowed": request_count <= self.requests
            }
    
    def add_rate_limit_headers(self, response: Response, rate_limit_info: Dict[str, Union[int, bool]]) -> None:
        """Add rate limit headers to the response."""
        if self.headers:
            response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset"])
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        FastAPI middleware handler for rate limiting.
        
        Args:
            request: FastAPI request object
            call_next: Function to call the next middleware or endpoint
            
        Returns:
            FastAPI response object
        """
        # Get client IP address
        client_id = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for certain paths (optional)
        path = request.url.path
        if path == "/health" or path.startswith("/docs") or path.startswith("/openapi"):
            return await call_next(request)
        
        try:
            # Check rate limit
            rate_limit_info = await self._check_rate_limit(client_id)
            
            # If allowed, proceed with the request
            if rate_limit_info["allowed"]:
                response = await call_next(request)
                self.add_rate_limit_headers(response, rate_limit_info)
                return response
            
            # If not allowed, return 429 Too Many Requests
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": self.period
                }
            )
            self.add_rate_limit_headers(response, rate_limit_info)
            return response
        
        except Exception as e:
            # If Redis is not available, allow the request and log the error
            print(f"Rate limiting error: {str(e)}")
            return await call_next(request)

def add_rate_limit_middleware(
    app: FastAPI,
    redis_url: Optional[str] = None,
    requests: int = 100,
    period: int = 60
) -> None:
    """
    Add rate limiting middleware to a FastAPI application.
    
    Args:
        app: FastAPI application
        redis_url: Redis URL
        requests: Maximum number of requests allowed per period
        period: Time period in seconds
    """
    rate_limiter = RateLimiter(redis_url=redis_url, requests=requests, period=period)
    app.middleware("http")(rate_limiter.__call__)
