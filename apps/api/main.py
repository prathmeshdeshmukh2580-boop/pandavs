"""Verified Course Material Studio - API / orchestrator."""
import os
import sys
import uuid
import json
import logging
import time
from pathlib import Path

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse, HTMLResponse

from apps.api.config import settings
from apps.api.models import (
    CreateDeckRequest, VerifyRequest, VerifyResponse,
    RegenerateSlideRequest, UpgradeFrameworkRequest,
    StartSelfHealRequest, AddToDeckRequest
)
from apps.api.store import DeckStore
from apps.api.generator import CourseGenerator, _patch_deck
from apps.api.generator import check_ollama_health as _check_ollama_health
from apps.api.schema_util import deck_errors
from services.verifier.theater import theater_service, DEMO_EXAMPLES


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import the full orchestrator (needs Docker services).
# If it fails, fall back to a lightweight mode that can still generate decks.
_orchestrator = None
try:
    from apps.api.orchestrator import Orchestrator as _OrchestratorClass
    _ORCHESTRATOR_AVAILABLE = True
except ImportError as _import_err:
    logger.warning("Full orchestrator unavailable (%s); running in lightweight mode.", _import_err)
    _ORCHESTRATOR_AVAILABLE = False

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Zero-trust course material generation and sandbox verification pipeline API",
)

# CORS Middleware (Allows Next.js frontend or any client)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize store and (optionally) orchestrator
store = DeckStore()
if _ORCHESTRATOR_AVAILABLE:
    try:
        _orchestrator = _OrchestratorClass(store=store)
    except Exception as _init_err:
        logger.warning("Orchestrator initialisation failed (%s); lightweight mode.", _init_err)
        _orchestrator = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index_page():
    index_file = Path(__file__).resolve().parent.parent / "web" / "public" / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Verified Course Material Studio API is running.</h1>"


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ollama_available": _check_ollama_health(),
        "gemini_available": bool(getattr(settings, "GEMINI_API_KEY", "")),
        "orchestrator_available": _orchestrator is not None,
        "sandbox_timeout_sec": settings.SANDBOX_TIMEOUT_SEC,
        "max_fix_attempts": settings.MAX_FIX_ATTEMPTS,
    }


@app.post("/verify", response_model=VerifyResponse)
def verify_snippet(req: VerifyRequest):
    """Run one snippet in the sandbox; returns status, stdout, stderr, duration, cached flag."""
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="Sandbox verifier not available in lightweight mode.")
    res = _orchestrator.runner.verify_snippet(
        lang=req.language,
        version=req.version,
        code=req.code,
        kind=req.kind or "spring-fragment",
        expected_output=req.expected_output,
    )
    return VerifyResponse(
        status=res["status"],
        stdout=res.get("stdout", ""),
        stderr=res.get("stderr", ""),
        duration_ms=res.get("duration_ms", 0.0),
        cached=res.get("cached", False),
        returncode=res.get("returncode", 0 if res["status"] == "passed" else 1),
    )


