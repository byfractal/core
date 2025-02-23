import os
import gzip
import json
import zipfile
import logging
import tempfile
import shutil
from pathlib import Path
from collection_module.pipeline.utils.config import Config
from collection_module.pipeline.utils.utils import get_file_type, ensure_directory_structure, setup_logging

logger = setup_logging()

def process_json_line(line, output_file):
    """Traite une ligne JSON et l'écrit dans le fichier de sortie"""
    try:
        if isinstance(line, bytes):
            line = line.decode('utf-8')
            
        json.loads(line)  # Valider le JSON
        output_file.write(line)
        if not line.endswith('\n'):
            output_file.write('\n')
    except json.JSONDecodeError:
        logger.warning("Ligne JSON invalide ignorée")
    except Exception as e:
        logger.error(f"Erreur lors du traitement de la ligne: {str(e)}")

def try_decompress_gzip(input_path, output_path):
    """Tente de décompresser un fichier comme GZIP"""
    try:
        logger.info(f"Tentative de décompression GZIP de {input_path}")
        with gzip.open(input_path, "rb") as gz_file:
            with open(output_path, "w", encoding='utf-8') as json_file:
                # Lire et décoder ligne par ligne
                content = gz_file.read().decode('utf-8')
                for line in content.splitlines():
                    if line.strip():  # Ignorer les lignes vides
                        process_json_line(line, json_file)
        logger.info(f"Décompression GZIP réussie vers {output_path}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la décompression GZIP: {str(e)}")
        return False

def try_decompress_zip(input_path, output_path):
    """Tente de décompresser un fichier comme ZIP"""
    try:
        logger.info(f"Tentative de décompression ZIP de {input_path}")
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(input_path, "r") as zip_ref:
                # Extraire dans un dossier temporaire
                zip_ref.extractall(temp_dir)
                temp_path = Path(temp_dir)
                
                # Chercher les fichiers .gz dans le dossier temporaire (récursif)
                for gz_file in temp_path.rglob("*.gz"):
                    logger.info(f"Fichier GZIP trouvé dans le ZIP: {gz_file}")
                    if try_decompress_gzip(gz_file, output_path):
                        return True
                
                # Si aucun fichier .gz n'est trouvé, chercher les fichiers .json
                for json_file in temp_path.rglob("*.json"):
                    logger.info(f"Fichier JSON trouvé dans le ZIP: {json_file}")
                    with open(json_file, 'r', encoding='utf-8') as src, \
                         open(output_path, 'w', encoding='utf-8') as dest:
                        for line in src:
                            if line.strip():
                                process_json_line(line, dest)
                        return True
                        
        logger.warning("Aucun fichier JSON ou GZIP trouvé dans le ZIP")
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de la décompression ZIP: {str(e)}")
        return False

def process_file(input_path, processed_path):
    """Traite un fichier selon son type"""
    logger.info(f"Début du traitement du fichier : {input_path}")
    logger.info(f"Dossier de destination : {processed_path}")
    
    try:
        processed_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Dossier de destination créé/vérifié : {processed_path}")
        
        output_path = processed_path / input_path.name.replace('.gz', '.json').replace('.zip', '.json')
        logger.info(f"Chemin de sortie : {output_path}")
        
        if try_decompress_gzip(input_path, output_path):
            logger.info("Décompression GZIP réussie")
            return True
        elif try_decompress_zip(input_path, output_path):
            logger.info("Décompression ZIP réussie")
            return True
        else:
            logger.error(f"Échec de la décompression pour {input_path}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors du traitement de {input_path}: {str(e)}")
        return False

def decompress_files() -> bool:
    """Décompresse les fichiers compressés du dossier raw"""
    try:
        # Vérification de la configuration
        if not Config.API_KEY or not Config.APP_ID:
            raise ValueError("Configuration incomplète (API_KEY ou APP_ID manquant)")
            
        # Obtenir les chemins des dossiers
        paths = ensure_directory_structure(Config.APP_ID)
        
        # Vérifier s'il y a des fichiers à décompresser
        raw_files = list(paths['raw'].glob('*.gz')) + list(paths['raw'].glob('*.zip'))
        if not raw_files:
            logger.warning("Aucun fichier à décompresser")
            return False
            
        # Décompresser chaque fichier
        for file_path in raw_files:
            try:
                # Créer le nom du fichier de sortie
                output_filename = f"decompressed_{file_path.stem}.json"
                output_path = paths['processed'] / output_filename
                
                # Lire les premiers octets pour identifier le type de fichier
                with open(file_path, 'rb') as f:
                    magic_bytes = f.read(2)
                
                if magic_bytes.startswith(b'\x1f\x8b'):  # Fichier GZIP
                    with gzip.open(file_path, 'rb') as f_in:
                        with open(output_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                elif magic_bytes.startswith(b'PK'):  # Fichier ZIP
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        # Prendre le premier fichier du ZIP
                        first_file = zip_ref.namelist()[0]
                        with zip_ref.open(first_file) as f_in:
                            with open(output_path, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                else:
                    raise ValueError(f"Format de fichier non supporté: {magic_bytes}")
                        
                logger.info(f"Fichier décompressé: {output_path}")
                
            except Exception as e:
                logger.error(f"Erreur lors de la décompression de {file_path}: {e}")
                continue
                
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la décompression: {e}")
        return False

if __name__ == "__main__":
    decompress_files()

    