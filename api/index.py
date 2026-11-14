"""
Vercel Serverless Entrypoint for SkillPath AI
Provides full Flask WSGI application powering the Career Digital Twin on Vercel.
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, redirect, url_for

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import CAREER_ROLES, SKILL_TAXONOMY, APP_NAME, APP_VERSION
from database.db import (
    init_db, seed_demo_student, authenticate_student, get_student_by_id,
    get_student_skills, get_projects, get_certifications, get_challenges_for_student,
    get_challenge_by_id, get_recent_submissions, get_roadmap, update_roadmap_status,
    get_active_rescue_plans, resolve_rescue_plan, get_readiness_history, get_latest_readiness,
    save_readiness_score, get_chat_history, save_chat_message, clear_chat_history,
    get_agent_logs, reset_student_to_demo, add_or_update_skill, delete_skill
)
from agents.orchestrator import AgentOrchestrator
from utils.helpers import compute_career_match_stats, is_gemini_available, get_gemini_api_key

app = Flask(__name__)
app.secret_key = "skillpath-ai-secret-key-vercel"

# Initialize DB on cold start
try:
    init_db()
    seed_demo_student()
except Exception as e:
    print(f"[Init Warning] {e}")

def get_current_student_id():
    """Retrieve demo student ID (M. Sudharshan) or default to first student."""
    user = authenticate_student("M.Sudharshan", "sudharsh390")
    if user:
        return user["id"]
    return 1

# --- BASE HTML TEMPLATE (SaaS Tailwind Layout) ---
BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }} – SkillPath AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f8fafc; }
        code, pre { font-family: 'JetBrains Mono', monospace; }
        .hero-banner { background: linear-gradient(135deg, #4f46e5 0%, #3730a3 50%, #1e1b4b 100%); }
        .badge { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600; }
        .badge-primary { background: #eef2ff; color: #4f46e5; }
        .badge-success { background: #ecfdf5; color: #059669; }
        .badge-warning { background: #fffbeb; color: #d97706; }
        .badge-agent { background: #f3e8ff; color: #7e22ce; border: 1px solid #e9d5ff; }
    </style>
</head>
<body class="text-slate-800 antialiased flex flex-col md:flex-row min-h-screen">

    <!-- SIDEBAR NAVIGATION -->
    <aside class="w-full md:w-64 bg-white border-r border-slate-200 p-5 flex flex-col justify-between shrink-0">
        <div>
            <!-- LOGO -->
            <div class="flex items-center gap-3 pb-4 border-b border-slate-100">
                <span class="text-3xl">🧬</span>
                <div>
                    <div class="font-extrabold text-lg text-slate-900 leading-tight">SkillPath AI</div>
                    <div class="text-[10px] font-bold text-indigo-600 tracking-wider">CAREER DIGITAL TWIN</div>
                </div>
            </div>

            <!-- STUDENT PILL -->
            <div class="bg-slate-50 border border-slate-200 rounded-xl p-3 my-4">
                <div class="text-xs text-slate-500 font-semibold">ACTIVE TWIN</div>
                <div class="font-bold text-slate-900 text-sm">{{ student.full_name }}</div>
                <div class="text-xs text-indigo-600 font-medium">🎯 {{ student.target_career }}</div>
            </div>

            <!-- NAV LINKS -->
            <nav class="space-y-1">
                <a href="/" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-semibold {% if active_page == 'dashboard' %}bg-indigo-50 text-indigo-700{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                    <span>📊</span> Dashboard
                </a>
                <a href="/profile" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-semibold {% if active_page == 'profile' %}bg-indigo-50 text-indigo-700{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                    <span>👤</span> My Profile
                </a>
                <a href="/skill-dna" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-semibold {% if active_page == 'skill-dna' %}bg-indigo-50 text-indigo-700{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                    <span>🧬</span> Skill DNA
                </a>
                <a href="/career-matching" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-semibold {% if active_page == 'career-matching' %}bg-indigo-50 text-indigo-700{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                    <span>🎯</span> Career Matching
                </a>
                <a href="/simulator" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-semibold {% if active_page == 'simulator' %}bg-indigo-50 text-indigo-700{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                    <span>💻</span> AI Career Simulator
                </a>
                <a href="/roadmap" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-semibold {% if active_page == 'roadmap' %}bg-indigo-50 text-indigo-700{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                    <span>🗺️</span> Learning Roadmap
                </a>
                <a href="/progress" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-semibold {% if active_page == 'progress' %}bg-indigo-50 text-indigo-700{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                    <span>📈</span> Progress Tracking
                </a>
                <a href="/mentor" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-semibold {% if active_page == 'mentor' %}bg-indigo-50 text-indigo-700{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                    <span>🤖</span> AI Mentor
                </a>
                <a href="/settings" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-semibold {% if active_page == 'settings' %}bg-indigo-50 text-indigo-700{% else %}text-slate-600 hover:bg-slate-50 hover:text-slate-900{% endif %}">
                    <span>⚙️</span> Settings
                </a>
            </nav>
        </div>

        <!-- SIDEBAR FOOTER -->
        <div class="pt-4 border-t border-slate-100">
            <div class="bg-amber-50 border border-amber-200 text-amber-800 text-[11px] rounded-lg p-2 font-medium mb-3">
                ● Demo Mode: Active (Heuristics)
            </div>
            <div class="flex gap-2">
                <form action="/api/settings/reset" method="POST" class="w-full">
                    <button type="submit" class="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold py-2 px-3 rounded-lg transition">
                        🔄 Reset Demo Twin
                    </button>
                </form>
            </div>
            <div class="text-[10px] text-slate-400 mt-2 text-center">SkillPath AI v1.0.0 • Vercel Edition</div>
        </div>
    </aside>

    <!-- MAIN CONTENT VIEW -->
    <main class="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full">
        {% block content %}{% endblock %}
    </main>

</body>
</html>
"""

