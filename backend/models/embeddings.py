from langchain_openai import OpenAIEmbeddings
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajouter le répertoire racine au PYTHONPATH
root_dir = str(Path(__file__).parent.parent.parent.absolute())
sys.path.append(root_dir)

# Charger les variables d'environnement avec un chemin absolu vers .env
env_path = os.path.join(root_dir, '.env')
print(f"Loading environment from: {env_path}")
load_dotenv(dotenv_path=env_path)

def get_embeddings_model():
    # Récupérer explicitement la clé API
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Afficher un message de débogage (masqué pour la sécurité)
    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"Clé API trouvée: {masked_key}")
    else:
        print("WARNING: No API key found in environment variables")
        # Tentative alternative de récupération de la clé API
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY='):
                        api_key = line.strip().split('=', 1)[1].strip('"').strip("'")
                        print("Clé API récupérée directement du fichier .env")
                        break
        except Exception as e:
            print(f"Error reading .env file: {e}")

    # Vérifier si la clé ressemble à "test_key" et avertir
    if api_key and "test_key" in api_key:
        print("WARNING: Using test_key will cause authentication errors with the OpenAI API")
        
    model = "text-embedding-ada-002"

    # Force pass the API key explicitly to override any defaults
    print("Initializing OpenAIEmbeddings with explicit API key")
    embeddings = OpenAIEmbeddings(model=model, openai_api_key=api_key)
    
    # Override the client's API key directly to be absolutely sure
    if hasattr(embeddings, 'client') and hasattr(embeddings.client, 'api_key'):
        embeddings.client.api_key = api_key
        print("API key directly set on client object")
        
    return embeddings

if __name__ == "__main__":
    try:
        # Forcer la valeur dans l'environnement en dernier recours
        if "OPENAI_API_KEY" in os.environ and "test_key" in os.environ["OPENAI_API_KEY"]:
            # Récupérer la clé du fichier .env
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('OPENAI_API_KEY='):
                        api_key = line.strip().split('=', 1)[1].strip('"').strip("'")
                        if "test_key" not in api_key:
                            os.environ["OPENAI_API_KEY"] = api_key
                            print("OPENAI_API_KEY environment variable overridden with value from .env file")
                        break
                        
        embeddings = get_embeddings_model()
        
        # Test avec un texte simple
        print("Testing embedding with a simple query...")
        test_result = embeddings.embed_query("Ceci est un test")
        print(f"Test réussi! Dimensions du vecteur: {len(test_result)}")
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        
        # Diagnostics supplémentaires
        import inspect
        if 'OpenAIEmbeddings' in sys.modules:
            openai_embeddings_module = sys.modules['langchain_openai.embeddings.openai']
            print(f"OpenAIEmbeddings module location: {inspect.getfile(openai_embeddings_module)}")