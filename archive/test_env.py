from dotenv import load_dotenv
import os
from pathlib import Path

# Charge les variables d'environnement
load_dotenv()

# Vérifie si les variables d'environnement sont correctement chargées
print("Variables d'environnement chargées :", os.environ.keys())

# Vérifie les chemins utilisés dans ton code
base_path = Path(os.getenv("BASE_PATH"))
print("base_path :", base_path)

# Vérifie si la variable est None avant de l'utiliser
if base_path is not None:
    full_path = base_path / "subfolder"
    print("full_path :", full_path)
else:
    print("base_path est None")

print("API_KEY:", os.getenv("API_KEY")) 