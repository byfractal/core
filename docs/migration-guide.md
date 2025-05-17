# Guide de Migration - Extension Chrome Analytics UX

Ce document détaille les fichiers à migrer du projet `hcentric_interface_old` vers le nouveau template WXT-React-Shadcn. Il décrit l'organisation cible, la justification de chaque composant, et les étapes de migration.

## Fichiers Backend à Migrer

### 1. API Core (Fonctionnalités métier)

| Chemin source | Destination | Justification |
|---------------|-------------|---------------|
| `backend/api/analysis.py` | `backend/api/analysis.py` | API principale d'analyse UX avec endpoints pour obtenir des insights |
| `backend/api/recommendations.py` | `backend/api/recommendations.py` | Génération des recommandations UI/UX, format JSON critique |
| `backend/api/main.py` | `backend/api/main.py` | Point d'entrée FastAPI, routage et configuration CORS |
| `backend/api/design.py` | `backend/api/design.py` | Intégration avec les composants de design (Figma) |
| `backend/api/feedback.py` | `backend/api/feedback.py` | Gestion du feedback utilisateur |

### 2. Services (Intégrations API tierces)

| Chemin source | Destination | Justification |
|---------------|-------------|---------------|
| `backend/services/amplitude/client.py` | `backend/services/amplitude/client.py` | Client API Amplitude avec encryption et auth |
| `backend/services/amplitude/query_builder.py` | `backend/services/amplitude/query_builder.py` | Construction de requêtes optimisées |
| `backend/services/amplitude/data_processor.py` | `backend/services/amplitude/data_processor.py` | Traitement des données brutes Amplitude |
| `backend/services/amplitude/__init__.py` | `backend/services/amplitude/__init__.py` | Exports du module |
| `backend/services/posthog_service.py` | `backend/services/posthog_service.py` | Service pour PostHog |
| `backend/services/analysis_service.py` | `backend/services/analysis_service.py` | Service d'analyse des données |

### 3. Scripts utilitaires

| Chemin source | Destination | Justification |
|---------------|-------------|---------------|
| `backend/scripts/generate_insights_from_amplitude.py` | `backend/scripts/generate_insights_from_amplitude.py` | Script central pour la génération des insights UX |
| `backend/scripts/process_amplitude_data.py` | `backend/scripts/process_amplitude_data.py` | Traitement des données brutes Amplitude |
| `backend/scripts/fetch_amplitude_sessions.py` | `backend/scripts/fetch_amplitude_sessions.py` | Récupération de sessions utilisateur |
| `backend/scripts/fetch_posthog_data.py` | `backend/scripts/fetch_posthog_data.py` | Récupération des données PostHog |

### 4. Autres fichiers essentiels

| Chemin source | Destination | Justification |
|---------------|-------------|---------------|
| `output/recommendations_output.json` | `backend/output/recommendations_output.json` et `frontend/public/recommendations_output.json` | Format JSON critique pour la structure frontend |
| `backend/STRUCTURE.md` | `docs/backend-structure.md` | Documentation de l'architecture backend |
| `requirements.txt` | `backend/requirements.txt` | Dépendances Python |
| `docker-compose.yml` | `docker-compose.yml` | Configuration de déploiement |
| `Dockerfile` | `Dockerfile` | Configuration de déploiement |

## Éléments à Recréer dans le Frontend

Le frontend doit être entièrement reconstruit avec le template WXT-React-Shadcn. Les composants clés à développer sont:

### 1. Components React

- **InsightCard.tsx** - Carte individuelle d'insight UX (basée sur le format JSON)
- **InsightList.tsx** - Liste des insights avec filtrage et tri
- **MetricDisplay.tsx** - Affichage des métriques au format approprié
- **SeverityBadge.tsx** - Badge visuel pour les niveaux de sévérité

### 2. Pages

- **Analysis.tsx** - Page principale d'affichage des insights
- **Settings.tsx** - Configuration de l'extension (API keys, etc.)
- **Import.tsx** - Interface d'import de données depuis Amplitude/PostHog

### 3. Hooks et Services

- **useInsights.ts** - Hook pour récupérer et filtrer les insights
- **amplitudeService.ts** - Service frontend pour interagir avec l'API backend Amplitude
- **posthogService.ts** - Service frontend pour interagir avec l'API backend PostHog

## Structure JSON des Insights

Le format JSON suivant est critique et doit être respecté par le frontend:

```json
{
  "timestamp": "2025-05-11T18:38:34.163194",
  "total_events_analyzed": 823,
  "insights": [
    {
      "issueTitle": "High time spent on page https://v0-financial-dashboard-seven-bice.vercel.app/organization",
      "severity": "needs-improvement",
      "rootCause": {
        "context": "Users are spending unusually long time on this page",
        "metric": {
          "text": "Avg. time spent: 473.1 seconds",
          "value": "473.1s"
        },
        "contextualData": "Extended page view times may indicate users are having trouble finding information or completing actions.",
        "conversionImpact": "This could be causing increased drop-off rates",
        "source": "Amplitude Analytics"
      },
      "recommendedFix": {
        "suggestion": "Consider reviewing page layout and content organization. Ensure key actions are clearly visible.",
        "source": "UX Best Practices"
      },
      "impactEstimate": "Optimizing this page could reduce average time spent by 40-60% and improve conversion rates",
      "tags": [
        "Layout",
        "Navigation",
        "User Flow"
      ],
      "sources": [
        "Amplitude",
        "UX Analysis"
      ]
    }
  ]
}
```

## Contexte Technique pour le Nouveau Projet

```markdown
# Contexte Projet - Extension Chrome Analytics UX

## Objectif
Extension Chrome (React + WXT + Shadcn/UI) qui affiche les insights UX générés par un backend IA. L'extension analyse les données d'utilisation et propose des améliorations d'interface.

## Architecture
- **Backend**: FastAPI, services Python (intégration Amplitude/PostHog, LLM processing)
- **Frontend**: Template WXT-React-Shadcn-TailwindCSS pour extension Chrome
- **Flux de données**:
  1. Import via API (Amplitude/PostHog)
  2. Traitement et analyse 
  3. Génération d'insights UX/UI
  4. Affichage dans l'extension avec suggestions d'amélioration

## Fonctionnalités Clés
- Import de données analytics via API
- Analyse automatisée du comportement utilisateur
- Identification des problèmes d'UX (temps passé excessif, abandons)
- Visualisation des insights par page/écran
- Recommandations d'amélioration UX avec impact estimé
```

## Étapes de Migration

1. Créer la structure du nouveau projet selon le template WXT-React-Shadcn
2. Copier les fichiers backend listés ci-dessus dans leurs emplacements respectifs
3. Copier `recommendations_output.json` à la fois dans le backend et le frontend (public)
4. Copier la documentation et les fichiers de configuration
5. Développer les composants frontend React qui consomment le format JSON
6. Configurer l'extension pour communiquer avec le backend local (port 8000)

Le frontend doit être conçu en gardant à l'esprit que la structure JSON des insights est immuable, car elle fait partie du contrat API entre le backend et le frontend. 