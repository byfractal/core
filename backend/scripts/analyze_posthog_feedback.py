#!/usr/bin/env python3
"""
Script pour extraire les données de PostHog et lancer l'analyse de feedback en un seul pipeline.
Ce script facilite l'analyse des feedbacks réels en automatisant le processus complet.
"""

import os
import sys
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

from backend.services.posthog_service import PostHogService
from backend.models.feedback_analyzer import analyze_feedbacks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Point d'entrée principal du script."""
    parser = argparse.ArgumentParser(description="Extraire les données de PostHog et lancer l'analyse de feedback")
    
    parser.add_argument(
        "--event",
        type=str,
        help="Nom de l'événement PostHog à récupérer (par défaut: valeur de POSTHOG_FEEDBACK_EVENT dans .env)"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Nombre de jours à récupérer (par défaut: 30)"
    )
    
    parser.add_argument(
        "--posthog-output",
        type=str,
        default="data/posthog_data/processed/latest.json",
        help="Chemin du fichier de sortie pour les données PostHog (par défaut: data/posthog_data/processed/latest.json)"
    )
    
    parser.add_argument(
        "--analysis-output",
        type=str,
        default=f"data/analysis_results/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        help="Chemin du fichier de sortie pour l'analyse"
    )
    
    parser.add_argument(
        "--page", 
        type=str, 
        help="Filtrer les feedbacks par page"
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        default="gpt-3.5-turbo",
        help="Modèle LLM à utiliser pour l'analyse (par défaut: gpt-3.5-turbo)"
    )
    
    parser.add_argument(
        "--skip-extraction",
        action="store_true",
        help="Ignorer l'étape d'extraction et utiliser directement le fichier existant"
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
    
    # Si aucun événement n'est spécifié, utiliser la valeur de POSTHOG_FEEDBACK_EVENT
    if not args.event:
        args.event = os.getenv("POSTHOG_FEEDBACK_EVENT", "feedback_submitted")
    
    # Calculer les dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    # Extraire les données de PostHog si nécessaire
    if not args.skip_extraction:
        logger.info(f"Étape 1/2: Extraction des événements PostHog du {start_date} au {end_date}")
        
        # Vérifier que les variables d'environnement nécessaires sont définies
        api_key = os.getenv("POSTHOG_API_KEY")
        project_id = os.getenv("POSTHOG_PROJECT_ID")
        
        if not api_key or not project_id:
            logger.error("Les variables d'environnement POSTHOG_API_KEY et POSTHOG_PROJECT_ID doivent être définies")
            sys.exit(1)
        
        # Créer l'instance du service PostHog
        base_url = args.api_url or os.getenv("POSTHOG_API_URL", "https://app.posthog.com/api")
        posthog_service = PostHogService(api_key=api_key, project_id=project_id, base_url=base_url)
        
        # Récupérer et sauvegarder les événements
        extracted_file = posthog_service.fetch_and_save_feedback(
            event_name=args.event,
            start_date=start_date,
            end_date=end_date,
            output_file=args.posthog_output
        )
        
        if extracted_file == "No events retrieved":
            logger.warning("Aucun événement récupéré depuis PostHog")
            sys.exit(1)
        elif extracted_file == "Error saving events":
            logger.error("Erreur lors de la sauvegarde des événements")
            sys.exit(1)
        
        logger.info(f"Données PostHog extraites et sauvegardées dans {extracted_file}")
        feedback_file = extracted_file
    else:
        logger.info("Étape d'extraction ignorée, utilisation du fichier existant")
        feedback_file = args.posthog_output
    
    # Lancer l'analyse
    logger.info(f"Étape 2/2: Analyse des feedbacks (page: {args.page or 'toutes'}, model: {args.model})")
    results = analyze_feedbacks(
        page_id=args.page,
        start_date=start_date,
        end_date=end_date,
        model=args.model,
        feedback_file=feedback_file
    )
    
    # Sauvegarder les résultats
    if results.get("status") == "success":
        logger.info(f"Analyse réussie! {results.get('metadata', {}).get('feedback_count', 0)} feedbacks analysés")
        
        # Créer le répertoire de sortie si nécessaire
        os.makedirs(os.path.dirname(args.analysis_output), exist_ok=True)
        
        # Sauvegarder les résultats
        try:
            import json
            with open(args.analysis_output, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Résultats sauvegardés dans {args.analysis_output}")
            
            # Afficher un résumé des résultats
            sentiment_distribution = results.get("results", {}).get("summary", {}).get("sentiment_distribution", {})
            if sentiment_distribution:
                logger.info(f"Distribution des sentiments:")
                for sentiment, percentage in sentiment_distribution.items():
                    logger.info(f"  - {sentiment}: {percentage}%")
            
            summaries = results.get("results", {}).get("summary", {}).get("summaries", {})
            if summaries:
                overall_summary = summaries.get("overall", "")
                if overall_summary:
                    logger.info(f"Résumé global: {overall_summary[:150]}...")
                
                recommendations = summaries.get("recommendations", "")
                if recommendations:
                    logger.info(f"Recommandations: {recommendations[:150]}...")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des résultats: {e}")
    else:
        logger.warning(f"Analyse échouée: {results.get('results', {}).get('error', 'Erreur inconnue')}")

if __name__ == "__main__":
    main() 