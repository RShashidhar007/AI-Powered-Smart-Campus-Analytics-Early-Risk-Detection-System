"""
ai_agent.py — Floating AI assistant chatbot widget.
Uses Groq API (llama3) for universal question answering.
Falls back gracefully if API key is not configured.
"""
import os
import streamlit as st
from language import TEXTS

SYSTEM_PROMPT = """You are the Smart Campus AI Assistant — a helpful, friendly, and knowledgeable 
virtual assistant embedded inside the "Smart Campus Analytics" dashboard. 

About the platform:
- It is an AI-Powered Early Risk Detection System for a university with 5 departments:
  CSE (Computer Science), ECE (Electronics), ME (Mechanical), CE (Civil), ISE (Information Science).
- Each department has 4 semesters with ~100 students each = ~2000 students total.
- It has 5 pages: Home (overview KPIs & charts), Predictions (ML models & single-student predictor), 
  Students (at-risk student list with filters), Reports (EDA — distributions, correlations, box plots, department comparison), 
  and Settings (theme & background customization).
- Users can filter by Department and Semester from the sidebar.
- Risk is calculated using attendance (<65%), internal marks (<25), semester marks (<120), 
  study hours (<2), and assignment scores (<25).
- ML models include Linear Regression, Random Forest, Gradient Boosting for regression, 
  and Logistic Regression, Decision Tree, Random Forest for classification.
- Supports English, Hindi, and Kannada languages.

Your role:
- Answer ANY question the user asks — about the platform, academics, data science, 
  programming, general knowledge, or anything else.
- Be concise but thorough. Use markdown formatting when helpful.
- EXACT STUDENT DATA: You have direct access to the complete student database (provided below in CSV format).
- If the user asks about a specific student, search the CSV data below. Provide their name, USN, department, semester, risk tier, attendance, and semester marks.
- You can also answer aggregate questions like "How many students in ECE have an F grade?" or "Which department has the highest at-risk rate?".
- Be warm, professional, and encouraging.
"""


def _get_groq_response(user_msg: str, chat_history: list) -> str:
    """Get response from Groq API."""
    import requests
    import pandas as pd
    from config import DATA_PATH
    
    # Check session state first, then environment variable
    api_key = st.session_state.get("groq_api_key", "") or os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return _get_fallback_response(user_msg)

    # Load Database Context (Severely compressed to bypass Groq 413 limit)
    try:
        from data_pro import run_pipeline
        df = run_pipeline(DATA_PATH)
        
        # Keep only the bare essentials (Name, USN, Dept, Sem, Attendance, Sem Marks, Risk)
        mini_df = df[['usn', 'name', 'department', 'semester', 'attendance', 'semester_marks', 'risk_tier']].copy()
        
        # Calculate swift aggregate statistics to provide contextual knowledge without exceeding token limits
        dept_stats = mini_df.groupby('department').agg(
            total_students=('usn', 'count'),
            avg_marks=('semester_marks', 'mean'),
            avg_att=('attendance', 'mean'),
            critical_count=('risk_tier', lambda x: (x=="Critical").sum())
        ).round(1).to_csv()
        
        # Filter for top 20 most critical students only, instead of dumping all 2000 rows
        critical_df = mini_df[mini_df['risk_tier'] == 'Critical'].head(20).copy()
        critical_df['attendance'] = critical_df['attendance'].round(0).astype(int)
        critical_df['semester_marks'] = critical_df['semester_marks'].round(0).astype(int)
        critical_df['semester'] = critical_df['semester'].astype(int)
        critical_df.columns = ['U', 'N', 'D', 'S', 'A', 'M', 'R']
        
        csv_data = critical_df.to_csv(index=False)
        db_context = f"\n\n--- AGGREGATE STATS ---\n{dept_stats}\n\n--- TOP CRITICAL STUDENTS (Limit 20) ---\n(U=USN, N=Name, D=Dept, S=Sem, A=Attendance, M=SemMarks, R=Risk)\n{csv_data}\n--- END ---\n"
    except Exception as e:
        db_context = f"\n\n(Student Database could not be loaded: {str(e)})"

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
    /* Hide the dummy streamlit button */
    [data-testid="stButton"] button p {
        font-family: 'Outfit', sans-serif;
    }
    .stButton:has(p:contains("AI_HIDDEN")) {
        display: none !important;
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

    # Sidebar toggle removed as per user request.
    import streamlit.components.v1 as components

    # Hidden Streamlit button to manage state
    if st.button("AI_HIDDEN_TOGGLE", key="ai_hidden_toggle"):
        st.session_state.ai_chat_open = not st.session_state.ai_chat_open
        st.rerun()

    components.html("""
    <script>
    const parentDoc = window.parent.document;
    
    // Hide the Streamlit button cleanly
    const buttons = parentDoc.querySelectorAll('button');
    let hiddenBtn = null;
    buttons.forEach(b => {
        if (b.innerText.includes('AI_HIDDEN_TOGGLE')) {
            hiddenBtn = b;
            const container = b.closest('.element-container');
            if (container) container.style.display = 'none';
        }
    });

    // Create persistent functional floating button
    let fab = parentDoc.getElementById('ai-floating-btn');
    if (!fab) {
        fab = parentDoc.createElement('button');
        fab.id = 'ai-floating-btn';
        fab.className = 'ai-fab';
        fab.innerHTML = '🤖';
        fab.title = 'AI Assistant';
        parentDoc.body.appendChild(fab);
    }
    
    // Proxy click to hidden streamlit button
    fab.onclick = function() {
        const isChatOpen = parentDoc.querySelector('[data-testid="stChatInput"]') !== null;
        // Only trigger click if chat is CLOSED
        if (!isChatOpen && hiddenBtn) {
            hiddenBtn.click();
        }
    };
    
    fab.ondblclick = function() {
        const isChatOpen = parentDoc.querySelector('[data-testid="stChatInput"]') !== null;
        // Only trigger click if chat is OPEN
        if (isChatOpen && hiddenBtn) {
            hiddenBtn.click();
            // Prevent text selection from double click
            parentDoc.getSelection().removeAllRanges();
        }
    };
    </script>
    """, height=0, width=0)

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

