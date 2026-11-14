"""
Module: Skill DNA Visual Network & Topological Analysis
Visualizes the student's technical genome using interactive Plotly network graphs,
prerequisite paths, existing vs missing skill breakdowns, and AI cognitive insights.
"""

import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import math
from SkillPath_AI.database.db import get_student_by_id, get_student_skills
from SkillPath_AI.agents.skill_dna_agent import SkillDNAAgent

def render_skill_analysis_module(student_id: int):
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="font-weight: 800; color: #1e293b; margin:0;">🧬 Skill DNA Visual Network</h2>
        <p style="color: #64748b; font-size: 14px; margin-top: 4px;">
            A topological map of your verified skills, missing competencies, prerequisite bridges, and recommended learning vectors.
        </p>
    </div>
    """, unsafe_allow_html=True)

    student = get_student_by_id(student_id)
    if not student:
        st.error("Student profile not found.")
        return

    skills = get_student_skills(student_id)
    target_career = student["target_career"]

    # Run Skill DNA Agent analysis
    agent = SkillDNAAgent()
    with st.spinner("Analyzing Skill DNA topology and graph connections..."):
        dna_result = agent.analyze_skill_dna(skills, target_career)

    # Top KPI Overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Target Career</div>
            <div class="metric-value" style="font-size:20px; color:#4f46e5;">{target_career}</div>
            <div class="metric-sub">Primary Calibration</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Existing Skills</div>
            <div class="metric-value" style="color:#10b981;">{len(dna_result['existing_skills'])}</div>
            <div class="metric-sub">Verified & Active</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Missing Skills</div>
            <div class="metric-value" style="color:#f59e0b;">{len(dna_result['missing_skills'])}</div>
            <div class="metric-sub">Target Role Gaps</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Next to Learn</div>
            <div class="metric-value" style="color:#6366f1;">{len(dna_result['next_to_learn'])}</div>
            <div class="metric-sub">High Priority Queue</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Interactive Graph Card
    st.markdown('<div class="sp-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sp-card-header">
        <h3 class="sp-card-title">🌐 Interactive Skill DNA Genome</h3>
        <span class="badge badge-agent">Agent: {dna_result['agent_name']} ({dna_result['provider']})</span>
    </div>
    """, unsafe_allow_html=True)

    fig = _create_plotly_skill_network(dna_result["graph_data"])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div style="display:flex; gap:16px; justify-content:center; flex-wrap:wrap; margin-top:10px; font-size:13px;">
        <span style="color:#10B981; font-weight:600;">● Green: Existing Active Skill</span>
        <span style="color:#F59E0B; font-weight:600;">● Amber: Missing Target Competency</span>
        <span style="color:#38BDF8; font-weight:600;">● Sky Blue: Related / Bridge Skill</span>
        <span style="color:#6366F1; font-weight:700;">● Purple: Target Career Anchor</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # AI Cognitive Analysis & Next Steps Breakdown
    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("### 🧠 AI Skill DNA Diagnosis")
        insights = dna_result.get("insights", {})

        st.markdown(f"""
        <div style="background:#f8fafc; border-left:4px solid #6366f1; padding:14px; border-radius:0 8px 8px 0; margin-bottom:14px;">
            <strong style="color:#1e293b;">Overall Topology Assessment:</strong>
            <p style="margin:4px 0 0 0; color:#334155; font-size:13px; line-height:1.5;">{insights.get('dna_summary')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**💪 Primary Strength:** {insights.get('primary_strength')}")
        st.markdown(f"**⚡ Critical Bottleneck:** <span style='color:#f59e0b; font-weight:700;'>{insights.get('critical_gap')}</span>", unsafe_allow_html=True)
        st.markdown(f"**📈 Recommended Velocity:** {insights.get('learning_velocity_recommendation')}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="sp-card">', unsafe_allow_html=True)
        st.markdown("### 🚀 Next Prioritized Skills to Learn")
        st.caption("Determined by topological prerequisites and career leverage.")

        for rank, n_skill in enumerate(dna_result["next_to_learn"], 1):
            st.markdown(f"""
            <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 14px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; margin-bottom:8px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="background:#4f46e5; color:#ffffff; width:24px; height:24px; display:inline-flex; align-items:center; justify-content:center; border-radius:50%; font-size:12px; font-weight:700;">{rank}</span>
                    <strong style="color:#0f172a; font-size:14px;">{n_skill}</strong>
                </div>
                <span class="badge badge-warning">Priority #{rank}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 🔍 All Missing Gaps")
        missing_tags = " ".join([f"<span class='badge badge-warning' style='margin:2px;'>{m}</span>" for m in dna_result["missing_skills"]])
        st.markdown(f"<div>{missing_tags}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def _create_plotly_skill_network(graph_data: dict) -> go.Figure:
    """Builds an interactive NetworkX circular-spring layout rendered in Plotly."""
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    G = nx.Graph()
    for n in nodes:
        G.add_node(n["id"], **n)
    for e in edges:
        G.add_edge(e["source"], e["target"])

    pos = nx.spring_layout(G, seed=42, k=0.85)

    # Edge traces
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color='#CBD5E1'),
        hoverinfo='none',
        mode='lines'
    )

    # Node traces
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        data = G.nodes[node]
        node_text.append(f"{data.get('label', node)}<br>Category: {data.get('group', 'Skill')}")
        node_color.append(data.get("color", "#6366F1"))
        node_size.append(data.get("size", 22))

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[G.nodes[n].get("label", n) for n in G.nodes()],
        textposition="top center",
        textfont=dict(size=11, family="Plus Jakarta Sans", color="#1E293B"),
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line_width=2,
            line_color='#FFFFFF'
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=10, r=10, t=20),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(248, 250, 252, 0.5)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=460
        )
    )
    return fig