# --- ROUTE 1: DASHBOARD ---
@app.route("/")
def dashboard():
    sid = get_current_student_id()
    student = get_student_by_id(sid)
    skills = get_student_skills(sid)
    target_career = student["target_career"]
    career_info = CAREER_ROLES.get(target_career, CAREER_ROLES["Full Stack Developer"])
    readiness = get_latest_readiness(sid)
    roadmap = get_roadmap(sid)
    rescues = get_active_rescue_plans(sid)
    agent_logs = get_agent_logs(sid, limit=6)
    submissions = get_recent_submissions(sid, limit=3)
    stats = compute_career_match_stats(skills, target_career)

    content = """
    {% extends "base" %}
    {% block content %}
    <!-- HERO BANNER -->
    <div class="hero-banner rounded-2xl p-6 text-white mb-6 shadow-md relative overflow-hidden">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative z-10">
            <div>
                <span class="inline-block bg-white/20 text-white text-xs font-semibold px-2.5 py-1 rounded-full mb-2">
                    ✨ Career Digital Twin v1.0 • Synchronized
                </span>
                <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight">{{ student.full_name }}</h1>
                <p class="text-indigo-200 text-sm mt-1">
                    Target Role: <strong>{{ career_info.icon }} {{ student.target_career }}</strong> • {{ career_info.demand }} Demand • Avg {{ career_info.avg_salary }}
                </p>
            </div>
            <div class="bg-white/10 backdrop-blur-md px-5 py-3 rounded-xl text-center border border-white/20">
                <div class="text-[11px] font-bold text-indigo-200 uppercase tracking-wider">READINESS INDEX</div>
                <div class="text-4xl font-extrabold text-white">{{ readiness.overall_score if readiness else 42 }}%</div>
                <div class="text-[11px] text-indigo-300">4-Pillar Calibration</div>
            </div>
        </div>
    </div>

    <!-- RESCUE ALERT -->
    {% if rescues %}
    {% for r in rescues %}
    <div class="bg-amber-50 border border-amber-300 border-l-4 border-l-amber-500 rounded-xl p-4 mb-6 shadow-sm">
        <div class="font-bold text-amber-900 text-sm flex items-center gap-2">
            🚨 Adaptive Learning Rescue Active: {{ r.weak_topic }}
        </div>
        <p class="text-amber-800 text-xs mt-1 leading-relaxed">
            The Learning Rescue Agent detected a need for remediation after an assessment score of <strong>{{ r.score_trigger }}%</strong>. A tailored recovery sprint has been injected into your roadmap.
        </p>
        <div class="mt-2">
            <a href="/roadmap" class="text-xs font-bold text-amber-900 underline">👉 View your customized remediation exercises</a>
        </div>
    </div>
    {% endfor %}
    {% endif %}

    <!-- 4 KPI CARDS -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Role Compatibility</div>
            <div class="text-2xl font-extrabold text-indigo-600 mt-1">{{ stats.match_percentage }}%</div>
            <div class="text-xs text-slate-500 mt-1">{{ stats.matched_core|length }} Core Met</div>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Verified Skills</div>
            <div class="text-2xl font-extrabold text-emerald-600 mt-1">{{ skills|length }}</div>
            <div class="text-xs text-slate-500 mt-1">Active in Twin</div>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Skill Gaps to Close</div>
            <div class="text-2xl font-extrabold text-amber-500 mt-1">{{ stats.gap_count }}</div>
            <div class="text-xs text-slate-500 mt-1">Target Competencies</div>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Roadmap Progress</div>
            <div class="text-2xl font-extrabold text-sky-500 mt-1">1/{{ roadmap|length }}</div>
            <div class="text-xs text-slate-500 mt-1">Modules Checked Off</div>
        </div>
    </div>

    <!-- GRID: TWIN SNAPSHOT & AGENT FEED -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
            <!-- TWIN STATUS CARD -->
            <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <h3 class="text-base font-bold text-slate-900 mb-2">🧬 Digital Twin Competency Snapshot</h3>
                <p class="text-xs text-slate-500 mb-4">Core verified foundations vs missing role requirements.</p>

                <div class="space-y-3">
                    <div>
                        <div class="flex justify-between text-xs font-semibold mb-1">
                            <span>Core Requirements Met</span>
                            <span class="text-emerald-600">{{ stats.matched_core|length }} / {{ (stats.matched_core|length + stats.missing_core|length) }}</span>
                        </div>
                        <div class="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                            <div class="bg-emerald-500 h-2.5 rounded-full" style="width: {{ (stats.matched_core|length / (stats.matched_core|length + stats.missing_core|length) * 100)|int }}%"></div>
                        </div>
                    </div>
                </div>

                <div class="bg-slate-50 border border-slate-200 rounded-lg p-3.5 mt-4 text-xs text-slate-600">
                    <strong>Twin Analysis:</strong> You possess strong fundamentals in <code>Python</code> and <code>SQL</code>. To bridge into <strong>{{ student.target_career }}</strong>, prioritize acquiring <strong>JavaScript (ES6+)</strong>, <strong>React</strong>, and <strong>Express.js</strong>.
                </div>
            </div>

            <!-- RECENT SUBMISSION -->
            <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <h3 class="text-base font-bold text-slate-900 mb-3">💻 Latest Practical Simulator Performance</h3>
                {% if submissions %}
                <div class="flex justify-between items-center bg-slate-50 border border-slate-200 p-3.5 rounded-lg">
                    <div>
                        <div class="font-bold text-slate-900 text-sm">{{ submissions[0].challenge_title }}</div>
                        <div class="text-xs text-slate-500">Difficulty: {{ submissions[0].difficulty }} • Date: {{ submissions[0].evaluated_at[:10] }}</div>
                    </div>
                    <div class="text-2xl font-extrabold {% if submissions[0].score >= 60 %}text-emerald-600{% else %}text-rose-600{% endif %}">
                        {{ submissions[0].score }}/100
                    </div>
                </div>
                {% else %}
                <p class="text-xs text-slate-400">No submissions yet. Head over to the <a href="/simulator" class="text-indigo-600 underline">AI Career Simulator</a>!</p>
                {% endif %}
            </div>
        </div>

        <!-- AGENT STREAM -->
        <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div class="flex justify-between items-center pb-3 border-b border-slate-100 mb-4">
                <h3 class="text-base font-bold text-slate-900">🤖 Multi-Agent Stream</h3>
                <span class="badge badge-agent">Live</span>
            </div>
            <div class="space-y-3">
                {% for log in agent_logs %}
                <div class="border-l-2 border-indigo-500 bg-slate-50 p-2.5 rounded-r-lg text-xs">
                    <div class="flex justify-between font-bold text-indigo-700 text-[11px] mb-1">
                        <span>{{ log.agent_name }}</span>
                        <span class="text-slate-400">{{ log.timestamp[11:19] }}</span>
                    </div>
                    <div class="font-semibold text-slate-800 text-[11px]">{{ log.action }}</div>
                    <p class="text-slate-600 font-mono text-[10px] mt-0.5">{{ log.output_summary }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    {% endblock %}
    """
    tmpl = BASE_LAYOUT.replace("{% block content %}{% endblock %}", content)
    return render_template_string(
        tmpl,
        page_title="Dashboard",
        active_page="dashboard",
        student=student,
        career_info=career_info,
        readiness=readiness,
        roadmap=roadmap,
        rescues=rescues,
        agent_logs=agent_logs,
        submissions=submissions,
        stats=stats,
        skills=skills
    )

