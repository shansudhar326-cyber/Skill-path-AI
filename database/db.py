"""
SQLite Database Layer for SkillPath AI
Manages students, skills, roadmaps, challenges, rescue plans, readiness scores, and agent logs.
"""

import sqlite3
import json
import os
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skillpath.db")

def get_connection():
    """Returns a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    """Simple SHA-256 hashing for student accounts."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    """Initializes all database tables with appropriate schemas and foreign keys."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        target_career TEXT NOT NULL,
        bio TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        category TEXT NOT NULL,
        proficiency_level INTEGER NOT NULL CHECK (proficiency_level BETWEEN 1 AND 5),
        is_existing INTEGER NOT NULL DEFAULT 1,
        verified INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS certifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        issuing_org TEXT NOT NULL,
        issue_date TEXT,
        credential_url TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        tech_stack TEXT NOT NULL,
        github_url TEXT,
        live_url TEXT,
        complexity TEXT DEFAULT 'Intermediate',
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS roadmap_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        week_number INTEGER NOT NULL,
        topic TEXT NOT NULL,
        description TEXT,
        skill_target TEXT NOT NULL,
        course_title TEXT,
        course_url TEXT,
        youtube_query TEXT,
        doc_url TEXT,
        practical_task TEXT,
        status TEXT NOT NULL DEFAULT 'Pending', -- 'Pending', 'In Progress', 'Completed', 'Rescue'
        created_at TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS challenges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        career_role TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        difficulty TEXT NOT NULL, -- 'Beginner', 'Intermediate', 'Advanced'
        starter_code TEXT,
        expected_output TEXT,
        rubrics_json TEXT,
        status TEXT NOT NULL DEFAULT 'Assigned'
    );

    CREATE TABLE IF NOT EXISTS challenge_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        challenge_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        code_submission TEXT NOT NULL,
        notes TEXT,
        score INTEGER NOT NULL,
        feedback TEXT,
        logic_score INTEGER,
        practical_score INTEGER,
        correctness_score INTEGER,
        evaluated_at TEXT NOT NULL,
        FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS rescue_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        weak_topic TEXT NOT NULL,
        score_trigger INTEGER NOT NULL,
        explanation_simple TEXT NOT NULL,
        tutorials_json TEXT NOT NULL,
        practice_questions_json TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active', -- 'Active', 'Resolved'
        created_at TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS readiness_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        overall_score INTEGER NOT NULL,
        tech_score INTEGER NOT NULL,
        challenge_score INTEGER NOT NULL,
        project_score INTEGER NOT NULL,
        quiz_score INTEGER NOT NULL,
        calculated_at TEXT NOT NULL,
        explanation TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS mentor_chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        role TEXT NOT NULL, -- 'user' or 'assistant'
        message TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS agent_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        agent_name TEXT NOT NULL,
        action TEXT NOT NULL,
        output_summary TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

def seed_demo_student():
    """
    Seeds the standard demo student (M. Sudharshan) matching the specification:
    - Username: M.Sudharshan
    - Password: sudharsh390
    - Target career: Full Stack Developer
    - Existing skills: Python (Level 3), SQL (Level 3), HTML5 (Level 2)
    - Missing skills: CSS3, JavaScript, React, Node.js, Express.js
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM students WHERE username = 'M.Sudharshan'")
    existing = cursor.fetchone()

    if not existing:
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO students (username, password_hash, full_name, email, target_career, bio, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            'M.Sudharshan',
            hash_password('sudharsh390'),
            'M. Sudharshan',
            'm.sudharshan@student.skillpath.ai',
            'Full Stack Developer',
            'Aspiring full stack web engineer transitioning from script automation into high-performance web applications.',
            now
        ))
        student_id = cursor.lastrowid
        conn.commit()
        conn.close()

        _seed_student_data(student_id)
    else:
        conn.close()

# --- Auth and Profile helpers ---

def create_student(username, password, full_name, email, target_career, bio=""):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    try:
        cursor.execute("""
            INSERT INTO students (username, password_hash, full_name, email, target_career, bio, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username.strip(), hash_password(password), full_name.strip(), email.strip(), target_career, bio, now))
        student_id = cursor.lastrowid
        conn.commit()
        return student_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def authenticate_student(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM students WHERE username = ? AND password_hash = ?
    """, (username.strip(), hash_password(password)))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_student_by_id(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_student_profile(student_id, full_name, bio, target_career):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE students
        SET full_name = ?, bio = ?, target_career = ?
        WHERE id = ?
    """, (full_name, bio, target_career, student_id))
    conn.commit()
    conn.close()

# --- Skills Management ---

