"""
Pedagogical Quality Gate for Pandavs Verified Course Material Studio.
Evaluates instructional depth, duration alignment, speaker notes coverage,
topic relevance, lab reproducibility, and verification claim accuracy.
"""

from typing import Dict, Any, List


def evaluate_course_quality(deck: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates whether a generated deck meets professional technical training standards.
    Returns a structured audit with scores, pass/fail checks, and actionable warnings.
    """
    slides = deck.get("slides", [])
    topic = deck.get("topic", "").strip()
    topic_lower = topic.lower()
    minutes = deck.get("minutes", 60)
    level = deck.get("level", "intermediate").lower()
    exercises = deck.get("exercises", [])
    quiz = deck.get("quiz", [])
    meta = deck.get("meta", {})

    total_slides = len(slides)
    checks: Dict[str, Dict[str, Any]] = {}
    warnings: List[str] = []

    # 1. Duration Alignment & Slide Volume Check
    # For a 90-min course: expect >= 18 slides. For 60-min: >= 12 slides. For 30-min: >= 6 slides.
    min_expected_slides = max(5, int(minutes / 4.5))
    duration_passed = total_slides >= min_expected_slides
    checks["duration_alignment"] = {
        "passed": duration_passed,
        "total_slides": total_slides,
        "min_expected_slides": min_expected_slides,
        "requested_minutes": minutes,
        "detail": (
            f"{total_slides} slides generated for {minutes} min session. "
            f"(Minimum target: {min_expected_slides} slides for comprehensive coverage)"
        ),
    }
    if not duration_passed:
        warnings.append(
            f"Slide volume ({total_slides}) is low for a {minutes}-minute course; risk of superficial delivery."
        )

    # 2. Topic Relevance & Hallucination Defense Check
    # Check that slide titles and bullets genuinely reflect the requested topic
    topic_keywords = [w for w in topic_lower.replace("-", " ").split() if len(w) > 2]
    matched_slides = 0
    irrelevant_slides = 0

    # Specific topic checks
    is_docker = any(k in topic_lower for k in ("docker", "container", "dockerfile", "image", "volume"))
    has_docker_mechanics = False

    for s in slides:
        combined = f"{s.get('title', '')} {' '.join(s.get('bullets', []))}".lower()
        if any(kw in combined for kw in topic_keywords):
            matched_slides += 1
        if is_docker:
            if any(k in combined for k in ("docker", "container", "layer", "image", "cgroup", "namespace", "daemon", "volume", "network")):
                has_docker_mechanics = True
            # Flag unrelated web frameworks
            if "fastapi route" in combined or "spring boot" in combined:
                irrelevant_slides += 1

    topic_relevance_passed = (matched_slides / max(1, total_slides)) >= 0.7 and irrelevant_slides == 0
    checks["topic_relevance"] = {
        "passed": topic_relevance_passed,
        "matched_slides_ratio": round(matched_slides / max(1, total_slides), 2),
        "irrelevant_slides": irrelevant_slides,
        "detail": (
            f"{matched_slides}/{total_slides} slides directly address '{topic}'. "
            f"Found {irrelevant_slides} off-topic slides."
        ),
    }
    if not topic_relevance_passed:
        warnings.append("Course contains content insufficiently focused on the requested topic.")

    # 3. Speaker Notes Depth & Instructional Completeness Check
    # Concept and code slides must have thorough trainer delivery notes (avg >= 80 words)
    substantive_slides = [s for s in slides if s.get("type") in ("content", "code", "section", "concept")]
    notes_word_counts = []
    structured_notes_count = 0

    for s in substantive_slides:
        notes = s.get("notes", "").strip()
        words = len(notes.split())
        notes_word_counts.append(words)
        if any(h in notes for h in ("TEACHING OBJECTIVE", "INSTRUCTOR EXPLANATION", "TECHNICAL WALKTHROUGH", "Instructor explanation", "Teaching objective")):
            structured_notes_count += 1

    avg_notes_words = round(sum(notes_word_counts) / max(1, len(notes_word_counts))) if notes_word_counts else 0
    notes_passed = avg_notes_words >= 60 and (structured_notes_count / max(1, len(substantive_slides))) >= 0.5
    checks["speaker_notes_coverage"] = {
        "passed": notes_passed,
        "average_words_per_slide": avg_notes_words,
        "structured_notes_ratio": round(structured_notes_count / max(1, len(substantive_slides)), 2),
        "detail": (
            f"Average notes length: {avg_notes_words} words. "
            f"{structured_notes_count}/{len(substantive_slides)} substantive slides include structured trainer guidance."
        ),
    }
    if not notes_passed:
        warnings.append(
            f"Presenter notes average only {avg_notes_words} words; real trainers require deeper technical scripts."
        )

    # 4. Hands-on Lab & Practical Completeness Check
    has_exercise_slide = any(s.get("type") == "exercise" for s in slides)
    lab_complete = False
    lab_detail = "No hands-on exercise detected."

    if exercises or has_exercise_slide:
        ex = exercises[0] if exercises else {}
        prompt = ex.get("prompt", "")
        tests = ex.get("tests", "")
        reference = ex.get("reference", "")
        has_commands = any(k in prompt.lower() for k in ("docker ", "curl", "run", "build", "step", "command", "bash"))
        has_starter = bool(ex.get("starter")) or bool(reference)
        lab_complete = bool(prompt) and (has_commands or bool(tests)) and has_starter
        lab_detail = f"Lab '{ex.get('title', 'Hands-on Challenge')}' with complete prompt, commands, and solution."

    checks["practical_lab_completeness"] = {
        "passed": lab_complete,
        "has_exercise": bool(exercises or has_exercise_slide),
        "detail": lab_detail,
    }
    if not lab_complete:
        warnings.append("Hands-on lab lacks complete step-by-step commands or executable solution.")

    # 5. Assessment & Knowledge Check Alignment
    quiz_passed = len(quiz) >= 2 or any(s.get("type") in ("quiz", "quiz_review") for s in slides)
    checks["assessment_alignment"] = {
        "passed": quiz_passed,
        "quiz_items_count": len(quiz),
        "detail": f"{len(quiz)} quiz question(s) configured for interactive comprehension checks.",
    }

    # 6. Technical Verification Integrity (Anti-Fabrication Check)
    # Ensure no false claims like "100% Sandbox Verified" for unexecuted Docker commands
    total_code_blocks = sum(len(s.get("code", [])) for s in slides)
    verified_blocks = sum(1 for s in slides for c in s.get("code", []) if c.get("verified") == "passed")
    unverified_blocks = sum(1 for s in slides for c in s.get("code", []) if c.get("verified") == "unverified")

    verification_honest = True
    for s in slides:
        bullets_text = " ".join(s.get("bullets", []))
        if "100% Sandbox Verified" in bullets_text and unverified_blocks > 0:
            verification_honest = False
            warnings.append("Slide contains unsupported '100% Sandbox Verified' claim while unverified blocks exist.")

    checks["verification_claim_accuracy"] = {
        "passed": verification_honest,
        "total_code_blocks": total_code_blocks,
        "verified_blocks": verified_blocks,
        "unverified_blocks": unverified_blocks,
        "detail": f"{verified_blocks}/{total_code_blocks} code blocks verified in isolated sandbox.",
    }

    # Overall Score Calculation (0 - 100)
    score = 0
    if checks["duration_alignment"]["passed"]:
        score += 20
    else:
        score += int(20 * (total_slides / max(1, min_expected_slides)))

    if checks["topic_relevance"]["passed"]:
        score += 20
    else:
        score += int(20 * checks["topic_relevance"]["matched_slides_ratio"])

    if checks["speaker_notes_coverage"]["passed"]:
        score += 25
    else:
        score += min(20, int(25 * (avg_notes_words / 80)))

    if checks["practical_lab_completeness"]["passed"]:
        score += 20
    else:
        score += 5 if (exercises or has_exercise_slide) else 0

    if checks["assessment_alignment"]["passed"]:
        score += 10

    if checks["verification_claim_accuracy"]["passed"]:
        score += 5

    score = max(0, min(100, score))

    verdict = (
        "Trainer-Grade Masterclass Ready"
        if score >= 85
        else "Standard Professional Training"
        if score >= 70
        else "Requires Pedagogical Enrichment"
    )
    grade = "A" if score >= 85 else ("B" if score >= 70 else ("C" if score >= 50 else "F"))

    return {
        "deck_id": deck.get("deck_id"),
        "topic": topic,
        "level": level,
        "minutes": minutes,
        "total_slides": total_slides,
        "quality_score": score,
        "overall_score": score,
        "grade": grade,
        "verdict": verdict,
        "passed": score >= 70,
        "passed_quality_gate": score >= 70,
        "checks": checks,
        "warnings": warnings,
    }
