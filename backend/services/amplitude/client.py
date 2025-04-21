"""
Client API for communicating with Amplitude.
Handles authentication, requests and response parsing.
"""
import os
import base64
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, Tuple, List
from dotenv import load_dotenv
import logging
from cryptography.fernet import Fernet
from pathlib import Path
import json
import gzip
import zipfile
import io
from io import BytesIO
from zipfile import ZipFile

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AmplitudeError(Exception):
    """Custom exception for Amplitude API errors"""
    pass

class AmplitudeClient:
    """Client for interacting with Amplitude API"""
    
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        """
        Initialize the Amplitude client.
        
        Args:
            api_key: Amplitude API key (defaults to env variable)
            secret_key: Amplitude Secret key (defaults to env variable)
        """
        # Use more specific environment variable names
        self.api_key = api_key or os.getenv("AMPLITUDE_API_KEY")
        self.secret_key = secret_key or os.getenv("AMPLITUDE_SECRET_KEY")
        
        if not self.api_key:
            raise ValueError("Amplitude API key is required")
            
        # URLs from environment or defaults
        self.export_url = os.getenv("AMPLITUDE_EXPORT_URL", "https://analytics.eu.amplitude.com/api/2/export")
        self.http_api_url = os.getenv("AMPLITUDE_HTTP_API_URL", "https://api.eu.amplitude.com/2/httpapi")
        self.session_replay_url = os.getenv("AMPLITUDE_SESSION_REPLAY_URL", "https://api.eu.amplitude.com/replay/v1")
        
        # Initialize encryption
        self._init_encryption()
        
        # Encrypt sensitive keys
        if self.api_key:
            self.api_key = self._encrypt_value(self.api_key)
        if self.secret_key:
            self.secret_key = self._encrypt_value(self.secret_key)
    
    def _init_encryption(self):
        """Initialize encryption key and Fernet instance"""
        key_file = Path(".amplitude_key")
        if key_file.exists():
            self.encryption_key = key_file.read_bytes()
        else:
            self.encryption_key = Fernet.generate_key()
            key_file.write_bytes(self.encryption_key)
            key_file.chmod(0o600)  # Restrict file permissions
            
        self.fernet = Fernet(self.encryption_key)
    
    def _encrypt_value(self, value: str) -> bytes:
        """Encrypt a value using Fernet"""
        return self.fernet.encrypt(value.encode())
    
    def _decrypt_value(self, encrypted_value: bytes) -> str:
        """Decrypt a value using Fernet"""
        return self.fernet.decrypt(encrypted_value).decode()
    
    def rotate_keys(self):
        """Rotate encryption keys and re-encrypt sensitive data"""
        # Generate new encryption key
        new_key = Fernet.generate_key()
        new_fernet = Fernet(new_key)
        
        # Re-encrypt sensitive data with new key
        if self.api_key:
            decrypted_api_key = self._decrypt_value(self.api_key)
            self.api_key = new_fernet.encrypt(decrypted_api_key.encode())
        
        if self.secret_key:
            decrypted_secret_key = self._decrypt_value(self.secret_key)
            self.secret_key = new_fernet.encrypt(decrypted_secret_key.encode())
        
        # Save new key
        key_file = Path(".amplitude_key")
        key_file.write_bytes(new_key)
        key_file.chmod(0o600)
        
        # Update Fernet instance
        self.encryption_key = new_key
        self.fernet = new_fernet
    
    def _read_compressed_response(self, response: bytes) -> List[Dict[str, Any]]:
        """
        Read a compressed response from Amplitude API.
        The response can be:
        - A ZIP file containing GZIP compressed JSON files
        - A GZIP compressed JSON file
        - A plain text JSON file
        
        Returns:
            List of event dictionaries
        """
        events = []
        
        # First try to read as ZIP
        try:
            with BytesIO(response) as bio:
                with ZipFile(bio) as zip_file:
                    for filename in zip_file.namelist():
                        logging.info(f"Successfully read ZIP file: {filename}")
                        # Read the content of each file in the ZIP
                        with zip_file.open(filename) as f:
                            file_content = f.read()
                            # Try to decompress as GZIP (files in ZIP are usually GZIP compressed)
                            try:
                                with gzip.GzipFile(fileobj=BytesIO(file_content)) as gz:
                                    content = gz.read().decode('utf-8')
                            except Exception as e:
                                logging.warning(f"Failed to decompress {filename} as GZIP: {str(e)}")
                                # If GZIP fails, try to read as plain text
                                try:
                                    content = file_content.decode('utf-8')
                                except UnicodeDecodeError as ue:
                                    logging.error(f"Failed to decode {filename} content: {str(ue)}")
                                    continue
                            
                            # Parse JSON lines
                            for line in content.splitlines():
                                if line.strip():  # Skip empty lines
                                    try:
                                        event = json.loads(line)
                                        events.append(event)
                                    except json.JSONDecodeError as je:
                                        logging.warning(f"Failed to parse JSON line: {str(je)}")
                    return events
        except Exception as e:
            logging.warning(f"Failed to read as ZIP: {str(e)}")
        
        # If ZIP fails, try GZIP
        try:
            with gzip.GzipFile(fileobj=BytesIO(response)) as gz:
                content = gz.read().decode('utf-8')
                for line in content.splitlines():
                    if line.strip():
                        try:
                            event = json.loads(line)
                            events.append(event)
                        except json.JSONDecodeError as je:
                            logging.warning(f"Failed to parse JSON line: {str(je)}")
                return events
        except Exception as e:
            logging.warning(f"Failed to read as GZIP: {str(e)}")
        
        # If both ZIP and GZIP fail, try plain text
        try:
            content = response.decode('utf-8')
            for line in content.splitlines():
                if line.strip():
                    try:
                        event = json.loads(line)
                        events.append(event)
                    except json.JSONDecodeError as je:
                        logging.warning(f"Failed to parse JSON line: {str(je)}")
            return events
        except UnicodeDecodeError as e:
            logging.error(f"Failed to decode content as UTF-8: {str(e)}")
            raise
        
        return events
    
    def get_data(self, start_date: Optional[datetime] = None, 
                  end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get data from Amplitude API for the specified date range.
        
        Args:
            start_date: Start date (defaults to today - 30 days)
            end_date: End date (defaults to today)
            
        Returns:
            List of event dictionaries
        """
        # If dates not provided, use last 30 days
        if start_date is None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        
        if not self.secret_key:
            raise ValueError("Secret key is required for data export")
        
        # Decrypt keys for use
        decrypted_api_key = self._decrypt_value(self.api_key)
        decrypted_secret_key = self._decrypt_value(self.secret_key)
        
        # Verify we have valid keys (without logging them)
        if not decrypted_api_key or len(decrypted_api_key) < 5:
            raise AmplitudeError("Invalid API key format")
        if not decrypted_secret_key or len(decrypted_secret_key) < 5:
            raise AmplitudeError("Invalid Secret key format")
            
        logger.info("API keys validated")
        
        # Create Basic auth header
        credentials = f"{decrypted_api_key}:{decrypted_secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
            'Accept': '*/*'  # Accept any content type
        }
        
        # Format dates in YYYYMMDD format
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        # Try standard URL first
        url = f"{self.export_url}?start={start_str}&end={end_str}"
        
        logger.info(f"Fetching events from {start_str} to {end_str}")
        logger.info(f"Using URL: {url}")
        
        try:
            # Make request
            response = requests.get(url, headers=headers)
            
            if response.status_code == 403:
                logger.error("Authentication failed - please verify API keys")
                raise AmplitudeError("Authentication failed")
                
            response.raise_for_status()
            
            # Parse response
            events = self._read_compressed_response(response.content)
            logger.info(f"Successfully fetched {len(events)} events")
            return events
            
        except requests.exceptions.HTTPError as e:
            # If 404, try alternative URL format
            if e.response.status_code == 404:
                alt_url = f"https://analytics.eu.amplitude.com/api/2/events/export?start={start_str}&end={end_str}"
                logger.info(f"Retrying with alternative URL: {alt_url}")
                
                alt_response = requests.get(alt_url, headers=headers)
                alt_response.raise_for_status()
                
                # Parse alternative response
                events = self._read_compressed_response(alt_response.content)
                logger.info(f"Successfully fetched {len(events)} events from alternative URL")
                return events
                
            raise AmplitudeError(f"Error fetching data: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise AmplitudeError(f"Error fetching data: {str(e)}")
    
    def send_event(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send event to Amplitude.
        
        Args:
            events: Event data to send
            
        Returns:
            Response from Amplitude API
        """
        if not self.api_key:
            raise ValueError("API key not configured")

        # Decrypt API key
        decrypted_api_key = self._decrypt_value(self.api_key)

        # Prepare request
        headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': decrypted_api_key
        }

        # Send events
        response = requests.post(
            self.http_api_url,
            headers=headers,
            json=events
        )
        response.raise_for_status()
        
        return response.json()
    
    def fetch_data_for_period(self, days: int = 30) -> Tuple[bytes, str]:
        """
        Fetch data for a given period.
        
        Args:
            days: Number of days to fetch
            
        Returns:
            Tuple containing (data, filename)
        """
        # Calculate dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Fetch data
        data = self.get_data(start_date, end_date)
        
        # Generate filename with date
        filename = f"amplitude_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gz"
        
        return data, filename

    def _validate_api_keys(self) -> Tuple[str, str]:
        """Validate and decrypt API keys"""
        if not self.api_key:
            raise ValueError("API key is required")
        if not self.secret_key:
            raise ValueError("Secret key is required")
            
        try:
            api_key = self._decrypt_value(self.api_key)
            secret_key = self._decrypt_value(self.secret_key)
            return api_key, secret_key
        except Exception as e:
            raise ValueError(f"Failed to decrypt API keys: {str(e)}")

    def get_session_replay(self, session_id: str) -> Dict[str, Any]:
        """
        Get session replay data for a specific session.
        
        Args:
            session_id: Session ID to fetch replay data for
            
        Returns:
            Dictionary containing session replay data
        """
        if not session_id:
            raise ValueError("Session ID is required")
            
        try:
            api_key, secret_key = self._validate_api_keys()
            
            # Construct URL with session ID
            url = f"{self.session_replay_url}/sessions/{session_id}"
            
            # Use basic auth with API key and secret key
            auth = base64.b64encode(f"{api_key}:{secret_key}".encode()).decode()
            headers = {
                "Authorization": f"Basic {auth}",
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch session replay: {str(e)}")
            raise ValueError(f"Failed to fetch session replay: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error fetching session replay: {str(e)}")
            raise ValueError(f"Error fetching session replay: {str(e)}")

def fetch_amplitude_data(start_date: str, end_date: str) -> List[Dict[Any, Any]]:
    """
    Fetch real user events from Amplitude between two dates.
    
    Args:
        start_date: Start date in format YYYYMMDDT00
        end_date: End date in format YYYYMMDDT00
        
    Returns:
        List of event dictionaries
        
    Raises:
        AmplitudeError: If API call fails
    """
    api_key = os.getenv("AMPLITUDE_API_KEY")
    secret_key = os.getenv("AMPLITUDE_SECRET_KEY")
    
    if not api_key or not secret_key:
        raise AmplitudeError("Missing Amplitude credentials in .env")
        
    # Create Basic Auth header
    credentials = f"{api_key}:{secret_key}"
    auth_header = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Accept": "application/json"
    }
    
    url = f"https://analytics.amplitude.com/api/2/export"
    params = {
        "start": start_date,
        "end": end_date
    }
    
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30,  # 30 seconds timeout
            stream=True  # Stream response for large datasets
        )
        
        response.raise_for_status()
        
        # Parse NDJSON response (each line is a JSON object)
        events = []
        for line in response.iter_lines():
            if line:  # Skip empty lines
                event = response.json()
                events.append(event)
                
        logger.info(f"Successfully fetched {len(events)} events from Amplitude")
        return events
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to fetch data from Amplitude: {str(e)}"
        logger.error(error_msg)
        raise AmplitudeError(error_msg) from e
