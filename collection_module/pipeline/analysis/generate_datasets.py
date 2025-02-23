import os
import csv
import random
import uuid

# Chemin vers le dossier où stocker le dataset
datasets_folder = "datasets"
os.makedirs(datasets_folder, exist_ok=True)

# Chemin du fichier de dataset généré
file_path = os.path.join(datasets_folder, "survey.csv")

# Liste des langues, plateformes, et genres fictifs
languages = ["en", "fr", "es", "de"]
platforms = ["Desktop", "Mobile", "Tablet"]
genders = ["male", "female", "non-binary"]

# Générer les données fictives
def generate_survey_data(num_entries=100):
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Ecrire l'entête
        header = [
            "user_id", "language", "platform", "gender", "age",
            "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10",
            "q11", "q12", "q13", "q14", "q15", "q16", "q17", "q18", "q19",
            "q20", "q21", "q22", "q23", "q24", "q25", "q26"
        ]
        writer.writerow(header)
        
        # Générer des réponses fictives
        for _ in range(num_entries):
            row = [
                str(uuid.uuid4()),  # user_id
                random.choice(languages),
                random.choice(platforms),
                random.choice(genders),
                random.randint(18, 65)  # age
            ] + [random.randint(1, 10) for _ in range(26)]  # Réponse aléato (1 à 10)
            writer.writerow(row)

    print(f"Fichier généré : {file_path}")

# Générer un dataset fictif
generate_survey_data(100)