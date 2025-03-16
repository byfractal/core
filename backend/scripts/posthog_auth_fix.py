#!/usr/bin/env python3
"""
Script pour tester et fixer les problèmes d'authentification avec l'API PostHog.
Ce script vérifie différentes méthodes d'authentification et affiche des conseils
pour résoudre les problèmes d'accès aux replays de session.
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv, set_key
from datetime import datetime, timedelta

# Ajouter le répertoire parent au chemin Python
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

# Charger les variables d'environnement
load_dotenv()

def verify_env_variables():
    """Vérifie les variables d'environnement PostHog et affiche leur état"""
    print("\n=== Variables d'environnement PostHog actuelles ===")
    
    api_key = os.getenv("POSTHOG_API_KEY")
    project_id = os.getenv("POSTHOG_PROJECT_ID")
    api_url = os.getenv("POSTHOG_API_URL")
    
    print(f"API URL: {api_url}")
    print(f"Project ID: {project_id}")
    
    # Masquer partiellement la clé API pour la sécurité
    if api_key:
        masked_key = api_key[:6] + "..." + api_key[-4:]
        print(f"API Key: {masked_key}")
    else:
        print("API Key: Non définie")
    
    # Vérifier si toutes les variables nécessaires sont définies
    if not all([api_key, project_id, api_url]):
        print("\n❌ Configuration incomplète: certaines variables d'environnement sont manquantes")
        return False
    
    return True

def test_personal_api_key():
    """Teste l'authentification avec la clé API personnelle"""
    print("\n=== Test d'authentification avec la clé API personnelle ===")
    
    api_key = os.getenv("POSTHOG_API_KEY")
    project_id = os.getenv("POSTHOG_PROJECT_ID")
    api_url = os.getenv("POSTHOG_API_URL")
    
    # Vérifier le projet
    url = f"{api_url}/projects/{project_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        project_data = response.json()
        print(f"✅ Authentification réussie à l'API PostHog")
        print(f"   Projet: {project_data.get('name', 'Nom non disponible')}")
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur d'authentification: {e}")
        print(f"   Statut: {e.response.status_code}")
        print(f"   Réponse: {e.response.text}")
        
        if e.response.status_code == 401:
            print("\n⚠️ La clé API est invalide ou a expiré.")
            print("   Veuillez vérifier que vous utilisez une clé API personnelle valide depuis les paramètres de PostHog.")
        
        return False
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_project_api_key():
    """Teste l'authentification avec une clé API de projet"""
    print("\n=== Test d'authentification alternative avec clé API de projet ===")
    
    api_key = os.getenv("POSTHOG_PROJECT_API_KEY", os.getenv("POSTHOG_API_KEY"))
    project_id = os.getenv("POSTHOG_PROJECT_ID")
    api_url = os.getenv("POSTHOG_API_URL")
    
    # Utiliser un format d'authentification différent pour les clés de projet
    url = f"{api_url}/projects/{project_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        project_data = response.json()
        print(f"✅ Authentification réussie avec la clé API de projet")
        print(f"   Projet: {project_data.get('name', 'Nom non disponible')}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_session_recording_access():
    """Teste spécifiquement l'accès aux enregistrements de session"""
    print("\n=== Test d'accès aux enregistrements de session ===")
    
    api_key = os.getenv("POSTHOG_API_KEY")
    project_id = os.getenv("POSTHOG_PROJECT_ID")
    api_url = os.getenv("POSTHOG_API_URL")
    
    # Date de 7 jours en arrière
    date_from = (datetime.now() - timedelta(days=7)).isoformat()
    
    # URL pour les enregistrements de session
    url = f"{api_url}/projects/{project_id}/session_recordings"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"limit": 1, "date_from": date_from}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        recordings = response.json()
        count = len(recordings.get("results", []))
        
        print(f"✅ Accès réussi aux enregistrements de session")
        print(f"   {count} enregistrements trouvés dans les 7 derniers jours")
        
        if count == 0:
            print("   ⚠️ Aucun enregistrement trouvé dans la période spécifiée.")
            print("      Cela peut être normal si aucune session n'a été enregistrée récemment.")
            print("      Essayez d'augmenter la plage de dates ou vérifiez que le recording est bien activé.")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur d'accès aux enregistrements: {e}")
        print(f"   Statut: {e.response.status_code}")
        print(f"   Réponse: {e.response.text}")
        
        if e.response.status_code == 403:
            print("\n⚠️ Erreur 403 Forbidden - Problème de permissions")
            print("   Votre clé API n'a pas les permissions nécessaires pour accéder aux enregistrements.")
            print("   Vérifiez que vous avez les permissions 'View recordings' dans les paramètres de projet.")
            print("   Si vous utilisez une clé personnelle, vérifiez que vous êtes bien administrateur du projet.")
        
        return False
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def update_api_key():
    """Permet à l'utilisateur de mettre à jour la clé API PostHog"""
    print("\n=== Mise à jour de la clé API PostHog ===")
    
    current_key = os.getenv("POSTHOG_API_KEY", "")
    masked_current = current_key[:6] + "..." + current_key[-4:] if current_key else "Non définie"
    
    print(f"Clé API actuelle: {masked_current}")
    print("\nPour créer une nouvelle clé API personnelle dans PostHog:")
    print("1. Connectez-vous à votre compte PostHog")
    print("2. Allez dans 'Settings' > 'Personal API Keys'")
    print("3. Cliquez sur 'Create personal API key'")
    print("4. Donnez un nom à votre clé (ex: 'HCentric Dev')")
    print("5. Copiez la clé générée")
    
    # Demander la nouvelle clé API
    new_key = input("\nEntrez votre nouvelle clé API PostHog (ou appuyez sur Entrée pour conserver l'actuelle): ").strip()
    
    # Si l'utilisateur a entré une nouvelle clé
    if new_key:
        # Trouver le chemin du fichier .env
        env_path = Path(os.path.join(os.getcwd(), '..', '.env'))
        if not env_path.exists():
            env_path = Path(os.path.join(os.getcwd(), '.env'))
        
        if env_path.exists():
            # Mettre à jour le fichier .env
            set_key(str(env_path), "POSTHOG_API_KEY", new_key)
            print(f"✅ Clé API mise à jour dans {env_path}")
            
            # Recharger les variables d'environnement
            os.environ["POSTHOG_API_KEY"] = new_key
            print("✅ Variable d'environnement mise à jour")
            
            return True
        else:
            print(f"❌ Fichier .env non trouvé à {env_path}")
            return False
    else:
        print("Aucune modification apportée à la clé API.")
        return False

