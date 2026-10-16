import os
import sys
import uuid
import asyncio
from pathlib import Path

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from apps.api.config import settings
from apps.api.models import (
    CreateDeckRequest, VerifyRequest, VerifyResponse,
    RegenerateSlideRequest, UpgradeFrameworkRequest
)
from apps.api.store import DeckStore
from apps.api.orchestrator import Orchestrator

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Zero-trust course material generation and sandbox verification pipeline API"
)

# CORS Middleware (Allows Next.js frontend or any client)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize store and orchestrator
store = DeckStore()
orchestrator = Orchestrator(store=store)

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
        "sandbox_timeout_sec": settings.SANDBOX_TIMEOUT_SEC,
        "max_fix_attempts": settings.MAX_FIX_ATTEMPTS
    }

@app.post("/verify", response_model=VerifyResponse)
def verify_snippet(req: VerifyRequest):
    """
    Run one snippet in the sandbox; returns status, stdout, stderr, duration, cached flag.
    """
    res = orchestrator.runner.verify_snippet(
        lang=req.language,
        version=req.version,
        code=req.code,
        kind=req.kind or "spring-fragment",
        expected_output=req.expected_output
    )
    return VerifyResponse(
        status=res["status"],
        stdout=res.get("stdout", ""),
        stderr=res.get("stderr", ""),
        duration_ms=res.get("duration_ms", 0.0),
        cached=res.get("cached", False),
        returncode=res.get("returncode", 0 if res["status"] == "passed" else 1)
    )

@app.post("/decks", status_code=202)
async def create_deck(req: CreateDeckRequest, background_tasks: BackgroundTasks):
    """
    Start generation from topic, level, minutes; returns deck_id immediately.
    Runs Planner -> Generator -> Verifier -> Renderer in background worker with live SSE progress.
    """
    deck_id = f"d_{uuid.uuid4().hex[:8]}"

    # Store initial pending state
    store.save_deck(
        deck_id=deck_id,
        deck_data={"deck_id": deck_id, "topic": req.topic, "level": req.level, "minutes": req.minutes, "slides": [], "exercises": []},
        status="processing"
    )

    # Launch pipeline in background task
    background_tasks.add_task(
        orchestrator.run_pipeline,
        deck_id=deck_id,
        topic=req.topic,
        level=req.level,
        minutes=req.minutes,
        stack=req.stack
    )

    return {
        "deck_id": deck_id,
        "status": "processing",
        "events_url": f"/decks/{deck_id}/events"
    }

@app.get("/decks/{deck_id}/events")
async def get_deck_events(deck_id: str):
    """
    SSE stream of stage progress for real-time live UI updates.
    """
    return StreamingResponse(
        orchestrator.stream_events(deck_id),
        media_type="text/event-stream"
    )

@app.get("/decks/{deck_id}")
def get_deck(deck_id: str):
    """
    Deck JSON with per-slide verification status.
    """
    deck = store.get_deck(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail=f"Deck '{deck_id}' not found")
    return deck

@app.post("/decks/{deck_id}/slides/{slide_id}/regenerate")
def regenerate_slide(deck_id: str, slide_id: str, req: Optional[RegenerateSlideRequest] = None):
    """
    Regenerate one slide, re-verify, re-render only it.
    """
    try:
        hint = req.prompt_hint if req else ""
        slide = orchestrator.regenerate_slide(deck_id, slide_id, hint)
        return {"status": "regenerated", "slide": slide}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/decks/{deck_id}/upgrade")
def upgrade_framework(deck_id: str, req: UpgradeFrameworkRequest):
    """
    Upgrade to a newer framework version; returns diff report and re-verifies code.
    """
    try:
        report = orchestrator.upgrade_framework(deck_id, req.target_stack)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/decks/{deck_id}/report")
def get_report(deck_id: str, format: Optional[str] = "json"):
    """
    Verification report (JSON and interactive HTML view).
    """
    report = store.get_report(deck_id)
    deck = store.get_deck(deck_id)
    if not report or not deck:
        raise HTTPException(status_code=404, detail=f"Report for deck '{deck_id}' not found")

    if format == "html":
        html_file = settings.DATA_DIR / "exports" / f"{deck_id}_verification_report.html"
        if not html_file.exists():
            orchestrator.exporter.export_html_report(report, deck)
        return FileResponse(html_file, media_type="text/html", filename=f"{deck_id}_report.html")

    return report

@app.get("/decks/{deck_id}/export")
def export_deck(deck_id: str, format: str = Query("pptx")):
    """
    Download the generated presentation in PPTX format.
    """
    deck = store.get_deck(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail=f"Deck '{deck_id}' not found")

    pptx_file = settings.DATA_DIR / "exports" / f"{deck_id}.pptx"
    if not pptx_file.exists():
        orchestrator.exporter.export_pptx(deck)

    return FileResponse(
        pptx_file,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"{deck_id}.pptx"
    )

@app.get("/decks")
def list_decks():
    """
    List all generated and cached decks.
    """
    return store.list_decks()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host=settings.HOST, port=settings.PORT, reload=True)
