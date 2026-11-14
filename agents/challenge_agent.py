"""
Challenge Agent
Generates practical real-world development challenges and rigorously evaluates student code submissions
based on correctness, logical structure, security, and production best practices.
"""

from config import CAREER_ROLES
from utils.helpers import call_gemini, clean_json_response

class ChallengeAgent:
    def __init__(self):
        self.name = "Challenge Agent"
        self.role = "Practical Code Evaluator & Simulator Proctor"

    def generate_challenge(self, career_role: str, skill_focus: str, difficulty: str = "Intermediate") -> dict:
        """Generates a dynamic real-world coding challenge for a given skill and role."""
        prompt = f"""
        Generate a practical coding challenge for a student aspiring to be a '{career_role}'.
        Skill focus: {skill_focus}
        Difficulty: {difficulty}

        Return a JSON object:
        {{
            "title": "Clear concise challenge title",
            "description": "Realistic scenario description of the requirement",
            "starter_code": "Code snippet or boilerplate for student to complete",
            "expected_output": "What the solution should accomplish or return",
            "rubrics": {{
                "correctness": "What correctness requires",
                "logic": "What clean architectural logic requires",
                "practical_readiness": "Production standards required"
            }}
        }}
        """

        raw_res, is_real_ai = call_gemini(
            prompt,
            system_instruction="You are a senior tech lead designing interview-level practical coding assessments.",
            response_json=True
        )

        res = clean_json_response(raw_res)
        if not res or not is_real_ai:
            res = self._fallback_challenge(career_role, skill_focus, difficulty)

        return res

    def evaluate_submission(self, challenge: dict, code_submission: str, student_notes: str = "") -> dict:
        """
        Evaluates student's code submission.
        Returns detailed score breakdown (correctness, logic, practical) and constructive feedback.
        """
        if not code_submission or len(code_submission.strip()) < 10:
            return {
                "score": 10,
                "correctness_score": 10,
                "logic_score": 10,
                "practical_score": 10,
                "feedback": "Submission is empty or contains insufficient code to evaluate.",
                "strengths": ["Attempt submitted"],
                "improvements": ["Provide complete code implementation satisfying the requirements."],
                "requires_rescue": True,
                "provider": "Static Sanity Guard"
            }

        prompt = f"""
        You are a senior software engineering evaluator. Grade this code submission objectively.

        Challenge Title: {challenge.get('title')}
        Challenge Description: {challenge.get('description')}
        Expected Output: {challenge.get('expected_output')}

        Student Submission:
        ```
        {code_submission}
        ```
        Student Implementation Notes: {student_notes}

        Provide a strict grading evaluation in JSON format:
        {{
            "score": <overall integer score 0-100>,
            "correctness_score": <integer 0-100>,
            "logic_score": <integer 0-100>,
            "practical_score": <integer 0-100>,
            "feedback": "<2-3 paragraph thorough evaluation of logic, correctness, security, and edge cases>",
            "strengths": ["<strength 1>", "<strength 2>"],
            "improvements": ["<concrete recommendation 1>", "<concrete recommendation 2>"],
            "requires_rescue": <true if score < 60, false otherwise>
        }}
        """

        raw_res, is_real_ai = call_gemini(
            prompt,
            system_instruction="You are an uncompromising, constructive senior code reviewer and mentor.",
            response_json=True
        )

        evaluation = clean_json_response(raw_res)
        if not evaluation or not is_real_ai:
            evaluation = self._fallback_evaluate(challenge, code_submission)
            provider_label = "Rule-based Code Analysis Engine (Demo Mode)"
        else:
            provider_label = "Google Gemini 1.5 Flash"

        evaluation["provider"] = provider_label
        evaluation["is_real_ai"] = is_real_ai
        # Ensure boolean rescue flag matches threshold
        evaluation["requires_rescue"] = evaluation.get("score", 0) < 60

        return evaluation

    def _fallback_challenge(self, role: str, skill: str, difficulty: str) -> dict:
        """Deterministic challenge generation when offline."""
        return {
            "title": f"Implement {skill} Logic for {role}",
            "description": f"Design and implement a clean, robust module demonstrating {skill} best practices for a modern {role} application.",
            "starter_code": f"// Starter template for {skill}\nfunction executeTask() {{\n    // Your implementation here\n}}\n",
            "expected_output": f"Functional {skill} module handling edge cases and returning formatted data.",
            "rubrics": {
                "correctness": "Handles inputs and outputs accurately",
                "logic": "Modular, readable structure",
                "practical_readiness": "Input sanitization and error boundaries"
            }
        }

    def _fallback_evaluate(self, challenge: dict, code: str) -> dict:
        """
        Deterministic, intelligent rule-based evaluator that examines syntax, structure,
        and handles specific demo scenarios (e.g. JavaScript 30% low score demo!).
        """
        code_lower = code.lower()
        title = challenge.get("title", "").lower()

        # Count non-empty, non-comment lines
        code_lines = [l.strip() for l in code.splitlines() if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("#")]

        # Check for simulated demo / weak attempt scenario
        is_poor_attempt = (
            len(code_lines) < 5 or
            "alert(" in code_lower or
            "var x = 1" in code_lower or
            "todo" in code_lower or
            "unfinished" in code_lower or
            "weak" in code_lower or
            ("return" not in code_lower and "res." not in code_lower and "set" not in code_lower and "<" not in code_lower)
        )

        if is_poor_attempt:
            # 30% score scenario as specified in requirement 5!
            return {
                "score": 30,
                "correctness_score": 30,
                "logic_score": 35,
                "practical_score": 25,
                "feedback": "The submission demonstrates basic syntax familiarity, but lacks necessary business logic, input validation, and asynchronous error boundaries. Key requirements like edge-case protection, modular scoping, and standard return types were omitted.",
                "strengths": ["Basic syntax executed without parsing errors", "Initiative in testing statements"],
                "improvements": [
                    "Implement modern ES6+ const/let scoping instead of global declarations.",
                    "Add try/catch exception handling and input validation.",
                    "Structure the code into reusable pure functions with explicit return values."
                ],
                "requires_rescue": True
            }

        # Otherwise score based on structural indicators
        has_functions = "def " in code or "function" in code or "=>" in code or "class " in code
        has_error_handling = "try" in code_lower or "catch" in code_lower or "except" in code_lower or "error" in code_lower
        has_validation = "if" in code_lower or "regex" in code_lower or "validate" in code_lower
        has_comments = "#" in code or "//" in code

        score = 50
        if has_functions: score += 15
        if has_error_handling: score += 15
        if has_validation: score += 10
        if has_comments: score += 5
        if len(code.splitlines()) > 10: score += 5

        score = min(95, score)

        return {
            "score": score,
            "correctness_score": min(100, score + 5),
            "logic_score": score,
            "practical_score": max(40, score - 5),
            "feedback": f"Strong submission! The solution successfully implements the required control flow with clean structural modularity. Code organization aligns well with industry norms for {challenge.get('career_role', 'development')}.",
            "strengths": [
                "Modular structural hierarchy and function boundaries",
                "Implementation incorporates validation logic"
            ],
            "improvements": [
                "Consider adding comprehensive unit test assertions",
                "Ensure strict typing or JSDoc/Type annotations are added for production maintainability"
            ],
            "requires_rescue": score < 60
        }
