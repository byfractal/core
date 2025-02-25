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

# Charger les variables d'environnement
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
        self.api_key = api_key or os.getenv("API_KEY")
        self.secret_key = secret_key or os.getenv("SECRET_KEY")
        
        if not self.api_key:
            raise ValueError("Amplitude API key is required")
            
        # URLs from environment or defaults
        self.export_url = os.getenv("EXPORT_URL", "https://amplitude.com/api/2/export")
        self.http_api_url = os.getenv("AMPLITUDE_URL", "https://api.amplitude.com/2/httpapi")
    
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
        # Si les dates ne sont pas fournies, utiliser les 30 derniers jours
        if start_date is None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        
        if not self.secret_key:
            raise ValueError("La clé secrète est requise pour l'export de données")
        
        # Créer le header d'authentification Basic
        credentials = f"{self.api_key}:{self.secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        }
        
        # Formater les dates au format ISO 8601
        # Utilisez les formats corrects pour Amplitude EU
        start_str = start_date.strftime("%Y%m%dT%H")
        end_str = end_date.strftime("%Y%m%dT%H")
        
        # Essayez l'URL standard d'abord
        url = f"{self.export_url}?start={start_str}&end={end_str}"
        
        logger = logging.getLogger(__name__)
        logger.info(f"Calling Amplitude Export API: {url}")
        
        try:
            # Faire la requête
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except requests.exceptions.HTTPError as e:
            # Si nous obtenons une 404, essayons avec un format différent d'URL
            if e.response.status_code == 404:
                # Essayez un format d'URL alternatif pour Amplitude EU
                alt_url = f"https://analytics.eu.amplitude.com/api/2/events/export?start={start_str}&end={end_str}"
                logger.info(f"Retrying with alternative URL: {alt_url}")
                alt_response = requests.get(alt_url, headers=headers)
                alt_response.raise_for_status()
                return alt_response.content
            raise Exception(f"Erreur lors de la récupération des données: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur lors de la récupération des données: {str(e)}")
    
    def send_event(self, events: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send event to Amplitude.
        
        Args:
            events: Event data to send
            
        Returns:
            Response from Amplitude API
        """
        if not self.api_key:
            raise ValueError("La clé API n'est pas configurée")

        # Préparation de la requête
        headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': self.api_key
        }

        # Envoi des événements
        response = requests.post(
            self.http_api_url,
            headers=headers,
            json=events
        )
        response.raise_for_status()
        
        return response.json()
    
    def fetch_data_for_period(self, days: int = 30) -> Tuple[bytes, str]:
        """
        Récupère les données pour une période donnée.
        
        Args:
            days: Nombre de jours à récupérer
            
        Returns:
            Tuple contenant (data, filename)
        """
        # Calcul des dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Récupération des données
        data = self.get_data(start_date, end_date)
        
        # Génération du nom de fichier avec la date
        filename = f"amplitude_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gz"
        
        return data, filename
