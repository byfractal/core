"""
Script to run the FastAPI application with Uvicorn.
"""

import os
import sys
from pathlib import Path

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

import uvicorn

def main():
    """
    Run the FastAPI application with Uvicorn.
    
    Usage:
        python -m backend.scripts.run_api
    """
    # Set environment variables if needed
    os.environ["PYTHONPATH"] = root_dir
    
    # Run the application
    uvicorn.run(
        "backend.api.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 