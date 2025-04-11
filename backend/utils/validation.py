"""
Input validation and sanitization utilities.
Provides functions to validate and sanitize various types of input data.
"""

import re
import html
import uuid
import unicodedata
from datetime import datetime
from typing import Any, Dict, List, Optional, Pattern, Set, Tuple, Union, TypeVar, Callable

# Type variable for generic functions
T = TypeVar('T')

# Common validation patterns
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")
URL_PATTERN = re.compile(r"^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$")
UUID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
DATE_ISO_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?$")
ALPHA_PATTERN = re.compile(r"^[a-zA-Z]+$")
ALPHANUMERIC_PATTERN = re.compile(r"^[a-zA-Z0-9]+$")
PHONE_PATTERN = re.compile(r"^\+?[0-9]{8,15}$")

# HTML Tag whitelist for sanitization
ALLOWED_HTML_TAGS = {
    "a", "b", "blockquote", "br", "code", "em", "h1", "h2", "h3", 
    "h4", "h5", "h6", "hr", "i", "li", "ol", "p", "pre", "s", 
    "span", "strong", "table", "tbody", "td", "th", "thead", "tr", "ul"
}
ALLOWED_HTML_ATTRS = {
    "a": {"href", "title", "target", "rel"},
    "img": {"src", "alt", "title", "width", "height"},
    "table": {"border", "cellpadding", "cellspacing"},
    "td": {"colspan", "rowspan", "align"},
    "th": {"colspan", "rowspan", "align"},
    "span": {"class", "style"},
    "pre": {"class"},
    "code": {"class"},
}

def is_valid_email(email: str) -> bool:
    """
    Validate an email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if the email is valid, False otherwise
    """
    if not email or len(email) > 320:  # RFC 3696
        return False
    
    return bool(EMAIL_PATTERN.match(email))

def is_strong_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a password against strong password requirements.
    
    Requires at least:
    - 8 characters
    - 1 uppercase letter
    - 1 lowercase letter
    - 1 digit
    - 1 special character
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[@$!%*?&]', password):
        return False, "Password must contain at least one special character (@$!%*?&)"
    
    return True, None

def is_valid_url(url: str) -> bool:
    """
    Validate a URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if the URL is valid, False otherwise
    """
    if not url or len(url) > 2048:  # Common browser limit
        return False
    
    return bool(URL_PATTERN.match(url))

def is_valid_uuid(uuid_str: str) -> bool:
    """
    Validate a UUID string.
    
    Args:
        uuid_str: UUID string to validate
        
    Returns:
        True if the UUID is valid, False otherwise
    """
    if not uuid_str:
        return False
    
    return bool(UUID_PATTERN.match(uuid_str.lower()))

def is_valid_date(date_str: str) -> bool:
    """
    Validate an ISO 8601 date string.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if the date is valid, False otherwise
    """
    if not date_str:
        return False
    
    # Check format with regex
    if not DATE_ISO_PATTERN.match(date_str):
        return False
    
    # Validate the date with datetime
    try:
        if "T" in date_str:
            datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            datetime.fromisoformat(date_str)
        return True
    except ValueError:
        return False

def is_within_length(text: str, min_length: int, max_length: int) -> bool:
    """
    Validate that a string is within a length range.
    
    Args:
        text: String to validate
        min_length: Minimum length
        max_length: Maximum length
        
    Returns:
        True if the string is within the length range, False otherwise
    """
    if text is None:
        return False
    
    length = len(text)
    return min_length <= length <= max_length

def is_numeric(value: str) -> bool:
    """
    Validate that a string contains only digits.
    
    Args:
        value: String to validate
        
    Returns:
        True if the string contains only digits, False otherwise
    """
    if not value:
        return False
    
    return value.isdigit()

def is_alpha(value: str) -> bool:
    """
    Validate that a string contains only alphabetic characters.
    
    Args:
        value: String to validate
        
    Returns:
        True if the string contains only alphabetic characters, False otherwise
    """
    if not value:
        return False
    
    return bool(ALPHA_PATTERN.match(value))

def is_alphanumeric(value: str) -> bool:
    """
    Validate that a string contains only alphanumeric characters.
    
    Args:
        value: String to validate
        
    Returns:
        True if the string contains only alphanumeric characters, False otherwise
    """
    if not value:
        return False
    
    return bool(ALPHANUMERIC_PATTERN.match(value))

