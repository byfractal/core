"""
This module implements the design recommendation chains for generating
UI/UX improvement suggestions based on user feedback analysis.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
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

# Define the prompt template for design recommendations
design_recommendations_template = PromptTemplate(
    input_variables=["analysis_summary", "page_id"],
    template="""
You are an expert UI/UX designer with deep knowledge of user behavior analytics.
Based on the following user feedback analysis for page '{page_id}', generate concrete design improvement recommendations.

ANALYSIS SUMMARY:
{analysis_summary}

Generate design recommendations that:
1. Address the key issues identified in the analysis
2. Maintain or enhance the positive aspects mentioned
3. Consider current UI/UX best practices
4. Can be implemented using existing UI components (no new component types)
5. Provide clear justification based on user feedback data

For each recommendation, provide:
- A clear description of what should be changed
- The specific location or component to modify
- The expected user impact
- The priority level (high/medium/low)
- Data-driven justification

You MUST return a valid JSON object with this exact structure:
{{
    "page_id": "{page_id}",
    "recommendations": [
        {{
            "title": "First recommendation title",
            "description": "Detailed description of what should be changed",
            "component": "Specific UI component to modify",
            "location": "Where on the page",
            "expected_impact": "How this will improve user experience",
            "priority": "high|medium|low",
            "justification": "Data-driven justification from the analysis",
            "before_after": {{
                "before": "Brief description of current state",
                "after": "Brief description of recommended state"
            }}
        }},
        {{
            "title": "Second recommendation title",
            "description": "Detailed description of what should be changed",
            "component": "Specific UI component to modify",
            "location": "Where on the page",
            "expected_impact": "How this will improve user experience",
            "priority": "high|medium|low",
            "justification": "Data-driven justification from the analysis",
            "before_after": {{
                "before": "Brief description of current state",
                "after": "Brief description of recommended state"
            }}
        }}
    ],
    "implementation_notes": "Any overall notes for implementation",
    "general_observations": "Overall observations about the page design"
}}

IMPORTANT: 
1. Do NOT include comments in the JSON
2. Do NOT use placeholders like <title> - replace them with actual content 
3. Use double quotes for all JSON keys and string values
4. Make sure all JSON keys match exactly the structure shown above
5. Your entire response must be valid JSON - nothing else
"""
)

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
        
        Signs of confusion can include:
        - Excessive mouse movement
        - Multiple failed clicks
        - Rapid back-and-forth scrolling
        - Multiple form field edits without submission
        
        Args:
            sessions (list): List of session recordings
            
        Returns:
            list: Areas of confusion with confidence scores
        """
        confusion_areas = []
        
        for session in sessions:
            session_id = session.get("id")
            if not session_id:
                continue
                
            # Extract events that might indicate confusion
            events = session.get("events", [])
            
            # Analyze for confusion patterns
            # (This is simplified - a real implementation would be more sophisticated)
            
            # Look for multiple clicks in the same area
            click_clusters = self._find_click_clusters(events)
            for area, score in click_clusters.items():
                confusion_areas.append({
                    "area": area,
                    "score": min(score / 5, 1.0),  # Normalize score to 0-1
                    "type": "multiple_clicks"
                })
            
            # Look for rapid scrolling
            scroll_patterns = self._analyze_scroll_patterns(events)
            for area, score in scroll_patterns.items():
                confusion_areas.append({
                    "area": area,
                    "score": min(score / 3, 1.0),  # Normalize score to 0-1
                    "type": "rapid_scrolling"
                })
        
        # Aggregate and merge similar areas
        return self._aggregate_confusion_areas(confusion_areas)
    
    def _find_click_clusters(self, events):
        """Find clusters of clicks that might indicate confusion"""
        # Simplified implementation
        clusters = {}
        
        for event in events:
            if event.get("type") == "$click" and "properties" in event:
                props = event["properties"]
                if "element" in props:
                    element = props["element"]
                    clusters[element] = clusters.get(element, 0) + 1
        
        # Filter out elements with just a few clicks
        return {k: v for k, v in clusters.items() if v >= 3}
    
    def _analyze_scroll_patterns(self, events):
        """Analyze scroll patterns for signs of confusion"""
        # Simplified implementation
        scroll_areas = {}
        
        for i in range(len(events) - 1):
            current = events[i]
            next_event = events[i + 1]
            
            if (current.get("type") == "$scroll" and next_event.get("type") == "$scroll" and
                "properties" in current and "properties" in next_event):
                # Look for scroll direction changes
                current_dir = self._get_scroll_direction(current["properties"])
                next_dir = self._get_scroll_direction(next_event["properties"])
                
                if current_dir and next_dir and current_dir != next_dir:
                    # Direction changed, might indicate confusion
                    page = current["properties"].get("path", "unknown")
                    scroll_areas[page] = scroll_areas.get(page, 0) + 1
        
        return scroll_areas
    
    def _get_scroll_direction(self, props):
        """Get the direction of a scroll event"""
        if "scrollY" not in props:
            return None
            
        scrollY = props["scrollY"]
        
        if scrollY > 0:
            return "down"
        elif scrollY < 0:
            return "up"
        return None
    
    def _aggregate_confusion_areas(self, areas):
        """Aggregate and merge similar confusion areas"""
        # Group by area
        grouped = {}
        for area_data in areas:
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