# --- ROUTE 2: PROFILE ---
@app.route("/profile")
def profile():
    sid = get_current_student_id()
    student = get_student_by_id(sid)
    skills = get_student_skills(sid)
    projects = get_projects(sid)
    certs = get_certifications(sid)

    content = """
    {% extends "base" %}
    {% block content %}
    <div class="mb-6">
        <h2 class="text-2xl font-extrabold text-slate-900">👤 Student Profile & Career Digital Twin</h2>
        <p class="text-slate-500 text-sm mt-1">Configure your verified skills, proficiency ratings, and portfolio projects.</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- IDENTITY & CAREER -->
        <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h3 class="text-base font-bold text-slate-900 mb-4">📋 Personal Information</h3>
            <div class="space-y-3 text-sm">
                <div>
                    <label class="text-xs font-semibold text-slate-500 uppercase">Full Name</label>
                    <div class="font-bold text-slate-900">{{ student.full_name }}</div>
                </div>
                <div>
                    <label class="text-xs font-semibold text-slate-500 uppercase">Username</label>
                    <div class="text-slate-800">{{ student.username }}</div>
                </div>
                <div>
                    <label class="text-xs font-semibold text-slate-500 uppercase">Email</label>
                    <div class="text-slate-800">{{ student.email }}</div>
                </div>
                <div>
                    <label class="text-xs font-semibold text-slate-500 uppercase">Target Career</label>
                    <div class="font-bold text-indigo-600">🎯 {{ student.target_career }}</div>
                </div>
                <div>
                    <label class="text-xs font-semibold text-slate-500 uppercase">Bio</label>
                    <p class="text-xs text-slate-600 leading-relaxed">{{ student.bio }}</p>
                </div>
            </div>
        </div>

        <!-- SKILLS LIST & ADD -->
        <div class="lg:col-span-2 space-y-6">
            <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-base font-bold text-slate-900">⚡ Verified Skills ({{ skills|length }})</h3>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
                    {% for s in skills %}
                    <div class="bg-slate-50 border border-slate-200 rounded-xl p-3.5 flex justify-between items-center">
                        <div>
                            <div class="font-bold text-slate-900 text-sm">{{ s.skill_name }}</div>
                            <div class="text-indigo-600 text-xs mt-0.5">
                                {% for i in range(s.proficiency_level) %}★{% endfor %}{% for i in range(5 - s.proficiency_level) %}☆{% endfor %}
                            </div>
                            <div class="text-[10px] text-slate-500">{{ s.category }}</div>
                        </div>
                        <form action="/api/skills/delete" method="POST">
                            <input type="hidden" name="skill_id" value="{{ s.id }}">
                            <button type="submit" class="text-xs text-rose-500 hover:text-rose-700 font-bold p-1">🗑️</button>
                        </form>
                    </div>
                    {% endfor %}
                </div>

                <!-- ADD SKILL FORM -->
                <div class="pt-4 border-t border-slate-100">
                    <h4 class="text-xs font-bold uppercase text-slate-500 mb-3">➕ Add Technical Skill</h4>
                    <form action="/api/skills/add" method="POST" class="grid grid-cols-1 sm:grid-cols-4 gap-3">
                        <input type="text" name="skill_name" placeholder="Skill (e.g., React, TypeScript)" required class="sm:col-span-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs">
                        <select name="proficiency" class="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs">
                            <option value="1">Level 1/5</option>
                            <option value="2">Level 2/5</option>
                            <option value="3" selected>Level 3/5</option>
                            <option value="4">Level 4/5</option>
                            <option value="5">Level 5/5</option>
                        </select>
                        <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs py-2 px-3 rounded-lg transition">Add</button>
                    </form>
                </div>
            </div>

            <!-- PROJECTS -->
            <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <h3 class="text-base font-bold text-slate-900 mb-3">💼 Completed Practical Projects</h3>
                {% for p in projects %}
                <div class="bg-slate-50 border border-slate-200 rounded-lg p-3.5 mb-2">
                    <div class="flex justify-between items-start">
                        <strong class="text-sm text-slate-900">📁 {{ p.title }}</strong>
                        <span class="badge badge-primary">{{ p.complexity }}</span>
                    </div>
                    <p class="text-xs text-slate-600 mt-1">{{ p.description }}</p>
                    <div class="text-[11px] text-indigo-600 font-semibold mt-1">Tech Stack: {{ p.tech_stack }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    {% endblock %}
    """
    tmpl = BASE_LAYOUT.replace("{% block content %}{% endblock %}", content)
    return render_template_string(tmpl, page_title="My Profile", active_page="profile", student=student, skills=skills, projects=projects, certs=certs)

