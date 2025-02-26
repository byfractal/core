from langchain_community.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
import json
import glob

# Trouver un fichier JSON existant dans processed
processed_files = glob.glob("data/amplitude_data/processed/*/*.json")
file_path = processed_files[0] if processed_files else "data/amplitude_data/processed/test_feedback.json"

# Charger le fichier JSON
with open(file_path, "r") as f:
    data = json.load(f)

# Créer les documents pour langchain 
documents = []
for item in data:
    # Adapter selon la structure du fichier
    feedback_text = item["event_properties"]["feedback_text"]
    
    # Créer un document
    doc = Document(
        page_content=feedback_text,
        metadata={
            "user_id": item["user_id"],
            "page": item["event_properties"]["page"]
        }
    )
    documents.append(doc)

# Création des chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=0,
    length_function=len,
)
docs = text_splitter.split_documents(documents)
print(f"Premier document: {docs[1]}")

def get_vector_store(chunk):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(chunk, embeddings=embeddings)
    return vectorstore


def save_vector_store(vectorstore, path="data/vectorstore"):
    vectorstore.save_locale(path)
    return path

def load_vectorstore(path="data/vectorstore"):
    if os.path.exists(path):
        return FAISS.laod_local(path, OpenAIEmbeddings())
    else:
        return None



