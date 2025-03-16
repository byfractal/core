#!/usr/bin/env python3
"""
Script pour générer des données simulées de PostHog.
Permet de travailler sur le développement sans avoir besoin d'un accès
complet aux données de replay de PostHog.
"""

import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Ajouter le répertoire parent au chemin Python
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

# Structure pour simuler les pages du site
SAMPLE_PAGES = [
    "/dashboard",
    "/login",
    "/signup",
    "/profile",
    "/settings",
    "/products",
    "/checkout",
    "/payment",
    "/confirmation"
]

# Structure pour simuler des éléments DOM
SAMPLE_DOM_ELEMENTS = [
    {"selector": "button.login-button", "name": "Login Button", "type": "button"},
    {"selector": "input#email", "name": "Email Input", "type": "input"},
    {"selector": "input#password", "name": "Password Input", "type": "input"},
    {"selector": "button.submit-button", "name": "Submit Button", "type": "button"},
    {"selector": "div.product-card", "name": "Product Card", "type": "div"},
    {"selector": "a.navigation-link", "name": "Navigation Link", "type": "a"},
    {"selector": "select#country", "name": "Country Dropdown", "type": "select"},
    {"selector": "form.checkout-form", "name": "Checkout Form", "type": "form"},
    {"selector": "img.product-image", "name": "Product Image", "type": "img"},
    {"selector": "button.add-to-cart", "name": "Add to Cart Button", "type": "button"}
]

def generate_mock_session_id():
    """Génère un ID de session aléatoire au format UUID"""
    return str(uuid.uuid4())

def generate_mock_event(timestamp, page, session_id):
    """Génère un événement simulé"""
    event_types = ["$pageview", "$click", "$change", "$submit", "$focus", "$blur", "$scroll"]
    event_type = random.choice(event_types)
    
    # Créer les propriétés de l'événement
    properties = {
        "path": page,
        "url": f"https://example.com{page}",
        "browser": random.choice(["Chrome", "Firefox", "Safari"]),
        "os": random.choice(["Windows", "MacOS", "Linux"]),
        "device": random.choice(["Desktop", "Mobile", "Tablet"]),
        "session_id": session_id
    }
    
    # Ajouter des propriétés spécifiques selon le type d'événement
    if event_type == "$click":
        element = random.choice(SAMPLE_DOM_ELEMENTS)
        properties.update({
            "element": element["selector"],
            "element_name": element["name"],
            "positionX": random.randint(10, 1200),
            "positionY": random.randint(10, 800)
        })
    elif event_type == "$scroll":
        properties.update({
            "scrollX": random.randint(0, 100),
            "scrollY": random.randint(-300, 300)
        })
    
    return {
        "id": str(uuid.uuid4()),
        "type": event_type,
        "timestamp": timestamp.isoformat(),
        "properties": properties
    }

def generate_mock_session(start_date=None, duration_minutes=None, pages=None):
    """Génère une session simulée complète avec des événements"""
    if start_date is None:
        # Générer une date de début aléatoire dans les 30 derniers jours
        days_ago = random.randint(0, 30)
        start_date = datetime.now() - timedelta(days=days_ago)
    
    if duration_minutes is None:
        duration_minutes = random.randint(2, 45)  # Entre 2 et 45 minutes
    
    if pages is None:
        # Choisir un nombre aléatoire de pages à visiter
        page_count = random.randint(1, 5)
        pages = random.sample(SAMPLE_PAGES, page_count)
    
    session_id = generate_mock_session_id()
    
    # Générer les propriétés de base de la session
    session = {
        "id": session_id,
        "start_time": start_date.isoformat(),
        "end_time": (start_date + timedelta(minutes=duration_minutes)).isoformat(),
        "duration": duration_minutes * 60,  # En secondes
        "pages": [],
        "events": []
    }
    
    # Générer les pages visitées
    for i, page in enumerate(pages):
        page_start = start_date + timedelta(minutes=i * (duration_minutes / len(pages)))
        page_duration = random.randint(30, 300)  # Entre 30 secondes et 5 minutes
        
        session["pages"].append({
            "url": f"https://example.com{page}",
            "path": page,
            "time": page_start.isoformat(),
            "duration": page_duration
        })
        
        # Générer entre 5 et 20 événements pour cette page
        event_count = random.randint(5, 20)
        for j in range(event_count):
            event_time = page_start + timedelta(seconds=random.randint(0, page_duration))
            event = generate_mock_event(event_time, page, session_id)
            session["events"].append(event)
    
    # Trier les événements par timestamp
    session["events"].sort(key=lambda x: x["timestamp"])
    
    return session

