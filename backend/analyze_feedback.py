"""
Main entry point for feedback analysis using LangChain pipelines.

This script processes feedback data from Amplitude or other sources,
runs it through the analysis chains, and outputs the results.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

# Import our analysis chains
from backend.models.analysis_chains import FeedbackAnalysisChains
from backend.models.vector_store import get_vector_store

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_feedback_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Load feedback data from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file containing feedback data
        
    Returns:
        List[Dict]: A list of feedback items with their metadata
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Successfully loaded {len(data)} feedback items from {file_path}")
        return data
    except Exception as e:
        logger.error(f"Error loading feedback data: {e}")
        return []

def filter_feedback_by_page(
    feedback_data: List[Dict[str, Any]], 
    page_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filter feedback data by page ID.
    
    Args:
        feedback_data (List[Dict]): The full feedback data
        page_id (str, optional): The page ID to filter by
        
    Returns:
        List[Dict]: Filtered feedback data
    """
    if not page_id:
        return feedback_data
        
    filtered_data = [
        item for item in feedback_data 
        if item.get("event_properties", {}).get("page") == page_id
    ]
    
    logger.info(f"Filtered {len(filtered_data)} feedback items for page {page_id}")
    return filtered_data

def filter_feedback_by_date(
    feedback_data: List[Dict[str, Any]],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Filter feedback data by date range.
    
    Args:
        feedback_data (List[Dict]): The full feedback data
        start_date (datetime, optional): The start date for filtering
        end_date (datetime, optional): The end date for filtering
        
    Returns:
        List[Dict]: Filtered feedback data
    """
    if not start_date and not end_date:
        return feedback_data
        
    filtered_data = []
    
    for item in feedback_data:
        # Get the timestamp from the item
        timestamp = item.get("time")
        if not timestamp:
            continue
            
        # Convert to datetime
        try:
            item_date = datetime.fromtimestamp(timestamp / 1000)  # Convert from milliseconds
            
            # Apply filters
            if start_date and item_date < start_date:
                continue
            if end_date and item_date > end_date:
                continue
                
            filtered_data.append(item)
        except Exception as e:
            logger.warning(f"Error processing date for item: {e}")
            continue
    
    date_range = ""
    if start_date:
        date_range += f"from {start_date.strftime('%Y-%m-%d')} "
    if end_date:
        date_range += f"to {end_date.strftime('%Y-%m-%d')}"
        
    logger.info(f"Filtered {len(filtered_data)} feedback items {date_range}")
    return filtered_data

def extract_feedback_texts(feedback_data: List[Dict[str, Any]]) -> List[str]:
    """
    Extract just the feedback text from the feedback data.
    
    Args:
        feedback_data (List[Dict]): The feedback data
        
    Returns:
        List[str]: A list of feedback texts
    """
    feedback_texts = []
    
    for item in feedback_data:
        feedback_text = item.get("event_properties", {}).get("feedback_text")
        if feedback_text:
            feedback_texts.append(feedback_text)
    
    logger.info(f"Extracted {len(feedback_texts)} feedback texts")
    return feedback_texts

def save_analysis_results(results: Dict[str, Any], output_file: str):
    """
    Save analysis results to a JSON file.
    
    Args:
        results (Dict): The analysis results
        output_file (str): Path to save the results
    """
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Analysis results saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving analysis results: {e}")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Analyze user feedback using LangChain pipelines")
    
    parser.add_argument(
        "--input", 
        type=str, 
        default="data/amplitude_data/processed/latest.json",
        help="Path to the input JSON file containing feedback data"
    )
    
    parser.add_argument(
        "--output", 
        type=str, 
        default=f"data/analysis_results/analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        help="Path to save the analysis results"
    )
    
    parser.add_argument(
        "--page", 
        type=str, 
        help="Filter feedback by page ID"
    )
    
    parser.add_argument(
        "--days", 
        type=int, 
        default=30,
        help="Number of days to look back for feedback (default: 30)"
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        default="gpt-4o",
        help="OpenAI model to use for analysis (default: gpt-4o)"
    )
    
    args = parser.parse_args()
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load and filter feedback data
    feedback_data = load_feedback_data(args.input)
    feedback_data = filter_feedback_by_page(feedback_data, args.page)
    feedback_data = filter_feedback_by_date(feedback_data, start_date, end_date)
    
    if not feedback_data:
        logger.error("No feedback data available after filtering")
        return
    
    # Extract feedback texts
    feedback_texts = extract_feedback_texts(feedback_data)
    
    if not feedback_texts:
        logger.error("No feedback texts found in the data")
        return
    
    # Initialize analysis chains
    logger.info(f"Initializing analysis chains with model: {args.model}")
    analysis_chains = FeedbackAnalysisChains(model=args.model)
    
    # Run analysis
    logger.info(f"Running batch analysis on {len(feedback_texts)} feedback items")
    analysis_results = analysis_chains.batch_analyze(feedback_texts)
    
    # Add metadata to results
    metadata = {
        "analysis_date": datetime.now().isoformat(),
        "page_id": args.page,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "model": args.model,
        "feedback_count": len(feedback_texts)
    }
    
    final_results = {
        "metadata": metadata,
        "results": analysis_results
    }
    
    # Save results
    save_analysis_results(final_results, args.output)
    
    logger.info("Analysis complete!")

if __name__ == "__main__":
    main() 