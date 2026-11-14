"""
Configuration and Domain Knowledge for SkillPath AI
Career Digital Twin Platform
"""

APP_NAME = "SkillPath AI"
APP_SUBTITLE = "AI-Powered Career Digital Twin"
APP_VERSION = "1.0.0"

# Target Career Roles and Requirements
CAREER_ROLES = {
    "Full Stack Developer": {
        "description": "Designs and builds end-to-end web applications, encompassing frontend client interfaces, backend microservices, REST/GraphQL APIs, and database persistence layers.",
        "icon": "💻",
        "avg_salary": "$115,000 / yr",
        "demand": "Very High",
        "core_skills": ["HTML5", "CSS3", "JavaScript", "React", "Node.js", "Express.js", "SQL", "Git"],
        "advanced_skills": ["TypeScript", "Next.js", "Docker", "REST APIs", "PostgreSQL", "CI/CD"],
        "soft_skills": ["Problem Solving", "System Architecture", "Cross-functional Collaboration", "Code Review"],
        "default_min_proficiency": {
            "HTML5": 3, "CSS3": 3, "JavaScript": 4, "React": 3,
            "Node.js": 3, "Express.js": 3, "SQL": 3, "Git": 3
        }
    },
    "Frontend Developer": {
        "description": "Creates responsive, accessible, interactive web interfaces and client experiences using modern modern component frameworks and CSS architectures.",
        "icon": "🎨",
        "avg_salary": "$105,000 / yr",
        "demand": "High",
        "core_skills": ["HTML5", "CSS3", "JavaScript", "TypeScript", "React", "Tailwind CSS", "Git"],
        "advanced_skills": ["Next.js", "State Management", "Web Performance", "Jest", "UI/UX Design"],
        "soft_skills": ["Visual Eye", "Empathy", "Attention to Detail", "Communication"],
        "default_min_proficiency": {
            "HTML5": 4, "CSS3": 4, "JavaScript": 4, "React": 4,
            "TypeScript": 3, "Tailwind CSS": 3, "Git": 3
        }
    },
    "Backend Developer": {
        "description": "Architects server-side logic, high-throughput microservices, data pipelines, caching layers, and secure cloud API infrastructures.",
        "icon": "⚙️",
        "avg_salary": "$120,000 / yr",
        "demand": "Very High",
        "core_skills": ["Python", "Node.js", "SQL", "PostgreSQL", "REST APIs", "Git", "Docker"],
        "advanced_skills": ["FastAPI", "Express.js", "Redis", "Microservices", "Kubernetes", "GraphQL"],
        "soft_skills": ["Algorithmic Thinking", "Data Modeling", "Scalability Planning", "Security Mindset"],
        "default_min_proficiency": {
            "Python": 4, "Node.js": 3, "SQL": 4, "PostgreSQL": 3,
            "REST APIs": 4, "Git": 3, "Docker": 2
        }
    },
    "Data Analyst": {
        "description": "Translates complex datasets into actionable business intelligence, interactive dashboards, and executive insights using SQL, Python, and BI tools.",
        "icon": "📊",
        "avg_salary": "$88,000 / yr",
        "demand": "High",
        "core_skills": ["SQL", "Python", "Pandas", "Data Visualization", "Excel", "Tableau", "Statistics"],
        "advanced_skills": ["PowerBI", "NumPy", "A/B Testing", "ETL", "Data Cleaning"],
        "soft_skills": ["Business Acumen", "Data Storytelling", "Critical Thinking", "Stakeholder Presentation"],
        "default_min_proficiency": {
            "SQL": 4, "Python": 3, "Pandas": 3, "Data Visualization": 3,
            "Excel": 4, "Statistics": 3
        }
    },
    "Data Scientist": {
        "description": "Leverages statistical modeling, machine learning, and exploratory data mining to discover predictive patterns and automate enterprise decision systems.",
        "icon": "🧪",
        "avg_salary": "$130,000 / yr",
        "demand": "High",
        "core_skills": ["Python", "SQL", "Pandas", "NumPy", "Scikit-learn", "Machine Learning", "Statistics"],
        "advanced_skills": ["Deep Learning", "PyTorch", "Model Evaluation", "Feature Engineering", "MLOps"],
        "soft_skills": ["Hypothesis Testing", "Research Agility", "Quantitative Intuition", "Clarity in Technical Communication"],
        "default_min_proficiency": {
            "Python": 4, "SQL": 3, "Pandas": 4, "NumPy": 4,
            "Scikit-learn": 3, "Machine Learning": 3, "Statistics": 4
        }
    },
    "AI/ML Engineer": {
        "description": "Deploys, optimizes, fine-tunes, and monitors state-of-the-art machine learning models, neural networks, and generative AI systems in production.",
        "icon": "🤖",
        "avg_salary": "$145,000 / yr",
        "demand": "Extremely High",
        "core_skills": ["Python", "PyTorch", "Scikit-learn", "Deep Learning", "LLMs", "Docker", "Git"],
        "advanced_skills": ["TensorFlow", "HuggingFace", "Vector Databases", "MLOps", "LangChain", "GPU Optimization"],
        "soft_skills": ["Math Rigor", "Fast Experimentation", "System Design", "Ethical AI Awareness"],
        "default_min_proficiency": {
            "Python": 5, "PyTorch": 4, "Deep Learning": 4, "LLMs": 3,
            "Docker": 3, "Git": 3
        }
    },
    "Cybersecurity Analyst": {
        "description": "Protects networks, applications, and cloud infrastructures against intrusions, monitors threat vectors, audits vulnerabilities, and enforces compliance.",
        "icon": "🛡️",
        "avg_salary": "$112,000 / yr",
        "demand": "Very High",
        "core_skills": ["Network Security", "Linux", "Python", "OWASP", "SIEM", "Cryptography", "Git"],
        "advanced_skills": ["Penetration Testing", "Cloud Security", "Incident Response", "Firewalls", "Wireshark"],
        "soft_skills": ["Investigative Mindset", "Attention to Detail", "High Pressure Composure", "Risk Governance"],
        "default_min_proficiency": {
            "Network Security": 4, "Linux": 4, "Python": 3, "OWASP": 3,
            "SIEM": 3, "Cryptography": 3
        }
    }
}

