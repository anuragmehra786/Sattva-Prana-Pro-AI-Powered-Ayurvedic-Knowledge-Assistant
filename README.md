# 🌿 Sattva-Prana Enterprise - RAG Integrated Clinical Platform

Sattva-Prana Enterprise is a top-tier SaaS AI system combining ancient Ayurvedic principles from the Brihatrayi (Charaka, Sushruta, Ashtanga Hridaya) with cutting-edge Machine Learning. 

It seamlessly melds a rule-based NLP dosha-analytics dashboard with a stateful FAISS Retrieval-Augmented Generation (RAG) chatbot, encapsulated inside a premium ChatGPT-styled UI.

## 🚀 Core Platform Features
- **📊 Real-time Dosha Analytics Dashboard:** Dynamically measures symptomatic keywords to produce live Vata/Pitta/Kapha variance and a generalized "Wellness Index".
- **🧠 Semantic RAG Engine:** Uses `sentence-transformers` nested over `FAISS` to execute hyper-fast similarity searches over Ayurvedic literature. Calculates mathematical Pseudo-Confidence intervals for transparency.
- **💬 ChatGPT Workspace UI:** Multi-threaded session history, secure login wall (`admin`/`admin` gateway), responsive dark mode styling, and persistent context caching.
- **⚕️ Hybrid Modality AI:** Functions flawlessly in a 100% offline Extractive Mode pulling direct citations, but can dynamically switch into an OpenAI Generative mode to synthesize the texts into actionable protocols.

## 📁 Repository Architecture
```text
Sattva-Prana-Enterprise/
├── app.py             # Advanced UI, Auth, and Dashboard logic
├── rag_utils.py       # FAISS Vector Search and MiniLM Embeddings
├── utils.py           # NLP Dosha detection and wellness scoring
├── data.py            # Static NLP word banks
├── knowledge.json     # Authentic Database from the Brihatrayi
├── requirements.txt   # Dependencies
└── README.md          # Documentation
```

## ⚙️ Deployment Instructions
1. Install dependencies: `pip install -r requirements.txt`
2. Run the platform server: `streamlit run app.py`
3. Access the clinical workspace at `localhost:8502`.
4. **Login:** Use `admin` for both Username and Password.
