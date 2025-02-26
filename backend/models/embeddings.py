from langchain_openai import OpenAIEmbeddings
import os

def get_embeddings_model():
    api_key = os.getenv("OPENAI_API_KEY")


    model = "text-embedding-ada-002"

    embeddings = OpenAIEmbeddings(model=model)
    return embeddings

if __name__ == "__main__":
    try:
        embeddings = get_embeddings_model()
        # Test avec un texte simple
        test_result = embeddings.embed_query("Ceci est un test")
        print(f"Test réussi! Dimensions du vecteur: {len(test_result)}")
    except Exception as e:
        print(f"Erreur lors du test: {e}")