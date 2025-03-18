from langchain_community.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os

# Set test API key
os.environ["OPENAI_API_KEY"] = "test_key"

# Create test documents
documents = [
    Document(page_content="This is a test document", metadata={"source": "test"}),
    Document(page_content="This is another test document", metadata={"source": "test"})
]

print("Test documents created")

try:
    # Create embeddings
    embedding = OpenAIEmbeddings()
    print("Embeddings created")
    
    # Try with the correct parameter name 'embedding' (singular)
    vectorstore = FAISS.from_documents(documents, embedding=embedding)
    print("Successfully created vectorstore using embedding parameter")
except Exception as e:
    print(f"Error with embedding parameter: {str(e)}")
    
    try:
        # Try with the alternative parameter name 'embeddings' (plural)
        vectorstore = FAISS.from_documents(documents, embeddings=embedding)
        print("Successfully created vectorstore using embeddings parameter")
    except Exception as e:
        print(f"Error with embeddings parameter: {str(e)}")
        
    try:
        # Try with positional argument
        vectorstore = FAISS.from_documents(documents, embedding)
        print("Successfully created vectorstore using positional argument")
    except Exception as e:
        print(f"Error with positional argument: {str(e)}") 