# Skill Taxonomy & Category Mapping
SKILL_TAXONOMY = {
    "Programming Languages": ["Python", "JavaScript", "TypeScript", "SQL", "Java", "C++", "Go", "Rust", "HTML5", "CSS3"],
    "Frontend Frameworks & Libs": ["React", "Next.js", "Vue", "Angular", "Tailwind CSS", "Redux", "Bootstrap"],
    "Backend & APIs": ["Node.js", "Express.js", "Django", "FastAPI", "Flask", "Spring Boot", "REST APIs", "GraphQL"],
    "Databases & Storage": ["PostgreSQL", "MySQL", "MongoDB", "SQLite", "Redis", "Elasticsearch"],
    "Data & AI": ["Pandas", "NumPy", "Scikit-learn", "PyTorch", "TensorFlow", "LLMs", "Machine Learning", "Deep Learning", "Statistics", "Data Visualization"],
    "DevOps & Infrastructure": ["Docker", "Kubernetes", "Git", "CI/CD", "Linux", "AWS", "GCP", "Azure"],
    "Cybersecurity": ["Network Security", "OWASP", "Cryptography", "Penetration Testing", "SIEM", "Incident Response"],
    "Soft Skills": ["Problem Solving", "Communication", "System Architecture", "Collaboration", "Time Management", "Critical Thinking"]
}

# Prerequisites and Related Skills Graph for Skill DNA
SKILL_RELATIONS = {
    "HTML5": {"related": ["CSS3", "JavaScript"], "prereqs": []},
    "CSS3": {"related": ["HTML5", "Tailwind CSS", "Responsive Design"], "prereqs": ["HTML5"]},
    "JavaScript": {"related": ["TypeScript", "React", "Node.js"], "prereqs": ["HTML5", "CSS3"]},
    "TypeScript": {"related": ["JavaScript", "React", "Node.js"], "prereqs": ["JavaScript"]},
    "React": {"related": ["JavaScript", "Next.js", "Redux", "CSS3"], "prereqs": ["JavaScript", "HTML5", "CSS3"]},
    "Node.js": {"related": ["Express.js", "JavaScript", "REST APIs", "MongoDB"], "prereqs": ["JavaScript"]},
    "Express.js": {"related": ["Node.js", "REST APIs", "SQL"], "prereqs": ["Node.js"]},
    "Python": {"related": ["SQL", "FastAPI", "Django", "Pandas", "Machine Learning"], "prereqs": []},
    "SQL": {"related": ["PostgreSQL", "Database Design", "Python", "Data Analyst"], "prereqs": []},
    "PostgreSQL": {"related": ["SQL", "Backend Developer", "Redis"], "prereqs": ["SQL"]},
    "REST APIs": {"related": ["Backend Developer", "Node.js", "FastAPI", "Express.js"], "prereqs": ["Python", "JavaScript"]},
    "Docker": {"related": ["Kubernetes", "CI/CD", "Linux", "Cloud"], "prereqs": ["Linux", "Git"]},
    "Git": {"related": ["CI/CD", "Collaboration", "GitHub"], "prereqs": []},
    "Pandas": {"related": ["NumPy", "Python", "Statistics", "Data Visualization"], "prereqs": ["Python"]},
    "NumPy": {"related": ["Pandas", "Scikit-learn", "Python"], "prereqs": ["Python"]},
    "Scikit-learn": {"related": ["Machine Learning", "Pandas", "NumPy"], "prereqs": ["Python", "Pandas", "NumPy"]},
    "PyTorch": {"related": ["Deep Learning", "LLMs", "Python"], "prereqs": ["Python", "NumPy"]},
    "Deep Learning": {"related": ["PyTorch", "TensorFlow", "Neural Networks"], "prereqs": ["Scikit-learn", "Python"]},
    "LLMs": {"related": ["Deep Learning", "PyTorch", "Prompt Engineering"], "prereqs": ["Deep Learning", "Python"]},
    "Network Security": {"related": ["Linux", "Cryptography", "OWASP"], "prereqs": ["Linux"]},
    "OWASP": {"related": ["REST APIs", "Network Security", "Penetration Testing"], "prereqs": ["Network Security"]}
}

# Gemini API Default Settings
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"
API_KEY_ENV_VAR = "GEMINI_API_KEY"

# Weights for Career Readiness Score
READINESS_WEIGHTS = {
    "technical_skills": 0.35,      # Coverage and depth of required skills
    "challenges": 0.30,            # Practical coding and simulator score
    "projects": 0.20,              # Completed portfolio projects
    "quizzes_problem_solving": 0.15 # Conceptual and problem-solving quizzes
}
