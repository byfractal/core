import pandas as pd
import requests
import json
import logging
from collection_module.pipeline.utils.config import Config
from collection_module.pipeline.utils.utils import setup_logging

def send_events(events):
    try:
        # Configuration du logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Configuration de l'API
        api_key = Config.API_KEY
        if not api_key:
            raise ValueError("La clé API n'est pas configurée")

        # Préparation de la requête
        headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': api_key
        }

        # Envoi des événements
        response = requests.post(
            'https://api.amplitude.com/2/httpapi',
            headers=headers,
            json=events
        )
        response.raise_for_status()
        
        return response.json()

    except Exception as e:
        logger.error(f"Erreur lors de l'envoi des événements: {str(e)}")
        raise

if __name__ == "__main__":
    # Vérification simple de la configuration
    if not Config.API_KEY:
        raise ValueError("La clé API n'est pas configurée")
    print("Configuration validée avec succès")