# --- ROUTE 3: SKILL DNA ---
@app.route("/skill-dna")
def skill_dna():
    sid = get_current_student_id()
    student = get_student_by_id(sid)
    skills = get_student_skills(sid)
    target_career = student["target_career"]

    orch = AgentOrchestrator()
    dna = orch.skill_dna_agent.analyze_skill_dna(skills, target_career)

    content = """
    {% extends "base" %}
    {% block content %}
    <div class="mb-6">
        <h2 class="text-2xl font-extrabold text-slate-900">🧬 Skill DNA Visual Network</h2>
        <p class="text-slate-500 text-sm mt-1">Topological map of your verified skills, missing competencies, and learning vectors.</p>
    </div>

    <!-- 4 KPI ROW -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Target Career</div>
            <div class="text-lg font-extrabold text-indigo-600 mt-1 truncate">{{ student.target_career }}</div>
            <div class="text-xs text-slate-500 mt-0.5">Calibration</div>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Existing Skills</div>
            <div class="text-2xl font-extrabold text-emerald-600 mt-1">{{ dna.existing_skills|length }}</div>
            <div class="text-xs text-slate-500 mt-0.5">Verified Active</div>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Missing Competencies</div>
            <div class="text-2xl font-extrabold text-amber-500 mt-1">{{ dna.missing_skills|length }}</div>
            <div class="text-xs text-slate-500 mt-0.5">Target Gaps</div>
        </div>
        <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
            <div class="text-xs font-bold text-slate-400 uppercase tracking-wider">Next to Learn</div>
            <div class="text-2xl font-extrabold text-sky-500 mt-1">{{ dna.next_to_learn|length }}</div>
            <div class="text-xs text-slate-500 mt-0.5">Priority Queue</div>
        </div>
    </div>

    <!-- PLOTLY GRAPH CONTAINER -->
    <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm mb-6">
        <div class="flex justify-between items-center mb-4">
            <h3 class="text-base font-bold text-slate-900">🌐 Interactive Skill DNA Genome</h3>
            <span class="badge badge-agent">Agent: Skill DNA Agent ({{ dna.provider }})</span>
        </div>
        <div id="plotly-div" style="width:100%; height:450px;"></div>
        <div class="flex flex-wrap justify-center gap-4 text-xs font-semibold mt-4">
            <span class="text-emerald-600">● Existing Skill</span>
            <span class="text-amber-500">● Missing Competency</span>
            <span class="text-sky-500">● Related Bridge</span>
            <span class="text-indigo-600">● Target Career Anchor</span>
        </div>
    </div>

    <!-- AI INSIGHTS & NEXT QUEUE -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h3 class="text-base font-bold text-slate-900 mb-3">🧠 AI Skill DNA Diagnosis</h3>
            <div class="bg-slate-50 border-l-4 border-l-indigo-600 p-3.5 rounded-r-lg text-xs leading-relaxed text-slate-700 mb-4">
                {{ dna.insights.dna_summary }}
            </div>
            <div class="text-xs space-y-2">
                <div><strong>💪 Primary Strength:</strong> {{ dna.insights.primary_strength }}</div>
                <div><strong>⚡ Critical Bottleneck:</strong> <span class="text-amber-600 font-bold">{{ dna.insights.critical_gap }}</span></div>
                <div><strong>📈 Recommended Velocity:</strong> {{ dna.insights.learning_velocity_recommendation }}</div>
            </div>
        </div>

        <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h3 class="text-base font-bold text-slate-900 mb-3">🚀 Next Prioritized Skills</h3>
            <div class="space-y-2 mb-4">
                {% for n in dna.next_to_learn %}
                <div class="flex justify-between items-center bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-xs">
                    <span class="font-bold text-slate-900">{{ n }}</span>
                    <span class="badge badge-warning">Priority #{{ loop.index }}</span>
                </div>
                {% endfor %}
            </div>
            <div class="text-xs text-slate-500">
                <strong>All Missing Gaps:</strong>
                <div class="flex flex-wrap gap-1 mt-1.5">
                    {% for m in dna.missing_skills %}
                    <span class="badge badge-warning">{{ m }}</span>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>

    <script>
        const graphData = {{ graph_data_json|safe }};
        const nodes = graphData.nodes || [];
        const edges = graphData.edges || [];

        // Simple radial layout for browser
        const numNodes = nodes.length;
        const nodeX = [], nodeY = [], nodeColor = [], nodeSize = [], nodeText = [];

        nodes.forEach((n, idx) => {
            const angle = (idx / numNodes) * 2 * Math.PI;
            const r = n.type === 'target_role' ? 0 : (n.type === 'existing' ? 1.5 : (n.type === 'missing' ? 2.5 : 3.2));
            nodeX.push(r * Math.cos(angle));
            nodeY.push(r * Math.sin(angle));
            nodeColor.push(n.color);
            nodeSize.push(n.size);
            nodeText.push(n.label);
        });

        const edgeX = [], edgeY = [];
        edges.forEach(e => {
            edgeX.push(0, nodeX[1] || 1, null);
            edgeY.push(0, nodeY[1] || 1, null);
        });

        const traceEdges = { x: edgeX, y: edgeY, mode: 'lines', line: { color: '#e2e8f0', width: 1.5 }, hoverinfo: 'none' };
        const traceNodes = { x: nodeX, y: nodeY, mode: 'markers+text', text: nodeText, textposition: 'top center', marker: { color: nodeColor, size: nodeSize, line: { color: '#ffffff', width: 2 } } };

        Plotly.newPlot('plotly-div', [traceEdges, traceNodes], {
            margin: { l: 20, r: 20, t: 20, b: 20 },
            showlegend: false,
            xaxis: { showgrid: false, zeroline: false, showticklabels: false },
            yaxis: { showgrid: false, zeroline: false, showticklabels: false },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(248,250,252,0.5)'
        });
    </script>
    {% endblock %}
    """
    tmpl = BASE_LAYOUT.replace("{% block content %}{% endblock %}", content)
    return render_template_string(
        tmpl,
        page_title="Skill DNA",
        active_page="skill-dna",
        student=student,
        dna=dna,
        graph_data_json=json.dumps(dna.get("graph_data", {}))
    )

