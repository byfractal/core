"""
Test script for JWT authentication.
This script tests the JWT authentication flow.
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Test user credentials
TEST_USER = {
    "username": "test_user",
    "password": "test_password"
}

def test_jwt_flow():
    """Test the JWT authentication flow."""
    print("\n🔍 Testing JWT authentication flow...")
    
    # Step 1: Get a token
    print("\nGetting JWT token...")
    try:
        # Note: This endpoint might need adjustment based on your actual implementation
        response = requests.post(
            f"{BASE_URL}/api/auth/token",
            data={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"Token received: {access_token[:10]}...")
            
            # Step 2: Test a protected endpoint with the token
            print("\nTesting protected endpoint with token...")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Note: Replace with your actual protected endpoint
            protected_response = requests.get(
                f"{BASE_URL}/api/auth/me",
                headers=headers
            )
            print(f"Status: {protected_response.status_code}")
            print(f"Response: {protected_response.json() if protected_response.status_code == 200 else protected_response.text}")
            
            # Step 3: Test with invalid token
            print("\nTesting with invalid token...")
            invalid_headers = {"Authorization": "Bearer invalid_token"}
            invalid_response = requests.get(
                f"{BASE_URL}/api/auth/me",
                headers=invalid_headers
            )
            print(f"Status: {invalid_response.status_code}")
            print(f"Expected 401 Unauthorized: {'✅ Passed' if invalid_response.status_code == 401 else '❌ Failed'}")
            
        else:
            print(f"Failed to get token: {response.text}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    """Main function to run all tests."""
    print("🚀 Starting JWT authentication tests...")
    
    try:
        test_jwt_flow()
        print("\n✅ JWT tests completed!")
    except Exception as e:
        print(f"\n❌ Tests failed: {str(e)}")

if __name__ == "__main__":
    main() 