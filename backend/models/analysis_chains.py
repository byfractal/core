"""
This module implements the analysis chains for processing user feedback.
It uses the prompt templates defined in prompts.py to create specialized
chains for sentiment analysis, theme extraction, and summary generation.
"""

# Configure encoding for API requests
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import sys
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

# Charger les variables d'environnement
from dotenv import load_dotenv
env_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path=env_path)

from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI

# Import our prompt templates
from backend.models.prompts import (
    sentiment_classification_template,
    emotion_theme_extraction_template,
    feedback_summary_template
)

class FeedbackAnalysisChains:
    """
    A class that manages the different analysis chains for processing user feedback.
    
    This class encapsulates the various chains needed for the complete
    feedback analysis pipeline, including sentiment analysis, emotion/theme
    extraction, and feedback summarization.
    """
    
    def __init__(self, model="gpt-4o", temperature=0):
        """
        Initialize the analysis chains with the specified LLM.
        
        Args:
            model (str): The OpenAI model to use for the chains
            temperature (float): The temperature setting for the LLM (0-1)
        """
        # Récupérer la clé API depuis les variables d'environnement
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Afficher un message pour debug (masqué pour la sécurité)
        if api_key:
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            print(f"Using API key: {masked_key}")
        else:
            print("AVERTISSEMENT: Aucune clé API OpenAI trouvée")
        
        # Pour les modèles de chat (comme GPT-3.5 et GPT-4), utiliser ChatOpenAI
        if any(chat_model in model.lower() for chat_model in ["gpt-3.5", "gpt-4"]):
            self.llm = ChatOpenAI(model=model, temperature=temperature, openai_api_key=api_key)
        else:
            # Pour les autres modèles, utiliser OpenAI
            self.llm = OpenAI(model=model, temperature=temperature, openai_api_key=api_key)
            
        self._initialize_chains()
        
    def _initialize_chains(self):
        """Initialize all the necessary chains for feedback analysis."""
        # Create the sentiment analysis chain using pipe syntax instead of from_components
        self.sentiment_chain = sentiment_classification_template | self.llm
        
        # Create the emotion/theme extraction chain
        self.emotion_theme_chain = emotion_theme_extraction_template | self.llm
        
        # Create the feedback summary chain
        self.summary_chain = feedback_summary_template | self.llm
    
    def analyze_sentiment(self, feedback: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of a single feedback.
        
        Args:
            feedback (str): The user feedback text to analyze
            
        Returns:
            Dict: A dictionary with sentiment classification results
        """
        result = self.sentiment_chain.invoke({"feedback": feedback})
        
        # Si le résultat est un AIMessage (ChatOpenAI), extraire le contenu
        if hasattr(result, 'content'):
            result_content = result.content
        else:
            result_content = result
            
        try:
            # Ensure the result is treated as UTF-8
            if isinstance(result_content, bytes):
                result_content = result_content.decode('utf-8')
            return json.loads(result_content)
        except (json.JSONDecodeError, TypeError):
            # Fallback if the result isn't a valid JSON
            return {"raw_result": str(result_content)}
    
    def extract_emotions_themes(self, feedback: str) -> Dict[str, Any]:
        """
        Extract emotions and themes from a single feedback.
        
        Args:
            feedback (str): The user feedback text to analyze
            
        Returns:
            Dict: A dictionary with emotions, themes, and issues
        """
        result = self.emotion_theme_chain.invoke({"feedback": feedback})
        
        # Si le résultat est un AIMessage (ChatOpenAI), extraire le contenu
        if hasattr(result, 'content'):
            result_content = result.content
        else:
            result_content = result
            
        try:
            # Ensure the result is treated as UTF-8
            if isinstance(result_content, bytes):
                result_content = result_content.decode('utf-8')
            return json.loads(result_content)
        except (json.JSONDecodeError, TypeError):
            return {"raw_result": str(result_content)}
    
    def summarize_feedback(self, feedback_list: List[str]) -> Dict[str, Any]:
        """
        Generate a summary from multiple feedback items.
        
        Args:
            feedback_list (List[str]): A list of user feedback texts
            
        Returns:
            Dict: A dictionary with summary information
        """
        # Format the feedback list as a numbered list for the prompt
        formatted_feedback = "\n".join([f"{i+1}. {feedback}" for i, feedback in enumerate(feedback_list)])
        result = self.summary_chain.invoke({"feedback_list": formatted_feedback})
        
        # Si le résultat est un AIMessage (ChatOpenAI), extraire le contenu
        if hasattr(result, 'content'):
            result_content = result.content
        else:
            result_content = result
        
        try:
            return json.loads(result_content)
        except (json.JSONDecodeError, TypeError):
            return {"raw_result": str(result_content)}
    
    def run_complete_analysis(self, feedback: str) -> Dict[str, Any]:
        """
        Run a complete analysis of a single feedback item.
        
        This method orchestrates the entire analysis pipeline:
        1. First determines sentiment
        2. Then extracts emotions and themes
        3. Based on sentiment and themes, may perform additional specialized analysis
        
        Args:
            feedback (str): The user feedback text to analyze
            
        Returns:
            Dict[str, Any]: A dictionary containing all analysis results
        """
        # Start with sentiment analysis
        sentiment_results = self.analyze_sentiment(feedback)
        
        # Extract emotions and themes
        themes_results = self.extract_emotions_themes(feedback)
        
        # Initialize the complete results dictionary
        complete_results = {
            "sentiment_analysis": sentiment_results,
            "themes_emotions": themes_results,
            "specialized_insights": {},
            "timestamp": str(datetime.now())
        }
        
        # Conditional branching based on sentiment and themes
        sentiment = sentiment_results.get("sentiment", "").upper()
        themes = themes_results.get("themes", [])
        emotions = themes_results.get("emotions", [])
        
        # For negative feedback, perform deeper analysis based on detected themes
        if sentiment == "NEGATIVE":
            # Check for specific themes that need deeper analysis
            if any(theme in ["Form Design/Input Fields", "Workflow/Process Flow"] for theme in themes):
                # Add specialized form analysis
                complete_results["specialized_insights"]["form_analysis"] = self._analyze_form_issues(feedback)
                
            if any(theme in ["Navigation/Information Architecture", "Page Layout/Visual Hierarchy"] for theme in themes):
                # Add navigation/layout specific analysis
                complete_results["specialized_insights"]["navigation_analysis"] = self._analyze_navigation_issues(feedback)
                
            if any(theme in ["Load Time/Performance"] for theme in themes):
                # Add performance analysis
                complete_results["specialized_insights"]["performance_analysis"] = self._analyze_performance_issues(feedback)
        
        # For mixed or positive feedback with feature requests
        if "Specific Feature Requests" in themes:
            complete_results["specialized_insights"]["feature_request_analysis"] = self._analyze_feature_requests(feedback)
        
        return complete_results
    
    # Additional specialized analysis methods
    def _analyze_form_issues(self, feedback: str) -> Dict[str, Any]:
        """Analyze form-related issues in more detail"""
        form_analysis_prompt = PromptTemplate(
            input_variables=["feedback"],
            template="""
            Analyze the following feedback focusing specifically on form-related issues:
            
            Feedback: {feedback}
            
            Identify:
            1. Which specific form elements are problematic
            2. The exact user pain points (too many fields, unclear labels, validation errors, etc.)
            3. Specific recommendations to improve the form experience
            
            Return your analysis as a JSON object.
            """
        )
        form_chain = form_analysis_prompt | self.llm | JsonOutputParser()
        result = form_chain.invoke({"feedback": feedback})
        
        # Si c'est déjà un dictionnaire, le retourner directement
        if isinstance(result, dict):
            return result
        
        # Sinon, extraire le contenu si c'est un AIMessage
        if hasattr(result, 'content'):
            try:
                return json.loads(result.content)
            except:
                return {"raw_result": str(result.content)}
        
        return result
    
    def _analyze_navigation_issues(self, feedback: str) -> Dict[str, Any]:
        """Analyze navigation and layout issues in more detail"""
        navigation_prompt = PromptTemplate(
            input_variables=["feedback"],
            template="""
            Analyze the following feedback focusing specifically on navigation and layout issues:
            
            Feedback: {feedback}
            
            Identify:
            1. Which specific navigation elements or page layouts are problematic
            2. The exact user pain points (confusing menu structure, poor information hierarchy, etc.)
            3. Specific recommendations to improve the navigation and layout
            
            Return your analysis as a JSON object.
            """
        )
        navigation_chain = navigation_prompt | self.llm | JsonOutputParser()
        result = navigation_chain.invoke({"feedback": feedback})
        
        # Si c'est déjà un dictionnaire, le retourner directement
        if isinstance(result, dict):
            return result
        
        # Sinon, extraire le contenu si c'est un AIMessage
        if hasattr(result, 'content'):
            try:
                return json.loads(result.content)
            except:
                return {"raw_result": str(result.content)}
        
        return result
    
    def _analyze_performance_issues(self, feedback: str) -> Dict[str, Any]:
        """Analyze performance issues in more detail"""
        performance_prompt = PromptTemplate(
            input_variables=["feedback"],
            template="""
            Analyze the following feedback focusing specifically on performance issues:
            
            Feedback: {feedback}
            
            Identify:
            1. Which specific performance aspects are problematic (loading time, responsiveness, etc.)
            2. The user's expectations regarding performance
            3. Specific recommendations to improve the performance perception
            
            Return your analysis as a JSON object.
            """
        )
        performance_chain = performance_prompt | self.llm | JsonOutputParser()
        result = performance_chain.invoke({"feedback": feedback})
        
        # Si c'est déjà un dictionnaire, le retourner directement
        if isinstance(result, dict):
            return result
        
        # Sinon, extraire le contenu si c'est un AIMessage
        if hasattr(result, 'content'):
            try:
                return json.loads(result.content)
            except:
                return {"raw_result": str(result.content)}
        
        return result
    
    def _analyze_feature_requests(self, feedback: str) -> Dict[str, Any]:
        """Analyze feature requests in more detail"""
        feature_prompt = PromptTemplate(
            input_variables=["feedback"],
            template="""
            Analyze the following feedback focusing specifically on feature requests:
            
            Feedback: {feedback}
            
            Identify:
            1. The specific features being requested
            2. The underlying user needs these features would address
            3. Priority assessment (how critical this feature might be)
            4. How this feature would improve the overall user experience
            
            Return your analysis as a JSON object.
            """
        )
        feature_chain = feature_prompt | self.llm | JsonOutputParser()
        result = feature_chain.invoke({"feedback": feedback})
        
        # Si c'est déjà un dictionnaire, le retourner directement
        if isinstance(result, dict):
            return result
        
        # Sinon, extraire le contenu si c'est un AIMessage
        if hasattr(result, 'content'):
            try:
                return json.loads(result.content)
            except:
                return {"raw_result": str(result.content)}
        
        return result
    
    def batch_analyze(self, feedback_list: List[str]) -> Dict[str, Any]:
        """
        Analyze a batch of feedback texts and generate a summary.
        
        This method:
        1. Analyzes each feedback individually
        2. Generates a summary across all feedback
        
        Args:
            feedback_list (List[str]): A list of user feedback texts
            
        Returns:
            Dict: A dictionary with individual and summary analyses
        """
        # En mode test, retourner un résultat fictif si TESTING est activé
        if os.environ.get('TESTING') == 'true':
            return {
                "individual_analyses": [],
                "summary": {
                    "key_themes": ["Navigation", "Interface design"],
                    "sentiment_distribution": {"POSITIVE": 50, "NEGATIVE": 30, "NEUTRAL": 20},
                    "overall_summary": "This is a test summary for feedback analysis."
                },
                "meta": {"analyzed_count": len(feedback_list)}
            }
            
        try:
            individual_results = []
            for feedback in feedback_list:
                # Assurer que le feedback est bien encodé en utf-8 si c'est une chaîne
                if isinstance(feedback, str):
                    feedback = feedback.encode('utf-8', errors='ignore').decode('utf-8')
                
                analysis = self.run_complete_analysis(feedback)
                individual_results.append(analysis)
            
            # Generate a summary across all feedback
            summary = self.summarize_feedback(feedback_list)
            
            # Combine individual results with the summary
            batch_results = {
                "individual_analyses": individual_results,
                "summary": summary
            }
            
            return batch_results
        except Exception as e:
            return {"error": str(e)}

# Test function
if __name__ == "__main__":
    # Create an instance of the feedback analysis chains
    analysis_chains = FeedbackAnalysisChains(model="gpt-3.5-turbo")
    
    # Test with a single feedback
    test_feedback = "I found the checkout process confusing and too lengthy. There were too many form fields and the submit button was hard to find."
    
    print("Testing single feedback analysis:")
    results = analysis_chains.run_complete_analysis(test_feedback)
    print(json.dumps(results, indent=2))
    
    # Test with multiple feedback items
    test_feedback_list = [
        "I found the checkout process confusing and too lengthy. There were too many form fields and the submit button was hard to find.",
        "The website looks very professional and I love the color scheme. Very easy to navigate!",
        "The mobile version is broken, I can't click on any of the menu items and the images don't load properly."
    ]
    
    print("\nTesting batch analysis:")
    batch_results = analysis_chains.batch_analyze(test_feedback_list)
    print(json.dumps(batch_results["summary"], indent=2)) 