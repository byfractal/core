#!/usr/bin/env python3
"""
Simple script to test direct data extraction from PostHog.
This script allows quick testing of PostHog API access
without running the full integration test suite.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

# Load environment variables
load_dotenv()

def check_env_vars():
    """Check if required environment variables are set"""
    print("\n=== PostHog Environment Variables ===")
    required_vars = ["POSTHOG_API_KEY", "POSTHOG_PROJECT_ID", "POSTHOG_API_URL"]
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Partially mask API key for security
            if var == "POSTHOG_API_KEY":
                masked_value = value[:8] + "..." + value[-8:]
                print(f"✅ {var} = {masked_value}")
            else:
                print(f"✅ {var} = {value}")
        else:
            print(f"❌ {var} is not defined in .env file")
            all_present = False
    
    return all_present

def make_simple_api_request():
    """Make a simple request to PostHog API to verify access"""
    print("\n=== Simple PostHog API Test ===")
    
    api_key = os.getenv("POSTHOG_API_KEY")
    project_id = os.getenv("POSTHOG_PROJECT_ID")
    api_url = os.getenv("POSTHOG_API_URL")
    
    if not all([api_key, project_id, api_url]):
        print("❌ Missing environment variables. Test impossible.")
        return False
    
    # Check if API is accessible
    print("Checking API access...")
    
    # URL to check project information
    url = f"{api_url}/projects/{project_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        project_data = response.json()
        print(f"✅ Successfully connected to PostHog API")
        print(f"   Project: {project_data.get('name', 'Name not available')}")
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Status: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_events_api():
    """Test access to events via PostHog API"""
    print("\n=== Testing Event Retrieval ===")
    
    api_key = os.getenv("POSTHOG_API_KEY")
    project_id = os.getenv("POSTHOG_PROJECT_ID")
    api_url = os.getenv("POSTHOG_API_URL")
    
    # Start date (7 days ago)
    date_from = (datetime.now() - timedelta(days=7)).isoformat()
    
    # URL to retrieve latest events
    url = f"{api_url}/projects/{project_id}/events"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"limit": 5, "date_from": date_from}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        events_data = response.json()
        results = events_data.get("results", [])
        
        print(f"✅ Successfully retrieved events")
        print(f"   Number of events: {len(results)}")
        
        if results:
            print("\n   Example event:")
            sample = results[0]
            print(f"   - Type: {sample.get('event', 'N/A')}")
            print(f"   - Date: {sample.get('timestamp', 'N/A')}")
            
            if "properties" in sample and sample["properties"]:
                print("   - Available properties:")
                for key in list(sample["properties"].keys())[:5]:  # Limit to 5 properties
                    print(f"     - {key}")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Status: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_session_recordings_api():
    """Test access to session recordings via PostHog API"""
    print("\n=== Testing Session Recordings Retrieval ===")
    
    api_key = os.getenv("POSTHOG_API_KEY")
    project_id = os.getenv("POSTHOG_PROJECT_ID")
    api_url = os.getenv("POSTHOG_API_URL")
    
    # Start date (30 days ago)
    date_from = (datetime.now() - timedelta(days=30)).isoformat()
    
    # URL to retrieve session recordings
    url = f"{api_url}/projects/{project_id}/session_recordings"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"limit": 5, "date_from": date_from}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        recordings_data = response.json()
        results = recordings_data.get("results", [])
        
        print(f"✅ Successfully retrieved session recordings")
        print(f"   Number of recordings: {len(results)}")
        
        if results:
            print("\n   Example recording:")
            sample = results[0]
            print(f"   - ID: {sample.get('id', 'N/A')}")
            print(f"   - Duration: {sample.get('duration', 'N/A')}")
            print(f"   - Date: {sample.get('start_time', 'N/A')}")
            
            if "person" in sample and sample["person"]:
                person = sample["person"]
                print(f"   - Person: {person.get('name', 'N/A')}")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Status: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
        
        if e.response.status_code == 403:
            print("\n⚠️ Error 403 Forbidden - Check that your API key has the necessary permissions")
            print("   You need 'View recordings' permission in PostHog")
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def print_summary(results):
    """Display a summary of test results"""
    print("\n=======================================")
    print("TEST SUMMARY")
    print("=======================================")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    
    for test, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test}")
    
    print("\n---------------------------------------")
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("---------------------------------------")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️ {failed} test(s) failed. Check errors above.")

def run_all_tests():
    """Run all tests"""
    results = {}
    
    # Check environment variables
    results["Environment variables check"] = check_env_vars()
    
    # If variables are missing, stop tests
    if not results["Environment variables check"]:
        print("\n❌ Missing environment variables. Cannot continue tests.")
        print_summary(results)
        return
    
    # Basic API test
    results["API connection test"] = make_simple_api_request()
    
    # If basic test fails, stop other tests
    if not results["API connection test"]:
        print("\n❌ Cannot connect to PostHog API. Stopping tests.")
        print_summary(results)
        return
    
    # Test events API
    results["Events API test"] = test_events_api()
    
    # Test session recordings API
    results["Session recordings API test"] = test_session_recordings_api()
    
    # Display summary
    print_summary(results)

if __name__ == "__main__":
    print("====================================")
    print("POSTHOG EXTRACTION TEST")
    print("====================================")
    run_all_tests() 