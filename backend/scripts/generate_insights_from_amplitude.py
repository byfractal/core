"""
Script to generate UX insights from Amplitude event data.
This script:
1. Reads Amplitude event data from JSON files
2. Processes events using existing analysis chains
3. Generates structured UX recommendations
4. Outputs recommendations in the format expected by the frontend
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging
from collections import defaultdict

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
import sys
sys.path.append(str(project_root))

# Import our analysis tools
from backend.models.analysis_chains import FeedbackAnalysisChains

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AmplitudeEventProcessor:
    """Processes Amplitude events to generate UX insights."""
    
    def __init__(self):
        """Initialize the processor with analysis chains."""
        self.analysis_chains = FeedbackAnalysisChains(model="gpt-4")
        
    def read_amplitude_events(self, file_path: str) -> List[Dict]:
        """Read events from an Amplitude JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                events = json.load(f)
            logger.info(f"Successfully loaded {len(events)} events from {file_path}")
            return events
        except Exception as e:
            logger.error(f"Error reading Amplitude events from {file_path}: {e}")
            return []

    def process_events(self, events: List[Dict]) -> List[Dict]:
        """
        Process Amplitude events to extract relevant user behavior patterns.
        Groups events by session and analyzes user flows and friction points.
        """
        # Group events by session
        sessions = defaultdict(list)
        for event in events:
            session_id = event.get('session_id')
            if session_id:
                sessions[session_id].append(event)
        
        insights = []
        for session_id, session_events in sessions.items():
            # Analyze user flow in this session
            session_insight = self._analyze_session(session_events)
            if session_insight:
                insights.append(session_insight)
        
        return insights

    def _analyze_session(self, events: List[Dict]) -> Dict:
        """
        Analyze a single session's events to identify UX patterns and issues.
        """
        # Extract relevant event data
        event_sequence = []
        for event in events:
            event_data = {
                'event_type': event.get('event_type'),
                'event_properties': event.get('event_properties', {}),
                'timestamp': event.get('event_time'),
                'page_url': event.get('event_properties', {}).get('[Amplitude] Page URL'),
                'page_title': event.get('event_properties', {}).get('[Amplitude] Page Title')
            }
            event_sequence.append(event_data)
        
        # Analyze the sequence for patterns
        return self._generate_insight_from_sequence(event_sequence)

    def _generate_insight_from_sequence(self, event_sequence: List[Dict]) -> Dict:
        """
        Generate UX insights from an event sequence.
        Returns insights in the format expected by the frontend.
        """
        # Analyze sequence for common patterns
        page_views = [e for e in event_sequence if e['event_type'] == '[Amplitude] Page Viewed']
        
        if not page_views:
            return None
        
        # Calculate time spent on pages
        page_times = defaultdict(float)
        for i in range(len(page_views) - 1):
            current = datetime.strptime(page_views[i]['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
            next_view = datetime.strptime(page_views[i + 1]['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
            duration = (next_view - current).total_seconds()
            page_times[page_views[i]['page_url']] += duration
        
        # Find pages with potential issues (e.g., long view times or quick exits)
        problematic_pages = []
        for page_url, time_spent in page_times.items():
            if time_spent > 120:  # More than 2 minutes on a page
                problematic_pages.append({
                    'url': page_url,
                    'time_spent': time_spent,
                    'type': 'high_time_spent'
                })
        
        # Generate insight card for each identified issue
        insights = []
        for problem in problematic_pages:
            insight = {
                "issueTitle": f"High time spent on page {problem['url']}",
                "severity": "needs-improvement",
                "rootCause": {
                    "context": "Users are spending unusually long time on this page",
                    "metric": {
                        "text": f"Avg. time spent: {problem['time_spent']:.1f} seconds",
                        "value": f"{problem['time_spent']:.1f}s"
                    },
                    "contextualData": "Extended page view times may indicate users are having trouble finding information or completing actions.",
                    "conversionImpact": "This could be causing increased drop-off rates",
                    "source": "Amplitude Analytics"
                },
                "recommendedFix": {
                    "suggestion": "Consider reviewing page layout and content organization. Ensure key actions are clearly visible.",
                    "source": "UX Best Practices"
                },
                "impactEstimate": "Optimizing this page could reduce average time spent by 40-60% and improve conversion rates",
                "tags": ["Layout", "Navigation", "User Flow"],
                "sources": ["Amplitude", "UX Analysis"]
            }
            insights.append(insight)
        
        return insights[0] if insights else None

    def generate_recommendations(self, input_file: str, output_file: str):
        """
        Main function to generate UX recommendations from Amplitude data.
        """
        # Read events
        events = self.read_amplitude_events(input_file)
        if not events:
            logger.error("No events found to process")
            return
        
        # Process events
        insights = self.process_events(events)
        
        # Format recommendations for frontend
        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "total_events_analyzed": len(events),
            "insights": insights
        }
        
        # Save recommendations
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(recommendations, f, indent=2)
            logger.info(f"Successfully wrote recommendations to {output_file}")
        except Exception as e:
            logger.error(f"Error writing recommendations: {e}")

def main():
    """Main execution function."""
    # Initialize processor
    processor = AmplitudeEventProcessor()
    
    # Get the latest Amplitude events file
    output_dir = project_root / "output"
    amplitude_files = list(output_dir.glob("amplitude_events_*.json"))
    if not amplitude_files:
        logger.error("No Amplitude event files found")
        return
    
    latest_file = max(amplitude_files, key=lambda x: x.stat().st_mtime)
    
    # Generate recommendations
    output_file = output_dir / "recommendations_output.json"
    processor.generate_recommendations(str(latest_file), str(output_file))
    
    # Synchroniser avec l'extension
    try:
        logger.info("Synchronizing insights with extension...")
        sync_script = project_root / "backend" / "scripts" / "sync_insights_to_extension.py"
        if sync_script.exists():
            import subprocess
            subprocess.run([sys.executable, str(sync_script)], check=True)
            logger.info("Synchronization completed successfully")
        else:
            logger.warning(f"Sync script not found at {sync_script}")
    except Exception as e:
        logger.error(f"Error synchronizing with extension: {e}")

if __name__ == "__main__":
    main() 