def generate_mock_feedback(page_id, sentiment=None, date=None):
    """Génère un feedback utilisateur simulé"""
    if sentiment is None:
        sentiment = random.choice(["positive", "negative", "neutral"])
    
    if date is None:
        days_ago = random.randint(0, 30)
        date = datetime.now() - timedelta(days=days_ago)
    
    # Simuler différents types de feedback selon le sentiment
    feedback_templates = {
        "positive": [
            "J'adore cette interface, c'est très intuitif!",
            "Facile à utiliser et bien conçu.",
            "Excellent design, c'est exactement ce dont j'avais besoin.",
            "Super expérience, je recommande vivement!"
        ],
        "negative": [
            "Cette page est confuse, je ne sais pas où cliquer.",
            "Trop d'informations, c'est difficile à comprendre.",
            "Le bouton de soumission est difficile à trouver.",
            "L'interface est trop lente et compliquée."
        ],
        "neutral": [
            "C'est correct, mais pourrait être amélioré.",
            "Fonctionnel mais pas exceptionnel.",
            "Ça fait le travail, mais j'ai vu mieux.",
            "Ni bon ni mauvais, juste moyen."
        ]
    }
    
    text = random.choice(feedback_templates[sentiment])
    rating = 5 if sentiment == "positive" else (2 if sentiment == "negative" else 3)
    
    return {
        "id": str(uuid.uuid4()),
        "event": "feedback_submitted",
        "timestamp": date.isoformat(),
        "properties": {
            "page": page_id,
            "text": text,
            "rating": rating,
            "sentiment": sentiment
        }
    }

def generate_mock_sessions_for_page(page_id, count=10):
    """Génère plusieurs sessions simulées pour une page spécifique"""
    sessions = []
    
    for _ in range(count):
        # Générer une session qui inclut la page spécifiée
        other_pages = random.sample([p for p in SAMPLE_PAGES if p != page_id], 
                                   k=random.randint(0, 3))
        pages = [page_id] + other_pages
        random.shuffle(pages)
        
        session = generate_mock_session(pages=pages)
        sessions.append(session)
    
    return sessions

