# Tests d'intégration PostHog

Ce répertoire contient les tests d'intégration pour vérifier la fonctionnalité de l'API PostHog et les fonctionnalités associées aux recommandations de design.

## Configuration des tests

Avant d'exécuter les tests, assurez-vous que les variables d'environnement suivantes sont configurées dans votre fichier `.env` à la racine du projet :

```
POSTHOG_API_KEY=your_api_key
POSTHOG_PROJECT_ID=your_project_id
POSTHOG_API_URL=https://app.posthog.com/api
POSTHOG_FEEDBACK_EVENT=feedback_submitted  # Nom de l'événement de feedback (optionnel)
```

## Exécution des tests

Pour exécuter tous les tests d'intégration PostHog :

```bash
cd backend
python -m tests.test_posthog_integration
```

Pour exécuter un test spécifique, vous pouvez modifier le fichier `test_posthog_integration.py` et appeler directement la fonction de test souhaitée au lieu de `run_all_tests()`.

## Tests disponibles

Le script de test `test_posthog_integration.py` comprend les tests suivants :

1. `test_posthog_connection()` - Vérifie la connexion de base à l'API PostHog
2. `test_fetch_sessions()` - Teste la récupération des enregistrements de session
3. `test_download_session_data()` - Teste le téléchargement des données détaillées d'une session
4. `test_page_specific_sessions()` - Teste la récupération des sessions pour une page spécifique
5. `test_feedback_retrieval()` - Teste la récupération des événements de feedback
6. `test_design_suggestion_generation()` - Teste la génération de suggestions de design
7. `test_design_recommendation_chain()` - Teste la chaîne de recommandation de design avec un LLM

## Adaptation des tests à votre environnement

Certains tests utilisent des valeurs par défaut qui peuvent ne pas correspondre à votre environnement :

- Dans `test_page_specific_sessions()` et `test_design_suggestion_generation()`, remplacez `/dashboard` par un chemin de page qui existe dans votre application.
- Le test `test_design_recommendation_chain()` utilise par défaut le modèle `gpt-3.5-turbo`. Si vous souhaitez utiliser un modèle différent, modifiez cette valeur.

## Dépannage

Si les tests échouent, vérifiez les points suivants :

1. **Clés d'API** : Assurez-vous que vos clés d'API PostHog sont correctes et ont les autorisations nécessaires.
2. **Connexion Internet** : Vérifiez votre connexion Internet car les tests font des appels d'API externes.
3. **Format des données** : Si votre implémentation de PostHog utilise un format de données différent, vous devrez peut-être adapter les fonctions de récupération et d'analyse.
4. **Limites d'API** : Si vous rencontrez des erreurs liées aux limites d'API, essayez de réduire le nombre de jours (`days`) dans les appels d'API.

## Extension des tests

Pour ajouter de nouveaux tests, suivez le modèle des fonctions de test existantes :

1. Créez une nouvelle fonction avec un nom descriptif préfixé par `test_`
2. Ajoutez des messages d'information clairs avec `print()`
3. Retournez `True` si le test réussit, `False` s'il échoue, ou `None` s'il est ignoré
4. Ajoutez votre test à la fonction `run_all_tests()` 