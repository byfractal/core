"""
Input validation middleware for FastAPI applications.
Provides additional validation beyond FastAPI's built-in validation.
Protects against common injection attacks and malicious inputs.
"""

import re
import json
from typing import Dict, List, Optional, Set, Any, Callable

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

# Common attack patterns to detect
SQL_INJECTION_PATTERNS = [
    r"(\b(?:SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE)\b.*?\b(?:FROM|TABLE|DATABASE)\b)", 
    r"(?:--|#|\*\/|\/\*)(?:.*)?(?:(?:DROP|ALTER|CREATE|TRUNCATE))",
    r"(?:UNION(?:\s+ALL)?(?:\s+SELECT))",
    r"'(?:\s+OR\s+|\s+AND\s+)(?:.*?)(?:--|#|\/\*|'|=|>)",
    r"(\bOR\b\s+\d+=\d+)",
    r"(\bAND\b\s+\d+=\d+)",
]

NOSQL_INJECTION_PATTERNS = [
    r"\{\s*\$(?:ne|eq|gt|lt|gte|lte|in|nin|or|and|regex|where|exists)\s*:",
    r"\$(?:ne|eq|gt|lt|gte|lte|in|nin|or|and|regex|where|exists)",
    r"db\.(?:.*?)\.(?:find|update|insert|delete)\(",
]

XSS_PATTERNS = [
    r"<script.*?>.*?<\/script>",
    r"javascript:",
    r"on(?:click|load|mouse|error|key|focus|blur|change|submit)=",
    r"<img.*?src.*?=.*?>",
    r"<iframe.*?>.*?<\/iframe>",
    r"data:(?:text|image)\/(?:html|javascript)",
    r"<noscript>(.*?)<\/noscript>",
]

PATH_TRAVERSAL_PATTERNS = [
    r"\.{2,}[\/\\]",
    r"(?:%2e|%252e){2,}[\/\\%]",
    r"\/etc\/(?:passwd|shadow|group|hosts)",
    r"(?:proc|sys)\/\w+\/(?:cmdline|environ)",
    r"\/(?:var|usr|bin|opt)\/",
]

COMMAND_INJECTION_PATTERNS = [
    r"(?:\||&|;|`|\$\(|\$\{)",
    r"(?:\/bin\/)(?:bash|sh|ksh|csh|tcsh|zsh|dash)",
    r"(?:ping|wget|curl|nc|telnet|ncat|nmap|dig)\s+",
    r"(?:cat|head|tail|more|less|nl)\s+\/",
    r"(?:ls|cp|mv|rm|rmdir|chmod|chown)\s+",
]

class InputValidationRule:
    """Rule for validating input."""
    
    def __init__(
        self,
        patterns: List[str],
        paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
        methods: Optional[List[str]] = None,
        field_names: Optional[List[str]] = None,
        content_types: Optional[List[str]] = None,
    ):
        """
        Initialize the input validation rule.
        
        Args:
            patterns: List of regex patterns to detect
            paths: List of paths to apply the rule to (None for all paths)
            exclude_paths: List of paths to exclude from the rule
            methods: List of HTTP methods to apply the rule to (None for all methods)
            field_names: List of field names to check (None for all fields)
            content_types: List of content types to apply the rule to
        """
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
        self.paths = set(paths) if paths else None
        self.exclude_paths = set(exclude_paths) if exclude_paths else set()
        self.methods = set(methods) if methods else None
        self.field_names = set(field_names) if field_names else None
        self.content_types = set(content_types) if content_types else None
    
    def applies_to_request(self, request: Request) -> bool:
        """
        Check if the rule applies to a request.
        
        Args:
            request: The request
            
        Returns:
            True if the rule applies to the request, False otherwise
        """
        # Check if the path is excluded
        if request.url.path in self.exclude_paths:
            return False
        
        # Check if the path is included
        if self.paths is not None and request.url.path not in self.paths:
            return False
        
        # Check if the method is included
        if self.methods is not None and request.method not in self.methods:
            return False
        
        # Check if the content type is included
        if self.content_types is not None:
            content_type = request.headers.get("Content-Type", "")
            if not any(ct in content_type for ct in self.content_types):
                return False
        
        return True
    
    def validate_field(self, field_name: str, field_value: Any) -> Optional[str]:
        """
        Validate a field against the rule's patterns.
        
        Args:
            field_name: The name of the field
            field_value: The value of the field
            
        Returns:
            Validation error message or None if the field is valid
        """
        # Check if the field should be validated
        if self.field_names is not None and field_name not in self.field_names:
            return None
        
        # Convert the field value to a string
        if not isinstance(field_value, str):
            try:
                field_value = str(field_value)
            except:
                return None
        
        # Check if the field value matches any of the patterns
        for pattern in self.patterns:
            if pattern.search(field_value):
                return f"Field '{field_name}' contains a potentially malicious pattern."
        
        return None

