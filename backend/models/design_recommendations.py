"""
This module implements the design recommendation chains for generating
UI/UX improvement suggestions based on user feedback analysis.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSequence
from .recommendation_validator import RecommendationValidator

# Use the new UX design recommendations template from prompts.py
from .prompts import ux_design_recommendations_template as design_recommendations_template

class PostHogClient:
    """
    Client for interacting with the PostHog API to retrieve session recordings,
    events, and other user behavior data.
    """
    
    def __init__(self):
        """
        Initialize the PostHog client with API credentials from environment variables.
        """
        from models.analytics_providers import get_configured_provider
        
        # Utiliser le provider configuré
        self.provider = get_configured_provider()
    
    def get_sessions_for_page(self, page_id, date_from=None, date_to=None, days=30):
        """
        Retrieve session recordings for a specific page.
        
        Args:
            page_id (str): The page identifier (e.g., '/home', '/checkout')
            date_from (str, optional): Start date in ISO format
            date_to (str, optional): End date in ISO format
            days (int): Number of days to look back if dates not provided
            
        Returns:
            List of session recordings related to the specified page
        """
        # Calculate date range if not provided
        if not date_from or not date_to:
            date_to = datetime.now() - timedelta(days=1)  # Yesterday to avoid timezone issues
            date_from = date_to - timedelta(days=days)
            
            # Format dates for API
            date_to = date_to.isoformat()
            date_from = date_from.isoformat()
        
        # Ensure we're using proper ISO format
        if isinstance(date_from, str) and not date_from.endswith('Z'):
            # Add timezone info if missing
            try:
                dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                date_from = dt.isoformat()
            except ValueError:
                print(f"Warning: Invalid date_from format: {date_from}")
        
        if isinstance(date_to, str) and not date_to.endswith('Z'):
            # Add timezone info if missing
            try:
                dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                date_to = dt.isoformat()
            except ValueError:
                print(f"Warning: Invalid date_to format: {date_to}")
        
        print(f"Fetching sessions for page {page_id} from {date_from} to {date_to}")
        
        # Récupérer les sessions via le provider
        return self.provider.get_sessions(
            page_id=page_id,
            date_from=date_from,
            date_to=date_to
        )
    
    def get_feedback_for_page(self, page_id, date_from=None, date_to=None, days=30):
        """
        Retrieve user feedback for a specific page.
        
        Args:
            page_id (str): The page identifier (e.g., '/home', '/checkout')
            date_from (str, optional): Start date in ISO format
            date_to (str, optional): End date in ISO format
            days (int): Number of days to look back if dates not provided
            
        Returns:
            List of feedback events related to the specified page
        """
        # Calculate date range if not provided
        if not date_from or not date_to:
            date_to = datetime.now() - timedelta(days=1)  # Yesterday to avoid timezone issues
            date_from = date_to - timedelta(days=days)
            
            # Format dates for API
            date_to = date_to.isoformat()
            date_from = date_from.isoformat()
        
        # Ensure we're using proper ISO format
        if isinstance(date_from, str) and not date_from.endswith('Z'):
            # Add timezone info if missing
            try:
                dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                date_from = dt.isoformat()
            except ValueError:
                print(f"Warning: Invalid date_from format: {date_from}")
        
        if isinstance(date_to, str) and not date_to.endswith('Z'):
            # Add timezone info if missing
            try:
                dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                date_to = dt.isoformat()
            except ValueError:
                print(f"Warning: Invalid date_to format: {date_to}")
        
        print(f"Fetching feedback for page {page_id} from {date_from} to {date_to}")
        
        # Récupérer les feedbacks via le provider
        return self.provider.get_user_feedback(
            page_id=page_id,
            date_from=date_from,
            date_to=date_to
        )
    
    def get_session_details(self, session_id):
        """
        Retrieve detailed information for a specific session.
        
        Args:
            session_id (str): The session identifier
            
        Returns:
            Dictionary with session details
        """
        return self.provider.get_session_recordings(session_id)
    
    def generate_click_heatmap(self, sessions):
        """
        Generate a heatmap of click events from session recordings.
        
        Args:
            sessions (list): List of session recordings
            
        Returns:
            dict: Heatmap data structure with click information
        """
        heatmap = {}
        
        for session in sessions:
            # Extract click events from the session
            events = session.get("events", [])
            for event in events:
                if event.get("type") == "$click" and "properties" in event:
                    props = event["properties"]
                    if "element" in props and "positionX" in props and "positionY" in props:
                        element = props["element"]
                        x = props["positionX"]
                        y = props["positionY"]
                        
                        if element not in heatmap:
                            heatmap[element] = []
                        
                        heatmap[element].append({"x": x, "y": y})
        
        return heatmap
    
    def identify_confusion_areas(self, sessions):
        """
        Identify areas of the UI where users show signs of confusion.
        
        Args:
            sessions (list): List of session recordings
            
        Returns:
            list: Areas of confusion with scores
        """
        confusion_areas = []
        
        for session in sessions:
            events = session.get("events", [])
            
            # Look for patterns indicating confusion
            # 1. Repeated clicks in the same area
            click_counts = {}
            
            for i, event in enumerate(events):
                if event.get("type") == "$click" and "properties" in event:
                    props = event["properties"]
                    if "element" in props:
                        element = props["element"]
                        
                        if element not in click_counts:
                            click_counts[element] = 0
                        
                        click_counts[element] += 1
            
            # Elements with many clicks may indicate confusion
            for element, count in click_counts.items():
                if count >= 3:  # Threshold for confusion
                    confusion_areas.append({
                        "area": element,
                        "score": min(count / 3, 10),  # Scale score 1-10
                        "type": "repeated_clicks"
                    })
            
            # 2. Rapid back and forth between pages
            page_changes = []
            
            for event in events:
                if event.get("type") == "$pageview" and "properties" in event:
                    props = event["properties"]
                    if "pathname" in props:
                        page_changes.append(props["pathname"])
            
            # Check for repeated page changes
            if len(page_changes) >= 3:
                for i in range(len(page_changes) - 2):
                    if page_changes[i] == page_changes[i+2] and page_changes[i] != page_changes[i+1]:
                        confusion_areas.append({
                            "area": page_changes[i],
                            "score": 8,  # High score for navigation confusion
                            "type": "navigation_loop"
                        })
        
        # Group by area
        grouped = {}
        for area_data in confusion_areas:
            area = area_data["area"]
            if area not in grouped:
                grouped[area] = []
            grouped[area].append(area_data)
        
        # Merge and calculate average scores
        result = []
        for area, data_list in grouped.items():
            avg_score = sum(item["score"] for item in data_list) / len(data_list)
            result.append({
                "area": area,
                "score": avg_score,
                "type": data_list[0]["type"] if len(data_list) == 1 else "multiple"
            })
        
        # Sort by score (descending)
        result.sort(key=lambda x: x["score"], reverse=True)
        
        return result

# Import the component list from the validator
from .recommendation_validator import SUPPORTED_COMPONENTS

class DesignRecommendationChain:
    """
    A class that manages the generation of design recommendations based on feedback analysis.
    """
    
    def __init__(self, model="gpt-4o", temperature=0, validator=None):
        """
        Initialize the design recommendation chain with the specified LLM.
        
        Args:
            model (str): The OpenAI model to use for the chain
            temperature (float): The temperature setting for the LLM (0-1)
            validator (RecommendationValidator, optional): Custom validator to use
        """
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.validator = validator or RecommendationValidator(model=model)
        self._initialize_chain()
        
    def _initialize_chain(self):
        """Initialize the design recommendation chain."""
        parser = JsonOutputParser()
        self.recommendation_chain = RunnableSequence(
            first=design_recommendations_template,
            last=self.llm
        )
    
    def generate_recommendations(
        self, 
        analysis_summary: Dict[str, Any],
        page_id: str,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Generate design recommendations based on feedback analysis.
        
        Args:
            analysis_summary (Dict): The summary of feedback analysis
            page_id (str): The ID of the page being analyzed
            validate (bool): Whether to validate recommendations after generation
            
        Returns:
            Dict: Design recommendations in structured format
        """
        # Check if in test mode
        if os.getenv("TESTING", "false").lower() == "true":
            mock_recommendations = self._generate_mock_recommendations(page_id)
            return mock_recommendations if not validate else self.validate_recommendations(mock_recommendations)
            
        # Convert the analysis summary to a string format suitable for the prompt
        summary_str = json.dumps(analysis_summary, indent=2)
        
        # Format component list as string
        component_list = "\n".join([f"- {component}" for component in SUPPORTED_COMPONENTS])
        
        # Generate recommendations
        result = self.recommendation_chain.invoke({
            "analysis_summary": summary_str,
            "page_id": page_id,
            "component_list": component_list
        })
        
        try:
            # Extract content from AIMessage if needed
            if hasattr(result, 'content'):
                result_content = result.content
            else:
                result_content = str(result)
                
            # Clean up the result to ensure valid JSON
            # Remove markdown code blocks if present
            result_content = result_content.replace("```json", "").replace("```", "").strip()
            
            # Attempt to parse the JSON
            try:
                parsed_json = json.loads(result_content)
                
                # Validate recommendations if requested
                if validate:
                    return self.validate_recommendations(parsed_json)
                return parsed_json
                
            except json.JSONDecodeError:
                # Try to extract JSON using regex as a fallback
                import re
                json_match = re.search(r'(\{[\s\S]*\})', result_content, re.DOTALL)
                if json_match:
                    try:
                        parsed_json = json.loads(json_match.group(1))
                        # Validate recommendations if requested
                        if validate:
                            return self.validate_recommendations(parsed_json)
                        return parsed_json
                    except:
                        pass
                
                # If we still couldn't parse it, raise an exception
                raise ValueError("Failed to parse LLM output as valid JSON")
        except Exception as e:
            # Rather than returning a simplified result, raise an exception
            # to force the use of real recommendations only
            raise ValueError(f"Failed to generate valid recommendations: {str(e)}")
    
    def validate_recommendations(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate generated recommendations for feasibility.
        
        Args:
            recommendations (Dict): The recommendations to validate
            
        Returns:
            Dict: Validated recommendations with feasibility information
        """
        return self.validator.validate_all_recommendations(recommendations)
            
    def _generate_mock_recommendations(self, page_id: str) -> Dict[str, Any]:
        """Generate mock recommendations for testing purposes."""
        return {
            "page_id": page_id,
            "recommendations": [
                {
                    "title": "Simplify form fields",
                    "description": "Reduce the number of form fields to only essential information, specifically remove the 'How did you hear about us' and 'Additional comments' fields",
                    "component": "Form",
                    "location": "Main checkout area",
                    "expected_impact": "Reduce checkout abandonment rate by 15-20% and increase form completion speed by 30%",
                    "priority": "high",
                    "justification": "Analysis shows 40% of users abandon checkout after seeing the full form, with heatmaps showing hesitation at non-essential fields",
                    "before_after": {
                        "before": "10 form fields with complex validation including optional fields that cause confusion",
                        "after": "5 essential form fields with clear validation messages and visual progress indication"
                    }
                },
                {
                    "title": "Make submit button more prominent",
                    "description": "Increase the size of the submit button by 30%, change color to primary brand color (#3A86FF), and add a subtle hover animation",
                    "component": "Button",
                    "location": "Bottom of form, centered with 24px margins",
                    "expected_impact": "Increase form completion rate by 25% and reduce time to completion",
                    "priority": "medium",
                    "justification": "Session recordings show 35% of users hesitate or scan the page looking for the submit button",
                    "before_after": {
                        "before": "Small (120px × 36px), low-contrast gray button that blends with background",
                        "after": "Larger (160px × 48px), high-contrast blue button with 'Complete Purchase' text and arrow icon"
                    }
                },
                {
                    "title": "Add progress indicator for multi-step form",
                    "description": "Add a horizontal progress bar showing all checkout steps (Cart, Shipping, Payment, Confirmation) with current step highlighted",
                    "component": "Navigation",
                    "location": "Top of checkout page, below header",
                    "expected_impact": "Reduce checkout abandonment by 20% by setting clear expectations on process length",
                    "priority": "high",
                    "justification": "Feedback analysis shows users complaining about uncertainty in checkout process length",
                    "before_after": {
                        "before": "No indication of checkout process length or current position",
                        "after": "Clear 4-step indicator showing current position and remaining steps with estimated time"
                    }
                }
            ],
            "implementation_notes": "These changes should be implemented in the next sprint for maximum impact. The progress indicator should be implemented first as it requires less visual design work and can provide immediate clarity to users.",
            "general_observations": "The page design has a solid foundation but lacks clear visual hierarchy and user guidance. Users are currently confused about the overall process, particularly on mobile devices where the submit button is often below the visible area."
        }
    
    def generate_recommendations_from_file(
        self,
        analysis_file: str,
        page_id: str = None,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Generate design recommendations from an analysis results file.
        
        Args:
            analysis_file (str): Path to the JSON file with analysis results
            page_id (str, optional): The ID of the page being analyzed
                                     (overrides the one in the file if provided)
            validate (bool): Whether to validate recommendations after generation
            
        Returns:
            Dict: Design recommendations in structured format
        """
        # Load the analysis results
        try:
            with open(analysis_file, 'r') as f:
                analysis_data = json.load(f)
        except Exception as e:
            raise Exception(f"Error loading analysis file: {e}")
        
        # Extract the summary from the analysis results
        if "results" in analysis_data and "summary" in analysis_data["results"]:
            summary = analysis_data["results"]["summary"]
        else:
            raise Exception("Analysis file does not contain summary data")
        
        # Get page ID from the file if not provided
        if not page_id and "metadata" in analysis_data and "page_id" in analysis_data["metadata"]:
            page_id = analysis_data["metadata"]["page_id"]
        
        if not page_id:
            page_id = "unknown_page"
        
        # Generate recommendations
        return self.generate_recommendations(summary, page_id, validate=validate)
    
    def rank_recommendations_by_impact(
        self, 
        recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Rank recommendations by estimated impact using feasibility and priority.
        
        Args:
            recommendations (Dict): Validated recommendations from validate_recommendations()
            
        Returns:
            Dict: Recommendations sorted by estimated impact with added impact scores
        """
        # Make a copy to avoid modifying the original
        result = recommendations.copy()
        result_recommendations = []
        
        # Priority weights
        priority_weights = {
            "high": 3.0,
            "medium": 2.0,
            "low": 1.0
        }
        
        # Process each recommendation
        for rec in recommendations.get("recommendations", []):
            # Skip if validation info is missing
            if "validation" not in rec:
                result_recommendations.append(rec)
                continue
                
            # Calculate impact score based on feasibility and priority
            priority = rec.get("priority", "medium")
            priority_weight = priority_weights.get(priority, 2.0)
            
            feasibility_score = rec["validation"].get("feasibility_score", 50) / 100.0
            
            # Impact formula: priority weight × feasibility score
            impact_score = priority_weight * feasibility_score * 10  # Scale to 0-30
            
            # Add impact score to recommendation
            rec_copy = rec.copy()
            rec_copy["impact_score"] = round(impact_score, 1)
            result_recommendations.append(rec_copy)
        
        # Sort by impact score (descending)
        result_recommendations.sort(key=lambda r: r.get("impact_score", 0), reverse=True)
        
        # Update recommendations list
        result["recommendations"] = result_recommendations
        
        return result

def analyze_feedbacks(page_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """
    Analyse les feedbacks pour une page spécifique dans une plage de dates donnée.
    
    Args:
        page_id: Identifiant de la page (ex: /checkout, /home)
        start_date: Date de début pour le filtrage
        end_date: Date de fin pour le filtrage
        
    Returns:
        Résultats d'analyse structurés
    """
    # Cette fonction serait normalement implémentée pour analyser les feedbacks
    # et générer un résumé d'analyse
    pass

def fetch_session_recordings(user_id=None, date_from=None, date_to=None):
    """
    Récupère les enregistrements de session depuis PostHog.
    
    Args:
        user_id: ID utilisateur spécifique (optionnel)
        date_from: Date de début (optionnel)
        date_to: Date de fin (optionnel)
        
    Returns:
        Liste des enregistrements de session avec leurs métadonnées
    """
    api_url = f"{os.getenv('POSTHOG_API_URL')}/projects/{os.getenv('POSTHOG_PROJECT_ID')}/session_recordings"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('POSTHOG_API_KEY')}"
    }
    
    params = {}
    if user_id:
        params["person_id"] = user_id
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to
    
    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching session recordings: {str(e)}")
        return {"results": []}

def download_session_data(session_id):
    """
    Télécharge les données complètes d'une session spécifique.
    
    Args:
        session_id: ID de la session à télécharger
        
    Returns:
        Les données détaillées de la session
    """
    api_url = f"{os.getenv('POSTHOG_API_URL')}/projects/{os.getenv('POSTHOG_PROJECT_ID')}/session_recordings/{session_id}"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('POSTHOG_API_KEY')}"
    }
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error downloading session data: {str(e)}")
        return {}

class DesignSuggestionGenerator:
    """
    Générateur de suggestions de design basé sur l'analyse des comportements utilisateurs.
    """
    
    def __init__(self):
        """Initialiser le générateur de suggestions."""
        self.posthog_client = PostHogClient()
    
    def generate_layout_suggestions(self, page_id, date_range=30):
        """
        Génère des suggestions de design basées sur les données utilisateur.
        
        Args:
            page_id: ID de la page/écran à analyser
            date_range: Nombre de jours à analyser
            
        Returns:
            Dict avec des suggestions de design structurées
        """
        # Récupérer les données
        sessions = self.posthog_client.get_sessions_for_page(page_id, days=date_range)
        feedback = self.posthog_client.get_feedback_for_page(page_id, days=date_range)
        
        # Analyser les comportements
        click_heatmap = self.posthog_client.generate_click_heatmap(sessions)
        confusion_areas = self.posthog_client.identify_confusion_areas(sessions)
        
        # Générer des suggestions
        return {
            "layout_improvements": self._suggest_layout_improvements(click_heatmap, confusion_areas),
            "ui_element_changes": self._suggest_ui_element_changes(feedback, sessions),
            "flow_improvements": self._suggest_flow_improvements(sessions)
        }
    
    def _suggest_layout_improvements(self, heatmap, confusion_areas):
        """
        Suggère des améliorations de mise en page basées sur la carte de chaleur et les zones de confusion.
        
        Args:
            heatmap: Données de la carte de chaleur des clics
            confusion_areas: Zones de confusion identifiées
            
        Returns:
            Liste de suggestions d'amélioration de mise en page
        """
        # Cette méthode utiliserait les données de la carte de chaleur et des zones de confusion
        # pour générer des suggestions d'amélioration de mise en page
        
        # Implémentation simplifiée pour le test
        suggestions = []
        
        # Analyser les zones de confusion
        for area in confusion_areas:
            if area["score"] > 0.7:
                suggestions.append({
                    "element": area["area"],
                    "suggestion": "Simplifier cette zone de l'interface",
                    "priority": "high",
                    "reason": f"Zone de confusion élevée (score: {area['score']})"
                })
            elif area["score"] > 0.4:
                suggestions.append({
                    "element": area["area"],
                    "suggestion": "Améliorer la clarté visuelle",
                    "priority": "medium",
                    "reason": f"Zone de confusion modérée (score: {area['score']})"
                })
        
        # Analyser la carte de chaleur pour les zones de faible interaction
        # (implémentation simplifiée)
        if len(heatmap.get("heatmap_data", [])) > 0:
            suggestions.append({
                "element": "call_to_action",
                "suggestion": "Rendre les boutons d'action plus visibles",
                "priority": "medium",
                "reason": "Faible taux de clic sur les éléments d'action"
            })
        
        return suggestions
    
    def _suggest_ui_element_changes(self, feedback, sessions):
        """
        Suggère des changements d'éléments d'interface basés sur les feedbacks et les sessions.
        
        Args:
            feedback: Données de feedback utilisateur
            sessions: Données de session utilisateur
            
        Returns:
            Liste de suggestions de modification d'éléments d'interface
        """
        # Cette méthode utiliserait les feedbacks et les données de session
        # pour suggérer des modifications d'éléments d'interface spécifiques
        
        # Implémentation simplifiée pour le test
        suggestions = []
        
        # Analyser les feedbacks
        sentiment_counters = {"positive": 0, "negative": 0, "neutral": 0}
        for item in feedback:
            sentiment = item.get("sentiment", "neutral")
            sentiment_counters[sentiment] += 1
            
            # Si feedback négatif, suggérer une amélioration
            if sentiment == "negative" and "text" in item:
                suggestions.append({
                    "element": "general",
                    "suggestion": "Améliorer l'interface selon le feedback utilisateur",
                    "priority": "medium",
                    "reason": f"Feedback négatif: {item['text']}"
                })
        
        # Suggérer des améliorations basées sur la proportion de sentiments
        total = sum(sentiment_counters.values())
        if total > 0 and sentiment_counters["negative"] / total > 0.3:
            suggestions.append({
                "element": "overall_design",
                "suggestion": "Revoir la conception globale de l'interface",
                "priority": "high",
                "reason": f"{round(sentiment_counters['negative'] / total * 100)}% des feedbacks sont négatifs"
            })
        
        return suggestions
    
    def _suggest_flow_improvements(self, sessions):
        """
        Suggère des améliorations de flux de navigation basées sur les données de session.
        
        Args:
            sessions: Données de session utilisateur
            
        Returns:
            Liste de suggestions d'amélioration de flux
        """
        # Cette méthode analyserait les parcours utilisateurs pour identifier
        # des opportunités d'amélioration du flux de navigation
        
        # Implémentation simplifiée pour le test
        suggestions = []
        
        # Identifier les abandons fréquents
        # (implémentation simulée)
        if len(sessions) > 0:
            suggestions.append({
                "element": "navigation",
                "suggestion": "Simplifier le processus de navigation",
                "priority": "medium",
                "reason": "Taux d'abandon élevé observé dans les sessions"
            })
        
        return suggestions

# Test function
if __name__ == "__main__":
    # Sample analysis summary for testing
    sample_summary = {
        "summary": "Users find the checkout process confusing and lengthy. The form has too many fields and the submit button is difficult to locate. Mobile users report additional issues with menu functionality and image loading.",
        "key_issues": [
            "Lengthy checkout process",
            "Too many form fields",
            "Hard to find submit button",
            "Mobile menu not working",
            "Images not loading on mobile"
        ],
        "positive_aspects": [
            "Professional website appearance",
            "Good color scheme",
            "Easy desktop navigation"
        ],
        "overall_sentiment": "Mixed, with significant frustration around checkout and mobile experience",
        "priority_recommendations": [
            "Simplify checkout form",
            "Make submit button more prominent",
            "Fix mobile menu functionality",
            "Optimize image loading for mobile"
        ]
    }
    
    # Create recommendation chain
    recommendation_chain = DesignRecommendationChain(model="gpt-3.5-turbo")
    
    # Generate recommendations
    recommendations = recommendation_chain.generate_recommendations(
        sample_summary,
        "checkout_page"
    )
    
    print("Design Recommendations:")
    print(json.dumps(recommendations, indent=2)) 