# --- ROUTE 4: CAREER MATCHING ---
@app.route("/career-matching")
def career_matching():
    sid = get_current_student_id()
    student = get_student_by_id(sid)
    skills = get_student_skills(sid)
    current_target = student["target_career"]

    orch = AgentOrchestrator()
    eval_data = orch.career_prediction_agent.evaluate_career_compatibility(skills, current_target)
    target_stats = eval_data["target_stats"]
    role_info = CAREER_ROLES.get(current_target, CAREER_ROLES["Full Stack Developer"])

    content = """
    {% extends "base" %}
    {% block content %}
    <div class="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
            <h2 class="text-2xl font-extrabold text-slate-900">🎯 Career Matching & Forecaster</h2>
            <p class="text-slate-500 text-sm mt-1">Audit compatibility across 7 roles and pivot your Career Digital Twin instantly.</p>
        </div>
        <!-- PIVOT GOAL SELECTOR -->
        <form action="/api/career/switch" method="POST" class="flex gap-2">
            <select name="new_career" class="bg-white border border-slate-300 rounded-lg px-3 py-2 text-xs font-semibold">
                {% for rname in all_roles %}
                <option value="{{ rname }}" {% if rname == student.target_career %}selected{% endif %}>{{ rname }}</option>
                {% endfor %}
            </select>
            <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs py-2 px-3 rounded-lg transition whitespace-nowrap">
                🎯 Pivot Goal
            </button>
        </form>
    </div>

    <!-- CURRENT ROLE CARD -->
    <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm mb-6">
        <div class="flex flex-col md:flex-row justify-between items-start gap-4">
            <div>
                <h3 class="text-xl font-extrabold text-slate-900">{{ role_info.icon }} {{ student.target_career }}</h3>
                <p class="text-slate-600 text-xs mt-1.5 max-w-2xl leading-relaxed">{{ role_info.description }}</p>
            </div>
            <div class="text-right">
                <div class="text-[10px] font-bold text-slate-400 uppercase">COMPATIBILITY INDEX</div>
                <div class="text-4xl font-extrabold {% if target_stats.match_percentage >= 65 %}text-emerald-600{% else %}text-amber-500{% endif %}">
                    {{ target_stats.match_percentage }}%
                </div>
                <div class="text-xs text-slate-500 mt-1">Market Demand: <strong class="text-indigo-600">{{ role_info.demand }}</strong> • Avg {{ role_info.avg_salary }}</div>
            </div>
        </div>
    </div>

    <!-- SIDE BY SIDE GAPS -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h3 class="text-base font-bold text-slate-900 mb-3">✅ Acquired Core & Advanced Skills ({{ target_stats.matched_core|length + target_stats.matched_adv|length }})</h3>
            <div class="space-y-2">
                {% for m in target_stats.matched_core %}
                <div class="flex justify-between bg-emerald-50 text-emerald-800 p-2.5 rounded-lg text-xs font-semibold">
                    <span>{{ m }}</span>
                    <span class="text-emerald-600">Core Met</span>
                </div>
                {% endfor %}
                {% for a in target_stats.matched_adv %}
                <div class="flex justify-between bg-teal-50 text-teal-800 p-2.5 rounded-lg text-xs font-semibold">
                    <span>{{ a }}</span>
                    <span class="text-teal-600">Advanced Bonus</span>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h3 class="text-base font-bold text-slate-900 mb-3">⚠️ Critical Skill Gaps to Bridge ({{ target_stats.gap_count }})</h3>
            <div class="space-y-2">
                {% for g in target_stats.missing_core %}
                <div class="flex justify-between bg-amber-50 border border-amber-200 text-amber-900 p-2.5 rounded-lg text-xs font-semibold">
                    <span>{{ g }}</span>
                    <span class="badge badge-warning">High Priority</span>
                </div>
                {% endfor %}
                {% for g in target_stats.missing_adv %}
                <div class="flex justify-between bg-slate-50 text-slate-600 p-2.5 rounded-lg text-xs">
                    <span>{{ g }}</span>
                    <span class="text-slate-400">Secondary</span>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <!-- BENCHMARK ACROSS 7 ROLES -->
    <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h3 class="text-base font-bold text-slate-900 mb-2">📊 Compatibility Across All 7 Industry Roles</h3>
        <p class="text-xs text-slate-500 mb-4">Benchmark your existing profile across the broader tech landscape.</p>
        <div class="space-y-3">
            {% for r in eval_data.all_roles_comparison %}
            <div>
                <div class="flex justify-between text-xs font-semibold mb-1">
                    <span class="text-slate-800">{{ r.role }} ({{ r.avg_salary }})</span>
                    <span class="font-bold text-indigo-600">{{ r.compatibility }}% Match</span>
                </div>
                <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div class="bg-indigo-600 h-2 rounded-full" style="width: {{ r.compatibility }}%"></div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endblock %}
    """
    tmpl = BASE_LAYOUT.replace("{% block content %}{% endblock %}", content)
    return render_template_string(
        tmpl,
        page_title="Career Matching",
        active_page="career-matching",
        student=student,
        eval_data=eval_data,
        target_stats=target_stats,
        role_info=role_info,
        all_roles=list(CAREER_ROLES.keys())
    )

# --- ROUTE 5: SIMULATOR ---
@app.route("/simulator")
def simulator():
    sid = get_current_student_id()
    student = get_student_by_id(sid)
    challenges = get_challenges_for_student(sid, role=student["target_career"])
    if not challenges:
        challenges = get_challenges_for_student(sid)

    ch_id = int(request.args.get("id", challenges[0]["id"] if challenges else 1))
    current_challenge = get_challenge_by_id(ch_id) or (challenges[0] if challenges else {})
    submissions = get_recent_submissions(sid, limit=5)

    content = """
    {% extends "base" %}
    {% block content %}
    <div class="mb-6">
        <h2 class="text-2xl font-extrabold text-slate-900">💻 AI Career Simulator & Code Proctor</h2>
        <p class="text-slate-500 text-sm mt-1">Solve practical challenges. Evaluated on logic, correctness, and production hygiene.</p>
    </div>

    <!-- CHALLENGE SELECTOR -->
    <div class="flex gap-2 mb-4 overflow-x-auto pb-2">
        {% for c in challenges %}
        <a href="/simulator?id={{ c.id }}" class="px-3.5 py-2 rounded-lg text-xs font-bold whitespace-nowrap {% if c.id == current_challenge.id %}bg-indigo-600 text-white{% else %}bg-white border border-slate-200 text-slate-700 hover:bg-slate-50{% endif %}">
            {{ c.difficulty }} • {{ c.title }}
        </a>
        {% endfor %}
    </div>

    <!-- SPEC CARD -->
    <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm mb-6">
        <div class="flex justify-between items-start mb-2">
            <h3 class="text-lg font-bold text-slate-900">📝 {{ current_challenge.title }}</h3>
            <span class="badge badge-primary">{{ current_challenge.difficulty }}</span>
        </div>
        <p class="text-slate-600 text-xs leading-relaxed mb-3">{{ current_challenge.description }}</p>
        <div class="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs text-slate-800">
            <strong>🎯 Expected Output:</strong> {{ current_challenge.expected_output }}
        </div>
    </div>

    <!-- EDITOR & ACTIONS -->
    <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm mb-6">
        <div class="flex flex-wrap justify-between items-center gap-2 mb-3">
            <h4 class="text-xs font-bold uppercase text-slate-400">Implementation Editor</h4>
            <div class="flex gap-2">
                <button type="button" onclick="loadWeakCode()" class="bg-amber-100 hover:bg-amber-200 text-amber-800 font-bold text-xs py-1.5 px-3 rounded-lg transition">
                    🧪 Simulate Weak Submission (30% Score)
                </button>
            </div>
        </div>

        <form action="/api/simulator/submit" method="POST">
            <input type="hidden" name="challenge_id" value="{{ current_challenge.id }}">
            <textarea id="code_area" name="code_submission" rows="10" required class="w-full font-mono text-xs bg-slate-900 text-emerald-400 rounded-xl p-4 leading-relaxed focus:outline-none mb-3">{{ current_challenge.starter_code }}</textarea>
            
            <div class="flex justify-between items-center">
                <input type="text" name="notes" placeholder="Notes (optional)..." class="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 w-2/3">
                <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs py-2.5 px-6 rounded-lg transition shadow-sm">
                    🚀 Submit for AI Evaluation
                </button>
            </div>
        </form>
    </div>

    <!-- SUBMISSION HISTORY -->
    <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h3 class="text-base font-bold text-slate-900 mb-3">🕒 Recent Evaluated Submissions</h3>
        {% if submissions %}
        <div class="space-y-2">
            {% for s in submissions %}
            <div class="flex justify-between items-center bg-slate-50 border border-slate-200 p-3 rounded-lg text-xs">
                <div>
                    <strong class="text-slate-900">{{ s.challenge_title }}</strong>
                    <div class="text-[10px] text-slate-400">Date: {{ s.evaluated_at[:19] }}</div>
                </div>
                <div class="text-base font-extrabold {% if s.score >= 60 %}text-emerald-600{% else %}text-rose-600{% endif %}">
                    {{ s.score }}/100
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <p class="text-xs text-slate-400">No submissions logged yet.</p>
        {% endif %}
    </div>

    <script>
        function loadWeakCode() {
            document.getElementById('code_area').value = "// Incomplete attempt\\nvar x = 1;\\nfunction checkLogin() {\\n    alert('logging in...');\\n    // TODO: implement REST auth\\n}";
        }
    </script>
    {% endblock %}
    """
    tmpl = BASE_LAYOUT.replace("{% block content %}{% endblock %}", content)
    return render_template_string(
        tmpl,
        page_title="AI Career Simulator",
        active_page="simulator",
        student=student,
        challenges=challenges,
        current_challenge=current_challenge,
        submissions=submissions
    )

