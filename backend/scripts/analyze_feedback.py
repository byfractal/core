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
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

# Import our analysis function
from backend.models.feedback_analyzer import analyze_feedbacks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_analysis_results(results: Dict[str, Any], output_file: str) -> None:
    """
    Save analysis results to a JSON file.
    
    Args:
        results (Dict): The analysis results to save
        output_file (str): Path to save the results
    """
    try:
        # Create the output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
                
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
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
    
    # Ajouter une nouvelle option pour ignorer le filtrage par date
    parser.add_argument(
        "--ignore-date-filter",
        action="store_true",
        help="Ignore date filtering (useful for testing with sample data)"
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
    if args.ignore_date_filter:
        # Set dates far in the past/future to effectively disable date filtering
        start_date = datetime.fromtimestamp(0)  # January 1, 1970
        end_date = datetime.now() + timedelta(days=365*10)  # 10 years in the future
    
    # Run analysis using the consolidated function
    logger.info(f"Starting feedback analysis with page={args.page}, days={args.days}")
    results = analyze_feedbacks(
        page_id=args.page,
        start_date=start_date,
        end_date=end_date,
        model=args.model,
        feedback_file=args.input
    )
    
    # Save results
    save_analysis_results(results, args.output)
    
    logger.info("Analysis complete!")

if __name__ == "__main__":
    main() 