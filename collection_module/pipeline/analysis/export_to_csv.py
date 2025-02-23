import os
import json
import pandas as pd

filtered_folder = "data/filtered"
output_csv = "data/events_summary.csv"

# Liste pour stocker tous les événements
all_events = []

for file_name in os.listdir(filtered_folder):
    if file_name.endswith(".json"):
        file_path = os.path.join(filtered_folder, file_name)
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
            all_events.extend(data)

# Convertir la DataFrame et Convertir en CSV
df = pd.DataFrame(all_events)
df.to_csv(output_csv, index=False)
print(f"Données exportées dans {output_csv}")