def get_student_skills(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM skills WHERE student_id = ? ORDER BY is_existing DESC, proficiency_level DESC", (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_or_update_skill(student_id, skill_name, category, proficiency_level, is_existing=1):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        SELECT id FROM skills WHERE student_id = ? AND LOWER(skill_name) = LOWER(?)
    """, (student_id, skill_name.strip()))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE skills
            SET category = ?, proficiency_level = ?, is_existing = ?, updated_at = ?
            WHERE id = ?
        """, (category, proficiency_level, is_existing, now, existing['id']))
    else:
        cursor.execute("""
            INSERT INTO skills (student_id, skill_name, category, proficiency_level, is_existing, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (student_id, skill_name.strip(), category, proficiency_level, is_existing, now))
    conn.commit()
    conn.close()

def delete_skill(skill_id, student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM skills WHERE id = ? AND student_id = ?", (skill_id, student_id))
    conn.commit()
    conn.close()

# --- Projects & Certifications ---

def get_projects(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE student_id = ? ORDER BY id DESC", (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_project(student_id, title, description, tech_stack, github_url="", live_url="", complexity="Intermediate"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO projects (student_id, title, description, tech_stack, github_url, live_url, complexity)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (student_id, title, description, tech_stack, github_url, live_url, complexity))
    conn.commit()
    conn.close()

def delete_project(project_id, student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ? AND student_id = ?", (project_id, student_id))
    conn.commit()
    conn.close()

def get_certifications(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM certifications WHERE student_id = ? ORDER BY id DESC", (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_certification(student_id, title, issuing_org, issue_date="", credential_url=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO certifications (student_id, title, issuing_org, issue_date, credential_url)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, title, issuing_org, issue_date, credential_url))
    conn.commit()
    conn.close()

# --- Roadmap Management ---

def get_roadmap(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM roadmap_items WHERE student_id = ? ORDER BY week_number ASC, id ASC", (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def clear_and_set_roadmap(student_id, items):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("DELETE FROM roadmap_items WHERE student_id = ?", (student_id,))
    for item in items:
        cursor.execute("""
            INSERT INTO roadmap_items (student_id, week_number, topic, description, skill_target, course_title, course_url, youtube_query, doc_url, practical_task, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            item.get('week_number', 1),
            item.get('topic', 'Topic'),
            item.get('description', ''),
            item.get('skill_target', ''),
            item.get('course_title', ''),
            item.get('course_url', ''),
            item.get('youtube_query', ''),
            item.get('doc_url', ''),
            item.get('practical_task', ''),
            item.get('status', 'Pending'),
            now
        ))
    conn.commit()
    conn.close()

def update_roadmap_status(item_id, student_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE roadmap_items SET status = ? WHERE id = ? AND student_id = ?
    """, (status, item_id, student_id))
    conn.commit()
    conn.close()

def prepend_rescue_module(student_id, rescue_item):
    """Inserts a high-priority rescue module at week 1 and shifts or marks roadmap."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO roadmap_items (student_id, week_number, topic, description, skill_target, course_title, course_url, youtube_query, doc_url, practical_task, status, created_at)
        VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?, ?, 'Rescue', ?)
    """, (
        student_id,
        rescue_item['topic'],
        rescue_item['description'],
        rescue_item['skill_target'],
        rescue_item.get('course_title', 'Rescue Foundations'),
        rescue_item.get('course_url', 'https://developer.mozilla.org/'),
        rescue_item.get('youtube_query', rescue_item['topic'] + ' beginner tutorial'),
        rescue_item.get('doc_url', 'https://developer.mozilla.org/'),
        rescue_item.get('practical_task', 'Complete targeted recovery exercises'),
        now
    ))
    conn.commit()
    conn.close()

# --- Challenges & Submissions ---

def get_challenges_for_student(student_id, role=None):
    conn = get_connection()
    cursor = conn.cursor()
    if role:
        cursor.execute("SELECT * FROM challenges WHERE (student_id = ? OR student_id IS NULL) AND career_role = ? ORDER BY id ASC", (student_id, role))
    else:
        cursor.execute("SELECT * FROM challenges WHERE (student_id = ? OR student_id IS NULL) ORDER BY id ASC", (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_challenge_by_id(challenge_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM challenges WHERE id = ?", (challenge_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def record_challenge_submission(challenge_id, student_id, code_submission, notes, evaluation):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO challenge_submissions (challenge_id, student_id, code_submission, notes, score, feedback, logic_score, practical_score, correctness_score, evaluated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        challenge_id,
        student_id,
        code_submission,
        notes,
        evaluation.get('score', 0),
        evaluation.get('feedback', ''),
        evaluation.get('logic_score', 0),
        evaluation.get('practical_score', 0),
        evaluation.get('correctness_score', 0),
        now
    ))
    submission_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return submission_id

def get_recent_submissions(student_id, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cs.*, c.title as challenge_title, c.difficulty, c.career_role
        FROM challenge_submissions cs
        JOIN challenges c ON cs.challenge_id = c.id
        WHERE cs.student_id = ?
        ORDER BY cs.id DESC
        LIMIT ?
    """, (student_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- Rescue Plans ---

def save_rescue_plan(student_id, weak_topic, score_trigger, explanation, tutorials, practice_questions):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO rescue_plans (student_id, weak_topic, score_trigger, explanation_simple, tutorials_json, practice_questions_json, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 'Active', ?)
    """, (
        student_id,
        weak_topic,
        score_trigger,
        explanation,
        json.dumps(tutorials),
        json.dumps(practice_questions),
        now
    ))
    rescue_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rescue_id

def get_active_rescue_plans(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rescue_plans WHERE student_id = ? AND status = 'Active' ORDER BY id DESC", (student_id,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d['tutorials'] = json.loads(d['tutorials_json'])
        d['practice_questions'] = json.loads(d['practice_questions_json'])
        result.append(d)
    return result

def resolve_rescue_plan(rescue_id, student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE rescue_plans SET status = 'Resolved' WHERE id = ? AND student_id = ?", (rescue_id, student_id))
    conn.commit()
    conn.close()

# --- Readiness History ---

def save_readiness_score(student_id, overall, tech, challenge, project, quiz, explanation):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO readiness_history (student_id, overall_score, tech_score, challenge_score, project_score, quiz_score, calculated_at, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (student_id, overall, tech, challenge, project, quiz, now, explanation))
    conn.commit()
    conn.close()

def get_latest_readiness(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM readiness_history WHERE student_id = ? ORDER BY id DESC LIMIT 1", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_readiness_history(student_id, limit=20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM readiness_history WHERE student_id = ? ORDER BY id ASC LIMIT ?", (student_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- Mentor Chats ---

def save_chat_message(student_id, role, message):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO mentor_chats (student_id, role, message, timestamp)
        VALUES (?, ?, ?, ?)
    """, (student_id, role, message, now))
    conn.commit()
    conn.close()

