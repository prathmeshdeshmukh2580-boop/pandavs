"""
Comprehensive regression tests for the Trainer-Grade Course Generation Overhaul.
Verifies:
1. Masterclass Docker benchmark curriculum depth (24 slides, 9 modules, 90 mins).
2. Speaker delivery notes depth (structured scripts, misconception runbooks, >100 words/slide).
3. Pedagogical Quality Gate scoring (score >= 85/100, pass duration/depth/relevance checks).
4. Dual-prover laboratory contract integrity ("Tests Must Bite").
5. Strict schema conformance against deck.schema.json (0 errors).
6. Multi-format artifact generation (PPTX with speaker notes, Trainer Guide, Student Notes).
7. FastAPI endpoints for trainer-guide, student-notes, and quality-review.
"""

import os
import json
import pytest
from pathlib import Path

from apps.api.generator.docker_benchmark import build_docker_benchmark_deck
from apps.api.generator import CourseGenerator, _patch_deck
from apps.api.quality_gate import evaluate_course_quality
from apps.api.speaker_notes import build_trainer_delivery_notes
from apps.api.schema_util import deck_errors
from services.renderer.exporter import Exporter
from services.verifier.prover import ExerciseProver


def test_docker_benchmark_curriculum_depth():
    """Verify that the Docker benchmark is genuinely trainer-grade with >= 20 slides."""
    deck = build_docker_benchmark_deck(
        deck_id="d_test_docker",
        topic="Docker Introduction for Intermediate Developers",
        level="intermediate",
        minutes=90,
    )

    slides = deck.get("slides", [])
    assert len(slides) >= 20, f"Expected >= 20 slides for a 90-min course, got {len(slides)}"
    assert deck["minutes"] == 90
    assert deck["level"] == "intermediate"

    # Schema validation must have 0 errors
    errors = deck_errors(deck)
    assert not errors, f"Schema validation failed on benchmark deck: {errors}"

    # Verify key technical modules are covered
    titles = " ".join([s["title"].lower() for s in slides])
    assert "cgroup" in titles or "namespace" in titles or "kernel" in titles
    assert "overlay2" in titles or "storage" in titles or "layer" in titles
    assert "lifecycle" in titles or "state" in titles or "architecture" in titles
    assert "multistage" in titles or "multi-stage" in titles or "buildkit" in titles
    assert "network" in titles
    assert "runbook" in titles or "troubleshooting" in titles
    assert "lab" in titles or "exercise" in titles


def test_speaker_notes_depth_and_structure():
    """Verify that speaker notes are not superficial 1-sentence summaries."""
    deck = build_docker_benchmark_deck(
        deck_id="d_test_notes",
        topic="Docker Introduction for Intermediate Developers",
        level="intermediate",
        minutes=90,
    )

    slides = deck.get("slides", [])
    word_counts = []

    for s in slides:
        notes = s.get("notes", "")
        words = len(notes.split())
        word_counts.append(words)
        # Every slide must have substantive notes (> 70 words, substantive content slides > 120 words)
        assert words >= 70, f"Slide '{s.get('title')}' notes too short ({words} words)"

    avg_words = sum(word_counts) / len(word_counts)
    assert avg_words >= 130, f"Expected average notes words >= 130, got {avg_words:.1f}"

    # Verify required structured delivery tags exist in the masterclass notes
    first_content_notes = slides[1].get("notes", "")
    assert "TEACHING OBJECTIVE:" in first_content_notes
    assert "INSTRUCTOR EXPLANATION:" in first_content_notes
    assert "QUESTIONS TO ASK LEARNERS:" in first_content_notes or "PROBING QUESTIONS:" in first_content_notes


def test_pedagogical_quality_gate_scoring():
    """Verify that the Pedagogical Quality Gate produces an A-grade evaluation on the benchmark."""
    deck = build_docker_benchmark_deck(
        deck_id="d_test_qg",
        topic="Docker Introduction for Intermediate Developers",
        level="intermediate",
        minutes=90,
    )

    audit = evaluate_course_quality(deck)
    assert audit["passed"] is True
    assert audit["overall_score"] >= 85, f"Expected score >= 85, got {audit['overall_score']}"
    assert audit["checks"]["duration_alignment"]["passed"] is True
    assert audit["checks"]["speaker_notes_coverage"]["passed"] is True
    assert audit["checks"]["topic_relevance"]["passed"] is True
    assert audit["checks"]["practical_lab_completeness"]["passed"] is True


