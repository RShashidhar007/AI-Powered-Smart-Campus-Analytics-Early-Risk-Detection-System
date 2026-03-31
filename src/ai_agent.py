"""
ai_agent.py — Floating AI assistant chatbot widget.
Uses Groq API (llama3) for universal question answering.
Falls back gracefully if API key is not configured.
"""
import streamlit as st
from language import TEXTS

SYSTEM_PROMPT = """You are the Smart Campus AI Assistant — a helpful, friendly, and knowledgeable 
virtual assistant embedded inside the "Smart Campus Analytics" dashboard. 

About the platform:
- It is an AI-Powered Early Risk Detection System for a CS Department with 500 students.
- It has 5 pages: Home (overview KPIs & charts), Predictions (ML models & single-student predictor), 
  Students (at-risk student list with filters), Reports (EDA — distributions, correlations, box plots), 
  and Settings (theme & background customization).
- Risk is calculated using attendance (<65%), internal marks (<25), semester marks (<120), 
  study hours (<2), and assignment scores (<25).
- ML models include Linear Regression, Random Forest, Gradient Boosting for regression, 
  and Logistic Regression, Decision Tree, Random Forest for classification.
- Supports English, Hindi (हिन्दी), and Kannada (ಕನ್ನಡ) languages.

Your role:
- Answer ANY question the user asks — about the platform, academics, data science, 
  programming, general knowledge, or anything else.
- Be concise but thorough. Use markdown formatting when helpful.
- EXACT STUDENT DATA: You have direct access to the complete student database (provided below in CSV format).
- If the user asks about a specific student, search the CSV data below. Provide their name, USN, risk tier, attendance, and semester marks.
- You can also answer aggregate questions like "How many students have an F grade?" or "Who has the highest attendance?".
- Be warm, professional, and encouraging.
"""


def _get_groq_response(user_msg: str, chat_history: list) -> str:
    """Get response from Groq API."""
    import requests
    import pandas as pd
    from config import DATA_PATH
    
    # We enforce the api key string here so it works even without visiting settings
    api_key = st.session_state.get("groq_api_key", "")
    if not api_key:
        api_key = "add your Groq API key in settings to enable AI assistant"#add your api key

    # Load Database Context (Severely compressed to bypass Groq 413 limit)
    try:
        from data_pro import run_pipeline
        df = run_pipeline(DATA_PATH)
        
        # Keep only the bare essentials (Name, USN, Attendance, Sem Marks, Risk)
        mini_df = df[['usn', 'name', 'attendance', 'semester_marks', 'risk_tier']].copy()
        
        # Round and convert numeric columns to save string space
        mini_df['attendance'] = mini_df['attendance'].round(0).astype(int)
        mini_df['semester_marks'] = mini_df['semester_marks'].round(0).astype(int)
        
        # Rename columns to single/short characters to massively shrink CSV token size
        mini_df.columns = ['U', 'N', 'A', 'M', 'R']
        
        csv_data = mini_df.to_csv(index=False)
        db_context = f"\n\n--- DATABASE ---\n(U=USN, N=Name, A=Attendance, M=SemMarks, R=Risk)\n{csv_data}\n--- END ---\n"
    except Exception:
        db_context = "\n\n(Student Database could not be loaded at this time.)"

    # Build conversation history for context
    system_prompt_with_data = SYSTEM_PROMPT + db_context
    history = [{"role": "system", "content": system_prompt_with_data}]
    for msg in chat_history[-10:]:  # Last 10 messages for context
        history.append({"role": msg["role"], "content": msg["content"]})

    history.append({"role": "user", "content": user_msg})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": history
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

def _get_fallback_response(user_msg: str) -> str:
    """Comprehensive fallback when Groq API is not available."""
    return ("⚠️ **AI API not configured.** To enable universal answers:\n\n"
            "1. Go to **Settings** page\n"
            "2. Enter your **Groq API key**\n"
            "   (Get one at [console.groq.com](https://console.groq.com))\n\n"
            "Once configured, I can answer any question!")


def render_ai_agent():
    """Render the floating AI agent button and chat panel."""

    # Initialise chat history
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []
    if "ai_chat_open" not in st.session_state:
        st.session_state.ai_chat_open = False
    if "groq_api_key" not in st.session_state:
        st.session_state.groq_api_key = ""

    # CSS for the floating button
    st.markdown("""
    <style>
    .ai-fab {
        position: fixed;
        bottom: 28px;
        right: 28px;
        z-index: 99999;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #5b5ef4 0%, #8b5cf6 100%);
        color: white;
        border: none;
        font-size: 28px;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(91, 94, 244, 0.45);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .ai-fab:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 28px rgba(91, 94, 244, 0.6);
    }
    .ai-fab-pulse {
        position: fixed;
        bottom: 28px;
        right: 28px;
        z-index: 99998;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: rgba(91, 94, 244, 0.3);
        animation: ai-pulse 2s ease-in-out infinite;
    }
    @keyframes ai-pulse {
        0%, 100% { transform: scale(1); opacity: 0.4; }
        50% { transform: scale(1.4); opacity: 0; }
    }
    </style>
    """, unsafe_allow_html=True)

    # Floating pulse ring
    st.markdown('<div class="ai-fab-pulse"></div>', unsafe_allow_html=True)

    # Sidebar toggle
    with st.sidebar:
        st.markdown("---")
        ai_open = st.toggle("🤖 AI Assistant", value=st.session_state.ai_chat_open,
                            key="ai_toggle")
        st.session_state.ai_chat_open = ai_open

    if st.session_state.ai_chat_open:
        st.markdown("---")
        st.markdown(
            "<div style='display:flex;align-items:center;gap:8px;margin-bottom:8px'>"
            "<span style='font-size:22px'>🤖</span>"
            "<span style='font-size:16px;font-weight:600;color:var(--main-text-color,#333)'>"
            "AI Campus Assistant</span>"
            "<span style='font-size:11px;color:var(--muted-color,#888);margin-left:auto'>"
            "Powered by Groq</span></div>",
            unsafe_allow_html=True,
        )

        # Chat history display
        chat_container = st.container(height=300)
        with chat_container:
            if not st.session_state.ai_chat_history:
                st.markdown(
                    "<div style='text-align:center;color:var(--muted-color,#888);"
                    "padding:40px 0;font-size:13px'>"
                    "👋 Hi! I'm your AI Campus Assistant.<br>"
                    "I can answer <b>any question</b> — about students, predictions,<br>"
                    "academics, programming, or anything else!"
                    "</div>",
                    unsafe_allow_html=True,
                )
            for msg in st.session_state.ai_chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Chat input
        user_input = st.chat_input("Ask me anything...", key="ai_chat_input")
        if user_input:
            st.session_state.ai_chat_history.append({"role": "user", "content": user_input})

            # Try Groq first, fall back if not configured
            response = _get_groq_response(user_input, st.session_state.ai_chat_history)
            if response is None:
                response = _get_fallback_response(user_input)

            st.session_state.ai_chat_history.append({"role": "assistant", "content": response})
            st.rerun()

    # Always show the visual floating button
    st.markdown(
        '<div class="ai-fab" title="AI Assistant">🤖</div>',
        unsafe_allow_html=True,
    )
