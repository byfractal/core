import os
import json
import gzip
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from collection_module.pipeline.utils.config import Config

def setup_logging():
    """Configure le système de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def ensure_directory_structure(app_id=None):
    """Crée la structure de dossiers nécessaire pour le projet"""
    # Vérifier si BASE_PATH est défini
    base_path = Config.BASE_PATH
    if base_path is None:
        # Utiliser un chemin par défaut si BASE_PATH n'est pas défini
        base_path = Path(os.path.expanduser("~")) / "Documents" / "Builds" / "hcentric_interface"
        print(f"BASE_PATH n'est pas défini, utilisation du chemin par défaut: {base_path}")
    else:
        base_path = Path(base_path)
    
    # Créer les dossiers nécessaires
    data_dir = base_path / "data"
    if app_id:
        app_dir = data_dir / app_id
    else:
        app_dir = data_dir / "default"
    
    raw_dir = app_dir / "raw"
    processed_dir = app_dir / "processed"
    
    # Créer les dossiers s'ils n'existent pas
    for directory in [data_dir, app_dir, raw_dir, processed_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    return {
        "base": base_path,
        "data": data_dir,
        "app": app_dir,
        "raw": raw_dir,
        "processed": processed_dir
    }

def get_file_type(file_path):
    """Détermine le type de fichier basé sur son contenu"""
    with open(file_path, 'rb') as f:
        magic_bytes = f.read(4)
        if magic_bytes.startswith(b'\x1f\x8b'):
            return 'gzip'
        elif magic_bytes.startswith(b'PK\x03\x04'):
            return 'zip'
        else:
            return 'unknown'

class JSONHandler:
    """Classe utilitaire pour gérer les opérations JSON"""
    
    @staticmethod
    def read(filepath: str) -> Any:
        """Lit un fichier JSON"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON dans {filepath}: {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la lecture de {filepath}: {e}")
            raise

    @staticmethod
    def write(filepath: str, data: Any, indent: int = 2) -> None:
        """Écrit des données dans un fichier JSON"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=indent)
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture dans {filepath}: {e}")
            raise

    @staticmethod
    def read_jsonl(file_path: Path) -> List[Dict[Any, Any]]:
        """Lit un fichier JSONL (peut être compressé en GZIP)"""
        try:
            # Lire les premiers octets pour vérifier si c'est un fichier GZIP
            with open(file_path, 'rb') as f:
                magic_bytes = f.read(2)
                f.seek(0)  # Retour au début du fichier
                
                if magic_bytes.startswith(b'\x1f\x8b'):  # Fichier GZIP
                    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                        return [json.loads(line) for line in f if line.strip()]
                else:  # Fichier texte normal
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return [json.loads(line) for line in f if line.strip()]
                        
        except Exception as e:
            logging.error(f"Erreur lors de la lecture JSONL de {file_path}: {e}")
            raise

    @staticmethod
    def validate_event(event: Dict, required_fields: List[str] = None) -> bool:
        """Valide qu'un événement contient tous les champs requis"""
        if not required_fields:
            return True
        return all(field in event for field in required_fields)