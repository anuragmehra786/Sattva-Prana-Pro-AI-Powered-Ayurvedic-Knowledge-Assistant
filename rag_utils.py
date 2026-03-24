import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import streamlit as st

@st.cache_resource
def get_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def load_knowledge_base(filepath):
    """Load Ayurvedic knowledge from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

@st.cache_resource
def create_vector_db(_knowledge_data):
    """
    Convert knowledge into embeddings and store in FAISS.
    Returns the FAISS index.
    """
    model = get_model()
    documents = [item['content'] for item in _knowledge_data]
    embeddings = model.encode(documents)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    return index

def retrieve_relevant_knowledge(query, index, knowledge_data, top_k=3):
    """
    Search FAISS index for the most relevant documents to the query.
    Returns list of dicts with 'content', 'source', 'topic', 'dosha', 'confidence'.
    """
    model = get_model()
    query_vector = model.encode([query]).astype('float32')
    distances, indices = index.search(query_vector, top_k)
    
    retrieved_results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(knowledge_data) and idx != -1:
            dist = distances[0][i]
            # Convert FAISS L2 distance to a pseudo-confidence score (0-100%)
            # all-MiniLM outputs distances mostly between 0.0 to 1.5. 
            confidence = max(0.0, min(100.0, 100.0 - (dist * 45)))
            
            entry = knowledge_data[idx].copy()
            entry['confidence'] = round(confidence, 1)
            entry['distance'] = float(dist)
            retrieved_results.append(entry)
            
    return retrieved_results

def format_context(retrieved_results):
    """Format the retrieved results into a readable context string."""
    context = ""
    for i, res in enumerate(retrieved_results):
        context += f"[Source: {res['source']}, Topic: {res['topic']}]\n"
        context += f"{res['content']}\n\n"
    return context.strip()
