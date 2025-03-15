# Feedback Analysis API

Ce document décrit l'API de filtrage et d'analyse des feedbacks implémentée dans l'étape 4 du projet.

## Aperçu

L'API permet d'analyser les feedbacks utilisateurs avec un filtrage par page et par date, et expose les résultats via des endpoints RESTful.

## Architecture

L'architecture de l'API est la suivante:

```
backend/
│
├── api/
│   ├── main.py         # Point d'entrée principal de l'API FastAPI
│   └── feedback.py     # Endpoints spécifiques à l'analyse de feedback
│
├── models/
│   ├── analysis_chains.py      # Chaînes d'analyse LLM
│   └── feedback_analyzer.py    # Module d'analyse de feedback avec filtrage
│
└── scripts/
    ├── run_api.py              # Script pour lancer l'API
    ├── test_api.py             # Script pour tester les endpoints de l'API
    ├── test_feedback_analyzer.py # Script pour tester l'analyseur de feedback
    └── analyze_feedback.py     # Script mis à jour pour utiliser l'analyseur
```

## Utilisation

### Démarrer l'API

Pour démarrer l'API localement, exécutez:

```bash
python -m backend.scripts.run_api
```

L'API sera disponible sur `http://localhost:8000`.

### Endpoints disponibles

#### Endpoints généraux

- **GET /** - Information sur l'API
- **GET /health** - Vérification de l'état de santé de l'API

#### Endpoints d'analyse de feedback

- **GET /feedback/pages** - Liste les pages disponibles dans les données
- **GET /feedback/analyze** - Analyse les feedbacks avec filtrage (méthode GET)
- **POST /feedback/analyze** - Analyse les feedbacks avec filtrage (méthode POST)
- **POST /feedback/analyze/background** - Lance une analyse en arrière-plan (pour les analyses longues)
- **GET /feedback/analyze/status/{task_id}** - Vérifie l'état d'une tâche d'analyse en arrière-plan

### Exemples de requêtes

#### Obtenir les pages disponibles

```bash
curl -X GET http://localhost:8000/feedback/pages
```

#### Analyser les feedbacks pour une page spécifique

```bash
curl -X POST http://localhost:8000/feedback/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "page_id": "/checkout",
    "start_date": "2023-01-01T00:00:00",
    "end_date": "2023-12-31T23:59:59"
  }'
```

#### Analyser les feedbacks des 30 derniers jours

```bash
curl -X GET "http://localhost:8000/feedback/analyze?start_date=2023-02-15T00:00:00&end_date=2023-03-15T23:59:59"
```

## Modèle de données

### Requête d'analyse

```json
{
  "page_id": "/checkout",
  "start_date": "2023-01-01T00:00:00", 
  "end_date": "2023-12-31T23:59:59",
  "model": "gpt-4o",
  "feedback_file": "data/amplitude_data/processed/latest.json"
}
```

### Réponse d'analyse

```json
{
  "metadata": {
    "analysis_date": "2023-03-15T12:34:56.789",
    "page_id": "/checkout",
    "date_range": {
      "start": "2023-01-01T00:00:00",
      "end": "2023-12-31T23:59:59"
    },
    "model": "gpt-4o",
    "feedback_count": 42
  },
  "results": {
    "summaries": {
      "overall": "Les utilisateurs sont généralement satisfaits...",
      "positive": "Les points forts mentionnés incluent...",
      "negative": "Les problèmes principaux concernent..."
    },
    "sentiments": {
      "positive": 0.65,
      "neutral": 0.2,
      "negative": 0.15
    },
    "emotions": {
      "satisfaction": 0.45,
      "frustration": 0.15,
      "confusion": 0.1,
      "autres": 0.3
    },
    "themes": [
      {
        "name": "Interface utilisateur",
        "count": 15,
        "sentiment": 0.2
      },
      {
        "name": "Performance",
        "count": 10,
        "sentiment": -0.3
      }
    ]
  },
  "status": "success"
}
```

## Tests

Pour tester l'analyseur de feedback directement (sans l'API):

```bash
python -m backend.scripts.test_feedback_analyzer
```

Pour tester les endpoints de l'API (assurez-vous que l'API est en cours d'exécution):

```bash
python -m backend.scripts.test_api
```

## Intégration avec les scripts existants

Le script `analyze_feedback.py` a été mis à jour pour utiliser la fonction `analyze_feedbacks` du nouveau module `feedback_analyzer.py`. Vous pouvez l'exécuter avec des options de filtrage:

```bash
python -m backend.scripts.analyze_feedback --page "/checkout" --days 30
```

Options disponibles:
- `--input` : Chemin vers le fichier d'entrée
- `--output` : Chemin pour enregistrer les résultats
- `--page` : Filtre par page
- `--days` : Nombre de jours à considérer
- `--ignore-date-filter` : Ignore le filtrage par date
- `--model` : Modèle OpenAI à utiliser

## Prochaines étapes

1. Ajouter une authentification pour sécuriser l'API
2. Optimiser les performances pour gérer de grands volumes de données
3. Ajouter plus d'options de filtrage (par exemple, par source, par utilisateur) 