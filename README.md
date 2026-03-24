# 🌿 Sattva-Prana RAG AI - Ayurvedic Knowledge Assistant

Sattva-Prana RAG AI is an advanced GenAI application utilizing Retrieval-Augmented Generation (RAG) to provide highly accurate, context-aware answers to Ayurvedic queries. By embedding authentic knowledge from ancient texts (like the Charaka Samhita) using Sentence Transformers and searching via FAISS, the system operates as a domain-expert AI chatbot with zero hallucinations.

## 🚀 Core Features
- **📚 RAG Knowledge Base:** Structured JSON database storing authentic Ayurvedic principles.
- **🧠 Vector Search Engine:** Converts domain knowledge into high-dimensional embeddings using `sentence-transformers` and performs sub-millisecond similarity searches using Facebook AI Similarity Search (`FAISS`).
- **💬 ChatGPT-Like UI:** A sleek, dark-themed Streamlit interface featuring stateful session chat history.
- **🔍 Context Dashboard:** A dedicated side-panel visualizing exactly which database chunks the AI retrieved to build its answer, ensuring complete transparency.
- **🤖 Contextual Text Generation:** OpenAI GPT models synthesize the retrieved vectors into seamless, natural language responses.

## 📁 Project Structure
```text
Sattva-Prana RAG AI/
├── app.py             # Main Streamlit application with Chat UI
├── rag_utils.py       # Embedding generation and FAISS retrieval logic
├── knowledge.json     # The unstructured/structured knowledge base
├── requirements.txt   # Python dependencies
└── README.md          # Documentation
```

## ⚙️ Step-by-Step Setup
1. **Navigate to Project Directory:**
   ```bash
   cd "Sattva-Prana Pro-AI-Powered Ayurvedic Wellness Assistant"
   ```
2. **Setup Virtual Environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run Application:**
   ```bash
   streamlit run app.py
   ```
5. **Configure AI:** Input your OpenAI API Key into the sidebar settings inside the web app.

## 🧠 What is RAG? (Retrieval-Augmented Generation)
Standard LLMs (like ChatGPT) might hallucinate or answer generally. RAG solves this by giving the AI an "open book" test. 
1. **Retrieval**: When you ask "What is a Vata diet?", the system searches our local database (`knowledge.json`) for paragraphs mathematically closest to your question.
2. **Augmentation**: It grabs those paragraphs and attaches them invisibly to your prompt.
3. **Generation**: It tells the AI: "Answer the user's question using ONLY these specific paragraphs." Result: Highly accurate, source-backed answers!
