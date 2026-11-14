"""
Module: Central Executive Dashboard
Presents the unified Career Digital Twin overview, KPI metrics,
multi-agent activity stream, and real-time status alerts.
"""

import streamlit as st
import plotly.graph_objects as go
from SkillPath_AI.database.db import (
    get_student_by_id, get_student_skills, get_projects,
    get_roadmap, get_latest_readiness, get_active_rescue_plans,
    get_agent_logs, get_recent_submissions
)
from SkillPath_AI.config import CAREER_ROLES
from SkillPath_AI.utils.helpers import compute_career_match_stats

def render_dashboard_module(student_id: int):
    student = get_student_by_id(student_id)
    if not student:
        st.error("Student profile not found.")
        return

    skills = get_student_skills(student_id)
    target_career = student["target_career"]
    career_info = CAREER_ROLES.get(target_career, CAREER_ROLES["Full Stack Developer"])
    readiness = get_latest_readiness(student_id)
    roadmap = get_roadmap(student_id)
    rescues = get_active_rescue_plans(student_id)
    agent_logs = get_agent_logs(student_id, limit=8)
    submissions = get_recent_submissions(student_id, limit=5)

    stats = compute_career_match_stats(skills, target_career)

    # Hero Banner
    st.markdown(f"""
    <div class="hero-banner">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
            <div>
                <span class="badge" style="background:rgba(255,255,255,0.2); color:#ffffff; margin-bottom:8px;">
                    ✨ Career Digital Twin v1.0 • Synchronized
                </span>
                <h1 class="hero-title">{student['full_name']}</h1>
                <p class="hero-subtitle">
                    Target Role: <strong>{career_info['icon']} {target_career}</strong> • {career_info['demand']} Demand • Avg {career_info['avg_salary']}
                </p>
            </div>
            <div style="background:rgba(255,255,255,0.12); padding:14px 22px; border-radius:12px; text-align:center; backdrop-filter:blur(8px);">
                <div style="font-size:11px; font-weight:700; letter-spacing:0.05em; color:#c7d2fe;">READINESS INDEX</div>
                <div style="font-size:38px; font-weight:800; color:#ffffff;">{readiness['overall_score'] if readiness else 42}%</div>
                <div style="font-size:11px; color:#a5b4fc;">4-Pillar Calibration</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Active Rescue Warning if present
    if rescues:
        for r in rescues:
            st.markdown(f"""
            <div class="rescue-banner">
                <div class="rescue-title">🚨 Adaptive Learning Rescue Active: {r['weak_topic']}</div>
                <p class="rescue-text">
                    The Learning Rescue Agent detected a need for remediation after an assessment score of <strong>{r['score_trigger']}%</strong>.
                    A tailored recovery sprint has been injected into your roadmap.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # 4 SaaS Metric Cards
    completed_weeks = sum(1 for item in roadmap if item["status"] == "Completed")
    total_weeks = len(roadmap) if roadmap else 1

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Role Compatibility</div>
            <div class="metric-value" style="color:#4f46e5;">{stats['match_percentage']}%</div>
            <div class="metric-sub">{len(stats['matched_core'])} Core Requirements Met</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Verified Skills</div>
            <div class="metric-value" style="color:#10b981;">{len(skills)}</div>
            <div class="metric-sub">Active in Digital Twin</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Skill Gaps to Close</div>
            <div class="metric-value" style="color:#f59e0b;">{stats['gap_count']}</div>
            <div class="metric-sub">Target Competencies</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Roadmap Velocity</div>
            <div class="metric-value" style="color:#0ea5e9;">{completed_weeks}/{total_weeks}</div>
            <div class="metric-sub">Modules Checked Off</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Grid: Left Column (Twin Status & Quick Shortcuts), Right Column (Agent Log Stream)
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("### 🧬 Digital Twin Competency Snapshot")
        
        # Skill Breakdown Bar
        fig_bars = go.Figure()
        fig_bars.add_trace(go.Bar(
            name='Acquired Skills',
            x=['Core Skills', 'Advanced Skills'],
            y=[len(stats['matched_core']), len(stats['matched_adv'])],
            marker_color='#10b981'
        ))
        fig_bars.add_trace(go.Bar(
            name='Missing Skills',
            x=['Core Skills', 'Advanced Skills'],
            y=[len(stats['missing_core']), len(stats['missing_adv'])],
            marker_color='#f59e0b'
        ))
        fig_bars.update_layout(
            barmode='stack',
            height=220,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(248, 250, 252, 0.4)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bars, use_container_width=True)

        st.markdown(f"""
        <div style="background:#f8fafc; border-radius:8px; padding:12px; font-size:13px; color:#334155; margin-top:8px;">
            <strong>Twin Analysis:</strong> You have strong fundamentals in <code>{', '.join([s['skill_name'] for s in skills[:2]])}</code>.
            To qualify for competitive {target_career} roles, focus on closing the <strong>{stats['missing_core'][0] if stats['missing_core'] else 'modern framework'}</strong> requirement.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Recent Practical Evaluation
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("### 💻 Latest Practical Simulator Performance")
        if submissions:
            latest_sub = submissions[0]
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; background:#f8fafc; padding:12px 16px; border-radius:8px; border:1px solid #e2e8f0;">
                <div>
                    <strong style="color:#0f172a; font-size:15px;">{latest_sub['challenge_title']}</strong>
                    <div style="font-size:12px; color:#64748b;">Difficulty: {latest_sub['difficulty']} • Date: {latest_sub['evaluated_at'][:10]}</div>
                </div>
                <div style="font-size:24px; font-weight:800; color:{'#10b981' if latest_sub['score'] >= 60 else '#ef4444'};">
                    {latest_sub['score']}/100
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No simulator challenges submitted yet. Head to the 'AI Career Simulator' to test your practical skills!")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="sp-card-header">
            <h3 class="sp-card-title">🤖 Multi-Agent Activity Stream</h3>
            <span class="badge badge-agent">Real-time</span>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Live coordination events across the 5 specialized AI agents:")

        if agent_logs:
            for log in agent_logs:
                st.markdown(f"""
                <div class="log-item">
                    <div class="log-meta">
                        <span style="color:#4f46e5;">{log['agent_name']}</span>
                        <span>{log['timestamp'][11:19] if 'T' in log['timestamp'] else log['timestamp'][:19]}</span>
                    </div>
                    <div style="font-weight:600; color:#1e293b; margin-bottom:2px;">{log['action']}</div>
                    <p class="log-text">{log['output_summary']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Agent activity stream initializing...")

        st.markdown('</div>', unsafe_allow_html=True)
