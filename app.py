"""
SkillPath AI - AI-Powered Career Digital Twin Platform
Main Application Entrypoint
"""

import streamlit as st
import os
import sys

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SkillPath_AI.config import APP_NAME, APP_SUBTITLE, APP_VERSION, CAREER_ROLES
from SkillPath_AI.database.db import (
    init_db, seed_demo_student, authenticate_student, create_student,
    get_student_by_id, reset_student_to_demo
)
from SkillPath_AI.modules import (
    render_dashboard_module,
    render_profile_module,
    render_skill_analysis_module,
    render_career_matching_module,
    render_simulator_module,
    render_roadmap_module,
    render_progress_module,
    render_mentor_module,
    render_settings_module
)
from SkillPath_AI.utils.helpers import is_gemini_available, get_gemini_api_key

# Page Configuration
st.set_page_config(
    page_title="SkillPath AI – Career Digital Twin",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize Database & Seed Demo User on Startup
init_db()
seed_demo_student()

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = True
    # Find M.Sudharshan ID
    demo_user = authenticate_student("M.Sudharshan", "sudharsh390")
    st.session_state["student_id"] = demo_user["id"] if demo_user else 1

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"

# --- AUTHENTICATION FLOW (If logged out) ---
if not st.session_state["authenticated"]:
    st.markdown("""
    <div style="text-align:center; padding: 40px 20px 20px 20px;">
        <div style="font-size:44px; margin-bottom:8px;">🧬</div>
        <h1 style="font-size:32px; font-weight:800; color:#1e293b; margin:0;">SkillPath AI</h1>
        <p style="color:#64748b; font-size:16px; margin-top:6px;">
            AI-Powered Career Digital Twin & Personalized Adaptive Learning
        </p>
    </div>
    """, unsafe_allow_html=True)

    auth_tab1, auth_tab2 = st.tabs(["🔐 Student Login", "📝 New Student Registration"])

    with auth_tab1:
        st.markdown('<div class="sp-card" style="max-width:480px; margin:0 auto;">', unsafe_allow_html=True)
        st.markdown("### Welcome Back")
        st.caption("Sign in to calibrate your Career Digital Twin.")

        with st.form("login_form"):
            l_user = st.text_input("Username", value="M.Sudharshan")
            l_pass = st.text_input("Password", value="sudharsh390", type="password")
            login_btn = st.form_submit_button("Sign In to Digital Twin", use_container_width=True, type="primary")

            if login_btn:
                user = authenticate_student(l_user, l_pass)
                if user:
                    st.session_state["authenticated"] = True
                    st.session_state["student_id"] = user["id"]
                    st.success(f"Welcome back, {user['full_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        st.markdown("""
        <div style="background:#f1f5f9; padding:10px; border-radius:6px; font-size:12px; color:#475569; margin-top:12px; text-align:center;">
            <strong>Demo Credentials:</strong> Username: <code>M.Sudharshan</code> • Password: <code>sudharsh390</code>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with auth_tab2:
        st.markdown('<div class="sp-card" style="max-width:520px; margin:0 auto;">', unsafe_allow_html=True)
        st.markdown("### Create Your Career Digital Twin")
        with st.form("reg_form"):
            r_user = st.text_input("Choose Username")
            r_pass = st.text_input("Choose Password", type="password")
            r_name = st.text_input("Full Name")
            r_email = st.text_input("Email Address")
            r_career = st.selectbox("Initial Target Career Goal", list(CAREER_ROLES.keys()))
            r_bio = st.text_area("Short Bio (Optional)")

            reg_btn = st.form_submit_button("Register & Initialize Twin", use_container_width=True, type="primary")
            if reg_btn:
                if r_user and r_pass and r_name and r_email:
                    new_id = create_student(r_user, r_pass, r_name, r_email, r_career, r_bio)
                    if new_id:
                        st.session_state["authenticated"] = True
                        st.session_state["student_id"] = new_id
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error("Username or email already exists.")
                else:
                    st.error("Please fill in all required fields.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# --- AUTHENTICATED USER SESSION ---
student_id = st.session_state["student_id"]
student = get_student_by_id(student_id)

if not student:
    st.session_state["authenticated"] = False
    st.rerun()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; padding:10px 0 16px 0; border-bottom:1px solid #f1f5f9;">
        <span style="font-size:28px;">🧬</span>
        <div>
            <div style="font-weight:800; font-size:18px; color:#1e293b; line-height:1.2;">SkillPath AI</div>
            <div style="font-size:11px; color:#6366f1; font-weight:600;">CAREER DIGITAL TWIN</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Active Student Pill
    st.markdown(f"""
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:10px 12px; margin: 12px 0;">
        <div style="font-size:13px; font-weight:700; color:#0f172a;">{student['full_name']}</div>
        <div style="font-size:11px; color:#64748b;">🎯 {student['target_career']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation menu
    nav_options = [
        ("Dashboard", "📊"),
        ("My Profile", "👤"),
        ("Skill DNA", "🧬"),
        ("Career Matching", "🎯"),
        ("AI Career Simulator", "💻"),
        ("Learning Roadmap", "🗺️"),
        ("Progress Tracking", "📈"),
        ("AI Mentor", "🤖"),
        ("Settings", "⚙️")
    ]

    selected_nav = st.radio(
        "Navigation",
        [item[0] for item in nav_options],
        format_func=lambda x: f"{dict(nav_options)[x]}  {x}",
        index=[item[0] for item in nav_options].index(st.session_state["current_page"]) if st.session_state["current_page"] in [item[0] for item in nav_options] else 0,
        label_visibility="collapsed"
    )
    st.session_state["current_page"] = selected_nav

    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)

    # AI Engine Status Pill
    if is_gemini_available():
        st.markdown("""
        <div style="background:#ecfdf5; border-radius:8px; padding:8px 12px; border:1px solid #a7f3d0; margin-bottom:12px;">
            <div style="display:flex; align-items:center; gap:6px;">
                <span style="color:#059669; font-size:14px;">●</span>
                <strong style="color:#065f46; font-size:11px;">Gemini 1.5 Flash Active</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#fffbeb; border-radius:8px; padding:8px 12px; border:1px solid #fde68a; margin-bottom:12px;">
            <div style="display:flex; align-items:center; gap:6px;">
                <span style="color:#d97706; font-size:14px;">●</span>
                <strong style="color:#92400e; font-size:11px;">Demo Mode (Heuristics)</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Quick Logout & Reset
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["student_id"] = None
            st.rerun()
    with col_s2:
        if st.button("🔄 Reset", use_container_width=True, help="Reset to demo state"):
            reset_student_to_demo(student_id)
            st.rerun()

    st.caption(f"SkillPath AI v{APP_VERSION} • Multi-Agent System")

# --- MAIN VIEW ROUTING ---
page = st.session_state["current_page"]

if page == "Dashboard":
    render_dashboard_module(student_id)
elif page == "My Profile":
    render_profile_module(student_id)
elif page == "Skill DNA":
    render_skill_analysis_module(student_id)
elif page == "Career Matching":
    render_career_matching_module(student_id)
elif page == "AI Career Simulator":
    render_simulator_module(student_id)
elif page == "Learning Roadmap":
    render_roadmap_module(student_id)
elif page == "Progress Tracking":
    render_progress_module(student_id)
elif page == "AI Mentor":
    render_mentor_module(student_id)
elif page == "Settings":
    render_settings_module(student_id)