@app.post("/decks", status_code=202)
async def create_deck(req: CreateDeckRequest, background_tasks: BackgroundTasks):
    """
    Start generation from topic, level, minutes; returns deck_id immediately.
    Uses the full orchestrator pipeline when available, otherwise generates
    the deck synchronously using the CourseGenerator (Gemini / deterministic).
    """
    deck_id = f"d_{uuid.uuid4().hex[:8]}"

    if _orchestrator is not None:
        # Full pipeline: Planner -> Generator -> Verifier -> Renderer (async)
        store.save_deck(
            deck_id=deck_id,
            deck_data={
                "deck_id": deck_id,
                "topic": req.topic,
                "level": req.level,
                "minutes": req.minutes,
                "slides": [],
                "exercises": [],
            },
            status="processing",
        )
        background_tasks.add_task(
            _orchestrator.run_pipeline,
            deck_id=deck_id,
            topic=req.topic,
            level=req.level,
            minutes=req.minutes,
            stack=req.stack,
        )
        return {"deck_id": deck_id, "status": "processing", "events_url": f"/decks/{deck_id}/events"}

    # Lightweight mode — generate deck synchronously via CourseGenerator
    try:
        generator = CourseGenerator()
        plan = {
            "deck_id": deck_id,
            "topic": req.topic,
            "level": req.level,
            "minutes": req.minutes,
            "stack": req.stack,
        }
        deck = generator.generate_deck(plan)
        deck["deck_id"] = deck_id

        # Validate against schema (warn but don't block)
        errors = deck_errors(deck)
        if errors:
            logger.warning("Generated deck has schema warnings: %s", errors)
            deck.setdefault("meta", {})
            deck["meta"]["validation_warnings"] = errors

        store.save_deck(deck_id=deck_id, deck_data=deck, status="ready")
        logger.info("Deck %s generated successfully (lightweight mode).", deck_id)

        return {"deck_id": deck_id, "status": "generated"}

    except Exception as exc:
        logger.error("Deck generation failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}")


@app.get("/decks/{deck_id}/events")
async def get_deck_events(deck_id: str):
    """SSE stream of stage progress for real-time live UI updates."""
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="SSE events not available in lightweight mode.")
    return StreamingResponse(
        _orchestrator.stream_events(deck_id),
        media_type="text/event-stream",
    )


@app.get("/decks/{deck_id}")
def get_deck(deck_id: str):
    """Deck JSON with per-slide verification status."""
    deck = store.get_deck(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail=f"Deck '{deck_id}' not found")
    return deck


@app.post("/decks/{deck_id}/slides/{slide_id}/regenerate")
def regenerate_slide(deck_id: str, slide_id: str, req: Optional[RegenerateSlideRequest] = None):
    """Regenerate one slide, re-verify, re-render only it."""
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="Regeneration not available in lightweight mode.")
    try:
        hint = req.prompt_hint if req else ""
        slide = _orchestrator.regenerate_slide(deck_id, slide_id, hint)
        return {"status": "regenerated", "slide": slide}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decks/{deck_id}/upgrade")
def upgrade_framework(deck_id: str, req: UpgradeFrameworkRequest):
    """Upgrade to a newer framework version; returns diff report and re-verifies code."""
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="Upgrade not available in lightweight mode.")
    try:
        report = _orchestrator.upgrade_framework(deck_id, req.target_stack)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/decks/{deck_id}/report")
def get_report(deck_id: str, format: Optional[str] = "json"):
    """Verification report (JSON and interactive HTML view)."""
    report = store.get_report(deck_id)
    deck = store.get_deck(deck_id)
    if not report or not deck:
        raise HTTPException(status_code=404, detail=f"Report for deck '{deck_id}' not found")
    if format == "html" and _orchestrator is not None:
        html_file = settings.DATA_DIR / "exports" / f"{deck_id}_verification_report.html"
        if not html_file.exists():
            _orchestrator.exporter.export_html_report(report, deck)
        return FileResponse(html_file, media_type="text/html", filename=f"{deck_id}_report.html")
    return report


@app.get("/decks/{deck_id}/export")
def export_deck(deck_id: str, format: str = Query("pptx")):
    """Download the generated presentation in PPTX format."""
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="Export not available in lightweight mode.")
    deck = store.get_deck(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail=f"Deck '{deck_id}' not found")
    pptx_file = settings.DATA_DIR / "exports" / f"{deck_id}.pptx"
    if not pptx_file.exists():
        _orchestrator.exporter.export_pptx(deck)
    return FileResponse(
        pptx_file,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"{deck_id}.pptx",
    )


@app.get("/decks")
def list_decks():
    """List all generated and cached decks."""
    return store.list_decks()


# ===================================================================
# AI Code Verification & Self-Healing Theater Endpoints
# ===================================================================

