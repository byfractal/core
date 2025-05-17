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

## Migration et Restructuration
Ce projet est une migration d'un ancien codebase (`hcentric_interface_old`) vers un nouveau template d'extension Chrome plus propre et maintenu (WXT-React-Shadcn). Nous conservons la logique métier backend tout en reconstruisant l'interface utilisateur.

Pour la migration complète, voir le fichier `docs/migration-guide.md` qui liste tous les fichiers à migrer avec leur emplacement cible.

## Tâches Immédiates
1. **Copier `recommendations_output.json`** dans `frontend/public/` pour servir de fallback local
2. **Créer le composant React `<InsightCard>`** basé sur le schéma JSON
3. **Implémenter la page `Analysis.tsx`** qui récupère les données depuis l'API

## Format JSON Critique
L'API backend génère un format JSON spécifique contenant:
- Timestamp et métadonnées
- Liste d'insights avec:
  - Titre du problème
  - Sévérité
  - Cause racine avec contexte et métriques
  - Solution recommandée
  - Estimation d'impact
  - Tags et sources

Ce format JSON est le contrat entre le backend et le frontend et doit être respecté par les composants React. 