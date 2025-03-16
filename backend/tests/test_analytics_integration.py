#!/usr/bin/env python3
"""
Test d'intégration pour l'architecture d'analytics.
Ce script vérifie la fonctionnalité de récupération des données depuis différentes
plateformes d'analytics (PostHog, Mixpanel, Amplitude, etc.) en utilisant l'architecture unifiée.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter le répertoire parent au chemin Python
sys.path.append(str(Path(__file__).parent.parent))

from models.analytics_providers import (
    AnalyticsFactory,
    PostHogProvider,
    MixpanelProvider,
    AmplitudeProvider,
    get_configured_provider
)

def check_environment_variables():
    """Vérifie les variables d'environnement requises pour les tests."""
    print("\n=== Variables d'environnement ===")
    
    # Vérifier la configuration du fournisseur d'analytics
    provider_type = os.getenv("ANALYTICS_PROVIDER", "posthog")
    print(f"Fournisseur d'analytics configuré: {provider_type}")
    
    # Vérifier les variables spécifiques au fournisseur
    if provider_type.lower() == "posthog":
        required_vars = ["POSTHOG_API_KEY", "POSTHOG_PROJECT_ID", "POSTHOG_API_URL"]
    elif provider_type.lower() == "mixpanel":
        required_vars = ["MIXPANEL_API_KEY", "MIXPANEL_API_SECRET"]
    elif provider_type.lower() == "amplitude":
        required_vars = ["AMPLITUDE_API_KEY"]
    else:
        print(f"⚠️ Fournisseur inconnu: {provider_type}")
        return False
    
    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Masquer les clés API pour la sécurité
            if var.endswith("API_KEY") or var.endswith("SECRET"):
                masked_value = value[:5] + "..." + value[-5:] if len(value) > 10 else "***"
                print(f"✅ {var} = {masked_value}")
            else:
                print(f"✅ {var} = {value}")
        else:
            print(f"❌ {var} n'est pas défini")
            all_present = False
    
    return all_present

def test_provider_initialization():
    """Teste l'initialisation des fournisseurs d'analytics."""
    print("\n=== Test d'initialisation des fournisseurs ===")
    
    try:
        # Récupérer le fournisseur configuré
        provider = get_configured_provider()
        provider_type = os.getenv("ANALYTICS_PROVIDER", "posthog").lower()
        
        # Vérifier que le bon type de fournisseur a été créé
        if provider_type == "posthog" and isinstance(provider, PostHogProvider):
            print("✅ Fournisseur PostHog correctement initialisé")
        elif provider_type == "mixpanel" and isinstance(provider, MixpanelProvider):
            print("✅ Fournisseur Mixpanel correctement initialisé")
        elif provider_type == "amplitude" and isinstance(provider, AmplitudeProvider):
            print("✅ Fournisseur Amplitude correctement initialisé")
        else:
            print(f"❌ Type de fournisseur incorrect: {type(provider).__name__}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'initialisation du fournisseur: {e}")
        return False

def test_session_retrieval(page_id="/login", days=30):
    """
    Teste la récupération des sessions pour une page spécifique.
    
    Args:
        page_id (str): Identifiant de la page
        days (int): Nombre de jours à analyser
    """
    print(f"\n=== Test de récupération des sessions pour {page_id} ({days} jours) ===")
    
    try:
        # Récupérer le fournisseur configuré
        provider = get_configured_provider()
        
        # Calculer la plage de dates
        date_to = datetime.now().isoformat()
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Récupérer les sessions
        print("Récupération des sessions...")
        sessions = provider.get_sessions(page_id, date_from=date_from, date_to=date_to)
        
        # Afficher les informations sur les sessions récupérées
        print(f"Sessions récupérées: {len(sessions)}")
        
        if sessions:
            # Afficher des détails sur la première session
            session = sessions[0]
            session_id = session.get("id", "N/A")
            print(f"Exemple de session (ID: {session_id}):")
            
            # Afficher quelques informations pertinentes
            if "snapshots" in session:
                snapshots = session["snapshots"]
                pages = snapshots.get("pages", [])
                print(f"  Pages visitées: {len(pages)}")
                for i, page in enumerate(pages[:3], 1):
                    print(f"    {i}. {page.get('url', 'URL inconnue')}")
                if len(pages) > 3:
                    print(f"    ... et {len(pages) - 3} autres pages")
                    
            elif "pages" in session:
                pages = session["pages"]
                print(f"  Pages visitées: {len(pages)}")
                for i, page in enumerate(pages[:3], 1):
                    print(f"    {i}. {page.get('path', 'Chemin inconnu')}")
                if len(pages) > 3:
                    print(f"    ... et {len(pages) - 3} autres pages")
            
            if "events" in session:
                events = session["events"]
                print(f"  Événements: {len(events)}")
                event_types = {}
                for event in events:
                    event_type = event.get("type", "Inconnu")
                    event_types[event_type] = event_types.get(event_type, 0) + 1
                
                print("  Types d'événements:")
                for event_type, count in event_types.items():
                    print(f"    - {event_type}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des sessions: {e}")
        return False

