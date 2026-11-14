"""
Module: Career Matching & Compatibility Engine
Allows students to explore target roles, evaluate skill compatibility percentages,
compare required vs acquired skills, and benchmark against 7 major tech roles.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from SkillPath_AI.config import CAREER_ROLES
from SkillPath_AI.database.db import get_student_by_id, get_student_skills
from SkillPath_AI.agents.career_prediction_agent import CareerPredictionAgent
from SkillPath_AI.agents.orchestrator import AgentOrchestrator

def render_career_matching_module(student_id: int):
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="font-weight: 800; color: #1e293b; margin:0;">🎯 Career Matching & Role Forecaster</h2>
        <p style="color: #64748b; font-size: 14px; margin-top: 4px;">
            Compare your Career Digital Twin against 7 tech roles, audit skill gaps, and explore compatibility indices.
        </p>
    </div>
    """, unsafe_allow_html=True)

    student = get_student_by_id(student_id)
    if not student:
        st.error("Student profile not found.")
        return

    skills = get_student_skills(student_id)
    current_target = student["target_career"]

    agent = CareerPredictionAgent()
    with st.spinner("Auditing career compatibility matrices..."):
        eval_data = agent.evaluate_career_compatibility(skills, current_target)

    # Dream Job Selector & Comparative Benchmark
    col_sel1, col_sel2 = st.columns([2, 1])
    with col_sel1:
        career_list = list(CAREER_ROLES.keys())
        selected_role = st.selectbox(
            "Select Career Role to Inspect & Audit:",
            career_list,
            index=career_list.index(current_target) if current_target in career_list else 0
        )
    with col_sel2:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        if selected_role != current_target:
            if st.button(f"🎯 Set {selected_role} as Active Goal", use_container_width=True, type="primary"):
                with st.spinner(f"Pivoting Digital Twin to {selected_role}..."):
                    orch = AgentOrchestrator()
                    orch.on_career_goal_changed(student_id, selected_role)
                st.success(f"Goal pivoted to {selected_role}! Learning roadmap and Skill DNA updated.")
                st.rerun()
        else:
            st.markdown(f"<span class='badge badge-success' style='padding:10px 14px;'>Current Primary Goal</span>", unsafe_allow_html=True)

    role_info = CAREER_ROLES[selected_role]
    role_eval = agent.evaluate_career_compatibility(skills, selected_role)
    target_stats = role_eval["target_stats"]
    match_pct = target_stats["match_percentage"]

    # Role Overview Card
    st.markdown(f"""
    <div class="sp-card" style="margin-top:16px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
            <div>
                <h3 style="margin:0; font-size:22px; color:#1e293b;">{role_info['icon']} {selected_role}</h3>
                <p style="color:#475569; font-size:14px; margin-top:6px; max-width:650px;">{role_info['description']}</p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:12px; color:#64748b; font-weight:600;">COMPATIBILITY INDEX</div>
                <div style="font-size:36px; font-weight:800; color:{'#10b981' if match_pct >= 65 else '#f59e0b'};">{match_pct}%</div>
                <div style="font-size:12px; color:#64748b;">Market Demand: <strong style="color:#4f46e5;">{role_info['demand']}</strong> • Avg: {role_info['avg_salary']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Detailed Skill Gap Comparison
    col_comp_l, col_comp_r = st.columns([1, 1])

    with col_comp_l:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("### ✅ Acquired Core & Advanced Skills")
        st.caption(f"{len(target_stats['matched_core']) + len(target_stats['matched_adv'])} matched competencies")

        if target_stats['matched_core']:
            st.markdown("**Core Requirements Met:**")
            for m in target_stats['matched_core']:
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:8px 12px; background:#ecfdf5; border-radius:6px; margin-bottom:6px; font-size:13px; color:#065f46;">
                    <strong>{m}</strong>
                    <span>Verified in Twin</span>
                </div>
                """, unsafe_allow_html=True)

        if target_stats['matched_adv']:
            st.markdown("**Advanced Specializations Met:**")
            for m in target_stats['matched_adv']:
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:8px 12px; background:#f0fdf4; border-radius:6px; margin-bottom:6px; font-size:13px; color:#166534;">
                    <strong>{m}</strong>
                    <span>Bonus Competency</span>
                </div>
                """, unsafe_allow_html=True)

        if not target_stats['matched_core'] and not target_stats['matched_adv']:
            st.info("No matching skills recorded yet for this role.")

        st.markdown('</div>', unsafe_allow_html=True)

    with col_comp_r:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("### ⚠️ Critical Skill Gaps to Bridge")
        st.caption(f"{target_stats['gap_count']} competencies remaining")

        if target_stats['missing_core']:
            st.markdown("**Missing Core Prerequisites:**")
            for g in target_stats['missing_core']:
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:8px 12px; background:#fffbeb; border:1px solid #fde68a; border-radius:6px; margin-bottom:6px; font-size:13px; color:#92400e;">
                    <strong>{g}</strong>
                    <span class="badge badge-warning">High Priority</span>
                </div>
                """, unsafe_allow_html=True)

        if target_stats['missing_adv']:
            st.markdown("**Missing Advanced Skills:**")
            for g in target_stats['missing_adv']:
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:8px 12px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; margin-bottom:6px; font-size:13px; color:#475569;">
                    <span>{g}</span>
                    <span style="font-size:11px; color:#94a3b8;">Secondary</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Benchmark across ALL 7 roles
    st.markdown('<div class="sp-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Benchmark Comparison Across All 7 Industry Roles")
    st.caption("Shows where your existing profile has the highest natural affinity.")

    roles_df = pd.DataFrame(eval_data["all_roles_comparison"])
    
    # Plotly Horizontal Bar Chart
    fig_bar = go.Figure(go.Bar(
        x=roles_df["compatibility"],
        y=roles_df["role"],
        orientation='h',
        marker=dict(
            color=roles_df["compatibility"],
            colorscale='Viridis',
            showscale=False
        ),
        text=[f"{val}%" for val in roles_df["compatibility"]],
        textposition="auto"
    ))
    fig_bar.update_layout(
        margin=dict(l=20, r=20, t=10, b=20),
        height=320,
        xaxis=dict(title="Compatibility Percentage (%)", range=[0, 100]),
        yaxis=dict(autorange="reversed"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(248, 250, 252, 0.4)'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Strategic AI Market Forecast
    forecast = eval_data.get("forecast", {})
    st.markdown(f"""
    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px; margin-top:10px;">
        <div style="display:flex; justify-content:space-between;">
            <strong style="color:#1e293b;">🤖 Strategic Forecast ({eval_data['provider']}):</strong>
        </div>
        <p style="margin:6px 0; color:#334155; font-size:13px;"><strong>Time to Hire:</strong> {forecast.get('feasibility_assessment')}</p>
        <p style="margin:6px 0; color:#334155; font-size:13px;"><strong>Strategic Advice:</strong> {forecast.get('strategic_advice')}</p>
        <div style="margin-top:8px;">
            <strong style="font-size:12px; color:#6366f1;">Emerging Industry Skills to Watch:</strong>
            <span style="font-size:12px; color:#475569;"> {', '.join(forecast.get('emerging_industry_skills', []))}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
