#!/bin/bash

# Script pour exécuter les tests de l'API Feedback

# Créer les répertoires nécessaires s'ils n'existent pas
mkdir -p data/amplitude_data/processed/
mkdir -p data/analysis_results/

# Définir les variables d'environnement pour le test
export TESTING=true

# Vérifier si les fichiers de données existent
if [ ! -f data/amplitude_data/processed/test_feedback.json ]; then
    echo "Création du fichier de test..."
    python create_test_data.py
fi

# Lier test_feedback.json à latest.json si nécessaire
if [ ! -f data/amplitude_data/processed/latest.json ]; then
    echo "Création du lien symbolique vers latest.json..."
    ln -sf $(pwd)/data/amplitude_data/processed/test_feedback.json $(pwd)/data/amplitude_data/processed/latest.json
fi

# Tester l'analyseur de feedback
echo "=== Test de l'analyseur de feedback ==="
python -m backend.scripts.test_feedback_analyzer

# Vérifier si le port 8000 est déjà utilisé
PORT_ALREADY_USED=$(lsof -i :8000 | grep LISTEN)
if [ ! -z "$PORT_ALREADY_USED" ]; then
    echo "Port 8000 déjà utilisé. Tentative de libération..."
    PID=$(echo "$PORT_ALREADY_USED" | awk '{print $2}')
    if [ ! -z "$PID" ]; then
        echo "Arrêt du processus $PID qui utilise le port 8000..."
        kill -9 $PID
        sleep 1
    fi
fi

# Démarrer l'API en arrière-plan
echo "=== Démarrage de l'API en arrière-plan ==="
python -m backend.scripts.run_api &
API_PID=$!

# Attendre que l'API démarre
echo "Attente du démarrage de l'API..."
sleep 3

# Exécuter les tests de l'API
echo "=== Test de l'API ==="
python -m backend.scripts.test_api

# Arrêter l'API
echo "=== Arrêt de l'API ==="
if ps -p $API_PID > /dev/null; then
    kill $API_PID
    echo "API arrêtée (PID: $API_PID)"
else
    echo "L'API n'est plus en cours d'exécution. Vérification des processus restants sur le port 8000..."
    PORT_USED=$(lsof -i :8000 | grep LISTEN)
    if [ ! -z "$PORT_USED" ]; then
        PID=$(echo "$PORT_USED" | awk '{print $2}')
        echo "Processus $PID trouvé sur le port 8000. Tentative d'arrêt..."
        kill -9 $PID
    fi
fi

echo "=== Tests terminés ===" 