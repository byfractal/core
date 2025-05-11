#!/usr/bin/env python
"""
Test script for API endpoints used by the Chrome extension.
This script tests the backend API endpoints needed for the Chrome extension.
"""

import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Base URL for the API
BASE_URL = "http://localhost:8080"

# Helper function to make authenticated requests
def make_auth_request(endpoint, method="get", data=None, token=None):
    """Make an authenticated request to the API."""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method.lower() == "get":
            response = requests.get(url, headers=headers)
        elif method.lower() == "post":
            response = requests.post(url, json=data, headers=headers)
        elif method.lower() == "put":
            response = requests.put(url, json=data, headers=headers)
        elif method.lower() == "delete":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        return response
    except Exception as e:
        print(f"Error making request to {url}: {str(e)}")
        return None

def get_token():
    """Get a JWT token for authentication."""
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

def test_health():
    """Test the health endpoint."""
    print("\n🔍 Testing health endpoint...")
    response = make_auth_request("/health")
    
    if response and response.status_code == 200:
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    else:
        if response:
            print(f"❌ Status: {response.status_code}")
            print(f"❌ Response: {response.text}")
        return False

def test_feedback_endpoints(token):
    """Test the feedback API endpoints."""
    print("\n🔍 Testing feedback endpoints...")
    
    # Test GET /api/feedback (list feedbacks)
    print("\n  GET /api/feedback")
    response = make_auth_request("/api/feedback", token=token)
    
    if response and response.status_code == 200:
        print(f"  ✅ Status: {response.status_code}")
        feedback_count = len(response.json())
        print(f"  ✅ Received {feedback_count} feedback entries")
    else:
        if response:
            print(f"  ❌ Status: {response.status_code}")
            print(f"  ❌ Response: {response.text}")
    
    # Test POST /api/feedback (create feedback)
    print("\n  POST /api/feedback")
    test_feedback = {
        "page_id": f"test_page_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "session_id": "test_session_123",
        "user_id": "test_user_456",
        "feedback_text": "This is a test feedback from the extension test script",
        "rating": 4,
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "browser": "Chrome",
            "version": "1.0.0",
            "source": "extension_test"
        }
    }
    
    response = make_auth_request("/api/feedback", method="post", data=test_feedback, token=token)
    
    if response and response.status_code in (200, 201):
        print(f"  ✅ Status: {response.status_code}")
        print(f"  ✅ Response: {response.json()}")
        feedback_id = response.json().get("id")
        return feedback_id
    else:
        if response:
            print(f"  ❌ Status: {response.status_code}")
            print(f"  ❌ Response: {response.text}")
        return None

def test_analysis_endpoints(token):
    """Test the analysis API endpoints."""
    print("\n🔍 Testing analysis endpoints...")
    
    # Test GET /api/analysis (list analyses)
    print("\n  GET /api/analysis")
    response = make_auth_request("/api/analysis", token=token)
    
    if response and response.status_code == 200:
        print(f"  ✅ Status: {response.status_code}")
        analysis_count = len(response.json())
        print(f"  ✅ Received {analysis_count} analysis entries")
    else:
        if response:
            print(f"  ❌ Status: {response.status_code}")
            print(f"  ❌ Response: {response.text}")
    
    # Test POST /api/analysis/generate (generate new analysis)
    print("\n  POST /api/analysis/generate")
    test_analysis_request = {
        "page_id": f"test_page_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "feedback_ids": [],  # Empty for testing
        "options": {
            "include_sentiment": True,
            "generate_recommendations": True
        }
    }
    
    response = make_auth_request("/api/analysis/generate", method="post", data=test_analysis_request, token=token)
    
    if response and response.status_code in (200, 201, 202):
        print(f"  ✅ Status: {response.status_code}")
        print(f"  ✅ Response: {response.json()}")
        return True
    else:
        if response:
            print(f"  ❌ Status: {response.status_code}")
            print(f"  ❌ Response: {response.text}")
        return False

def main():
    """Main function to run all tests."""
    print("\n============================================")
    print("🔬 Chrome Extension API Test Suite")
    print("============================================")
    
    # Test health endpoint (doesn't require authentication)
    health_ok = test_health()
    
    if health_ok:
        # Get authentication token
        token = get_token()
        
        if token:
            # Test feedback endpoints
            feedback_id = test_feedback_endpoints(token)
            
            # Test analysis endpoints
            analysis_ok = test_analysis_endpoints(token)
        else:
            print("\n❌ Skipping authenticated endpoint tests due to missing token")
    else:
        print("\n❌ Skipping further tests due to health check failure")
    
    print("\n============================================")
    print("📊 Test Summary")
    print("============================================")
    print(f"API Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    if 'token' in locals():
        print(f"Authentication: {'✅ PASS' if token else '❌ FAIL'}")
        if token:
            print(f"Feedback API: {'✅ PASS' if 'feedback_id' in locals() and feedback_id else '❌ FAIL'}")
            print(f"Analysis API: {'✅ PASS' if 'analysis_ok' in locals() and analysis_ok else '❌ FAIL'}")
    print("============================================")

if __name__ == "__main__":
    main() 