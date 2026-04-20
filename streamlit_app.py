import streamlit as st
import os
import json
import re
import sqlite3
import pandas as pd
from datetime import datetime
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# --- CONFIGURATION & ENV ---
load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))
HF_API_KEY = os.getenv("HF_API_KEY")
DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "emails.db")

# Ensure the backend directory exists for the DB
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI Email Generator | Premium",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (Aesthetics) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #050505;
        color: #e0e0e0;
    }
    
    /* Center the title */
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff 0%, #666666 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-title {
        text-align: center;
        color: #888888;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }

    /* Glassmorphism Containers */
    div.stButton > button {
        background-color: #ffffff;
        color: #000000;
        border-radius: 12px;
        font-weight: 700;
        padding: 0.75rem 2rem;
        border: none;
        transition: all 0.3s ease;
        width: 100%;
        font-size: 1.1rem;
    }
    
    div.stButton > button:hover {
        background-color: #cccccc;
        transform: scale(1.02);
        box-shadow: 0 10px 20px rgba(255,255,255,0.1);
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    
    /* Custom input styling */
    .stSelectbox, .stTextArea, .stTextInput {
        background-color: #111111 !important;
        border-radius: 12px !important;
    }
    
    /* Result Box */
    .result-subject {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        border-left: 4px solid #ffffff;
        padding-left: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .result-body {
        font-family: 'Inter', sans-serif;
        line-height: 1.7;
        color: #cccccc;
        white-space: pre-wrap;
        background: #111111;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #222222;
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #0a0a0a !important;
    }
    
    .history-item {
        background: #111111;
        border: 1px solid #222222;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .history-item:hover {
        background: #1a1a1a;
        border-color: #444444;
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE LOGIC ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purpose TEXT,
            tone TEXT,
            audience TEXT,
            points TEXT,
            subject TEXT,
            email_body TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(purpose, tone, audience, points, subject, email_body):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO history (purpose, tone, audience, points, subject, email_body)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (purpose, tone, audience, points, subject, email_body))
    conn.commit()
    conn.close()

def get_history():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM history ORDER BY id DESC LIMIT 20", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# --- AI GENERATION LOGIC ---
def generate_email(purpose, tone, audience, points):
    if not HF_API_KEY:
        return None, "Error: Hugging Face API key missing. Please add HF_API_KEY to your .env file."

    client = InferenceClient(api_key=HF_API_KEY)
    
    # Models to try (fallback strategy)
    models = [
        "Qwen/Qwen2.5-72B-Instruct",
        "meta-llama/Llama-3.1-8B-Instruct",
        "microsoft/Phi-3.5-mini-instruct",
    ]

    prompt = (
        f"Write a professional email.\n"
        f"Purpose: {purpose}\n"
        f"Tone: {tone}\n"
        f"Audience: {audience}\n"
        f"Key Points: {points}\n\n"
        f"Return ONLY a JSON object with two keys: 'subject' and 'email'. "
        f"No extra text, no markdown, just the JSON."
    )

    for model_id in models:
        try:
            messages = [{"role": "user", "content": prompt}]
            response = client.chat_completion(
                model=model_id,
                messages=messages,
                max_tokens=800,
                temperature=0.4
            )
            content = response.choices[0].message.content.strip()
            
            # Parse JSON
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group(0))
                return data, None
            
            # Fallback if not JSON
            subject = "Generated Email"
            body = content
            if "Subject:" in content:
                parts = content.split("Subject:", 1)[1].split("\n", 1)
                subject = parts[0].strip()
                body = parts[1].strip() if len(parts) > 1 else content
            
            return {"subject": subject, "email": body}, None
                
        except Exception as e:
            continue
            
    return None, "All AI models are currently busy or reached quota. Please try again in 1 minute."

# --- INITIALIZATION ---
init_db()

# --- SIDEBAR (History) ---
with st.sidebar:
    st.markdown("### 🕒 Generation History")
    history_df = get_history()
    
    if history_df.empty:
        st.info("No history yet. Generate your first email!")
    else:
        for index, row in history_df.iterrows():
            with st.expander(f"✉️ {row['subject'][:30]}..."):
                st.write(f"**To:** {row['audience']}")
                st.write(f"**Tone:** {row['tone']}")
                st.caption(f"Created: {row['created_at']}")
                if st.button(f"Load #{row['id']}", key=f"btn_{row['id']}"):
                    st.session_state.purpose = row['purpose']
                    st.session_state.tone = row['tone']
                    st.session_state.audience = row['audience']
                    st.session_state.points = row['points']
                    st.session_state.result = {"subject": row['subject'], "email": row['email_body']}
                    st.rerun()

# --- MAIN UI ---
st.markdown("<h1 class='main-title'>AI Email Generator</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Craft high-converting emails with Llama 3 & Qwen Intelligence</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🛠️ Configuration")
    
    purpose_options = ["Sales Outreach", "Networking", "Follow-up Meeting", "Job Application", "Thank You Note", "Announcement"]
    purpose = st.selectbox("Purpose", options=purpose_options, key="purpose")
    
    tone_col, audience_col = st.columns(2)
    with tone_col:
        tone = st.selectbox("Tone", options=["Professional", "Friendly", "Bold", "Formal", "Urgent"], key="tone")
    with audience_col:
        audience = st.text_input("Target Audience", placeholder="e.g. Hiring Manager", key="audience")
    
    points = st.text_area("Key Highlights / Context", placeholder="What are the must-include points?", height=150, key="points")
    
    if st.button("🚀 Generate Email Blueprint"):
        if not audience or not points:
            st.warning("Please provide both audience and key highlights.")
        else:
            with st.spinner("✨ Crafting your masterpiece..."):
                result, error = generate_email(purpose, tone, audience, points)
                if error:
                    st.error(error)
                else:
                    st.session_state.result = result
                    save_to_db(purpose, tone, audience, points, result['subject'], result['email'])
                    st.success("Generation complete!")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    if "result" in st.session_state and st.session_state.result:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📄 Generated Result")
        
        st.markdown(f"<div class='result-subject'>{st.session_state.result['subject']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-body'>{st.session_state.result['email']}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📋 Copy to Clipboard"):
            # Note: Hard to do real clipboard copy in Streamlit without custom components, 
            # so we'll just show a text area for easy copy.
            st.code(f"Subject: {st.session_state.result['subject']}\n\n{st.session_state.result['email']}")
            st.toast("Text ready for copying below!", icon="✅")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='glass-card' style='height: 500px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; color: #555;'>", unsafe_allow_html=True)
        st.write("### Ready for generation")
        st.write("Fill in the configuration on the left and click the button to see the magic happen.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: #555;'>Built with Streamlit & Dual AI Pipeline (Llama 3 + Qwen)</p>", unsafe_allow_html=True)
