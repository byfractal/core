"""
Client API for communicating with Amplitude.
Handles authentication, requests and response parsing.
"""
import os
import base64
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, Tuple
from dotenv import load_dotenv
import logging
from cryptography.fernet import Fernet
from pathlib import Path

# Load environment variables
load_dotenv()

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
    
    def get_data(self, start_date: Optional[datetime] = None, 
                  end_date: Optional[datetime] = None) -> bytes:
        """
        Get data from Amplitude API for the specified date range.
        
        Args:
            start_date: Start date (defaults to today - 30 days)
            end_date: End date (defaults to today)
            
        Returns:
            Amplitude data as bytes
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
        
        # Create Basic auth header
        credentials = f"{decrypted_api_key}:{decrypted_secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }
        
        # Format dates in ISO 8601 format for Amplitude EU
        start_str = start_date.strftime("%Y%m%dT%H")
        end_str = end_date.strftime("%Y%m%dT%H")
        
        # Try standard URL first
        url = f"{self.export_url}?start={start_str}&end={end_str}"
        
        logger = logging.getLogger(__name__)
        logger.info(f"Calling Amplitude Export API: {url}")
        
        try:
            # Make request
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.HTTPError as e:
            # If 404, try alternative URL format
            if e.response.status_code == 404:
                alt_url = f"https://analytics.eu.amplitude.com/api/2/events/export?start={start_str}&end={end_str}"
                logger.info(f"Retrying with alternative URL: {alt_url}")
                alt_response = requests.get(alt_url, headers=headers)
                alt_response.raise_for_status()
                return alt_response.content
            raise Exception(f"Error fetching data: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching data: {str(e)}")
    
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