# --- ROUTE 6: ROADMAP ---
@app.route("/roadmap")
def roadmap():
    sid = get_current_student_id()
    student = get_student_by_id(sid)
    items = get_roadmap(sid)
    rescues = get_active_rescue_plans(sid)

    content = """
    {% extends "base" %}
    {% block content %}
    <div class="mb-6">
        <h2 class="text-2xl font-extrabold text-slate-900">🗺️ Personalized Learning Roadmap</h2>
        <p class="text-slate-500 text-sm mt-1">Adaptive curriculum dynamically recalibrated based on your challenges and goals.</p>
    </div>

    <!-- RESCUES -->
    {% for r in rescues %}
    <div class="bg-amber-50 border border-amber-300 rounded-xl p-6 mb-6 shadow-sm">
        <div class="flex justify-between items-start mb-2">
            <h3 class="text-base font-bold text-amber-900">🚨 Active Learning Rescue Sprint: {{ r.weak_topic }}</h3>
            <span class="badge badge-warning">Score Trigger: {{ r.score_trigger }}%</span>
        </div>
        <div class="bg-white/80 p-3.5 rounded-lg border border-amber-200 text-xs text-amber-900 leading-relaxed mb-4">
            <strong>💡 Simplified Mental Model:</strong> {{ r.explanation_simple }}
        </div>
        
        <h4 class="text-xs font-bold text-amber-900 uppercase mb-2">🎥 Curated Video Tutorials & Guides</h4>
        <div class="space-y-1 text-xs mb-4">
            {% for t in r.tutorials %}
            <div>• <a href="{{ t.url }}" target="_blank" class="text-indigo-600 font-semibold underline">{{ t.title }}</a> ({{ t.platform }})</div>
            {% endfor %}
        </div>

        <form action="/api/rescue/resolve" method="POST">
            <input type="hidden" name="rescue_id" value="{{ r.id }}">
            <button type="submit" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs py-2 px-4 rounded-lg transition">
                ✅ Mark Remediated & Clear Rescue
            </button>
        </form>
    </div>
    {% endfor %}

    <!-- ROADMAP ITEMS -->
    <div class="space-y-4">
        {% for item in items %}
        <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-sm {% if item.status == 'Completed' %}border-l-4 border-l-emerald-500{% elif item.status == 'In Progress' %}border-l-4 border-l-indigo-600{% elif item.status == 'Rescue' %}border-l-4 border-l-amber-500{% endif %}">
            <div class="flex justify-between items-center mb-1">
                <span class="text-xs font-bold text-indigo-600">WEEK {{ item.week_number }} • TARGET: {{ item.skill_target }}</span>
                <span class="badge {% if item.status == 'Completed' %}badge-success{% elif item.status == 'In Progress' %}badge-primary{% else %}badge-warning{% endif %}">
                    {{ item.status }}
                </span>
            </div>
            <h3 class="text-base font-bold text-slate-900">{{ item.topic }}</h3>
            <p class="text-xs text-slate-600 mt-1 leading-relaxed">{{ item.description }}</p>

            <div class="flex flex-wrap gap-4 text-xs mt-3 p-2.5 bg-slate-50 rounded-lg">
                <div>🎓 <a href="{{ item.course_url }}" target="_blank" class="text-indigo-600 underline">{{ item.course_title }}</a></div>
                <div>📺 <a href="https://www.youtube.com/results?search_query={{ item.youtube_query|urlencode }}" target="_blank" class="text-indigo-600 underline">Search Tutorials</a></div>
                <div>📖 <a href="{{ item.doc_url }}" target="_blank" class="text-indigo-600 underline">Documentation</a></div>
            </div>

            <div class="flex justify-between items-center mt-3 pt-3 border-t border-slate-100">
                <div class="text-xs text-slate-700"><strong>🛠️ Practical Task:</strong> {{ item.practical_task }}</div>
                <form action="/api/roadmap/update" method="POST">
                    <input type="hidden" name="item_id" value="{{ item.id }}">
                    {% if item.status != 'Completed' %}
                    <input type="hidden" name="status" value="Completed">
                    <button type="submit" class="bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs py-1.5 px-3 rounded-lg transition">
                        ✓ Mark Completed
                    </button>
                    {% else %}
                    <input type="hidden" name="status" value="In Progress">
                    <button type="submit" class="text-xs text-slate-400 hover:text-slate-600">Reopen</button>
                    {% endif %}
                </form>
            </div>
        </div>
        {% endfor %}
    </div>
    {% endblock %}
    """
    tmpl = BASE_LAYOUT.replace("{% block content %}{% endblock %}", content)
    return render_template_string(tmpl, page_title="Learning Roadmap", active_page="roadmap", student=student, items=items, rescues=rescues)

