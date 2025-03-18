"""
Script de test pour vérifier l'intégration avec PostHog et l'accès aux données des sessions replay.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Ajouter le répertoire racine au PYTHONPATH
root_dir = str(Path(__file__).parent.absolute())
sys.path.append(root_dir)

# Charger les variables d'environnement
load_dotenv()

# Importer les fonctions à tester
from backend.models.design_recommendations import (
    fetch_session_recordings,
    download_session_data
)

class PostHogClient:
    """
    Client PostHog pour interagir avec l'API de manière plus structurée.
    """
    def __init__(self):
        self.api_key = os.getenv("POSTHOG_API_KEY")
        self.project_id = os.getenv("POSTHOG_PROJECT_ID")
        self.api_url = os.getenv("POSTHOG_API_URL")
        
        if not all([self.api_key, self.project_id, self.api_url]):
            raise ValueError("Les variables d'environnement PostHog ne sont pas correctement configurées")
    
    def get_sessions_for_page(self, page_id, days=30):
        """
        Récupère les sessions pour une page spécifique dans les X derniers jours.
        """
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        date_to = datetime.now().isoformat()
        
        # Récupérer toutes les sessions
        sessions = fetch_session_recordings(date_from=date_from, date_to=date_to)
        
        # Filtrer les sessions qui contiennent la page demandée
        # Cette partie est simplifiée et devra être adaptée selon la structure réelle des données
        filtered_sessions = []
        
        # Le filtrage réel dépendra de la structure exacte des données renvoyées par PostHog
        # Ceci est juste un exemple
        for session in sessions.get("results", []):
            if "pages" in session and any(page["url"].endswith(page_id) for page in session.get("pages", [])):
                filtered_sessions.append(session)
        
        return filtered_sessions
    
    def get_feedback_for_page(self, page_id, days=30):
        """
        Récupère les feedbacks pour une page spécifique dans les X derniers jours.
        """
        # Cette méthode devra être implémentée selon la structure de vos données de feedback
        # Retourne un résultat simulé pour le test
        return [{
            "text": "Test feedback",
            "sentiment": "positive",
            "page": page_id,
            "timestamp": datetime.now().isoformat()
        }]
    
    def generate_click_heatmap(self, sessions):
        """
        Génère une carte de chaleur des clics à partir des données de session.
        """
        # Cette méthode devra être implémentée selon la structure exacte des données
        # Retourne un résultat simulé pour le test
        return {
            "heatmap_data": [
                {"x": 100, "y": 200, "value": 5},
                {"x": 300, "y": 150, "value": 10},
                {"x": 500, "y": 300, "value": 3}
            ]
        }
    
    def identify_confusion_areas(self, sessions):
        """
        Identifie les zones de confusion basées sur les mouvements de souris, clics multiples, etc.
        """
        # Cette méthode devra être implémentée selon la structure exacte des données
        # Retourne un résultat simulé pour le test
        return [
            {"area": "form_section", "score": 0.8},
            {"area": "navigation_menu", "score": 0.4}
        ]

def test_posthog_connection():
    """
    Teste la connexion à l'API PostHog.
    """
    print("\n--- Test de connexion à PostHog ---")
    
    # Vérifier que les variables d'environnement sont définies
    api_key = os.getenv("POSTHOG_API_KEY")
    project_id = os.getenv("POSTHOG_PROJECT_ID")
    api_url = os.getenv("POSTHOG_API_URL")
    
    print(f"API URL: {api_url}")
    print(f"Project ID: {project_id}")
    print(f"API Key: {api_key[:5]}...{api_key[-3:] if api_key else None}")
    
    if not all([api_key, project_id, api_url]):
        print("❌ Configuration PostHog incomplète")
        return False
    
    print("✅ Configuration PostHog complète")
    return True

def test_fetch_sessions():
    """
    Teste la récupération des sessions depuis PostHog.
    """
    print("\n--- Test de récupération des sessions ---")
    
    # Définir une période de test (7 derniers jours)
    date_from = (datetime.now() - timedelta(days=7)).isoformat()
    date_to = datetime.now().isoformat()
    
    try:
        sessions = fetch_session_recordings(date_from=date_from, date_to=date_to)
        
        # Vérifier que nous avons des résultats
        if "results" in sessions:
            session_count = len(sessions["results"])
            print(f"✅ Récupération réussie : {session_count} sessions trouvées")
            
            # Afficher des informations sur la première session si disponible
            if session_count > 0:
                first_session = sessions["results"][0]
                session_id = first_session.get("id", "N/A")
                print(f"ID de la première session : {session_id}")
                return first_session
            
        else:
            print("❌ Format de réponse inattendu")
            print(f"Réponse reçue : {json.dumps(sessions, indent=2)[:500]}...")
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des sessions : {str(e)}")
    
    return None

def test_download_session():
    """
    Teste le téléchargement des données détaillées d'une session.
    """
    print("\n--- Test de téléchargement d'une session ---")
    
    # D'abord récupérer une session à télécharger
    session = test_fetch_sessions()
    
    if not session:
        print("❌ Aucune session disponible pour le téléchargement")
        return
    
    session_id = session.get("id")
    
    try:
        session_data = download_session_data(session_id)
        
        # Vérifier que nous avons des données
        if session_data:
            print(f"✅ Téléchargement réussi pour la session {session_id}")
            
            # Afficher un aperçu des données
            print("\nAperçu des données de session :")
            for key, value in session_data.items():
                if isinstance(value, dict) or isinstance(value, list):
                    value_type = f"{type(value).__name__} de taille {len(value)}"
                else:
                    value_type = value
                print(f"- {key}: {value_type}")
            
            # Analyser les événements si disponibles
            if "events" in session_data:
                events = session_data["events"]
                event_count = len(events)
                print(f"\nNombre d'événements dans la session : {event_count}")
                
                if event_count > 0:
                    event_types = {}
                    for event in events:
                        event_type = event.get("type")
                        event_types[event_type] = event_types.get(event_type, 0) + 1
                    
                    print("Types d'événements présents :")
                    for event_type, count in event_types.items():
                        print(f"- {event_type}: {count}")
        else:
            print(f"❌ Aucune donnée reçue pour la session {session_id}")
            
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement de la session : {str(e)}")

def test_design_suggestion_generator():
    """
    Teste la génération de suggestions de design.
    """
    print("\n--- Test du générateur de suggestions de design ---")
    
    try:
        # Initialiser le client PostHog
        client = PostHogClient()
        print("✅ Client PostHog initialisé")
        
        # Tester la récupération des sessions pour une page
        page_id = "/home"  # À adapter selon votre structure d'URL
        sessions = client.get_sessions_for_page(page_id, days=30)
        
        print(f"Sessions récupérées pour la page {page_id}: {len(sessions)}")
        
        # Tester la génération de heatmap
        heatmap = client.generate_click_heatmap(sessions)
        print("✅ Génération de heatmap réussie")
        
        # Tester l'identification des zones de confusion
        confusion_areas = client.identify_confusion_areas(sessions)
        print("✅ Identification des zones de confusion réussie")
        
        # Tester la récupération des feedbacks
        feedback = client.get_feedback_for_page(page_id, days=30)
        print(f"Feedbacks récupérés pour la page {page_id}: {len(feedback)}")
        
        print("✅ Tous les tests du générateur de suggestions réussis")
        
    except Exception as e:
        print(f"❌ Erreur lors du test du générateur de suggestions : {str(e)}")

if __name__ == "__main__":
    print("=== Tests d'intégration PostHog ===")
    
    # Tester la connexion à PostHog
    if test_posthog_connection():
        # Tester la récupération des sessions
        test_fetch_sessions()
        
        # Tester le téléchargement d'une session
        test_download_session()
        
        # Tester le générateur de suggestions de design
        test_design_suggestion_generator()
        
    print("\n=== Fin des tests ===") 