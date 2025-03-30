"""
Module for validating design recommendations to ensure they are feasible
and align with best UI/UX practices.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Add root directory to Python path to enable imports
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableSequence

# Design patterns and component library information
SUPPORTED_COMPONENTS = [
    "Button", "TextField", "Dropdown", "Checkbox", "RadioButton", "Slider", 
    "Toggle", "Form", "Card", "Modal", "Navigation", "Menu", "Tab", "Accordion",
    "Table", "List", "Image", "Icon", "Typography", "Container", "Layout",
    "SectionDivider", "BreadCrumb", "Pagination", "SearchBar", "DatePicker",
    "Notification", "Progress", "Tooltip", "Badge", "Carousel"
]

# Template for validation prompt
validation_prompt_template = PromptTemplate(
    input_variables=["recommendation"],
    template="""
You are an expert UI/UX engineer responsible for validating design recommendations to ensure they are feasible and align with best practices.

Review the following design recommendation:
{recommendation}

Evaluate this recommendation based on the following criteria:
1. Technical feasibility - Can this be implemented with standard web components?
2. UI/UX best practices - Does it follow established design patterns?
3. Accessibility - Does it maintain or improve accessibility?
4. Consistency - Is it consistent with modern design systems?
5. Implementation complexity - How difficult would it be to implement?

Provide a detailed analysis of the recommendation's feasibility and any potential issues or modifications needed.

Return a JSON object with this exact structure:
{{
    "recommendation_title": "Title from the original recommendation",
    "is_feasible": true/false,
    "feasibility_score": 0-100,
    "issues": [
        {{
            "issue_type": "technical|ux|accessibility|consistency|complexity",
            "description": "Detailed description of the issue",
            "severity": "high|medium|low",
            "suggested_fix": "Suggestion to address this issue"
        }}
    ],
    "modified_recommendation": {{
        "title": "Same or modified title",
        "description": "Same or modified description",
        "component": "Same or modified component type",
        "location": "Same location",
        "expected_impact": "Same or modified impact",
        "priority": "Same or adjusted priority",
        "justification": "Same justification",
        "before_after": {{
            "before": "Same before state",
            "after": "Modified after state if needed"
        }}
    }},
    "implementation_notes": "Notes on how to implement this recommendation"
}}

