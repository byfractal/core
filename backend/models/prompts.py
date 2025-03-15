"""
This module contains all the prompt templates used in the LangChain pipelines
for analyzing user feedback and generating UI/UX recommendations.

Each template is optimized for a specific task in the analysis process:
- Sentiment classification
- Emotion/theme extraction
- Summary generation
"""

from langchain.prompts import PromptTemplate

# Sentiment Analysis Prompt Template
# This prompt classifies user feedback as positive, negative, or neutral
sentiment_classification_template = PromptTemplate(
    input_variables=["feedback"],
    template="""
You are an expert UX researcher analyzing user feedback about a digital interface.
Your task is to classify the sentiment of the following user feedback as POSITIVE, NEGATIVE, or NEUTRAL.
Provide a JSON response with the sentiment and confidence score.

User Feedback: {feedback}

Analyze the feedback carefully, looking for emotional language, complaints, praise, or neutral observations.
Consider the context of UI/UX when determining sentiment.

Examples:
- "I love how easy it is to navigate this app" → POSITIVE
- "The login process took forever and I couldn't figure out how to reset my password" → NEGATIVE
- "The dashboard shows all my data but I wish there were filtering options" → MIXED (classify as slightly NEGATIVE since it indicates a missing feature)
- "The page has a form with 5 fields" → NEUTRAL (purely descriptive)

For mixed feedback, weigh the dominant sentiment and lean towards the user's final impression.

Return your analysis in this exact JSON format:
{{
    "sentiment": "POSITIVE/NEGATIVE/NEUTRAL",
    "confidence": <score between 0 and 1>,
    "reasoning": "<brief explanation of your classification>"
}}
"""
)

# Emotion/Theme Extraction Prompt Template
# This prompt identifies key emotions, themes, and specific UI/UX issues from feedback
emotion_theme_extraction_template = PromptTemplate(
    input_variables=["feedback"],
    template="""
You are an expert UX researcher analyzing user feedback about a digital interface.
Your task is to extract the key emotions, themes, and specific UI/UX issues from the following feedback.

User Feedback: {feedback}

Analyze the feedback carefully to identify:

1. Primary emotions expressed (select from these categories):
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

2. Key UX/UI themes or topics mentioned (select all that apply):
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

3. Specific UI/UX issues or pain points:
   - Describe the exact problem the user is experiencing
   - Identify where in the interface the issue occurs
   - Note any workarounds the user attempted

Return your analysis in this exact JSON format:
{{
    "emotions": ["<emotion1>", "<emotion2>", ...],
    "themes": ["<theme1>", "<theme2>", ...],
    "issues": ["<specific issue1>", "<specific issue2>", ...],
    "severity": "<low/medium/high>"
}}
"""
)

# Feedback Summary Prompt Template
# This prompt generates a concise summary of multiple pieces of feedback
feedback_summary_template = PromptTemplate(
    input_variables=["feedback_list"],
    template="""
You are an expert UX researcher analyzing multiple pieces of user feedback about a digital interface.
Your task is to create a concise summary that captures the main insights across all feedback.

User Feedback Items:
{feedback_list}

Create a summary that:
1. Identifies common patterns and themes across feedback
2. Highlights the most significant UI/UX issues
3. Notes any positive aspects that should be preserved
4. Provides a balanced view of user sentiment

Return your summary in this exact JSON format:
{{
    "summary": "<concise summary of all feedback>",
    "key_issues": ["<issue1>", "<issue2>", ...],
    "positive_aspects": ["<positive1>", "<positive2>", ...],
    "overall_sentiment": "<overall sentiment across all feedback>",
    "priority_recommendations": ["<recommendation1>", "<recommendation2>", ...]
}}
"""
)

# Function to get all available prompt templates
def get_prompt_templates():
    """Returns a dictionary of all available prompt templates"""
    return {
        "sentiment_classification": sentiment_classification_template,
        "emotion_theme_extraction": emotion_theme_extraction_template,
        "feedback_summary": feedback_summary_template
    }

# Test function
if __name__ == "__main__":
    import json 
    from pathlib import Path
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    # Import data
    from create_test_data import test_data

    # Display the number of feedbacks loaded
    print(f"Loaded {len(test_data)} feedback items from create_test_data.py")

    # Browns each feedback in the test data
    for i, feedback_item in enumerate(test_data):
        # Extract text from feedback
        feedback_text = feedback_item.get("event_properties", {}).get("feedback_text", "")

        # Check if the feedback exists
        if not feedback_text:
            continue

        # Display feedback informatuon currently being processed
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


    


   