class DesignRecommendationChain:
    """
    A class that manages the generation of design recommendations based on feedback analysis.
    """
    
    def __init__(self, model="gpt-4o", temperature=0):
        """
        Initialize the design recommendation chain with the specified LLM.
        
        Args:
            model (str): The OpenAI model to use for the chain
            temperature (float): The temperature setting for the LLM (0-1)
        """
        self.llm = ChatOpenAI(model=model, temperature=temperature)
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
        page_id: str
    ) -> Dict[str, Any]:
        """
        Generate design recommendations based on feedback analysis.
        
        Args:
            analysis_summary (Dict): The summary of feedback analysis
            page_id (str): The ID of the page being analyzed
            
        Returns:
            Dict: Design recommendations in structured format
        """
        # Check if in test mode
        if os.getenv("TESTING", "false").lower() == "true":
            return self._generate_mock_recommendations(page_id)
            
        # Convert the analysis summary to a string format suitable for the prompt
        summary_str = json.dumps(analysis_summary, indent=2)
        
        # Generate recommendations
        result = self.recommendation_chain.invoke({
            "analysis_summary": summary_str,
            "page_id": page_id
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
                return parsed_json
            except json.JSONDecodeError:
                # Try to extract JSON using regex as a fallback
                import re
                json_match = re.search(r'(\{[\s\S]*\})', result_content, re.DOTALL)
                if json_match:
                    try:
                        parsed_json = json.loads(json_match.group(1))
                        return parsed_json
                    except:
                        pass
                
                # If we still couldn't parse it, raise an exception
                raise ValueError("Failed to parse LLM output as valid JSON")
        except Exception as e:
            # Rather than returning a simplified result, raise an exception
            # to force the use of real recommendations only
            raise ValueError(f"Failed to generate valid recommendations: {str(e)}")
            
    def _generate_mock_recommendations(self, page_id: str) -> Dict[str, Any]:
        """Generate mock recommendations for testing purposes."""
        return {
            "page_id": page_id,
            "recommendations": [
                {
                    "title": "Simplify form fields",
                    "description": "Reduce the number of form fields to only essential information",
                    "component": "Form",
                    "location": "Main checkout area",
                    "expected_impact": "Reduced user frustration and higher completion rate",
                    "priority": "high",
                    "justification": "Users complained about too many form fields causing confusion",
                    "before_after": {
                        "before": "10 form fields with complex validation",
                        "after": "5 essential form fields with clear validation messages"
                    }
                },
                {
                    "title": "Make submit button more prominent",
                    "description": "Increase size and contrast of the submit button",
                    "component": "Button",
                    "location": "Bottom of form",
                    "expected_impact": "Easier completion of checkout process",
                    "priority": "medium",
                    "justification": "Users reported difficulty finding the submit button",
                    "before_after": {
                        "before": "Small, low-contrast button",
                        "after": "Large, high-contrast button with clear call to action"
                    }
                }
            ],
            "implementation_notes": "These changes should be implemented in the next sprint for maximum impact",
            "general_observations": "The page design is generally sound but needs refinement in key areas"
        }
    
    def generate_recommendations_from_file(
        self,
        analysis_file: str,
        page_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate design recommendations from an analysis results file.
        
        Args:
            analysis_file (str): Path to the JSON file with analysis results
            page_id (str, optional): The ID of the page being analyzed
                                     (overrides the one in the file if provided)
            
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
        return self.generate_recommendations(summary, page_id)

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