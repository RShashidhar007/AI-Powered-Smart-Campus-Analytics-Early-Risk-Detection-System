"""
student_ai_agent.py - Floating AI chatbot for the Student Portal.

Privacy-sandboxed: the LLM only receives the logged-in student's own
academic data and is instructed to refuse any request for other students',
departments', or campus-wide information.
"""
import os
import streamlit as st
import pandas as pd
from language import TEXTS

# ── System prompt (strict privacy boundary) ──────────────────────────

STUDENT_SYSTEM_PROMPT = """\
You are **CampusInsight Personal Advisor** — a friendly, encouraging AI tutor
embedded inside the student portal of the CampusInsight analytics platform.

## Your Identity
- You are a *personal academic advisor* for **one specific student** only.
- You have access to ONLY this student's data (provided below).
- You do NOT have access to any other student's data, any other department's
  data, or any campus-wide / aggregate statistics.

## Strict Privacy Rules  (NEVER violate these)
1. If the user asks about **another student** (by name, USN, or description),
   politely decline: "I can only help with your own academic data."
2. If the user asks for **department-wide, semester-wide, or campus-wide**
   statistics, rankings, or comparisons with other students, politely decline.
3. If the user asks "how many students…", "list all students…", "who has the
   highest/lowest…", or similar aggregate queries, decline.
4. NEVER fabricate data about other students.  NEVER reveal data you were
   not given.

## What You CAN Do
- Answer questions about this student's marks, attendance, risk tier, grade,
  predictions, and performance index.
- Provide **actionable, specific improvement tips** based on their data.
  For example: "Your attendance is 58 %, which is below the 65 % at-risk
  threshold. Attending at least 3 more classes per week could raise it above
  75 % and significantly lower your risk score."
- Explain what risk scores, grades, and performance indices mean.
- Answer general academic questions (study tips, exam strategies, etc.).
- Be warm, motivational, and supportive.

## How Risk Is Calculated (for context)
- attendance < 65 % → +30 risk points
- internal_marks < 25  → +25 risk points
- semester_marks < 120 → +25 risk points
- study_hours < 2      → +10 risk points
- assignment_score < 25 → +10 risk points
Risk tiers: Low (0-20), Moderate (21-45), High (46-70), Critical (71-100).

## Grade Thresholds (semester_marks out of 200)
A: 165-200 | B: 150-165 | C: 135-150 | D: 120-135 | F: < 120

Use markdown formatting. Be concise but thorough.
"""


# ── Data helpers ─────────────────────────────────────────────────────

