"""
Functions to build queries for the Amplitude API.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
import re
import bleach
from urllib.parse import quote_plus

def sanitize_string(value: str) -> str:
    """
    Sanitize a string input to prevent injection attacks.
    
    Args:
        value: The string to sanitize
        
    Returns:
        The sanitized and URL-encoded string
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")
    
    # Clean the string using bleach to remove any HTML/scripts
    cleaned = bleach.clean(value, tags=[], strip=True)
    # URL encode the cleaned string
    return quote_plus(cleaned)

def validate_date_range(start_date: datetime, end_date: datetime) -> None:
    """
    Validate that the date range is valid for Amplitude queries.
    
    Args:
        start_date: The start date
        end_date: The end date
        
    Raises:
        ValueError: If the date range is invalid
    """
    if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
        raise ValueError("Dates must be datetime objects")
        
    if start_date >= end_date:
        raise ValueError("Start date must be before end date")
        
    date_range = end_date - start_date
    if date_range > timedelta(days=365):
        raise ValueError("Date range cannot exceed 1 year")

def validate_event_type(event_type: str) -> None:
    """
    Validate that an event type meets Amplitude's requirements.
    
    Args:
        event_type: The event type to validate
        
    Raises:
        ValueError: If the event type is invalid
    """
    if not event_type:
        raise ValueError("Event type cannot be empty")
        
    if not re.match(r'^[\w\- ]{1,40}$', event_type):
        raise ValueError(
            "Event type can only contain letters, numbers, underscores, hyphens and spaces, "
            "and must be 40 characters or less"
        )

def build_query(
    start_date: datetime,
    end_date: datetime,
    event_type: Optional[str] = None,
    user_id: Optional[str] = None,
    properties: Optional[Dict[str, str]] = None
) -> Dict[str, Union[str, Dict]]:
    """
    Build a query for the Amplitude Analytics API with input validation.
    
    Args:
        start_date: Query start date
        end_date: Query end date
        event_type: Optional event type to filter by
        user_id: Optional user ID to filter by
        properties: Optional properties to filter by
        
    Returns:
        A dictionary containing the validated and sanitized query parameters
    """
    validate_date_range(start_date, end_date)
    
    query = {
        "start": start_date.strftime("%Y-%m-%d"),
        "end": end_date.strftime("%Y-%m-%d")
    }
    
    if event_type:
        validate_event_type(event_type)
        query["event_type"] = sanitize_string(event_type)
        
    if user_id:
        query["user_id"] = sanitize_string(user_id)
        
    if properties:
        sanitized_props = {}
        for key, value in properties.items():
            sanitized_key = sanitize_string(key)
            sanitized_value = sanitize_string(str(value))
            sanitized_props[sanitized_key] = sanitized_value
        query["properties"] = sanitized_props
        
    return query

def build_export_query(
    start_date: datetime,
    end_date: datetime,
    event_types: Optional[List[str]] = None
) -> Dict[str, Union[str, List[str]]]:
    """
    Build a query for the Amplitude Export API with input validation.
    
    Args:
        start_date: Export start date
        end_date: Export end date
        event_types: Optional list of event types to filter by
        
    Returns:
        A dictionary containing the validated and sanitized query parameters
    """
    validate_date_range(start_date, end_date)
    
    query = {
        "start_time": start_date.strftime("%Y-%m-%d"),
        "end_time": end_date.strftime("%Y-%m-%d")
    }
    
    if event_types:
        sanitized_types = []
        for event_type in event_types:
            validate_event_type(event_type)
            sanitized_types.append(sanitize_string(event_type))
        query["event_types"] = sanitized_types
        
    return query

def build_event_payload(
    event_type: str,
    user_id: str,
    device_id: Optional[str] = None,
    user_properties: Optional[Dict[str, str]] = None,
    event_properties: Optional[Dict[str, str]] = None
) -> Dict[str, Union[str, Dict]]:
    """
    Build an event payload for the Amplitude Ingestion API with input validation.
    
    Args:
        event_type: The type of event
        user_id: The user's ID
        device_id: Optional device ID
        user_properties: Optional user properties
        event_properties: Optional event properties
        
    Returns:
        A dictionary containing the validated and sanitized event payload
    """
    validate_event_type(event_type)
    
    event = {
        "event_type": sanitize_string(event_type),
        "user_id": sanitize_string(user_id),
        "time": int(datetime.now().timestamp() * 1000)
    }
    
    if device_id:
        event["device_id"] = sanitize_string(device_id)
        
    if user_properties:
        sanitized_user_props = {}
        for key, value in user_properties.items():
            sanitized_key = sanitize_string(key)
            sanitized_value = sanitize_string(str(value))
            sanitized_user_props[sanitized_key] = sanitized_value
        event["user_properties"] = sanitized_user_props
        
    if event_properties:
        sanitized_event_props = {}
        for key, value in event_properties.items():
            sanitized_key = sanitize_string(key)
            sanitized_value = sanitize_string(str(value))
            sanitized_event_props[sanitized_key] = sanitized_value
        event["event_properties"] = sanitized_event_props
        
    return event