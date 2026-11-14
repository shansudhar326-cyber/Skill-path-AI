# SkillPath AI – AI-Powered Career Digital Twin 🧬

**SkillPath AI** is an advanced, production-grade personalized learning and career guidance web platform built with a multi-agent AI architecture. It introduces the concept of a **Career Digital Twin**—a live, virtual representation of a student's technical abilities, missing competencies, practical coding skills, and career readiness.

Unlike traditional static learning platforms, SkillPath AI leverages **five specialized AI agents** coordinated by a central orchestrator to evaluate submissions, simplify stumbling blocks, formulate emergency rescue modules, and adapt curriculum roadmaps in real time.

---

## 🌟 Key Features

1. **Career Digital Twin Identity**:
   - Comprehensive student skill portfolio tracking technical depth (1–5 scale), verified credentials, and portfolio projects.
   - Pre-seeded with the demonstration scenario: **Alex Chen**, an aspiring **Full Stack Developer** with foundational knowledge in **Python**, **SQL**, and **HTML5**.

2. **Skill DNA Visual Genome**:
   - Interactive **Plotly topological network graph** mapping existing skills (Green), missing target skills (Amber), related/bridge skills (Sky Blue), and target roles (Purple).
   - Graph prerequisite analysis identifying the exact next 3–4 high-leverage skills to learn.
   - Cognitive AI diagnosis analyzing strengths and critical bottlenecks.

3. **Career Matching & Role Forecasting**:
   - Compares profile against **7 industry roles**: Full Stack Developer, Frontend Developer, Backend Developer, Data Analyst, Data Scientist, AI/ML Engineer, and Cybersecurity Analyst.
   - Calculates dynamic role compatibility percentages (0–100%).
   - One-click career pivot engine that recalculates skill gaps and generates completely new roadmaps.

4. **AI Career Simulator & Practical Code Proctor**:
   - Real-world software engineering challenges (REST API auth, React task components, secure SQL queries, responsive views).
   - Strict evaluation based on **Correctness**, **Logic & Architecture**, and **Practical Production Standards**.
   - Built-in one-click test helpers to simulate both production exemplar solutions and weak attempts (e.g. 30% score in JavaScript).

5. **Adaptive Learning Rescue**:
   - Automatically intervenes when an assessment or challenge score is below 60%.
   - Explains complex concepts in simple, intuitive language using memorable real-world analogies (ELI5).
   - Recommends curated video tutorials and scaffolded practice exercises.
   - Dynamically injects a **Rescue Sprint** into the student's roadmap, requiring foundational mastery before allowing advancement into downstream frameworks (e.g., solidifying JavaScript before React).

6. **Transparent Career Readiness Index**:
   - Real-time circular progress gauge calculated from 4 transparent pillars:
     - **Technical Skills Coverage (35%)**
     - **Practical Challenges / Simulator (30%)**
     - **Portfolio Projects & Complexity (20%)**
     - **Problem-Solving / Quizzes (15%)**
   - Explicit disclaimer explaining that the score reflects practical platform readiness without guaranteeing employment.

7. **AI Career Mentor**:
   - Interactive conversational co-pilot grounded in the student's Career Digital Twin context.
   - Answers programming queries, explains difficult concepts, recommends portfolio projects, and offers interview coaching.

---

## 🤖 Multi-Agent AI Architecture

SkillPath AI is powered by five independent agent modules communicating through a **Central Agent Orchestrator**:

```
                              ┌────────────────────────┐
                              │ Central Orchestrator   │
                              │ (State & Event Sync)   │
                              └───────────┬────────────┘
                                          │
        ┌───────────────────┬─────────────┼─────────────┬────────────────────┐
        │                   │             │             │                    │
┌───────▼──────────┐ ┌──────▼──────┐ ┌────▼──────┐ ┌────▼──────────┐ ┌───────▼──────────┐
│  Skill DNA       │ │ Career      │ │ Challenge │ │ Learning      │ │ Career           │
│  Agent           │ │ Prediction  │ │ Agent     │ │ Rescue Agent  │ │ Readiness Agent  │
│  (Topology/Gaps) │ │ (Demand/7)  │ │ (Code/Rub)│ │ (ELI5/Sprint) │ │ (4-Pillar Score) │
└──────────────────┘ └─────────────┘ └───────────┘ └───────────────┘ └──────────────────┘
```

1. **Skill DNA Agent** (`agents/skill_dna_agent.py`): Computes graph adjacency, categorizes active vs missing skills, and visualizes prerequisite relationships.
2. **Career Prediction Agent** (`agents/career_prediction_agent.py`): Benchmarks against all 7 industry roles and identifies emerging high-demand skills.
3. **Challenge Agent** (`agents/challenge_agent.py`): Generates coding scenarios and grades submissions across correctness, logic, and production hygiene.
4. **Learning Rescue Agent** (`agents/learning_rescue_agent.py`): Triggers on low scores (<60%), simplifies difficult mental models, and designs remediation sprints.
5. **Career Readiness Agent** (`agents/career_readiness_agent.py`): Synthesizes multi-pillar performance into an objective, transparent readiness score.
6. **Central Orchestrator** (`agents/orchestrator.py`): Directs agent workflows, propagates state changes, and records audit logs to SQLite.

---

## 💻 Technology Stack

