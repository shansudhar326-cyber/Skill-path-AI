"""
Verification and Test Suite for SkillPath AI
Tests all agents, database operations, adaptive learning loops, and roadmap adaptations.
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import (
    init_db, seed_demo_student, authenticate_student, get_student_by_id,
    get_student_skills, get_roadmap, get_challenges_for_student,
    get_recent_submissions, get_active_rescue_plans, reset_student_to_demo
)
from agents.orchestrator import AgentOrchestrator

def run_tests():
    print("==================================================")
    print("🧪 Running SkillPath AI End-to-End Validation...")
    print("==================================================")

    # 1. Database Init & Demo Student Seed
    print("\n[Step 1] Initializing Database & Seeding M. Sudharshan...")
    init_db()
    seed_demo_student()
    user = authenticate_student("M.Sudharshan", "sudharsh390")
    assert user is not None, "Failed to authenticate demo student!"
    assert user["full_name"] == "M. Sudharshan", f"Expected M. Sudharshan, got {user['full_name']}"
    assert user["target_career"] == "Full Stack Developer", "Career mismatch"
    print("✅ Demo user authenticated successfully.")

    student_id = user["id"]

    # 2. Check Existing Skills
    skills = get_student_skills(student_id)
    skill_names = [s["skill_name"] for s in skills]
    print(f"✅ Existing Skills: {skill_names}")
    assert "Python" in skill_names and "SQL" in skill_names and "HTML5" in skill_names, "Missing baseline skills!"

    # 3. Test Full Multi-Agent Diagnostic Cycle
    print("\n[Step 2] Running Multi-Agent Diagnostic Cycle...")
    orchestrator = AgentOrchestrator()
    diag = orchestrator.run_full_diagnosis(student_id)
    
    assert "dna" in diag, "Missing Skill DNA in diagnosis"
    assert "missing_skills" in diag["dna"], "Missing skills list not found"
    assert "JavaScript" in diag["dna"]["missing_skills"], "JavaScript should be flagged as missing"
    assert "React" in diag["dna"]["missing_skills"], "React should be flagged as missing"
    print(f"✅ Skill DNA correctly flagged missing skills: {diag['dna']['missing_skills']}")

    assert "prediction" in diag, "Missing Career Prediction in diagnosis"
    print(f"✅ Career Prediction Compatibility: {diag['prediction']['target_stats']['match_percentage']}%")

    assert "readiness" in diag, "Missing Career Readiness in diagnosis"
    print(f"✅ Career Readiness Score: {diag['readiness']['overall_score']}% ({diag['readiness']['tier']})")

    # 4. Test AI Career Simulator: 30% Score & Learning Rescue Flow
    print("\n[Step 3] Testing AI Career Simulator & Adaptive Rescue Flow...")
    challenges = get_challenges_for_student(student_id, role="Full Stack Developer")
    assert len(challenges) > 0, "No challenges found for Full Stack Developer!"
    target_challenge = challenges[0]
    print(f"Selected challenge: {target_challenge['title']}")

    # Submit weak attempt to trigger 30% score & rescue
    weak_code = """
    // Basic unfinished code
    var x = 1;
    function checkLogin() {
        alert('logging in');
    }
    """
    res = orchestrator.evaluate_and_orchestrate_submission(
        student_id=student_id,
        challenge=target_challenge,
        code_submission=weak_code,
        student_notes="Testing low score trigger"
    )

    score = res["evaluation"]["score"]
    print(f"Evaluation Score: {score}/100")
    assert score <= 40, f"Expected low score (<= 40), got {score}"
    assert res["rescue_triggered"] is True, "Learning rescue should have been triggered!"
    print("✅ Learning Rescue Agent successfully triggered!")

    # Verify Rescue Module in Roadmap
    active_rescues = get_active_rescue_plans(student_id)
    assert len(active_rescues) > 0, "Active rescue plan should be stored in DB!"
    print(f"✅ Active Rescue Plan: {active_rescues[0]['weak_topic']}")
    print(f"   Explanation: {active_rescues[0]['explanation_simple'][:120]}...")

    roadmap = get_roadmap(student_id)
    assert any("rescue" in item["topic"].lower() or item["status"] == "Rescue" for item in roadmap), "Rescue module not found in roadmap!"
    print(f"✅ Rescue Module successfully injected into learning roadmap!")

    # 5. Test Career Pivot Flow: Switch to Data Analyst
    print("\n[Step 4] Testing Career Pivot to Data Analyst...")
    pivot_res = orchestrator.on_career_goal_changed(student_id, "Data Analyst")
    assert pivot_res["status"] == "success", "Career pivot failed"
    
    updated_student = get_student_by_id(student_id)
    assert updated_student["target_career"] == "Data Analyst", "Target career not updated in DB"
    
    updated_roadmap = get_roadmap(student_id)
    assert any("pandas" in item["skill_target"].lower() or "sql" in item["skill_target"].lower() for item in updated_roadmap), "Roadmap should have adapted for Data Analyst!"
    print("✅ Career goal pivoted and new Data Analyst roadmap generated!")

    # 6. Reset back to demo state
    print("\n[Step 5] Testing State Reset...")
    reset_student_to_demo(student_id)
    reset_student = get_student_by_id(student_id)
    assert reset_student["target_career"] == "Full Stack Developer", "Failed to reset to Full Stack Developer"
    print("✅ Clean demo state restored successfully.")

    print("\n==================================================")
    print("🎉 ALL TEST SUITES PASSED! SkillPath AI is 100% OPERATIONAL.")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