def _build_student_context(usn: str) -> str:
    """Return a text block with ONLY this student's data for the LLM."""
    from config import CURRENT_ACADEMIC_YEAR
    from data_pro import run_pipeline_from_db
    from ml_models import train_regression_models, train_classification_models

    year = st.session_state.get('selected_academic_year', CURRENT_ACADEMIC_YEAR)
    df = run_pipeline_from_db(year)
    student_df = df[df['usn'] == usn]

    if student_df.empty:
        return "\n\n[Student data not found for this USN.]\n"

    s = student_df.iloc[0]

    # Peer percentile (only the number, no peer names)
    percentile = 0
    if 'performance_index' in df.columns and len(df) > 0:
        percentile = int(round(
            (df['performance_index'] <= s['performance_index']).mean() * 100
        ))

    # Predictions (try to compute if not already present)
    pred_marks = s.get('predicted_marks', None)
    pred_grade = s.get('predicted_grade', None)
    if pd.isna(pred_marks) or pd.isna(pred_grade):
        try:
            FEATURES = ['attendance', 'internal_marks', 'assignment_score',
                         'quiz_score', 'lab_marks', 'study_hours']
            reg = train_regression_models(df)
            clf = train_classification_models(df)

            row = student_df[FEATURES]
            best_reg = reg['trained_models'][reg['best_model']]
            is_lin = reg['best_model'] == 'Linear Regression'
            X_in = reg['scaler'].transform(row) if is_lin else row
            pred_marks = float(best_reg.predict(X_in)[0])

            best_clf = clf['trained_models'][clf['best_model']]
            is_log = clf['best_model'] == 'Logistic Regression'
            X_clf = clf['scaler'].transform(row) if is_log else row
            pred_grade = clf['label_encoder'].inverse_transform(
                best_clf.predict(X_clf)
            )[0]
        except Exception:
            pred_marks = pred_marks if not pd.isna(pred_marks) else "N/A"
            pred_grade = pred_grade if not pd.isna(pred_grade) else "N/A"

    context = f"""
--- STUDENT PROFILE (this is the ONLY student you know about) ---
Name:             {s['name']}
USN:              {s['usn']}
Department:       {s['department']}
Semester:         {int(s['semester'])}
Academic Year:    {year}

Attendance:       {s['attendance']:.1f} %
Internal Marks:   {s['internal_marks']:.1f} / 50
Assignment Score: {s['assignment_score']:.1f} / 50
Quiz Score:       {s['quiz_score']:.1f} / 50
Lab Marks:        {s['lab_marks']:.1f} / 50
Semester Marks:   {s['semester_marks']:.1f} / 200
Study Hours/Day:  {s['study_hours']:.1f}

Current Grade:    {s['grade_label']}
Risk Score:       {int(s['risk_score'])} / 100
Risk Tier:        {s['risk_tier']}
At-Risk Flag:     {"Yes" if s['is_at_risk'] else "No"}
Performance Index:{s['performance_index']:.1f} / 100
Percentile:       {percentile}th (among all students)

Predicted Semester Marks: {pred_marks if isinstance(pred_marks, str) else f"{pred_marks:.1f}"}
Predicted Grade:          {pred_grade}
--- END OF STUDENT DATA ---
"""
    return context


# ── Groq API call (sandboxed) ────────────────────────────────────────

def _get_student_groq_response(user_msg: str, chat_history: list,
                                student_context: str) -> str:
    """Call Groq with the privacy-enforced student prompt."""
    import requests

    session_key = st.session_state.get("groq_api_key", "")
    env_key = os.environ.get("GROQ_API_KEY", "")
    api_key = (session_key.strip() if session_key and session_key.strip()
               else env_key.strip())
    if not api_key:
        return _student_fallback()

    system_prompt = STUDENT_SYSTEM_PROMPT + student_context
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_msg})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
    }

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=payload,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f" API Error: {str(e)}"


def _student_fallback() -> str:
    return (" **AI API not configured.** To enable your personal advisor:\n\n"
            "1. Ask your faculty to set the **Groq API key** in Settings\n"
            "   (Get one free at [console.groq.com](https://console.groq.com))\n\n"
            "Once configured, I can answer questions about your academics!")


# ── Floating UI widget ───────────────────────────────────────────────

