#!/usr/bin/env python
"""
Script pour synchroniser automatiquement les données d'insights entre le backend et l'extension.
Ce script:
1. Vérifie l'existence du fichier recommendations_output.json du backend
2. Le copie dans le répertoire output de l'extension
3. Recompile l'extension si webpack est disponible
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import json
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chemins relatifs des fichiers
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
BACKEND_OUTPUT_FILE = PROJECT_ROOT / "output" / "recommendations_output.json"
EXTENSION_OUTPUT_DIR = PROJECT_ROOT / "extension" / "output"
EXTENSION_OUTPUT_FILE = EXTENSION_OUTPUT_DIR / "recommendation_output.json"
WEBPACK_CONFIG = PROJECT_ROOT / "extension" / "webpack.config.js"

def check_files_exist():
    """Vérifie si les fichiers et répertoires nécessaires existent."""
    if not BACKEND_OUTPUT_FILE.exists():
        logger.error(f"Le fichier source {BACKEND_OUTPUT_FILE} n'existe pas!")
        return False
    
    if not EXTENSION_OUTPUT_DIR.exists():
        logger.warning(f"Le répertoire de destination {EXTENSION_OUTPUT_DIR} n'existe pas, création...")
        EXTENSION_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    return True

def sync_files():
    """Copie le fichier d'insights du backend vers l'extension."""
    try:
        # Lecture du fichier source
        with open(BACKEND_OUTPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Écriture dans le fichier de destination
        with open(EXTENSION_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Fichier copié avec succès: {BACKEND_OUTPUT_FILE} -> {EXTENSION_OUTPUT_FILE}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la copie du fichier: {str(e)}")
        return False

def build_extension():
    """Recompile l'extension si webpack est disponible."""
    if not WEBPACK_CONFIG.exists():
        logger.warning("Fichier webpack.config.js non trouvé, compilation ignorée.")
        return False
    
    try:
        logger.info("Compilation de l'extension en cours...")
        subprocess.run(
            ["npm", "run", "build"], 
            cwd=str(PROJECT_ROOT / "extension"),
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("Extension compilée avec succès!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de la compilation: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Erreur lors de la compilation: {str(e)}")
        return False

def main():
    """Fonction principale."""
    logger.info("Démarrage de la synchronisation des insights...")
    
    # Vérification des fichiers
    if not check_files_exist():
        return 1
    
    # Synchronisation des fichiers
    if not sync_files():
        return 1
    
    # Compilation de l'extension
    build_result = build_extension()
    if not build_result:
        logger.warning("L'extension n'a pas pu être compilée automatiquement.")
        logger.info("Pour compiler manuellement, exécutez 'cd extension && npm run build'")
    
    logger.info("Synchronisation terminée avec succès!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 