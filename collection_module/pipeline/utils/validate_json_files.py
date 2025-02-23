import os
import json

# Chemin vers le dossier contenant les fichiers JSON décompressés
processed_folder = "data/processed"

def validate_json_file(file_path):
    """Valide le contenu JSON d'un fichier."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            json.load(file)
        print(f"✅ Fichier valide : {file_path}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Erreur dans le fichier {file_path} : {e}")
        return False

def validate_all_json_files(folder_path):
    """Parcourt et valide tous les fichiers JSON dans un dossier."""
    all_files_valid = True
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_path, file_name)
            if not validate_json_file(file_path):
                all_files_valid = False
    return all_files_valid

# Validation de tous les fichiers JSON
if __name__ == "__main__":
    if os.path.exists(processed_folder):
        if validate_all_json_files(processed_folder):
            print("\nTous les fichiers JSON sont valides.")
        else:
            print("\nCertains fichiers JSON contiennent des erreurs.")
    else:
        print(f"Le dossier {processed_folder} n'existe pas.")
