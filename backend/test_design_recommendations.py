#!/usr/bin/env python3
"""
Script de test pour vérifier le fonctionnement du système de recommandations de design
avec les données simulées de PostHog.
"""

import os
import sys
import json
from pathlib import Path

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports des classes nécessaires
from models.design_recommendations import PostHogClient, DesignRecommendationChain, DesignSuggestionGenerator

def test_posthog_client():
    """Test la récupération des données depuis PostHog (mode simulation)"""
    print("\n=== Test du client PostHog ===")
    
    client = PostHogClient()
    print(f"Mode simulation actif: {client.use_mock_data}")
    
    # Tester la récupération des sessions
    sessions = client.get_sessions_for_page("/login")
    print(f"Sessions trouvées pour /login: {len(sessions)}")
    
    # Tester la récupération des feedbacks
    feedback = client.get_feedback_for_page("/login")
    print(f"Feedbacks trouvés pour /login: {len(feedback)}")
    
    if len(sessions) > 0:
        print(f"Exemple de session: {sessions[0]['id']}")
    
    if len(feedback) > 0:
        print(f"Exemple de feedback: {feedback[0].get('message', 'N/A')}")
    
    return sessions, feedback

def test_design_suggestions():
    """Test la génération de suggestions de design"""
    print("\n=== Test du générateur de suggestions de design ===")
    
    generator = DesignSuggestionGenerator()
    suggestions = generator.generate_layout_suggestions("/login")
    
    print(f"Suggestions générées:")
    for category, items in suggestions.items():
        print(f"- {category}: {len(items)} suggestions")
    
    return suggestions

def test_design_recommendations():
    """Test la génération de recommandations détaillées par le LLM"""
    print("\n=== Test de la chaîne de recommandations de design ===")
    
    # Créer une analyse simulée
    analysis = {
        "summary": "Les utilisateurs ont des difficultés à se connecter à l'application. Les principaux problèmes signalés sont la visibilité du bouton de connexion et la clarté des messages d'erreur.",
        "key_issues": [
            "Bouton de connexion peu visible",
            "Messages d'erreur confus",
            "Champ de mot de passe sans indicateur de force"
        ],
        "positive_aspects": [
            "Interface épurée",
            "Chargement rapide de la page"
        ],
        "overall_sentiment": "Majoritairement négatif concernant le processus de connexion",
        "priority_recommendations": [
            "Améliorer la visibilité du bouton de connexion",
            "Clarifier les messages d'erreur",
            "Ajouter un indicateur de force du mot de passe"
        ]
    }
    
    # Générer les recommandations
    chain = DesignRecommendationChain()
    print("Génération des recommandations...")
    recommendations = chain.generate_recommendations(analysis, "/login")
    
    print("✅ Recommandations générées")
    print(f"Nombre de recommandations: {len(recommendations.get('recommendations', []))}")
    
    # Afficher les titres des recommandations
    for rec in recommendations.get("recommendations", []):
        print(f"- {rec.get('title')}: {rec.get('priority', 'N/A')}")
    
    return recommendations

if __name__ == "__main__":
    print("==========================================")
    print("TEST DU SYSTÈME DE RECOMMANDATIONS DE DESIGN")
    print("==========================================")
    
    # Tester le client PostHog
    sessions, feedback = test_posthog_client()
    
    # Tester le générateur de suggestions
    suggestions = test_design_suggestions()
    
    # Tester la chaîne de recommandations
    recommendations = test_design_recommendations()
    
    print("\n==========================================")
    print("TESTS TERMINÉS")
    print("==========================================") 