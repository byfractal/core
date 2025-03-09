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
1. Primary emotions expressed (frustration, satisfaction, confusion, etc.)
2. Key themes or topics mentioned (navigation, forms, layout, performance, etc.)
3. Specific UI/UX issues or pain points

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
    # Example usage
    test_feedback = "I found the checkout process confusing and too lengthy. There were too many form fields and the submit button was hard to find."
    
    # Test sentiment classification prompt
    sentiment_prompt = sentiment_classification_template.format(feedback=test_feedback)
    print("Sentiment Classification Prompt:")
    print(sentiment_prompt)
    print("\n" + "-"*50 + "\n")
    
    # Test emotion/theme extraction prompt
    emotion_prompt = emotion_theme_extraction_template.format(feedback=test_feedback)
    print("Emotion/Theme Extraction Prompt:")
    print(emotion_prompt) 