def render_student_ai_agent():
    """Render the floating AI chatbot button + panel for the student portal."""

    # Session state (separate keys from the teacher agent)
    if "student_ai_chat_history" not in st.session_state:
        st.session_state.student_ai_chat_history = []
    if "student_ai_chat_open" not in st.session_state:
        st.session_state.student_ai_chat_open = False

    # ── CSS for the floating action button ──
    st.markdown("""
    <style>
    .ai-fab-student {
        position: fixed;
        bottom: 28px;
        right: 28px;
        z-index: 99999;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        font-size: 28px;
        cursor: pointer;
        box-shadow: 0 4px 24px rgba(99,102,241,0.45);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .ai-fab-student:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 32px rgba(99,102,241,0.65);
    }
    .ai-fab-student-pulse {
        position: fixed;
        bottom: 28px;
        right: 28px;
        z-index: 99998;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: rgba(99,102,241,0.3);
        animation: student-pulse 2s ease-in-out infinite;
    }
    @keyframes student-pulse {
        0%, 100% { transform: scale(1); opacity: 0.4; }
        50% { transform: scale(1.4); opacity: 0; }
    }
    </style>
    """, unsafe_allow_html=True)

    # Pulse ring
    st.markdown('<div class="ai-fab-student-pulse"></div>', unsafe_allow_html=True)

    # Hidden Streamlit button to toggle chat (same pattern as teacher agent)
    import streamlit.components.v1 as components

    if st.button("STUDENT_AI_HIDDEN_TOGGLE", key="student_ai_hidden_toggle"):
        st.session_state.student_ai_chat_open = not st.session_state.student_ai_chat_open
        st.rerun()

    components.html("""
    <script>
    const parentDoc = window.parent.document;

    // Hide the Streamlit toggle button
    const buttons = parentDoc.querySelectorAll('button');
    let hiddenBtn = null;
    buttons.forEach(b => {
        if (b.innerText.includes('STUDENT_AI_HIDDEN_TOGGLE')) {
            hiddenBtn = b;
            const container = b.closest('.element-container');
            if (container) container.style.display = 'none';
        }
    });

    // Create floating button
    let fab = parentDoc.getElementById('student-ai-floating-btn');
    if (!fab) {
        fab = parentDoc.createElement('button');
        fab.id = 'student-ai-floating-btn';
        fab.className = 'ai-fab-student';
        fab.innerHTML = '💬';
        fab.title = 'Personal Academic Advisor';
        parentDoc.body.appendChild(fab);
    }

    // Click → open, Double-click → close
    fab.onclick = function() {
        const isChatOpen = parentDoc.querySelector('[data-testid="stChatInput"]') !== null;
        if (!isChatOpen && hiddenBtn) hiddenBtn.click();
    };
    fab.ondblclick = function() {
        const isChatOpen = parentDoc.querySelector('[data-testid="stChatInput"]') !== null;
        if (isChatOpen && hiddenBtn) {
            hiddenBtn.click();
            parentDoc.getSelection().removeAllRanges();
        }
    };
    </script>
    """, height=0, width=0)

    # ── Chat panel ──
    if st.session_state.student_ai_chat_open:
        st.markdown("---")
        st.markdown(
            "<div style='display:flex;align-items:center;gap:10px;margin-bottom:8px'>"
            "<span style='font-size:22px'></span>"
            "<span style='font-size:16px;font-weight:700;color:var(--text-primary)'>"
            "Personal Academic Advisor</span>"
            "<span style='font-size:11px;color:var(--text-muted);margin-left:auto'>"
            "Only your data · Powered by Groq</span></div>",
            unsafe_allow_html=True,
        )

        chat_container = st.container(height=320)
        with chat_container:
            if not st.session_state.student_ai_chat_history:
                st.markdown(
                    "<div style='text-align:center;color:var(--text-muted);"
                    "padding:40px 0;font-size:13px'>"
                    " Hi! I'm your <b>Personal Academic Advisor</b>.<br>"
                    "I can only see <b>your</b> data — no one else's.<br><br>"
                    "Ask me about your marks, attendance, risk status,<br>"
                    "or how to improve your grades!"
                    "</div>",
                    unsafe_allow_html=True,
                )
            for msg in st.session_state.student_ai_chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_input = st.chat_input(
            "Ask about your academics...",
            key="student_ai_chat_input",
        )
        if user_input:
            st.session_state.student_ai_chat_history.append(
                {"role": "user", "content": user_input}
            )

            # Build student context on each request (cheap — single row)
            usn = st.session_state.get("student_usn")
            if usn:
                ctx = _build_student_context(usn)
                response = _get_student_groq_response(
                    user_input,
                    st.session_state.student_ai_chat_history,
                    ctx,
                )
            else:
                response = " I couldn't identify your student session. Please log out and log back in."

            st.session_state.student_ai_chat_history.append(
                {"role": "assistant", "content": response}
            )
            st.rerun()
