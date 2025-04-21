#!/usr/bin/env python3
"""
Script pour générer un rapport détaillé des sessions Amplitude.

Usage:
    python generate_session_report.py <fichier_events.json> [--output rapport.md]
    
Example:
    python generate_session_report.py output/amplitude_events_20250421_125829.json
"""
import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Générer un rapport de sessions Amplitude")
    
    parser.add_argument('input_file', type=str, help="Fichier JSON contenant les événements Amplitude")
    parser.add_argument('--output', type=str, default=None, 
                        help="Fichier de sortie pour le rapport (par défaut: session_report_YYYYMMDD_HHMMSS.md)")
    
    return parser.parse_args()

def extract_sessions(events):
    """Extraire et regrouper les événements par session"""
    sessions = defaultdict(list)
    
    # Group events by session ID
    for event in events:
        session_id = event.get("event_properties", {}).get("[Amplitude] Session Replay ID")
        if session_id:
            sessions[session_id].append(event)
    
    return sessions

def get_page_view_sequence(events):
    """Extraire la séquence des pages consultées"""
    page_views = []
    
    # Sort events by event_time
    sorted_events = sorted(events, key=lambda e: e.get("event_time", ""))
    
    # Extract page view events
    for event in sorted_events:
        event_type = event.get("event_type")
        if event_type == "[Amplitude] Page Viewed":
            page_url = event.get("event_properties", {}).get("[Amplitude] Page URL")
            page_title = event.get("event_properties", {}).get("[Amplitude] Page Title")
            
            if page_url:
                page_views.append({
                    "url": page_url,
                    "title": page_title,
                    "time": event.get("event_time")
                })
    
    return page_views

def get_clicked_elements(events):
    """Extraire les éléments cliqués"""
    clicks = []
    
    # Sort events by event_time
    sorted_events = sorted(events, key=lambda e: e.get("event_time", ""))
    
    # Extract click events
    for event in sorted_events:
        if event.get("event_type") == "[Amplitude] Element Clicked":
            element_id = event.get("event_properties", {}).get("[Amplitude] Element ID")
            element_tag = event.get("event_properties", {}).get("[Amplitude] Element Tag Name")
            element_text = event.get("event_properties", {}).get("[Amplitude] Element Text")
            
            clicks.append({
                "element_id": element_id,
                "element_tag": element_tag,
                "element_text": element_text,
                "time": event.get("event_time"),
                "page_url": event.get("event_properties", {}).get("[Amplitude] Page URL"),
            })
    
    return clicks

def calculate_session_metrics(events):
    """Calculer les métriques de la session"""
    # Sort events by event_time
    sorted_events = sorted(events, key=lambda e: e.get("event_time", ""))
    
    # If no events, return empty metrics
    if not sorted_events:
        return {}
    
    # Get the first and last event times
    start_time_str = sorted_events[0].get("event_time", "")
    end_time_str = sorted_events[-1].get("event_time", "")
    
    # Convert to datetime objects
    try:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S.%f")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S.%f") 
        duration = end_time - start_time
        
        # Count event types
        event_types = defaultdict(int)
        for event in sorted_events:
            event_type = event.get("event_type", "unknown")
            event_types[event_type] += 1
        
        # Count unique pages
        pages = set()
        for event in sorted_events:
            page_url = event.get("event_properties", {}).get("[Amplitude] Page URL")
            if page_url:
                pages.add(page_url)
        
        return {
            "start_time": start_time_str,
            "end_time": end_time_str,
            "duration": str(duration),
            "duration_seconds": duration.total_seconds(),
            "total_events": len(sorted_events),
            "event_types": dict(event_types),
            "unique_pages": len(pages)
        }
    except (ValueError, TypeError):
        return {}

