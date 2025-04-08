"""
Main FastAPI application.
This is the entry point for the backend API.
"""

import sys
from pathlib import Path
from typing import Dict
import os

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.feedback import feedback_router
from backend.api.design import design_router
from backend.api.analysis import analysis_router

# Create the main application
app = FastAPI(
    title="Design Insights API",
    description="API pour l'analyse UX/UI et la génération de recommandations",
    version="0.1.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dans un environnement de production, spécifiez les origines exactes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.mount("/feedback", feedback_router)
app.mount("/design", design_router)
app.mount("/analysis", analysis_router)

@app.get("/")
async def root():
    """
    Root endpoint that returns basic API information.
    """
    return {
        "status": "online",
        "service": "Design Insights API",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running correctly.
    """
    return {
        "status": "healthy",
        "timestamp": os.path.getmtime(__file__)
    }

# Main entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 