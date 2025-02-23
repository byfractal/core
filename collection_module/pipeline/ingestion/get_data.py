from datetime import datetime, timezone, timedelta
import requests
import logging
from pathlib import Path
from collection_module.pipeline.utils.config import Config
from collection_module.pipeline.utils.utils import setup_logging, ensure_directory_structure
import base64

logger = setup_logging()

def get_data(start_date=None, end_date=None):
    """Récupère les données de l'API Amplitude"""
    # Si les dates ne sont pas fournies, utiliser les 30 derniers jours
    if start_date is None:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
    
    # Configuration de l'API
    api_key = Config.API_KEY
    secret_key = Config.SECRET_KEY
    
    if not api_key or not secret_key:
        raise ValueError("La clé API et la clé secrète sont requises")
    
    # Créer le header d'authentification Basic
    credentials = f"{api_key}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/json'
    }
    
    # Utiliser l'URL d'export depuis la config
    base_url = Config.EXPORT_URL
    
    # Formater les dates au format ISO 8601
    start_str = start_date.strftime("%Y%m%dT%H")
    end_str = end_date.strftime("%Y%m%dT%H")
    
    url = f"{base_url}?start={start_str}&end={end_str}"
    
    try:
        # Faire la requête
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erreur lors de la récupération des données: {str(e)}")

def save_data_to_file(data, filename, paths):
    """Sauvegarde les données récupérées dans un fichier"""
    try:
        file_path = paths['raw'] / filename
        
        # Validation du format
        if data[:2] == b'\x1f\x8b' or data[:2] == b'PK':  # GZIP ou ZIP
            with open(file_path, "wb") as file:
                file.write(data)
            logger.info(f"Données sauvegardées dans {file_path}")
        else:
            # Si les données ne sont pas compressées, les sauvegarder en JSON
            with open(file_path.with_suffix('.json'), "wb") as file:
                file.write(data)
            logger.info(f"Données non compressées sauvegardées en JSON")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des données: {e}")
        raise

def fetch_data_for_period(days: int):
    """Récupère les données pour une période donnée"""
    try:
        # Vérification de la configuration
        if not Config.API_KEY:
            raise ValueError("La clé API n'est pas configurée")
        
        # Création des dossiers nécessaires
        paths = ensure_directory_structure(Config.APP_ID)
        
        # Calcul des dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Vérifier si des données existent déjà pour cette période
        existing_files = list(paths['raw'].glob('amplitude_data_*.gz'))
        if existing_files:
            logger.info("Des données existent déjà. Nettoyage des anciens fichiers...")
            for file in existing_files:
                file.unlink()  # Supprime les anciens fichiers
        
        # Récupération des données
        data = get_data(start_date, end_date)
        
        # Génération du nom de fichier avec la date
        filename = f"amplitude_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gz"
        
        # Sauvegarde des données
        save_data_to_file(data, filename, paths)
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        setup_logging()
        data = get_data()
        print("Données récupérées avec succès")
    except Exception as e:
        print(f"Erreur: {str(e)}")