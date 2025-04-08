"""
FastAPI endpoints pour l'analyse UX/UI et la génération de recommandations.
Ce module fournit une API RESTful pour analyser les composants Figma et générer des insights UI/UX.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

from fastapi import FastAPI, HTTPException, Query, Path as PathParam, Body, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.models.analysis_card import AnalysisRequest, AnalysisResponse, AnalysisCard, SeverityLevel
from backend.services.analysis_service import AnalysisService

# Créer un router pour l'API d'analyse
analysis_router = FastAPI(
    title="Design Analysis API",
    description="API pour l'analyse UX/UI et la génération de recommandations",
    version="0.1.0"
)

# Dépendance pour obtenir le service d'analyse
def get_analysis_service():
    return AnalysisService()

# Cache pour stocker les analyses en cours
analysis_tasks = {}

@analysis_router.post("/generate", response_model=AnalysisResponse)
async def generate_analysis(
    request: AnalysisRequest,
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    Génère des analyses UX/UI basées sur les données Figma et les métriques d'analytics.
    
    - **figma_file_key**: Clé du fichier Figma à analyser
    - **node_ids**: Liste des IDs de nœuds Figma à analyser
    - **data_sources**: Sources de données à utiliser (ex: Amplitude, PostHog)
    - **date_range**: Plage de dates pour l'analyse
    - **api_keys**: Clés API pour les différentes sources de données
    """
    try:
        # Ici, nous simulons des données métriques pour l'exemple
        # Dans un cas réel, vous les récupéreriez à partir des sources spécifiées
        metrics_data = {
            "page_views": 25000,
            "bounce_rate": "65%",
            "avg_session_duration": "2m 15s",
            "conversion_rate": "3.2%",
            "benchmarks": {
                "industry_bounce_rate": "45%",
                "industry_conversion_rate": "5.4%"
            }
        }
        
        # Générer les cartes d'analyse
        cards = service.generate_analysis(
            figma_file_key=request.figma_file_key,
            node_ids=request.node_ids,
            metrics_data=metrics_data
        )
        
        # Retourner la réponse paginée
        return service.get_paginated_response(cards)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analysis: {str(e)}")