IMPORTANT: 
- If the recommendation is mostly feasible with minor adjustments, set is_feasible to true but include the necessary modifications.
- If the recommendation has fundamental flaws that make it impractical, set is_feasible to false and explain why.
- Your response must be valid JSON - nothing else.
"""
)

class RecommendationValidator:
    """
    A class that validates design recommendations for feasibility and alignment with best practices.
    """
    
    def __init__(self, model="gpt-4o", temperature=0):
        """
        Initialize the recommendation validator with the specified LLM.
        
        Args:
            model (str): The OpenAI model to use 
            temperature (float): The temperature setting for the LLM (0-1)
        """
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self._initialize_validator()
        
    def _initialize_validator(self):
        """Initialize the validation chain"""
        parser = JsonOutputParser()
        self.validation_chain = RunnableSequence(
            first=validation_prompt_template,
            last=self.llm
        )
    
    def validate_recommendation(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single design recommendation.
        
        Args:
            recommendation (Dict): The recommendation to validate
            
        Returns:
            Dict: Validation results with feasibility assessment and potential modifications
        """
        # Convert the recommendation to a string format for the prompt
        recommendation_str = json.dumps(recommendation, indent=2)
        
        # Generate validation
        result = self.validation_chain.invoke({
            "recommendation": recommendation_str
        })
        
        # Process the validation result
        try:
            # Extract content from AIMessage if needed
            if hasattr(result, 'content'):
                result_content = result.content
            else:
                result_content = str(result)
                
            # Clean up the result to ensure valid JSON
            result_content = result_content.replace("```json", "").replace("```", "").strip()
            
            # Parse the validation result
            validation_result = json.loads(result_content)
            return validation_result
        except Exception as e:
            # Return an error result if parsing fails
            return {
                "recommendation_title": recommendation.get("title", "Unknown recommendation"),
                "is_feasible": False,
                "feasibility_score": 0,
                "issues": [{
                    "issue_type": "technical",
                    "description": f"Failed to validate recommendation: {str(e)}",
                    "severity": "high",
                    "suggested_fix": "Please review the recommendation format"
                }],
                "modified_recommendation": recommendation,
                "implementation_notes": "Validation failed, please review the recommendation manually"
            }
    
    def validate_all_recommendations(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate all recommendations in a recommendations object.
        
        Args:
            recommendations (Dict): The full recommendations object with multiple recommendations
            
        Returns:
            Dict: Updated recommendations with validation results and modifications
        """
        validated_recommendations = {
            "page_id": recommendations.get("page_id", "unknown_page"),
            "recommendations": [],
            "implementation_notes": recommendations.get("implementation_notes", ""),
            "general_observations": recommendations.get("general_observations", ""),
            "validation_summary": {
                "total_recommendations": 0,
                "feasible_count": 0,
                "needs_modification_count": 0,
                "infeasible_count": 0,
                "average_feasibility_score": 0
            }
        }
        
        # Track validation statistics
        total_score = 0
        feasible_count = 0
        needs_modification_count = 0
        infeasible_count = 0
        
        # Process each recommendation
        for rec in recommendations.get("recommendations", []):
            # Validate the recommendation
            validation_result = self.validate_recommendation(rec)
            
            # Use the modified recommendation if available
            modified_rec = validation_result.get("modified_recommendation", rec)
            
            # Add validation information
            modified_rec["validation"] = {
                "is_feasible": validation_result.get("is_feasible", False),
                "feasibility_score": validation_result.get("feasibility_score", 0),
                "issues": validation_result.get("issues", [])
            }
            
            # Update statistics
            if validation_result.get("is_feasible", False):
                if validation_result.get("issues", []):
                    needs_modification_count += 1
                else:
                    feasible_count += 1
            else:
                infeasible_count += 1
                
            total_score += validation_result.get("feasibility_score", 0)
            
            # Add to validated recommendations
            validated_recommendations["recommendations"].append(modified_rec)
            
        # Update validation summary
        total_recommendations = len(validated_recommendations["recommendations"])
        validated_recommendations["validation_summary"] = {
            "total_recommendations": total_recommendations,
            "feasible_count": feasible_count,
            "needs_modification_count": needs_modification_count,
            "infeasible_count": infeasible_count,
            "average_feasibility_score": total_score / total_recommendations if total_recommendations > 0 else 0
        }
        
        # Sort recommendations by feasibility and priority
        validated_recommendations["recommendations"] = sorted(
            validated_recommendations["recommendations"],
            key=lambda r: (
                not r["validation"]["is_feasible"],
                {"high": 0, "medium": 1, "low": 2}.get(r.get("priority", "medium"), 1),
                -r["validation"]["feasibility_score"]
            )
        )
        
        return validated_recommendations
    
    def check_component_support(self, component_type: str) -> Tuple[bool, List[str]]:
        """
        Check if a component type is supported and suggest alternatives if not.
        
        Args:
            component_type (str): The component type to check
            
        Returns:
            Tuple[bool, List[str]]: (is_supported, alternative_suggestions)
        """
        # Normalize component type
        normalized_type = component_type.lower().strip()
        
        # Check if component is directly supported
        for supported in SUPPORTED_COMPONENTS:
            if normalized_type == supported.lower():
                return True, []
        
        # Component not directly supported, find alternatives
        alternatives = []
        for supported in SUPPORTED_COMPONENTS:
            if normalized_type in supported.lower() or supported.lower() in normalized_type:
                alternatives.append(supported)
        
        # If no close matches, suggest common components
        if not alternatives:
            if "input" in normalized_type or "field" in normalized_type:
                alternatives = ["TextField", "Dropdown", "Checkbox", "RadioButton"]
            elif "button" in normalized_type:
                alternatives = ["Button", "Toggle"]
            elif "container" in normalized_type or "section" in normalized_type:
                alternatives = ["Container", "Card", "Layout"]
            elif "nav" in normalized_type or "menu" in normalized_type:
                alternatives = ["Navigation", "Menu", "Tab", "BreadCrumb"]
            else:
                alternatives = ["Container", "Card", "Layout"]
        
        return False, alternatives[:3]  # Return top 3 alternatives

# Test function
if __name__ == "__main__":
    # Sample recommendation for testing
    sample_recommendation = {
        "title": "Add Clear Filters Button",
        "description": "Add a clearly visible 'Clear Filters' button next to the filter controls",
        "component": "Button",
        "location": "Top of search results, next to existing filters",
        "expected_impact": "Users can easily reset search filters without refreshing the page",
        "priority": "medium",
        "justification": "Users reported difficulty clearing multiple filters",
        "before_after": {
            "before": "No way to clear all filters at once",
            "after": "Clear Filters button prominently displayed next to filter controls"
        }
    }
    
    # Create validator and test
    validator = RecommendationValidator()
    validation_result = validator.validate_recommendation(sample_recommendation)
    
    print("Validation Result:")
    print(json.dumps(validation_result, indent=2)) 