# --- ROUTE 7: PROGRESS ---
@app.route("/progress")
def progress():
    sid = get_current_student_id()
    student = get_student_by_id(sid)
    skills = get_student_skills(sid)
    projects = get_projects(sid)
    certs = get_certifications(sid)
    submissions = get_recent_submissions(sid)
    readiness = get_latest_readiness(sid)
    history = get_readiness_history(sid)

    content = """
    {% extends "base" %}
    {% block content %}
    <div class="mb-6">
        <h2 class="text-2xl font-extrabold text-slate-900">📈 Career Readiness & Progress Tracking</h2>
        <p class="text-slate-500 text-sm mt-1">Multi-pillar mathematical evaluation of your hireability index.</p>
    </div>

    <!-- GAUGE & PILLARS -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- CIRCULAR GAUGE -->
        <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm text-center">
            <h3 class="text-base font-bold text-slate-900 mb-1">🎯 Career Readiness Index</h3>
            <span class="badge badge-primary">{{ readiness.overall_score }}% • Practitioner</span>
            
            <div class="my-6">
                <div class="text-6xl font-extrabold text-indigo-600">{{ readiness.overall_score }}%</div>
                <div class="text-xs text-slate-400 mt-1">Platform Performance Metric</div>
            </div>

            <p class="text-[11px] text-slate-400 leading-relaxed max-w-sm mx-auto">
                {{ readiness.explanation or 'Transparency Note: Score reflects verified platform performance and does not guarantee formal employment.' }}
            </p>
        </div>

        <!-- 4 PILLARS -->
        <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h3 class="text-base font-bold text-slate-900 mb-4">⚖️ Transparent Scoring Formula</h3>
            
            <div class="space-y-4">
                <div>
                    <div class="flex justify-between text-xs font-semibold mb-1">
                        <span>Technical Skills (35%)</span>
                        <span class="text-indigo-600">{{ readiness.tech_score }}/100</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div class="bg-indigo-600 h-2 rounded-full" style="width: {{ readiness.tech_score }}%"></div>
                    </div>
                </div>
                <div>
                    <div class="flex justify-between text-xs font-semibold mb-1">
                        <span>Challenges & Simulator (30%)</span>
                        <span class="text-sky-500">{{ readiness.challenge_score }}/100</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div class="bg-sky-500 h-2 rounded-full" style="width: {{ readiness.challenge_score }}%"></div>
                    </div>
                </div>
                <div>
                    <div class="flex justify-between text-xs font-semibold mb-1">
                        <span>Portfolio Projects (20%)</span>
                        <span class="text-emerald-500">{{ readiness.project_score }}/100</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div class="bg-emerald-500 h-2 rounded-full" style="width: {{ readiness.project_score }}%"></div>
                    </div>
                </div>
                <div>
                    <div class="flex justify-between text-xs font-semibold mb-1">
                        <span>Problem-Solving / Quizzes (15%)</span>
                        <span class="text-amber-500">{{ readiness.quiz_score }}/100</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div class="bg-amber-500 h-2 rounded-full" style="width: {{ readiness.quiz_score }}%"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- QUIZ CHECK -->
    <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h3 class="text-base font-bold text-slate-900 mb-2">🧩 Problem-Solving Knowledge Check</h3>
        <p class="text-xs text-slate-500 mb-4">Complete quick quizzes to raise your Problem-Solving pillar.</p>
        
        <form action="/api/quiz/submit" method="POST" class="space-y-3">
            <div class="text-xs font-semibold text-slate-800">What is the primary difference between `var`, `let`, and `const` in ECMAScript?</div>
            <label class="flex items-center gap-2 text-xs text-slate-700">
                <input type="radio" name="answer" value="B" required>
                <span>B) 'var' is function-scoped; 'let' and 'const' are block-scoped and temporal dead-zoned.</span>
            </label>
            <label class="flex items-center gap-2 text-xs text-slate-700">
                <input type="radio" name="answer" value="A">
                <span>A) 'var' is block-scoped while 'let' and 'const' are global.</span>
            </label>
            <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs py-2 px-4 rounded-lg transition mt-2">
                Submit & Verify
            </button>
        </form>
    </div>
    {% endblock %}
    """
    tmpl = BASE_LAYOUT.replace("{% block content %}{% endblock %}", content)
    return render_template_string(tmpl, page_title="Progress Tracking", active_page="progress", student=student, readiness=readiness, history=history)

# --- ROUTE 8: MENTOR ---
@app.route("/mentor")
def mentor():
    sid = get_current_student_id()
    student = get_student_by_id(sid)
    history = get_chat_history(sid)

    content = """
    {% extends "base" %}
    {% block content %}
    <div class="mb-6">
        <h2 class="text-2xl font-extrabold text-slate-900">🤖 AI Career Mentor</h2>
        <p class="text-slate-500 text-sm mt-1">Senior engineering mentor grounded in your real-time Career Digital Twin.</p>
    </div>

    <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col h-[520px]">
        <!-- CHAT STREAM -->
        <div class="flex-1 overflow-y-auto space-y-3 mb-4 pr-2">
            {% if history %}
            {% for c in history %}
            <div class="flex {% if c.role == 'user' %}justify-end{% else %}justify-start{% endif %}">
                <div class="max-w-xl text-xs rounded-xl p-3.5 {% if c.role == 'user' %}bg-indigo-600 text-white{% else %}bg-slate-100 text-slate-800 leading-relaxed{% endif %}">
                    <strong>{% if c.role == 'user' %}You{% else %}🤖 Mentor{% endif %}:</strong><br>
                    <div class="mt-1 whitespace-pre-wrap">{{ c.message }}</div>
                </div>
            </div>
            {% endfor %}
            {% else %}
            <div class="text-center py-20 text-slate-400 text-xs">
                Ask your AI Mentor anything about full-stack architecture, challenges, or interview advice!
            </div>
            {% endif %}
        </div>

        <!-- QUICK PROMPTS -->
        <div class="flex gap-2 mb-3 overflow-x-auto pb-1 text-xs">
            <button type="button" onclick="setQuery('Explain JavaScript Event Loop (ELI5)')" class="bg-slate-100 hover:bg-slate-200 text-slate-700 px-2.5 py-1.5 rounded-lg whitespace-nowrap">
                Explain JS Event Loop (ELI5)
            </button>
            <button type="button" onclick="setQuery('What portfolio project should I build next?')" class="bg-slate-100 hover:bg-slate-200 text-slate-700 px-2.5 py-1.5 rounded-lg whitespace-nowrap">
                What project should I build?
            </button>
        </div>

        <!-- INPUT FORM -->
        <form action="/api/mentor/chat" method="POST" class="flex gap-2">
            <input type="text" id="query_input" name="message" required placeholder="Type your question..." class="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-3.5 py-2.5 text-xs focus:outline-none">
            <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs py-2.5 px-5 rounded-lg transition">
                Send
            </button>
        </form>
    </div>

    <script>
        function setQuery(q) {
            document.getElementById('query_input').value = q;
        }
    </script>
    {% endblock %}
    """
    tmpl = BASE_LAYOUT.replace("{% block content %}{% endblock %}", content)
    return render_template_string(tmpl, page_title="AI Mentor", active_page="mentor", student=student, history=history)

