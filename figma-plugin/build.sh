#!/bin/bash

# Script de build pour le plugin HCentric Figma
echo "🚀 Starting build process for HCentric Figma Plugin..."

# Nettoyage du répertoire dist
echo "🧹 Cleaning dist directory..."
rm -rf dist
mkdir -p dist
mkdir -p dist/ui
mkdir -p dist/ui/pages
mkdir -p dist/ui/pages/projects
mkdir -p dist/ui/pages/import
mkdir -p dist/ui/styles

# Exécution du build via Webpack
echo "🔨 Building with Webpack..."
npm run build

# Vérification que les fichiers nécessaires ont été créés
echo "✅ Verifying build output..."
if [ -f "dist/code.js" ] && [ -f "dist/ui.html" ] && [ -f "dist/manifest.json" ]; then
  echo "✨ Build successful! Required files generated."

  # Liste des fichiers générés
  echo "📁 Build output:"
  find dist -type f | sort
else
  echo "❌ Build failed! Some required files are missing."
  exit 1
fi

echo "🎉 Build process completed successfully!"
echo "Instructions:"
echo "1. Open Figma"
echo "2. Go to Plugins > Development > Import plugin from manifest..."
echo "3. Select the manifest.json file in the dist directory"
echo "4. Test the plugin with Plugins > Development > HCentric UI/UX Optimizer" 