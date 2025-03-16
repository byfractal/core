"""
FastAPI endpoints pour la génération de designs basée sur l'analyse des feedbacks utilisateurs.
Ce module fournit une API RESTful pour transformer les recommandations en composants Figma.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from models.code_to_design import (
    CodeToDesignClient, 
    FigmaLayoutGenerator,
    extract_components_from_website
)

# Modèles Pydantic pour les requêtes et les réponses
class DesignGenerationRequest(BaseModel):
    """Modèle de requête pour la génération de designs"""
    page_id: str = Field(..., description="Identifiant de la page pour laquelle générer un design")
    recommendations_file: Optional[str] = Field(None, description="Chemin vers le fichier de recommandations (optionnel)")
    analysis_file: Optional[str] = Field(None, description="Chemin vers le fichier d'analyse (optionnel)")
    extract_components_from_url: Optional[str] = Field(None, description="URL du site pour extraire les composants (optionnel)")

class ComponentGenerationRequest(BaseModel):
    """Modèle de requête pour la génération d'un composant spécifique"""
    component_spec: Dict[str, Any] = Field(..., description="Spécification du composant à générer")

class WebsiteExtractionRequest(BaseModel):
    """Modèle de requête pour l'extraction des composants d'un site web"""
    url: str = Field(..., description="URL du site à analyser")

class DesignGenerationResponse(BaseModel):
    """Modèle de réponse pour la génération de designs"""
    page_id: str = Field(..., description="Identifiant de la page")
    timestamp: str = Field(..., description="Horodatage de la génération")
    layout: Dict[str, Any] = Field(..., description="Layout généré")
    implementation_notes: str = Field(..., description="Notes d'implémentation")

class ErrorResponse(BaseModel):
    """Modèle de réponse pour les erreurs"""
    error: str
    status: str = "error"

# Créer un router pour l'API de design
design_router = FastAPI(
    title="Design Generation API",
    description="API pour la génération de designs basée sur l'analyse des feedbacks",
    version="1.0.0"
)

# Cache pour stocker les résultats de génération de design
design_cache = {}
generation_tasks = {}

