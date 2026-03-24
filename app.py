import streamlit as st
import uuid
import pandas as pd
from openai import OpenAI
from rag_utils import load_knowledge_base, create_vector_db, retrieve_relevant_knowledge, format_context
from utils import detect_dosha, calculate_wellness_score

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Sattva-Prana AI Enterprise", page_icon="🌿", layout="wide")

# --- INITIALIZATION ---
@st.cache_resource
def initialize_rag_system():
    knowledge_data = load_knowledge_base("knowledge.json")
    index = create_vector_db(knowledge_data)
    return index, knowledge_data

try:
    index, knowledge_data = initialize_rag_system()
except Exception as e:
    st.error(f"Error loading RAG system. Details: {e}")
    st.stop()

# --- CSS STYLING (Premium SaaS) ---
st.markdown("""
<style>
    /* Global Styles */
    .stApp { background-color: #0c0d11; color: #ececf1; }
    
    /* Layout Overrides */
    .block-container { padding-top: 2rem; max-width: 1200px; }
    
    /* Login Page */
    .login-box { background-color: #1a1b23; padding: 40px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin-top: 10vh; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #13141b; border-right: 1px solid #2d2f3a; }
    
    /* Cards and Containers */
    .dashboard-card { background-color: #1a1b23; padding: 20px; border-radius: 12px; border: 1px solid #2d2f3a; margin-bottom: 20px; text-align: center; }
    .dashboard-value { font-size: 2rem; font-weight: bold; color: #10a37f; }
    .dashboard-label { font-size: 0.9rem; color: #8e8ea0; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Chat bubbles */
    .stChatMessage { padding: 1.5rem; background-color: transparent; }
    .stChatMessage[data-testid="chat-message-assistant"] { background-color: #1a1b23; border-radius: 8px; border: 1px solid #2d2f3a; }
    
    /* Badges */
    .badge-confidence { background-color: #10a37f; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75em; }
    .badge-topic { background-color: #3b82f6; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75em; }
    .badge-dosha { background-color: #8b5cf6; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75em; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "chats" not in st.session_state:
    chat_id = str(uuid.uuid4())
    st.session_state.chats = {chat_id: {"name": "New Consultation", "messages": [], "dosha": None, "score": None, "percentages": None}}
    st.session_state.current_chat = chat_id
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""

# --- LOGIN SYSTEM ---
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: white;'>🌿 Sattva-Prana Enterprise</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8e8ea0; margin-bottom: 30px;'>Log in to your clinical workspace</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_id = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="admin")
            if st.form_submit_button("Authenticate into Workspace", use_container_width=True):
                if user_id == "admin" and password == "admin":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials (Use admin / admin).")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR (History & Settings) ---
with st.sidebar:
    st.markdown("### 🌿 Sattva-Prana Pro")
    if st.button("➕ New Patient Consultation", use_container_width=True, type="primary"):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"name": "New Consultation", "messages": [], "dosha": None, "score": None, "percentages": None}
        st.session_state.current_chat = new_id
        st.rerun()
        
    st.markdown("<hr style='border-top: 1px solid #2d2f3a;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.8em; color: #8e8ea0; margin-bottom: 10px;'>SESSION HISTORY</p>", unsafe_allow_html=True)
    
    for c_id, chat_data in reversed(list(st.session_state.chats.items())):
        is_active = (c_id == st.session_state.current_chat)
        if st.button(f"💬 {chat_data['name']}", key=f"btn_{c_id}", use_container_width=True, type="secondary"):
            st.session_state.current_chat = c_id
            st.rerun()
            
    st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True) 
    st.markdown("---")
    
    with st.expander("⚙️ System Configuration"):
        st.markdown("**Core Engine:** RAG (FAISS + MiniLM)")
        st.session_state.openai_api_key = st.text_input("OpenAI API Key (Optional)", type="password", value=st.session_state.openai_api_key, help="Enable OpenAI to synthesize structured generative responses.")
        st.caption("Status: " + ("🟢 GPT Synthesis Active" if st.session_state.openai_api_key else "🟡 Local Extractive Mode Only"))
        if st.button("🚪 Secure Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

# --- MAIN WORKSPACE ---
if st.session_state.current_chat not in st.session_state.chats:
    st.session_state.current_chat = list(st.session_state.chats.keys())[0]

active_chat = st.session_state.chats[st.session_state.current_chat]

# Top Dashboard (Wellness & Dosha)
if active_chat["messages"]:
    # Process dosha based on combined chat history inputs
    all_user_text = " ".join([m["content"] for m in active_chat["messages"] if m["role"] == "user"])
    dosha_percentages, dominant_dosha, match_count = detect_dosha(all_user_text)
    wellness_score = calculate_wellness_score(match_count)
    
    st.markdown("### 📊 Live Wellness Analytics")
    d_col1, d_col2, d_col3, d_col4 = st.columns(4)
    with d_col1:
        st.markdown(f"<div class='dashboard-card'><div class='dashboard-label'>Dominant Dosha</div><div class='dashboard-value'>{dominant_dosha}</div></div>", unsafe_allow_html=True)
    with d_col2:
        color = "#10a37f" if wellness_score > 70 else "#f59e0b" if wellness_score > 40 else "#ef4444"
        st.markdown(f"<div class='dashboard-card'><div class='dashboard-label'>Wellness Index</div><div class='dashboard-value' style='color:{color};'>{wellness_score}%</div></div>", unsafe_allow_html=True)
    with d_col3:
        st.markdown(f"<div class='dashboard-card'><div class='dashboard-label'>Symptoms Detected</div><div class='dashboard-value'>{match_count}</div></div>", unsafe_allow_html=True)
    with d_col4:
        st.markdown(f"<div class='dashboard-card'><div class='dashboard-label'>AI Modality</div><div class='dashboard-value' style='font-size:1.2rem; margin-top:10px;'>{'OpenAI Fusion' if st.session_state.openai_api_key else 'Local Extractive'}</div></div>", unsafe_allow_html=True)
else:
    st.markdown("<br><h1 style='text-align: center;'>🌿 Sattva-Prana Enterprise</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8e8ea0; font-size: 1.1em;'>Describe your symptoms below to generate clinical insights and dosha analytics.</p>", unsafe_allow_html=True)
    
    # Suggested Prompt Buttons
    st.markdown("<br>", unsafe_allow_html=True)
    colA, colB, colC = st.columns(3)
    if colA.button("Describe Hair Thinning & Stress", use_container_width=True):
        st.session_state.suggested_prompt = "My hair is thinning rapidly and I feel very stressed and anxious lately. What is my dosha imbalance?"
        st.rerun()
    if colB.button("Describe Acid Reflux & Anger", use_container_width=True):
        st.session_state.suggested_prompt = "I have terrible acid reflux after meals and I've been feeling quick to anger and hot."
        st.rerun()
    if colC.button("Describe Lethargy & Weight Gain", use_container_width=True):
        st.session_state.suggested_prompt = "I sleep heavily, feel sluggish all day, and have gained weight despite eating less."
        st.rerun()

st.markdown("---")

# Display Chat Messages
for msg in active_chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("context_html"):
            with st.expander("📚 View Embedded Sources & Metadata"):
                st.markdown(msg["context_html"], unsafe_allow_html=True)

# Chat Input Processing
default_prompt = ""
if "suggested_prompt" in st.session_state:
    default_prompt = st.session_state.suggested_prompt
    del st.session_state.suggested_prompt

prompt = st.chat_input("Enter clinical symptoms or Ayurvedic queries...")

if default_prompt or prompt:
    active_prompt = default_prompt if default_prompt else prompt
    
    if len(active_chat["messages"]) == 0:
        active_chat["name"] = active_prompt[:25] + "..."
    
    active_chat["messages"].append({"role": "user", "content": active_prompt, "context_html": ""})
    st.rerun()

# RAG & LLM Execution Trigger (only if last message is from user)
if len(active_chat["messages"]) > 0 and active_chat["messages"][-1]["role"] == "user":
    current_prompt = active_chat["messages"][-1]["content"]
    
    with st.spinner("Analyzing semantics against Brihatrayi Texts..."):
        results = retrieve_relevant_knowledge(current_prompt, index, knowledge_data, top_k=3)
        
        context_html = ""
        if results:
            for res in results:
                context_html += f"""
                <div style='background-color:#1a1b23; padding:15px; border-radius:8px; margin-bottom:10px; border-left:4px solid #10a37f;'>
                    <div style='margin-bottom: 8px;'>
                        <span class='badge-topic'>{res['topic']}</span>
                        <span class='badge-dosha'>{res['dosha']}</span>
                        <span class='badge-confidence'>Confidence: {res['confidence']}%</span>
                    </div>
                    <p style='margin-top:5px; font-size:0.95em;'>"{res['content']}"</p>
                    <small style='color:#8e8ea0;'><i>Source: {res['source']}</i></small>
                </div>
                """
                
    with st.chat_message("assistant"):
        api_key = st.session_state.openai_api_key
        
        if not api_key:
            if results:
                best = results[0]
                resp = "### 🌿 Core Ayurvedic Insight\n"
                resp += f"Based on local retrieval from the **{best['source']}**:\n\n> {best['content']}\n\n"
                
                if len(results) > 1:
                    resp += "### 📌 Supplementary Context\n"
                    for r in results[1:]:
                        resp += f"- **{r['topic']} ({r['dosha']} imbalance):** {r['content']} *(Source: {r['source']})*\n"
            else:
                resp = "No statistically significant correlations found in the local knowledge base."
            
            st.markdown(resp)
            if context_html:
                with st.expander("📚 View Embedded Sources & Metadata"):
                    st.markdown(context_html, unsafe_allow_html=True)
            active_chat["messages"].append({"role": "assistant", "content": resp, "context_html": context_html})
            st.rerun()
            
        else:
            context_text = format_context(results) if results else "No specific Ayurvedic context found."
            system_prompt = (
                "You are Sattva-Prana AI, a premium clinical Ayurvedic Assistant. "
                "Synthesize the provided context into a structured, highly professional response. "
                "FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS using Markdown:\n\n"
                "### 🌿 Clinical Insight\n[Your brief analysis based on context]\n\n"
                "### 📖 Textual Explanation\n[Detailed expansion citing the provided sources natively]\n\n"
                "### ✅ Actionable Protocols\n[Bullet points of remedies/lifestyle changes based ONLY on context]"
                "\n\nIf the context is empty or irrelevant, state that you cannot provide an authenticated answer."
            )
            user_prompt = f"Context:\n{context_text}\n\nUser Query: {current_prompt}"
            
            try:
                client = OpenAI(api_key=api_key)
                message_placeholder = st.empty()
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    stream=True,
                )
                
                full_response = ""
                for chunk in stream:
                    if getattr(chunk.choices[0], 'delta', None) and getattr(chunk.choices[0].delta, 'content', None):
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
                if context_html:
                    with st.expander("📚 View Embedded Sources & Metadata"):
                        st.markdown(context_html, unsafe_allow_html=True)
                
                active_chat["messages"].append({"role": "assistant", "content": full_response, "context_html": context_html})
                st.rerun()
                
            except Exception as e:
                err_msg = f"❌ AI Synthesis Error: {str(e)}"
                st.error(err_msg)
                active_chat["messages"].append({"role": "assistant", "content": err_msg, "context_html": ""})
                st.rerun()

st.markdown("<br><br><p style='text-align: center; color: #8e8ea0; font-size: 0.8em;'>Powered by Advanced FAISS-based RAG Engine | ⚠️ Provided for educational purposes only. Not validated medical advice.</p>", unsafe_allow_html=True)
