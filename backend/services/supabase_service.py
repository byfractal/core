import os
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Charger les variables d'environnement
load_dotenv()

# Variables de configuration Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# Cache pour la connexion client
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Crée ou récupère une instance de client Supabase.
    
    Returns:
        Client Supabase
    
    Raises:
        ValueError: Si les informations de connexion Supabase ne sont pas définies
    """
    global _supabase_client
    
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "Supabase URL and anonymous key must be set in environment variables "
                "SUPABASE_URL and SUPABASE_ANON_KEY"
            )
        
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    return _supabase_client

def get_analysis_cards(figma_file_key):
    """Récupère les cartes d'analyse pour un fichier Figma spécifique.
    
    Args:
        figma_file_key: La clé du fichier Figma
        
    Returns:
        Une liste de cartes d'analyse depuis Supabase
    """
    supabase = get_supabase_client()
    result = supabase.table('analysis_cards').select('*').eq('figma_file_key', figma_file_key).execute()
    return result.data 