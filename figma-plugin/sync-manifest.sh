#!/bin/bash

# Script pour synchroniser les fichiers manifest.json
# Utilisation: ./sync-manifest.sh

# Définir les chemins des fichiers
ROOT_MANIFEST="./manifest.json"
DIST_MANIFEST="./dist/manifest.json"

# Créer le dossier dist s'il n'existe pas
mkdir -p dist

# Vérifier si le fichier à la racine a été modifié
if [ -f "$ROOT_MANIFEST" ]; then
  echo "Synchronisation $ROOT_MANIFEST → $DIST_MANIFEST"
  cp "$ROOT_MANIFEST" "$DIST_MANIFEST"
  echo "✅ Manifest.json synchronisé vers dist/"
else
  echo "❌ Erreur: $ROOT_MANIFEST n'existe pas"
  exit 1
fi

# S'assurer que le dossier ui existe dans dist
mkdir -p dist/ui

# Copier également le fichier ProjectsPage.html dans dist/ui/
if [ -f "./src/ui/ProjectsPage.html" ]; then
  echo "Copie src/ui/ProjectsPage.html → dist/ui/ProjectsPage.html"
  cp "./src/ui/ProjectsPage.html" "./dist/ui/ProjectsPage.html"
  echo "✅ ProjectsPage.html copié vers dist/ui/"
else
  echo "⚠️ Attention: src/ui/ProjectsPage.html n'existe pas"
fi

echo "Synchronisation terminée!"
