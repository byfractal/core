"""
This module implements the design recommendation chains for generating
UI/UX improvement suggestions based on user feedback analysis.
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

Return your recommendations in this exact JSON format:
{{
    "page_id": "{page_id}",
    "recommendations": [
        {{
            "title": "<brief title of recommendation>",
            "description": "<detailed description of what should be changed>",
            "component": "<specific UI component to modify>",
            "location": "<where on the page>",
            "expected_impact": "<how this will improve user experience>",
            "priority": "<high/medium/low>",
            "justification": "<data-driven justification from the analysis>",
            "before_after": {{
                "before": "<brief description of current state>",
                "after": "<brief description of recommended state>"
            }}
        }},
        // Additional recommendations...
    ],
    "implementation_notes": "<any overall notes for implementation>",
    "general_observations": "<overall observations about the page design>"
}}
"""
)

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
        self.llm = OpenAI(model=model, temperature=temperature)
        self._initialize_chain()
        
    def _initialize_chain(self):
        """Initialize the design recommendation chain."""
        self.recommendation_chain = RunnableSequence.from_components(
            design_recommendations_template,
            self.llm
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
        # Convert the analysis summary to a string format suitable for the prompt
        summary_str = json.dumps(analysis_summary, indent=2)
        
        # Generate recommendations
        result = self.recommendation_chain.invoke({
            "analysis_summary": summary_str,
            "page_id": page_id
        })
        
        try:
            return json.loads(result)
        except (json.JSONDecodeError, TypeError):
            return {"raw_result": result, "page_id": page_id}
    
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