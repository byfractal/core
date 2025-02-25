"""
Test script for Amplitude service integration.
Run this to verify the migration was successful.
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import json
import gzip

# Charger les variables d'environnement depuis .env
# Assurez-vous que le fichier .env est à la racine du projet
load_dotenv()

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ajout du répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.amplitude.client import AmplitudeClient
from backend.services.amplitude.data_processor import (
    save_data_to_file, process_raw_file, prepare_for_vectorization
)
from backend.services.amplitude.query_builder import build_query, build_event_payload

# Afficher les variables d'environnement pour le debug
logger.info(f"API_KEY present: {'API_KEY' in os.environ}")
logger.info(f"SECRET_KEY present: {'SECRET_KEY' in os.environ}")

def test_amplitude_query_builder():
    """Test the query builder functionality"""
    logger.info("Testing query builder...")
    
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()
    
    # Test basic query
    query = build_query(start_date, end_date, event_type="feedback")
    logger.info(f"Generated query: {query}")
    
    # Test event payload
    event = build_event_payload(
        user_id="test_user",
        device_id="test_device",
        event_type="test_event",
        event_properties={"feedback": "This is a test feedback", "page": "home"}
    )
    logger.info(f"Generated event payload: {event}")
    
    return True

def generate_mock_amplitude_data():
    """Generate mock Amplitude data for testing"""
    events = []
    for i in range(10):
        event = {
            "event_id": f"event_{i}",
            "user_id": f"user_{i % 3}",  # Repeat some users
            "device_id": f"device_{i % 5}",
            "event_type": "feedback" if i % 2 == 0 else "page_view",
            "time": int(datetime.now().timestamp() * 1000) - i * 3600000,
            "event_properties": {
                "feedback": f"This is test feedback number {i}. The product is {'great' if i % 3 == 0 else 'needs improvement'}.",
                "page": f"/page_{i % 4}",
                "rating": i % 5 + 1
            },
            "platform": "Web",
            "os_name": "MacOS",
            "device_family": "Mac"
        }
        events.append(event)
    
    # Convert to JSON and then to gzipped data
    events_json = "\n".join(json.dumps(event) for event in events)
    return gzip.compress(events_json.encode('utf-8'))

def test_amplitude_fetch(use_mock=False):
    """Test fetching data from Amplitude"""
    logger.info("Testing data fetching...")
    
    if use_mock:
        # Use mock data instead of real API
        logger.info("Using mock data instead of real API call")
        data = generate_mock_amplitude_data()
        filename = f"mock_amplitude_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gz"
        logger.info(f"Generated {len(data)} bytes of mock data")
        
        # Save data to file
        file_path = save_data_to_file(data, filename)
        logger.info(f"Saved mock data to {file_path}")
        
        return file_path
    else:
        client = AmplitudeClient()
        
        try:
            # Fetch data for last 7 days
            data, filename = client.fetch_data_for_period(days=7)
            logger.info(f"Successfully retrieved {len(data)} bytes of data")
            
            # Save data to file
            file_path = save_data_to_file(data, filename)
            logger.info(f"Saved data to {file_path}")
            
            return file_path
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None

def test_data_processing(file_path):
    """Test processing raw data file"""
    logger.info("Testing data processing...")
    
    if not file_path or not file_path.exists():
        logger.error("No file to process")
        return None
    
    try:
        # Process the raw file
        events = process_raw_file(file_path)
        logger.info(f"Processed {len(events)} events")
        
        # Prepare for vectorization
        documents = prepare_for_vectorization(events)
        logger.info(f"Created {len(documents)} documents for vectorization")
        
        # Print a sample document
        if documents:
            logger.info(f"Sample document: {documents[0]}")
        
        return documents
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return None

def main():
    """Run all tests"""
    logger.info("Starting Amplitude integration tests")
    
    # Test query builder
    if not test_amplitude_query_builder():
        logger.error("Query builder test failed")
        return
    
    # Test data fetching - passer True pour utiliser des données simulées
    file_path = test_amplitude_fetch(use_mock=True)
    if not file_path:
        logger.error("Data fetching test failed")
        return
    
    # Test data processing
    documents = test_data_processing(file_path)
    if not documents:
        logger.error("Data processing test failed")
        return
    
    logger.info("All tests completed successfully!")

if __name__ == "__main__":
    main() 