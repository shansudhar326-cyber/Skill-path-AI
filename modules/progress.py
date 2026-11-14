"""
Module: Progress Tracking & Career Readiness Score
Displays the circular readiness gauge, transparent pillar calculations,
historical readiness progression, curriculum velocity, and interactive quiz checks.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from SkillPath_AI.database.db import (
    get_student_by_id, get_student_skills, get_projects,
    get_certifications, get_recent_submissions, get_roadmap,
    get_latest_readiness, get_readiness_history, save_readiness_score
)
from SkillPath_AI.agents.career_readiness_agent import CareerReadinessAgent

def render_progress_module(student_id: int):
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="font-weight: 800; color: #1e293b; margin:0;">📈 Career Readiness & Progress Tracking</h2>
        <p style="color: #64748b; font-size: 14px; margin-top: 4px;">
            Audited evaluation of your multi-pillar competency, curriculum velocity, and career readiness trajectory.
        </p>
    </div>
    """, unsafe_allow_html=True)

    student = get_student_by_id(student_id)
    if not student:
        st.error("Student profile not found.")
        return

    target_career = student["target_career"]
    skills = get_student_skills(student_id)
    projects = get_projects(student_id)
    certs = get_certifications(student_id)
    submissions = get_recent_submissions(student_id)
    roadmap = get_roadmap(student_id)

    # Re-calculate readiness using agent
    agent = CareerReadinessAgent()
    readiness = agent.calculate_readiness(skills, target_career, submissions, projects, certs)

    # Top Section: Gauge Chart & Transparent Breakdown
    col_gauge, col_breakdown = st.columns([1, 1])

    with col_gauge:
        st.markdown('<div class="sp-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown(f"### 🎯 Career Readiness Index")
        st.markdown(f"<span class='badge' style='background:{readiness['badge_color']}; color:#ffffff; font-size:13px; padding:6px 14px;'>{readiness['tier']}</span>", unsafe_allow_html=True)

        # Plotly Circular Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = readiness["overall_score"],
            domain = {'x': [0, 1], 'y': [0, 1]},
            number = {'suffix': "%", 'font': {'size': 44, 'family': "Plus Jakarta Sans", 'color': "#1e293b"}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
                'bar': {'color': "#4f46e5", 'thickness': 0.28},
                'bgcolor': "#f1f5f9",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 40], 'color': "rgba(139, 92, 246, 0.15)"},
                    {'range': [40, 70], 'color': "rgba(59, 130, 246, 0.15)"},
                    {'range': [70, 100], 'color': "rgba(16, 185, 129, 0.15)"}
                ],
            }
        ))
        fig_gauge.update_layout(
            height=260,
            margin=dict(l=20, r=20, t=20, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            font={'family': "Plus Jakarta Sans"}
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.caption(readiness.get("disclaimer"))
        st.markdown('</div>', unsafe_allow_html=True)

    with col_breakdown:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("### ⚖️ Transparent Scoring Formula")
        st.caption("How your score is calibrated from verified platform activities:")

        pillars = [
            ("Technical Skills Coverage", readiness["tech_score"], "35%", "#4f46e5"),
            ("Practical Challenge Submissions", readiness["challenge_score"], "30%", "#0ea5e9"),
            ("Portfolio Projects & Complexity", readiness["project_score"], "20%", "#10b981"),
            ("Problem-Solving & Certifications", readiness["quiz_score"], "15%", "#f59e0b")
        ]

        for name, score, weight, color in pillars:
            st.markdown(f"""
            <div style="margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;">
                    <strong style="color:#1e293b;">{name}</strong>
                    <span style="color:#64748b; font-weight:600;">{score}/100 • Weight: {weight}</span>
                </div>
                <div style="background:#f1f5f9; border-radius:9999px; height:8px; overflow:hidden;">
                    <div style="background:{color}; width:{score}%; height:100%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px; margin-top:14px; font-size:12px; color:#475569;">
            <strong>🚀 Highest Leverage Action:</strong> {readiness['audit'].get('highest_leverage_action')}
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Historical Progression Chart
    st.markdown('<div class="sp-card">', unsafe_allow_html=True)
    st.markdown("### 📈 Readiness Index Progression History")
    history = get_readiness_history(student_id)

    if history:
        hist_df = pd.DataFrame(history)
        hist_df["calculated_at"] = pd.to_datetime(hist_df["calculated_at"])
        
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Scatter(
            x=hist_df["calculated_at"].dt.strftime("%b %d, %H:%M"),
            y=hist_df["overall_score"],
            mode='lines+markers',
            name='Overall Readiness',
            line=dict(color='#4f46e5', width=3),
            marker=dict(size=8)
        ))
        fig_hist.add_trace(go.Scatter(
            x=hist_df["calculated_at"].dt.strftime("%b %d, %H:%M"),
            y=hist_df["tech_score"],
            mode='lines',
            name='Technical Skills',
            line=dict(color='#0ea5e9', dash='dash')
        ))
        fig_hist.add_trace(go.Scatter(
            x=hist_df["calculated_at"].dt.strftime("%b %d, %H:%M"),
            y=hist_df["challenge_score"],
            mode='lines',
            name='Challenges',
            line=dict(color='#10b981', dash='dot')
        ))
        fig_hist.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            height=280,
            xaxis=dict(title="Assessment Timeline"),
            yaxis=dict(title="Score (0-100)", range=[0, 100]),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(248, 250, 252, 0.4)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No historical progress datapoints logged yet.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Interactive Problem-Solving Knowledge Check
    st.markdown('<div class="sp-card">', unsafe_allow_html=True)
    st.markdown("### 🧩 Quick Problem-Solving Knowledge Check")
    st.caption("Answer mini-quizzes to elevate your Problem-Solving pillar.")

    with st.form("quick_quiz_form"):
        st.markdown("**Question: What is the primary difference between `var`, `let`, and `const` in modern ECMAScript?**")
        quiz_choice = st.radio(
            "Select the correct answer:",
            [
                "A) 'var' is block-scoped while 'let' and 'const' are function-scoped.",
                "B) 'var' is function-scoped and hoisted with undefined, while 'let' and 'const' are block-scoped and temporal dead-zoned.",
                "C) 'const' creates completely immutable nested objects that can never be modified.",
                "D) There is no behavioral difference; they are syntactic aliases."
            ],
            index=0
        )
        submitted_quiz = st.form_submit_button("Verify Answer & Boost Problem-Solving Score")

        if submitted_quiz:
            if quiz_choice.startswith("B"):
                st.success("🎉 Correct! 'let' and 'const' respect lexical block scopes and prevent accidental hoisting bugs.")
                # Save boosted readiness
                new_quiz = min(100, readiness["quiz_score"] + 10)
                save_readiness_score(
                    student_id,
                    min(100, readiness["overall_score"] + 2),
                    readiness["tech_score"],
                    readiness["challenge_score"],
                    readiness["project_score"],
                    new_quiz,
                    "Boosted by successfully completing JavaScript Scoping Knowledge Check."
                )
                st.rerun()
            else:
                st.error("Incorrect. Review lexical scoping: 'var' is function-scoped while 'let' and 'const' are block-scoped.")

    st.markdown('</div>', unsafe_allow_html=True)
