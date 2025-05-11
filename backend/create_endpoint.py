#!/usr/bin/env python
"""
Script temporaire pour exposer un endpoint d'insights simple à des fins de test.
"""

import json
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/analysis/insights")
async def get_insights():
    """Endpoint test pour récupérer les insights"""
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
        
        print(f"Serving data from {file_path}")
        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("Starting simple insights API server...")
    uvicorn.run(app, host="0.0.0.0", port=8080) 