- **Frontend**: Streamlit 1.50+
- **Backend**: Python 3.9+
- **Database**: SQLite with persistent relational schema
- **AI Integration**: Google Gemini API (`gemini-1.5-flash`) with automatic, high-fidelity rule-based demo fallback
- **Data Analysis**: Pandas, NetworkX
- **Charts & Graphs**: Plotly (circular progress gauge, bar charts, spring-layout network graph)
- **Styling**: Modern SaaS Custom CSS (Indigo/Blue palette, cards, KPI metrics, responsive sidebar)

---

## 📁 Project Folder Structure

```
SkillPath_AI/
├── app.py                      # Application entrypoint & navigation router
├── config.py                   # Role definitions, taxonomy, skill relations
├── requirements.txt            # Python dependencies
├── skillpath.db                # SQLite database (auto-created on first run)
├── database/
│   ├── __init__.py
│   └── db.py                   # Relational tables, CRUD operations, demo seeder
├── agents/
│   ├── __init__.py
│   ├── skill_dna_agent.py      # Skill graph & topology agent
│   ├── career_prediction_agent.py # Role compatibility forecaster
│   ├── challenge_agent.py      # Practical code evaluator
│   ├── learning_rescue_agent.py # Adaptive remediation specialist
│   ├── career_readiness_agent.py # 4-pillar readiness auditor
│   └── orchestrator.py         # Multi-agent central coordinator
├── modules/
│   ├── __init__.py
│   ├── dashboard.py            # Overview dashboard & KPI cards
│   ├── profile.py              # Student identity, skills, projects, certs
│   ├── skill_analysis.py       # Interactive Skill DNA network graph
│   ├── career_matching.py      # Career benchmark & gap comparison
│   ├── simulator.py            # Practical coding simulator & evaluator
│   ├── roadmap.py              # Personalized roadmap & rescue center
│   ├── progress.py             # Readiness gauge & knowledge check
│   ├── mentor.py               # AI Career Mentor chatbot
│   └── settings.py             # Gemini API key & demo reset
├── utils/
│   ├── __init__.py
│   └── helpers.py              # Gemini caller, JSON cleaner, math helpers
├── assets/
│   └── style.css               # Clean modern SaaS styling
└── README.md                   # Documentation & setup guide
```

---

## 🚀 Installation & Setup Instructions

### 1. Prerequisites
- Python 3.9 or higher installed.

### 2. Create and Activate a Virtual Environment
```bash
# Navigate to the project directory
cd SkillPath_AI

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Google Gemini API Key (Optional)
The application works in two modes:
1. **Google Gemini Live Mode**: Powered by `gemini-1.5-flash`.
2. **Demo Mode (Heuristics)**: Fully functional offline rule-based mode with rich responses and complete multi-agent workflows.

To enable live Gemini AI:
```bash
# Option A: Environment variable
export GEMINI_API_KEY="AIzaSy..."

# Option B: In-App UI
# Navigate to 'Settings' in the sidebar and enter your key in the secure input field.
```

### 5. Launch the Application
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🧪 Demonstration & Testing Walk-Through

### Scenario 1: Initial Baseline Digital Twin
1. Log in with the pre-seeded demo user:
   - **Username**: `alex_chen`
   - **Password**: `demo123`
2. Notice Alex's baseline profile:
   - Target Role: **Full Stack Developer**
   - Active Skills: **Python (3/5), SQL (3/5), HTML5 (2/5)**
3. Navigate to **Skill DNA**:
   - See the interactive network graph with Green nodes for existing skills and Amber nodes for missing skills (`CSS3`, `JavaScript`, `React`, `Node.js`, `Express.js`).
   - Notice the AI diagnosis highlighting Python/SQL as the backend strength and JavaScript as the critical bottleneck.

### Scenario 2: Adaptive Learning Rescue (JavaScript 30% Score)
1. Go to **AI Career Simulator**.
2. Select the challenge: *"Create a Responsive Navigation & Login View"* or *"Build a Secure REST API"*.
3. Click the test button: **🧪 Simulate Weak Submission (30% Score)**.
4. Click **🚀 Submit Solution for AI Evaluation**.
5. Observe the Challenge Agent evaluate the code with a **30/100 score**.
6. Notice the immediate alert: **🚨 Adaptive Learning Rescue Triggered!**
7. Navigate to **Learning Roadmap**:
   - Observe the new **Rescue Sprint Module** injected at the top.
   - Review the simplified ELI5 explanation of the JavaScript event loop and scoping.
   - Check the curated tutorials and practice exercises.
   - Click **✅ Mark Remediated** once review is complete.

### Scenario 3: Career Goal Pivot to Data Analyst
1. Go to **Career Matching**.
2. From the dropdown, select **Data Analyst**.
3. Notice that with Python and SQL, Alex's compatibility immediately jumps to **75%+**!
4. Click **🎯 Set Data Analyst as Active Goal**.
5. The orchestrator triggers:
   - Re-runs the Skill DNA Agent for Data Analyst.
   - Replaces the Full Stack roadmap with a tailored **5-Week Data Analyst Roadmap** (Advanced SQL, Pandas, Plotly Dashboards, Statistics & A/B Testing, Tableau).
   - Recalculates the Career Readiness Score.

### Scenario 4: AI Career Mentor
1. Go to **AI Mentor**.
2. Click any of the quick prompt pills (e.g. *"Explain JavaScript Event Loop (ELI5)"* or *"What project should I build next?"*).
3. Experience conversational guidance that factors in Alex's current active skills and target career.

---

## 🛡️ License
Designed and developed for academic and developer excellence. Open-source under the MIT License.
