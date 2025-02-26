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

#Création de la conversation chain

if "conversation" not in st.session_state:
    st.session_state.conversation = None

def get_conversation_chain(vectorstore):
    llm = OpenAI(model="gpt-4o")
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

st.session_state.conversation 

# Test du fichier standalone (optionnel)
if __name__ == "__main__":
    print("Test du module chain.py")
    # Vous pouvez ajouter du code de test ici


