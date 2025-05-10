"""
This module contains all the prompt templates used in the LangChain pipelines
for analyzing user feedback and generating UI/UX recommendations.

Each template is optimized for a specific task in the analysis process using
principles learned from leaked system prompts of popular AI tools.
"""

from langchain.prompts import PromptTemplate

# ----------------------------------------------------------------------
# SENTIMENT ANALYSIS PROMPT
# ----------------------------------------------------------------------
sentiment_classification_template = PromptTemplate(
    input_variables=["feedback"],
    template="""
You are an expert UX researcher analyzing user feedback about a digital interface.
Your task is to classify the sentiment of the following user feedback as POSITIVE, NEGATIVE, or NEUTRAL.

### Input JSON Schema
{
    "feedback": "User feedback text to analyze for sentiment"
}

### Output JSON Schema
{
    "sentiment": "POSITIVE|NEGATIVE|NEUTRAL",
    "confidence": "Float between 0.0 and 1.0",
    "reasoning": "Brief explanation of classification rationale"
}

### Step-by-Step Analysis Process
1. Read and understand the entire user feedback, paying attention to emotional cues
2. Identify all positive expressions (praise, satisfaction, appreciation)
3. Identify all negative expressions (complaints, problems, frustration)
4. Identify all neutral/descriptive statements
5. Weigh the overall sentiment by considering which sentiment dominates
6. Assign confidence level based on clarity and strength of emotional signals
7. Verify classification before responding, ensuring it matches the user's intent

### Input
User Feedback: {feedback}

### Examples
Input: "I love how easy it is to navigate this app"
Output: {{ "sentiment": "POSITIVE", "confidence": 0.95, "reasoning": "Strong positive language with 'love' and praise for navigation" }}

Input: "The login process took forever and I couldn't figure out how to reset my password"
Output: {{ "sentiment": "NEGATIVE", "confidence": 0.90, "reasoning": "Clear frustration about time taken and inability to perform a task" }}

Input: "The dashboard shows all my data but I wish there were filtering options"
Output: {{ "sentiment": "MIXED", "confidence": 0.75, "reasoning": "Positive observation about data visibility but negative wish for missing functionality" }}

Input: "The page has a form with 5 fields"
Output: {{ "sentiment": "NEUTRAL", "confidence": 0.98, "reasoning": "Purely descriptive statement without emotional valence" }}

### Requirements
- For mixed feedback, determine the dominant sentiment
- Consider context - missing features are generally negative indicators
- Focus on UI/UX context when evaluating sentiment
- Provide a clear reasoning that references specific words or phrases

Output your response as a valid JSON object with no additional text.
"""
)

# ----------------------------------------------------------------------
# EMOTION/THEME EXTRACTION PROMPT
# ----------------------------------------------------------------------
emotion_theme_extraction_template = PromptTemplate(
    input_variables=["feedback"],
    template="""
You are an expert UX researcher analyzing user feedback about a digital interface.
Your task is to extract the key emotions, themes, and specific UI/UX issues from user feedback.

### Input JSON Schema
{
    "feedback": "User feedback text to analyze for emotions and themes"
}

### Output JSON Schema
{
    "emotions": ["List of primary emotions detected"],
    "themes": ["List of UX/UI themes or topics mentioned"],
    "issues": ["List of specific UI/UX issues or pain points"],
    "severity": "low|medium|high"
}

### Step-by-Step Analysis Process
1. Read and understand the entire user feedback
2. Identify emotions expressed by the user
3. Categorize UX/UI themes mentioned
4. Extract specific issues, pain points, or problems
5. Evaluate overall severity based on emotion intensity and issue impact
6. Verify completeness and accuracy of extraction

### Input
User Feedback: {feedback}

### Emotions Categories
- Frustration/Annoyance
- Confusion/Uncertainty
- Satisfaction/Delight
- Disappointment
- Impatience
- Trust/Confidence
- Anxiety/Concern
- Indifference
- Overwhelmed
- Other (specify if not in the above categories)

### UX/UI Theme Categories
- Navigation/Information Architecture
- Form Design/Input Fields
- Page Layout/Visual Hierarchy
- Load Time/Performance
- Content Clarity/Readability
- Accessibility Issues
- Mobile Responsiveness
- Feedback/Error Messages
- Visual Design/Aesthetics
- Consistency Issues
- Workflow/Process Flow
- Specific Feature Requests
- Other (specify if not in the above categories)

### Severity Guidelines
- Low: Minor issue, minimal impact on experience, aesthetic preference
- Medium: Moderate impact on usability, causes some friction but has workarounds
- High: Significant issue, prevents task completion, causes strong negative emotion

Output your response as a valid JSON object with no additional text.
"""
)