def generate_mock_feedback_for_page(page_id, count=5):
    """Génère plusieurs feedbacks simulés pour une page spécifique"""
    feedbacks = []
    
    # Répartir les sentiments pour être réalistes
    sentiments = ["positive"] * 2 + ["negative"] * 2 + ["neutral"] * 1
    random.shuffle(sentiments)
    
    # Si count > len(sentiments), nous répétons les sentiments
    sentiments = (sentiments * (count // len(sentiments) + 1))[:count]
    
    for sentiment in sentiments:
        feedback = generate_mock_feedback(page_id, sentiment)
        feedbacks.append(feedback)
    
    return feedbacks

def generate_confusion_areas(page_id):
    """Génère des zones de confusion simulées pour une page"""
    confusion_areas = []
    
    # Simuler quelques zones problématiques
    potential_areas = [
        {"area": "checkout_form", "base_score": 0.8, "type": "multiple_clicks"},
        {"area": "navigation_menu", "base_score": 0.4, "type": "rapid_scrolling"},
        {"area": "search_field", "base_score": 0.6, "type": "multiple_clicks"},
        {"area": "filter_options", "base_score": 0.5, "type": "rapid_scrolling"},
        {"area": "product_selection", "base_score": 0.7, "type": "multiple_clicks"}
    ]
    
    # Sélectionner aléatoirement 2-3 zones pour la page
    selected_areas = random.sample(potential_areas, k=random.randint(2, 3))
    
    for area in selected_areas:
        # Ajouter une variation aléatoire au score
        score_variation = random.uniform(-0.1, 0.1)
        final_score = max(0.1, min(0.9, area["base_score"] + score_variation))
        
        confusion_areas.append({
            "area": area["area"],
            "score": round(final_score, 2),
            "type": area["type"]
        })
    
    return confusion_areas

def generate_heatmap_data():
    """Génère des données de heatmap simulées"""
    heatmap_data = []
    
    # Générer 50 points de clic
    for _ in range(50):
        x = random.randint(50, 1200)
        y = random.randint(50, 800)
        value = random.randint(1, 10)  # Intensité du clic
        
        heatmap_data.append({
            "x": x,
            "y": y,
            "value": value
        })
    
    return heatmap_data

def save_mock_data(data, filename):
    """Sauvegarde les données simulées dans un fichier JSON"""
    output_dir = Path(os.path.join(parent_dir, "mock_data"))
    output_dir.mkdir(exist_ok=True)
    
    file_path = output_dir / filename
    
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Données simulées sauvegardées dans {file_path}")
    return file_path

def generate_all_mock_data():
    """Génère un ensemble complet de données simulées pour le développement"""
    mock_data = {}
    
    print("Génération de données simulées pour PostHog...")
    
    # Générer des sessions pour chaque page
    all_sessions = []
    for page in SAMPLE_PAGES:
        print(f"Génération de sessions pour la page {page}...")
        page_sessions = generate_mock_sessions_for_page(page, count=5)
        all_sessions.extend(page_sessions)
    
    mock_data["sessions"] = all_sessions
    
    # Générer des feedbacks pour chaque page
    all_feedbacks = []
    for page in SAMPLE_PAGES:
        print(f"Génération de feedbacks pour la page {page}...")
        page_feedbacks = generate_mock_feedback_for_page(page, count=3)
        all_feedbacks.extend(page_feedbacks)
    
    mock_data["feedbacks"] = all_feedbacks
    
    # Générer des zones de confusion pour chaque page
    confusion_areas = {}
    for page in SAMPLE_PAGES:
        confusion_areas[page] = generate_confusion_areas(page)
    
    mock_data["confusion_areas"] = confusion_areas
    
    # Générer des données de heatmap
    mock_data["heatmaps"] = {page: generate_heatmap_data() for page in SAMPLE_PAGES}
    
    # Enregistrer toutes les données dans un fichier
    file_path = save_mock_data(mock_data, "posthog_mock_data.json")
    
    print(f"\n🎉 Génération de données simulées terminée! Fichier: {file_path}")
    print("Vous pouvez maintenant utiliser ces données pour le développement sans accès à PostHog.")
    
    return file_path

def setup_mock_mode():
    """Configure le mode simulation dans le fichier .env"""
    print("\n=== Configuration du mode simulation pour PostHog ===")
    
    # Trouver le fichier .env
    env_path = Path(os.path.join(os.getcwd(), '..', '.env'))
    if not env_path.exists():
        env_path = Path(os.path.join(os.getcwd(), '.env'))
    
    if not env_path.exists():
        print("❌ Fichier .env non trouvé. Impossible de configurer le mode simulation.")
        return False
    
    # Vérifier si la variable existe déjà
    from dotenv import set_key, dotenv_values
    env_vars = dotenv_values(env_path)
    current_value = env_vars.get("POSTHOG_USE_MOCK_DATA", "false")
    
    # Demander confirmation pour activer le mode simulation
    print(f"Mode simulation actuellement {'activé' if current_value.lower() == 'true' else 'désactivé'}")
    choice = input("Souhaitez-vous activer le mode simulation? (o/n): ").lower()
    
    if choice == 'o' or choice == 'oui':
        # Activer le mode simulation
        set_key(str(env_path), "POSTHOG_USE_MOCK_DATA", "true")
        
        # Générer les données simulées si elles n'existent pas
        mock_data_path = Path(os.path.join(parent_dir, "mock_data", "posthog_mock_data.json"))
        if not mock_data_path.exists():
            print("Données simulées non trouvées. Génération en cours...")
            generate_all_mock_data()
        else:
            print(f"✅ Données simulées existantes trouvées: {mock_data_path}")
        
        print("✅ Mode simulation activé. Les appels à PostHog utiliseront des données simulées.")
        return True
    else:
        if current_value.lower() == 'true':
            set_key(str(env_path), "POSTHOG_USE_MOCK_DATA", "false")
            print("✅ Mode simulation désactivé. Les appels à PostHog utiliseront l'API réelle.")
        else:
            print("Mode simulation non modifié.")
        return False

if __name__ == "__main__":
    print("==========================================")
    print("GÉNÉRATEUR DE DONNÉES POSTHOG SIMULÉES")
    print("==========================================")
    
    # Menu principal
    print("\nQue souhaitez-vous faire?")
    print("1. Générer des données simulées pour le développement")
    print("2. Configurer le mode simulation dans .env")
    print("3. Générer des données et configurer le mode simulation")
    print("4. Quitter")
    
    choice = input("\nEntrez votre choix (1-4): ")
    
    if choice == "1":
        generate_all_mock_data()
    elif choice == "2":
        setup_mock_mode()
    elif choice == "3":
        generate_all_mock_data()
        setup_mock_mode()
    else:
        print("Au revoir!")
    
    print("\n==========================================") 