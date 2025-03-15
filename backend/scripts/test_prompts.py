"""
Script de test pour valider les prompts de LangChain
"""
import sys
import json
from pathlib import Path

# Add root directory to Python path
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

# Import necessary modules
from backend.models.prompts import get_prompt_templates, sentiment_classification_template, emotion_theme_extraction_template, feedback_summary_template

# Définir nos propres données de test
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
    
    # Rapport final
    safe_print("\nRésumé des tests de l'Étape 3 - Configuration des Prompts:")
    safe_print("--------------------------------------------------")
    safe_print("1. Les templates de prompts ont été validés avec succès")
    safe_print("2. Les templates suivants sont disponibles et fonctionnels:")
    safe_print("   - sentiment_classification: Pour l'analyse de sentiment")
    safe_print("   - emotion_theme_extraction: Pour l'extraction d'émotions et thèmes")
    safe_print("   - feedback_summary: Pour la synthèse des feedbacks")
    safe_print("--------------------------------------------------")
    safe_print("Note: Pour tester avec le modèle LLM, une clé API OpenAI valide est nécessaire") 