@app.get("/api/self-heal/examples")
def list_self_heal_examples():
    """Returns allowlisted controlled failure demo examples."""
    return [
        {
            "id": ex["id"],
            "name": ex["name"],
            "description": ex["description"],
            "lang": ex["lang"],
            "version": ex["version"],
            "original_code": ex["original_code"],
            "test_code": ex["test_code"],
        }
        for ex in DEMO_EXAMPLES.values()
    ]


@app.post("/api/self-heal/demo", status_code=202)
async def start_self_heal_demo(
    background_tasks: BackgroundTasks,
    req: Optional[StartSelfHealRequest] = None,
):
    """
    Starts a controlled failure demonstration and launches real sandbox execution
    and self-healing in the background.
    """
    example_id = req.example_id if (req and req.example_id) else "python_add"
    try:
        run = theater_service.create_run(example_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    background_tasks.add_task(theater_service.run_theater_pipeline, run["run_id"])
    return {
        "status": "started",
        "run_id": run["run_id"],
        "example_id": example_id,
        "example_name": run["example_name"],
        "demo_type": run["demo_type"],
    }


@app.get("/api/self-heal/{run_id}")
def get_self_heal_run(run_id: str):
    """Returns current status, execution results, diff, and logs for a self-heal run."""
    run = theater_service.runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Self-heal run '{run_id}' not found")
    return run


@app.get("/api/self-heal/{run_id}/events")
async def stream_self_heal_events(run_id: str):
    """Streams real-time SSE progress events for a self-heal demonstration run."""
    if run_id not in theater_service.runs:
        raise HTTPException(status_code=404, detail=f"Self-heal run '{run_id}' not found")
    return StreamingResponse(
        theater_service.stream_events(run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/api/self-heal/{run_id}/add-to-deck")
def add_self_heal_to_deck(run_id: str, req: Optional[AddToDeckRequest] = None):
    """
    Appends the successfully verified repaired snippet to an existing or new course deck.
    """
    run = theater_service.runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Self-heal run '{run_id}' not found")
    if run.get("verified") != "passed":
        raise HTTPException(status_code=400, detail="Only successfully verified snippets can be added to course decks.")

    target_deck_id = (req.deck_id if req and req.deck_id else None) or "d_001"
    deck = store.get_deck(target_deck_id)
    if not deck:
        target_deck_id = f"d_{uuid.uuid4().hex[:8]}"
        deck = {
            "deck_id": target_deck_id,
            "topic": f"Verified Code: {run['example_name']}",
            "level": "intermediate",
            "minutes": 30,
            "stack": {run["lang"]: run["version"]},
            "slides": [],
            "exercises": [],
            "quiz": [],
            "cheat_sheet": "",
            "meta": {"source": "self-healing-theater"},
        }

    slide_index = len(deck.get("slides", [])) + 1
    new_slide = {
        "id": f"s_{slide_index:03d}",
        "type": "code",
        "title": f"Verified: {run['example_name']}",
        "bullets": [
            "Self-healed & verified in isolated execution sandbox",
            f"Repaired via {run.get('repair_provider', 'self-healer')} ({run.get('repair_model', 'unknown')})",
            "100% test assertions passed",
        ],
        "code": [
            {
                "id": f"c_{slide_index:03d}_1",
                "lang": run["lang"],
                "version": run["version"],
                "kind": "plain",
                "source": run["repaired_code"],
                "verified": "passed",
                "attempts": run.get("repair_attempts", 1),
            }
        ],
        "diagram": None,
        "notes": f"Originally failed execution. Repaired via {run.get('repair_provider')} and verified against unit test suite.",
    }
    deck["slides"].append(new_slide)
    deck = _patch_deck(deck, run["lang"], run["version"])
    store.save_deck(target_deck_id, deck, status="ready")

    return {
        "status": "added",
        "deck_id": target_deck_id,
        "slide_id": new_slide["id"],
        "slide_title": new_slide["title"],
        "slides_count": len(deck["slides"]),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host=settings.HOST, port=settings.PORT, reload=True)
