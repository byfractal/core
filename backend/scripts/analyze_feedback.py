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

def filter_feedback_by_date(feedback_data: List[Dict[str, Any]], start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """
    Filter feedback data by date range.
    
    Args:
        feedback_data (List[Dict]): The feedback data to filter
        start_date (datetime): Start date for the filter
        end_date (datetime): End date for the filter
        
    Returns:
        List[Dict]: Filtered feedback data
    """
    # Temporairement désactivé pour les tests - retourner toutes les données sans filtrage
    logger.info(f"Date filtering temporarily disabled for testing")
    return feedback_data
    
    # Original code:
    # filtered_data = []
    # for item in feedback_data:
    #     timestamp = item.get("time", 0)
    #     if timestamp:
    #         # Convert milliseconds timestamp to datetime
    #         item_date = datetime.fromtimestamp(timestamp / 1000.0)
    #         if start_date <= item_date <= end_date:
    #             filtered_data.append(item)
    
    # logger.info(f"Filtered {len(filtered_data)} feedback items from {start_date.date()} to {end_date.date()}")
    # return filtered_data

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

def save_analysis_results(results: Dict[str, Any], output_file: str) -> None:
    """
    Save analysis results to a JSON file.
    
    Args:
        results (Dict): The analysis results to save
        output_file (str): Path to the output file
    """
    try:
        # Fonction pour nettoyer les chaînes JSON entourées de backticks
        def clean_json_string(s):
            if not isinstance(s, str):
                return s
                
            # Enlever les backticks et les marqueurs ```json
            s = s.strip()
            if s.startswith('```json'):
                s = s[7:]
            elif s.startswith('```'):
                s = s[3:]
                
            if s.endswith('```'):
                s = s[:-3]
                
            return s.strip()
        
        # Fonction récursive pour convertir les objets non sérialisables
        def make_json_serializable(obj):
            if isinstance(obj, dict):
                result = {}
                for k, v in obj.items():
                    # Cas spécial pour les champs raw_result qui contiennent des chaînes JSON
                    if k == "raw_result" and isinstance(v, str):
                        cleaned = clean_json_string(v)
                        try:
                            # Tenter de le parser en JSON
                            result = json.loads(cleaned)
                        except:
                            # Si échec, garder la chaîne nettoyée
                            result[k] = cleaned
                    else:
                        result[k] = make_json_serializable(v)
                return result
            elif isinstance(obj, list):
                return [make_json_serializable(item) for item in obj]
            elif hasattr(obj, 'content'):  # Pour les AIMessage
                content = obj.content
                # Nettoyer la chaîne JSON si nécessaire
                cleaned_content = clean_json_string(content)
                try:
                    # Tenter de le parser en JSON
                    return json.loads(cleaned_content)
                except:
                    return cleaned_content
            elif hasattr(obj, '__dict__'):  # Pour les autres objets avec attributs
                return str(obj)
            else:
                return obj
        
        # Convertir les résultats en objets sérialisables
        serializable_results = make_json_serializable(results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
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
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load and filter feedback data
    feedback_data = load_feedback_data(args.input)
    feedback_data = filter_feedback_by_page(feedback_data, args.page)
    if not args.ignore_date_filter:
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