class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for validating input in FastAPI applications.
    
    Checks request parameters, headers, and body for malicious patterns.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        rules: Optional[List[InputValidationRule]] = None,
        max_body_size: int = 1024 * 1024,  # 1MB
        max_url_length: int = 2048,
        block_on_validation_error: bool = True,
        log_func: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize the input validation middleware.
        
        Args:
            app: ASGI application
            rules: List of input validation rules
            max_body_size: Maximum allowed body size in bytes
            max_url_length: Maximum allowed URL length
            block_on_validation_error: Whether to block requests that fail validation
            log_func: Function to log validation errors
        """
        super().__init__(app)
        
        # Default rules if none provided
        self.rules = rules or self._default_rules()
        self.max_body_size = max_body_size
        self.max_url_length = max_url_length
        self.block_on_validation_error = block_on_validation_error
        self.log_func = log_func or print
    
    @staticmethod
    def _default_rules() -> List[InputValidationRule]:
        """
        Create a default set of input validation rules.
        
        Returns:
            List of default input validation rules
        """
        return [
            # SQL injection rule for all paths
            InputValidationRule(
                patterns=SQL_INJECTION_PATTERNS,
                content_types=["application/json", "application/x-www-form-urlencoded"],
            ),
            
            # NoSQL injection rule for all paths
            InputValidationRule(
                patterns=NOSQL_INJECTION_PATTERNS,
                content_types=["application/json"],
            ),
            
            # XSS rule for all paths
            InputValidationRule(
                patterns=XSS_PATTERNS,
                content_types=["application/json", "application/x-www-form-urlencoded", "text/plain"],
            ),
            
            # Path traversal rule for all paths with path parameters
            InputValidationRule(
                patterns=PATH_TRAVERSAL_PATTERNS,
            ),
            
            # Command injection rule for all paths
            InputValidationRule(
                patterns=COMMAND_INJECTION_PATTERNS,
                content_types=["application/json", "application/x-www-form-urlencoded", "text/plain"],
            ),
        ]
    
    async def validate_body(self, request: Request) -> Optional[Dict[str, str]]:
        """
        Validate the request body.
        
        Args:
            request: The request
            
        Returns:
            Dict of validation errors or None if the body is valid
        """
        content_type = request.headers.get("Content-Type", "")
        errors = {}
        
        # Check if the body should be validated
        if not content_type.startswith(("application/json", "application/x-www-form-urlencoded")):
            return None
        
        try:
            # Parse the body
            body = await request.json() if content_type.startswith("application/json") else await request.form()
            
            # Apply validation rules
            for rule in self.rules:
                if not rule.applies_to_request(request):
                    continue
                
                # Recursively check all fields in the body
                if isinstance(body, dict):
                    self._validate_dict(body, rule, errors)
                elif hasattr(body, "items"):  # For form data
                    for key, value in body.items():
                        error = rule.validate_field(key, value)
                        if error:
                            errors[key] = error
        except Exception as e:
            errors["body"] = f"Error parsing request body: {str(e)}"
        
        return errors if errors else None
    
    def _validate_dict(self, data: Dict, rule: InputValidationRule, errors: Dict[str, str], prefix: str = ""):
        """
        Recursively validate a dictionary against a rule.
        
        Args:
            data: The dictionary to validate
            rule: The validation rule
            errors: Dict to add validation errors to
            prefix: Prefix for nested field names
        """
        for key, value in data.items():
            field_name = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                self._validate_dict(value, rule, errors, field_name)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._validate_dict(item, rule, errors, f"{field_name}[{i}]")
                    else:
                        error = rule.validate_field(f"{field_name}[{i}]", item)
                        if error:
                            errors[f"{field_name}[{i}]"] = error
            else:
                error = rule.validate_field(field_name, value)
                if error:
                    errors[field_name] = error
    
    def validate_query_params(self, request: Request) -> Optional[Dict[str, str]]:
        """
        Validate the request query parameters.
        
        Args:
            request: The request
            
        Returns:
            Dict of validation errors or None if the query parameters are valid
        """
        errors = {}
        
        # Apply validation rules
        for rule in self.rules:
            if not rule.applies_to_request(request):
                continue
            
            # Check each query parameter
            for key, value in request.query_params.items():
                error = rule.validate_field(key, value)
                if error:
                    errors[key] = error
        
        return errors if errors else None
    
    def validate_headers(self, request: Request) -> Optional[Dict[str, str]]:
        """
        Validate the request headers.
        
        Args:
            request: The request
            
        Returns:
            Dict of validation errors or None if the headers are valid
        """
        errors = {}
        
        # Skip validating standard headers
        skip_headers = {"content-type", "content-length", "accept", "user-agent", "accept-encoding"}
        
        # Apply validation rules
        for rule in self.rules:
            if not rule.applies_to_request(request):
                continue
            
            # Check each header
            for key, value in request.headers.items():
                if key.lower() in skip_headers:
                    continue
                
                error = rule.validate_field(key, value)
                if error:
                    errors[key] = error
        
        return errors if errors else None
    
    def validate_url_length(self, request: Request) -> Optional[str]:
        """
        Validate the URL length.
        
        Args:
            request: The request
            
        Returns:
            Error message if the URL is too long, None otherwise
        """
        url_length = len(str(request.url))
        if url_length > self.max_url_length:
            return f"URL length ({url_length}) exceeds maximum allowed length ({self.max_url_length})."
        
        return None
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process the request and validate inputs.
        
        Args:
            request: Incoming request
            call_next: Next middleware or endpoint
            
        Returns:
            Response from the next middleware or endpoint
        """
        # Validate URL length
        url_error = self.validate_url_length(request)
        if url_error:
            self.log_func(f"Validation error (URL): {url_error}")
            if self.block_on_validation_error:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid request URL."},
                )
        
        # Validate query parameters
        query_errors = self.validate_query_params(request)
        if query_errors:
            self.log_func(f"Validation errors (query): {json.dumps(query_errors)}")
            if self.block_on_validation_error:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid query parameters.", "errors": query_errors},
                )
        
        # Validate headers
        header_errors = self.validate_headers(request)
        if header_errors:
            self.log_func(f"Validation errors (headers): {json.dumps(header_errors)}")
            if self.block_on_validation_error:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid request headers.", "errors": header_errors},
                )
        
        # Validate body
        body_size = request.headers.get("Content-Length", "0")
        if body_size and int(body_size) > self.max_body_size:
            self.log_func(f"Validation error (body size): exceeds {self.max_body_size} bytes")
            if self.block_on_validation_error:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "Request body too large."},
                )
        
        body_errors = await self.validate_body(request)
        if body_errors:
            self.log_func(f"Validation errors (body): {json.dumps(body_errors)}")
            if self.block_on_validation_error:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Invalid request body.", "errors": body_errors},
                )
        
        # Process the request
        return await call_next(request)

def add_input_validation_middleware(
    app: FastAPI,
    rules: Optional[List[InputValidationRule]] = None,
    max_body_size: int = 1024 * 1024,
    max_url_length: int = 2048,
    block_on_validation_error: bool = True,
    log_func: Optional[Callable[[str], None]] = None,
) -> None:
    """
    Add input validation middleware to a FastAPI application.
    
    Args:
        app: FastAPI application
        rules: List of input validation rules
        max_body_size: Maximum allowed body size in bytes
        max_url_length: Maximum allowed URL length
        block_on_validation_error: Whether to block requests that fail validation
        log_func: Function to log validation errors
    """
    app.add_middleware(
        InputValidationMiddleware,
        rules=rules,
        max_body_size=max_body_size,
        max_url_length=max_url_length,
        block_on_validation_error=block_on_validation_error,
        log_func=log_func,
    )
