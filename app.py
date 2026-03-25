import streamlit as st
import uuid
from openai import OpenAI
from rag_utils import load_knowledge_base, create_vector_db, retrieve_relevant_knowledge, format_context
from utils import detect_dosha, calculate_wellness_score

# --- PAGE CONFIG ---
st.set_page_config(page_title="Sattva-Prana AI", page_icon="🌿", layout="wide")

# --- INITIALIZE PIPELINE ---
@st.cache_resource
def initialize_rag():
    data = load_knowledge_base("knowledge.json")
    idx = create_vector_db(data)
    return idx, data

index, knowledge_data = initialize_rag()

# --- CSS STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .block-container { padding-top: 2rem; max-width: 1000px; }
    [data-testid="stSidebar"] { background-color: #161821; border-right: 1px solid #2d2f3a; }
    
    .metric-box { background-color: #1e212b; border: 1px solid #333645; border-radius: 8px; padding: 15px; text-align: center; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .metric-title { font-size: 0.8rem; color: #9ca3af; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
    .metric-val { font-size: 1.6rem; font-weight: 700; margin: 5px 0; }
    
    .stChatMessage { padding: 1.2rem; background: transparent; }
    .stChatMessage[data-testid="chat-message-assistant"] { background-color: #1e212b; border-radius: 8px; border: 1px solid #333645; }
    
    .badge { padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; margin-right: 5px; display: inline-block;}
    .bg-topic { background-color: #3b82f6; color: white; }
    .bg-dosha { background-color: #8b5cf6; color: white; }
    .bg-conf { background-color: #4b5563; color: white; }
    
    .source-block { background-color: #161821; padding: 12px; border-left: 3px solid #10b981; border-radius: 4px; margin-bottom: 8px; font-size: 0.9em; }
</style>
""", unsafe_allow_html=True)

# --- LOCAL GENERATION HELPER ---
def generate_answer(results):
    """
    Combines retrieved vectors into a clean, concise pseudo-reasoning response.
    """
    if not results:
        return "I don't have enough specific information in my classical database to answer that. Could you provide a bit more detail about your symptoms?"
        
    best = results[0]
    
    insight = f"Based on the **{best['source']}**, these generalized symptoms are closely tied to the **{best['dosha']}** dosha."
    explanation = best['content']
    
    tips = []
    for r in results:
        sentences = r['content'].replace("!", ".").split(".")
        for s in sentences:
            s = s.strip()
            if len(s) > 10 and any(kw in s.lower() for kw in ["avoid", "include", "use", "should", "recommend", "consume", "practice", "drink", "eat", "apply"]):
                if s not in tips:
                    tips.append(s)
                    
    if not tips:
        tips = [s.strip() for s in best['content'].split('.') if len(s.strip()) > 10]

    md = f"**🌿 Ayurvedic Insight**\n{insight}\n\n"
    md += f"**📖 Explanation**\n{explanation}\n\n"
    md += "**✅ Practical Tips**\n"
    for tip in tips[:3]: 
        clean_tip = tip.capitalize().strip()
        if not clean_tip.endswith('.'): clean_tip += '.'
        md += f"- {clean_tip}\n"
        
    return md

# --- SESSION MGMT ---
if "chats" not in st.session_state:
    chat_id = str(uuid.uuid4())
    st.session_state.chats = {chat_id: {"name": "New Session", "messages": []}}
    st.session_state.current_chat = chat_id
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

active_chat = st.session_state.chats[st.session_state.current_chat]

# --- SIDEBAR ---
with st.sidebar:
    st.title("🌿 Sattva-Prana AI")
    if st.button("➕ New Consultation", use_container_width=True, type="primary"):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"name": "New Session", "messages": []}
        st.session_state.current_chat = new_id
        st.rerun()
        
    st.markdown("<hr style='border-color: #333645; margin: 10px 0;'>", unsafe_allow_html=True)
    st.caption("HISTORY")
    for c_id, chat_data in reversed(list(st.session_state.chats.items())):
        if st.button(f"💬 {chat_data['name']}", key=c_id, use_container_width=True):
            st.session_state.current_chat = c_id
            st.rerun()
            
    st.markdown("<div style='flex-grow:1'></div><hr style='border-color: #333645; margin: 10px 0;'>", unsafe_allow_html=True)
    
    st.session_state.api_key = st.text_input("OpenAI Key (For AI Synthesis)", type="password", value=st.session_state.api_key)
    mode = "🧠 AI Mode" if st.session_state.api_key else "⚡ RAG Mode"
    st.caption(f"Status: **{mode}**")

# --- DASHBOARD UI ---
st.markdown("### 🧬 Wellness Insights")

# Disclaimer
st.warning("⚠️ **Disclaimer:** For educational purposes only. Not a medical diagnosis.")

all_user_text = " ".join([m["content"] for m in active_chat["messages"] if m["role"] == "user"])

if all_user_text:
    percentages, dominant, match_count = detect_dosha(all_user_text)
    score = calculate_wellness_score(match_count)
    
    latest_confidence = "N/A"
    latest_topic = "General Inquiry"
    if len(active_chat["messages"]) > 1 and active_chat["messages"][-1]["role"] == "assistant":
        if "meta_topic" in active_chat["messages"][-1]:
            latest_topic = active_chat["messages"][-1]["meta_topic"]
            latest_confidence = f"{active_chat['messages'][-1]['meta_conf']}%"
            
    col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1])
    with col1:
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Dominant Dosha</div><div class='metric-val' style='color:#3b82f6;'>{dominant}</div><span class='badge bg-dosha'>V:{percentages['Vata']}% | P:{percentages['Pitta']}% | K:{percentages['Kapha']}%</span></div>", unsafe_allow_html=True)
    with col2:
        c_color = "#10b981" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Wellness Score</div><div class='metric-val' style='color:{c_color};'>{score}%</div><progress value='{score}' max='100' style='width:100%'></progress></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Primary Concern</div><div class='metric-val' style='color:#a78bfa; font-size:1.2rem; margin-top:15px;'>{latest_topic}</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-box'><div class='metric-title'>Response Confidence</div><div class='metric-val' style='color:#10b981; font-size:1.6rem; margin-top:10px;'>{latest_confidence}</div></div>", unsafe_allow_html=True)
else:
    st.info("👋 Welcome! Describe your symptoms to populate your personalized wellness insights.")
    st.markdown("**Suggested Queries:**")
    c1, c2, c3 = st.columns(3)
    if c1.button("I'm feeling anxious and my hair is thinning. What dosha is this?", use_container_width=True):
        st.session_state.sugg_prompt = "I've been feeling very anxious recently, and my hair is thinning quickly. What dosha is imbalanced?"
        st.rerun()
    if c2.button("I have acid reflux and feel irritable. Any cooling tips?", use_container_width=True):
        st.session_state.sugg_prompt = "I am struggling with acid reflux after lunch and feeling easily irritable. Do you have any cooling tips?"
        st.rerun()
    if c3.button("I struggle to wake up and feel heavy. How to balance Kapha?", use_container_width=True):
        st.session_state.sugg_prompt = "I sleep heavily, struggle to wake up, and feel sluggish all day. How do I balance this Kapha?"
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- CHAT RENDERING ---
for msg in active_chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("🔍 View Retrieved Sources"):
                for src in msg["sources"]:
                    st.markdown(f"<div class='source-block'><span class='badge bg-topic'>{src['source']}</span><span class='badge bg-conf'>{src['confidence']}% Match</span><br><br>{src['content']}</div>", unsafe_allow_html=True)

# --- CHAT INPUT RAG INFERENCE ---
default_p = st.session_state.pop("sugg_prompt", "")
prompt = st.chat_input("Enter your symptoms or query...")

if prompt or default_p:
    p = prompt if prompt else default_p
    if len(active_chat["messages"]) == 0:
        active_chat["name"] = p[:25] + "..."
        
    active_chat["messages"].append({"role": "user", "content": p})
    st.rerun() 

if len(active_chat["messages"]) > 0 and active_chat["messages"][-1]["role"] == "user":
    current_prompt = active_chat["messages"][-1]["content"]
    
    with st.spinner("Analyzing semantics against Knowledge Base..."):
        results = retrieve_relevant_knowledge(current_prompt, index, knowledge_data, top_k=4)
        
        context_html = ""
        avg_conf = 0.0
        if results:
            avg_conf = round(sum(r['confidence'] for r in results)/len(results))
            for res in results:
                context_html += f"""
                <div style='background-color:#1a1b23; padding:12px; border-radius:6px; margin-bottom:8px; border-left:3px solid #10b981;'>
                    <div style='margin-bottom: 6px;'>
                        <span class='badge bg-topic'>{res['topic']}</span>
                        <span class='badge bg-dosha'>{res['dosha']}</span>
                        <span class='badge bg-conf'>{res['confidence']}%</span>
                    </div>
                    <p style='margin-top:5px; font-size:0.9em; line-height:1.4;'>"{res['content']}"</p>
                    <small style='color:#8e8ea0;'><i>Source: {res['source']}</i></small>
                </div>
                """
                
    with st.chat_message("assistant"):
        api_key = st.session_state.api_key
        top_topic = results[0]['topic'] if results else "General"
        
        if not api_key:
            # ⚡ RAG LOCAL SYNTHESIS
            resp = generate_answer(results)
            st.markdown(resp)
            if context_html:
                with st.expander("🔍 View Retrieved Sources"):
                    st.markdown(context_html, unsafe_allow_html=True)
            active_chat["messages"].append({"role": "assistant", "content": resp, "sources": results, "meta_topic": top_topic, "meta_conf": avg_conf})
            st.rerun()
            
        else:
            # 🧠 OPENAI GENERATIVE MODE
            context_text = format_context(results) if results else "No specific Ayurvedic context found."
            system_prompt = (
                "You are Sattva-Prana AI, a highly professional clinical Ayurvedic Assistant. "
                "Synthesize the provided context into a concise, readable reasoning response. "
                "You MUST use ONLY the provided context. If the context fails to answer, state that gently.\n\n"
                "FORMAT EXACTLY AS:\n"
                "**🌿 Ayurvedic Insight**\n[1 sentence summarizing the core principle relating to the query]\n\n"
                "**📖 Explanation**\n[1-2 short sentences synthesizing the retrieved texts locally]\n\n"
                "**✅ Practical Tips**\n[Max 3 bullet points of practical action items derived entirely from context.]"
            )
            
            try:
                client = OpenAI(api_key=api_key)
                placeholder = st.empty()
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Context:\n{context_text}\n\nQuery:\n{current_prompt}"}
                    ],
                    stream=True
                )
                
                full_resp = ""
                for chunk in stream:
                    if getattr(chunk.choices[0], 'delta', None) and getattr(chunk.choices[0].delta, 'content', None):
                        full_resp += chunk.choices[0].delta.content
                        placeholder.markdown(full_resp + "▌")
                placeholder.markdown(full_resp)
                
                if context_html:
                    with st.expander("🔍 View Retrieved Sources"):
                        st.markdown(context_html, unsafe_allow_html=True)
                        
                active_chat["messages"].append({"role": "assistant", "content": full_resp, "sources": results, "meta_topic": top_topic, "meta_conf": avg_conf})
                st.rerun()
                
            except Exception as e:
                st.error(f"API Error: {str(e)}")
                active_chat["messages"].append({"role": "assistant", "content": f"Error: {str(e)}", "sources": [], "meta_topic": "Error", "meta_conf": 0})

st.markdown("<p style='text-align: center; color: #6b7280; font-size: 0.8rem; margin-top: 60px;'>Powered by RAG (Retrieval-Augmented Generation)</p>", unsafe_allow_html=True)