def is_valid_phone(phone: str) -> bool:
    """
    Validate a phone number.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if the phone number is valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove common formatting characters
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    return bool(PHONE_PATTERN.match(phone))

def sanitize_html(html_content: str, allowed_tags: Optional[Set[str]] = None, 
                 allowed_attrs: Optional[Dict[str, Set[str]]] = None) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    This is a basic implementation. For production use, consider using a library
    like bleach.
    
    Args:
        html_content: HTML content to sanitize
        allowed_tags: Set of allowed HTML tags
        allowed_attrs: Dict of allowed attributes for each tag
        
    Returns:
        Sanitized HTML content
    """
    if not html_content:
        return ""
    
    allowed_tags = allowed_tags or ALLOWED_HTML_TAGS
    allowed_attrs = allowed_attrs or ALLOWED_HTML_ATTRS
    
    # First, escape all HTML
    escaped = html.escape(html_content)
    
    # Then, selectively unescape allowed tags
    # This is a simplified approach; a production implementation would use a proper HTML parser
    for tag in allowed_tags:
        # Replace escaped opening tags
        escaped = re.sub(
            r'&lt;' + tag + r'(\s+[^&>]*)??&gt;',
            r'<' + tag + r'\1>',
            escaped
        )
        
        # Replace escaped closing tags
        escaped = re.sub(
            r'&lt;/' + tag + r'&gt;',
            r'</' + tag + r'>',
            escaped
        )
    
    # This is a very basic implementation; a production version would need more robust parsing
    return escaped

def normalize_string(text: str, form: str = "NFKC") -> str:
    """
    Normalize a Unicode string.
    
    Args:
        text: String to normalize
        form: Normalization form (NFC, NFD, NFKC, NFKD)
        
    Returns:
        Normalized string
    """
    if not text:
        return ""
    
    return unicodedata.normalize(form, text)

def validate_and_normalize(
    value: Optional[T],
    validators: List[Callable[[T], bool]],
    normalizer: Optional[Callable[[T], T]] = None,
    default: Optional[T] = None
) -> Tuple[Optional[T], bool]:
    """
    Validate and normalize a value.
    
    Args:
        value: Value to validate and normalize
        validators: List of validation functions
        normalizer: Normalization function
        default: Default value to return if validation fails
        
    Returns:
        Tuple of (normalized_value, is_valid)
    """
    if value is None:
        return default, default is not None
    
    # Normalize the value if a normalizer is provided
    normalized = normalizer(value) if normalizer else value
    
    # Run all validators
    is_valid = all(validator(normalized) for validator in validators)
    
    return normalized if is_valid else default, is_valid

def strip_non_printable_chars(text: str) -> str:
    """
    Strip non-printable characters from a string.
    
    Args:
        text: String to process
        
    Returns:
        String with non-printable characters removed
    """
    if not text:
        return ""
    
    # Remove control characters, keep whitespace
    return "".join(c for c in text if unicodedata.category(c)[0] != "C" or c.isspace())

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal and command injection.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return ""
    
    # Remove directory traversal sequences and path separators
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    sanitized = re.sub(r'\.{2,}', '.', sanitized)
    
    # Ensure the filename doesn't start with a dot or dash
    if sanitized.startswith((".", "-")):
        sanitized = f"_" + sanitized[1:]
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255 - len(ext)] + ext
    
    return sanitized

def sanitize_sql_identifier(identifier: str) -> str:
    """
    Sanitize an SQL identifier (table name, column name, etc).
    
    Args:
        identifier: SQL identifier to sanitize
        
    Returns:
        Sanitized SQL identifier
    """
    if not identifier:
        return ""
    
    # Allow only alphanumeric and underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', identifier)
    
    # Ensure it starts with a letter or underscore
    if sanitized and not (sanitized[0].isalpha() or sanitized[0] == '_'):
        sanitized = f"_{sanitized}"
    
    return sanitized

def generate_secure_random_string(length: int = 32) -> str:
    """
    Generate a secure random string.
    
    Args:
        length: Length of the string
        
    Returns:
        Secure random string
    """
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_secure_password(length: int = 16) -> str:
    """
    Generate a secure random password that meets strong password requirements.
    
    Args:
        length: Length of the password
        
    Returns:
        Secure random password
    """
    import secrets
    import string
    
    if length < 8:
        length = 8
    
    # Ensure including at least one of each required character type
    all_chars = string.ascii_letters + string.digits + "@$!%*?&"
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("@$!%*?&"),
    ]
    
    # Add random characters to fill up to the desired length
    password.extend(secrets.choice(all_chars) for _ in range(length - 4))
    
    # Shuffle the password
    result = list(password)
    secrets.SystemRandom().shuffle(result)
    
    return ''.join(result)
