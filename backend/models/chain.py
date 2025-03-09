import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
root_dir = str(Path(__file__).parent.parent.parent)
sys.path.append(root_dir)

# Importer Streamlit
import streamlit as st

from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import OpenAI
from backend.models.vector_store import get_vector_store

# Configuration des paramètres du modèle
MODEL_NAME = "gpt-4"
TEMPERATURE = 0.7
MAX_TOKENS = 1000

# Configuration de la mémoire
MEMORY_KEY = 'chat_history'

class ConversationChainError(Exception):
    """Classe personnalisée pour les erreurs de chaîne de conversation"""
    pass

def check_api_key():
    """Vérifie si la clé API OpenAI est configurée"""
    if not os.getenv("OPENAI_API_KEY"):
        raise ConversationChainError(
            "Clé API OpenAI non trouvée. Veuillez configurer la variable d'environnement OPENAI_API_KEY"
        )

def initialize_conversation_state():
    """Initialise l'état de la conversation si nécessaire"""
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

def get_conversation_chain(vectorstore):
    """Crée ou récupère une chaîne de conversation"""
    try:
        # Vérifier la clé API
        check_api_key()
        
        # Initialiser l'état si nécessaire
        initialize_conversation_state()
        
        # Si une conversation existe déjà, la retourner
        if st.session_state.conversation is not None:
            return st.session_state.conversation
        
        # Sinon, créer une nouvelle conversation
        llm = OpenAI(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        # Vérifier que le vectorstore est valide
        if not vectorstore:
            raise ConversationChainError("Vectorstore non valide")
            
        memory = ConversationBufferMemory(memory_key=MEMORY_KEY, return_messages=True)
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            memory=memory
        )
        
        # Sauvegarder la nouvelle conversation dans l'état
        st.session_state.conversation = conversation_chain
        return conversation_chain
        
    except Exception as e:
        error_msg = f"Erreur lors de la création de la chaîne de conversation: {str(e)}"
        st.error(error_msg)  # Afficher l'erreur dans l'interface Streamlit
        raise ConversationChainError(error_msg)

# Test du fichier standalone (optionnel)
if __name__ == "__main__":
    print("Test du module chain.py")
    # Vous pouvez ajouter du code de test ici


