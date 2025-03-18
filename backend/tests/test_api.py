"""
Test script for the FastAPI endpoints.
This script assumes the API is running locally on port 8000.
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Add backend directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

def test_root_endpoint():
    """Test the root endpoint."""
    print("\n--- Testing Root Endpoint ---")
    try:
        response = requests.get("http://localhost:8000/")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error connecting to API: {e}")

def test_health_endpoint():
    """Test the health endpoint."""
    print("\n--- Testing Health Endpoint ---")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error connecting to API: {e}")

def test_pages_endpoint():
    """Test the pages endpoint."""
    print("\n--- Testing Pages Endpoint ---")
    try:
        response = requests.get("http://localhost:8000/feedback/pages")
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error connecting to API: {e}")

def test_analyze_endpoint():
    """Test the analyze endpoint."""
    print("\n--- Testing Analyze Endpoint (GET) ---")
    try:
        response = requests.get(
            "http://localhost:8000/feedback/analyze",
            params={
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": datetime.now().isoformat()
            }
        )
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Analysis status: {result.get('status')}")
            print(f"Feedback count: {result.get('metadata', {}).get('feedback_count', 0)}")
            
            # Print just the first part of any summaries to keep the output manageable
            if result.get('status') == 'success' and 'summaries' in result.get('results', {}):
                print("\nSummaries:")
                for key, value in result['results']['summaries'].items():
                    print(f"- {key}: {value[:100]}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error connecting to API: {e}")

def test_analyze_with_page_endpoint():
    """Test the analyze endpoint with page filter."""
    print("\n--- Testing Analyze Endpoint with Page Filter (POST) ---")
    
    # First, get available pages
    try:
        pages_response = requests.get("http://localhost:8000/feedback/pages")
        if pages_response.status_code == 200:
            pages = pages_response.json()
            if not pages:
                print("No pages available to test with.")
                return
                
            test_page = pages[0]
            print(f"Testing with page: {test_page}")
            
            # Now test the analyze endpoint with this page
            response = requests.post(
                "http://localhost:8000/feedback/analyze",
                json={
                    "page_id": test_page,
                    "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                    "end_date": datetime.now().isoformat()
                }
            )
            
            print(f"Status code: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Analysis status: {result.get('status')}")
                print(f"Feedback count: {result.get('metadata', {}).get('feedback_count', 0)}")
                
                # Print just the first part of any summaries to keep the output manageable
                if result.get('status') == 'success' and 'summaries' in result.get('results', {}):
                    print("\nSummaries:")
                    for key, value in result['results']['summaries'].items():
                        print(f"- {key}: {value[:100]}...")
            else:
                print(f"Error: {response.text}")
        else:
            print(f"Error getting pages: {pages_response.text}")
    except Exception as e:
        print(f"Error in test: {e}")

def test_background_analysis():
    """Test the background analysis endpoint."""
    print("\n--- Testing Background Analysis Endpoint ---")
    try:
        # Start the background task
        response = requests.post(
            "http://localhost:8000/feedback/analyze/background",
            json={
                "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
                "end_date": datetime.now().isoformat()
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            print(f"Task started with ID: {task_id}")
            
            # Check the status a couple of times
            for i in range(3):
                print(f"\nChecking status (attempt {i+1})...")
                status_response = requests.get(
                    f"http://localhost:8000/feedback/analyze/status/{task_id}"
                )
                
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    print(f"Task status: {status_result.get('status')}")
                    
                    if status_result.get('status') != 'processing':
                        print("Task completed!")
                        if 'metadata' in status_result:
                            print(f"Feedback count: {status_result.get('metadata', {}).get('feedback_count', 0)}")
                        break
                else:
                    print(f"Error checking status: {status_response.text}")
                    break
                    
                # Wait a bit before checking again
                import time
                time.sleep(2)
        else:
            print(f"Error starting background task: {response.text}")
    except Exception as e:
        print(f"Error in test: {e}")

def main():
    """Run all tests."""
    print("Running API tests...")
    
    # Test basic endpoints
    test_root_endpoint()
    test_health_endpoint()
    
    # Test feedback-specific endpoints
    test_pages_endpoint()
    test_analyze_endpoint()
    test_analyze_with_page_endpoint()
    test_background_analysis()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 