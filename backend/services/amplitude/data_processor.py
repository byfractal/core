"""
Process and format data received from Amplitude.
"""
import os
import json
import gzip
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Union, Optional

from langchain.schema import Document

# Configuration du logging
logger = logging.getLogger(__name__)

def ensure_directory_structure(app_id: str = "amplitude_data") -> Dict[str, Path]:
    """
    Crée la structure de répertoires nécessaire et retourne les chemins.
    
    Args:
        app_id: ID de l'application
        
    Returns:
        Dictionary with paths to different directories
    """
    # Définir le chemin de base depuis l'environnement ou utiliser un chemin  défaut
    base_path = os.getenv("BASE_PATH", "data")
    base_dir = Path(base_path)
    
    # Créer la structure de répertoires
    paths = {
        "base": base_dir,
        "raw": base_dir / app_id / "raw",
        "processed": base_dir / app_id / "processed",
        "exports": base_dir / app_id / "exports",
    }
    
    # S'assurer que tous les répertoires existent
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
        
    return paths

def save_data_to_file(data: bytes, filename: str, base_path: Optional[Path] = None) -> Path:
    """
    Save Amplitude data to a file.
    
    Args:
        data: Data to save
        filename: Filename to save to
        base_path: Base path to save to (defaults to data/amplitude_data/raw)
        
    Returns:
        Path to the saved file
    """
    # Créer les répertoires si nécessaire
    paths = ensure_directory_structure()
    raw_path = paths["raw"] if base_path is None else base_path
    
    try:
        file_path = raw_path / filename
        
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
        
        return file_path
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des données: {e}")
        raise

def process_raw_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Process a raw Amplitude data file.
    
    Args:
        file_path: Path to the raw file
        
    Returns:
        List of processed events
    """
    try:
        events = []
        
        # Vérifier si c'est un fichier gzip
        if file_path.suffix == ".gz":
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for line in f:
                    try:
                        event = json.loads(line)
                        events.append(event)
                    except json.JSONDecodeError:
                        logger.warning(f"Ligne ignorée: {line[:50]}...")
        else:
            # Fichier JSON normal
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    events = data
                else:
                    events = [data]
        
        logger.info(f"Traité {len(events)} événements depuis {file_path}")
        return events
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement du fichier {file_path}: {e}")
        raise

def prepare_for_vectorization(events: List[Dict[str, Any]]) -> List[Document]:
    """
    Convert Amplitude events to LangChain Documents for vectorization.
    
    Args:
        events: List of Amplitude events
        
    Returns:
        List of Document objects
    """
    documents = []
    
    for event in events:
        # Extract relevant text and metadata from the event
        # Adapter cette partie selon la structure de vos événements Amplitude
        event_properties = event.get("event_properties", {})
        text = event_properties.get("feedback", "")
        
        # Si pas de feedback, essayer d'autres champs possibles
        if not text:
            text = event_properties.get("comment", "")
        if not text:
            text = event_properties.get("text", "")
        if not text:
            continue  # Ignorer les événements sans texte
            
        metadata = {
            "event_id": event.get("event_id", ""),
            "user_id": event.get("user_id", ""),
            "device_id": event.get("device_id", ""),
            "event_type": event.get("event_type", ""),
            "time": event.get("time", ""),
            "page": event_properties.get("page", "unknown"),
            "platform": event.get("platform", ""),
            "os_name": event.get("os_name", ""),
            "device_family": event.get("device_family", "")
        }
        
        # Create a Document object
        document = Document(
            page_content=text,
            metadata=metadata
        )
        
        documents.append(document)
    
    logger.info(f"Créé {len(documents)} documents pour la vectorisation")
    return documents
