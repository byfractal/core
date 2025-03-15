from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

# Charger les variables d'environnement du fichier .env
load_dotenv()

def get_embeddings_model():
    # Récupérer la clé API depuis les variables d'environnement
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Afficher un message pour debug
    if api_key is None:
        print("ATTENTION: Aucune clé API trouvée dans les variables d'environnement")
    else:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"Clé API trouvée: {masked_key}")

    model = "text-embedding-ada-002"

    # Passer explicitement la clé API
    embeddings = OpenAIEmbeddings(model=model, openai_api_key=api_key)
    return embeddings

if __name__ == "__main__":
    try:
        embeddings = get_embeddings_model()
        # Test avec un texte simple
        test_result = embeddings.embed_query("Ceci est un test")
        print(f"Test réussi! Dimensions du vecteur: {len(test_result)}")
    except Exception as e:
        print(f"Erreur lors du test: {e}")