# --- ROUTE 9: SETTINGS ---
@app.route("/settings")
def settings():
    sid = get_current_student_id()
    student = get_student_by_id(sid)

    content = """
    {% extends "base" %}
    {% block content %}
    <div class="mb-6">
        <h2 class="text-2xl font-extrabold text-slate-900">⚙️ Settings & System Diagnostics</h2>
        <p class="text-slate-500 text-sm mt-1">Inspect multi-agent architecture, AI keys, and reset demo states.</p>
    </div>

    <div class="space-y-6">
        <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h3 class="text-base font-bold text-slate-900 mb-2">🔑 Google Gemini API Configuration</h3>
            <p class="text-xs text-slate-500 mb-4">Provide an optional Gemini API key to enable live LLM synthesis, or run offline via high-fidelity Demo Mode heuristics.</p>
            <form action="/api/settings/apikey" method="POST" class="flex gap-2 max-w-md">
                <input type="password" name="gemini_key" placeholder="AIzaSy..." class="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs">
                <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs py-2 px-4 rounded-lg transition">Save Key</button>
            </form>
        </div>

        <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h3 class="text-base font-bold text-slate-900 mb-2">🔄 Reset Demo Student</h3>
            <p class="text-xs text-slate-500 mb-4">Restores <strong>M. Sudharshan</strong> (Full Stack Developer, Python 3/5, SQL 3/5, HTML5 2/5).</p>
            <form action="/api/settings/reset" method="POST">
                <button type="submit" class="bg-rose-50 border border-rose-200 hover:bg-rose-100 text-rose-700 font-bold text-xs py-2 px-4 rounded-lg transition">
                    ⚠️ Reset to Baseline State
                </button>
            </form>
        </div>
    </div>
    {% endblock %}
    """
    tmpl = BASE_LAYOUT.replace("{% block content %}{% endblock %}", content)
    return render_template_string(tmpl, page_title="Settings", active_page="settings", student=student)

# --- POST ACTION HANDLERS ---
@app.route("/api/simulator/submit", methods=["POST"])
def submit_challenge():
    sid = get_current_student_id()
    ch_id = int(request.form.get("challenge_id", 1))
    code = request.form.get("code_submission", "")
    notes = request.form.get("notes", "")

    ch = get_challenge_by_id(ch_id)
    if ch:
        orch = AgentOrchestrator()
        orch.evaluate_and_orchestrate_submission(sid, ch, code, notes)

    return redirect(url_for("simulator", id=ch_id))

@app.route("/api/career/switch", methods=["POST"])
def switch_career():
    sid = get_current_student_id()
    new_c = request.form.get("new_career")
    if new_c:
        orch = AgentOrchestrator()
        orch.on_career_goal_changed(sid, new_c)
    return redirect(url_for("career_matching"))

@app.route("/api/skills/add", methods=["POST"])
def add_skill_action():
    sid = get_current_student_id()
    name = request.form.get("skill_name", "").strip()
    prof = int(request.form.get("proficiency", 3))
    if name:
        add_or_update_skill(sid, name, "Languages & Frameworks", prof)
    return redirect(url_for("profile"))

@app.route("/api/skills/delete", methods=["POST"])
def delete_skill_action():
    sid = get_current_student_id()
    sk_id = int(request.form.get("skill_id", 0))
    if sk_id:
        delete_skill(sk_id, sid)
    return redirect(url_for("profile"))

@app.route("/api/roadmap/update", methods=["POST"])
def update_roadmap_action():
    sid = get_current_student_id()
    item_id = int(request.form.get("item_id", 0))
    status = request.form.get("status", "Completed")
    if item_id:
        update_roadmap_status(item_id, sid, status)
    return redirect(url_for("roadmap"))

@app.route("/api/rescue/resolve", methods=["POST"])
def resolve_rescue_action():
    sid = get_current_student_id()
    r_id = int(request.form.get("rescue_id", 0))
    if r_id:
        resolve_rescue_plan(r_id, sid)
    return redirect(url_for("roadmap"))

@app.route("/api/mentor/chat", methods=["POST"])
def mentor_chat_action():
    sid = get_current_student_id()
    msg = request.form.get("message", "").strip()
    if msg:
        save_chat_message(sid, "user", msg)
        student = get_student_by_id(sid)
        skills = [s["skill_name"] for s in get_student_skills(sid)]
        from utils.helpers import call_gemini
        prompt = f"You are a career mentor AI. The student targets '{student['target_career']}' and knows {', '.join(skills)}. Answer: {msg}"
        ai_reply, is_real = call_gemini(prompt)
        if is_real and ai_reply:
            reply = ai_reply
        else:
            reply = f"Great question! As someone targeting **{student['target_career']}** with skills in {', '.join(skills)}, I'd recommend focusing on your skill gaps first. Check your Skill DNA and Learning Roadmap for a personalized plan. Keep practicing and building projects — consistency is key! 🚀"
        save_chat_message(sid, "assistant", reply)
    return redirect(url_for("mentor"))

@app.route("/api/quiz/submit", methods=["POST"])
def quiz_submit_action():
    sid = get_current_student_id()
    ans = request.form.get("answer")
    if ans == "B":
        readiness = get_latest_readiness(sid)
        if readiness:
            save_readiness_score(
                sid,
                min(100, readiness["overall_score"] + 2),
                readiness["tech_score"],
                readiness["challenge_score"],
                readiness["project_score"],
                min(100, readiness["quiz_score"] + 10),
                "Knowledge Check verified: JavaScript scoping and temporal dead zone."
            )
    return redirect(url_for("progress"))

@app.route("/api/settings/reset", methods=["POST"])
def settings_reset_action():
    sid = get_current_student_id()
    reset_student_to_demo(sid)
    return redirect(url_for("dashboard"))

@app.route("/api/settings/apikey", methods=["POST"])
def settings_apikey_action():
    key = request.form.get("gemini_key", "").strip()
    if key:
        os.environ["GEMINI_API_KEY"] = key
    return redirect(url_for("settings"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
