"""
Module: AI Career Mentor Chatbot
An intelligent conversational companion grounded in the student's Career Digital Twin context.
Answers queries, simplifies concepts, recommends high-yield resources, and provides career advice.
"""

import streamlit as st
from datetime import datetime
from database.db import (
    get_student_by_id, get_student_skills, get_projects,
    get_recent_submissions, get_active_rescue_plans,
    get_chat_history, save_chat_message, clear_chat_history
)
from utils.helpers import call_gemini

def render_mentor_module(student_id: int):
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h2 style="font-weight: 800; color: #1e293b; margin:0;">🤖 AI Career Mentor & Co-pilot</h2>
        <p style="color: #64748b; font-size: 14px; margin-top: 4px;">
            A senior technical mentor grounded in your real-time Career Digital Twin. Ask for concept clarifications, code reviews, or interview preparation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    student = get_student_by_id(student_id)
    if not student:
        st.error("Student profile not found.")
        return

    skills = get_student_skills(student_id)
    projects = get_projects(student_id)
    submissions = get_recent_submissions(student_id)
    rescues = get_active_rescue_plans(student_id)
    target_career = student["target_career"]

    existing_skill_names = [s["skill_name"] for s in skills if s.get("is_existing", 1)]

    # Quick Prompts
    st.markdown("##### 💡 Suggested Questions")
    col_q1, col_q2, col_q3 = st.columns(3)
    quick_query = None
    with col_q1:
        if st.button("Explain JavaScript Event Loop (ELI5)", use_container_width=True):
            quick_query = "Explain the JavaScript Event Loop, Call Stack, and Task Queue like I'm 12 years old."
    with col_q2:
        if st.button("What project should I build next?", use_container_width=True):
            quick_query = f"Based on my current skills ({', '.join(existing_skill_names)}) and goal ({target_career}), what portfolio project should I build next to maximize hireability?"
    with col_q3:
        if st.button("How do I ace Full Stack interviews?", use_container_width=True):
            quick_query = f"What are the top 3 interview pitfalls for {target_career} candidates and how can I avoid them?"

    # Chat History Container
    st.markdown('<div class="sp-card" style="padding: 16px 20px; min-height: 400px;">', unsafe_allow_html=True)

    history = get_chat_history(student_id)
    if not history:
        st.markdown(f"""
        <div style="text-align:center; padding:40px 20px; color:#64748b;">
            <div style="font-size:36px; margin-bottom:8px;">👋</div>
            <strong style="color:#1e293b; font-size:16px;">Hello {student['full_name']}! I am your SkillPath AI Career Mentor.</strong>
            <p style="font-size:13px; max-width:500px; margin:8px auto 0 auto;">
                I have full visibility into your Career Digital Twin ({target_career}, active skills: {', '.join(existing_skill_names)}). Ask me anything about programming, code architecture, or career roadmaps!
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for chat in history:
            if chat["role"] == "user":
                st.markdown(f"""
                <div style="display:flex; justify-content:flex-end; margin-bottom:12px;">
                    <div style="background:#4f46e5; color:#ffffff; padding:10px 16px; border-radius:14px 14px 2px 14px; max-width:75%; font-size:14px;">
                        <strong>You:</strong><br>{chat['message']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex; justify-content:flex-start; margin-bottom:12px;">
                    <div style="background:#f1f5f9; color:#1e293b; padding:12px 18px; border-radius:14px 14px 14px 2px; max-width:85%; font-size:14px; line-height:1.6; border:1px solid #e2e8f0;">
                        <strong style="color:#4f46e5;">🤖 Mentor:</strong><br>{chat['message']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Input form
    with st.form("chat_form", clear_on_submit=True):
        user_msg = st.text_input("Ask your mentor a question...", value=quick_query or "", placeholder="e.g. How does React re-render when state changes?")
        col_c1, col_c2 = st.columns([4, 1])
        with col_c1:
            send_btn = st.form_submit_button("💬 Send Message", use_container_width=True)
        with col_c2:
            pass

    if st.button("🗑️ Clear Conversation History"):
        clear_chat_history(student_id)
        st.success("Chat history cleared.")
        st.rerun()

    query_to_process = quick_query if quick_query else (user_msg if send_btn and user_msg.strip() else None)

    if query_to_process:
        # Save user message
        save_chat_message(student_id, "user", query_to_process)

        # Context-aware system prompt
        context_prompt = f"""
        You are the SkillPath AI Career Mentor. You are speaking with student '{student['full_name']}'.
        Their Career Digital Twin context:
        - Target Career: {target_career}
        - Existing Skills: {', '.join(existing_skill_names)}
        - Completed Projects: {', '.join([p['title'] for p in projects]) if projects else 'None yet'}
        - Active Rescue Interventions: {', '.join([r['weak_topic'] for r in rescues]) if rescues else 'None'}
        - Recent Challenge Score: {submissions[0]['score'] if submissions else 'Not taken'}

        User question: "{query_to_process}"

        Provide an encouraging, technically accurate, and structured answer.
        Use clean markdown, bullet points, and practical analogies where helpful.
        """

        with st.spinner("AI Mentor thinking..."):
            reply_text, is_real_ai = call_gemini(
                context_prompt,
                system_instruction="You are a compassionate, world-class software engineering mentor and tech career coach."
            )

            if not reply_text or not is_real_ai:
                reply_text = _generate_fallback_mentor_reply(query_to_process, student, target_career, existing_skill_names)

            save_chat_message(student_id, "assistant", reply_text)

        st.rerun()

def _generate_fallback_mentor_reply(query: str, student: dict, target_career: str, skills: list) -> str:
    """Intelligent conversational responses when Gemini API is offline."""
    q_lower = query.lower()
    
    if "event loop" in q_lower:
        return """Great question! Let's demystify the **JavaScript Event Loop**:

1. **The Call Stack (The Chef):** Executes synchronous code line-by-line (`LIFO`). If a function calls another, it's pushed on top.
2. **Web APIs (The Kitchen Timers & Delivery Drivers):** Things like `setTimeout`, DOM events, and `fetch()` are handled outside the single thread by the browser.
3. **The Callback / Task Queue (The Order Ticket Line):** Once a background task finishes, its callback waits in line here.
4. **The Event Loop (The Waiter):** It constantly asks: *"Is the Call Stack empty?"* As soon as the stack is completely clear, it takes the first task from the queue and pushes it onto the stack!

💡 **Key Takeaway:** JavaScript remains single-threaded, but non-blocking because async operations wait in the queue until the main stack is empty."""

    elif "project" in q_lower:
        return f"""Based on your target goal as a **{target_career}** and your existing skills in **{', '.join(skills)}**, here is the highest-leverage project you should build next:

### 🏆 Recommended Project: Full-Stack Multi-Tenant Task API with React Frontend
- **Backend:** Node.js + Express with SQLite/PostgreSQL. Implement JWT authentication, bcrypt hashing, and CRUD endpoints.
- **Frontend:** React (Vite) with component state hooks and responsive CSS Grid/Flexbox.
- **Why it matters:** It bridges your current Python/SQL knowledge directly into modern web frameworks, satisfying the exact missing skills identified in your Skill DNA!"""

    elif "interview" in q_lower:
        return f"""Here are the top 3 things hiring managers look for in a **{target_career}**:

1. **Architectural Thinking over Syntax Memorization:** Be ready to explain *why* you chose a specific database schema or component structure, not just *how*.
2. **Handling Failure Gracefully:** In live coding, write input validation and error handling first. Production systems break, and seniors want to see defensive coding.
3. **Communication & Trade-offs:** Always speak your thoughts out loud during challenges. If a solution is $O(n^2)$, acknowledge it and explain how a hash map would optimize it to $O(n)$."""

    else:
        return f"""Thank you for asking! As your Career Mentor for **{target_career}**, I recommend continuing to practice with the **AI Career Simulator** challenges and checking off weekly milestones in your **Learning Roadmap**. 

Your current foundation with {', '.join(skills)} provides a solid springboard. What specific topic would you like to dive into next?"""