@design_router.post("/generate", response_model=DesignGenerationResponse, 
               responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def generate_design(request: DesignGenerationRequest):
    """
    Génère un design Figma basé sur des recommandations ou une analyse de feedback.
    
    Si recommendations_file est fourni, utilise directement ces recommandations.
    Si analysis_file est fourni, génère d'abord des recommandations à partir de l'analyse.
    Si extract_components_from_url est fourni, extrait d'abord les composants du site.
    """
    try:
        # Initialiser le générateur de layout
        layout_generator = FigmaLayoutGenerator()
        
        # Extraire les composants d'un site web si nécessaire
        if request.extract_components_from_url:
            extraction_result = extract_components_from_website(request.extract_components_from_url)
            if "error" in extraction_result:
                raise HTTPException(status_code=400, detail=f"Failed to extract components: {extraction_result['error']}")
        
        # Générer le design
        if request.recommendations_file:
            # Charger les recommandations depuis un fichier
            import json
            try:
                with open(request.recommendations_file, 'r') as f:
                    recommendations = json.load(f)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to load recommendations file: {e}")
            
            # Générer le layout à partir des recommandations
            result = layout_generator.generate_layout_from_recommendations(recommendations)
        
        elif request.analysis_file:
            # Charger l'analyse depuis un fichier
            import json
            try:
                with open(request.analysis_file, 'r') as f:
                    analysis = json.load(f)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to load analysis file: {e}")
            
            # Extraire le résumé d'analyse
            if "results" in analysis and "summary" in analysis["results"]:
                summary = analysis["results"]["summary"]
            else:
                raise HTTPException(status_code=400, detail="Analysis file does not contain summary data")
            
            # Générer le layout à partir de l'analyse
            result = layout_generator.generate_layout_from_analysis(summary, request.page_id)
        
        else:
            # Si aucun fichier n'est fourni, lever une exception
            raise HTTPException(
                status_code=400, 
                detail="Either recommendations_file or analysis_file must be provided"
            )
        
        # Mettre en cache le résultat
        cache_key = f"{request.page_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        design_cache[cache_key] = result
        
        return result
    
    except Exception as e:
        # Gérer les exceptions
        raise HTTPException(status_code=500, detail=str(e))

@design_router.post("/generate/background", response_model=Dict[str, str])
async def generate_design_background(
    background_tasks: BackgroundTasks,
    request: DesignGenerationRequest
):
    """
    Lance la génération de design en tâche de fond et retourne immédiatement.
    Utilise le même processus que l'endpoint /generate mais de manière asynchrone.
    """
    # Générer un ID de tâche
    import uuid
    task_id = str(uuid.uuid4())
    
    # Initialiser l'état de la tâche
    generation_tasks[task_id] = {
        "status": "pending",
        "request": request.dict(),
        "result": None,
        "error": None
    }
    
    # Définir la tâche de génération
    def run_generation_task():
        try:
            # Initialiser le générateur de layout
            layout_generator = FigmaLayoutGenerator()
            
            # Mettre à jour le statut
            generation_tasks[task_id]["status"] = "processing"
            
            # Extraire les composants d'un site web si nécessaire
            if request.extract_components_from_url:
                extraction_result = extract_components_from_website(request.extract_components_from_url)
                if "error" in extraction_result:
                    raise Exception(f"Failed to extract components: {extraction_result['error']}")
            
            # Générer le design
            if request.recommendations_file:
                # Charger les recommandations depuis un fichier
                import json
                try:
                    with open(request.recommendations_file, 'r') as f:
                        recommendations = json.load(f)
                except Exception as e:
                    raise Exception(f"Failed to load recommendations file: {e}")
                
                # Générer le layout à partir des recommandations
                result = layout_generator.generate_layout_from_recommendations(recommendations)
            
            elif request.analysis_file:
                # Charger l'analyse depuis un fichier
                import json
                try:
                    with open(request.analysis_file, 'r') as f:
                        analysis = json.load(f)
                except Exception as e:
                    raise Exception(f"Failed to load analysis file: {e}")
                
                # Extraire le résumé d'analyse
                if "results" in analysis and "summary" in analysis["results"]:
                    summary = analysis["results"]["summary"]
                else:
                    raise Exception("Analysis file does not contain summary data")
                
                # Générer le layout à partir de l'analyse
                result = layout_generator.generate_layout_from_analysis(summary, request.page_id)
            
            else:
                # Si aucun fichier n'est fourni, lever une exception
                raise Exception("Either recommendations_file or analysis_file must be provided")
            
            # Mettre en cache le résultat
            generation_tasks[task_id]["status"] = "completed"
            generation_tasks[task_id]["result"] = result
            
        except Exception as e:
            # Gérer les exceptions
            generation_tasks[task_id]["status"] = "failed"
            generation_tasks[task_id]["error"] = str(e)
    
    # Ajouter la tâche en arrière-plan
    background_tasks.add_task(run_generation_task)
    
    # Retourner l'ID de tâche
    return {"task_id": task_id, "status": "pending"}

@design_router.get("/generate/status/{task_id}", response_model=Dict[str, Any])
async def get_generation_status(task_id: str):
    """
    Récupère le statut d'une tâche de génération de design.
    """
    if task_id not in generation_tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    task_info = generation_tasks[task_id]
    
    # Préparer la réponse
    response = {
        "task_id": task_id,
        "status": task_info["status"],
    }
    
    # Ajouter le résultat ou l'erreur si disponible
    if task_info["status"] == "completed" and task_info["result"]:
        response["result"] = task_info["result"]
    elif task_info["status"] == "failed" and task_info["error"]:
        response["error"] = task_info["error"]
    
    return response

@design_router.post("/components/generate", response_model=Dict[str, Any],
               responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def generate_component(request: ComponentGenerationRequest):
    """
    Génère un composant Figma à partir d'une spécification.
    """
    try:
        # Initialiser le client Code.to.Design
        client = CodeToDesignClient()
        
        # Générer le composant
        result = client.generate_component(request.component_spec)
        
        # Vérifier s'il y a une erreur
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except Exception as e:
        # Gérer les exceptions
        raise HTTPException(status_code=500, detail=str(e))

@design_router.post("/extract", response_model=Dict[str, Any],
               responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def extract_website_components(request: WebsiteExtractionRequest):
    """
    Extrait les composants UI d'un site web existant.
    """
    try:
        # Extraire les composants
        result = extract_components_from_website(request.url)
        
        # Vérifier s'il y a une erreur
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except Exception as e:
        # Gérer les exceptions
        raise HTTPException(status_code=500, detail=str(e))

@design_router.get("/components/types", response_model=List[str])
async def get_component_types():
    """
    Récupère la liste des types de composants supportés par Code.to.Design.
    """
    # Liste des types de composants supportés
    component_types = [
        "button",
        "form",
        "input",
        "dropdown",
        "menu",
        "card",
        "modal",
        "navigation",
        "sidebar",
        "header",
        "footer",
        "table",
        "list",
        "checkbox",
        "radio",
        "toggle",
        "generic"
    ]
    
    return component_types 