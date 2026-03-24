import streamlit as st
import uuid
from openai import OpenAI
from rag_utils import load_knowledge_base, create_vector_db, retrieve_relevant_knowledge, format_context

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Sattva-Prana RAG AI", page_icon="🌿", layout="wide")

# --- INITIALIZATION ---
@st.cache_resource
def initialize_rag_system():
    knowledge_data = load_knowledge_base("knowledge.json")
    index, data = create_vector_db(knowledge_data)
    return index, data

try:
    index, knowledge_data = initialize_rag_system()
except Exception as e:
    st.error(f"Error loading RAG system. Details: {e}")
    st.stop()

# --- CSS STYLING (ChatGPT-like) ---
st.markdown("""
<style>
    /* Global Styles */
    .stApp { background-color: #343541; color: #ececf1; }
    
    /* Layout Overrides */
    .block-container { padding-top: 2rem; max-width: 900px; }
    
    /* Login Page */
    .login-box {
        background-color: #202123;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        margin-top: 10vh;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #202123;
        border-right: 1px solid #4d4d4f;
    }
    .new-chat-btn button {
        width: 100%;
        background-color: transparent !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
        text-align: left !important;
        padding: 10px 15px !important;
        justify-content: flex-start !important;
    }
    .new-chat-btn button:hover {
        background-color: #2A2B32 !important;
    }
    
    /* Chat bubbles */
    .stChatMessage { padding: 1.5rem; background-color: transparent; }
    .stChatMessage[data-testid="chat-message-assistant"] { background-color: #444654; }
    
    /* Custom Sources */
    .source-box {
        background-color: #2d2f3a; 
        padding: 12px; 
        border-radius: 8px; 
        margin-bottom: 8px; 
        font-size: 0.9em; 
        border-left: 4px solid #10a37f;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "chats" not in st.session_state:
    # Dictionary storing chats: { "chat_id": {"name": "Chat Name", "messages": []} }
    chat_id = str(uuid.uuid4())
    st.session_state.chats = {chat_id: {"name": "New Chat", "messages": []}}
    st.session_state.current_chat = chat_id
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""

# --- LOGIN SYSTEM ---
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: white;'>🌿 Sattva-Prana AI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8e8ea0; margin-bottom: 30px;'>Log in to your account</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_id = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="admin")
            submitted = st.form_submit_button("Continue", use_container_width=True)
            
            if submitted:
                # Mock Database Check
                if user_id == "admin" and password == "admin":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials. Use 'admin' as both Username and Password.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR (ChatGPT Style) ---
with st.sidebar:
    st.markdown("<div class='new-chat-btn'>", unsafe_allow_html=True)
    if st.button("➕ New Chat"):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"name": "New Chat", "messages": []}
        st.session_state.current_chat = new_id
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<br><p style='font-size: 0.8em; color: #8e8ea0; margin-bottom: 10px; padding-left: 5px;'>Chat History</p>", unsafe_allow_html=True)
    
    # List chats
    for c_id, chat_data in reversed(list(st.session_state.chats.items())):
        is_active = (c_id == st.session_state.current_chat)
        btn_label = f"💬 {chat_data['name']}"
        if st.button(btn_label, key=f"btn_{c_id}", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.current_chat = c_id
            st.rerun()
            
    st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True) # Spacer
    st.markdown("---")
    
    # Bottom Settings & Profile
    with st.expander("⚙️ Settings & Profile"):
        st.markdown("**👤 Logged in as:** `admin`")
        st.markdown("---")
        st.markdown("**🧠 OpenAI Configuration:**")
        st.session_state.openai_api_key = st.text_input("API Key (Optional)", type="password", value=st.session_state.openai_api_key, help="Add your key to enable AI conversational mode. Leave blank for local mode.")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

# --- MAIN CHAT AREA ---
# Make sure current_chat exists
if st.session_state.current_chat not in st.session_state.chats:
    st.session_state.current_chat = list(st.session_state.chats.keys())[0]
active_chat = st.session_state.chats[st.session_state.current_chat]

# Welcome Screen (Only if no messages)
if len(active_chat["messages"]) == 0:
    st.markdown("<br><br><br><h1 style='text-align: center;'>🌿 Sattva-Prana RAG AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8e8ea0; font-size: 1.1em;'>How can I help you with ancient Ayurvedic knowledge today?</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# Display Messages
for idx, msg in enumerate(active_chat["messages"]):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("context_html"):
            with st.expander("📚 View Retrieved Sources"):
                st.markdown(msg["context_html"], unsafe_allow_html=True)

# Chat Input
if prompt := st.chat_input("Message Sattva-Prana..."):
    
    # Rename chat if it's the first message
    if len(active_chat["messages"]) == 0:
        st.session_state.chats[st.session_state.current_chat]["name"] = prompt[:20] + ("..." if len(prompt) > 20 else "")
    
    # Append User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    active_chat["messages"].append({"role": "user", "content": prompt, "context_html": ""})
        
    # Retrieval Phase
    with st.spinner("Searching ancient texts..."):
        results = retrieve_relevant_knowledge(prompt, index, knowledge_data, top_k=3)
    
        # Construct Context HTML block for Expanders
        context_html = ""
        if results:
            for res in results:
                context_html += f"""
                <div class='source-box'>
                    <b style='color: #10a37f;'>{res['source']}</b> <i>({res['topic']} - {res['dosha']})</i><br>
                    {res['content']}
                </div>
                """
                
    # Generation Phase
    with st.chat_message("assistant"):
        api_key = st.session_state.openai_api_key
        
        if not api_key:
            # LOCAL MODE
            if results:
                best = results[0]
                local_resp = f"**According to the {best['source']}:**\n\n{best['content']}\n\n"
                if len(results) > 1:
                    local_resp += "\n*Additional Insights:* " + " | ".join([f"*{r['content']}*" for r in results[1:]])
            else:
                local_resp = "I couldn't find relevant texts in my database for this query."
            
            st.markdown(local_resp)
            if context_html:
                with st.expander("📚 View Retrieved Sources"):
                    st.markdown(context_html, unsafe_allow_html=True)
            
            # Save Assistant Message
            active_chat["messages"].append({"role": "assistant", "content": local_resp, "context_html": context_html})
            
        else:
            # OPENAI MODE
            context_text = format_context(results) if results else "No specific Ayurvedic context found."
            system_prompt = (
                "You are Sattva-Prana RAG AI, an expert Ayurvedic Assistant. "
                "You must answer the user's question USING ONLY the provided context retrieved from "
                "authentic Ayurvedic texts. "
                "Start your response with 'According to Ayurveda...' or reference the specific text if provided. "
                "If the context does not contain the answer, politely say you don't have that information in your current knowledge base. "
                "Do NOT invent medical advice."
            )
            user_prompt = f"Context:\n{context_text}\n\nUser Question: {prompt}"
            
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
                    # new openai streaming syntax delta check
                    if getattr(chunk.choices[0], 'delta', None) and getattr(chunk.choices[0].delta, 'content', None):
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
                if context_html:
                    with st.expander("📚 View Retrieved Sources"):
                        st.markdown(context_html, unsafe_allow_html=True)
                
                active_chat["messages"].append({"role": "assistant", "content": full_response, "context_html": context_html})
                
            except Exception as e:
                err_msg = f"❌ OpenAI API Error: {str(e)}"
                st.error(err_msg)
                active_chat["messages"].append({"role": "assistant", "content": err_msg, "context_html": ""})
