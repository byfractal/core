"""
Test script for PostHog integration functionality.

This script tests the interaction with the PostHog API and the functionality
of the design recommendation components.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to enable imports
parent_dir = str(Path(__file__).parent.parent)
sys.path.append(parent_dir)

# Import the modules to test
from models.design_recommendations import (
    PostHogClient,
    DesignSuggestionGenerator,
    DesignRecommendationChain,
    fetch_session_recordings,
    download_session_data
)

def test_posthog_connection():
    """Test the connection to the PostHog API"""
    print("\n=== Testing PostHog Connection ===")
    
    # Check if environment variables are set
    api_key = os.getenv("POSTHOG_API_KEY")
    project_id = os.getenv("POSTHOG_PROJECT_ID")
    api_url = os.getenv("POSTHOG_API_URL")
    
    if not all([api_key, project_id, api_url]):
        print("❌ Error: PostHog environment variables are not set")
        print("Please set POSTHOG_API_KEY, POSTHOG_PROJECT_ID, and POSTHOG_API_URL in your .env file")
        return False
    
    # Create a client instance
    try:
        client = PostHogClient()
        print(f"✅ Successfully initialized PostHogClient with project ID: {client.project_id}")
        
        # Try a simple API call
        date_from = (datetime.now() - timedelta(days=7)).isoformat()
        date_to = datetime.now().isoformat()
        
        response = client._fetch_session_recordings(date_from=date_from, date_to=date_to, limit=1)
        
        if "results" in response:
            print(f"✅ Successfully connected to PostHog API")
            print(f"   Found {len(response['results'])} session recordings in the last 7 days")
            return True
        else:
            print("❌ Error: Failed to get results from PostHog API")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_fetch_sessions():
    """Test fetching session recordings"""
    print("\n=== Testing Session Recording Fetching ===")
    
    try:
        # Test the standalone function
        print("Testing standalone fetch_session_recordings function...")
        sessions = fetch_session_recordings(date_from=(datetime.now() - timedelta(days=7)).isoformat())
        
        if "results" in sessions:
            print(f"✅ Successfully fetched {len(sessions['results'])} session recordings with standalone function")
        else:
            print("❌ Error: Failed to fetch session recordings with standalone function")
        
        # Test the client class method
        print("\nTesting PostHogClient._fetch_session_recordings method...")
        client = PostHogClient()
        client_sessions = client._fetch_session_recordings(date_from=(datetime.now() - timedelta(days=7)).isoformat())
        
        if "results" in client_sessions:
            print(f"✅ Successfully fetched {len(client_sessions['results'])} session recordings with client method")
            
            if len(client_sessions['results']) > 0:
                session = client_sessions['results'][0]
                print(f"   Sample session ID: {session.get('id', 'N/A')}")
                print(f"   Created at: {session.get('created_at', 'N/A')}")
                return True
            else:
                print("   Note: No session recordings found in the specified time range")
                return True
        else:
            print("❌ Error: Failed to fetch session recordings with client method")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_download_session_data():
    """Test downloading detailed session data"""
    print("\n=== Testing Session Data Download ===")
    
    try:
        # First get a session ID
        client = PostHogClient()
        sessions = client._fetch_session_recordings(date_from=(datetime.now() - timedelta(days=30)).isoformat(), limit=1)
        
        if not sessions.get('results'):
            print("ℹ️ No sessions found to test download. Skipping this test.")
            return None
        
        session_id = sessions['results'][0].get('id')
        if not session_id:
            print("❌ Error: Session ID not found in results")
            return False
        
        print(f"Testing session data download for session: {session_id}")
        
        # Test standalone function
        print("Testing standalone download_session_data function...")
        session_data = download_session_data(session_id)
        
        if session_data:
            print(f"✅ Successfully downloaded session data with standalone function")
        else:
            print("❌ Error: Failed to download session data with standalone function")
        
        # Test client method
        print("\nTesting PostHogClient.get_session_details method...")
        client_session_data = client.get_session_details(session_id)
        
        if client_session_data:
            print(f"✅ Successfully downloaded session data with client method")
            
            # Print some details about the session
            if 'events' in client_session_data:
                print(f"   Number of events: {len(client_session_data['events'])}")
                
                # Count event types
                event_types = {}
                for event in client_session_data['events']:
                    event_type = event.get('type', 'unknown')
                    event_types[event_type] = event_types.get(event_type, 0) + 1
                
                print("   Event types:")
                for event_type, count in event_types.items():
                    print(f"     - {event_type}: {count}")
                
            return True
        else:
            print("❌ Error: Failed to download session data with client method")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_page_specific_sessions():
    """Test getting sessions for a specific page"""
    print("\n=== Testing Page-Specific Session Fetching ===")
    
    try:
        client = PostHogClient()
        
        # Test with a sample page - adjust this to match a page in your application
        test_page = "/dashboard"  # Change this to a page you know exists
        print(f"Testing session fetching for page: {test_page}")
        
        sessions = client.get_sessions_for_page(test_page, days=30)
        
        print(f"✅ Found {len(sessions)} sessions for page {test_page}")
        if len(sessions) > 0:
            print("   Sample session details:")
            print(f"   - ID: {sessions[0].get('id', 'N/A')}")
            print(f"   - Duration: {sessions[0].get('duration', 'N/A')}")
            
            # Check if we have any events
            if 'events' in sessions[0]:
                print(f"   - Events: {len(sessions[0]['events'])}")
            
        return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_design_suggestion_generation():
    """Test generating design suggestions from session data"""
    print("\n=== Testing Design Suggestion Generation ===")
    
    try:
        generator = DesignSuggestionGenerator()
        
        # Test with a sample page - adjust this to match a page in your application
        test_page = "/dashboard"  # Change this to a page you know exists
        print(f"Testing suggestion generation for page: {test_page}")
        
        suggestions = generator.generate_layout_suggestions(test_page, date_range=30)
        
        if suggestions:
            print(f"✅ Successfully generated design suggestions")
            
            if "layout_improvements" in suggestions:
                print(f"   Layout improvements: {len(suggestions['layout_improvements'])}")
            
            if "ui_element_changes" in suggestions:
                print(f"   UI element changes: {len(suggestions['ui_element_changes'])}")
            
            if "flow_improvements" in suggestions:
                print(f"   Flow improvements: {len(suggestions['flow_improvements'])}")
            
            # Print a sample suggestion
            print("\n   Sample suggestions:")
            
            if suggestions.get('layout_improvements'):
                sample = suggestions['layout_improvements'][0]
                print(f"   Layout: {sample.get('suggestion')} ({sample.get('priority')}) - {sample.get('reason')}")
            
            if suggestions.get('ui_element_changes'):
                sample = suggestions['ui_element_changes'][0]
                print(f"   UI: {sample.get('suggestion')} ({sample.get('priority')}) - {sample.get('reason')}")
            
            if suggestions.get('flow_improvements'):
                sample = suggestions['flow_improvements'][0]
                print(f"   Flow: {sample.get('suggestion')} ({sample.get('priority')}) - {sample.get('reason')}")
            
            return True
        else:
            print("❌ Error: Failed to generate design suggestions")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_design_recommendation_chain():
    """Test the design recommendation chain"""
    print("\n=== Testing Design Recommendation Chain ===")
    
    try:
        # Create a design recommendation chain
        chain = DesignRecommendationChain(model="gpt-3.5-turbo")
        
        # Create sample analysis summary
        sample_summary = {
            "summary": "Users find the checkout process confusing and lengthy. The form has too many fields and the submit button is difficult to locate. Mobile users report additional issues.",
            "key_issues": [
                "Lengthy checkout process",
                "Too many form fields",
                "Hard to find submit button"
            ],
            "positive_aspects": [
                "Professional website appearance",
                "Good color scheme"
            ],
            "overall_sentiment": "Mixed, with frustration around checkout"
        }
        
        # Test the chain
        print("Generating design recommendations from sample analysis...")
        recommendations = chain.generate_recommendations(sample_summary, "checkout_page")
        
        if recommendations:
            print(f"✅ Successfully generated design recommendations")
            
            if "recommendations" in recommendations:
                print(f"   Number of recommendations: {len(recommendations['recommendations'])}")
                
                if recommendations['recommendations']:
                    sample = recommendations['recommendations'][0]
                    print(f"\n   Sample recommendation:")
                    print(f"   - Title: {sample.get('title', 'N/A')}")
                    print(f"   - Description: {sample.get('description', 'N/A')}")
                    print(f"   - Priority: {sample.get('priority', 'N/A')}")
                    print(f"   - Component: {sample.get('component', 'N/A')}")
            
            if "implementation_notes" in recommendations:
                print(f"\n   Implementation notes: {recommendations['implementation_notes'][:100]}...")
            
            return True
        else:
            print("❌ Error: Failed to generate design recommendations")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_feedback_retrieval():
    """Test retrieving feedback events for a specific page"""
    print("\n=== Testing Feedback Retrieval ===")
    
    try:
        client = PostHogClient()
        
        # Test with a sample page - adjust this to match a page in your application
        test_page = "/dashboard"  # Change this to a page you know exists
        print(f"Testing feedback retrieval for page: {test_page}")
        
        feedback = client.get_feedback_for_page(test_page, days=30)
        
        print(f"✅ Found {len(feedback)} feedback events for page {test_page}")
        if len(feedback) > 0:
            print("   Sample feedback details:")
            sample = feedback[0]
            print(f"   - Event ID: {sample.get('id', 'N/A')}")
            print(f"   - Timestamp: {sample.get('timestamp', 'N/A')}")
            
            # Check for properties or text
            if 'properties' in sample:
                props = sample['properties']
                if 'text' in props:
                    print(f"   - Feedback text: {props['text']}")
                if 'rating' in props:
                    print(f"   - Rating: {props['rating']}")
            
        return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and summarize results"""
    print("\n======================================")
    print("RUNNING POSTHOG INTEGRATION TESTS")
    print("======================================\n")
    
    results = {}
    
    # Run connection test first - skip other tests if this fails
    results["connection"] = test_posthog_connection()
    if not results["connection"]:
        print("\n❌ PostHog connection failed. Skipping remaining tests.")
        return summarize_results(results)
    
    # Run the remaining tests
    results["fetch_sessions"] = test_fetch_sessions()
    results["download_session"] = test_download_session_data()
    results["page_sessions"] = test_page_specific_sessions()
    results["feedback"] = test_feedback_retrieval()
    results["suggestions"] = test_design_suggestion_generation()
    results["recommendations"] = test_design_recommendation_chain()
    
    return summarize_results(results)

def summarize_results(results):
    """Summarize the test results"""
    print("\n======================================")
    print("TEST RESULTS SUMMARY")
    print("======================================")
    
    successful = 0
    failed = 0
    skipped = 0
    
    for test, result in results.items():
        if result is True:
            status = "✅ PASSED"
            successful += 1
        elif result is False:
            status = "❌ FAILED"
            failed += 1
        else:
            status = "ℹ️ SKIPPED"
            skipped += 1
            
        print(f"{status} - {test}")
    
    print("\n-------------------------------------")
    print(f"Total tests: {len(results)}")
    print(f"Passed: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print("-------------------------------------\n")
    
    if failed == 0:
        print("🎉 All executed tests passed!")
    else:
        print(f"⚠️ {failed} test(s) failed. Please review the output above.")
    
    return failed == 0

if __name__ == "__main__":
    run_all_tests() 