# ----------------------------------------------------------------------
# FEEDBACK SUMMARY PROMPT
# ----------------------------------------------------------------------
feedback_summary_template = PromptTemplate(
    input_variables=["feedback_list"],
    template="""
You are an expert UX researcher analyzing multiple pieces of user feedback about a digital interface.
Your task is to create a concise summary that captures the main insights across all feedback.

### Input JSON Schema
{
    "feedback_list": "List of separate user feedback items"
}

### Output JSON Schema
{
    "summary": "Concise summary of all feedback",
    "key_issues": ["List of major UI/UX issues identified"],
    "positive_aspects": ["List of UI/UX elements that work well"],
    "overall_sentiment": "Aggregate sentiment across all feedback",
    "priority_recommendations": ["List of actionable improvements"]
}

### Step-by-Step Analysis Process
1. Read and understand all feedback items
2. Identify recurring themes, issues, and sentiments
3. Find patterns of positive feedback and what users like
4. Detect critical pain points affecting multiple users
5. Formulate clear, actionable recommendations based on the feedback
6. Verify analysis is balanced, comprehensive, and prioritized properly

### Input
User Feedback Items:
{feedback_list}

### Analysis Requirements
- Focus on identifying patterns across feedback (not just individual issues)
- Maintain a balanced perspective of both positive and negative aspects
- Prioritize issues based on frequency of mention and impact on user experience
- Make recommendations specific and actionable
- Consider both quick wins and strategic improvements

Output your response as a valid JSON object with no additional text.
"""
)

# ----------------------------------------------------------------------
# DESIGN RECOMMENDATIONS DETAILED PROMPT
# ----------------------------------------------------------------------
ux_design_recommendations_template = PromptTemplate(
    input_variables=["analysis_summary", "page_info", "component_list"],
    template="""
You are an expert UI/UX designer specializing in data-driven design optimization based on user behavioral analytics and feedback.
Your task is to generate specific, high-impact design recommendations to improve the user experience.

### Input JSON Schema
{
    "analysis_summary": "Detailed summary of user feedback and analytics",
    "page_info": "Information about the page being analyzed",
    "component_list": "List of available UI components that can be modified"
}

### Output JSON Schema
{
    "page_id": "Identifier of the page being optimized",
    "recommendations": [
        {
            "title": "Clear, action-oriented title",
            "description": "Detailed description with specifications",
            "component": "Specific UI component to modify",
            "location": "Precise location on the page",
            "expected_impact": "Specific measurable impact",
            "priority": "high|medium|low",
            "justification": "Data-driven justification",
            "before_after": {
                "before": "Current problematic state",
                "after": "Improved state with changes"
            },
            "dom_patch": {
                "selector": "CSS selector targeting the element",
                "action": "add|modify|remove",
                "code": "CSS or HTML code to apply"
            }
        }
    ],
    "implementation_notes": "Technical guidance for implementation",
    "general_observations": "Overall design observations"
}

### Step-by-Step Recommendation Process
1. Analyze the provided user feedback and behavioral data thoroughly
2. Identify the top 3-5 most impactful UX issues to address
3. For each issue:
   a. Define the exact problem based on data
   b. Determine which component needs modification
   c. Design a specific, measurable solution
   d. Create precise implementation details
   e. Verify the solution addresses the root cause
4. Prioritize recommendations by impact vs. implementation effort
5. Review all recommendations for completeness, feasibility, and specificity
6. Format output according to the required JSON schema

### Input
Analysis Summary: {analysis_summary}
Page Information: {page_info}
Available Components: {component_list}

### UX Design Principles to Apply
- Visual Hierarchy: Elements should be prioritized by importance
- Progressive Disclosure: Reveal information gradually as needed
- Recognition over Recall: Make options visible and accessible
- Error Prevention: Design to prevent errors before they occur
- Consistency: Maintain consistent patterns and behaviors
- Feedback: Provide clear feedback for user actions
- Efficiency: Minimize steps to complete common tasks
- Accessibility: Ensure interface is usable by people with disabilities

### DOM Patch Guidelines
- Provide exact CSS selectors that target the specific elements
- Keep changes minimal and focused on solving the specific issue
- Use standard CSS/HTML that works across modern browsers
- Namespace any added classes with 'ext-' prefix to avoid conflicts
- For layout changes, consider both mobile and desktop viewports

Output your response as a valid JSON object with no additional text.
"""
)

