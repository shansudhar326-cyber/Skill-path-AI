"""
Module: Settings & Multi-Agent Diagnostics
Controls Gemini API configuration, demo reset triggers, and agent architecture diagnostics.
"""

import streamlit as st
import os
from SkillPath_AI.database.db import (
    reset_student_to_demo, get_connection
)
from SkillPath_AI.utils.helpers import get_gemini_api_key, is_gemini_available, call_gemini

def render_settings_module(student_id: int):
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="font-weight: 800; color: #1e293b; margin:0;">⚙️ System Settings & AI Configuration</h2>
        <p style="color: #64748b; font-size: 14px; margin-top: 4px;">
            Configure Google Gemini API credentials, inspect the multi-agent architecture, or reset to standard demo scenarios.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_api, tab_agents, tab_db = st.tabs(["🔑 Gemini AI Configuration", "🤖 Agent Architecture Inspector", "🗄️ Database & Demo State"])

    # TAB 1: Gemini AI Key
    with tab_api:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("### Google Gemini API Integration")
        st.caption("Provide an API key to enable live LLM generation for all 5 specialized agents. If left empty, SkillPath AI runs in high-fidelity Demo Mode with deterministic rule-based heuristics.")

        current_key = get_gemini_api_key()
        has_key = is_gemini_available()

        if has_key:
            st.markdown("""
            <div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:8px; padding:12px; margin-bottom:16px;">
                <strong style="color:#065f46;">🟢 Gemini API Mode: ACTIVE</strong>
                <p style="margin:4px 0 0 0; color:#047857; font-size:13px;">
                    Google Gemini 1.5 Flash is actively powering Skill DNA insights, Code challenge evaluations, Rescue plans, and the AI Mentor.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:12px; margin-bottom:16px;">
                <strong style="color:#92400e;">🟡 Demo Mode: ACTIVE (Rule-based Heuristics)</strong>
                <p style="margin:4px 0 0 0; color:#b45309; font-size:13px;">
                    Operating in fully-functional offline Demo Mode. All agent loops, adaptive learning triggers, and calculations run reliably via built-in domain logic.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with st.form("api_key_form"):
            key_input = st.text_input(
                "Enter Gemini API Key (e.g., AIzaSy...):",
                value=current_key if current_key else "",
                type="password",
                help="Obtain a free API key at https://aistudio.google.com/"
            )
            col_k1, col_k2 = st.columns([1, 1])
            with col_k1:
                save_key = st.form_submit_button("💾 Save Key to Session", use_container_width=True)
            with col_k2:
                clear_key = st.form_submit_button("🗑️ Remove Key & Use Demo Mode", use_container_width=True)

            if save_key:
                if key_input.strip():
                    st.session_state["gemini_api_key"] = key_input.strip()
                    os.environ["GEMINI_API_KEY"] = key_input.strip()
                    st.success("API Key saved! Verifying connection...")
                    
                    # Ping test
                    res, ok = call_gemini("Reply with: 'SkillPath AI Gemini connection verified.'")
                    if ok:
                        st.balloons()
                        st.success(f"Connection Verified: {res.strip()}")
                    else:
                        st.warning("Key saved, but test call failed or was rate limited. The system will safely use rule-based fallback if API errors occur.")
                    st.rerun()

            if clear_key:
                st.session_state["gemini_api_key"] = ""
                if "GEMINI_API_KEY" in os.environ:
                    del os.environ["GEMINI_API_KEY"]
                st.info("Switched to offline Demo Mode.")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # TAB 2: Agent Architecture
    with tab_agents:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("### 5 Specialized Agent Roster")
        st.caption("Each agent executes specialized duties and synchronizes state via the Central Agent Orchestrator:")

        agent_specs = [
            ("🧬 Skill DNA Agent", "Skill Graph & Topology", "Analyzes verified skills, builds interactive NetworkX graph, computes missing target skills and adjacent learning vectors.", "Student Skills, Target Role", "Graph Nodes/Edges, Missing Skills, Velocity Advice"),
            ("🎯 Career Prediction Agent", "Market & Compatibility Forecaster", "Evaluates compatibility percentage across all 7 industry roles, calculates transition friction, and tracks emerging tech trends.", "Skills Portfolio, Career Target", "Compatibility %, Gap Counts, Strategic Advice"),
            ("💻 Challenge Agent", "Practical Code Evaluator", "Generates role-specific coding challenges and rigorously evaluates submissions on correctness, logic, security, and standards.", "Challenge Rubric, Student Code", "Score (0-100), Sub-scores, Feedback, Rescue Flag"),
            ("🚨 Learning Rescue Agent", "Adaptive Remediation Specialist", "Automatically intervenes on low scores (<60%), simplifies complex concepts with analogies, and injects remedial sprints into roadmap.", "Weak Topic, Assessment Score", "ELI5 Explanation, Curated Tutorials, Practice Tasks"),
            ("⚖️ Career Readiness Agent", "Multi-Pillar Readiness Auditor", "Synthesizes Technical Skills (35%), Challenges (30%), Projects (20%), and Problem Solving (15%) into a transparent readiness score.", "4-Pillar Performance Metrics", "Readiness Index %, Tier Classification, Audit Narrative")
        ]

        for name, role, desc, inputs, outputs in agent_specs:
            st.markdown(f"""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px; margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong style="font-size:16px; color:#1e293b;">{name}</strong>
                    <span class="badge badge-primary">{role}</span>
                </div>
                <p style="color:#475569; font-size:13px; margin:6px 0 10px 0;">{desc}</p>
                <div style="display:flex; gap:20px; font-size:12px; color:#64748b; background:#ffffff; padding:8px 12px; border-radius:6px; border:1px solid #f1f5f9;">
                    <div><strong>Inputs:</strong> {inputs}</div>
                    <div><strong>Outputs:</strong> {outputs}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # TAB 3: Database & Reset
    with tab_db:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("### 🗄️ Database State & Demonstration Reset")
        st.caption("Inspect persistent SQLite tables or restore the exact specification demo scenario.")

        conn = get_connection()
        c = conn.cursor()
        counts = {}
        for tbl in ["students", "skills", "projects", "certifications", "challenges", "challenge_submissions", "roadmap_items", "rescue_plans", "readiness_history", "mentor_chats", "agent_logs"]:
            c.execute(f"SELECT COUNT(*) FROM {tbl}")
            counts[tbl] = c.fetchone()[0]
        conn.close()

        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.markdown(f"**Students Registered:** {counts.get('students', 0)}")
            st.markdown(f"**Skills Tracked:** {counts.get('skills', 0)}")
            st.markdown(f"**Projects Logged:** {counts.get('projects', 0)}")
        with col_d2:
            st.markdown(f"**Challenges Configured:** {counts.get('challenges', 0)}")
            st.markdown(f"**Challenge Submissions:** {counts.get('challenge_submissions', 0)}")
            st.markdown(f"**Roadmap Milestones:** {counts.get('roadmap_items', 0)}")
        with col_d3:
            st.markdown(f"**Active/Resolved Rescues:** {counts.get('rescue_plans', 0)}")
            st.markdown(f"**Readiness History:** {counts.get('readiness_history', 0)}")
            st.markdown(f"**Agent Actions Logged:** {counts.get('agent_logs', 0)}")

        st.divider()
        st.markdown("#### 🔄 Reset Demo Student Scenario")
        st.markdown("""
        Restores **M. Sudharshan** to the initial baseline state from the project specification:
        - Username: **M.Sudharshan** (Password: **sudharsh390**)
        - Target Role: **Full Stack Developer**
        - Existing Skills: **Python (3/5), SQL (3/5), Basic HTML (2/5)**
        - Missing Skills to Bridge: **CSS3, JavaScript, React, Node.js, Express.js**
        - Clears active rescue plans and resets baseline readiness score.
        """)

        if st.button("⚠️ Reset to Baseline Demo State", type="secondary"):
            reset_student_to_demo(student_id)
            st.success("Successfully reset student profile to baseline specification!")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
