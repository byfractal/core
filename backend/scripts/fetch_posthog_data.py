#!/usr/bin/env python3
"""
Script pour extraire les données de feedback depuis PostHog et les préparer pour l'analyse.
Ce script récupère les événements de feedback depuis l'API PostHog, les convertit au format
compatible avec notre analyseur et les sauvegarde dans un fichier JSON.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

from backend.services.posthog_service import PostHogService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Point d'entrée principal du script."""
    parser = argparse.ArgumentParser(description="Extraire les données de feedback depuis PostHog")
    
    parser.add_argument(
        "--event",
        type=str,
        default="feedback_submitted",
        help="Nom de l'événement PostHog à récupérer (par défaut: feedback_submitted)"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Nombre de jours à récupérer (par défaut: 30)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="data/posthog_data/processed/latest.json",
        help="Chemin du fichier de sortie (par défaut: data/posthog_data/processed/latest.json)"
    )
    
    parser.add_argument(
        "--link",
        action="store_true",
        help="Créer un lien symbolique vers latest.json (utilisé par l'analyseur)"
    )
    
    parser.add_argument(
        "--env-file",
        type=str,
        default=".env",
        help="Chemin du fichier .env contenant les variables d'environnement"
    )
    
    parser.add_argument(
        "--api-url",
        type=str,
        help="URL de base de l'API PostHog (par défaut: https://app.posthog.com/api)"
    )
    
    args = parser.parse_args()
    
    # Charger les variables d'environnement
    if os.path.exists(args.env_file):
        load_dotenv(dotenv_path=args.env_file)
    else:
        load_dotenv()
    
    # Vérifier que les variables d'environnement nécessaires sont définies
    api_key = os.getenv("POSTHOG_API_KEY")
    project_id = os.getenv("POSTHOG_PROJECT_ID")
    
    if not api_key or not project_id:
        logger.error("Les variables d'environnement POSTHOG_API_KEY et POSTHOG_PROJECT_ID doivent être définies")
        sys.exit(1)
    
    # Calculer les dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    logger.info(f"Extraction des événements de feedback depuis PostHog du {start_date} au {end_date}")
    
    # Créer l'instance du service PostHog
    base_url = args.api_url or os.getenv("POSTHOG_API_URL", "https://app.posthog.com/api")
    posthog_service = PostHogService(api_key=api_key, project_id=project_id, base_url=base_url)
    
    # Récupérer et sauvegarder les événements
    output_file = posthog_service.fetch_and_save_feedback(
        event_name=args.event,
        start_date=start_date,
        end_date=end_date,
        output_file=args.output
    )
    
    if output_file == "No events retrieved":
        logger.warning("Aucun événement récupéré depuis PostHog")
        sys.exit(1)
    elif output_file == "Error saving events":
        logger.error("Erreur lors de la sauvegarde des événements")
        sys.exit(1)
    
    logger.info(f"Événements sauvegardés dans {output_file}")
    
    # Créer un lien symbolique vers latest.json si demandé
    if args.link:
        amplitude_dir = "data/amplitude_data/processed"
        amplitude_latest = f"{amplitude_dir}/latest.json"
        
        # Créer le répertoire si nécessaire
        os.makedirs(amplitude_dir, exist_ok=True)
        
        # Supprimer le lien existant s'il existe
        if os.path.exists(amplitude_latest):
            if os.path.islink(amplitude_latest):
                os.unlink(amplitude_latest)
            else:
                os.rename(amplitude_latest, f"{amplitude_dir}/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Créer un lien relatif pour plus de portabilité
        relative_path = os.path.relpath(output_file, amplitude_dir)
        os.symlink(relative_path, amplitude_latest)
        
        logger.info(f"Lien symbolique créé: {amplitude_latest} -> {relative_path}")
    
    # Afficher un résumé des événements
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            events = json.load(f)
            
        # Extraire les pages uniques
        pages = set()
        for event in events:
            page = event.get("event_properties", {}).get("page")
            if page:
                pages.add(page)
        
        logger.info(f"Résumé des événements:")
        logger.info(f"  - Nombre total d'événements: {len(events)}")
        logger.info(f"  - Pages uniques: {', '.join(pages)}")
        
        # Afficher quelques exemples de feedback
        if events:
            logger.info(f"Exemples de feedback:")
            for i, event in enumerate(events[:3]):
                feedback = event.get("event_properties", {}).get("feedback_text", "")
                if feedback:
                    logger.info(f"  {i+1}. {feedback[:100]}...")
    except Exception as e:
        logger.warning(f"Impossible d'afficher le résumé des événements: {e}")

if __name__ == "__main__":
    main() 