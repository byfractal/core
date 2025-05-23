"""
FastAPI endpoints for feedback analysis operations.
This module provides RESTful API for analyzing user feedback with page and date filtering.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from backend.models.feedback_analyzer import analyze_feedbacks
from backend.security.auth0 import get_current_user, Auth0User, requires_scopes

# Modèles Pydantic pour les requêtes et les réponses
class AnalysisRequest(BaseModel):
    """Request model for feedback analysis"""
    page_id: Optional[str] = Field(None, description="Page identifier to filter feedbacks")
    start_date: Optional[datetime] = Field(None, description="Start date for filtering (ISO format)")
    end_date: Optional[datetime] = Field(None, description="End date for filtering (ISO format)")
    model: str = Field("gpt-4o", description="LLM model to use for analysis")
    feedback_file: str = Field("data/amplitude_data/processed/latest.json", 
                             description="Path to the feedback data file")

class AnalysisResponse(BaseModel):
    """Response model for feedback analysis results"""
    metadata: Dict[str, Any] = Field(..., description="Metadata about the analysis")
    results: Dict[str, Any] = Field(..., description="Analysis results")
    status: str = Field(..., description="Status of the analysis")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    status: str = "error"

# Cache to store analysis results
analysis_cache = {}

# Create router for feedback API
feedback_router = FastAPI(
    title="Feedback Analysis API",
    description="API for analyzing user feedback with page and date filtering",
    version="1.0.0"
)

@feedback_router.post("/analyze", response_model=AnalysisResponse, 
                     responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def analyze_feedback(
    request: AnalysisRequest,
    user: Auth0User = Depends(get_current_user)
):
    """
    Analyze user feedback with filtering by page and date range.
    
    - **page_id**: Optional page identifier to filter feedbacks
    - **start_date**: Optional start date for filtering (defaults to 30 days ago)
    - **end_date**: Optional end date for filtering (defaults to current date)
    - **model**: LLM model to use for analysis (default: gpt-4o)
    - **feedback_file**: Path to the feedback data file
    
    Returns analysis results including sentiment analysis, themes/emotions, and summaries.
    """
    try:
        # Check for cached results with the same parameters
        cache_key = f"{request.page_id}_{request.start_date}_{request.end_date}_{request.model}_{request.feedback_file}"
        if cache_key in analysis_cache:
            return analysis_cache[cache_key]
        
        # Run the analysis
        results = analyze_feedbacks(
            page_id=request.page_id,
            start_date=request.start_date,
            end_date=request.end_date,
            model=request.model,
            feedback_file=request.feedback_file
        )
        
        # Cache the results
        analysis_cache[cache_key] = results
        
        return results
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Analysis failed: {str(e)}", "status": "error"}
        )

@feedback_router.get("/analyze", response_model=AnalysisResponse, 
                    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def analyze_feedback_get(
    page_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    model: str = "gpt-4o",
    feedback_file: str = "data/amplitude_data/processed/latest.json",
    user: Auth0User = Depends(get_current_user)
):
    """
    Analyze user feedback with filtering by page and date range (GET method).
    
    - **page_id**: Optional page identifier to filter feedbacks
    - **start_date**: Optional start date for filtering (defaults to 30 days ago)
    - **end_date**: Optional end date for filtering (defaults to current date)
    - **model**: LLM model to use for analysis (default: gpt-4o)
    - **feedback_file**: Path to the feedback data file
    
    Returns analysis results including sentiment analysis, themes/emotions, and summaries.
    """
    try:
        # Check for cached results with the same parameters
        cache_key = f"{page_id}_{start_date}_{end_date}_{model}_{feedback_file}"
        if cache_key in analysis_cache:
            return analysis_cache[cache_key]
        
        # Run the analysis
        results = analyze_feedbacks(
            page_id=page_id,
            start_date=start_date,
            end_date=end_date,
            model=model,
            feedback_file=feedback_file
        )
        
        # Cache the results
        analysis_cache[cache_key] = results
        
        return results
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Analysis failed: {str(e)}", "status": "error"}
        )

@feedback_router.post("/analyze/background", response_model=Dict[str, str])
@requires_scopes(["read:feedback", "write:feedback"])
async def analyze_feedback_background(
    background_tasks: BackgroundTasks,
    request: AnalysisRequest,
    user: Auth0User = Depends(get_current_user)
):
    """
    Start a background task to analyze feedback (useful for long-running analyses).
    
    - **page_id**: Optional page identifier to filter feedbacks
    - **start_date**: Optional start date for filtering (defaults to 30 days ago)
    - **end_date**: Optional end date for filtering (defaults to current date)
    - **model**: LLM model to use for analysis (default: gpt-4o)
    - **feedback_file**: Path to the feedback data file
    
    Returns a task ID that can be used to check the status of the analysis.
    """
    from uuid import uuid4
    task_id = str(uuid4())
    
    def run_analysis_task():
        try:
            results = analyze_feedbacks(
                page_id=request.page_id,
                start_date=request.start_date,
                end_date=request.end_date,
                model=request.model,
                feedback_file=request.feedback_file
            )
            analysis_cache[f"task_{task_id}"] = results
        except Exception as e:
            analysis_cache[f"task_{task_id}"] = {
                "error": f"Analysis failed: {str(e)}",
                "status": "error"
            }
    
    background_tasks.add_task(run_analysis_task)
    return {"task_id": task_id, "status": "processing"}

@feedback_router.get("/analyze/status/{task_id}", response_model=Dict[str, Any])
async def get_analysis_status(
    task_id: str,
    user: Auth0User = Depends(get_current_user)
):
    """
    Check the status of a background analysis task.
    
    - **task_id**: The ID of the task to check
    
    Returns the status of the task and the results if available.
    """
    cache_key = f"task_{task_id}"
    if cache_key in analysis_cache:
        return analysis_cache[cache_key]
    return {"status": "processing"}

@feedback_router.get("/pages", response_model=List[str])
async def get_available_pages(
    feedback_file: str = "data/amplitude_data/processed/latest.json",
    user: Auth0User = Depends(get_current_user)
):
    """
    Get a list of available page IDs from the feedback data.
    
    - **feedback_file**: Path to the feedback data file
    
    Returns a list of unique page IDs found in the feedback data.
    """
    from backend.models.feedback_analyzer import load_feedback_data
    
    try:
        feedback_data = load_feedback_data(feedback_file)
        # Extract unique page IDs
        page_ids = list(set(item.get("page_id", "") for item in feedback_data))
        # Filter out empty strings
        page_ids = [page_id for page_id in page_ids if page_id]
        return page_ids
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available pages: {str(e)}"
        )
