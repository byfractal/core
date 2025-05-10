# HCentric UI Optimizer - Chrome Extension

Une extension Chrome pour l'optimisation d'interface utilisateur basée sur les analyses comportementales et les insights d'IA.

## Fonctionnalités

- Analyse des comportements utilisateurs sur votre site web
- Identification des points de friction dans l'interface
- Recommandations d'optimisation UI/UX avec impact estimé
- Application des correctifs directement via l'extension
- Suivi des résultats des optimisations

## Installation pour le développement

1. Cloner ce dépôt
2. Installer les dépendances: `npm install`
3. Construire l'extension: `npm run build`
4. Charger l'extension dans Chrome:
   - Ouvrir `chrome://extensions/`
   - Activer le "Mode développeur"
   - Cliquer sur "Charger l'extension non empaquetée"
   - Sélectionner le dossier `dist` généré

## Développement

Pour le développement avec compilation automatique:

```bash
npm run dev
```

## Architecture

L'extension se compose de plusieurs éléments clés:

- **Background Script**: Gère l'état global et la communication avec l'API
- **Content Script**: Injecté dans les pages web pour collecter des données et appliquer des optimisations
- **Popup**: Interface utilisateur de l'extension

## Transformation depuis le plugin Figma

Cette extension est une adaptation du plugin Figma HCentric UI Optimizer, transformée pour fonctionner directement dans les navigateurs.
Les principales différences incluent:

- Interface adaptée aux standards des extensions Chrome
- Interactivité complète avec les pages web (possibilité d'analyser et modifier le DOM)
- Workflow optimisé pour intégration directe avec les sites

## Structure des fichiers

```
extension/
├── src/
│   ├── background.ts     # Script background
│   ├── content.ts        # Script injecté dans les pages
│   ├── popup.ts          # Logique de la popup
│   └── types/            # Définitions TypeScript
├── icons/                # Icônes de l'extension
├── popup.html            # Interface de la popup
├── styles.css            # Styles de la popup
├── content.css           # Styles injectés dans les pages
├── manifest.json         # Manifeste de l'extension
└── webpack.config.js     # Configuration de build
``` 