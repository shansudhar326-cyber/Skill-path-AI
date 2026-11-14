"""
Central Agent Orchestrator
Coordinates communication, event triggers, and state synchronization
across all five specialized AI agents.
"""

from database.db import (
    get_student_by_id, get_student_skills, get_projects,
    get_certifications, get_challenges_for_student, get_recent_submissions,
    update_student_profile, save_readiness_score, clear_and_set_roadmap,
    prepend_rescue_module, record_challenge_submission, save_rescue_plan,
    log_agent_action, get_active_rescue_plans
)
from agents.skill_dna_agent import SkillDNAAgent
from agents.career_prediction_agent import CareerPredictionAgent
from agents.challenge_agent import ChallengeAgent
from agents.learning_rescue_agent import LearningRescueAgent
from agents.career_readiness_agent import CareerReadinessAgent
from config import CAREER_ROLES

class AgentOrchestrator:
    def __init__(self):
        self.skill_dna_agent = SkillDNAAgent()
        self.career_prediction_agent = CareerPredictionAgent()
        self.challenge_agent = ChallengeAgent()
        self.learning_rescue_agent = LearningRescueAgent()
        self.career_readiness_agent = CareerReadinessAgent()

    def run_full_diagnosis(self, student_id: int) -> dict:
        """
        Orchestrates an end-to-end multi-agent evaluation:
        1. Skill DNA Agent -> Analyzes topology, missing skills, graph
        2. Career Prediction Agent -> Calculates role compatibility and trends
        3. Career Readiness Agent -> Computes weighted readiness score
        """
        student = get_student_by_id(student_id)
        if not student:
            return {}

        skills = get_student_skills(student_id)
        projects = get_projects(student_id)
        certs = get_certifications(student_id)
        submissions = get_recent_submissions(student_id)
        target_career = student["target_career"]

        # 1. Skill DNA Agent
        dna_result = self.skill_dna_agent.analyze_skill_dna(skills, target_career)
        log_agent_action(
            student_id,
            self.skill_dna_agent.name,
            "Skill Graph Diagnosis",
            f"Analyzed {len(dna_result['existing_skills'])} existing skills. Flagged {len(dna_result['missing_skills'])} gaps."
        )

        # 2. Career Prediction Agent
        prediction_result = self.career_prediction_agent.evaluate_career_compatibility(skills, target_career)
        log_agent_action(
            student_id,
            self.career_prediction_agent.name,
            "Role Compatibility Audit",
            f"Evaluated compatibility for {target_career}: {prediction_result['target_stats']['match_percentage']}% match."
        )

        # 3. Career Readiness Agent
        readiness_result = self.career_readiness_agent.calculate_readiness(
            skills, target_career, submissions, projects, certs
        )
        save_readiness_score(
            student_id,
            readiness_result["overall_score"],
            readiness_result["tech_score"],
            readiness_result["challenge_score"],
            readiness_result["project_score"],
            readiness_result["quiz_score"],
            readiness_result["audit"]["audit_summary"]
        )
        log_agent_action(
            student_id,
            self.career_readiness_agent.name,
            "Readiness Score Sync",
            f"Overall Career Readiness Index calibrated at {readiness_result['overall_score']}% ({readiness_result['tier']})."
        )

        return {
            "student": student,
            "target_career": target_career,
            "dna": dna_result,
            "prediction": prediction_result,
            "readiness": readiness_result,
            "active_rescues": get_active_rescue_plans(student_id)
        }

    def on_career_goal_changed(self, student_id: int, new_career: str) -> dict:
        """
        Triggered when student switches career goal (e.g., from Full Stack Developer to Data Analyst).
        Re-runs Skill DNA, Career Prediction, updates Roadmap, and recalibrates Readiness.
        """
        student = get_student_by_id(student_id)
        if not student:
            return {}

        # 1. Update Student Profile in DB
        update_student_profile(student_id, student["full_name"], student.get("bio", ""), new_career)
        log_agent_action(
            student_id,
            "Orchestrator",
            "Career Goal Pivot Triggered",
            f"User pivoted target career from '{student['target_career']}' to '{new_career}'."
        )

        # 2. Re-run Skill DNA Agent
        skills = get_student_skills(student_id)
        dna_result = self.skill_dna_agent.analyze_skill_dna(skills, new_career)
        log_agent_action(
            student_id,
            self.skill_dna_agent.name,
            "Skill Gap Re-calculation",
            f"Recalculated gaps for {new_career}. Found {len(dna_result['missing_skills'])} missing competencies."
        )

        # 3. Generate New Tailored Roadmap for the new career
        new_roadmap_items = self._build_career_roadmap(new_career, dna_result["missing_skills"])
        clear_and_set_roadmap(student_id, new_roadmap_items)
        log_agent_action(
            student_id,
            "Orchestrator",
            "Roadmap Re-generation",
            f"Generated {len(new_roadmap_items)}-week customized learning roadmap tailored for {new_career}."
        )

        # 4. Re-run Career Readiness Agent
        projects = get_projects(student_id)
        certs = get_certifications(student_id)
        submissions = get_recent_submissions(student_id)
        readiness_result = self.career_readiness_agent.calculate_readiness(
            skills, new_career, submissions, projects, certs
        )
        save_readiness_score(
            student_id,
            readiness_result["overall_score"],
            readiness_result["tech_score"],
            readiness_result["challenge_score"],
            readiness_result["project_score"],
            readiness_result["quiz_score"],
            readiness_result["audit"]["audit_summary"]
        )

        return {
            "status": "success",
            "new_career": new_career,
            "dna": dna_result,
            "readiness": readiness_result,
            "roadmap_count": len(new_roadmap_items)
        }

    def evaluate_and_orchestrate_submission(
        self,
        student_id: int,
        challenge: dict,
        code_submission: str,
        student_notes: str = ""
    ) -> dict:
        """
        Orchestrates submission evaluation:
        1. Challenge Agent evaluates code.
        2. Records submission in DB.
        3. If score < 60 (or specifically 30% low score):
           Triggers Learning Rescue Agent -> Creates rescue plan -> Updates roadmap!
        4. Recalibrates Career Readiness.
        """
        # 1. Challenge Agent Evaluation
        eval_result = self.challenge_agent.evaluate_submission(challenge, code_submission, student_notes)
        score = eval_result.get("score", 0)

        # 2. Record submission in DB
        submission_id = record_challenge_submission(
            challenge["id"],
            student_id,
            code_submission,
            student_notes,
            eval_result
        )

        log_agent_action(
            student_id,
            self.challenge_agent.name,
            f"Challenge Evaluation: {challenge.get('title')}",
            f"Evaluated submission with Score: {score}/100. Logic: {eval_result.get('logic_score')}, Correctness: {eval_result.get('correctness_score')}."
        )

        rescue_triggered = False
        rescue_plan = None

        # 3. Adaptive Learning Rescue Trigger Check
        if eval_result.get("requires_rescue") or score < 60:
            weak_topic = challenge.get("title", "Technical Challenge")
            # If JavaScript related, focus on JavaScript
            if "javascript" in weak_topic.lower() or "js" in weak_topic.lower() or "navigation" in weak_topic.lower() or "login" in weak_topic.lower():
                weak_concept = "JavaScript Fundamentals & DOM/Async Flow"
                downstream = "React & Node.js"
            else:
                weak_concept = weak_topic
                downstream = "Production Architecture"

            rescue_plan = self.learning_rescue_agent.formulate_rescue_plan(
                weak_topic=weak_concept,
                score=score,
                context_notes=eval_result.get("feedback", ""),
                downstream_skill=downstream
            )

            # Persist Rescue Plan to DB
            save_rescue_plan(
                student_id=student_id,
                weak_topic=weak_concept,
                score_trigger=score,
                explanation=rescue_plan["simplified_explanation"],
                tutorials=rescue_plan["recommended_tutorials"],
                practice_questions=rescue_plan["practice_exercises"]
            )

            # Prepend Rescue Intervention to Roadmap
            prepend_rescue_module(student_id, {
                "topic": f"Rescue Module: {weak_concept}",
                "description": rescue_plan["simplified_explanation"][:200] + "...",
                "skill_target": weak_concept,
                "course_title": "Targeted Remediation & Concept Simplification",
                "course_url": "https://developer.mozilla.org/",
                "youtube_query": f"{weak_concept} crash course for beginners",
                "doc_url": "https://developer.mozilla.org/",
                "practical_task": rescue_plan["practice_exercises"][0]["task"] if rescue_plan["practice_exercises"] else "Practice exercises"
            })

            rescue_triggered = True
            log_agent_action(
                student_id,
                self.learning_rescue_agent.name,
                "Adaptive Rescue Plan Formulated",
                f"Score {score}% triggered rescue for '{weak_concept}'. Simplified explanation, tutorials, and roadmap intervention generated."
            )

        # 4. Recalibrate Readiness Score
        student = get_student_by_id(student_id)
        skills = get_student_skills(student_id)
        projects = get_projects(student_id)
        certs = get_certifications(student_id)
        submissions = get_recent_submissions(student_id)

        readiness_result = self.career_readiness_agent.calculate_readiness(
            skills, student["target_career"], submissions, projects, certs
        )
        save_readiness_score(
            student_id,
            readiness_result["overall_score"],
            readiness_result["tech_score"],
            readiness_result["challenge_score"],
            readiness_result["project_score"],
            readiness_result["quiz_score"],
            readiness_result["audit"]["audit_summary"]
        )

        return {
            "evaluation": eval_result,
            "submission_id": submission_id,
            "rescue_triggered": rescue_triggered,
            "rescue_plan": rescue_plan,
            "updated_readiness": readiness_result
        }

    def _build_career_roadmap(self, role: str, missing_skills: list) -> list:
        """Constructs an industry-aligned roadmap for a specific career target."""
        if role == "Data Analyst":
            return [
                {
                    "week_number": 1,
                    "topic": "Advanced SQL & Analytical Queries",
                    "description": "Window functions (ROW_NUMBER, RANK, DENSE_RANK), CTEs, self-joins, and query execution plans.",
                    "skill_target": "SQL",
                    "course_title": "Advanced SQL for Data Scientists & Analysts",
                    "course_url": "https://www.coursera.org/learn/advanced-sql-data-science",
                    "youtube_query": "advanced sql window functions cte alex the analyst",
                    "doc_url": "https://mode.com/sql-tutorial/",
                    "practical_task": "Write customer cohort retention analysis queries on an e-commerce database.",
                    "status": "In Progress"
                },
                {
                    "week_number": 2,
                    "topic": "Exploratory Data Analysis with Pandas & NumPy",
                    "description": "Vectorized computations, handling null values, group-by aggregations, reshaping, and time-series indexing.",
                    "skill_target": "Pandas",
                    "course_title": "Data Analysis with Python (FreeCodeCamp)",
                    "course_url": "https://www.freecodecamp.org/learn/data-analysis-with-python/",
                    "youtube_query": "pandas complete tutorial keith galli",
                    "doc_url": "https://pandas.pydata.org/docs/",
                    "practical_task": "Clean and normalize a raw 50,000-row real estate dataset.",
                    "status": "Pending"
                },
                {
                    "week_number": 3,
                    "topic": "Data Storytelling & Interactive Visualizations with Plotly",
                    "description": "Chart design theory, categorical distributions, correlation heatmaps, interactive slider filters, and executive dashboards.",
                    "skill_target": "Data Visualization",
                    "course_title": "Interactive Python Dashboards with Plotly and Dash",
                    "course_url": "https://www.udemy.com/course/interactive-python-dashboards-with-plotly-and-dash/",
                    "youtube_query": "plotly express python crash course",
                    "doc_url": "https://plotly.com/python/",
                    "practical_task": "Build an executive financial KPI dashboard in Plotly and Streamlit.",
                    "status": "Pending"
                },
                {
                    "week_number": 4,
                    "topic": "Statistical Foundations & A/B Testing",
                    "description": "Hypothesis testing, p-values, z-scores, confidence intervals, sample size determination, and variance analysis.",
                    "skill_target": "Statistics",
                    "course_title": "Intro to Inferential Statistics (Khan Academy / Udacity)",
                    "course_url": "https://www.khanacademy.org/math/statistics-probability",
                    "youtube_query": "hypothesis testing ab testing explained statquest",
                    "doc_url": "https://docs.scipy.org/doc/scipy/reference/stats.html",
                    "practical_task": "Conduct a two-tailed t-test on simulated product conversion experiments.",
                    "status": "Pending"
                },
                {
                    "week_number": 5,
                    "topic": "Business Intelligence & Executive Presentation",
                    "description": "Designing automated reporting dashboards in Tableau/PowerBI with calculated fields and parameter actions.",
                    "skill_target": "Tableau",
                    "course_title": "Tableau A-Z: Hands-On Training for Data Science",
                    "course_url": "https://www.udemy.com/course/tableau10/",
                    "youtube_query": "tableau tutorial for beginners step by step",
                    "doc_url": "https://help.tableau.com/",
                    "practical_task": "Deploy an end-to-end business intelligence case study on Tableau Public or GitHub.",
                    "status": "Pending"
                }
            ]
        elif role == "AI/ML Engineer":
            return [
                {
                    "week_number": 1,
                    "topic": "Vectorized Linear Algebra & PyTorch Tensors",
                    "description": "Tensor transformations, GPU memory management, broadcasting, and autograd backpropagation mechanics.",
                    "skill_target": "PyTorch",
                    "course_title": "Deep Learning with PyTorch: A 60 Minute Blitz",
                    "course_url": "https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html",
                    "youtube_query": "pytorch for deep learning full course daniel bourke",
                    "doc_url": "https://pytorch.org/docs/stable/index.html",
                    "practical_task": "Train a multi-layer perceptron from scratch with autograd.",
                    "status": "In Progress"
                },
                {
                    "week_number": 2,
                    "topic": "Deep Learning Architectures (CNNs, RNNs, Transformers)",
                    "description": "Attention mechanisms, multi-head self-attention, loss curves, learning rate schedulers, and regularization.",
                    "skill_target": "Deep Learning",
                    "course_title": "CS25: Transformers United (Stanford)",
                    "course_url": "https://web.stanford.edu/class/cs25/",
                    "youtube_query": "transformers neural networks visual explanation 3blue1brown",
                    "doc_url": "https://huggingface.co/learn/nlp-course/",
                    "practical_task": "Implement self-attention layer and train a transformer classifier.",
                    "status": "Pending"
                },
                {
                    "week_number": 3,
                    "topic": "Large Language Models & Prompt Engineering Systems",
                    "description": "Instruction fine-tuning, LoRA/PEFT, vector databases (ChromaDB), RAG architectures, and evaluation frameworks.",
                    "skill_target": "LLMs",
                    "course_title": "Generative AI with Large Language Models (DeepLearning.AI)",
                    "course_url": "https://www.deeplearning.ai/courses/generative-ai-with-llms/",
                    "youtube_query": "retrieval augmented generation rag langchain tutorial",
                    "doc_url": "https://python.langchain.com/docs/get_started/introduction",
                    "practical_task": "Build a production RAG system with citation tracking and embeddings.",
                    "status": "Pending"
                },
                {
                    "week_number": 4,
                    "topic": "MLOps & Model Deployment with Docker and FastAPI",
                    "description": "Packaging models as microservices, containerization, latency benchmarking, and endpoint scaling.",
                    "skill_target": "Docker",
                    "course_title": "Made With ML: Production Machine Learning",
                    "course_url": "https://madewithml.com/",
                    "youtube_query": "fastapi deploy ml model docker tutorial",
                    "doc_url": "https://fastapi.tiangolo.com/",
                    "practical_task": "Containerize a PyTorch inference API with Docker and deploy to cloud.",
                    "status": "Pending"
                }
            ]
        else: # Standard Full Stack Roadmap
            return [
                {
                    "week_number": 1,
                    "topic": "Modern CSS3, Flexbox, Grid & Responsive UI",
                    "description": "Responsive layout mechanics, media queries, CSS variables, and modern Tailwind conventions.",
                    "skill_target": "CSS3",
                    "course_title": "Modern HTML & CSS From The Beginning",
                    "course_url": "https://www.udemy.com/course/modern-html-css-from-the-beginning/",
                    "youtube_query": "css grid flexbox complete tutorial freecodecamp",
                    "doc_url": "https://developer.mozilla.org/en-US/docs/Learn/CSS",
                    "practical_task": "Build a responsive SaaS pricing and feature landing page.",
                    "status": "In Progress"
                },
                {
                    "week_number": 2,
                    "topic": "JavaScript Deep Dive: Asynchronous ES6+ & DOM Manipulation",
                    "description": "Closures, event loop, promises, async/await, fetch API, and modular architecture.",
                    "skill_target": "JavaScript",
                    "course_title": "JavaScript: Understanding the Weird Parts",
                    "course_url": "https://www.udemy.com/course/understand-javascript/",
                    "youtube_query": "javascript crash course for beginners traversy media",
                    "doc_url": "https://javascript.info/",
                    "practical_task": "Build an interactive CRUD Kanban board with localStorage.",
                    "status": "Pending"
                },
                {
                    "week_number": 3,
                    "topic": "React.js Component Architecture & State Management",
                    "description": "Hooks (useState, useEffect, useMemo), custom hooks, context API, and component life cycle.",
                    "skill_target": "React",
                    "course_title": "The Ultimate React Course (Jonas Schmedtmann)",
                    "course_url": "https://www.udemy.com/course/the-ultimate-react-course/",
                    "youtube_query": "react course 2024 for beginners freecodecamp",
                    "doc_url": "https://react.dev/learn",
                    "practical_task": "Build a real-time job application tracking dashboard.",
                    "status": "Pending"
                },
                {
                    "week_number": 4,
                    "topic": "Backend REST APIs with Node.js & Express.js",
                    "description": "Middleware architecture, routing, request validation, JWT authentication, and error handling.",
                    "skill_target": "Node.js",
                    "course_title": "Node.js, Express, MongoDB Bootcamp",
                    "course_url": "https://www.udemy.com/course/nodejs-express-mongodb-bootcamp/",
                    "youtube_query": "node js express crash course 2024",
                    "doc_url": "https://expressjs.com/",
                    "practical_task": "Build a secure multi-tenant authentication microservice.",
                    "status": "Pending"
                },
                {
                    "week_number": 5,
                    "topic": "Full Stack Database Integration & Deployment",
                    "description": "Connecting React client to Express server with PostgreSQL/SQLite, CORS, Docker containers, and CI/CD.",
                    "skill_target": "Express.js",
                    "course_title": "Full Stack Open (University of Helsinki)",
                    "course_url": "https://fullstackopen.com/en/",
                    "youtube_query": "full stack web development complete project fireship",
                    "doc_url": "https://fullstackopen.com/",
                    "practical_task": "Deploy production full stack web application to Render/Fly.io.",
                    "status": "Pending"
                }
            ]