def generate_markdown_report(sessions):
    """Générer un rapport Markdown des sessions"""
    report = []
    
    # Add report header
    report.append("# Rapport des Sessions Amplitude")
    report.append(f"Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append(f"Nombre total de sessions: {len(sessions)}")
    report.append("")
    
    # Sort sessions by duration (longest first)
    sorted_sessions = []
    for session_id, events in sessions.items():
        metrics = calculate_session_metrics(events)
        device_id = events[0].get("device_id") if events else None
        device_type = events[0].get("device_type") if events else None
        os_name = events[0].get("os_name") if events else None
        platform = events[0].get("platform") if events else None
        
        sorted_sessions.append({
            "session_id": session_id,
            "events": events,
            "metrics": metrics,
            "device_id": device_id,
            "device_type": device_type,
            "os_name": os_name,
            "platform": platform
        })
    
    # Sort by duration (longest first)
    sorted_sessions.sort(key=lambda s: s["metrics"].get("duration_seconds", 0), reverse=True)
    
    # Generate report for each session
    for session_data in sorted_sessions:
        session_id = session_data["session_id"]
        events = session_data["events"]
        metrics = session_data["metrics"]
        
        report.append(f"## Session: {session_id}")
        report.append("")
        
        # Device information
        report.append("### Informations de l'appareil")
        report.append("```")
        report.append(f"Platform: {session_data['platform']}")
        report.append(f"OS: {session_data['os_name']}")
        report.append(f"Device Type: {session_data['device_type']}")
        report.append(f"Device ID: {session_data['device_id']}")
        report.append("```")
        report.append("")
        
        # Session metrics
        report.append("### Métriques de la session")
        report.append("```")
        report.append(f"Début: {metrics.get('start_time', 'N/A')}")
        report.append(f"Fin: {metrics.get('end_time', 'N/A')}")
        report.append(f"Durée: {metrics.get('duration', 'N/A')}")
        report.append(f"Nombre total d'événements: {metrics.get('total_events', 'N/A')}")
        report.append(f"Pages uniques visitées: {metrics.get('unique_pages', 'N/A')}")
        report.append("```")
        report.append("")
        
        # Event type distribution
        report.append("### Distribution des types d'événements")
        report.append("```")
        if "event_types" in metrics:
            for event_type, count in sorted(metrics["event_types"].items(), key=lambda x: x[1], reverse=True):
                report.append(f"{event_type}: {count}")
        else:
            report.append("Aucune information disponible")
        report.append("```")
        report.append("")
        
        # Page views
        page_views = get_page_view_sequence(events)
        report.append("### Séquence de pages visitées")
        if page_views:
            report.append("| Heure | Page | Titre |")
            report.append("| ----- | ---- | ----- |")
            for page in page_views:
                report.append(f"| {page.get('time', 'N/A')} | {page.get('url', 'N/A')} | {page.get('title', 'N/A')} |")
        else:
            report.append("Aucune page visitée")
        report.append("")
        
        # Clicked elements
        clicks = get_clicked_elements(events)
        report.append("### Éléments cliqués")
        if clicks:
            report.append("| Heure | Élément | Texte | Page |")
            report.append("| ----- | ------- | ----- | ---- |")
            for click in clicks:
                element = click.get("element_tag", "")
                if click.get("element_id"):
                    element += f" #{click.get('element_id')}"
                report.append(f"| {click.get('time', 'N/A')} | {element} | {click.get('element_text', 'N/A')} | {click.get('page_url', 'N/A')} |")
        else:
            report.append("Aucun élément cliqué")
        report.append("")
        
        # Separator between sessions
        report.append("---")
        report.append("")
    
    return "\n".join(report)

def main():
    args = parse_args()
    
    # Load events from JSON file
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            events = json.load(f)
        logger.info(f"Chargé {len(events)} événements depuis {args.input_file}")
    except Exception as e:
        logger.error(f"Erreur lors du chargement des événements: {e}")
        sys.exit(1)
    
    # Extract sessions
    sessions = extract_sessions(events)
    logger.info(f"Trouvé {len(sessions)} sessions")
    
    # Generate report
    report = generate_markdown_report(sessions)
    
    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"output/session_report_{timestamp}.md"
    
    # Save report to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Rapport généré et enregistré dans {output_file}")
        print(f"Rapport généré et enregistré dans {output_file}")
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du rapport: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 