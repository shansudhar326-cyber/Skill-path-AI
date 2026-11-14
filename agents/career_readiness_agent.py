"""
Career Readiness Agent
Evaluates student technical proficiency, challenge submissions, practical portfolio projects,
and problem-solving assessments to compute an objective, transparent Career Readiness Score.
"""

from SkillPath_AI.config import CAREER_ROLES, READINESS_WEIGHTS
from SkillPath_AI.utils.helpers import call_gemini, clean_json_response, compute_career_match_stats

class CareerReadinessAgent:
    def __init__(self):
        self.name = "Career Readiness Agent"
        self.role = "Holistic Readiness Auditor & Portfolio Evaluator"

    def calculate_readiness(
        self,
        student_skills: list[dict],
        target_career: str,
        submissions: list[dict],
        projects: list[dict],
        certifications: list[dict]
    ) -> dict:
        """
        Calculates four distinct performance pillars:
        1. Technical Skill Coverage (35%)
        2. Practical Challenge Performance (30%)
        3. Portfolio Projects & Complexity (20%)
        4. Problem Solving & Assessments (15%)
        """
        # Pillar 1: Technical Skills Coverage & Depth (0-100)
        match_stats = compute_career_match_stats(student_skills, target_career)
        career_meta = CAREER_ROLES.get(target_career, CAREER_ROLES["Full Stack Developer"])
        req_proficiencies = career_meta.get("default_min_proficiency", {})

        # Compute skill depth score
        total_depth_target = sum(req_proficiencies.values()) if req_proficiencies else 20
        acquired_depth = 0
        student_skill_map = {s["skill_name"].lower(): s["proficiency_level"] for s in student_skills if s.get("is_existing", 1)}

        for skill_name, req_level in req_proficiencies.items():
            current_level = student_skill_map.get(skill_name.lower(), 0)
            acquired_depth += min(current_level, req_level)

        skill_depth_score = int((acquired_depth / max(total_depth_target, 1)) * 100)
        # Combine breadth and depth
        tech_score = int((match_stats["match_percentage"] * 0.6) + (skill_depth_score * 0.4))
        tech_score = min(100, max(15, tech_score))

        # Pillar 2: Practical Challenge Score (0-100)
        if submissions:
            # Average score of submissions with recency weight
            scores = [sub.get("score", 0) for sub in submissions]
            challenge_score = int(sum(scores) / len(scores))
        else:
            # Baseline when no challenges completed yet
            challenge_score = 40

        # Pillar 3: Practical Projects & Complexity (0-100)
        if projects:
            project_base = min(len(projects) * 25, 75)
            # Complexity bonus
            has_adv = any(p.get("complexity") == "Advanced" for p in projects)
            has_med = any(p.get("complexity") == "Intermediate" for p in projects)
            complexity_bonus = 25 if has_adv else (15 if has_med else 5)
            project_score = min(100, project_base + complexity_bonus)
        else:
            project_score = 30

        # Pillar 4: Problem-Solving & Certifications (0-100)
        # Based on certifications, verification and problem solving
        cert_count = len(certifications)
        quiz_score = min(100, 35 + (cert_count * 20) + (len(student_skills) * 3))

        # Overall Weighted Score
        w_tech = READINESS_WEIGHTS["technical_skills"]
        w_chal = READINESS_WEIGHTS["challenges"]
        w_proj = READINESS_WEIGHTS["projects"]
        w_quiz = READINESS_WEIGHTS["quizzes_problem_solving"]

        overall = int(
            (tech_score * w_tech) +
            (challenge_score * w_chal) +
            (project_score * w_proj) +
            (quiz_score * w_quiz)
        )
        overall = min(100, max(10, overall))

        # Readiness Tier
        if overall >= 85:
            tier = "Job-Ready (Senior Competency)"
            badge_color = "#10B981" # Green
        elif overall >= 70:
            tier = "Industry Ready (Entry-to-Mid)"
            badge_color = "#3B82F6" # Blue
        elif overall >= 50:
            tier = "Developing Practitioner"
            badge_color = "#F59E0B" # Amber
        else:
            tier = "Foundational Learner"
            badge_color = "#8B5CF6" # Purple

        # Call Gemini or fallback for personalized audit explanation
        prompt = f"""
        Provide a transparent career readiness summary for a student aiming to be a {target_career}.
        Overall Score: {overall}/100 ({tier})
        - Technical Skill Score: {tech_score}/100 (Weight: 35%)
        - Practical Challenges Score: {challenge_score}/100 (Weight: 30%)
        - Portfolio Projects Score: {project_score}/100 (Weight: 20%)
        - Problem-Solving / Quizzes: {quiz_score}/100 (Weight: 15%)

        Missing Target Skills: {', '.join(match_stats['missing_core'][:4])}

        Return a JSON object:
        {{
            "audit_summary": "1-2 sentence candid overview of readiness",
            "highest_leverage_action": "The single fastest action to raise the readiness score by 10+ points",
            "transparency_breakdown": "Explanation of how this mathematical score reflects industry hiring filters"
        }}
        """

        raw_res, is_real_ai = call_gemini(
            prompt,
            system_instruction="You are a principal engineer conducting transparent talent evaluations. Be honest, data-driven, and supportive.",
            response_json=True
        )

        ai_audit = clean_json_response(raw_res)
        if not ai_audit or not is_real_ai:
            ai_audit = self._fallback_audit(overall, tier, target_career, match_stats["missing_core"])
            provider_label = "Career Readiness Heuristic Engine (Demo Mode)"
        else:
            provider_label = "Google Gemini 1.5 Flash"

        return {
            "agent_name": self.name,
            "provider": provider_label,
            "is_real_ai": is_real_ai,
            "overall_score": overall,
            "tech_score": tech_score,
            "challenge_score": challenge_score,
            "project_score": project_score,
            "quiz_score": quiz_score,
            "weights": READINESS_WEIGHTS,
            "tier": tier,
            "badge_color": badge_color,
            "audit": ai_audit,
            "disclaimer": "Transparency Note: This readiness index reflects practical platform performance, project depth, and core curriculum coverage. It serves as an actionable growth indicator and does not guarantee formal employment."
        }

    def _fallback_audit(self, overall: int, tier: str, target_career: str, missing_skills: list) -> dict:
        missing_str = ", ".join(missing_skills[:3]) if missing_skills else "advanced frameworks"
        return {
            "audit_summary": f"Your current readiness is calibrated at {overall}% ({tier}) for {target_career}. Your portfolio projects and foundations provide a base, but closing gaps in {missing_str} will dramatically increase interview confidence.",
            "highest_leverage_action": f"Complete a practical challenge and deploy a full-stack project addressing {missing_str}.",
            "transparency_breakdown": "The score is calculated via 4 weighted dimensions: Technical Skills (35%), Practical Challenges (30%), Portfolio Projects (20%), and Problem-Solving (15%)."
        }
