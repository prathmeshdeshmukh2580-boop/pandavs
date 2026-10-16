import asyncio
import datetime
import json
from typing import Dict, Any, AsyncGenerator
from apps.api.config import settings
from apps.api.store import DeckStore
from apps.api.planner import CoursePlanner
from apps.api.generator import CourseGenerator
from services.verifier.runner import SandboxRunner
from services.verifier.prover import ExerciseProver
from services.verifier.self_heal import SelfHealer
from services.renderer.exporter import Exporter

class Orchestrator:
    """
    Coordinates the multi-stage pipeline:
    Trainer Prompt -> Planner -> Generator -> Verifier (Docker/Sandbox) -> Self-Heal -> Renderer -> Export
    Streams live progress over SSE.
    """
    def __init__(self, store: DeckStore):
        self.store = store
        self.planner = CoursePlanner()
        self.generator = CourseGenerator()
        self.runner = SandboxRunner(timeout_sec=settings.SANDBOX_TIMEOUT_SEC)
        self.prover = ExerciseProver(timeout_sec=settings.SANDBOX_TIMEOUT_SEC)
        self.healer = SelfHealer(runner=self.runner, max_attempts=settings.MAX_FIX_ATTEMPTS)
        self.exporter = Exporter(export_dir=str(settings.DATA_DIR / "exports"))
        
        # Event queues per deck_id for SSE streaming
        self.event_queues: Dict[str, asyncio.Queue] = {}

    def get_queue(self, deck_id: str) -> asyncio.Queue:
        if deck_id not in self.event_queues:
            self.event_queues[deck_id] = asyncio.Queue()
        return self.event_queues[deck_id]

    async def emit_event(self, deck_id: str, stage: str, progress: int, message: str, meta: Dict[str, Any] = None):
        q = self.get_queue(deck_id)
        event = {
            "stage": stage,
            "progress": progress,
            "message": message,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "meta": meta or {}
        }
        await q.put(event)

    async def stream_events(self, deck_id: str) -> AsyncGenerator[str, None]:
        q = self.get_queue(deck_id)
        while True:
            try:
                event = await asyncio.wait_for(q.get(), timeout=25.0)
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("stage") in ("complete", "failed"):
                    break
            except asyncio.TimeoutError:
                # SSE heartbeat comment
                yield ": ping\n\n"

    async def run_pipeline(self, deck_id: str, topic: str, level: str, minutes: int, stack: Dict[str, str]) -> Dict[str, Any]:
        """
        Executes complete pipeline with zero-trust verification.
        """
        try:
            # Stage 1: Planner
            await self.emit_event(deck_id, "planner", 15, f"Planning course curriculum for '{topic}'...")
            await asyncio.sleep(0.3)
            plan = self.planner.plan_course(topic, level, minutes, stack)
            plan["deck_id"] = deck_id

            # Stage 2: Generator
            await self.emit_event(deck_id, "generator", 35, "Generating schema-valid slide deck and code blocks...")
            await asyncio.sleep(0.3)
            deck = self.generator.generate_deck(plan)

            # Stage 3: Verifier & Sandbox
            await self.emit_event(deck_id, "verifier", 55, "Executing snippets in isolated sandbox...")
            execution_summary = []
            
            for slide in deck.get("slides", []):
                for block in slide.get("code", []):
                    slide_id = slide["id"]
                    snippet_id = block["id"]
                    lang = block["lang"]
                    ver = block["version"]
                    kind = block.get("kind", "spring-fragment")
                    source = block["source"]
                    expected = block.get("expected_output")

                    await self.emit_event(
                        deck_id, "verifier", 65, 
                        f"Verifying {snippet_id} ({lang} {ver}) on slide {slide_id}...",
                        meta={"slide_id": slide_id, "snippet_id": snippet_id}
                    )

                    res = self.runner.verify_snippet(lang, ver, source, kind, expected)
                    
                    if res["status"] == "passed":
                        block["verified"] = "passed"
                        block["attempts"] = 1
                        block["error_message"] = None
                        execution_summary.append({
                            "snippet_id": snippet_id,
                            "slide_id": slide_id,
                            "lang": lang,
                            "version": ver,
                            "status": "passed",
                            "duration_ms": res.get("duration_ms", 100),
                            "attempts": 1,
                            "cached": res.get("cached", False),
                            "error": None
                        })
                    else:
                        # Trigger Self-Heal Loop
                        await self.emit_event(deck_id, "verifier", 72, f"Snippet {snippet_id} failed sandbox. Initiating self-heal loop...")
                        heal_res = self.healer.heal_snippet(
                            lang=lang,
                            version=ver,
                            code=source,
                            kind=kind,
                            initial_error=res.get("stderr", "Execution error"),
                            expected_output=expected
                        )
                        block["source"] = heal_res["code"]
                        block["verified"] = heal_res["verified"]
                        block["attempts"] = heal_res["attempts"]
                        block["error_message"] = heal_res.get("error_message")

                        execution_summary.append({
                            "snippet_id": snippet_id,
                            "slide_id": slide_id,
                            "lang": lang,
                            "version": ver,
                            "status": heal_res["verified"],
                            "duration_ms": res.get("duration_ms", 150),
                            "attempts": heal_res["attempts"],
                            "cached": False,
                            "error": heal_res.get("error_message")
                        })

            # Exercise Prover ("Tests Must Bite")
            proven_exercises = []
            for ex in deck.get("exercises", []):
                proof = self.prover.prove_exercise(
                    starter=ex.get("starter", ""),
                    tests=ex.get("tests", ""),
                    reference=ex.get("reference", ""),
                    naive=ex.get("naive", "")
                )
                ex["proof"] = {
                    "reference_passes": proof["reference_passes"],
                    "naive_fails": proof["naive_fails"]
                }
                proven_exercises.append({
                    "exercise_id": ex["id"],
                    "title": ex.get("title", ""),
                    "reference_passes": proof["reference_passes"],
                    "naive_fails": proof["naive_fails"],
                    "tests_must_bite": proof["proven"],
                    "status": "proven" if proof["proven"] else "unproven"
                })

            # Compile Verification Report
            total_snippets = len(execution_summary)
            passed_snippets = sum(1 for s in execution_summary if s["status"] == "passed")
            verification_rate = round((passed_snippets / max(1, total_snippets)) * 100, 1)

            report = {
                "deck_id": deck_id,
                "topic": topic,
                "generated_at": datetime.datetime.utcnow().isoformat(),
                "total_slides": len(deck.get("slides", [])),
                "total_snippets": total_snippets,
                "passed": passed_snippets,
                "failed": total_snippets - passed_snippets,
                "unverified": sum(1 for s in execution_summary if s["status"] == "unverified"),
                "verification_rate_pct": verification_rate,
                "sandbox_type": "Docker / Native Isolate",
                "execution_summary": execution_summary,
                "exercises_proven": proven_exercises
            }

            # Stage 4: Renderer
            await self.emit_event(deck_id, "renderer", 85, "Rendering branded PPTX deck and inspection fit-check...")
            pptx_path = self.exporter.export_pptx(deck)
            html_report_path = self.exporter.export_html_report(report, deck)

            # Save in Store
            self.store.save_deck(deck_id, deck, status="ready", report=report)

            # Complete!
            await self.emit_event(
                deck_id, "complete", 100, 
                "Course generation and verification completed successfully!",
                meta={
                    "deck_id": deck_id,
                    "pptx_path": pptx_path,
                    "html_report_path": html_report_path,
                    "verification_rate": verification_rate
                }
            )

            return deck

        except Exception as e:
            await self.emit_event(deck_id, "failed", 0, f"Pipeline error: {str(e)}")
            raise e

    def regenerate_slide(self, deck_id: str, slide_id: str, hint: str = "") -> Dict[str, Any]:
        """
        Regenerates only a single slide, re-verifies code, updates presentation.
        Keeps all other slides unchanged!
        """
        deck = self.store.get_deck(deck_id)
        if not deck:
            raise ValueError(f"Deck '{deck_id}' not found")

        target_slide = None
        for s in deck.get("slides", []):
            if s.get("id") == slide_id:
                target_slide = s
                break

        if not target_slide:
            raise ValueError(f"Slide '{slide_id}' not found in deck '{deck_id}'")

        # Update slide content
        if hint:
            target_slide["notes"] = f"Updated: {hint}. " + target_slide.get("notes", "")
            target_slide["bullets"].append(f"Regenerated focus: {hint[:30]}")
            if len(target_slide["bullets"]) > 5:
                target_slide["bullets"] = target_slide["bullets"][-5:]

        # Re-verify code on this slide
        for block in target_slide.get("code", []):
            res = self.runner.verify_snippet(
                lang=block["lang"],
                version=block["version"],
                code=block["source"],
                kind=block.get("kind", "spring-fragment")
            )
            block["verified"] = res["status"]
            block["attempts"] = 1

        self.store.save_deck(deck_id, deck, status="ready")
        self.exporter.export_pptx(deck)
        return target_slide

    def upgrade_framework(self, deck_id: str, target_stack: Dict[str, str]) -> Dict[str, Any]:
        """
        Upgrades framework version across the entire deck (e.g. Spring Boot 2.7 -> 3.3).
        Produces a diff report and re-verifies all modified code snippets.
        """
        deck = self.store.get_deck(deck_id)
        if not deck:
            raise ValueError(f"Deck '{deck_id}' not found")

        old_stack = dict(deck.get("stack", {}))
        deck["stack"] = target_stack
        diff_changes = []

        is_target_spring3 = "3." in target_stack.get("spring_boot", "") or target_stack.get("spring_boot", "").startswith("3")

        for slide in deck.get("slides", []):
            for block in slide.get("code", []):
                old_code = block["source"]
                if is_target_spring3 and "javax." in old_code:
                    new_code = old_code.replace("javax.validation", "jakarta.validation")
                    new_code = new_code.replace("javax.persistence", "jakarta.persistence")
                    new_code = new_code.replace("javax.servlet", "jakarta.servlet")
                    block["source"] = new_code
                    block["version"] = target_stack.get("java", "21")
                    diff_changes.append({
                        "slide_id": slide["id"],
                        "snippet_id": block["id"],
                        "change": "Migrated javax.* namespace to jakarta.* for Spring Boot 3"
                    })
                # Re-verify upgraded code
                res = self.runner.verify_snippet(
                    lang=block["lang"],
                    version=block["version"],
                    code=block["source"],
                    kind=block.get("kind", "spring-fragment")
                )
                block["verified"] = res["status"]

        self.store.save_deck(deck_id, deck, status="ready")
        self.exporter.export_pptx(deck)

        return {
            "deck_id": deck_id,
            "old_stack": old_stack,
            "new_stack": target_stack,
            "changes_count": len(diff_changes),
            "diff": diff_changes,
            "status": "upgrade_completed"
        }
