"""
This module implements the analysis chains for processing user feedback.
It uses the prompt templates defined in prompts.py to create specialized
chains for sentiment analysis, theme extraction, and summary generation.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSequence

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
        self.llm = OpenAI(model=model, temperature=temperature)
        self._initialize_chains()
        
    def _initialize_chains(self):
        """Initialize all the necessary chains for feedback analysis."""
        # Create the sentiment analysis chain
        self.sentiment_chain = RunnableSequence.from_components(
            sentiment_classification_template, 
            self.llm
        )
        
        # Create the emotion/theme extraction chain
        self.emotion_theme_chain = RunnableSequence.from_components(
            emotion_theme_extraction_template,
            self.llm
        )
        
        # Create the feedback summary chain
        self.summary_chain = RunnableSequence.from_components(
            feedback_summary_template,
            self.llm
        )
    
    def analyze_sentiment(self, feedback: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of a single feedback.
        
        Args:
            feedback (str): The user feedback text to analyze
            
        Returns:
            Dict: A dictionary with sentiment classification results
        """
        result = self.sentiment_chain.invoke({"feedback": feedback})
        try:
            return json.loads(result)
        except (json.JSONDecodeError, TypeError):
            # Fallback if the result isn't a valid JSON
            return {"raw_result": result}
    
    def extract_emotions_themes(self, feedback: str) -> Dict[str, Any]:
        """
        Extract emotions and themes from a single feedback.
        
        Args:
            feedback (str): The user feedback text to analyze
            
        Returns:
            Dict: A dictionary with emotions, themes, and issues
        """
        result = self.emotion_theme_chain.invoke({"feedback": feedback})
        try:
            return json.loads(result)
        except (json.JSONDecodeError, TypeError):
            return {"raw_result": result}
    
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
        try:
            return json.loads(result)
        except (json.JSONDecodeError, TypeError):
            return {"raw_result": result}
    
    def run_complete_analysis(self, feedback: str) -> Dict[str, Any]:
        """
        Run a complete analysis pipeline on a single feedback.
        
        This method runs both sentiment analysis and emotion/theme extraction
        and combines the results into a single output.
        
        Args:
            feedback (str): The user feedback text to analyze
            
        Returns:
            Dict: A dictionary with combined analysis results
        """
        sentiment_results = self.analyze_sentiment(feedback)
        emotion_theme_results = self.extract_emotions_themes(feedback)
        
        # Combine the results
        combined_results = {
            "feedback": feedback,
            "sentiment_analysis": sentiment_results,
            "emotion_theme_analysis": emotion_theme_results
        }
        
        return combined_results
    
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
        individual_results = []
        for feedback in feedback_list:
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