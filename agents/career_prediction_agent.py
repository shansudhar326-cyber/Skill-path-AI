"""
Career Prediction Agent
Analyzes career market demand, evaluates role compatibility percentages,
identifies critical skill gaps, and forecasts future industry demands.
"""

from SkillPath_AI.config import CAREER_ROLES
from SkillPath_AI.utils.helpers import call_gemini, clean_json_response, compute_career_match_stats

class CareerPredictionAgent:
    def __init__(self):
        self.name = "Career Prediction Agent"
        self.role = "Market Demand & Career Compatibility Forecaster"

    def evaluate_career_compatibility(self, student_skills: list[dict], target_career: str) -> dict:
        """
        Evaluates compatibility against the selected target career and all other roles,
        providing comparative rankings, gap analysis, and industry trends.
        """
        # Calculate stats for the target role
        target_stats = compute_career_match_stats(student_skills, target_career)

        # Calculate compatibility across ALL available roles for benchmarking
        all_roles_comparison = []
        for role_name in CAREER_ROLES.keys():
            stats = compute_career_match_stats(student_skills, role_name)
            all_roles_comparison.append({
                "role": role_name,
                "compatibility": stats["match_percentage"],
                "missing_count": stats["gap_count"],
                "demand": CAREER_ROLES[role_name]["demand"],
                "avg_salary": CAREER_ROLES[role_name]["avg_salary"]
            })

        # Sort by compatibility
        all_roles_comparison.sort(key=lambda x: x["compatibility"], reverse=True)

        # AI-based career forecasting
        existing_names = [s["skill_name"] for s in student_skills if s.get("is_existing", 1)]
        prompt = f"""
        Analyze the career trajectory for a student aiming for: {target_career}.
        Current skills: {', '.join(existing_names)}
        Target Core Gaps: {', '.join(target_stats['missing_core'])}
        Target Advanced Gaps: {', '.join(target_stats['missing_adv'])}

        Return a JSON object:
        {{
            "feasibility_assessment": "Realistic evaluation of time-to-hire and transition difficulty (e.g., 3-6 months with focused roadmap)",
            "emerging_industry_skills": ["List 3 modern cutting-edge skills gaining rapid adoption in this field"],
            "pivot_alternatives": "Brief note on secondary career paths they are already well-positioned for",
            "strategic_advice": "Actionable advice to stand out to hiring managers"
        }}
        """

        raw_res, is_real_ai = call_gemini(
            prompt,
            system_instruction="You are a senior tech recruiter and industry talent forecaster. Give realistic, constructive assessments.",
            response_json=True
        )

        ai_forecast = clean_json_response(raw_res)
        if not ai_forecast or not is_real_ai:
            ai_forecast = self._generate_fallback_forecast(target_career, existing_names, target_stats)
            provider_label = "Career Engine Predictive Matrix (Demo Mode)"
        else:
            provider_label = "Google Gemini 1.5 Flash"

        return {
            "agent_name": self.name,
            "provider": provider_label,
            "is_real_ai": is_real_ai,
            "target_stats": target_stats,
            "all_roles_comparison": all_roles_comparison,
            "forecast": ai_forecast
        }

    def _generate_fallback_forecast(self, target_career: str, existing_skills: list, stats: dict) -> dict:
        """High-fidelity heuristic fallback when Gemini API key is not present."""
        if target_career == "Full Stack Developer":
            return {
                "feasibility_assessment": "Estimated 12-16 weeks of structured project building. Your backend foundations reduce the ramp-up time significantly compared to complete beginners.",
                "emerging_industry_skills": ["Next.js App Router & Server Actions", "Docker & Cloud-Run Deployment", "AI Tooling Integration (Vercel AI SDK)"],
                "pivot_alternatives": "With Python and SQL already active, you also have a 65%+ foundation for Backend Developer or Data Analyst roles.",
                "strategic_advice": "Do not just build toy apps. Build a full-stack CRUD application with JWT authentication, relational database migrations, and clean responsive CSS."
            }
        elif target_career == "Data Analyst":
            return {
                "feasibility_assessment": "Estimated 6-8 weeks. With your SQL and Python background, you already possess the core technical foundations required for junior analyst openings.",
                "emerging_industry_skills": ["Automated Data Pipelines with dbt", "Interactive Streamlit Dashboards", "Statistical A/B Testing"],
                "pivot_alternatives": "You have direct transferability to Business Intelligence Analyst and Analytics Engineering.",
                "strategic_advice": "Publish exploratory data analysis case studies on Kaggle or GitHub with interactive Plotly visualizations."
            }
        else:
            return {
                "feasibility_assessment": f"Estimated 14-20 weeks to bridge the {stats['gap_count']} missing competencies for {target_career}.",
                "emerging_industry_skills": ["Cloud Infrastructure Automation", "API Security Best Practices", "Containerized Workflows"],
                "pivot_alternatives": "Consider leveraging your existing competencies while upskilling in high-priority gaps.",
                "strategic_advice": "Focus on production-grade portfolio projects demonstrating end-to-end problem solving."
            }
