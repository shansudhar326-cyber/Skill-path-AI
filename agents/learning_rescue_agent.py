"""
Learning Rescue Agent
Identifies weak topics from failed or low-scoring assessments,
deconstructs difficult concepts into beginner-friendly explanations,
recommends targeted tutorials, generates scaffolded practice exercises,
and updates the roadmap to prevent premature advancement into dependent skills.
"""

from SkillPath_AI.utils.helpers import call_gemini, clean_json_response

class LearningRescueAgent:
    def __init__(self):
        self.name = "Learning Rescue Agent"
        self.role = "Adaptive Remediation & Concept Simplification Specialist"

    def formulate_rescue_plan(self, weak_topic: str, score: int, context_notes: str = "", downstream_skill: str = "React") -> dict:
        """
        Formulates a comprehensive rescue and remediation package for a student struggling with a topic.
        Example: 30% score on JavaScript -> simplifies JS event loop/scope, provides tutorials,
        practice questions, and locks downstream skill (React) until fundamentals are solidified.
        """
        prompt = f"""
        A student scored {score}% on an assessment/challenge focused on: '{weak_topic}'.
        They are aiming for a career where downstream advanced skill '{downstream_skill}' depends heavily on this foundation.

        Generate a complete Learning Rescue Package in JSON format:
        {{
            "weak_concept_diagnosis": "Explain exactly why students struggle with this and what core misunderstanding occurred",
            "simplified_explanation": "Explain the concept in simple, intuitive, non-jargon language using a vivid real-world analogy (ELI5 style)",
            "key_rules_to_remember": [
                "Rule 1 in plain English",
                "Rule 2 in plain English",
                "Rule 3 in plain English"
            ],
            "recommended_tutorials": [
                {{
                    "title": "Tutorial title",
                    "platform": "YouTube / MDN / FreeCodeCamp",
                    "url": "https://...",
                    "duration": "e.g. 25 mins"
                }}
            ],
            "practice_exercises": [
                {{
                    "level": "Step 1: Foundational",
                    "task": "Specific mini task",
                    "hint": "Helpful hint"
                }},
                {{
                    "level": "Step 2: Practical",
                    "task": "Specific task requiring logic",
                    "hint": "Helpful hint"
                }},
                {{
                    "level": "Step 3: Verification",
                    "task": "Mini challenge to verify mastery before moving to " + downstream_skill,
                    "hint": "Helpful hint"
                }}
            ],
            "roadmap_intervention": {{
                "action": "INSERT_RESCUE_MODULE",
                "module_title": f"Rescue Sprint: {weak_topic} Remediation & Mastery",
                "prerequisite_warning": f"Hold off on {downstream_skill} until this foundational module achieves >= 75% reassessment."
            }}
        }}
        """

        raw_res, is_real_ai = call_gemini(
            prompt,
            system_instruction="You are an empathetic, world-class computer science educator who specializes in breaking down complex concepts for struggling students.",
            response_json=True
        )

        plan = clean_json_response(raw_res)
        if not plan or not is_real_ai:
            plan = self._generate_fallback_rescue(weak_topic, score, downstream_skill)
            provider_label = "SkillPath Adaptive Rescue Matrix (Demo Mode)"
        else:
            provider_label = "Google Gemini 1.5 Flash"

        plan["provider"] = provider_label
        plan["is_real_ai"] = is_real_ai
        plan["weak_topic"] = weak_topic
        plan["score_trigger"] = score

        return plan

    def _generate_fallback_rescue(self, weak_topic: str, score: int, downstream_skill: str) -> dict:
        """
        High-quality deterministic rescue plan specifically tuned for the user's
        demonstration scenario (JavaScript low score before advancing to React).
        """
        if "javascript" in weak_topic.lower() or "js" in weak_topic.lower():
            return {
                "weak_concept_diagnosis": "Scoring 30% indicates difficulty with asynchronous JavaScript flow, ES6 syntax (destructuring, arrow functions), and DOM event bubbling. Jumping straight into React while shaky on vanilla JavaScript causes severe cognitive overload.",
                "simplified_explanation": "Think of JavaScript like a restaurant kitchen. The Call Stack is the single head chef preparing one dish at a time. The Web APIs and Event Loop are the prep cooks and waitstaff taking orders in the background. If you ask the chef to wait 10 minutes for oven baking without an asynchronous timer, the entire restaurant freezes! Understanding this single-threaded event loop is the secret to everything in JS and React.",
                "key_rules_to_remember": [
                    "Rule 1: Always use 'const' by default and 'let' only when reassigning. Never use 'var'.",
                    "Rule 2: An arrow function '(x) => x * 2' does not bind its own 'this' context.",
                    "Rule 3: Asynchronous code (fetch, promises) never blocks the UI—it waits in the callback queue until the stack clears."
                ],
                "recommended_tutorials": [
                    {
                        "title": "JavaScript Crash Course For Beginners (Traversy Media)",
                        "platform": "YouTube",
                        "url": "https://www.youtube.com/watch?v=hdI2bqOjy3c",
                        "duration": "90 mins"
                    },
                    {
                        "title": "What the heck is the event loop anyway? (Philip Roberts)",
                        "platform": "YouTube / JSConf",
                        "url": "https://www.youtube.com/watch?v=8aGhZQkoFbQ",
                        "duration": "26 mins"
                    },
                    {
                        "title": "MDN JavaScript Basics Interactive Guide",
                        "platform": "MDN Web Docs",
                        "url": "https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/JavaScript_basics",
                        "duration": "Self-paced"
                    }
                ],
                "practice_exercises": [
                    {
                        "level": "Step 1: Foundational Syntax",
                        "task": "Create an array of 5 products with prices and use .filter() and .reduce() to calculate the total cost of items over $20.",
                        "hint": "Remember: .filter returns a new array, while .reduce accumulates a single value."
                    },
                    {
                        "level": "Step 2: Asynchronous Flow",
                        "task": "Write an async function that fetches user data from 'https://jsonplaceholder.typicode.com/users/1' with a try/catch block and logs the username.",
                        "hint": "Use 'await fetch(...)' and don't forget to 'await res.json()'."
                    },
                    {
                        "level": "Step 3: DOM Event Handling",
                        "task": "Build a simple counter button that increments and changes color when it hits 10 without page reload.",
                        "hint": "Use document.querySelector and addEventListener('click', ...)."
                    }
                ],
                "roadmap_intervention": {
                    "action": "INSERT_RESCUE_MODULE",
                    "module_title": "Rescue Sprint: JavaScript Core Foundations & ES6 Mastery",
                    "prerequisite_warning": f"Hold off on {downstream_skill} until this foundational module achieves >= 75% reassessment."
                }
            }
        else:
            return {
                "weak_concept_diagnosis": f"Scoring {score}% indicates foundational gaps in {weak_topic} syntax, mental models, or execution patterns.",
                "simplified_explanation": f"To master {weak_topic}, break it down into atomic components. Learn how data enters, how logic transforms it, and where the output flows.",
                "key_rules_to_remember": [
                    f"Rule 1: Verify data types and inputs before processing in {weak_topic}.",
                    "Rule 2: Keep functions small, focused, and pure.",
                    "Rule 3: Inspect error stack traces carefully rather than guessing."
                ],
                "recommended_tutorials": [
                    {
                        "title": f"{weak_topic} for Beginners - Complete Crash Course",
                        "platform": "FreeCodeCamp / YouTube",
                        "url": f"https://www.youtube.com/results?search_query={weak_topic.replace(' ', '+')}+tutorial+for+beginners",
                        "duration": "45 mins"
                    },
                    {
                        "title": f"Official {weak_topic} Documentation & Getting Started",
                        "platform": "Official Docs",
                        "url": "https://developer.mozilla.org/",
                        "duration": "Self-paced"
                    }
                ],
                "practice_exercises": [
                    {
                        "level": "Step 1: Foundational",
                        "task": f"Write a basic hello-world module implementing core {weak_topic} syntax.",
                        "hint": "Review the official quickstart syntax."
                    },
                    {
                        "level": "Step 2: Practical",
                        "task": f"Build a practical validator utility with error handling using {weak_topic}.",
                        "hint": "Check edge cases like null or empty parameters."
                    }
                ],
                "roadmap_intervention": {
                    "action": "INSERT_RESCUE_MODULE",
                    "module_title": f"Rescue Sprint: {weak_topic} Remediation & Mastery",
                    "prerequisite_warning": f"Review concepts before proceeding to advanced modules."
                }
            }
