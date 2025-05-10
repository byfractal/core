"""
Process raw Amplitude data files into a format suitable for analysis.
"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from services.amplitude.data_processor import process_raw_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_latest_data() -> None:
    """
    Process the most recent raw Amplitude data file and save the processed events.
    """
    try:
        # Set up paths
        data_dir = backend_dir.parent / "data" / "amplitude_data"
        raw_dir = data_dir / "raw"
        processed_dir = data_dir / "processed"
        
        # Create directories if they don't exist
        raw_dir.mkdir(parents=True, exist_ok=True)
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Find the most recent .gz file
        gz_files = list(raw_dir.glob("*.gz"))
        if not gz_files:
            logger.error("No raw data files found in data/amplitude_data/raw")
            return
            
        latest_file = max(gz_files, key=lambda x: x.stat().st_mtime)
        
        # Process the file
        events = process_raw_file(latest_file)
        
        # Transform events into the desired format
        processed_events = []
        for event in events:
            processed_event = {
                "event_type": event.get("event_type"),
                "event_id": event.get("event_id"),
                "user_id": event.get("user_id"),
                "device_id": event.get("device_id"),
                "time": event.get("time"),
                "app_version": event.get("app_version"),
                "platform": event.get("platform"),
                "os_name": event.get("os_name"),
                "os_version": event.get("os_version"),
                "device_model": event.get("device_model"),
                "country": event.get("country"),
                "region": event.get("region"),
                "city": event.get("city"),
                "event_properties": event.get("event_properties", {}),
                "user_properties": event.get("user_properties", {})
            }
            processed_events.append(processed_event)
            
        # Save processed events
        output_file = processed_dir / "latest.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_events, f, indent=2)
            
        logger.info(f"Processed {len(processed_events)} events")
        logger.info(f"Output saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        raise

if __name__ == "__main__":
    process_latest_data() 