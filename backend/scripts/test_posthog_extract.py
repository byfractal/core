#!/usr/bin/env python3
"""
Script simple pour tester l'extraction directe des données de PostHog.
Ce script permet de tester rapidement si l'accès à l'API PostHog fonctionne
sans exécuter l'ensemble des tests d'intégration.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

# Load environment variables
load_dotenv()

def check_env_vars():
    """Vérifie si les variables d'environnement nécessaires sont définies"""
    print("\n=== Variables d'environnement PostHog ===")
    required_vars = ["POSTHOG_API_KEY", "POSTHOG_PROJECT_ID", "POSTHOG_API_URL"]
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Masquer partiellement la clé API pour la sécurité
            if var == "POSTHOG_API_KEY":
                masked_value = value[:8] + "..." + value[-8:]
                print(f"✅ {var} = {masked_value}")
            else:
                print(f"✅ {var} = {value}")
        else:
            print(f"❌ {var} n'est pas défini dans le fichier .env")
            all_present = False
    
    return all_present

def make_simple_api_request():
    """Fait une simple requête à l'API PostHog pour vérifier l'accès"""
    print("\n=== Test simple de l'API PostHog ===")
    
    api_key = os.getenv("POSTHOG_API_KEY")
    project_id = os.getenv("POSTHOG_PROJECT_ID")
    api_url = os.getenv("POSTHOG_API_URL")
    
    if not all([api_key, project_id, api_url]):
        print("❌ Variables d'environnement manquantes. Test impossible.")
        return False
    
    # Vérifier si l'API est accessible
    print("Vérification de l'accès à l'API...")
    
    # URL pour vérifier les informations du projet
    url = f"{api_url}/projects/{project_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        project_data = response.json()
        print(f"✅ Connexion réussie à l'API PostHog")
        print(f"   Projet: {project_data.get('name', 'Nom non disponible')}")
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur HTTP: {e}")
        print(f"   Statut: {e.response.status_code}")
        print(f"   Réponse: {e.response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_events_api():
    """Teste l'accès aux événements via l'API PostHog"""
    print("\n=== Test de récupération des événements ===")
    
    api_key = os.getenv("POSTHOG_API_KEY")
    project_id = os.getenv("POSTHOG_PROJECT_ID")
    api_url = os.getenv("POSTHOG_API_URL")
    
    # Date de début (7 jours en arrière)
    date_from = (datetime.now() - timedelta(days=7)).isoformat()
    
    # URL pour récupérer les derniers événements
    url = f"{api_url}/projects/{project_id}/events"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"limit": 5, "date_from": date_from}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        events_data = response.json()
        results = events_data.get("results", [])
        
        print(f"✅ Récupération réussie des événements")
        print(f"   Nombre d'événements: {len(results)}")
        
        if results:
            print("\n   Exemple d'événement:")
            sample = results[0]
            print(f"   - Type: {sample.get('event', 'N/A')}")
            print(f"   - Date: {sample.get('timestamp', 'N/A')}")
            
            if "properties" in sample and sample["properties"]:
                print("   - Propriétés disponibles:")
                for key in list(sample["properties"].keys())[:5]:  # Limiter à 5 propriétés
                    print(f"     - {key}")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur HTTP: {e}")
        print(f"   Statut: {e.response.status_code}")
        print(f"   Réponse: {e.response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_session_recordings_api():
    """Teste l'accès aux enregistrements de session via l'API PostHog"""
    print("\n=== Test de récupération des enregistrements de session ===")
    
    api_key = os.getenv("POSTHOG_API_KEY")
    project_id = os.getenv("POSTHOG_PROJECT_ID")
    api_url = os.getenv("POSTHOG_API_URL")
    
    # Date de début (30 jours en arrière)
    date_from = (datetime.now() - timedelta(days=30)).isoformat()
    
    # URL pour récupérer les enregistrements de session
    url = f"{api_url}/projects/{project_id}/session_recordings"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"limit": 5, "date_from": date_from}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        recordings_data = response.json()
        results = recordings_data.get("results", [])
        
        print(f"✅ Récupération réussie des enregistrements de session")
        print(f"   Nombre d'enregistrements: {len(results)}")
        
        if results:
            print("\n   Exemple d'enregistrement:")
            sample = results[0]
            print(f"   - ID: {sample.get('id', 'N/A')}")
            print(f"   - Durée: {sample.get('duration', 'N/A')}")
            print(f"   - Date: {sample.get('start_time', 'N/A')}")
            
            if "person" in sample and sample["person"]:
                person = sample["person"]
                print(f"   - Personne: {person.get('name', 'N/A')}")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur HTTP: {e}")
        print(f"   Statut: {e.response.status_code}")
        print(f"   Réponse: {e.response.text}")
        
        if e.response.status_code == 403:
            print("\n⚠️ Erreur 403 Forbidden - Vérifiez que votre clé API a les permissions nécessaires")
            print("   Vous devez avoir la permission 'View recordings' dans PostHog")
        
        return False
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def print_summary(results):
    """Affiche un résumé des résultats des tests"""
    print("\n=======================================")
    print("RÉSUMÉ DES TESTS")
    print("=======================================")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    
    for test, result in results.items():
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{status} - {test}")
    
    print("\n---------------------------------------")
    print(f"Total des tests: {total}")
    print(f"Réussis: {passed}")
    print(f"Échoués: {failed}")
    print("---------------------------------------")
    
    if failed == 0:
        print("🎉 Tous les tests ont réussi!")
    else:
        print(f"⚠️ {failed} test(s) ont échoué. Vérifiez les erreurs ci-dessus.")

def run_all_tests():
    """Exécute tous les tests"""
    results = {}
    
    # Vérifier les variables d'environnement
    results["Vérification des variables d'environnement"] = check_env_vars()
    
    # Si les variables sont manquantes, arrêter les tests
    if not results["Vérification des variables d'environnement"]:
        print("\n❌ Variables d'environnement manquantes. Impossible de continuer les tests.")
        print_summary(results)
        return
    
    # Test de base de l'API
    results["Test de connexion à l'API"] = make_simple_api_request()
    
    # Si le test de base échoue, arrêter les autres tests
    if not results["Test de connexion à l'API"]:
        print("\n❌ Impossible de se connecter à l'API PostHog. Arrêt des tests.")
        print_summary(results)
        return
    
    # Tester l'API des événements
    results["Test de l'API des événements"] = test_events_api()
    
    # Tester l'API des enregistrements de session
    results["Test de l'API des enregistrements de session"] = test_session_recordings_api()
    
    # Afficher le résumé
    print_summary(results)

if __name__ == "__main__":
    print("====================================")
    print("TEST D'EXTRACTION POSTHOG")
    print("====================================")
    run_all_tests() 