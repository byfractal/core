from dotenv import load_dotenv
import os
import logging
from pathlib import Path

# Charger les variables d'environnement
load_dotenv()

# Configuration globale
class Config:
    API_KEY = os.getenv("API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
    EXPORT_URL = os.getenv("EXPORT_URL")
    AMPLITUDE_URL = os.getenv("AMPLITUDE_URL")
    APP_ID = os.getenv("APP_ID")

    # Validation des variables requises
    @classmethod
    def validate(cls):
        required_vars = ["API_KEY", "SECRET_KEY", "EXPORT_URL", "APP_ID"]
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Variables d'environnement manquantes: {', '.join(missing_vars)}")

    @classmethod
    def log_config(cls):
        logging.info(f"Configuration chargée:")
        logging.info(f"APP_ID: {cls.APP_ID}")
        logging.info(f"API_KEY présente: {'Oui' if cls.API_KEY else 'Non'}")
        logging.info(f"SECRET_KEY présente: {'Oui' if cls.SECRET_KEY else 'Non'}")