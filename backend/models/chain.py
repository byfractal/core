"""
LangChain conversation chain module for UX/UI analysis.
This module handles:
- Conversation state management
- Error handling
- OpenAI integration
- Vector store interaction
"""

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
TEMPERATURE = 0.7  # Controls creativity vs precision
MAX_TOKENS = 1000  # Maximum response length

# Configuration de la mémoire
MEMORY_KEY = 'chat_history'

class ConversationChainError(Exception):
    """Custom exception class for conversation chain errors."""
    pass

def check_api_key():
    """
    Verify if OpenAI API key is properly configured.
    
    Raises:
        ConversationChainError: If API key is not found in environment variables
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise ConversationChainError(
            "OpenAI API key not found. Please configure OPENAI_API_KEY environment variable"
        )

def initialize_conversation_state():
    """
    Initialize or reset conversation state in Streamlit session.
    This ensures conversation persistence between reruns.
    """
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

def get_conversation_chain(vectorstore):
    """
    Create or retrieve a conversation chain for UX/UI analysis.
    
    Args:
        vectorstore: Vector store for context retrieval
        
    Returns:
        ConversationalRetrievalChain: Configured conversation chain
        
    Raises:
        ConversationChainError: For any errors in chain creation
    """
    try:
        # Verify API key
        check_api_key()
        
        # Initialize state if needed
        initialize_conversation_state()
        
        # Return existing conversation if available
        if st.session_state.conversation is not None:
            return st.session_state.conversation
        
        # Create new conversation
        llm = OpenAI(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        # Validate vectorstore
        if not vectorstore:
            raise ConversationChainError("Invalid vectorstore provided")
            
        memory = ConversationBufferMemory(memory_key=MEMORY_KEY, return_messages=True)
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            memory=memory
        )
        
        # Save new conversation in state
        st.session_state.conversation = conversation_chain
        return conversation_chain
        
    except Exception as e:
        error_msg = f"Error creating conversation chain: {str(e)}"
        st.error(error_msg)
        raise ConversationChainError(error_msg)

# Test du fichier standalone (optionnel)
if __name__ == "__main__":
    print("Testing chain.py module")
    try:
        # Initialize test environment
        os.environ["OPENAI_API_KEY"] = "test_key"
        vectorstore = get_vector_store()
        
        # Test conversation chain creation
        chain = get_conversation_chain(vectorstore)
        print("✓ Conversation chain created successfully")
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")


