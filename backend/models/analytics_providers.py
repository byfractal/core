"""
Ce module définit l'architecture pour l'intégration de différentes plateformes d'analytics.
Il fournit une interface commune pour récupérer des données utilisateur depuis
PostHog, Mixpanel, Amplitude et d'autres services similaires.
"""

import os
import sys
import json
import abc
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Add root directory to Python path
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

class AnalyticsProvider(abc.ABC):
    """
    Classe abstraite définissant l'interface pour tous les fournisseurs d'analytics.
    Chaque plateforme d'analytics (PostHog, Mixpanel, etc.) doit implémenter cette interface.
    """
    
    @abc.abstractmethod
    def get_sessions(self, page_id: str, date_from: Optional[str] = None, 
                    date_to: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les sessions utilisateur pour une page spécifique.
        
        Args:
            page_id: Identifiant de la page
            date_from: Date de début (format ISO)
            date_to: Date de fin (format ISO)
            limit: Nombre maximum de sessions à récupérer
            
        Returns:
            Liste des sessions avec leurs données associées
        """
        pass
    
    @abc.abstractmethod
    def get_events(self, event_name: str, page_id: Optional[str] = None, 
                  date_from: Optional[str] = None, date_to: Optional[str] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les événements d'un type spécifique.
        
        Args:
            event_name: Nom de l'événement à récupérer
            page_id: Filtrer par page spécifique (optionnel)
            date_from: Date de début (format ISO)
            date_to: Date de fin (format ISO)
            limit: Nombre maximum d'événements à récupérer
            
        Returns:
            Liste des événements avec leurs propriétés
        """
        pass
    
    @abc.abstractmethod
    def get_user_feedback(self, page_id: Optional[str] = None,
                         date_from: Optional[str] = None, 
                         date_to: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les feedbacks utilisateur.
        
        Args:
            page_id: Filtrer par page spécifique (optionnel)
            date_from: Date de début (format ISO)
            date_to: Date de fin (format ISO)
            
        Returns:
            Liste des feedbacks avec leurs propriétés
        """
        pass
    
    @abc.abstractmethod
    def get_session_recordings(self, session_id: str) -> Dict[str, Any]:
        """
        Récupère les enregistrements d'une session spécifique.
        
        Args:
            session_id: Identifiant de la session
            
        Returns:
            Données détaillées de la session
        """
        pass
    
    @staticmethod
    def get_date_range(days: int) -> tuple:
        """
        Calcule une plage de dates à partir d'aujourd'hui.
        
        Args:
            days: Nombre de jours à remonter dans le passé
            
        Returns:
            Tuple de dates (date_from, date_to) au format ISO
        """
        date_to = datetime.now().isoformat()
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        return date_from, date_to


class PostHogProvider(AnalyticsProvider):
    """
    Implémentation de l'interface AnalyticsProvider pour PostHog.
    """
    
    def __init__(self):
        """
        Initialise le provider PostHog avec les informations d'authentification.
        """
        self.api_key = os.getenv("POSTHOG_API_KEY")
        self.project_id = os.getenv("POSTHOG_PROJECT_ID")
        self.api_url = os.getenv("POSTHOG_API_URL", "https://app.posthog.com/api")
        self.feedback_event = os.getenv("POSTHOG_FEEDBACK_EVENT", "feedback_submitted")
        
        if not self.api_key:
            raise ValueError("PostHog API key missing. Check POSTHOG_API_KEY environment variable.")
        
        if not self.project_id:
            raise ValueError("PostHog Project ID missing. Check POSTHOG_PROJECT_ID environment variable.")
        
        # Déterminer le type de clé API (project ou personal)
        self.is_project_key = self.api_key.startswith("phc_")
        self.is_personal_key = self.api_key.startswith("phx_")
        
        # Log the key type for debugging
        print(f"PostHog Provider initialized with {'Project' if self.is_project_key else 'Personal'} API key")
        
        # Configurer les headers selon le type de clé
        if self.is_project_key:
            # For project API keys: use Api-Key authentication
            self.headers = {
                "Authorization": f"Api-Key {self.api_key}",
                "Content-Type": "application/json"
            }
        else:
            # For personal API keys: use Bearer token authentication
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        
        # Tester la connexion
        self._test_connection()
    
    def _test_connection(self):
        """
        Teste la connexion à l'API PostHog.
        """
        # For personal API keys, a good test endpoint is the current user endpoint
        if self.is_personal_key:
            test_url = self.api_url.replace("/api", "/api/users/@me/")
        else:
            test_url = f"{self.api_url}/projects/{self.project_id}"
        
        print(f"Testing connection to: {test_url}")
        
        try:
            response = requests.get(test_url, headers=self.headers)
            response.raise_for_status()
            print(f"✅ PostHog connection successful: {response.status_code}")
            if self.is_personal_key and 'id' in response.json():
                print(f"  Connected as user: {response.json().get('email', 'Unknown')}")
        except requests.exceptions.RequestException as e:
            print(f"❌ PostHog connection failed: {e}")
            
            # Try alternative URL if this might be EU/US cloud
            if "app.posthog.com" in self.api_url:
                print("Trying EU cloud URL...")
                alt_url = self.api_url.replace("app.posthog.com", "eu.posthog.com")
                try:
                    if self.is_personal_key:
                        test_alt_url = alt_url.replace("/api", "/api/users/@me/")
                    else:
                        test_alt_url = f"{alt_url}/projects/{self.project_id}"
                    
                    print(f"Testing alternate URL: {test_alt_url}")
                    response = requests.get(test_alt_url, headers=self.headers)
                    response.raise_for_status()
                    print(f"✅ PostHog connection successful with EU cloud URL: {response.status_code}")
                    # Update the API URL to use the working URL
                    self.api_url = alt_url
                    return
                except requests.exceptions.RequestException as e:
                    print(f"❌ EU cloud URL also failed: {e}")
            
            # If still failing, try alternate authentication method
            print("Trying alternative authentication method...")
            if self.is_project_key:
                print("Trying with Bearer token instead of Api-Key...")
                self.headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            else:
                # For personal keys, try adding as a query parameter
                print("Trying with personal_api_key as query parameter...")
                try:
                    if self.is_personal_key:
                        param_url = f"{test_url}?personal_api_key={self.api_key}"
                    else:
                        param_url = f"{test_url}?token={self.api_key}"
                    
                    response = requests.get(param_url, headers={"Content-Type": "application/json"})
                    response.raise_for_status()
                    print(f"✅ PostHog connection successful with API key as parameter: {response.status_code}")
                    # Update strategy to use query params
                    self.use_query_param = True
                    return
                except requests.exceptions.RequestException as e:
                    print(f"❌ API key as parameter also failed: {e}")
                    self.use_query_param = False
                    
                    # Try Api-Key for personal key as last resort
                    print("Trying with Api-Key header for personal key (last resort)...")
                    self.headers = {
                        "Authorization": f"Api-Key {self.api_key}",
                        "Content-Type": "application/json"
                    }
            
            # Test again with alternate method
            try:
                response = requests.get(test_url, headers=self.headers)
                response.raise_for_status()
                print(f"✅ PostHog connection successful with alternate authentication: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ PostHog connection still failed with alternate authentication: {e}")
                print(f"   Status: {e.response.status_code if hasattr(e, 'response') and e.response else 'Unknown'}")
                print(f"   Response: {e.response.text[:200] if hasattr(e, 'response') and e.response else 'No response'}")
    
    def _add_auth_to_request(self, url, params=None):
        """Helper method to add authentication to requests based on determined method"""
        if hasattr(self, 'use_query_param') and self.use_query_param:
            # Use query param authentication
            if params is None:
                params = {}
            
            if self.is_personal_key:
                params['personal_api_key'] = self.api_key
            else:
                params['token'] = self.api_key
        
        return url, params

    def get_sessions(self, page_id: str, date_from: Optional[str] = None, 
                    date_to: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les sessions utilisateur pour une page spécifique depuis PostHog.
        """
        # Si dates non spécifiées, utiliser les 30 derniers jours
        if not date_from:
            date_from, date_to = self.get_date_range(30)
        
        # Parse dates to ensure correct format
        if isinstance(date_from, str):
            try:
                datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            except ValueError:
                print(f"⚠️ Invalid date_from format: {date_from}, using default")
                date_from, _ = self.get_date_range(30)
        
        if isinstance(date_to, str):
            try:
                datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            except ValueError:
                print(f"⚠️ Invalid date_to format: {date_to}, using default")
                _, date_to = self.get_date_range(30)
        
        print(f"Fetching sessions for page {page_id} from {date_from} to {date_to}")
        
        # Récupérer les enregistrements de session
        url = f"{self.api_url}/projects/{self.project_id}/session_recordings"
        params = {
            "limit": limit,
            "date_from": date_from
        }
        if date_to:
            params["date_to"] = date_to
        
        # Add authentication if using query params
        url, params = self._add_auth_to_request(url, params)
            
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            recordings = response.json().get("results", [])
            print(f"Retrieved {len(recordings)} total session recordings")
            
            # Filtrer les enregistrements qui contiennent la page demandée
            filtered_sessions = []
            for recording in recordings:
                session_id = recording.get("id")
                if not session_id:
                    continue
                    
                # Debugging
                # print(f"Processing session {session_id}")
                # print(f"Keys in session: {recording.keys()}")
                
                # Pour éviter trop de requêtes, vérifier d'abord si la page existe dans les données déjà récupérées
                if "start_url" in recording and page_id in recording.get("start_url", ""):
                    filtered_sessions.append(recording)
                    continue
                
                if "urls" in recording:
                    urls = recording.get("urls", [])
                    if urls and isinstance(urls, list) and any(page_id in url for url in urls):
                        filtered_sessions.append(recording)
                        continue
                
                # Si pas trouvé dans les métadonnées, récupérer les détails complets
                try:
                    session_details = self.get_session_recordings(session_id)
                    
                    # Vérifier si la session contient la page demandée
                    if self._session_contains_page(session_details, page_id):
                        filtered_sessions.append(session_details)
                except Exception as e:
                    print(f"Error retrieving details for session {session_id}: {e}")
            
            print(f"Filtered to {len(filtered_sessions)} sessions containing page {page_id}")
            return filtered_sessions
            
        except Exception as e:
            print(f"Error fetching sessions from PostHog: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.status_code} - {e.response.text[:200]}")
            return []
    
    def get_events(self, event_name: str, page_id: Optional[str] = None, 
                  date_from: Optional[str] = None, date_to: Optional[str] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les événements d'un type spécifique depuis PostHog.
        """
        # Si dates non spécifiées, utiliser les 30 derniers jours
        if not date_from:
            date_from, date_to = self.get_date_range(30)
        
        print(f"Fetching '{event_name}' events for page {page_id} from {date_from} to {date_to}")
            
        url = f"{self.api_url}/projects/{self.project_id}/events"
        params = {
            "event": event_name,
            "limit": limit,
            "date_from": date_from
        }
        if date_to:
            params["date_to"] = date_to
        if page_id:
            params["properties"] = json.dumps({"$current_url": f"*{page_id}*"})
        
        # Add authentication if using query params
        url, params = self._add_auth_to_request(url, params)
            
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            events = response.json().get("results", [])
            print(f"Retrieved {len(events)} events of type '{event_name}'")
            return events
        except Exception as e:
            print(f"Error fetching events from PostHog: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.status_code} - {e.response.text[:200]}")
            return []
    
    def get_user_feedback(self, page_id: Optional[str] = None,
                        date_from: Optional[str] = None, 
                        date_to: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les feedbacks utilisateur depuis PostHog.
        """
        # Utiliser l'événement de feedback configuré
        events = self.get_events(
            event_name=self.feedback_event,
            page_id=page_id,
            date_from=date_from,
            date_to=date_to
        )
        
        # Transformer les événements en format de feedback
        feedbacks = []
        for event in events:
            properties = event.get("properties", {})
            feedback = {
                "id": event.get("id"),
                "timestamp": event.get("timestamp"),
                "page": properties.get("$current_url", ""),
                "message": properties.get("message", ""),
                "sentiment": properties.get("sentiment", "neutral"),
                "user_id": properties.get("distinct_id", "")
            }
            feedbacks.append(feedback)
        
        print(f"Transformed {len(feedbacks)} events into feedback format")
        return feedbacks
    
    def get_session_recordings(self, session_id: str) -> Dict[str, Any]:
        """
        Récupère les enregistrements d'une session spécifique depuis PostHog.
        """
        url = f"{self.api_url}/projects/{self.project_id}/session_recordings/{session_id}"
        
        # Add authentication if using query params
        url, params = self._add_auth_to_request(url)
        
        try:
            response = requests.get(url, headers=self.headers, params=params if params else None)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching session recording from PostHog: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.status_code} - {e.response.text[:200]}")
            return {}
    
    def _session_contains_page(self, session: Dict[str, Any], page_id: str) -> bool:
        """
        Vérifie si une session contient une page spécifique.
        
        Args:
            session: Données de la session
            page_id: Identifiant de la page à rechercher
            
        Returns:
            True si la session contient la page, False sinon
        """
        # Debugging
        # print(f"Checking if session contains page {page_id}")
        # print(f"Session keys: {session.keys()}")
        
        # Check different places where page URL might be stored
        
        # 1. Check start_url
        start_url = session.get("start_url", "")
        if start_url and page_id in start_url:
            return True
            
        # 2. Check URLs list
        urls = session.get("urls", [])
        if urls and isinstance(urls, list):
            for url in urls:
                if page_id in url:
                    return True
        
        # 3. Check snapshots/pages
        snapshots = session.get("snapshots", {})
        if snapshots and isinstance(snapshots, dict):
            pages = snapshots.get("pages", [])
            if pages and isinstance(pages, list):
                for page in pages:
                    if isinstance(page, dict) and "url" in page and page_id in page.get("url", ""):
                        return True
        
        # 4. Check events for page views
        events = session.get("events", [])
        if events and isinstance(events, list):
            for event in events:
                if isinstance(event, dict):
                    props = event.get("properties", {})
                    if isinstance(props, dict) and "$current_url" in props and page_id in props["$current_url"]:
                        return True
                
        return False


class MixpanelProvider(AnalyticsProvider):
    """
    Implémentation de l'interface AnalyticsProvider pour Mixpanel.
    Note: Cette implémentation est partielle et nécessite d'être complétée.
    """
    
    def __init__(self):
        """
        Initialise le provider Mixpanel avec les informations d'authentification.
        """
        self.api_key = os.getenv("MIXPANEL_API_KEY")
        self.api_secret = os.getenv("MIXPANEL_API_SECRET")
        self.project_id = os.getenv("MIXPANEL_PROJECT_ID")
        self.api_url = "https://mixpanel.com/api"
        
        if not all([self.api_key, self.api_secret]):
            raise ValueError("Mixpanel API configuration missing. Check environment variables.")
        
        # En-têtes pour l'authentification
        import base64
        auth_header = base64.b64encode(f"{self.api_key}:{self.api_secret}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json"
        }
    
    def get_sessions(self, page_id: str, date_from: Optional[str] = None, 
                    date_to: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les sessions utilisateur pour une page spécifique depuis Mixpanel.
        Note: Cette implémentation est un exemple et doit être adaptée à l'API Mixpanel.
        """
        # TODO: Implémenter la récupération des sessions Mixpanel
        return []
    
    def get_events(self, event_name: str, page_id: Optional[str] = None, 
                  date_from: Optional[str] = None, date_to: Optional[str] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les événements d'un type spécifique depuis Mixpanel.
        """
        # TODO: Implémenter la récupération des événements Mixpanel
        return []
    
    def get_user_feedback(self, page_id: Optional[str] = None,
                         date_from: Optional[str] = None, 
                         date_to: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les feedbacks utilisateur depuis Mixpanel.
        """
        # TODO: Implémenter la récupération des feedbacks Mixpanel
        return []
    
    def get_session_recordings(self, session_id: str) -> Dict[str, Any]:
        """
        Récupère les enregistrements d'une session spécifique depuis Mixpanel.
        """
        # TODO: Implémenter la récupération des enregistrements de session Mixpanel
        return {}


class AmplitudeProvider(AnalyticsProvider):
    """
    Implémentation de l'interface AnalyticsProvider pour Amplitude.
    Note: Cette implémentation est partielle et nécessite d'être complétée.
    """
    
    def __init__(self):
        """
        Initialise le provider Amplitude avec les informations d'authentification.
        """
        self.api_key = os.getenv("AMPLITUDE_API_KEY")
        self.api_secret = os.getenv("AMPLITUDE_SECRET_KEY")
        self.api_url = "https://amplitude.com/api/2"
        
        if not all([self.api_key]):
            raise ValueError("Amplitude API configuration missing. Check environment variables.")
        
        # En-têtes pour l'authentification
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def get_sessions(self, page_id: str, date_from: Optional[str] = None, 
                    date_to: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les sessions utilisateur pour une page spécifique depuis Amplitude.
        """
        # TODO: Implémenter la récupération des sessions Amplitude
        return []
    
    def get_events(self, event_name: str, page_id: Optional[str] = None, 
                  date_from: Optional[str] = None, date_to: Optional[str] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère les événements d'un type spécifique depuis Amplitude.
        """
        # TODO: Implémenter la récupération des événements Amplitude
        return []
    
    def get_user_feedback(self, page_id: Optional[str] = None,
                         date_from: Optional[str] = None, 
                         date_to: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Récupère les feedbacks utilisateur depuis Amplitude.
        """
        # TODO: Implémenter la récupération des feedbacks Amplitude
        return []
    
    def get_session_recordings(self, session_id: str) -> Dict[str, Any]:
        """
        Récupère les enregistrements d'une session spécifique depuis Amplitude.
        """
        # TODO: Implémenter la récupération des enregistrements de session Amplitude
        return {}


class AnalyticsFactory:
    """
    Factory pour créer des instances de providers d'analytics en fonction du type.
    """
    
    @staticmethod
    def create_provider(provider_type: str) -> AnalyticsProvider:
        """
        Crée une instance du provider d'analytics demandé.
        
        Args:
            provider_type: Type de provider ('posthog', 'mixpanel', 'amplitude')
            
        Returns:
            Instance du provider d'analytics
            
        Raises:
            ValueError: Si le type de provider n'est pas supporté
        """
        if provider_type.lower() == 'posthog':
            return PostHogProvider()
        elif provider_type.lower() == 'mixpanel':
            return MixpanelProvider()
        elif provider_type.lower() == 'amplitude':
            return AmplitudeProvider()
        else:
            raise ValueError(f"Provider type '{provider_type}' not supported")

# Fonction utilitaire pour obtenir le provider configuré dans l'environnement
def get_configured_provider() -> AnalyticsProvider:
    """
    Récupère le provider d'analytics configuré dans les variables d'environnement.
    
    Returns:
        Instance du provider d'analytics configuré
    """
    provider_type = os.getenv("ANALYTICS_PROVIDER", "posthog")
    return AnalyticsFactory.create_provider(provider_type) 