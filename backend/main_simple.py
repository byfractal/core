#!/usr/bin/env python
"""
Serveur FastAPI minimaliste pour servir les insights aux fins de test.
"""

import json
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HCentric Insights API")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines en mode développement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint racine pour vérifier que le serveur fonctionne"""
    return {"message": "HCentric Insights API is running"}

@app.get("/api/analysis/insights")
async def get_insights():
    """Endpoint pour récupérer les insights d'analyse UI/UX"""
    try:
        # Trouver le fichier le plus récent
        project_root = Path(__file__).parent.parent
        output_dir = project_root / "output"
        recommendation_files = list(output_dir.glob("recommendations_output*.json"))
        
        if recommendation_files:
            # Utiliser le fichier le plus récent
            latest_file = max(recommendation_files, key=lambda x: x.stat().st_mtime)
            file_path = latest_file
        else:
            # Fallback sur le fichier de l'extension
            file_path = project_root / "extension" / "output" / "recommendation_output.json"
        
        # Lire et retourner les données
        with open(file_path, "r") as f:
            data = json.load(f)
        
        print(f"Serving insights data from {file_path}")
        return data
    
    except Exception as e:
        print(f"Error retrieving insights: {str(e)}")
        return {"error": str(e)} 