#!/usr/bin/env python
"""
Test script for simple JWT authentication.
This script tests the JWT authentication flow with the simplified auth implementation.
"""

import sys
import requests
import json
from pathlib import Path

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Base URL for the API
BASE_URL = "http://localhost:8080"

# Test user credentials
TEST_USER = {
    "username": "test_user",
    "password": "test_password"
}

def test_health():
    """Test the health check endpoint."""
    print("\n🔍 Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_public_endpoint():
    """Test a public endpoint that doesn't require authentication."""
    print("\n🔍 Testing public endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/public")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_get_token():
    """Test obtaining a JWT token with valid credentials."""
    print("\n🔍 Testing token generation...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/token",
            data={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"Token received: {token[:20]}...")
            return token
        else:
            print(f"Failed to get token: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint with a valid token."""
    print("\n🔍 Testing protected endpoint...")
    if not token:
        print("No token available. Skipping test.")
        return False
        
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_invalid_token():
    """Test accessing a protected endpoint with an invalid token."""
    print("\n🔍 Testing invalid token...")
    try:
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        # Should fail with 401
        return response.status_code == 401
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    """Main function to run all tests."""
    print("\n============================================")
    print("🧪 JWT Authentication Test Suite")
    print("============================================")
    
    # Test health endpoint
    health_ok = test_health()
    
    # Test public endpoint
    public_ok = test_public_endpoint()
    
    # Test token generation
    token = test_get_token()
    
    # Test protected endpoint
    if token:
        protected_ok = test_protected_endpoint(token)
    else:
        protected_ok = False
    
    # Test invalid token
    invalid_token_ok = test_invalid_token()
    
    # Print summary
    print("\n============================================")
    print("📊 Test Results Summary")
    print("============================================")
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Public Endpoint: {'✅ PASS' if public_ok else '❌ FAIL'}")
    print(f"Token Generation: {'✅ PASS' if token else '❌ FAIL'}")
    print(f"Protected Endpoint: {'✅ PASS' if protected_ok else '❌ FAIL'}")
    print(f"Invalid Token: {'✅ PASS' if invalid_token_ok else '❌ FAIL'}")
    print("============================================")

if __name__ == "__main__":
    main() 