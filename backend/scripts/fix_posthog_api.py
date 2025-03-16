#!/usr/bin/env python3
"""
PostHog API Authentication Troubleshooter and Fixer

This script helps diagnose and fix authentication issues with the PostHog API.
It tests both Personal and Project API keys to determine which one works properly.
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

def setup_args():
    """Configure command line arguments."""
    parser = argparse.ArgumentParser(
        description='PostHog API Authentication Troubleshooter'
    )
    parser.add_argument(
        '--api_key', 
        type=str, 
        help='PostHog API key to test (overrides environment variable)'
    )
    parser.add_argument(
        '--project_id', 
        type=str, 
        help='PostHog project ID to test (overrides environment variable)'
    )
    parser.add_argument(
        '--api_url', 
        type=str, 
        default='https://app.posthog.com/api',
        help='PostHog API URL (overrides environment variable)'
    )
    parser.add_argument(
        '--save', 
        action='store_true',
        help='Save working credentials to .env file'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Display detailed information'
    )
    
    return parser.parse_args()

def get_env_variables(args):
    """Get environment variables, with command-line arguments taking precedence."""
    api_key = args.api_key or os.environ.get('POSTHOG_API_KEY')
    project_id = args.project_id or os.environ.get('POSTHOG_PROJECT_ID')
    api_url = args.api_url or os.environ.get('POSTHOG_API_URL', 'https://app.posthog.com/api')
    
    return api_key, project_id, api_url

def test_project_api_key(api_key, project_id, api_url, verbose=False):
    """
    Test a PostHog Project API key (phc_*).
    
    Args:
        api_key: PostHog Project API key
        project_id: PostHog project ID
        api_url: PostHog API URL
        verbose: Whether to print detailed information
        
    Returns:
        (bool, str): (Success status, Error message or '')
    """
    if verbose:
        print(f"Testing Project API key {api_key[:5]}...{api_key[-5:]}")
    
    # Project API keys should use Api-Key header
    headers = {
        "Authorization": f"Api-Key {api_key}",
        "Content-Type": "application/json"
    }
    
    endpoint = f"{api_url}/projects/{project_id}"
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        
        if verbose:
            print(f"  ✅ Project API key works! Status: {response.status_code}")
            if response.status_code == 200:
                project_info = response.json()
                print(f"  Project name: {project_info.get('name', 'Unknown')}")
                print(f"  Created at: {project_info.get('created_at', 'Unknown')}")
        
        return True, ""
    except requests.exceptions.RequestException as e:
        error_msg = f"  ❌ Project API key failed: {e}"
        if hasattr(e, 'response') and e.response:
            error_msg += f"\n  Status code: {e.response.status_code}"
            error_msg += f"\n  Response: {e.response.text[:100]}"
        
        if verbose:
            print(error_msg)
        
        return False, error_msg

def test_personal_api_key(api_key, project_id, api_url, verbose=False):
    """
    Test a PostHog Personal API key (likely starting with phx_).
    
    Args:
        api_key: PostHog Personal API key
        project_id: PostHog project ID
        api_url: PostHog API URL
        verbose: Whether to print detailed information
        
    Returns:
        (bool, str): (Success status, Error message or '')
    """
    if verbose:
        print(f"Testing Personal API key {api_key[:5]}...{api_key[-5:]}")
    
    # Personal API keys should use Bearer token
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    endpoint = f"{api_url}/projects/{project_id}"
    
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        
        if verbose:
            print(f"  ✅ Personal API key works! Status: {response.status_code}")
            if response.status_code == 200:
                project_info = response.json()
                print(f"  Project name: {project_info.get('name', 'Unknown')}")
                print(f"  Created at: {project_info.get('created_at', 'Unknown')}")
        
        return True, ""
    except requests.exceptions.RequestException as e:
        error_msg = f"  ❌ Personal API key failed: {e}"
        if hasattr(e, 'response') and e.response:
            error_msg += f"\n  Status code: {e.response.status_code}"
            error_msg += f"\n  Response: {e.response.text[:100]}"
        
        if verbose:
            print(error_msg)
        
        return False, error_msg

def test_sessions_api(api_key, project_id, api_url, is_project_key=True, verbose=False):
    """
    Test the Sessions Recordings API with the given credentials.
    
    Args:
        api_key: PostHog API key
        project_id: PostHog project ID
        api_url: PostHog API URL
        is_project_key: Whether the API key is a Project API key
        verbose: Whether to print detailed information
        
    Returns:
        (bool, str): (Success status, Error message or '')
    """
    if verbose:
        print(f"Testing Sessions Recordings API...")
    
    # Set appropriate headers based on key type
    if is_project_key:
        headers = {
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "application/json"
        }
    else:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    # Calculate date range (last 30 days)
    date_to = datetime.now()
    date_from = date_to - timedelta(days=30)
    
    endpoint = f"{api_url}/projects/{project_id}/session_recordings"
    params = {
        "limit": 5,
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat()
    }
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        result_count = len(data.get("results", []))
        
        if verbose:
            print(f"  ✅ Sessions API works! Status: {response.status_code}")
            print(f"  Retrieved {result_count} session recordings")
        
        return True, ""
    except requests.exceptions.RequestException as e:
        error_msg = f"  ❌ Sessions API failed: {e}"
        if hasattr(e, 'response') and e.response:
            error_msg += f"\n  Status code: {e.response.status_code}"
            error_msg += f"\n  Response: {e.response.text[:100]}"
        
        if verbose:
            print(error_msg)
        
        return False, error_msg

def test_events_api(api_key, project_id, api_url, is_project_key=True, verbose=False):
    """
    Test the Events API with the given credentials.
    
    Args:
        api_key: PostHog API key
        project_id: PostHog project ID
        api_url: PostHog API URL
        is_project_key: Whether the API key is a Project API key
        verbose: Whether to print detailed information
        
    Returns:
        (bool, str): (Success status, Error message or '')
    """
    if verbose:
        print(f"Testing Events API...")
    
    # Set appropriate headers based on key type
    if is_project_key:
        headers = {
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "application/json"
        }
    else:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    # Calculate date range (last 30 days)
    date_to = datetime.now()
    date_from = date_to - timedelta(days=30)
    
    endpoint = f"{api_url}/projects/{project_id}/events"
    params = {
        "limit": 5,
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat()
    }
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        result_count = len(data.get("results", []))
        
        if verbose:
            print(f"  ✅ Events API works! Status: {response.status_code}")
            print(f"  Retrieved {result_count} events")
        
        return True, ""
    except requests.exceptions.RequestException as e:
        error_msg = f"  ❌ Events API failed: {e}"
        if hasattr(e, 'response') and e.response:
            error_msg += f"\n  Status code: {e.response.status_code}"
            error_msg += f"\n  Response: {e.response.text[:100]}"
        
        if verbose:
            print(error_msg)
        
        return False, error_msg

def update_env_file(api_key, project_id, api_url, is_project_key, verbose=False):
    """
    Update the .env file with the working credentials.
    
    Args:
        api_key: PostHog API key
        project_id: PostHog project ID
        api_url: PostHog API URL
        is_project_key: Whether the API key is a Project API key
        verbose: Whether to print detailed information
        
    Returns:
        bool: Success status
    """
    env_file_path = Path(root_dir) / '.env'
    
    if not env_file_path.exists():
        if verbose:
            print(f"❌ .env file not found at {env_file_path}")
        return False
    
    try:
        # Read existing .env file
        with open(env_file_path, 'r') as f:
            env_lines = f.readlines()
        
        # Update or add PostHog configuration
        updated_lines = []
        posthog_vars_found = {
            'POSTHOG_API_KEY': False,
            'POSTHOG_PROJECT_ID': False,
            'POSTHOG_API_URL': False,
            'ANALYTICS_PROVIDER': False
        }
        
        for line in env_lines:
            line = line.rstrip('\n')
            if line.startswith('POSTHOG_API_KEY='):
                updated_lines.append(f'POSTHOG_API_KEY={api_key}')
                posthog_vars_found['POSTHOG_API_KEY'] = True
            elif line.startswith('POSTHOG_PROJECT_ID='):
                updated_lines.append(f'POSTHOG_PROJECT_ID={project_id}')
                posthog_vars_found['POSTHOG_PROJECT_ID'] = True
            elif line.startswith('POSTHOG_API_URL='):
                updated_lines.append(f'POSTHOG_API_URL={api_url}')
                posthog_vars_found['POSTHOG_API_URL'] = True
            elif line.startswith('ANALYTICS_PROVIDER='):
                updated_lines.append('ANALYTICS_PROVIDER=posthog')
                posthog_vars_found['ANALYTICS_PROVIDER'] = True
            else:
                updated_lines.append(line)
        
        # Add missing variables
        if not posthog_vars_found['POSTHOG_API_KEY']:
            updated_lines.append(f'POSTHOG_API_KEY={api_key}')
        if not posthog_vars_found['POSTHOG_PROJECT_ID']:
            updated_lines.append(f'POSTHOG_PROJECT_ID={project_id}')
        if not posthog_vars_found['POSTHOG_API_URL']:
            updated_lines.append(f'POSTHOG_API_URL={api_url}')
        if not posthog_vars_found['ANALYTICS_PROVIDER']:
            updated_lines.append('ANALYTICS_PROVIDER=posthog')
        
        # Add a comment about API key type if not present
        key_type_line = f'# Using PostHog {"Project" if is_project_key else "Personal"} API Key'
        if key_type_line not in updated_lines:
            # Find the index of POSTHOG_API_KEY line
            for i, line in enumerate(updated_lines):
                if line.startswith('POSTHOG_API_KEY='):
                    # Insert comment line before API key
                    updated_lines.insert(i, key_type_line)
                    break
        
        # Write updated .env file
        with open(env_file_path, 'w') as f:
            f.write('\n'.join(updated_lines) + '\n')
        
        if verbose:
            print(f"✅ Updated .env file at {env_file_path}")
        
        return True
    except Exception as e:
        if verbose:
            print(f"❌ Failed to update .env file: {e}")
        return False

def main():
    """Main function."""
    args = setup_args()
    verbose = args.verbose
    
    print("==== PostHog API Authentication Troubleshooter ====")
    
    # Get credentials
    api_key, project_id, api_url = get_env_variables(args)
    
    if not api_key:
        print("❌ No PostHog API key provided or found in environment variables.")
        return False
    
    if not project_id:
        print("❌ No PostHog project ID provided or found in environment variables.")
        return False
    
    print(f"Testing PostHog API credentials for project {project_id}")
    print(f"API URL: {api_url}")
    print(f"API Key: {api_key[:5]}...{api_key[-5:]}")
    
    # Determine API key type
    is_project_key = api_key.startswith('phc_')
    is_personal_key = api_key.startswith('phx_')
    
    print(f"API Key Type: {'Project' if is_project_key else 'Personal' if is_personal_key else 'Unknown'}")
    
    # Test API key based on its type
    project_key_works = False
    personal_key_works = False
    
    if is_project_key:
        project_key_works, error_msg = test_project_api_key(api_key, project_id, api_url, verbose)
        if not project_key_works:
            # Try as personal key as fallback
            personal_key_works, _ = test_personal_api_key(api_key, project_id, api_url, verbose)
    elif is_personal_key:
        personal_key_works, error_msg = test_personal_api_key(api_key, project_id, api_url, verbose)
        if not personal_key_works:
            # Try as project key as fallback
            project_key_works, _ = test_project_api_key(api_key, project_id, api_url, verbose)
    else:
        # Unknown key type, try both
        project_key_works, _ = test_project_api_key(api_key, project_id, api_url, verbose)
        personal_key_works, _ = test_personal_api_key(api_key, project_id, api_url, verbose)
    
    # Determine the working key type
    is_working_key_project = project_key_works
    is_working_key_personal = personal_key_works and not project_key_works
    
    if project_key_works or personal_key_works:
        print("\n✅ API key authentication working!")
        print(f"Working as: {'Project key' if is_working_key_project else 'Personal key'}")
        
        # Test specific API endpoints
        sessions_works, _ = test_sessions_api(api_key, project_id, api_url, is_working_key_project, verbose)
        events_works, _ = test_events_api(api_key, project_id, api_url, is_working_key_project, verbose)
        
        print("\n=== API Endpoints Status ===")
        print(f"Sessions API: {'✅ Working' if sessions_works else '❌ Not working'}")
        print(f"Events API: {'✅ Working' if events_works else '❌ Not working'}")
        
        if args.save:
            updated = update_env_file(api_key, project_id, api_url, is_working_key_project, verbose)
            if updated:
                print("\n✅ Credentials saved to .env file")
                print(f"Authorization header will use: {'Api-Key' if is_working_key_project else 'Bearer'}")
            else:
                print("\n❌ Failed to update .env file")
        
    else:
        print("\n❌ API key authentication failed with both Project and Personal authentication methods")
        print("Please check your API key and project ID")
        
        # Provide suggestions
        print("\nSuggestions:")
        print("1. Verify your API key and project ID are correct")
        print("2. Check if your API key has the necessary permissions")
        print("3. If you're using a Project API key, try a Personal API key instead (or vice versa)")
        print("4. Check if your PostHog instance requires a different authentication method")
        
        return False
    
    return True

if __name__ == "__main__":
    main() 