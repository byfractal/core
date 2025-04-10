Ok c'est parti !

🧱 Étapes :
1. `git add .` puis `git commit` → snapshot des modifs actuelles
2. `git checkout -b frontend-projectspage` → création d'une **nouvelle branche dédiée**
3. Tu implémentes uniquement l'écran `ProjectsPage` (pas les suivants pour le moment).

---

📌 Contexte :
Nous utilisons désormais du **HTML/CSS pur** dans le plugin Figma, sans React, pour :
- éviter les bugs d'interface Figma (écrans blancs, sandbox)
- garantir la compatibilité avec le MCP
- garder des composants facilement modifiables (même si basés initialement sur `shadcn/ui`)

---

🔍 🎨 Écran à reproduire (via MCP + screen fourni) :
- `ProjectsPage`
- Lien MCP :  
  `@mcp.json`  
  `@https://www.figma.com/design/Cyv2WbRChVdBlXfxySgrvC/Prototype-pipeline--Plugin--1-?node-id=316-767&t=Bin7yXxXsy41Budj-4`

- 📄 **Description Figma** du composant (visible via le MCP) :
  > "Small semantic tag representing the optimization category (e.g. Layout, Friction). Used to group issues by type. Appears in both InsightCard and ProjectOverviewPage."

---

🛠️ **Stack frontend à utiliser (très important)** :
- HTML/CSS pur (pas de React)
- Tu peux utiliser Tailwind pour les styles
- JS Vanilla uniquement pour les interactions (postMessage etc.)
- Copie/adapte les composants `shadcn/ui` si besoin (mais sans React)
- Fichier de destination : `/ui/ProjectsPage.html` ou intégré dans `index.html` selon architecture

---

✅ **Objectif**
Reproduire la `ProjectsPage` à l'identique visuellement (pixel perfect) depuis Figma, avec une structure HTML propre, stylée, et prête à recevoir la logique JS (interactions plus tard).

Ne passe pas à l'écran suivant tant que cette page n'est pas validée. Tu peux me montrer un aperçu HTML+CSS intermédiaire si tu veux valider.

Bonne chance 🔥

<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M7 18H17V8H7V18Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M7 8V4H13L17 8H7Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M13 15L10 12L11 11L13 13L17 9L18 10L13 15Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
