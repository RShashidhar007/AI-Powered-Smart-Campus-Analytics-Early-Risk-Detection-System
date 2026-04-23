import os
import streamlit as st
import numpy as np
import pandas as pd
import time
from language import TEXTS
from config import DATA_PATH, CURRENT_ACADEMIC_YEAR
from database import init_db, create_faculty_user, authenticate_faculty_user

# Design system
# PAGE_CSS is now centrally managed in ui_theme.py and injected via styles.py

# Admin credentials - override via environment variables
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "teacher")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "team07pro")


def _load_student_usns():
    """Load all valid USNs from the student dataset for login validation."""
    try:
        from data_pro import run_pipeline, run_pipeline_from_db
        df = run_pipeline_from_db(CURRENT_ACADEMIC_YEAR)
        if df.empty:
            df = run_pipeline(DATA_PATH)
        return set(df['usn'].astype(str).str.strip().str.upper())
    except Exception:
        return set()


def render_login_page():

    # Ensure database is initialised
    init_db()
    
    # Get current language texts
    T = TEXTS[st.session_state.language]
    
    # ===================== Login Header & Language Selector =====================
    # Align the language change button side by side to the title to save vertical space
    header_col1, header_col2 = st.columns([8, 2])
    
    with header_col1:
        st.markdown(f"""
        <div class="login-box" style="margin-top: 0; margin-bottom: 0px; padding: 15px 30px;">
            <div class="login-title" style="text-align:left; font-size: 32px;">{T["title_text"]}</div>
            <div class="login-subtitle" style="text-align:left; margin-bottom:0px;">{T["login_subtitle"]}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with header_col2:
        st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
        def _on_login_lang_change():
            st.session_state.language = st.session_state.language_topright

        st.selectbox(
            "Language", 
            ["English", "हिन्दी", "ಕನ್ನಡ"], 
            key="language_topright", 
            label_visibility="collapsed",
            index=["English", "हिन्दी", "ಕನ್ನಡ"].index(st.session_state.language),
            on_change=_on_login_lang_change,
        )

    # ===================== Role Selection Tabs =====================
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        role_tab1, role_tab2 = st.tabs([
            T.get('faculty_tab', 'Faculty Login'),
            T.get('student_tab', 'Student Login')
        ])

        # ==================== FACULTY LOGIN ====================
        with role_tab1:
            st.markdown(f"""
            <div style="text-align:center; margin-top: 10px; margin-bottom: 10px; color: var(--text-muted); font-size: 14px; font-weight: 600;">{T["login_portal_text"]}</div>
            """, unsafe_allow_html=True)

            # Tab-based login mode selection
            tab1, tab2, tab3 = st.tabs(["Username/Password", "OTP", "Register"])

            with tab1:
                with st.form("login_form_user_pass"):
                    username = st.text_input("Username", placeholder=T["username_placeholder"], key="username")
                    password = st.text_input("Password", placeholder=T["password_placeholder"], type="password", key="password")
                    remember = st.checkbox(T["remember_text"])
                    submit_user_pass = st.form_submit_button(T["login_button_text"])
                    if submit_user_pass:
                        # Check admin explicitly, then fall back to database
                        is_admin = (username == ADMIN_USERNAME and password == ADMIN_PASSWORD)
                        is_valid_user = authenticate_faculty_user(username, password)
                        
                        if is_admin or is_valid_user:
                            st.session_state.authenticated = True
                            st.session_state.user_role = "teacher"
                            st.session_state.student_usn = None
                            st.success(T["login_success"])
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(T["invalid_credentials"])

            with tab2:
                with st.form("login_form_otp"):
                    email = st.text_input(T["email_placeholder"], key="otp_email")
                    if st.form_submit_button(T["send_otp_text"]):
                        st.session_state.generated_otp = np.random.randint(100000, 999999)
                        st.success(T["otp_success"].format(otp=st.session_state.generated_otp))
                    otp_input = st.text_input("Enter OTP", key="otp_input")
                    submit_otp = st.form_submit_button(T["verify_otp_text"])
                    if submit_otp:
                        if str(otp_input) == str(st.session_state.get("generated_otp", "")):
                            st.session_state.authenticated = True
                            st.session_state.user_role = "teacher"
                            st.session_state.student_usn = None
                            st.success(T["otp_verified"])
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(T["invalid_otp"])

            with tab3:
                st.markdown("### Create New Account")
                with st.form("registration_form"):
                    new_username = st.text_input("Choose Username", placeholder="Enter desired username", key="reg_username")
                    new_email = st.text_input("Email Address", placeholder="Enter your email", key="reg_email")
                    new_password = st.text_input("Create Password", type="password", placeholder="At least 8 characters", key="reg_password")
                    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="reg_confirm")
                    department = st.selectbox("Department", ["Academic Affairs", "Administration", "IT Support", "Finance", "Other"], key="reg_department")
                    
                    # Password strength indicator for registration
                    if new_password:
                        password_strength = "Weak"
                        strength_color = ""
                        if len(new_password) >= 8:
                            if any(c.isupper() for c in new_password) and any(c.isdigit() for c in new_password):
                                password_strength = "Strong"
                                strength_color = ""
                            else:
                                password_strength = "Medium"
                                strength_color = ""
                        st.caption(f"Password Strength: {strength_color} {password_strength}")
                    
                    submit_register = st.form_submit_button("Register Account", use_container_width=True)
                    if submit_register:
                        if not new_username or not new_email or not new_password:
                            st.error("All fields are required.")
                        elif len(new_password) < 8:
                            st.error("Password must be at least 8 characters long.")
                        elif new_password != confirm_password:
                            st.error("Passwords do not match.")
                        elif "@" not in new_email:
                            st.error("Please enter a valid email address.")
                        else:
                            # Register new user to the database
                            success = create_faculty_user(new_username, new_email, new_password, department)
                            if success:
                                st.success("Account created successfully!")
                                st.info(f"Your username: **{new_username}**\n\nYou can now log in using your username and password in the 'Username/Password' tab.")
                            else:
                                st.error("Username already exists. Please choose another.")

            # Forgot Password link under the tabs
            st.markdown(f"<a href='#' style='color:var(--text-muted); font-size:14px; display:block; text-align:center; margin-top:10px;'>{T['forgot_password_text']}</a>", unsafe_allow_html=True)

        # ==================== STUDENT LOGIN ====================
        with role_tab2:
            st.markdown(f"""
            <div style="text-align:center; margin-top: 10px; margin-bottom: 10px; color: var(--text-muted); font-size: 14px; font-weight: 600;">
                {T.get("student_portal_text", "Student Portal")}
            </div>
            """, unsafe_allow_html=True)

            # Student login description
            st.markdown("""
            <div style="text-align:center; margin-bottom: 20px;">
                <div style="color: var(--text-muted); font-size: 14px; font-family: 'Inter', sans-serif;">
                    Log in with your USN to view your marks, attendance &amp; results
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("student_login_form"):
                student_usn = st.text_input(
                    "USN",
                    placeholder=T.get("student_usn_placeholder", "Enter your USN (e.g. 1RV21CSE1001)"),
                    key="student_usn_input",
                )
                student_password = st.text_input(
                    "Password",
                    placeholder=T.get("student_password_placeholder", "Enter your password (default: your USN)"),
                    type="password",
                    key="student_password_input",
                )
                st.caption("Default password is your USN")

                submit_student = st.form_submit_button(
                    T.get("login_button_text", "Login"),
                    use_container_width=True,
                    type="primary",
                )
                if submit_student:
                    usn_clean = student_usn.strip().upper()
                    if not usn_clean:
                        st.error("Please enter your USN.")
                    else:
                        valid_usns = _load_student_usns()
                        if usn_clean not in valid_usns:
                            st.error(T.get("student_usn_not_found", "No student found with this USN"))
                        elif student_password.strip().upper() != usn_clean:
                            st.error(T.get("student_invalid_password", "Invalid password"))
                        else:
                            st.session_state.authenticated = True
                            st.session_state.user_role = "student"
                            st.session_state.student_usn = usn_clean
                            st.success(T.get("student_login_success", "Welcome back, student!"))
                            time.sleep(1)
                            st.rerun()

    st.markdown(f"<p style='text-align:center; color:var(--text-muted); font-size:12px; margin-top:20px;'>{T['footer']}</p>", unsafe_allow_html=True)
