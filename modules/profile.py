"""
Module: Student Profile & Career Digital Twin Identity
Manages personal information, existing technical/soft skills, proficiencies, certifications, and projects.
"""

import streamlit as st
from datetime import datetime
from config import CAREER_ROLES, SKILL_TAXONOMY
from database.db import (
    get_student_by_id, get_student_skills, add_or_update_skill, delete_skill,
    get_projects, add_project, delete_project,
    get_certifications, add_certification, update_student_profile
)
from agents.orchestrator import AgentOrchestrator

def render_profile_module(student_id: int):
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="font-weight: 800; color: #1e293b; margin:0;">👤 Student Profile & Career Digital Twin</h2>
        <p style="color: #64748b; font-size: 14px; margin-top: 4px;">
            Configure your technical foundation, verified credentials, and portfolio projects to calibrate your AI Career Twin.
        </p>
    </div>
    """, unsafe_allow_html=True)

    student = get_student_by_id(student_id)
    if not student:
        st.error("Student profile not found.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Identity & Target Career", "⚡ Skills Portfolio", "💼 Portfolio Projects", "📜 Certifications"])

    # TAB 1: Identity & Target Career
    with tab1:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("### Personal & Career Direction")
        
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name", value=student["full_name"])
                email = st.text_input("Email Address", value=student["email"], disabled=True)
            with col2:
                career_options = list(CAREER_ROLES.keys())
                curr_idx = career_options.index(student["target_career"]) if student["target_career"] in career_options else 0
                target_career = st.selectbox("🎯 Target Career Goal", career_options, index=curr_idx)
                username = st.text_input("Username", value=student["username"], disabled=True)

            bio = st.text_area("Professional Summary / Bio", value=student.get("bio", ""), height=100)

            submitted = st.form_submit_button("💾 Save Profile Changes", use_container_width=True)
            if submitted:
                old_career = student["target_career"]
                update_student_profile(student_id, full_name, bio, target_career)
                st.success("✅ Profile successfully updated!")
                
                # If career changed, notify orchestrator to adapt roadmap and skills
                if old_career != target_career:
                    with st.spinner(f"Re-calibrating Career Digital Twin for {target_career}..."):
                        orchestrator = AgentOrchestrator()
                        orchestrator.on_career_goal_changed(student_id, target_career)
                    st.info(f"🔄 Career goal changed to **{target_career}**. The AI Agents recalculated your Skill DNA and generated a new customized learning roadmap!")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # TAB 2: Skills Portfolio
    with tab2:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("### Existing Technical & Soft Skills")
        st.caption("Skills configured here directly feed the Skill DNA and Career Readiness Agents.")

        skills = get_student_skills(student_id)
        if skills:
            cols = st.columns(3)
            for idx, s in enumerate(skills):
                with cols[idx % 3]:
                    stars = "★" * s["proficiency_level"] + "☆" * (5 - s["proficiency_level"])
                    badge_cls = "badge-success" if s["proficiency_level"] >= 3 else "badge-warning"
                    st.markdown(f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong style="color:#0f172a; font-size:15px;">{s['skill_name']}</strong>
                            <span class="badge {badge_cls}">Level {s['proficiency_level']}/5</span>
                        </div>
                        <div style="color:#6366f1; font-size:13px; margin: 4px 0;">{stars}</div>
                        <div style="font-size:11px; color:#64748b;">Category: {s['category']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🗑️ Remove", key=f"del_skill_{s['id']}"):
                        delete_skill(s['id'], student_id)
                        st.rerun()
        else:
            st.info("No skills configured yet. Add your first skill below!")

        st.divider()
        st.markdown("#### ➕ Add or Update a Skill")
        with st.form("add_skill_form"):
            col_a, col_b, col_c = st.columns([2, 2, 1])
            with col_a:
                skill_name_input = st.text_input("Skill Name (e.g., Python, JavaScript, SQL, React)")
            with col_b:
                cat_options = list(SKILL_TAXONOMY.keys())
                skill_category = st.selectbox("Taxonomy Category", cat_options)
            with col_c:
                proficiency = st.slider("Proficiency", 1, 5, 3)

            add_btn = st.form_submit_button("Add Skill to Digital Twin", use_container_width=True)
            if add_btn and skill_name_input.strip():
                add_or_update_skill(student_id, skill_name_input.strip(), skill_category, proficiency)
                st.success(f"Added {skill_name_input.strip()} (Level {proficiency})")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # TAB 3: Projects
    with tab3:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("### Completed Practical Projects")
        st.caption("Practical projects contribute 20% to your Career Readiness Index.")

        projects = get_projects(student_id)
        if projects:
            for p in projects:
                col_p1, col_p2 = st.columns([4, 1])
                with col_p1:
                    st.markdown(f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between;">
                            <strong style="color:#1e293b; font-size:16px;">📁 {p['title']}</strong>
                            <span class="badge badge-primary">{p.get('complexity', 'Intermediate')}</span>
                        </div>
                        <p style="color:#475569; font-size:13px; margin: 6px 0;">{p['description']}</p>
                        <div style="font-size:12px; color:#6366f1;"><strong>Tech Stack:</strong> {p['tech_stack']}</div>
                        {f'<div style="font-size:12px; margin-top:4px;"><a href="{p["github_url"]}" target="_blank">🔗 GitHub Repository</a></div>' if p.get('github_url') else ''}
                    </div>
                    """, unsafe_allow_html=True)
                with col_p2:
                    if st.button("🗑️ Delete", key=f"del_proj_{p['id']}"):
                        delete_project(p['id'], student_id)
                        st.rerun()
        else:
            st.info("No projects added yet.")

        st.divider()
        st.markdown("#### ➕ Add Portfolio Project")
        with st.form("add_project_form"):
            p_title = st.text_input("Project Title")
            p_desc = st.text_area("Description & Architectural Highlights", height=70)
            col_x, col_y = st.columns(2)
            with col_x:
                p_stack = st.text_input("Tech Stack (e.g., Python, SQLite, FastAPI)")
                p_github = st.text_input("GitHub or Demo URL")
            with col_y:
                p_complexity = st.selectbox("Complexity Level", ["Beginner", "Intermediate", "Advanced"])
                p_live = st.text_input("Live Production URL (Optional)")

            if st.form_submit_button("Add Project", use_container_width=True):
                if p_title.strip() and p_stack.strip():
                    add_project(student_id, p_title.strip(), p_desc.strip(), p_stack.strip(), p_github.strip(), p_live.strip(), p_complexity)
                    st.success("Project logged into Digital Twin!")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # TAB 4: Certifications
    with tab4:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("### Certifications & Accreditations")
        certs = get_certifications(student_id)
        if certs:
            for c in certs:
                st.markdown(f"""
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px; margin-bottom:10px;">
                    <strong style="color:#0f172a; font-size:15px;">📜 {c['title']}</strong>
                    <div style="color:#64748b; font-size:12px;">Issuer: {c['issuing_org']} • Date: {c.get('issue_date', 'N/A')}</div>
                    {f'<a href="{c["credential_url"]}" target="_blank" style="font-size:11px; color:#4f46e5;">Verify Credential</a>' if c.get('credential_url') else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No certifications recorded.")

        st.divider()
        with st.form("add_cert_form"):
            c_title = st.text_input("Certification Title")
            c_org = st.text_input("Issuing Organization (e.g., Coursera, AWS, Google)")
            c_url = st.text_input("Credential Verification URL")
            if st.form_submit_button("Add Credential", use_container_width=True):
                if c_title.strip() and c_org.strip():
                    add_certification(student_id, c_title.strip(), c_org.strip(), datetime.now().strftime("%Y-%m-%d"), c_url.strip())
                    st.success("Certification added!")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
