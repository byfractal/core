#!/usr/bin/env python
"""
Simple script to test API endpoints manually.
"""

import requests
import json
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:8080"

def test_health():
    """Test health endpoint."""
    print("\n=== Testing health endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_token():
    """Test JWT token generation."""
    print("\n=== Testing JWT token generation ===")
    try:
        # Adjust this to match your actual auth endpoint
        response = requests.post(
            f"{BASE_URL}/api/auth/token",
            data={
                "username": "test_user",
                "password": "test_password"
            }
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Token received: {data.get('access_token', '')[:10]}...")
            return data.get("access_token")
        else:
            print(f"Failed to get token: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_protected_endpoint(token):
    """Test a protected endpoint."""
    print("\n=== Testing protected endpoint ===")
    try:
        if not token:
            print("No token available. Skipping test.")
            return False
            
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    """Main function."""
    print("🚀 API Testing Script")
    print("====================")
    
    # Test health endpoint
    health_ok = test_health()
    
    if health_ok:
        # Test token generation
        token = test_token()
        
        # Test protected endpoint
        if token:
            test_protected_endpoint(token)
    
    print("\n====================")
    print("✅ Testing completed")

if __name__ == "__main__":
    main() 