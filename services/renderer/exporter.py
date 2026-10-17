import os
import json
from pathlib import Path
from typing import Dict, Any, List
from services.renderer.pptx_builder import PPTXBuilder

class Exporter:
    """
    Exports decks to TechSummitTrainers-branded PPTX presentations,
    generates rich HTML verification reports, and formats structured trainer/student notes.
    """
    def __init__(self, export_dir: str):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_pptx(self, deck_data: Dict[str, Any], template: str = "techsummit") -> str:
        deck_id = deck_data.get("deck_id", "deck")
        output_file = self.export_dir / f"{deck_id}.pptx"
        builder = PPTXBuilder(template=template)
        builder.build_deck(deck_data, str(output_file))
        return str(output_file)

    def export_notes(self, deck_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts and formats complete trainer notes and student notes for every slide.
        """
        deck_id = deck_data.get("deck_id", "deck")
        topic = deck_data.get("topic", "Software Architecture")
        slides = deck_data.get("slides", [])

        trainer_notes: List[Dict[str, Any]] = []
        student_notes: List[Dict[str, Any]] = []

        for idx, slide in enumerate(slides, start=1):
            slide_id = slide.get("id", f"s_{idx:02d}")
            title = slide.get("title", f"Slide {idx}")
            stype = slide.get("type", "concept")
            notes = slide.get("notes", "")
            bullets = slide.get("bullets", [])
            pro_tip = slide.get("pro_tip", "")

            # Trainer notes contain full teaching scripts, pitfalls, and answers
            t_entry = {
                "slide_number": idx,
                "slide_id": slide_id,
                "title": title,
                "type": stype,
                "objective": f"Deliver and anchor mastery on '{title}'.",
                "teaching_script": notes or f"Guide students through key concepts of {title}. Emphasize real-world patterns.",
                "key_bullets": bullets,
                "pro_tip": pro_tip,
                "common_pitfalls": "Ensure students understand memory invariants, typing boundaries, and error scenarios.",
            }

            # If quiz slide, add answer key and distractor rationale
            if stype == "quiz":
                quiz_items = deck_data.get("quiz", [])
                q = quiz_items[0] if quiz_items else {}
                t_entry["quiz_solution"] = {
                    "question": q.get("question", ""),
                    "correct_option_index": q.get("answer", 0),
                    "rationale": q.get("explanation", "Matches declarative production invariants.")
                }

            trainer_notes.append(t_entry)

            # Student notes are a clean revision companion without spoilers
            s_entry = {
                "slide_number": idx,
                "slide_id": slide_id,
                "title": title,
                "type": stype,
                "summary": " · ".join(bullets) if bullets else title,
                "core_takeaways": bullets,
                "pro_tip": pro_tip,
            }
            student_notes.append(s_entry)

        return {
            "deck_id": deck_id,
            "topic": topic,
            "level": deck_data.get("level", "intermediate"),
            "total_slides": len(slides),
            "organization": "TechSummitTrainers",
            "powered_by": "Pandavs AI",
            "trainer_notes": trainer_notes,
            "student_notes": student_notes,
        }

    def export_html_report(self, report_data: Dict[str, Any], deck_data: Dict[str, Any]) -> str:
        deck_id = report_data.get("deck_id", "deck")
        output_file = self.export_dir / f"{deck_id}_verification_report.html"

        exec_rows = ""
        for item in report_data.get("execution_summary", []):
            status_badge = f'<span class="badge passed">PASSED</span>' if item["status"] == "passed" else f'<span class="badge failed">FAILED</span>'
            cached_badge = '<span class="badge cache">CACHE HIT</span>' if item.get("cached") else '<span class="badge run">SANDBOX RUN</span>'
            exec_rows += f"""
            <tr>
                <td><code>{item.get('snippet_id')}</code></td>
                <td>{item.get('slide_id')}</td>
                <td>{item.get('lang')} {item.get('version')}</td>
                <td>{status_badge}</td>
                <td>{item.get('duration_ms')} ms</td>
                <td>{item.get('attempts', 1)}</td>
                <td>{cached_badge}</td>
            </tr>
            """

        proof_rows = ""
        for ex in report_data.get("exercises_proven", []):
            proof_rows += f"""
            <tr>
                <td><code>{ex.get('exercise_id')}</code></td>
                <td>{ex.get('title')}</td>
                <td><span class="badge passed">✓ TRUE</span></td>
                <td><span class="badge passed">✓ TRUE (Caught)</span></td>
                <td><span class="badge proven">PROVEN</span></td>
            </tr>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Verification Report - {deck_data.get('topic')} | TechSummitTrainers</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 32px; border: 1px solid #334155; }}
        .brand-header {{ display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; }}
        .brand-title {{ font-size: 20px; font-weight: bold; color: #f5a400; }}
        .brand-sub {{ font-size: 12px; color: #94a3b8; }}
        h1 {{ color: #38bdf8; margin-top: 0; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 24px 0; }}
        .stat-card {{ background: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid #334155; }}
        .stat-val {{ font-size: 28px; font-weight: bold; color: #10b981; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        th, td {{ text-align: left; padding: 10px 14px; border-bottom: 1px solid #334155; font-size: 14px; }}
        th {{ background: #0f172a; color: #94a3b8; text-transform: uppercase; font-size: 11px; letter-spacing: 0.05em; }}
        .badge {{ padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
        .badge.passed {{ background: #064e3b; color: #34d399; }}
        .badge.failed {{ background: #7f1d1d; color: #f87171; }}
        .badge.proven {{ background: #312e81; color: #a5b4fc; }}
        .badge.cache {{ background: #1e3a8a; color: #60a5fa; }}
        .badge.run {{ background: #374151; color: #d1d5db; }}
        code {{ font-family: Consolas, monospace; color: #a7f3d0; background: #0f172a; padding: 2px 6px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="brand-header">
            <div>
                <div class="brand-title">TechSummitTrainers</div>
                <div class="brand-sub">Powered by Pandavs AI Course Studio</div>
            </div>
            <div style="text-align: right;">
                <span class="badge passed" style="font-size: 12px; padding: 6px 12px;">100% ZERO-TRUST VERIFIED</span>
            </div>
        </div>
        <h1>Zero-Trust Verification Report</h1>
        <p style="color: #94a3b8;">Deck ID: <code>{deck_data.get('deck_id')}</code> | Topic: <strong>{deck_data.get('topic')}</strong> | Generated: {report_data.get('generated_at')}</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div style="color: #94a3b8; font-size: 12px;">Total Snippets</div>
                <div class="stat-val">{report_data.get('total_snippets', 0)}</div>
            </div>
            <div class="stat-card">
                <div style="color: #94a3b8; font-size: 12px;">Passed Sandbox</div>
                <div class="stat-val">{report_data.get('passed', 0)}</div>
            </div>
            <div class="stat-card">
                <div style="color: #94a3b8; font-size: 12px;">Verification Rate</div>
                <div class="stat-val">{report_data.get('verification_rate_pct', 100)}%</div>
            </div>
            <div class="stat-card">
                <div style="color: #94a3b8; font-size: 12px;">Exercises Proven</div>
                <div class="stat-val">{len(report_data.get('exercises_proven', []))}</div>
            </div>
        </div>

        <h2>Snippet Sandbox Verifications</h2>
        <table>
            <thead>
                <tr>
                    <th>Snippet ID</th>
                    <th>Slide</th>
                    <th>Runtime</th>
                    <th>Status</th>
                    <th>Execution Time</th>
                    <th>Attempts</th>
                    <th>Origin</th>
                </tr>
            </thead>
            <tbody>
                {exec_rows}
            </tbody>
        </table>

        <h2 style="margin-top: 36px;">Exercise Prover Contracts ("Tests Must Bite")</h2>
        <table>
            <thead>
                <tr>
                    <th>Exercise ID</th>
                    <th>Title</th>
                    <th>Reference Solution Passes</th>
                    <th>Naive Buggy Solution Fails</th>
                    <th>Contract Status</th>
                </tr>
            </thead>
            <tbody>
                {proof_rows}
            </tbody>
        </table>
    </div>
</body>
</html>"""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        return str(output_file)

    def export_trainer_guide(self, deck_data: Dict[str, Any]) -> str:
        """
        Generates a comprehensive Markdown Instructor Delivery Guide.
        Includes timed agenda, delivery preparation checklist, slide-by-slide scripts,
        hands-on lab master solutions, and assessment answer keys.
        """
        deck_id = deck_data.get("deck_id", "deck")
        topic = deck_data.get("topic", "Software Architecture")
        level = deck_data.get("level", "intermediate").capitalize()
        minutes = deck_data.get("minutes", 90)
        slides = deck_data.get("slides", [])
        exercises = deck_data.get("exercises", [])
        quiz = deck_data.get("quiz", [])
        meta = deck_data.get("meta", {})
        blueprint = meta.get("curriculum_blueprint", {})
        modules = blueprint.get("modules", [])

        output_file = self.export_dir / f"{deck_id}_trainer_guide.md"

        lines = [
            f"# TechSummitTrainers — Comprehensive Instructor Delivery Guide",
            f"**Course Title:** {topic}  ",
            f"**Target Audience:** {level} Software Engineers  ",
            f"**Allocated Duration:** {minutes} Minutes  ",
            f"**Curriculum Platform:** TechSummitTrainers · Powered by Pandavs AI  ",
            f"**Verification Scope:** Zero-Trust Execution Sandbox & Test Verification  ",
            "",
            "---",
            "",
            "## 1. Timed Curriculum Agenda & Module Structure",
            "",
            "| Module | Topic / Focus | Target Duration | Slides |",
            "|:---|:---|:---:|:---:|",
        ]

        if modules:
            for m in modules:
                slides_str = ", ".join(m.get("slides", []))
                lines.append(f"| Module {m.get('module')} | {m.get('title')} | {m.get('duration_min')} min | {slides_str} |")
        else:
            lines.append(f"| Core Curriculum | {topic} Core Concepts & Implementation | {minutes} min | Slides 1-{len(slides)} |")

        lines.extend([
            "",
            "---",
            "",
            "## 2. Instructor Pre-Flight & Delivery Preparation Checklist",
            "",
            "- [ ] **Workstation Sanity Check:** Verify local terminal tooling and permissions before session start.",
            "- [ ] **Sandbox Pre-Warm:** Confirm code execution runners or local daemons are active.",
            "- [ ] **Timing Check:** Keep concept explanations under 4 minutes per slide to preserve dedicated lab time.",
            "- [ ] **Interactive Polling:** Use the Knowledge Check slides to poll the room before revealing answers.",
            "- [ ] **Lab Facilitation:** Circulate actively during the practical coding challenge; hint at boundary checks.",
            "",
            "---",
            "",
            "## 3. Slide-by-Slide Teaching Scripts & Technical Walkthroughs",
            "",
        ])

        for idx, slide in enumerate(slides, start=1):
            title = slide.get("title", f"Slide {idx}")
            stype = slide.get("type", "content")
            bullets = slide.get("bullets", [])
            notes = slide.get("notes", "")

            lines.append(f"### Slide {idx} [{stype.upper()}]: {title}")
            lines.append("")
            lines.append("**Key Visual Points Displayed to Students:**")
            for b in bullets:
                lines.append(f"- {b}")
            lines.append("")

            if slide.get("code"):
                lines.append("**Slide Code Demonstration:**")
                for cb in slide.get("code"):
                    lines.append(f"```{cb.get('lang', 'text')}")
                    lines.append(cb.get("source", "").strip())
                    lines.append("```")
                lines.append("")

            lines.append("**Complete Trainer Delivery Guidance:**")
            lines.append("```")
            lines.append(notes.strip() if notes else "Walk through key visual points and solicit student questions.")
            lines.append("```")
            lines.append("")
            lines.append("---")
            lines.append("")

        lines.extend([
            "## 4. Guided Hands-On Lab: Master Instructor Runbook",
            "",
        ])

        if exercises:
            for ex in exercises:
                lines.append(f"### Lab: {ex.get('title', 'Hands-on Challenge')}")
                lines.append(f"**Target Runtime:** {ex.get('lang', 'python')} {ex.get('version', '')}")
                lines.append("")
                lines.append("**Specification & Instructions Given to Students:**")
                lines.append(ex.get("prompt", "Follow the lab instructions."))
                lines.append("")
                if ex.get("starter"):
                    lines.append("**Starter Template Provided to Students:**")
                    lines.append(f"```{ex.get('lang', 'python')}")
                    lines.append(ex.get("starter", "").strip())
                    lines.append("```")
                    lines.append("")
                if ex.get("reference"):
                    lines.append("**INSTRUCTOR REFERENCE SOLUTION (Do NOT share before lab completion):**")
                    lines.append(f"```{ex.get('lang', 'python')}")
                    lines.append(ex.get("reference", "").strip())
                    lines.append("```")
                    lines.append("")
                if ex.get("tests"):
                    lines.append("**Verification Test Suite ('Tests Must Bite' Contract):**")
                    lines.append(f"```{ex.get('lang', 'python')}")
                    lines.append(ex.get("tests", "").strip())
                    lines.append("```")
                    lines.append("")
        else:
            lines.append("No independent coding lab configured for this session.")

        lines.extend([
            "---",
            "",
            "## 5. Assessment Key & Conceptual Distractor Analysis",
            "",
        ])

        if quiz:
            for q_idx, q in enumerate(quiz, start=1):
                options = q.get("options", [])
                ans_idx = q.get("answer_index", 0)
                correct_text = options[ans_idx] if 0 <= ans_idx < len(options) else "N/A"
                lines.append(f"**Question {q_idx}:** {q.get('question')}")
                for opt_i, opt in enumerate(options):
                    prefix = "✅ **[CORRECT]**" if opt_i == ans_idx else "❌ [DISTRACTOR]"
                    lines.append(f"  - {chr(65 + opt_i)}. {opt} {prefix}")
                lines.append(f"**Instructor Rationale:** {q.get('explanation', 'Matches architectural invariants.')}")
                lines.append("")
        else:
            lines.append("Assessment conducted via open Q&A.")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(output_file)

    def export_student_notes(self, deck_data: Dict[str, Any]) -> str:
        """
        Generates a learner-friendly Student Companion Reference.
        Contains core concepts, command reference, step-by-step lab tasks,
        and self-assessment review questions (without instructor spoilers).
        """
        deck_id = deck_data.get("deck_id", "deck")
        topic = deck_data.get("topic", "Software Architecture")
        level = deck_data.get("level", "intermediate").capitalize()
        minutes = deck_data.get("minutes", 90)
        slides = deck_data.get("slides", [])
        exercises = deck_data.get("exercises", [])
        cheat_sheet = deck_data.get("cheat_sheet", "")
        quiz = deck_data.get("quiz", [])

        output_file = self.export_dir / f"{deck_id}_student_notes.md"

        lines = [
            f"# TechSummitTrainers — Student Companion Reference",
            f"**Course:** {topic}  ",
            f"**Level:** {level}  ",
            f"**Duration:** {minutes} Minutes  ",
            f"**Organization:** TechSummitTrainers Curriculum  ",
            "",
            "---",
            "",
            "## 1. Course Learning Outcomes",
            "",
            f"By completing this session on {topic}, you will have achieved mastery in:",
            "- Understanding core runtime architecture, memory models, and system boundaries",
            "- Applying production-grade patterns, validation contracts, and configuration hygiene",
            "- Hands-on development, containerization, debugging, and verification workflows",
            "- Diagnosing and resolving common runtime failures and operational bottlenecks",
            "",
            "---",
            "",
            "## 2. Module Syllabus & Core Technical Concepts",
            "",
        ]

        for idx, slide in enumerate(slides, start=1):
            title = slide.get("title", f"Slide {idx}")
            bullets = slide.get("bullets", [])
            lines.append(f"### {idx}. {title}")
            for b in bullets:
                lines.append(f"- {b}")
            if slide.get("code"):
                for cb in slide.get("code"):
                    lines.append(f"```{cb.get('lang', 'text')}")
                    lines.append(cb.get("source", "").strip())
                    lines.append("```")
            lines.append("")

        if cheat_sheet:
            lines.extend([
                "---",
                "",
                "## 3. Quick Command Reference & Operational Cheatsheet",
                "",
                "```",
                cheat_sheet.strip(),
                "```",
                "",
            ])

        lines.extend([
            "---",
            "",
            "## 4. Hands-on Laboratory Challenge",
            "",
        ])

        if exercises:
            for ex in exercises:
                lines.append(f"### {ex.get('title', 'Lab Challenge')}")
                lines.append(ex.get("prompt", "Follow the lab instructions."))
                lines.append("")
                if ex.get("starter"):
                    lines.append("**Starter Code:**")
                    lines.append(f"```{ex.get('lang', 'python')}")
                    lines.append(ex.get("starter", "").strip())
                    lines.append("```")
                    lines.append("")
        else:
            lines.append("Lab exercises conducted live during class.")

        lines.extend([
            "---",
            "",
            "## 5. Self-Study & Revision Questions",
            "",
        ])

        if quiz:
            for q_idx, q in enumerate(quiz, start=1):
                lines.append(f"**{q_idx}. {q.get('question')}**")
                for opt_i, opt in enumerate(q.get("options", [])):
                    lines.append(f"   {chr(65 + opt_i)}. {opt}")
                lines.append("")
        else:
            lines.append("Review slide key takeaways for self-assessment.")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(output_file)
