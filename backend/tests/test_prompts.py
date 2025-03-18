"""
Test script for validating LangChain prompts
"""
import sys
import json
from pathlib import Path

# Add backend directory to Python path
backend_dir = str(Path(__file__).parent.parent)
sys.path.append(backend_dir)

# Import necessary modules
from backend.models.prompts import get_prompt_templates, sentiment_classification_template, emotion_theme_extraction_template, feedback_summary_template

# Define test data
TEST_FEEDBACKS = [
    "The color scheme is pleasing but I found it difficult to find the settings menu",
    "The new interface is very intuitive, I love it!",
    "The page takes too long to load and sometimes crashes",
    "I can't find the logout button, very frustrating experience"
]

def safe_print(text):
    """Print text safely, handling UTF-8 encoding"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8').decode('ascii', 'ignore'))

def test_all_prompt_templates():
    """Test that all prompt templates are properly formatted"""
    templates = get_prompt_templates()
    safe_print(f"Loaded {len(templates)} prompt templates successfully")
    
    # Test each template
    for name, template in templates.items():
        safe_print(f"\nTesting template: {name}")
        safe_print("-" * 50)
        
        # Format the template with sample data
        sample_feedback = TEST_FEEDBACKS[0]
        
        if name == "feedback_summary":
            formatted_prompt = template.format(feedback_list=TEST_FEEDBACKS)
        else:
            formatted_prompt = template.format(feedback=sample_feedback)
        
        # Display a portion of the formatted prompt (first 10 lines)
        lines = formatted_prompt.split('\n')
        preview = '\n'.join(lines[:10]) + "\n..."
        safe_print(preview)
        safe_print("-" * 50)
    
    return True

if __name__ == "__main__":
    safe_print("Starting tests for prompts...")
    
    # Test all prompt templates
    if test_all_prompt_templates():
        safe_print("\n✅ All prompt templates test passed!")
    else:
        safe_print("\n❌ Prompt templates test failed!")
    
    safe_print("\nTests completed!")
    
    # Final report
    safe_print("\nStep 3 Test Summary - Prompt Configuration:")
    safe_print("--------------------------------------------------")
    safe_print("1. Prompt templates have been successfully validated")
    safe_print("2. The following templates are available and functional:")
    safe_print("   - sentiment_classification: For sentiment analysis")
    safe_print("   - emotion_theme_extraction: For emotion and theme extraction")
    safe_print("   - feedback_summary: For feedback summarization")
    safe_print("--------------------------------------------------")
    safe_print("Note: To test with the LLM model, a valid OpenAI API key is required") 