#!/usr/bin/env python3
"""
Script to fetch specific Amplitude session replays by ID.

Usage:
    python fetch_amplitude_sessions.py <session_id1> <session_id2> ...
    
Example:
    python fetch_amplitude_sessions.py "63bbee4f-fb94-46fd-bcd9-5c8d8fd209a1/1745192467517" 
"""
import os
import sys
import json
import logging
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from services.amplitude.client import AmplitudeClient, AmplitudeError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_replay_to_file(replay_data, filename):
    """Save replay data to a JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(replay_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Replay data saved to {filename}")

def main():
    # Get session IDs from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python fetch_amplitude_sessions.py <session_id1> <session_id2> ...")
        sys.exit(1)
    
    session_ids = sys.argv[1:]
    logger.info(f"Fetching session replays for {len(session_ids)} session IDs")
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Initialize Amplitude client
    try:
        client = AmplitudeClient()
    except ValueError as e:
        logger.error(f"Failed to initialize Amplitude client: {e}")
        logger.error("Check your environment variables for AMPLITUDE_API_KEY and AMPLITUDE_SECRET_KEY")
        sys.exit(1)
    
    # Fetch and save each session replay
    for session_id in session_ids:
        print(f"\n=== Fetching Session Replay for ID: {session_id} ===")
        try:
            replay_data = client.get_session_replay(session_id)
            
            # Save replay data to file (replace '/' in filename with '_')
            replay_file = output_dir / f"session_replay_{session_id.replace('/', '_')}.json"
            save_replay_to_file(replay_data, replay_file)
            
            # Print summary of the replay data
            print(f"Session replay retrieved for: {session_id}")
            if 'sessionId' in replay_data:
                print(f"Session ID: {replay_data['sessionId']}")
            if 'userId' in replay_data and replay_data['userId']:
                print(f"User ID: {replay_data['userId']}")
            if 'deviceId' in replay_data:
                print(f"Device ID: {replay_data['deviceId']}")
            if 'startTime' in replay_data:
                print(f"Start Time: {replay_data['startTime']}")
            if 'endTime' in replay_data:
                print(f"End Time: {replay_data['endTime']}")
            if 'eventCount' in replay_data:
                print(f"Event Count: {replay_data['eventCount']}")
            if 'pages' in replay_data and isinstance(replay_data['pages'], list):
                print(f"Number of Pages: {len(replay_data['pages'])}")
                for i, page in enumerate(replay_data['pages'], 1):
                    print(f"  Page {i}: {page.get('title', 'No title')} - {page.get('url', 'No URL')}")
            
        except Exception as e:
            print(f"Failed to fetch session replay for {session_id}: {e}")
    
    print("\n" + "="*50)
    print(f"Session replays fetched and saved to {output_dir} directory")
    print("="*50)

if __name__ == "__main__":
    main() 