import os
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement
load_dotenv()

class Config:
    # Clés API
    API_KEY = os.getenv("API_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # URLs
    EXPORT_URL = os.getenv("EXPORT_URL")
    AMPLITUDE_URL = os.getenv("AMPLITUDE_URL")
    
    # Chemins
    BASE_PATH = os.getenv("BASE_PATH")
    
    # ID de l'application
    APP_ID = "amplitude_data"
    
    # Vous pouvez ajouter d'autres configurations ici si nécessaire
    # BASE_URL = os.getenv('BASE_URL')
    # TIMEOUT = int(os.getenv('TIMEOUT', 30)) 