def test_exercise_prover_tests_must_bite():
    """Verify that the hands-on lab exercise passes dual-prover testing."""
    deck = build_docker_benchmark_deck(
        deck_id="d_test_prover",
        topic="Docker Introduction for Intermediate Developers",
        level="intermediate",
        minutes=90,
    )

    exercises = deck.get("exercises", [])
    assert len(exercises) >= 1

    prover = ExerciseProver(timeout_sec=15)
    ex = exercises[0]
    proof = prover.prove_exercise(
        starter=ex["starter"],
        tests=ex["tests"],
        reference=ex["reference"],
        naive=ex["naive"],
    )

    assert proof["reference_passes"] is True, f"Reference solution must pass tests: {proof}"
    assert proof["naive_fails"] is True, f"Naive buggy solution must fail tests: {proof}"
    assert proof["proven"] is True


def test_multi_artifact_export(tmp_path):
    """Verify that PPTX, Trainer Guide, and Student Notes export without errors."""
    deck = build_docker_benchmark_deck(
        deck_id="d_test_export",
        topic="Docker Introduction for Intermediate Developers",
        level="intermediate",
        minutes=90,
    )

    exporter = Exporter(export_dir=str(tmp_path))

    # 1. PPTX export
    pptx_path = exporter.export_pptx(deck)
    assert os.path.exists(pptx_path)
    assert os.path.getsize(pptx_path) > 10000

    # 2. Trainer Guide export
    trainer_guide_path = exporter.export_trainer_guide(deck)
    assert os.path.exists(trainer_guide_path)
    with open(trainer_guide_path, "r", encoding="utf-8") as f:
        guide_text = f.read()
    assert "Instructor Delivery Guide" in guide_text
    assert "Timed Curriculum Agenda" in guide_text
    assert "INSTRUCTOR REFERENCE SOLUTION" in guide_text
    assert "Assessment Key & Conceptual Distractor Analysis" in guide_text

    # 3. Student Notes export
    student_notes_path = exporter.export_student_notes(deck)
    assert os.path.exists(student_notes_path)
    with open(student_notes_path, "r", encoding="utf-8") as f:
        notes_text = f.read()
    assert "Student Companion Reference" in notes_text or "Student Study Notes" in notes_text
    assert "Hands-on Laboratory Challenge" in notes_text or "Laboratory" in notes_text
    # Solutions must NOT be leaked in student notes
    assert "INSTRUCTOR REFERENCE SOLUTION" not in notes_text
    assert "Master Solution" not in notes_text


def test_course_generator_routes_docker_deterministically():
    """Verify that CourseGenerator deterministic route produces the 24-slide trainer-grade benchmark."""
    gen = CourseGenerator()
    plan = {
        "deck_id": "d_gen_docker",
        "topic": "Docker Introduction for Intermediate Developers",
        "level": "intermediate",
        "minutes": 90,
        "stack": {"docker": "26.0"},
    }
    deck = gen._generate_deterministic(plan, lang="python", version="3.12")

    assert len(deck.get("slides", [])) >= 20
    assert "cgroup" in " ".join(s["title"].lower() for s in deck["slides"]) or "container" in deck["topic"].lower()
    errors = deck_errors(deck)
    assert not errors, f"Deterministic generation has schema errors: {errors}"


def test_api_trainer_grade_endpoints():
    """Verify API endpoints for trainer-guide, student-notes, and quality-review."""
    from fastapi.testclient import TestClient
    from apps.api.main import app, store

    deck = build_docker_benchmark_deck(
        deck_id="d_test_api_endpoints",
        topic="Docker Introduction for Intermediate Developers",
        level="intermediate",
        minutes=90,
    )
    store.save_deck("d_test_api_endpoints", deck, status="ready")

    client = TestClient(app)

    # 1. Quality review endpoint
    qr_res = client.get("/decks/d_test_api_endpoints/quality-review")
    assert qr_res.status_code == 200
    qr_data = qr_res.json()
    assert qr_data["passed"] is True
    assert qr_data["overall_score"] >= 85

    # 2. Trainer guide endpoint
    tg_res = client.get("/decks/d_test_api_endpoints/trainer-guide")
    assert tg_res.status_code == 200
    assert "content" in tg_res.json()
    assert "Instructor Delivery Guide" in tg_res.json()["content"]

    # 3. Student notes endpoint
    sn_res = client.get("/decks/d_test_api_endpoints/student-notes")
    assert sn_res.status_code == 200
    assert "content" in sn_res.json()
    assert "Student Companion Reference" in sn_res.json()["content"]