# ----------------------------------------------------------------------
# DOM MODIFICATION VALIDATOR PROMPT
# ----------------------------------------------------------------------
dom_modification_validator_template = PromptTemplate(
    input_variables=["recommendation", "page_html"],
    template="""
You are an expert front-end developer specializing in UI implementation and quality assurance.
Your task is to validate and improve a proposed DOM modification to ensure it will work correctly when applied.

### Input JSON Schema
{
    "recommendation": "The complete recommendation object with DOM patch details",
    "page_html": "Relevant HTML snippet from the target page"
}

### Output JSON Schema
{
    "is_valid": true|false,
    "improved_patch": {
        "selector": "CSS selector targeting the element",
        "action": "add|modify|remove",
        "code": "CSS or HTML code to apply"
    },
    "validation_notes": "Explanation of issues found and improvements made",
    "potential_side_effects": "Any potential side effects of the change"
}

### Step-by-Step Validation Process
1. Examine the provided HTML to understand the page structure
2. Check if the CSS selector in the recommendation matches actual elements in the HTML
3. Verify that the proposed change addresses the UX issue effectively
4. Ensure the patch won't cause layout shifts, style conflicts, or other issues
5. Improve the selector or code if necessary for better targeting or performance
6. Check for accessibility implications and browser compatibility issues
7. Document any concerns or side effects

### Input
Recommendation: {recommendation}
Page HTML: {page_html}

### Validation Requirements
- Selectors must match at least one element in the page
- Changes should preserve accessibility (contrast, focus states, semantic structure)
- CSS changes should be specific enough to avoid unexpected side effects
- HTML changes should maintain proper document structure and semantics
- Consider both desktop and mobile views when validating layout changes
- Ensure the change actually addresses the UX issue identified

Output your response as a valid JSON object with no additional text.
"""
)

# ----------------------------------------------------------------------
# USER JOURNEY ANALYZER PROMPT
# ----------------------------------------------------------------------
user_journey_analyzer_template = PromptTemplate(
    input_variables=["session_recordings", "page_id"],
    template="""
You are an expert in UX research specializing in session recording analysis.
Your task is to analyze user journey data to identify friction points, confusion areas, and drop-offs.

### Input JSON Schema
{
    "session_recordings": "Data from multiple user session recordings",
    "page_id": "Identifier of the page being analyzed"
}

### Output JSON Schema
{
    "journey_patterns": [
        {
            "pattern_name": "Short descriptive name",
            "frequency": "Percentage of users following this pattern",
            "steps": ["List of steps in the journey"],
            "success_rate": "Percentage completing the journey",
            "friction_points": [
                {
                    "location": "Where in the journey friction occurs",
                    "behavior": "Observed user behavior",
                    "severity": "high|medium|low",
                    "impact": "Description of impact on conversion/experience"
                }
            ]
        }
    ],
    "confusion_areas": [
        {
            "element": "UI element causing confusion",
            "indicators": ["List of behaviors indicating confusion"],
            "frequency": "How often this occurs",
            "potential_causes": ["List of potential causes"]
        }
    ],
    "recommendations": [
        {
            "issue": "Issue to address",
            "suggestion": "Specific improvement suggestion",
            "expected_impact": "Anticipated improvement"
        }
    ]
}

### Step-by-Step Analysis Process
1. Review all session recording data to identify common paths users take
2. Group similar navigation patterns into distinct journey types
3. For each journey type, identify success rates and completion times
4. Detect points where users hesitate, repeat actions, or abandon
5. Analyze mouse movements, clicks, and time spent on elements
6. Determine common confusion areas based on behavioral signals
7. Formulate specific recommendations based on observed patterns
8. Verify analysis is thorough and insights are actionable

### Input
Session Recordings: {session_recordings}
Page ID: {page_id}

### Behavioral Indicators of UX Issues
- Repeated clicks on non-interactive elements (confusion)
- Rapid back-and-forth navigation (lostness)
- Long hesitation before form submission (uncertainty)
- Rage clicks or rapid cursor movements (frustration)
- Abandonment after specific interactions (friction)
- Multiple form field edits (validation issues)
- Excessive scrolling up and down (search behavior)
- Quick exit after page load (irrelevance or load issues)

Output your response as a valid JSON object with no additional text.
"""
)

