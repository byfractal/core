Très bonne remarque — tu es à une **étape cruciale** du projet : le passage d’un design validé à une **implémentation technique claire et scalable**.

Voici la version _parfaite_ du prompt pour **`ImportPage`**, dans le même ton et le même soin que celui d’hier 👇

---

## ✨ Ok c’est parti pour l’`ImportPage` !

---

### 🧱 Étapes préliminaires :

1. `git add .` puis `git commit` → snapshot des modifs précédentes (`ProjectsPage`)
2. `git checkout -b frontend-importpage` → création d’une **nouvelle branche dédiée**
3. Tu implémentes **uniquement l’écran `ImportPage`** (on ne fait pas les connexions ou logique JS pour le moment)

---

### 📌 Contexte du projet :
Nous construisons une **interface HTML/CSS native** pour un plugin Figma :
- ✅ Fiable, rapide, sans React
- ✅ 100% compatible avec Figma sandbox
- ✅ Composants modifiables facilement à la main (issus de `shadcn/ui` remixés)
- ✅ Rendu fidèle au Figma (pixel perfect = exigence MVP)

---

### 🎯 Mission de cette tâche :

Implémenter l’écran **`ImportPage`** dans `/ui/ImportPage.html` ou structure équivalente. Cet écran permet d’importer des données d’usage produit via API (Amplitude, Mixpanel…) ou via une extension navigateur.

---

### 🔍 🎨 Références Figma :

- 🔗 Lien MCP avec accès complet aux descriptions composants :  
  `@mcp`  
  `@https://www.figma.com/design/Cyv2WbRChVdBlXfxySgrvC/Prototype-pipeline--Plugin--1-?node-id=316-770&t=2qjmVhKoTF8Zzc8n-4`

- 🔧 Mode Dev / inspect :  
  `https://www.figma.com/design/Cyv2WbRChVdBlXfxySgrvC/Prototype-pipeline--Plugin--1-?node-id=316-770&m=dev&t=2qjmVhKoTF8Zzc8n-1`

- 📄 **Description officielle** dans Figma (accessible via MCP) :  
  > **"Allows users to import behavioral data from platforms like Amplitude or Mixpanel via API key. Includes a date range selector and an alternative import method using the browser extension. Designed for fast setup before analysis."**

---

### 🧠 Détail des composants attendus :

1. **Header** : titre `Import Project` + sous-titre explicatif
2. **Champ API Key** :
   - Input avec icône clé à gauche
   - Texte placeholder : `Enter your API key : Amplitude, Mixpanel...`
3. **Sélecteur de date** :
   - Icône calendrier
   - Placeholder : `Pick a date`
4. **Bouton principal** `Import`
5. **Séparateur** visuel `or` (ligne + texte centré)
6. **Bloc extension navigateur** :
   - Icône Chrome
   - Titre `Import via the browser extension`
   - Texte lorem temporaire (on le changera plus tard)
   - Bouton secondaire : `Install our browser extension`

---

### 🛠️ Stack à utiliser (strict) :

| Élément | Stack |
|--------|-------|
| UI     | HTML + CSS natif |
| Style  | Tailwind CSS si dispo, sinon classes manuelles |
| JS     | Aucun JS à ce stade (sauf minimum requis postMessage plus tard) |
| Composants | Basés sur shadcn/ui mais **reproduits à la main** (pas React) |

---

### ✅ Critères de validation :

- Respect visuel **pixel-perfect**
- Bonne hiérarchie HTML (`section`, `label`, `input`, etc.)
- Aucun composant React ou injection dynamique
- Responsive : s’adapte bien dans la UI Figma
- Pas encore connecté aux autres écrans (on verra les connexions plus tard)

---

### 💡 Faut-il connecter les pages entre elles maintenant ?

> ❌ **Non** — pas pour l’instant.

L’objectif est de valider chaque **écran isolé**, sans logique de navigation.  
On implémentera la navigation (avec `postMessage`, ou `state` centralisé dans `main.js`) **une fois tous les écrans fidèlement réalisés**.

---

Si tu veux, je peux générer une structure `ui/` propre pour organiser chaque page en composants HTML séparés (`/ui/components/...`) et préparer les connexions pour plus tard.

Bonne chance, tu maîtrises la partie ! 🔥