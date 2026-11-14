"""
Module: AI Career Simulator & Practical Evaluator
Presents real-world software engineering challenges, proctors submissions,
and evaluates code on correctness, logic, security, and practical production standards.
"""

import streamlit as st
import json
from SkillPath_AI.database.db import (
    get_student_by_id, get_challenges_for_student, get_challenge_by_id,
    get_recent_submissions
)
from SkillPath_AI.agents.orchestrator import AgentOrchestrator

def render_simulator_module(student_id: int):
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="font-weight: 800; color: #1e293b; margin:0;">💻 AI Career Simulator & Code Proctor</h2>
        <p style="color: #64748b; font-size: 14px; margin-top: 4px;">
            Demonstrate real-world engineering proficiency by solving role-specific practical challenges. Evaluated on logic, correctness, and production hygiene.
        </p>
    </div>
    """, unsafe_allow_html=True)

    student = get_student_by_id(student_id)
    if not student:
        st.error("Student profile not found.")
        return

    target_career = student["target_career"]
    challenges = get_challenges_for_student(student_id, role=target_career)

    if not challenges:
        challenges = get_challenges_for_student(student_id)

    if not challenges:
        st.warning("No challenges configured yet. Please check back shortly.")
        return

    # Select Challenge
    challenge_titles = [f"{c['difficulty']} • {c['title']}" for c in challenges]
    sel_idx = st.selectbox("Select a Practical Simulation Challenge:", range(len(challenge_titles)), format_func=lambda i: challenge_titles[i])
    current_challenge = challenges[sel_idx]

    # Challenge Specification Card
    st.markdown(f"""
    <div class="sp-card">
        <div class="sp-card-header">
            <h3 class="sp-card-title">📝 {current_challenge['title']}</h3>
            <div>
                <span class="badge badge-primary">{current_challenge['difficulty']}</span>
                <span class="badge badge-agent">Role: {current_challenge['career_role']}</span>
            </div>
        </div>
        <p style="color:#334155; font-size:14px; line-height:1.6; margin-bottom:12px;">{current_challenge['description']}</p>
        <div style="background:#f1f5f9; border-radius:8px; padding:12px; font-size:13px; color:#1e293b;">
            <strong>🎯 Expected Deliverable:</strong> {current_challenge['expected_output']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Coding Workspace & Quick Action Buttons
    st.markdown("### 🛠️ Interactive Code Workspace")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn1:
        if st.button("📋 Load Starter Boilerplate", use_container_width=True):
            st.session_state[f"code_editor_{current_challenge['id']}"] = current_challenge.get("starter_code", "")
            st.rerun()
    with col_btn2:
        # User requirement 5 test helper:
        if st.button("🧪 Simulate Weak Submission (30% Score)", use_container_width=True, help="Loads a submission that triggers the Adaptive Learning Rescue flow"):
            st.session_state[f"code_editor_{current_challenge['id']}"] = """// Weak / Incomplete attempt
var x = 1;
function checkLogin() {
    alert("logging in...");
    // TODO: implement REST API and database query
}"""
            st.session_state[f"notes_{current_challenge['id']}"] = "Tried to start the function but struggled with asynchronous callbacks and JWT tokens."
            st.rerun()
    with col_btn3:
        if st.button("✨ Load Production Exemplar Solution", use_container_width=True):
            if "rest api" in current_challenge['title'].lower():
                st.session_state[f"code_editor_{current_challenge['id']}"] = """const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// POST /api/auth/login
router.post('/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        if (!email || !password) {
            return res.status(400).json({ error: 'Email and password are required.' });
        }

        // Safe database lookup & bcrypt verification
        const user = await findUserByEmail(email);
        if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
            return res.status(401).json({ error: 'Invalid authentication credentials.' });
        }

        // Signed JWT Token with expiry
        const token = jwt.sign(
            { sub: user.id, email: user.email, role: user.role },
            process.env.JWT_SECRET || 'secret-key',
            { expiresIn: '2h' }
        );

        return res.status(200).json({
            message: 'Authentication successful',
            token,
            expiresIn: 7200
        });
    } catch (err) {
        console.error('Auth error:', err);
        return res.status(500).json({ error: 'Internal server error' });
    }
});

module.exports = router;"""
            elif "react" in current_challenge['title'].lower():
                st.session_state[f"code_editor_{current_challenge['id']}"] = """import React, { useState, useEffect } from 'react';

export default function TaskList() {
  const [tasks, setTasks] = useState(() => {
    const saved = localStorage.getItem('skillpath_tasks');
    return saved ? JSON.parse(saved) : [];
  });
  const [inputVal, setInputVal] = useState('');

  useEffect(() => {
    localStorage.setItem('skillpath_tasks', JSON.stringify(tasks));
  }, [tasks]);

  const handleAddTask = (e) => {
    e.preventDefault();
    if (!inputVal.trim()) return;
    const newTask = { id: Date.now(), title: inputVal.trim(), completed: false };
    setTasks(prev => [...prev, newTask]);
    setInputVal('');
  };

  const toggleTask = (id) => {
    setTasks(prev => prev.map(t => t.id === id ? { ...t, completed: !t.completed } : t));
  };

  return (
    <div className="task-container">
      <form onSubmit={handleAddTask}>
        <input 
          value={inputVal} 
          onChange={e => setInputVal(e.target.value)} 
          placeholder="New task..."
        />
        <button type="submit">Add Task</button>
      </form>
      <ul>
        {tasks.map(t => (
          <li key={t.id} onClick={() => toggleTask(t.id)} style={{ textDecoration: t.completed ? 'line-through' : 'none' }}>
            {t.title}
          </li>
        ))}
      </ul>
    </div>
  );
}"""
            else:
                st.session_state[f"code_editor_{current_challenge['id']}"] = current_challenge.get("starter_code", "")
            st.rerun()

    code_val = st.session_state.get(f"code_editor_{current_challenge['id']}", current_challenge.get("starter_code", ""))
    notes_val = st.session_state.get(f"notes_{current_challenge['id']}", "")

    code_input = st.text_area("Your Code Implementation:", value=code_val, height=260, key=f"input_area_{current_challenge['id']}")
    notes_input = st.text_input("Implementation Notes / Assumptions (Optional):", value=notes_val, key=f"notes_area_{current_challenge['id']}")

    submit_col1, submit_col2 = st.columns([2, 1])
    with submit_col1:
        submit_btn = st.button("🚀 Submit Solution for AI Evaluation", type="primary", use_container_width=True)

    if submit_btn:
        with st.spinner("Challenge Agent evaluating logic, correctness, and security..."):
            orch = AgentOrchestrator()
            result = orch.evaluate_and_orchestrate_submission(
                student_id=student_id,
                challenge=current_challenge,
                code_submission=code_input,
                student_notes=notes_input
            )

        evaluation = result["evaluation"]
        score = evaluation.get("score", 0)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sp-card" style="border-top: 4px solid {'#10b981' if score >= 60 else '#ef4444'};">
            <div class="sp-card-header">
                <h3 class="sp-card-title">📊 Evaluation Report</h3>
                <span class="badge badge-agent">Evaluator: {evaluation.get('provider')}</span>
            </div>
            <div style="display:flex; justify-content:space-around; text-align:center; margin:16px 0; background:#f8fafc; padding:16px; border-radius:10px;">
                <div>
                    <div style="font-size:12px; color:#64748b; font-weight:600;">OVERALL SCORE</div>
                    <div style="font-size:32px; font-weight:800; color:{'#10b981' if score >= 75 else ('#f59e0b' if score >= 60 else '#ef4444')};">{score}/100</div>
                </div>
                <div>
                    <div style="font-size:12px; color:#64748b; font-weight:600;">CORRECTNESS</div>
                    <div style="font-size:26px; font-weight:700; color:#1e293b;">{evaluation.get('correctness_score')}%</div>
                </div>
                <div>
                    <div style="font-size:12px; color:#64748b; font-weight:600;">LOGIC & ARCH</div>
                    <div style="font-size:26px; font-weight:700; color:#1e293b;">{evaluation.get('logic_score')}%</div>
                </div>
                <div>
                    <div style="font-size:12px; color:#64748b; font-weight:600;">PRACTICAL</div>
                    <div style="font-size:26px; font-weight:700; color:#1e293b;">{evaluation.get('practical_score')}%</div>
                </div>
            </div>
            <h4 style="margin:14px 0 6px 0; color:#1e293b;">Detailed Lead Engineer Feedback:</h4>
            <p style="color:#334155; line-height:1.6; font-size:14px; background:#f1f5f9; padding:14px; border-radius:8px;">{evaluation.get('feedback')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Highlight if rescue was triggered!
        if result.get("rescue_triggered"):
            r_plan = result.get("rescue_plan", {})
            st.markdown(f"""
            <div class="rescue-banner">
                <div class="rescue-title">🚨 Adaptive Learning Rescue Triggered (Score: {score}%)</div>
                <p class="rescue-text">
                    <strong>Weak Concept Diagnosed:</strong> {r_plan.get('weak_concept_diagnosis')}<br><br>
                    <strong>Simplified Mental Model:</strong> {r_plan.get('simplified_explanation')}<br><br>
                    <strong>Roadmap Action:</strong> {r_plan.get('roadmap_intervention', {}).get('prerequisite_warning')}
                </p>
                <div style="margin-top:10px;">
                    <a href="#learning-roadmap" style="font-size:12px; font-weight:700; color:#b45309;">👉 Head over to the 'Learning Roadmap' tab to view your customized remediation modules and exercises.</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Recent Submissions History
    st.markdown('<div class="sp-card">', unsafe_allow_html=True)
    st.markdown("### 🕒 Recent Challenge Submissions")
    subs = get_recent_submissions(student_id)
    if subs:
        for s in subs:
            score_color = "#10b981" if s["score"] >= 75 else ("#f59e0b" if s["score"] >= 60 else "#ef4444")
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; margin-bottom:8px;">
                <div>
                    <strong style="color:#0f172a; font-size:14px;">{s['challenge_title']}</strong>
                    <div style="font-size:11px; color:#64748b;">Evaluated at: {s['evaluated_at'][:19].replace('T', ' ')} • Role: {s['career_role']}</div>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:18px; font-weight:800; color:{score_color};">{s['score']}/100</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No submissions logged yet.")
    st.markdown('</div>', unsafe_allow_html=True)