@analysis_router.get("/cards", response_model=AnalysisResponse)
async def get_analysis_cards(
    figma_file_key: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=50, description="Items per page"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    severity: Optional[List[SeverityLevel]] = Query(None, description="Filter by severity"),
    sort_by: Optional[str] = Query(None, description="Sort by criteria (severity, created_at, optimization_number)"),
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    Récupère les cartes d'analyse avec pagination et filtrage.
    
    - **figma_file_key**: Clé du fichier Figma
    - **page**: Numéro de page (commence à 1)
    - **per_page**: Nombre d'éléments par page
    - **tags**: Filtrer par tags
    - **severity**: Filtrer par niveau de sévérité
    - **sort_by**: Critère de tri
    """
    try:
        # Récupérer les cartes depuis la base de données
        cards = service.get_cards_by_file_key(figma_file_key)
        
        # Obtenir la réponse paginée
        response = service.get_paginated_response(
            cards=cards,
            page=page,
            per_page=per_page,
            filter_tags=tags,
            filter_severity=severity,
            sort_by=sort_by
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis cards: {str(e)}")


@analysis_router.get("/cards/{card_id}", response_model=AnalysisCard)
async def get_analysis_card_by_id(
    card_id: str = PathParam(..., description="ID of the analysis card"),
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    Récupère une carte d'analyse spécifique par son ID.
    
    - **card_id**: ID de la carte d'analyse
    """
    try:
        # Récupérer toutes les cartes (dans un cas réel, vous récupéreriez juste celle avec l'ID spécifique)
        all_cards = service.get_cards_by_file_key("*")  # Utiliser "*" comme joker
        
        # Rechercher la carte avec l'ID spécifié
        card = next((c for c in all_cards if c.id == card_id), None)
        
        if not card:
            raise HTTPException(status_code=404, detail=f"Analysis card with ID {card_id} not found")
        
        return card
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis card: {str(e)}")


@analysis_router.post("/cards/{card_id}/mark-viewed")
async def mark_card_as_viewed(
    card_id: str = PathParam(..., description="ID of the analysis card"),
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    Marque une carte comme déjà vue (désactive l'animation "shine").
    
    - **card_id**: ID de la carte d'analyse
    """
    try:
        success = service.mark_card_as_viewed(card_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Analysis card with ID {card_id} not found")
        
        return {"status": "success", "message": "Card marked as viewed"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking card as viewed: {str(e)}")


@analysis_router.post("/apply-fix", response_model=Dict[str, Any])
async def apply_fix(
    card_id: str = Body(..., embed=True, description="ID of the analysis card"),
    figma_file_key: str = Body(..., embed=True, description="Figma file key"),
    node_id: str = Body(..., embed=True, description="Figma node ID"),
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    Applique une correction recommandée à un élément de l'interface Figma.
    
    - **card_id**: ID de la carte d'analyse
    - **figma_file_key**: Clé du fichier Figma
    - **node_id**: ID du nœud Figma à modifier
    """
    try:
        # Dans un cas réel, vous utiliseriez l'API Figma pour appliquer la correction
        # Pour l'exemple, nous retournons simplement un message de succès
        
        return {
            "status": "success",
            "message": f"Fix applied to node {node_id} in file {figma_file_key}",
            "card_id": card_id,
            "applied_at": str(datetime.now())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying fix: {str(e)}")


@analysis_router.post("/apply-all-fixes", response_model=Dict[str, Any])
async def apply_all_fixes(
    figma_file_key: str = Body(..., embed=True, description="Figma file key"),
    node_ids: List[str] = Body(..., embed=True, description="List of Figma node IDs"),
    card_ids: List[str] = Body(..., embed=True, description="List of analysis card IDs"),
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    Applique toutes les corrections recommandées à plusieurs éléments de l'interface Figma.
    
    - **figma_file_key**: Clé du fichier Figma
    - **node_ids**: Liste des IDs de nœuds Figma à modifier
    - **card_ids**: Liste des IDs des cartes d'analyse correspondantes
    """
    try:
        # Dans un cas réel, vous utiliseriez l'API Figma pour appliquer les corrections
        # Pour l'exemple, nous retournons simplement un message de succès
        
        return {
            "status": "success",
            "message": f"All fixes applied to {len(node_ids)} nodes in file {figma_file_key}",
            "nodes_affected": node_ids,
            "cards_processed": card_ids,
            "applied_at": str(datetime.now())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying fixes: {str(e)}")


@analysis_router.post("/import-data", response_model=Dict[str, Any])
async def import_analytics_data(
    source: str = Body(..., embed=True, description="Source of data (amplitude, posthog, extension)"),
    api_key: Optional[str] = Body(None, embed=True, description="API key for the data source"),
    date_range: Optional[List[str]] = Body(None, embed=True, description="Date range for data import [start, end]"),
    project_id: Optional[str] = Body(None, embed=True, description="Project ID for the data source"),
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    Importe des données d'analytics à partir d'une source externe.
    
    - **source**: Source des données (amplitude, posthog, extension)
    - **api_key**: Clé API pour la source de données
    - **date_range**: Plage de dates pour l'importation des données [début, fin]
    - **project_id**: ID du projet pour la source de données
    """
    try:
        # Dans un cas réel, vous utiliseriez les informations fournies pour importer les données
        # Pour l'exemple, nous retournons simplement un message de succès
        
        return {
            "status": "success",
            "message": f"Data import from {source} started",
            "import_id": str(datetime.now().timestamp()),
            "estimated_completion_time": "30 seconds",
            "source": source,
            "date_range": date_range
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing data: {str(e)}")


@analysis_router.get("/import-status/{import_id}", response_model=Dict[str, Any])
async def get_import_status(
    import_id: str = PathParam(..., description="ID of the import process"),
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    Récupère le statut d'un processus d'importation de données.
    
    - **import_id**: ID du processus d'importation
    """
    try:
        # Dans un cas réel, vous récupéreriez le statut réel du processus d'importation
        # Pour l'exemple, nous simulons un statut terminé
        
        return {
            "status": "completed",
            "message": "Data import completed successfully",
            "import_id": import_id,
            "pages_imported": 5,
            "metrics_imported": ["page_views", "bounce_rate", "conversion_rate", "avg_session_duration"],
            "date_range_processed": ["2023-01-01", "2023-01-31"],
            "completed_at": str(datetime.now())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving import status: {str(e)}")


@analysis_router.get("/available-pages/{import_id}", response_model=Dict[str, Any])
async def get_available_pages(
    import_id: str = PathParam(..., description="ID of the import process"),
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    Récupère la liste des pages disponibles après un import pour la sélection.
    
    - **import_id**: ID du processus d'importation
    """
    try:
        # Dans un cas réel, vous récupéreriez les pages réellement importées
        # Pour l'exemple, nous retournons des pages simulées
        
        return {
            "import_id": import_id,
            "pages": [
                {
                    "id": "page1",
                    "title": "Homepage",
                    "url": "/",
                    "metrics": {
                        "page_views": 12500,
                        "bounce_rate": "45%",
                        "conversion_rate": "3.8%"
                    }
                },
                {
                    "id": "page2",
                    "title": "Product Page",
                    "url": "/products/main",
                    "metrics": {
                        "page_views": 8300,
                        "bounce_rate": "38%",
                        "conversion_rate": "5.2%"
                    }
                },
                {
                    "id": "page3",
                    "title": "Checkout",
                    "url": "/checkout",
                    "metrics": {
                        "page_views": 3200,
                        "bounce_rate": "22%",
                        "conversion_rate": "62.5%"
                    }
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving available pages: {str(e)}")


@analysis_router.post("/select-pages", response_model=Dict[str, Any])
async def select_pages_for_analysis(
    import_id: str = Body(..., embed=True, description="ID of the import process"),
    page_ids: List[str] = Body(..., embed=True, description="IDs of the pages to analyze"),
    service: AnalysisService = Depends(get_analysis_service)
):
    """
    Sélectionne les pages à analyser parmi celles disponibles après l'import.
    
    - **import_id**: ID du processus d'importation
    - **page_ids**: Liste des IDs des pages à analyser
    """
    try:
        # Dans un cas réel, vous utiliseriez les informations fournies pour lancer l'analyse
        # Pour l'exemple, nous retournons simplement un message de succès
        
        return {
            "status": "success",
            "message": f"Analysis started for {len(page_ids)} pages",
            "import_id": import_id,
            "analysis_id": str(datetime.now().timestamp()),
            "pages_selected": page_ids,
            "estimated_completion_time": "2 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error selecting pages for analysis: {str(e)}") 