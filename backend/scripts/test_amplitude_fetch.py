"""
Test script to fetch real data from Amplitude

Usage:
    python test_amplitude_fetch.py [--start YYYYMMDD] [--end YYYYMMDD] [--days N] [--interval {1,7,30}] [--limit N]
    
Examples:
    python test_amplitude_fetch.py --days 7                     # Last 7 days
    python test_amplitude_fetch.py --start 20230101 --end 20230131  # Specific date range
    python test_amplitude_fetch.py --interval 7                 # Weekly data for last 30 days
"""
import os
import sys
import json
import logging
import argparse
from datetime import datetime, timedelta
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

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Fetch data from Amplitude API")
    
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument('--days', type=int, default=7,
                          help="Number of days to fetch data for (default: 7)")
    date_group.add_argument('--start', type=str,
                          help="Start date in format YYYYMMDD (e.g., 20230101)")
    
    parser.add_argument('--end', type=str,
                      help="End date in format YYYYMMDD (e.g., 20230131)")
    parser.add_argument('--interval', type=int, choices=[1, 7, 30], default=1,
                      help="Interval for data aggregation: 1=daily, 7=weekly, 30=monthly (default: 1)")
    parser.add_argument('--limit', type=int, default=5,
                      help="Number of sample events to display (default: 5)")
    parser.add_argument('--output-dir', type=str, default="output",
                      help="Directory to save output files (default: 'output')")
    
    return parser.parse_args()

def format_amplitude_date(date_obj, is_end_date=False):
    """Format date for Amplitude API in YYYYMMDDTHH format"""
    hour = "23" if is_end_date else "00"
    return date_obj.strftime(f"%Y%m%dT{hour}")

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Set up dates based on arguments
    end_date = datetime.now()
    
    if args.start:
        try:
            start_date = datetime.strptime(args.start, "%Y%m%d")
            if args.end:
                end_date = datetime.strptime(args.end, "%Y%m%d")
        except ValueError:
            logger.error("Invalid date format. Use YYYYMMDD (e.g., 20230101)")
            sys.exit(1)
    else:
        # Use days argument for relative date
        start_date = end_date - timedelta(days=args.days)
    
    logger.info(f"Fetching data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"Using interval: {args.interval} day(s)")
    
    # Initialize client
    try:
        client = AmplitudeClient()
    except ValueError as e:
        logger.error(f"Failed to initialize Amplitude client: {e}")
        logger.error("Check your environment variables for AMPLITUDE_API_KEY and AMPLITUDE_SECRET_KEY")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Get data from Amplitude
        events = client.get_data(start_date, end_date)
        logger.info(f"Successfully retrieved {len(events)} events")
        
        # Display events summary
        print("\n" + "="*50)
        print(f"=== AMPLITUDE EVENTS SUMMARY ===")
        print("="*50)
        print(f"Total events: {len(events)}")
        print(f"Date range: {start_date.date()} to {end_date.date()}")
        print(f"Interval: {args.interval} day(s)")
        print(f"API query: start={format_amplitude_date(start_date)}, end={format_amplitude_date(end_date, is_end_date=True)}")
        
        # Display event type distribution
        event_types = {}
        for event in events:
            event_type = event.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        print("\n=== Event Type Distribution ===")
        for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"{event_type}: {count} events ({count/len(events)*100:.1f}%)")
        
        # Display sample events
        print(f"\n=== Sample Events (first {args.limit}) ===")
        for i, event in enumerate(events[:args.limit], 1):
            print(f"\nEvent {i}:")
            details = display_event_details(event)
            print(json.dumps(details, indent=2, ensure_ascii=False))
        
        # Try to fetch session replay for first event with replay ID
        session_replays_found = 0
        processed_session_ids = set()  # Track which session IDs we've already processed
        
        for event in events:
            session_id = get_session_replay_id(event)
            if session_id and session_id not in processed_session_ids and session_replays_found < 3:  # Limit to 3 session replays
                processed_session_ids.add(session_id)  # Mark this session ID as processed
                print(f"\n=== Fetching Session Replay for ID: {session_id} ===")
                try:
                    replay_data = client.get_session_replay(session_id)
                    
                    # Save replay data to file
                    replay_file = output_dir / f"session_replay_{session_id.replace('/', '_')}.json"
                    
                    with open(replay_file, 'w', encoding='utf-8') as f:
                        json.dump(replay_data, f, indent=2, ensure_ascii=False)
                    print(f"Session replay data saved to {replay_file}")
                    
                    session_replays_found += 1
                except Exception as e:
                    print(f"Failed to fetch session replay: {e}")
        
        # Save all events to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = output_dir / f"amplitude_events_{timestamp}.json"
        save_events_to_file(events, filename)
        
        print("\n" + "="*50)
        print(f"All events saved to {filename}")
        print("="*50)
            
    except AmplitudeError as e:
        logger.error(f"Amplitude API error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 