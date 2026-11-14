"""
Skill DNA Agent
Analyzes existing skills, computes topological skill adjacency,
identifies missing skills, and constructs the interactive Skill DNA network graph.
"""

import json
from config import CAREER_ROLES, SKILL_RELATIONS, SKILL_TAXONOMY
from utils.helpers import call_gemini, clean_json_response

class SkillDNAAgent:
    def __init__(self):
        self.name = "Skill DNA Agent"
        self.role = "Skill Graph & Topology Analyst"

    def analyze_skill_dna(self, student_skills: list[dict], target_career: str) -> dict:
        """
        Executes comprehensive Skill DNA extraction:
        1. Categorizes Existing vs Missing vs Related skills.
        2. Determines the recommended next 3-4 skills to acquire.
        3. Constructs interactive graph nodes and edges for visualization.
        4. Provides AI-powered cognitive analysis of the student's skill portfolio.
        """
        career_meta = CAREER_ROLES.get(target_career, CAREER_ROLES["Full Stack Developer"])
        target_core = career_meta.get("core_skills", [])
        target_adv = career_meta.get("advanced_skills", [])
        all_target = list(dict.fromkeys(target_core + target_adv))

        existing_names = [s["skill_name"] for s in student_skills if s.get("is_existing", 1)]
        existing_names_lower = {s.lower(): s for s in existing_names}

        # Identify existing vs missing
        missing_skills = []
        for req in all_target:
            if req.lower() not in existing_names_lower:
                missing_skills.append(req)

        # Identify related skills (skills connected in the knowledge graph)
        related_skills = []
        for s in existing_names:
            rel = SKILL_RELATIONS.get(s, {}).get("related", [])
            for r in rel:
                if r not in existing_names and r not in related_skills:
                    related_skills.append(r)

        # Recommend next skills based on prerequisite readiness
        next_to_learn = []
        for m in missing_skills:
            prereqs = SKILL_RELATIONS.get(m, {}).get("prereqs", [])
            # If all prereqs are met or no prereqs
            prereqs_met = all(p.lower() in existing_names_lower for p in prereqs)
            if prereqs_met:
                next_to_learn.append(m)
        if not next_to_learn and missing_skills:
            next_to_learn = missing_skills[:3]

        # Call Gemini for qualitative AI insight
        prompt = f"""
        Analyze the student's Skill DNA profile:
        Target Career: {target_career}
        Existing Skills: {', '.join(existing_names) if existing_names else 'None'}
        Missing Skills for Goal: {', '.join(missing_skills)}
        Next Prioritized Skills: {', '.join(next_to_learn)}

        Return a JSON object with:
        {{
            "dna_summary": "2-3 sentence assessment of the student's current skill profile and foundation",
            "primary_strength": "Main technical advantage of the student",
            "critical_gap": "The single most impactful bottleneck skill to unlock next",
            "learning_velocity_recommendation": "Advice on pacing and approach"
        }}
        """
        raw_res, is_real_ai = call_gemini(
            prompt,
            system_instruction="You are an expert AI Career and Tech Skill DNA Analyst. Provide rigorous, personalized talent analysis.",
            response_json=True
        )

        ai_insights = clean_json_response(raw_res)
        if not ai_insights or not is_real_ai:
            ai_insights = self._generate_fallback_insights(existing_names, missing_skills, target_career, next_to_learn)
            provider_label = "SkillPath Heuristic Engine (Demo Mode)"
        else:
            provider_label = "Google Gemini 1.5 Flash"

        # Construct Network Graph data
        graph_data = self._build_network_graph(existing_names, missing_skills, related_skills, target_career)

        return {
            "agent_name": self.name,
            "provider": provider_label,
            "is_real_ai": is_real_ai,
            "existing_skills": existing_names,
            "missing_skills": missing_skills,
            "related_skills": related_skills,
            "next_to_learn": next_to_learn,
            "insights": ai_insights,
            "graph_data": graph_data
        }

    def _generate_fallback_insights(self, existing: list, missing: list, target_career: str, next_skills: list) -> dict:
        """Deterministic, rich fallback when Gemini API key is absent."""
        if "Python" in existing and "SQL" in existing and target_career == "Full Stack Developer":
            return {
                "dna_summary": "Your foundational backend data skills (Python, SQL) are solid, giving you an advantage in data persistence. However, your client-tier competencies (JavaScript, CSS, React) represent a primary gap that must be bridged to achieve full-stack fluency.",
                "primary_strength": "Backend Data Manipulation & Script Logic",
                "critical_gap": "Modern ECMAScript (JavaScript ES6+) and Component State Management",
                "learning_velocity_recommendation": "Prioritize JavaScript fundamentals and DOM manipulation before diving directly into React component architecture."
            }
        elif "Python" in existing and target_career in ["Data Analyst", "Data Scientist"]:
            return {
                "dna_summary": f"Strong alignment for {target_career}. Your Python background will allow rapid acceleration into statistical data pipelines and exploratory analysis.",
                "primary_strength": "Python Core Scripting",
                "critical_gap": f"Advanced {missing[0] if missing else 'Data Modeling'} and Business Intelligence",
                "learning_velocity_recommendation": "Focus on real-world datasets and data storytelling with Pandas and Plotly."
            }
        else:
            first_missing = missing[0] if missing else "Advanced Frameworks"
            return {
                "dna_summary": f"Your current profile has {len(existing)} active skills. Transitioning into {target_career} requires mastering {len(missing)} additional target competencies.",
                "primary_strength": f"{existing[0] if existing else 'Initiative'} Proficiency",
                "critical_gap": f"{first_missing} Architecture",
                "learning_velocity_recommendation": f"Focus sequentially on {', '.join(next_skills[:2])} to build rapid project momentum."
            }

    def _build_network_graph(self, existing: list, missing: list, related: list, target_career: str) -> dict:
        """Constructs node and edge coordinate layout for Plotly network chart."""
        nodes = []
        edges = []

        # Central Role Node
        nodes.append({
            "id": target_career,
            "label": f"🎯 {target_career}",
            "type": "target_role",
            "color": "#6366F1", # Indigo
            "size": 34,
            "group": "Target Role"
        })

        # Existing Skill Nodes (Green)
        for s in existing:
            nodes.append({
                "id": s,
                "label": f"✅ {s}",
                "type": "existing",
                "color": "#10B981", # Emerald Green
                "size": 24,
                "group": "Existing Skill"
            })
            # Connect existing to target if in target requirements
            edges.append({"source": s, "target": target_career, "color": "#10B981", "style": "solid"})

        # Missing Skill Nodes (Orange / Amber)
        for m in missing[:8]: # Limit for visual clarity
            nodes.append({
                "id": m,
                "label": f"⚡ {m}",
                "type": "missing",
                "color": "#F59E0B", # Amber
                "size": 22,
                "group": "Missing Skill"
            })
            edges.append({"source": target_career, "target": m, "color": "#F59E0B", "style": "dash"})

        # Related / Bridge Nodes (Sky Blue)
        for r in related[:5]:
            if r not in [n["id"] for n in nodes]:
                nodes.append({
                    "id": r,
                    "label": f"🔗 {r}",
                    "type": "related",
                    "color": "#38BDF8", # Light Blue
                    "size": 18,
                    "group": "Related Skill"
                })
                # Connect to first existing related
                edges.append({"source": existing[0] if existing else target_career, "target": r, "color": "#94A3B8", "style": "dot"})

        return {"nodes": nodes, "edges": edges}