# ----------------------------------------------------------------------
# FUNCTION DEFINITIONS
# ----------------------------------------------------------------------
def get_prompt_templates():
    """Returns a dictionary of all available prompt templates"""
    return {
        "sentiment_classification": sentiment_classification_template,
        "emotion_theme_extraction": emotion_theme_extraction_template,
        "feedback_summary": feedback_summary_template,
        "ux_design_recommendations": ux_design_recommendations_template,
        "dom_modification_validator": dom_modification_validator_template,
        "user_journey_analyzer": user_journey_analyzer_template
    }

# Test function
if __name__ == "__main__":
    import json 
    from pathlib import Path
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    # Import data
    try:
        from create_test_data import test_data
    except ImportError:
        test_data = [
            {"event_properties": {"feedback_text": "I found the checkout form confusing with too many fields."}},
            {"event_properties": {"feedback_text": "Love the new dashboard design, very intuitive!"}}
        ]

    # Display the number of feedbacks loaded
    print(f"Loaded {len(test_data)} feedback items for testing")

    # Browse each feedback in the test data
    for i, feedback_item in enumerate(test_data):
        # Extract text from feedback
        feedback_text = feedback_item.get("event_properties", {}).get("feedback_text", "")

        # Check if the feedback exists
        if not feedback_text:
            continue

        # Display feedback information currently being processed
        print(f"\n{'='*50}\nTesting with feedback {i+1}: {feedback_text}\n{'='*50}\n")

        # Test the sentiment classification prompt 
        sentiment_prompt = sentiment_classification_template.format(feedback=feedback_text)
        print("Sentiment Classification Prompt:")
        print(sentiment_prompt)
        print("\n" + "-"*50 + "\n")

        # Test the emotion/theme extraction prompt
        emotion_prompt = emotion_theme_extraction_template.format(feedback=feedback_text)
        print(emotion_prompt)
        print("\n" + "-"*50 + "\n")

"""
Module for interacting with LLM models via LangChain.
Provides functions for sending prompts to LLMs and processing their responses.
"""

import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from langchain_openai import OpenAI, ChatOpenAI
from langchain.output_parsers import JsonOutputToolsParser
from langchain.schema import Document

# Load environment variables (API keys)
load_dotenv()

def get_llm_model(model_name: str = "gpt-4o", temperature: float = 0):
    """
    Initializes and returns an LLM model of Langchain

    Args:
        model_name: Name of the model to be used (default: gpt-4o)
        temperature: Temperature parameter between 0 and 1 (0 = most deterministic)
        
    Returns:
        An initialised LLM model
    """
    if "gpt-3.5" in model_name or "gpt-4" in model_name:
        # For GPT models, use ChatOpenAI, which is more efficient
        return ChatOpenAI(model_name=model_name, temperature=temperature)
    else:
        # Fallback for other models
        return OpenAI(model_name=model_name, temperature=temperature)
    
def send_prompt_to_llm(prompt: str, model_name: str = "gpt-4o", temperature: float = 0) -> str:
    """
    Sends a simple prompt to an LLM and returns its response as text.
    
    Args:
        prompt: The text of the prompt to send
        model_name: Name of the model to use
        temperature: Temperature parameter
        
    Returns:
        The text response from the LLM
    """
    llm = get_llm_model(model_name, temperature)
    response = llm.invoke(prompt)
    return response

def analyze_with_json_output(prompt: str, model_name: str = "gpt-4o", temperature: float = 0) -> Dict[str, Any]:
    """
    Sends a prompt to the LLM and parses its response as JSON.
    
    Args:
        prompt: The text of the prompt to send
        model_name: Name of the model to use
        temperature: Temperature parameter
        
    Returns:
        A Python dictionary containing the parsed JSON data
    """
    llm = get_llm_model(model_name, temperature)
    output_parser = JsonOutputToolsParser()

    try:
        # Create a LangChain string with JSON parser
        chain = llm | output_parser
        result = chain.invoke(prompt)
        return result
    except Exception as e:
        print(f"Error when parsing JSON: {e}")
        # If this fails, try to recover the raw response
        raw_response = llm.invoke(prompt)
        return {"error": str(e), "raw_response": raw_response}


    


   