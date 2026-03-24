import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import streamlit as st

# Load the sentence transformer model - caching to prevent reloading
@st.cache_resource
def get_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def load_knowledge_base(filepath):
    """Load Ayurvedic knowledge from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def create_vector_db(knowledge_data):
    """
    Convert knowledge into embeddings and store in FAISS.
    Returns the FAISS index and the list of documents for retrieval.
    """
    model = get_model()
    documents = [item['content'] for item in knowledge_data]
    
    # Generate embeddings (returns a numpy array)
    embeddings = model.encode(documents)
    
    # Dimension of the embeddings
    dimension = embeddings.shape[1]
    
    # Initialize FAISS Index (L2 distance)
    index = faiss.IndexFlatL2(dimension)
    
    # Add embeddings to the index
    index.add(np.array(embeddings).astype('float32'))
    
    return index, knowledge_data

def retrieve_relevant_knowledge(query, index, knowledge_data, top_k=3):
    """
    Search FAISS index for the most relevant documents to the query.
    """
    model = get_model()
    # Embed the query
    query_vector = model.encode([query]).astype('float32')
    
    # Perform standard vector similarity search
    distances, indices = index.search(query_vector, top_k)
    
    retrieved_results = []
    for idx in indices[0]:
        if idx < len(knowledge_data) and idx != -1:
            retrieved_results.append(knowledge_data[idx])
            
    return retrieved_results

def format_context(retrieved_results):
    """Format the retrieved results into a readable context string."""
    context = ""
    for i, res in enumerate(retrieved_results):
        context += f"[Source: {res['source']}, Topic: {res['topic']}]\n"
        context += f"{res['content']}\n\n"
    return context.strip()