def show_fallback_options():
    """Affiche les options de repli si l'accès à l'API échoue"""
    print("\n=== Options de développement sans accès aux replays ===")
    
    print("Si vous ne pouvez pas accéder aux replays de PostHog, vous pouvez:")
    print("1. Créer des données de test simulées pour le développement")
    print("2. Mettre en place un mode de développement qui utilise des données fictives")
    print("3. Utiliser des captures d'écran statiques pour les tests de mise en page")
    
    print("\nPour implémenter le mode de développement avec données simulées:")
    print("- Ajoutez une variable POSTHOG_USE_MOCK_DATA=true dans votre .env")
    print("- Dans la classe PostHogClient, modifiez les méthodes pour retourner des données simulées quand cette variable est activée")

def run_tests():
    """Exécute tous les tests d'authentification et d'accès"""
    results = {}
    
    # Vérifier les variables d'environnement
    env_vars_ok = verify_env_variables()
    results["Variables d'environnement"] = env_vars_ok
    
    if not env_vars_ok:
        print("\n❌ Variables d'environnement incomplètes. Veuillez les configurer avant de continuer.")
        return results
    
    # Tester l'authentification avec la clé API personnelle
    results["Authentification API"] = test_personal_api_key()
    
    # Tester l'accès aux enregistrements de session
    results["Accès aux replays"] = test_session_recording_access()
    
    # Si l'authentification a échoué, essayer avec une clé de projet
    if not results["Authentification API"]:
        results["Authentification alternative"] = test_project_api_key()
    
    return results

def print_summary(results):
    """Affiche un résumé des résultats des tests"""
    print("\n=======================================")
    print("RÉSUMÉ DES TESTS")
    print("=======================================")
    
    for test, result in results.items():
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{status} - {test}")
    
    # Vérifier si tous les tests ont réussi
    if all(results.values()):
        print("\n🎉 Tous les tests ont réussi! Vous pouvez accéder aux données de PostHog.")
        return True
    else:
        print("\n⚠️ Certains tests ont échoué. Des actions sont nécessaires.")
        return False

def suggest_fixes(results):
    """Suggère des corrections basées sur les résultats des tests"""
    if not results.get("Variables d'environnement", False):
        print("\n1. Vous devez d'abord configurer toutes les variables d'environnement:")
        print("   - POSTHOG_API_KEY: Votre clé API personnelle")
        print("   - POSTHOG_PROJECT_ID: L'ID de votre projet PostHog")
        print("   - POSTHOG_API_URL: L'URL de l'API (généralement https://app.posthog.com/api)")
    
    if not results.get("Authentification API", False):
        print("\n2. Problème d'authentification:")
        print("   - Vérifiez que votre clé API est valide et n'a pas expiré")
        print("   - Générez une nouvelle clé API personnelle si nécessaire")
    
    if not results.get("Accès aux replays", False):
        print("\n3. Problème d'accès aux replays:")
        print("   - Vérifiez que l'enregistrement des sessions est activé dans votre projet")
        print("   - Assurez-vous que votre compte a les permissions pour voir les enregistrements")
        print("   - Si vous utilisez une clé de projet, elle doit avoir la permission 'View recordings'")
    
    # Offrir d'autres options si les tests continuent d'échouer
    print("\nSi les problèmes persistent après avoir essayé les solutions ci-dessus:")
    print("- Essayez une autre clé API (de projet ou personnelle)")
    print("- Contactez votre administrateur PostHog pour vérifier les permissions")
    print("- Considérez l'utilisation de données simulées pour le développement (voir ci-dessous)")

if __name__ == "__main__":
    print("==========================================")
    print("DIAGNOSTIC D'AUTHENTIFICATION POSTHOG")
    print("==========================================")
    
    # Exécuter les tests
    results = run_tests()
    
    # Afficher le résumé
    all_passed = print_summary(results)
    
    # Si certains tests ont échoué, proposer des solutions
    if not all_passed:
        suggest_fixes(results)
        
        # Demander si l'utilisateur souhaite mettre à jour la clé API
        update_choice = input("\nSouhaitez-vous mettre à jour votre clé API PostHog? (o/n): ").lower()
        if update_choice == 'o' or update_choice == 'oui':
            update_api_key()
            print("\nVeuillez exécuter ce script à nouveau pour vérifier si le problème est résolu.")
        
        # Montrer les options de repli
        show_fallback_options()
    
    print("\n==========================================") 