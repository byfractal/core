#!/usr/bin/env python
"""
Test script for the Recommendations API.
This script tests the recommendations endpoints that will be used by the Chrome extension.
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Base URL for the API
BASE_URL = "http://localhost:8080"

def get_token():
    """Get JWT token for authentication."""
    print("\n🔑 Getting authentication token...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/token",
            data={
                "username": "test_user",
                "password": "test_password"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Token received: {token[:15]}...")
            return token
        else:
            print(f"❌ Failed to get token: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_import_amplitude_data(token):
    """Test importing data from Amplitude."""
    print("\n🔍 Testing Amplitude data import...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Request data
    data = {
        "api_key": "test_amplitude_api_key",
        "start_date": "2023-01-01",
        "end_date": "2023-01-31",
        "project_id": "test_project"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/recommendations/import/amplitude",
            json=data,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Task ID: {result.get('task_id')}")
            print(f"Status: {result.get('status')}")
            
            # Test checking the status
            task_id = result.get('task_id')
            if task_id:
                print("\nChecking task status...")
                # Wait a bit for the background task to complete
                time.sleep(3)
                
                status_response = requests.get(
                    f"{BASE_URL}/api/recommendations/import/status/{task_id}",
                    headers=headers
                )
                print(f"Status check response: {status_response.status_code}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"Task status: {status_data.get('status')}")
                    
                    if status_data.get('status') == "completed" and 'result' in status_data:
                        print("\nTask completed successfully!")
                        print(f"Data points: {status_data['result'].get('data_points')}")
                        print(f"Pages analyzed: {status_data['result'].get('pages_analyzed')}")
                        print(f"Metrics extracted: {', '.join(status_data['result'].get('metrics_extracted', []))}")
                    else:
                        print(f"Task not yet completed or failed: {status_data}")
                else:
                    print(f"Failed to check status: {status_response.text}")
                
            return result.get('task_id')
        else:
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_generate_recommendations(token, page_id="test-homepage"):
    """Test generating recommendations for a specific page."""
    print(f"\n🔍 Testing recommendation generation for page: {page_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Sample metrics data that would come from your analytics
    metrics = {
        "bounce_rate": 75.2,
        "avg_session_duration": 60,
        "conversion_rate": 1.8,
        "ctr": 2.5,
        "page_views": 15000
    }
    
    # Request body
    data = {
        "page_id": page_id,
        "metrics": metrics,
        "options": {
            "include_visual_recommendations": True,
            "focus_areas": ["conversion", "engagement", "layout"]
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/recommendations/generate",
            json=data,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            insights_count = len(result.get("insights", []))
            print(f"Generated {insights_count} insights")
            print(f"Summary: {result.get('summary')}")
            
            # Print all insights
            print("\n📊 Generated Insights:")
            for i, insight in enumerate(result.get("insights", [])):
                print(f"\n--- Insight {i+1}: {insight.get('title')} ---")
                print(f"Type: {insight.get('type')}")
                print(f"Severity: {insight.get('severity')}")
                print(f"Description: {insight.get('description')}")
                print(f"Recommendation: {insight.get('recommendation')}")
                
                # Print metrics impact if available
                metrics_impact = insight.get("metrics_impact")
                if metrics_impact:
                    print("Metrics Impact:")
                    for metric, impact in metrics_impact.items():
                        print(f"  - {metric}: {impact}")
            
            return True
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_get_recommendations(token, page_id="test-homepage"):
    """Test retrieving recommendations for a specific page."""
    print(f"\n🔍 Testing recommendation retrieval for page: {page_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/recommendations/{page_id}",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            insights_count = len(result.get("insights", []))
            print(f"Retrieved {insights_count} insights")
            
            # Verify the insights are the same as what was generated
            print("\n📊 Cached Insights:")
            for i, insight in enumerate(result.get("insights", [])[:2]):  # Show first 2 insights
                print(f"\n--- Insight {i+1}: {insight.get('title')} ---")
                print(f"Type: {insight.get('type')}")
                print(f"Severity: {insight.get('severity')}")
            
            return True
        elif response.status_code == 404:
            print("No recommendations found for this page")
            return False
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_different_metrics(token):
    """Test generating recommendations with different metrics to see how insights change."""
    print("\n🧪 Testing recommendation generation with different metrics...")
    
    # Test cases with different metrics
    test_cases = [
        {
            "name": "High bounce rate, low conversion",
            "page_id": "test-page-high-bounce",
            "metrics": {
                "bounce_rate": 85.0,
                "avg_session_duration": 45,
                "conversion_rate": 0.8,
                "ctr": 3.5,
                "page_views": 20000
            }
        },
        {
            "name": "Low bounce rate, good metrics",
            "page_id": "test-page-good-metrics",
            "metrics": {
                "bounce_rate": 35.0,
                "avg_session_duration": 180,
                "conversion_rate": 4.5,
                "ctr": 6.2,
                "page_views": 18000
            }
        },
        {
            "name": "Poor CTR, good duration",
            "page_id": "test-page-poor-ctr",
            "metrics": {
                "bounce_rate": 45.0,
                "avg_session_duration": 150,
                "conversion_rate": 3.2,
                "ctr": 1.8,
                "page_views": 12000
            }
        }
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for test_case in test_cases:
        print(f"\n--- Test case: {test_case['name']} ---")
        
        data = {
            "page_id": test_case["page_id"],
            "metrics": test_case["metrics"],
            "options": {
                "include_visual_recommendations": True
            }
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/recommendations/generate",
                json=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                insights_count = len(result.get("insights", []))
                print(f"Generated {insights_count} insights")
                
                # Print insight types and severities
                insight_types = {}
                for insight in result.get("insights", []):
                    insight_type = insight.get("type")
                    severity = insight.get("severity")
                    
                    if insight_type not in insight_types:
                        insight_types[insight_type] = []
                    
                    insight_types[insight_type].append(severity)
                
                print("Insight breakdown:")
                for insight_type, severities in insight_types.items():
                    print(f"  - {insight_type}: {len(severities)} insights ({', '.join(severities)})")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    """Main function to run all tests."""
    print("\n============================================")
    print("🔬 Recommendations API Test Suite")
    print("============================================")
    
    # Get authentication token
    token = get_token()
    
    if not token:
        print("❌ Skipping tests due to authentication failure")
        return
    
    # Test Amplitude data import
    task_id = test_import_amplitude_data(token)
    
    # Test recommendation generation
    page_id = f"test-page-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    test_generate_recommendations(token, page_id)
    
    # Test recommendation retrieval
    test_get_recommendations(token, page_id)
    
    # Test different metrics
    test_different_metrics(token)
    
    print("\n============================================")
    print("✅ Recommendations API tests completed")
    print("============================================")

if __name__ == "__main__":
    main() 