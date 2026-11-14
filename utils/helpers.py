"""
Utility and AI Helper Functions for SkillPath AI
Handles Gemini API integration, JSON extraction, and domain calculations.
"""

import os
import json
import re
import google.generativeai as genai
from config import CAREER_ROLES, DEFAULT_GEMINI_MODEL, API_KEY_ENV_VAR

# Streamlit is optional — not available on Vercel (Flask-only deployment)
try:
    import streamlit as st
    _HAS_STREAMLIT = True
except ImportError:
    _HAS_STREAMLIT = False

def get_gemini_api_key() -> str:
    """Retrieve Gemini API key from session state, secrets, or environment variable."""
    # 1. Check Streamlit session state (only if Streamlit is loaded)
    if _HAS_STREAMLIT:
        try:
            if "gemini_api_key" in st.session_state and st.session_state["gemini_api_key"]:
                return st.session_state["gemini_api_key"].strip()
        except Exception:
            pass

        # 2. Check Streamlit secrets
        try:
            if "GEMINI_API_KEY" in st.secrets:
                return st.secrets["GEMINI_API_KEY"].strip()
        except Exception:
            pass

    # 3. Check OS environment variable
    return os.environ.get(API_KEY_ENV_VAR, "").strip()

def is_gemini_available() -> bool:
    """Checks if a non-empty Gemini API key is configured."""
    key = get_gemini_api_key()
    return bool(key and len(key) > 10)

def call_gemini(prompt: str, system_instruction: str = None, response_json: bool = False) -> tuple[str, bool]:
    """
    Calls Google Gemini API.
    Returns: (response_text_or_json_str, is_real_ai_call)
    If API key is missing or call fails, returns ("", False) to trigger the agent's rule-based fallback.
    """
    key = get_gemini_api_key()
    if not key:
        return "", False

    try:
        genai.configure(api_key=key)
        generation_config = {
            "temperature": 0.4,
            "top_p": 0.95,
            "max_output_tokens": 2048,
        }
        if response_json:
            generation_config["response_mime_type"] = "application/json"

        model_kwargs = {
            "model_name": DEFAULT_GEMINI_MODEL,
            "generation_config": generation_config
        }
        if system_instruction:
            model_kwargs["system_instruction"] = system_instruction

        model = genai.GenerativeModel(**model_kwargs)
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text, True
        return "", False
    except Exception as e:
        # Fallback to rule-based engine when API fails or quota exceeded
        print(f"[Gemini API Notice] Falling back to rule-based engine: {e}")
        return "", False

def clean_json_response(raw_text: str) -> dict:
    """Safely extracts JSON from an LLM response string."""
    if not raw_text:
        return {}
    
    # Clean markdown codeblocks like ```json ... ```
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try finding json object inside brackets
        match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
        return {}

def compute_career_match_stats(student_skills: list[dict], target_career: str) -> dict:
    """
    Calculates exact skill match, missing skills, and career readiness stats.
    """
    career_info = CAREER_ROLES.get(target_career, CAREER_ROLES["Full Stack Developer"])
    core_skills = set(career_info.get("core_skills", []))
    advanced_skills = set(career_info.get("advanced_skills", []))
    all_required = core_skills.union(advanced_skills)

    student_skill_map = {s["skill_name"].lower(): s["proficiency_level"] for s in student_skills if s.get("is_existing", 1)}

    matched_core = []
    missing_core = []
    for req in core_skills:
        if req.lower() in student_skill_map:
            matched_core.append(req)
        else:
            missing_core.append(req)

    matched_adv = []
    missing_adv = []
    for adv in advanced_skills:
        if adv.lower() in student_skill_map:
            matched_adv.append(adv)
        else:
            missing_adv.append(adv)

    # Core skill match is 70% of match weight, advanced is 30%
    core_ratio = len(matched_core) / max(len(core_skills), 1)
    adv_ratio = len(matched_adv) / max(len(advanced_skills), 1) if advanced_skills else 1.0

    match_percentage = int((core_ratio * 75) + (adv_ratio * 25))
    match_percentage = min(100, max(5, match_percentage))

    return {
        "target_career": target_career,
        "match_percentage": match_percentage,
        "matched_core": matched_core,
        "missing_core": missing_core,
        "matched_adv": matched_adv,
        "missing_adv": missing_adv,
        "total_required": len(all_required),
        "total_acquired": len(matched_core) + len(matched_adv),
        "gap_count": len(missing_core) + len(missing_adv)
    }
