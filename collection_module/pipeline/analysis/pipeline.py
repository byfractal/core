from collections import defaultdict
import logging
import traceback
from pathlib import Path
from typing import Dict, List, Optional
from collection_module.pipeline.analysis import pipeline

from collection_module.pipeline.utils.config import Config
from collection_module.pipeline.utils.utils import setup_logging, ensure_directory_structure, JSONHandler
from collection_module.pipeline.ingestion.decompress_files import decompress_files


logger = setup_logging()

class DataPipeline:
    def __init__(self):
        self.desired_event_types = ["SurveySubmitted", "TestEvent"]
        self.required_fields = ["event_type", "user_properties"]
        self.paths = None
        self.logger = logging.getLogger(__name__)
        
    def initialize(self) -> None:
        """Initialise le pipeline"""
        # Vérification de la configuration
        if not Config.API_KEY:
            raise ValueError("La clé API n'est pas configurée")
        if not Config.APP_ID:
            raise ValueError("L'APP_ID n'est pas configuré")
            
        self.paths = ensure_directory_structure(Config.APP_ID)
        
    def filter_events(self) -> bool:
        """Filtre les événements selon les types désirés"""
        try:
            processed_files = list(self.paths['processed'].glob('**/*.json'))
            if not processed_files:
                logger.warning("Aucun fichier à traiter dans le dossier processed")
                return False
                
            for file_path in processed_files:
                try:
                    # Lire et filtrer les événements
                    events = JSONHandler.read_jsonl(file_path)
                    filtered_data = [
                        event for event in events
                        if JSONHandler.validate_event(event, self.required_fields) and
                        event.get("event_type") in self.desired_event_types
                    ]
                    
                    if filtered_data:
                        # Sauvegarder les événements filtrés
                        output_path = self.paths['filtered'] / f"filtered_{file_path.name}"
                        JSONHandler.write(output_path, filtered_data)
                        logger.info(f"Événements filtrés sauvegardés dans: {output_path}")
                        
                except Exception as e:
                    logger.error(f"Erreur lors du traitement de {file_path}: {e}")
                    continue
                    
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du filtrage des événements: {e}")
            return False
            
    def create_summary(self) -> bool:
        """Crée un résumé des événements"""
        try:
            summary = defaultdict(int)
            filtered_files = list(self.paths['filtered'].glob('*.json'))
            
            if not filtered_files:
                logger.warning("Aucun fichier à résumer dans le dossier filtered")
                return False
                
            for file_path in filtered_files:
                try:
                    data = JSONHandler.read(file_path)
                    for event in data:
                        if JSONHandler.validate_event(event):
                            summary[event.get("event_type", "unknown")] += 1
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture de {file_path}: {e}")
                    continue
            
            # Sauvegarder le résumé en JSON
            summary_path = self.paths['filtered'] / "events_summary.json"
            JSONHandler.write(summary_path, dict(summary))
            logger.info(f"Résumé sauvegardé dans: {summary_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du résumé: {e}")
            return False
    
    def export_to_json(self) -> bool:
        """Exporte les données filtrées en JSON"""
        try:
            all_events = []
            filtered_files = list(self.paths['filtered'].glob('*.json'))
            
            for file_path in filtered_files:
                try:
                    data = JSONHandler.read(file_path)
                    all_events.extend(data)
                except Exception as e:
                    logger.error(f"Erreur lors de la lecture de {file_path}: {e}")
                    continue
            
            if all_events:
                json_path = self.paths['filtered'] / "events_data.json"
                JSONHandler.write(json_path, all_events)
                logger.info(f"Données exportées dans: {json_path}")
                return True
            else:
                logger.warning("Aucune donnée à exporter")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'export JSON: {str(e)}")
            return False
    
    def run(self) -> bool:
        """Exécute le pipeline complet"""
        try:
            self.logger.info("Démarrage du pipeline de traitement...")
            
            # Étape 1: Obtenir les chemins des dossiers
            self.logger.info("Étape 1: Obtention des chemins des dossiers...")
            paths = ensure_directory_structure(Config.APP_ID)
            self.logger.info(f"Chemins obtenus: {paths}")
            
            # Étape 2: Trouver les fichiers de données brutes
            self.logger.info("Étape 2: Recherche des fichiers de données brutes...")
            raw_files = list(paths['raw'].glob('amplitude_data_*.gz'))
            if not raw_files:
                self.logger.error("Aucun fichier de données brutes trouvé")
                return False
            self.logger.info(f"Fichiers trouvés: {raw_files}")
            
            # Étape 3: Traiter chaque fichier
            self.logger.info("Étape 3: Traitement des fichiers...")
            for file_path in raw_files:
                self.logger.info(f"Traitement du fichier: {file_path}")
                # Ajoute ici le code pour traiter le fichier
                # Par exemple: self._process_file(file_path, paths['processed'])
            
            self.logger.info("Pipeline de traitement terminé avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement: {str(e)}")
            self.logger.error(traceback.format_exc())  # Affiche la stack trace complète
            return False
    
    def _process_file(self, file_path, output_dir):
        """Traite un fichier de données brutes"""
        try:
            self.logger.info(f"Traitement du fichier {file_path}...")
            # Ajoute ici le code pour traiter le fichier
            # Par exemple: lire le fichier, transformer les données, sauvegarder les résultats
            self.logger.info(f"Fichier {file_path} traité avec succès")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement du fichier {file_path}: {str(e)}")
            self.logger.error(traceback.format_exc())
            return False

def run_pipeline():
    try:
        # Configuration du logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Démarrage du pipeline...")

        # Vérification de la clé API
        if not Config.API_KEY:
            raise ValueError("La clé API n'est pas configurée")

        # Création des dossiers nécessaires avec l'app_id de Config
        app_id = Config.APP_ID  # Assurez-vous d'avoir APP_ID dans votre Config
        ensure_directory_structure(app_id)

        # Décompression des fichiers
        decompress_files()

        logger.info("Pipeline terminé avec succès")

    except Exception as e:
        logger.error(f"Erreur dans le pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    run_pipeline()