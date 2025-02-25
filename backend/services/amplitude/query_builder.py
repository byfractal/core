"""
Build queries for Amplitude API.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

def build_query(start_date: Optional[datetime] = None, 
                end_date: Optional[datetime] = None,
                event_type: Optional[str] = None,
                user_id: Optional[str] = None,
                page: Optional[str] = None,
                limit: int = 100) -> Dict[str, Any]:
    """
    Build a query for Amplitude API.
    
    Args:
        start_date: Start date
        end_date: End date
        event_type: Type of event to filter by
        user_id: User ID to filter by
        page: Page to filter by
        limit: Maximum number of results to return
        
    Returns:
        Query dictionary
    """
    # Dates par défaut si non spécifiées
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    # Formater les dates au format attendu par Amplitude
    start_str = start_date.strftime("%Y%m%dT%H")
    end_str = end_date.strftime("%Y%m%dT%H")
    
    # Construire la requête de base
    query = {
        "start": start_str,
        "end": end_str,
    }
    
    # Ajouter des filtres optionnels
    if event_type:
        query["event_type"] = event_type
    
    if user_id:
        query["user_id"] = user_id
    
    if page:
        query.setdefault("event_properties", {})["page"] = page
    
    # Ajouter la limite
    query["limit"] = limit
    
    return query

def build_export_query(start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> Dict[str, str]:
    """
    Build a query for Amplitude Export API.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Query params dictionary
    """
    # Dates par défaut si non spécifiées
    if not start_date:
        start_date = datetime.now() - timedelta(days=30)
    if not end_date:
        end_date = datetime.now()
    
    # Formater les dates au format attendu par l'API Export
    start_str = start_date.strftime("%Y%m%dT%H")
    end_str = end_date.strftime("%Y%m%dT%H")
    
    return {
        "start": start_str,
        "end": end_str
    }

def build_event_payload(user_id: str, 
                      device_id: str, 
                      event_type: str, 
                      event_properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build an event payload for Amplitude HTTP API.
    
    Args:
        user_id: User ID
        device_id: Device ID
        event_type: Type of event
        event_properties: Event properties
        
    Returns:
        Event payload dictionary
    """
    # Timestamp actuel en millisecondes
    timestamp = int(datetime.now().timestamp() * 1000)
    
    return {
        "api_key": None,  # Sera ajouté par le client
        "events": [
            {
                "user_id": user_id,
                "device_id": device_id,
                "event_type": event_type,
                "time": timestamp,
                "event_properties": event_properties
            }
        ]
    }