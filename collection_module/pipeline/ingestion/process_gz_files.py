import os
import json
import zipfile

# Chemin vers le dossier contenant les fichiers compressés
output_folder = "data/raw/output_data/"

# Dossier où sauvegarder les fichiers JSON décompressés
processed_folder = "data/processed/{app_id}"
os.makedirs(processed_folder, exist_ok=True)

# Parcourir tous les fichiers dans le dossier spécifié
for file_name in os.listdir(output_folder):
    if file_name.endswith(".zip"):  # Traiter uniquement les fichiers ZIP
        file_path = os.path.join(output_folder, file_name)
        print(f"Traitement du fichier ZIP : {file_name}")

        # Extraction du contenu du fichier ZIP
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(processed_folder)

        print(f"Fichiers extraits dans : {processed_folder}")

# Parcourir les fichiers JSON extraits pour traitement supplémentaire (optionnel)
for file_name in os.listdir(processed_folder):
    if file_name.endswith(".json"):
        file_path = os.path.join(processed_folder, file_name)
        print(f"Traitement du fichier JSON : {file_name}")
        with open(file_path, "r", encoding="utf-8") as json_file:
            try: 
                data = json.load(json_file)
                print(f"Contenu chargé avec succès pour {file_name}")
            except json.JSONDecodeError as e:
                print(f"Erreur de décodage JSON pour {file_name} : {e}")