def get_chat_history(student_id, limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mentor_chats WHERE student_id = ? ORDER BY id ASC LIMIT ?", (student_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def clear_chat_history(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mentor_chats WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()

# --- Agent Activity Logs ---

def log_agent_action(student_id, agent_name, action, output_summary):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO agent_logs (student_id, agent_name, action, output_summary, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, agent_name, action, output_summary, now))
    conn.commit()
    conn.close()

def get_agent_logs(student_id, limit=25):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agent_logs WHERE student_id = ? ORDER BY id DESC LIMIT ?", (student_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- Resetting Demo State ---

def reset_student_to_demo(student_id=None):
    """Resets the demo student M. Sudharshan to initial baseline state."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Locate or determine target student_id
    if student_id:
        sid = student_id
    else:
        cursor.execute("SELECT id FROM students WHERE username = 'M.Sudharshan'")
        row = cursor.fetchone()
        sid = row["id"] if row else None

    if sid:
        cursor.execute("DELETE FROM skills WHERE student_id = ?", (sid,))
        cursor.execute("DELETE FROM certifications WHERE student_id = ?", (sid,))
        cursor.execute("DELETE FROM projects WHERE student_id = ?", (sid,))
        cursor.execute("DELETE FROM roadmap_items WHERE student_id = ?", (sid,))
        cursor.execute("DELETE FROM challenge_submissions WHERE student_id = ?", (sid,))
        cursor.execute("DELETE FROM rescue_plans WHERE student_id = ?", (sid,))
        cursor.execute("DELETE FROM readiness_history WHERE student_id = ?", (sid,))
        cursor.execute("DELETE FROM mentor_chats WHERE student_id = ?", (sid,))
        cursor.execute("DELETE FROM agent_logs WHERE student_id = ?", (sid,))
        
        # Reset student details
        cursor.execute("""
            UPDATE students 
            SET username = 'M.Sudharshan',
                password_hash = ?,
                full_name = 'M. Sudharshan',
                email = 'm.sudharshan@student.skillpath.ai',
                target_career = 'Full Stack Developer',
                bio = 'Aspiring full stack web engineer transitioning from script automation into high-performance web applications.'
            WHERE id = ?
        """, (hash_password('sudharsh390'), sid))
        conn.commit()
        conn.close()

        # Re-seed baseline data for this specific student_id
        _seed_student_data(sid)
    else:
        cursor.execute("DELETE FROM students WHERE username = 'M.Sudharshan' OR username = 'alex_chen'")
        conn.commit()
        conn.close()
        seed_demo_student()

def _seed_student_data(student_id: int):
    """Internal helper to insert baseline skills, projects, and roadmap for a given student ID."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    # Initial skills
    initial_skills = [
        (student_id, 'Python', 'Programming Languages', 3, 1, 1, now),
        (student_id, 'SQL', 'Databases & Storage', 3, 1, 1, now),
        (student_id, 'HTML5', 'Programming Languages', 2, 1, 0, now),
    ]
    cursor.executemany("""
        INSERT INTO skills (student_id, skill_name, category, proficiency_level, is_existing, verified, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, initial_skills)

    # Initial certification
    cursor.execute("""
        INSERT INTO certifications (student_id, title, issuing_org, issue_date, credential_url)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, 'Python for Everyone Specialist', 'Coursera / University of Michigan', '2024-05-15', 'https://coursera.org/verify/demo-alex-py'))

    # Initial project
    cursor.execute("""
        INSERT INTO projects (student_id, title, description, tech_stack, github_url, live_url, complexity)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        'ExpenseFlow Tracker CLI & DB',
        'CLI-based budget management tool with SQLite database persistence, transaction logging, and financial summaries.',
        'Python, SQLite',
        'https://github.com/alexchen-dev/expense-flow',
        None,
        'Intermediate'
    ))

    # Initial roadmap
    roadmap_data = [
        (student_id, 1, 'HTML5 Semantic Layouts & CSS3 Mastery', 'Master Flexbox, CSS Grid, media queries, and responsive web typography.', 'CSS3', 'Modern HTML & CSS From The Beginning', 'https://www.udemy.com/course/modern-html-css-from-the-beginning/', 'css grid flexbox full course freecodecamp', 'https://developer.mozilla.org/en-US/docs/Learn/CSS', 'Build a responsive SaaS pricing landing page.', 'In Progress', now),
        (student_id, 2, 'JavaScript Fundamentals & DOM Manipulation', 'Core JavaScript syntax, ES6+ features, closures, event loop, and asynchronous promises.', 'JavaScript', 'JavaScript: The Hard Parts', 'https://frontendmasters.com/courses/javascript-hard-parts-v2/', 'javascript full course for beginners bro code', 'https://javascript.info/', 'Build an interactive task planner with local storage.', 'Pending', now),
        (student_id, 3, 'Component Architecture with React.js', 'Declarative UI, JSX, state vs props, custom hooks, and context API.', 'React', 'The Ultimate React Course', 'https://www.udemy.com/course/the-ultimate-react-course/', 'react course 2024 freecodecamp', 'https://react.dev/learn', 'Build a real-time job application tracker.', 'Pending', now),
        (student_id, 4, 'Backend API Architecture with Node.js & Express', 'Server-side execution, RESTful conventions, middleware, routing, and JWT authentication.', 'Node.js', 'Node.js, Express & MongoDB Dev to Deployment', 'https://www.udemy.com/course/nodejs-express-mongodb-bootcamp/', 'node js express crash course traversy media', 'https://expressjs.com/en/starter/installing.html', 'Build an authentication & resource microservice.', 'Pending', now),
        (student_id, 5, 'Full Stack Capstone Integration', 'Connecting React frontend with Express backend and SQL database, handling CORS, Docker deployment.', 'Express.js', 'Full Stack Open', 'https://fullstackopen.com/en/', 'full stack web developer roadmap fireship', 'https://fullstackopen.com/', 'Deploy a production-ready web application with CI/CD.', 'Pending', now),
    ]
    for item in roadmap_data:
        cursor.execute("""
            INSERT INTO roadmap_items (student_id, week_number, topic, description, skill_target, course_title, course_url, youtube_query, doc_url, practical_task, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, item)

    # Initial baseline readiness score
    cursor.execute("""
        INSERT INTO readiness_history (student_id, overall_score, tech_score, challenge_score, project_score, quiz_score, calculated_at, explanation)
        VALUES (?, 42, 38, 45, 50, 40, ?, ?)
    """, (
        student_id,
        now,
        "Baseline Digital Twin assessment: Student possesses strong foundations in Python and SQL (backend/data), with basic HTML knowledge. Significant skill gap exists in JavaScript, modern CSS, React, and Express.js for the Full Stack Developer role."
    ))

    # Initial agent logs
    cursor.execute("""
        INSERT INTO agent_logs (student_id, agent_name, action, output_summary, timestamp)
        VALUES (?, 'Skill DNA Agent', 'Initial Skill Mapping', 'Identified existing: [Python, SQL, HTML5]. Flagged missing requirements for Full Stack Developer: [CSS3, JavaScript, React, Node.js, Express.js].', ?)
    """, (student_id, now))

    conn.commit()
    conn.close()
