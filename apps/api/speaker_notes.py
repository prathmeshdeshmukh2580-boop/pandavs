"""
Trainer-Grade Speaker Notes Generator for Pandavs Course Studio.
Produces substantive, human-quality presenter scripts (150-300+ words)
covering objectives, explanation, technical walkthrough, demonstrations,
probing questions, misconceptions, troubleshooting runbooks, and transitions.
"""

from typing import Dict, Any, List, Optional


def build_trainer_delivery_notes(
    slide_title: str,
    slide_type: str,
    bullets: List[str],
    topic: str,
    level: str = "intermediate",
    pro_tip: Optional[str] = None,
    code_snippet: Optional[str] = None,
    module_name: Optional[str] = None,
    time_minutes: int = 4,
    custom_guidance: Optional[Dict[str, str]] = None,
) -> str:
    """
    Constructs a comprehensive, trainer-grade delivery note string.
    Follows TechSummitTrainers pedagogical guidelines.
    """
    bullets_text = " ".join(bullets)
    custom = custom_guidance or {}

    # Teaching Objective
    obj = custom.get(
        "objective",
        f"Ensure learners understand the architectural mechanisms, trade-offs, and operational commands associated with '{slide_title}'.",
    )

    # Explanation Script (100 - 200 words)
    exp = custom.get("explanation")
    if not exp:
        if slide_type == "title":
            exp = (
                f"Welcome learners to this {level}-level technical training on '{topic}'. "
                "Set expectations upfront: this session moves beyond high-level syntax into production internals, "
                "reproducible workflows, and zero-trust verification. Emphasize that every code block and architecture pattern "
                "presented has been battle-tested against real enterprise workloads."
            )
        elif slide_type == "code":
            exp = (
                f"Walk students through the concrete code implementation on screen. Explain the mental model behind "
                f"each statement and how it adheres to the invariants of {topic}. Emphasize separation of concerns, "
                "resource disposal, defensive parameter validation, and how errors propagate up the call stack. "
                "Contrast this idiomatic approach against fragile rookie implementations often found in sample code."
            )
        elif slide_type == "exercise":
            exp = (
                "Introduce the hands-on lab. Instruct learners to read the functional acceptance criteria and test contract "
                "before writing their first line of code. Emphasize the 'Tests Must Bite' principle: the test suite is engineered "
                "to catch subtle regressions, boundary conditions, and unhandled exceptions. Circulate actively and prompt "
                "students who get stuck on initial environment setup."
            )
        else:
            exp = (
                f"Explain the foundational mechanics of '{slide_title}'. Guide students through the technical bullets on screen: "
                f"{'; '.join(bullets[:3])}. Clarify why this pattern exists in modern systems, how the underlying operating system "
                "or runtime enforces it, and what happens at scale when teams neglect this invariant. Connect the theory to "
                "concrete operational cost, system availability, and incident post-mortems."
            )

    # Technical Walkthrough
    walk = custom.get("walkthrough")
    if not walk:
        if code_snippet:
            walk = (
                f"Highlight lines in the code snippet. Note specific parameter choices, error handlers, and return signatures. "
                f"Demonstrate how input arguments are sanitized and how exceptions are caught cleanly."
            )
        elif bullets:
            walk = (
                f"Deep-dive into each point: Point 1 ({bullets[0] if bullets else ''}) establishes the system invariant. "
                f"Point 2 ({bullets[1] if len(bullets) > 1 else ''}) illustrates the runtime execution path. "
                f"Point 3 ({bullets[2] if len(bullets) > 2 else ''}) enforces production reliability."
            )
        else:
            walk = "Walk through the architectural topology step by step, illustrating data flow from entrypoint to persistence."

    # Demonstration & Observations
    demo = custom.get(
        "demonstration",
        "Demonstrate the command or pattern live in the terminal. Point out exit codes, stdout logs, and state verification.",
    )
    obs = custom.get(
        "observations",
        "Learners should observe clean execution without warnings, expected structured log output, and deterministic behavior.",
    )

    # Questions to Ask
    questions = custom.get("questions")
    if not questions:
        questions = (
            f"1. What is the single biggest operational risk if this pattern is misconfigured?\n"
            f"   Expected: Resource leakage, cascade failures, or unauthenticated exposure.\n"
            f"2. How does this behavior differ under high concurrent load versus single-user testing?\n"
            f"   Expected: Race conditions, lock contention, or connection pool exhaustion."
        )

    # Common Misconceptions
    misconceptions = custom.get(
        "misconceptions",
        "Learners frequently mistake declarative configuration for runtime guarantees, or assume defaults are production-ready.",
    )

    # Troubleshooting & Failure Modes
    troubleshooting = custom.get(
        "troubleshooting",
        "Symptom: Process crashes or hangs silently. Solution: Inspect stderr, check resource limits (memory/CPU), and verify network port bindings.",
    )

    # Transition
    transition = custom.get(
        "transition",
        "With this invariant established, let us examine how this connects to the next architectural component in the pipeline.",
    )

    # Pro-tip addition
    pt_block = f"\n\nTECHSUMMIT PRO-TIP:\n{pro_tip}" if pro_tip else ""

    return (
        f"TEACHING OBJECTIVE:\n{obj}\n\n"
        f"INSTRUCTOR EXPLANATION:\n{exp}\n\n"
        f"TECHNICAL WALKTHROUGH:\n{walk}\n\n"
        f"DEMONSTRATION & OBSERVATIONS:\nShow: {demo}\nObserve: {obs}\n\n"
        f"QUESTIONS TO ASK LEARNERS:\n{questions}\n\n"
        f"COMMON MISCONCEPTIONS:\n{misconceptions}\n\n"
        f"TROUBLESHOOTING & FAILURE MODES:\n{troubleshooting}\n\n"
        f"TRANSITION:\n{transition}\n\n"
        f"TIME ALLOCATION:\nSuggested Pacing: {time_minutes} minutes"
        f"{pt_block}"
    )
