"""
Test script to verify Amplitude API connection and data fetching.
"""
from datetime import datetime, timedelta
from client import AmplitudeClient
import logging
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_environment():
    """
    Load environment variables from the correct .env file
    """
    # Get the project root directory (3 levels up from current file)
    project_root = Path(__file__).parent.parent.parent.parent
    env_path = project_root / '.env'
    
    if not env_path.exists():
        logger.error(f"❌ .env file not found at {env_path}")
        return False
        
    logger.info(f"Loading environment from: {env_path}")
    load_dotenv(env_path)
    return True

def test_amplitude_connection():
    """
    Test the connection to Amplitude API and fetch some data.
    """
    try:
        # Initialize the client
        logger.info("Initializing Amplitude client...")
        client = AmplitudeClient()
        
        # Test data fetching for last 7 days
        logger.info("Attempting to fetch data for the last 7 days...")
        data, filename = client.fetch_data_for_period(days=7)
        
        # Save the data to a file in the backend/data/amplitude directory
        output_dir = Path(__file__).parent.parent.parent / "data" / "amplitude"
        output_dir.mkdir(parents=True, exist_ok=True)
            
        output_path = output_dir / filename
        with open(output_path, "wb") as f:
            f.write(data)
            
        logger.info(f"Successfully fetched and saved data to: {output_path}")
        logger.info(f"Data size: {len(data)} bytes")
        
        return True
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting Amplitude connection test...")
    
    # Load environment variables from the correct location
    if not load_environment():
        sys.exit(1)
    
    # Check if environment variables are set
    if not os.getenv("AMPLITUDE_API_KEY") or not os.getenv("AMPLITUDE_SECRET_KEY"):
        logger.error("ERROR: Please set AMPLITUDE_API_KEY and AMPLITUDE_SECRET_KEY environment variables")
        sys.exit(1)
        
    # Log the values (masked) to verify they're loaded
    api_key = os.getenv("AMPLITUDE_API_KEY", "")
    secret_key = os.getenv("AMPLITUDE_SECRET_KEY", "")
    logger.info(f"API Key loaded (first 4 chars): {api_key[:4]}...")
    logger.info(f"Secret Key loaded (first 4 chars): {secret_key[:4]}...")
    
    # Run the test
    success = test_amplitude_connection()
    
    if success:
        logger.info("✅ Test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Test failed!")
        sys.exit(1) 