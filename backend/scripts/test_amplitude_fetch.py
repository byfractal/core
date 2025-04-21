"""
Test script to fetch real data from Amplitude
"""
import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from services.amplitude.client import AmplitudeClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_events_to_file(events, filename):
    """Save events to a JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    logger.info(f"Events saved to {filename}")

def display_event_details(event):
    """Display important details of an event"""
    important_fields = [
        'event_type', 'event_id', 'user_id', 'device_id',
        'event_time', 'platform', 'os_name', 'device_type'
    ]
    
    details = {k: event.get(k) for k in important_fields if k in event}
    
    # Add user properties if they exist
    if 'user_properties' in event:
        details['user_properties'] = event['user_properties']
    
    # Add event properties if they exist
    if 'event_properties' in event:
        details['event_properties'] = event['event_properties']
    
    return details

def get_session_replay_id(event):
    """Extract session replay ID from event if it exists"""
    event_props = event.get('event_properties', {})
    return event_props.get('[Amplitude] Session Replay ID')

def main():
    # Initialize client
    client = AmplitudeClient()
    
    # Get data for last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    try:
        events = client.get_data(start_date, end_date)
        logger.info(f"Successfully retrieved {len(events)} events")
        
        # Display events summary
        print("\n=== Events Summary ===")
        print(f"Total events: {len(events)}")
        print(f"Date range: {start_date.date()} to {end_date.date()}")
        
        # Display first 5 events with details
        print("\n=== Sample Events (first 5) ===")
        for i, event in enumerate(events[:5], 1):
            print(f"\nEvent {i}:")
            details = display_event_details(event)
            print(json.dumps(details, indent=2, ensure_ascii=False))
        
        # Try to fetch session replay for first event with replay ID
        for event in events:
            session_id = get_session_replay_id(event)
            if session_id:
                print(f"\n=== Fetching Session Replay for ID: {session_id} ===")
                try:
                    replay_data = client.get_session_replay(session_id)
                    
                    # Save replay data to file
                    output_dir = Path("output")
                    output_dir.mkdir(exist_ok=True)
                    replay_file = output_dir / f"session_replay_{session_id.replace('/', '_')}.json"
                    
                    with open(replay_file, 'w', encoding='utf-8') as f:
                        json.dump(replay_data, f, indent=2, ensure_ascii=False)
                    print(f"Session replay data saved to {replay_file}")
                    
                    # Only process first replay found
                    break
                except Exception as e:
                    print(f"Failed to fetch session replay: {e}")
        
        # Save all events to file
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        filename = output_dir / f"amplitude_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_events_to_file(events, filename)
            
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise

if __name__ == "__main__":
    main() 