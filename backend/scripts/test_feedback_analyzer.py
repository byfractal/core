"""
Test script for the feedback_analyzer module.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

from backend.models.feedback_analyzer import analyze_feedbacks, load_feedback_data

def test_analyze_feedbacks():
    """Test the analyze_feedbacks function with various parameters."""
    
    # Get available feedback files
    feedback_dir = os.path.join(root_dir, "data", "amplitude_data", "processed")
    
    # Use default test file if available, otherwise use the most recent file
    feedback_files = []
    if os.path.exists(feedback_dir):
        feedback_files = [f for f in os.listdir(feedback_dir) if f.endswith('.json')]
    
    if not feedback_files:
        print("No feedback files found in data/amplitude_data/processed/")
        return
    
    # Prefer test file if it exists
    if "test_feedback.json" in feedback_files:
        feedback_file = os.path.join(feedback_dir, "test_feedback.json")
    elif "latest.json" in feedback_files:
        feedback_file = os.path.join(feedback_dir, "latest.json")  
    else:
        feedback_file = os.path.join(feedback_dir, feedback_files[0])
    
    print(f"Using feedback file: {feedback_file}")
    
    # First, check what pages are available in the feedback data
    feedback_data = load_feedback_data(feedback_file)
    pages = set()
    for item in feedback_data:
        page = item.get("event_properties", {}).get("page")
        if page:
            pages.add(page)
    
    print(f"Available pages: {pages}")
    
    # If we have pages, use the first one, otherwise None
    test_page = next(iter(pages)) if pages else None
    
    # Test cases
    test_cases = [
        {
            "name": "Default parameters",
            "params": {
                "feedback_file": feedback_file
            }
        },
        {
            "name": "With page filter",
            "params": {
                "page_id": test_page,
                "feedback_file": feedback_file
            }
        },
        {
            "name": "With date filter (last 7 days)",
            "params": {
                "start_date": datetime.now() - timedelta(days=7),
                "end_date": datetime.now(),
                "feedback_file": feedback_file
            }
        },
        {
            "name": "With page and date filter",
            "params": {
                "page_id": test_page,
                "start_date": datetime.now() - timedelta(days=14),
                "end_date": datetime.now(),
                "feedback_file": feedback_file
            }
        }
    ]
    
    # Run test cases
    for test_case in test_cases:
        print(f"\n--- Running test: {test_case['name']} ---")
        try:
            results = analyze_feedbacks(**test_case["params"])
            
            # Print a summary of results
            print(f"Status: {results.get('status')}")
            print(f"Feedback count: {results.get('metadata', {}).get('feedback_count', 0)}")
            if results.get('status') == 'success':
                print("Analysis successful!")
                
                # Print summaries if they exist 
                if 'summaries' in results.get('results', {}):
                    print("\nSummaries:")
                    for key, value in results['results']['summaries'].items():
                        print(f"- {key}: {value[:100]}...")
            else:
                print(f"Analysis not successful: {results.get('results', {}).get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_analyze_feedbacks() 