def test_feedback_retrieval(page_id="/login", days=30):
    """
    Teste la récupération des feedbacks pour une page spécifique.
    
    Args:
        page_id (str): Identifiant de la page
        days (int): Nombre de jours à analyser
    """
    print(f"\n=== Test de récupération des feedbacks pour {page_id} ({days} jours) ===")
    
    try:
        # Récupérer le fournisseur configuré
        provider = get_configured_provider()
        
        # Calculer la plage de dates
        date_to = datetime.now().isoformat()
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Récupérer les feedbacks
        print("Récupération des feedbacks...")
        feedbacks = provider.get_user_feedback(page_id, date_from=date_from, date_to=date_to)
        
        # Afficher les informations sur les feedbacks récupérés
        print(f"Feedbacks récupérés: {len(feedbacks)}")
        
        if feedbacks:
            # Afficher des détails sur les feedbacks
            sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
            for feedback in feedbacks:
                sentiment = feedback.get("sentiment", "neutral")
                sentiment_counts[sentiment] += 1
            
            print("Répartition des sentiments:")
            for sentiment, count in sentiment_counts.items():
                print(f"  - {sentiment}: {count}")
            
            # Afficher quelques exemples de feedback
            print("\nExemples de feedbacks:")
            for i, feedback in enumerate(feedbacks[:3], 1):
                message = feedback.get("message", "Pas de message")
                sentiment = feedback.get("sentiment", "neutral")
                print(f"  {i}. {sentiment.capitalize()}: {message}")
            
            if len(feedbacks) > 3:
                print(f"  ... et {len(feedbacks) - 3} autres feedbacks")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des feedbacks: {e}")
        return False

def run_all_tests():
    """Exécute tous les tests d'intégration."""
    print("=====================================")
    print("TESTS D'INTÉGRATION ANALYTICS")
    print("=====================================")
    
    # Vérifier les variables d'environnement
    env_vars_ok = check_environment_variables()
    
    if not env_vars_ok:
        print("\n⚠️ Des variables d'environnement sont manquantes. Certains tests pourraient échouer.")
    
    # Tester l'initialisation des fournisseurs
    provider_ok = test_provider_initialization()
    
    if not provider_ok:
        print("\n❌ Impossible d'initialiser le fournisseur d'analytics. Arrêt des tests.")
        return
    
    # Tester la récupération des sessions
    sessions_ok = test_session_retrieval()
    
    # Tester la récupération des feedbacks
    feedbacks_ok = test_feedback_retrieval()
    
    # Résumé des tests
    print("\n=====================================")
    print("RÉSUMÉ DES TESTS")
    print("=====================================")
    print(f"✅ Variables d'environnement: {'OK' if env_vars_ok else 'ÉCHEC'}")
    print(f"✅ Initialisation du fournisseur: {'OK' if provider_ok else 'ÉCHEC'}")
    print(f"✅ Récupération des sessions: {'OK' if sessions_ok else 'ÉCHEC'}")
    print(f"✅ Récupération des feedbacks: {'OK' if feedbacks_ok else 'ÉCHEC'}")
    
    # Conclusion
    total_tests = 4
    passed_tests = sum([env_vars_ok, provider_ok, sessions_ok, feedbacks_ok])
    print("\n-------------------------------------")
    print(f"Total des tests: {total_tests}")
    print(f"Réussis: {passed_tests}")
    print(f"Échoués: {total_tests - passed_tests}")
    print("-------------------------------------")
    
    if passed_tests == total_tests:
        print("🎉 Tous les tests ont réussi! L'intégration avec l'API fonctionne correctement.")
    else:
        print(f"⚠️ {total_tests - passed_tests} test(s) ont échoué. Vérifiez les erreurs ci-dessus.")

if __name__ == "__main__":
    run_all_tests() 