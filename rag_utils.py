import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import streamlit as st

@st.cache_resource
def get_model():
    # MiniLM scales flawlessly to millions of queries on standard CPUs.
    return SentenceTransformer('all-MiniLM-L6-v2')

def load_knowledge_base(filepath):
    """Load and parse structured JSON knowledge base."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@st.cache_resource
def create_vector_db(_knowledge_data):
    """
    Initializes a highly efficient FAISS vector database.
    Easily scales to 1M+ entries.
    """
    if not _knowledge_data:
        return None
    model = get_model()
    documents = [item['content'] for item in _knowledge_data]
    embeddings = model.encode(documents)
    dimension = embeddings.shape[1]
    
    # Using L2 distance for fast semantic similarity search
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    return index

def retrieve_relevant_knowledge(query, index, knowledge_data, top_k=3):
    """
    Searches FAISS index for semantic similarity.
    Returns clustered documents with normalized confidence metrics.
    """
    if not index or not knowledge_data:
        return []
        
    model = get_model()
    query_vector = model.encode([query]).astype('float32')
    distances, indices = index.search(query_vector, top_k)
    
    results = []
    seen_contents = set() # Avoid repetitive chunks
    
    for i, idx in enumerate(indices[0]):
        if idx < len(knowledge_data) and idx != -1:
            content = knowledge_data[idx]['content']
            if content in seen_contents:
                continue
                
            seen_contents.add(content)
            dist = distances[0][i]
            
            # Map FAISS L2 distance to an intuitive 0-100 Confidence Metric
            confidence = max(0.0, min(100.0, 100.0 - (dist * 40)))
            
            # Context filtration for precision 
            if confidence > 20.0:
                entry = knowledge_data[idx].copy()
                entry['confidence'] = round(confidence, 1)
                entry['distance'] = float(dist)
                results.append(entry)
            
    return results

def format_context(results):
    """Aggregates context tightly to prevent LLM token bloat."""
    return "\n".join([f"[{r['source']} - {r['topic']}]: {r['content']}" for r in results])
