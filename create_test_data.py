import json
from pathlib import Path

# Créer le dossier processed s'il n'existe pas
processed_dir = Path("data/amplitude_data/processed")
processed_dir.mkdir(parents=True, exist_ok=True)

# Créer des données de test
test_data = [
    {
        "user_id": "user_123",
        "event_type": "feedback",
        "event_properties": {
            "feedback_text": "Le design est confus, trop d'informations",
            "page": "/dashboard",
            "rating": 2
        },
        "user_properties": {
            "plan": "premium"
        },
        "time": 1623754800000
    },
    {
        "user_id": "user_456",
        "event_type": "feedback",
        "event_properties": {
            "feedback_text": "J'adore la nouvelle interface, très intuitive",
            "page": "/home",
            "rating": 5
        },
        "user_properties": {
            "plan": "basic"
        },
        "time": 1623841200000
    }
]

# Sauvegarder dans un fichier
with open(processed_dir / "test_feedback.json", "w") as f:
    json.dump(test_data, f, indent=2)

print(f"Fichier test créé: {processed_dir}/test_feedback.json") 