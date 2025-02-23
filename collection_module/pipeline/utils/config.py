import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

class Config:
    API_KEY = os.getenv('API_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')
    EXPORT_URL = os.getenv('EXPORT_URL')
    AMPLITUDE_URL = os.getenv('AMPLITUDE_URL')
    APP_ID = os.getenv('APP_ID')
    
    # Vous pouvez ajouter d'autres configurations ici si nécessaire
    # BASE_URL = os.getenv('BASE_URL')
    # TIMEOUT = int(os.getenv('TIMEOUT', 30)) 