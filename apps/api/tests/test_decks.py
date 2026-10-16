"""
Tests for POST /decks endpoint and generator schema compliance.
Uses mocked responses first — no API keys needed.
"""
import json
import sys
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from apps.api.main import app
from apps.api.generator import CourseGenerator, _patch_deck, _infer_lang_and_version
from apps.api.schema_util import deck_errors

client = TestClient(app)


# ===================================================================
# Health endpoint
# ===================================================================

class TestHealth:
    def test_health_returns_ok(self):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ("ok", "healthy")

    def test_health_has_version(self):
        r = client.get("/health")
        data = r.json()
        assert "version" in data

    def test_health_has_gemini_flag(self):
        r = client.get("/health")
        data = r.json()
        assert "gemini_available" in data


# ===================================================================
# Generator deterministic output — must pass schema validation
# ===================================================================

class TestGeneratorDeterministic:
    """Test the deterministic (no-API) generator produces schema-valid decks."""

    def _generate(self, topic="Python basics", lang_stack=None):
        gen = CourseGenerator()
        stack = lang_stack or {"python": "3.12"}
        plan = {"topic": topic, "level": "beginner", "minutes": 30, "stack": stack}
        return gen.generate_deck(plan)

    def test_deterministic_python_deck_validates(self):
        deck = self._generate("Python FastAPI basics", {"python": "3.12"})
        errors = deck_errors(deck)
        assert errors == [], f"Schema errors: {errors}"

    def test_deterministic_java_deck_validates(self):
        deck = self._generate("Spring Boot REST APIs", {"java": "21", "spring_boot": "3.3"})
        errors = deck_errors(deck)
        assert errors == [], f"Schema errors: {errors}"

    def test_deck_has_required_fields(self):
        deck = self._generate()
        for field in ("deck_id", "topic", "level", "minutes", "stack",
                       "slides", "exercises", "quiz", "cheat_sheet"):
            assert field in deck, f"Missing required field: {field}"

    def test_slides_have_correct_structure(self):
        deck = self._generate()
        for slide in deck["slides"]:
            assert "id" in slide
            assert "type" in slide
            assert slide["type"] in ("title", "section", "content", "code",
                                      "diagram", "exercise", "summary")
            assert "title" in slide
            assert "bullets" in slide
            assert isinstance(slide["bullets"], list)
            assert "code" in slide
            assert isinstance(slide["code"], list)
            assert "diagram" in slide  # can be None or dict
            assert "notes" in slide

    def test_code_blocks_have_correct_structure(self):
        deck = self._generate()
        for slide in deck["slides"]:
            for cb in slide["code"]:
                assert "id" in cb
                assert cb["lang"] in ("java", "python")
                assert cb["kind"] in ("plain", "spring-fragment")
                assert "source" in cb and len(cb["source"]) > 0
                assert cb["verified"] in ("passed", "failed", "unverified")
                assert "attempts" in cb
                assert "expected_output" in cb
                # Must NOT have error_message (additionalProperties: false)
                assert "error_message" not in cb

    def test_exercises_have_correct_structure(self):
        deck = self._generate()
        for ex in deck["exercises"]:
            for field in ("id", "title", "lang", "version", "prompt",
                          "starter", "tests", "reference", "naive", "proof"):
                assert field in ex, f"Exercise missing field: {field}"
            proof = ex["proof"]
            assert "reference_passes" in proof
            assert "naive_fails" in proof

    def test_quiz_items_have_correct_structure(self):
        deck = self._generate()
        for qi in deck["quiz"]:
            for field in ("id", "question", "options", "answer_index", "explanation"):
                assert field in qi, f"Quiz item missing field: {field}"
            assert isinstance(qi["options"], list)
            assert len(qi["options"]) >= 2

    def test_diagram_structure(self):
        deck = self._generate()
        for slide in deck["slides"]:
            d = slide["diagram"]
            if d is not None:
                assert isinstance(d, dict)
                assert "id" in d
                assert d["kind"] == "mermaid"
                assert "source" in d and len(d["source"]) > 0


# ===================================================================
# _patch_deck helper
# ===================================================================

class TestPatchDeck:
    def test_fixes_invalid_slide_type(self):
        raw = {
            "slides": [{"id": "s_001", "type": "overview", "title": "X",
                         "bullets": [], "code": [], "diagram": None, "notes": ""}],
            "exercises": [], "quiz": [],
        }
        patched = _patch_deck(raw, "python", "3.12")
        assert patched["slides"][0]["type"] == "content"

    def test_fixes_string_diagram(self):
        raw = {
            "slides": [{"id": "s_001", "type": "diagram", "title": "X",
                         "bullets": [], "code": [],
                         "diagram": "flowchart LR\n  A --> B",
                         "notes": ""}],
            "exercises": [], "quiz": [],
        }
        patched = _patch_deck(raw, "python", "3.12")
        d = patched["slides"][0]["diagram"]
        assert isinstance(d, dict)
        assert d["kind"] == "mermaid"
        assert "flowchart" in d["source"]

    def test_fixes_quiz_answer_field(self):
        raw = {
            "slides": [], "exercises": [],
            "quiz": [{"question": "Q?", "options": ["A", "B"],
                       "answer": 1, "explanation": "Because."}],
        }
        patched = _patch_deck(raw, "python", "3.12")
        qi = patched["quiz"][0]
        assert "answer_index" in qi
        assert "answer" not in qi
        assert qi["answer_index"] == 1

    def test_removes_extra_code_block_keys(self):
        raw = {
            "slides": [{"id": "s_001", "type": "code", "title": "X",
                         "bullets": [], "notes": "",
                         "code": [{"id": "c_001", "lang": "java", "version": "21",
                                    "kind": "plain", "source": "x",
                                    "expected_output": None, "verified": "unverified",
                                    "attempts": 0, "error_message": "bad"}],
                         "diagram": None}],
            "exercises": [], "quiz": [],
        }
        patched = _patch_deck(raw, "java", "21")
        assert "error_message" not in patched["slides"][0]["code"][0]

    def test_adds_missing_exercise_fields(self):
        raw = {
            "slides": [], "quiz": [],
            "exercises": [{"id": "e_001", "title": "Ex",
                            "description": "Do stuff",
                            "starter": "x", "tests": "t",
                            "reference": "r", "naive": "n",
                            "proof": {"reference_passes": True, "naive_fails": True}}],
        }
        patched = _patch_deck(raw, "python", "3.12")
        ex = patched["exercises"][0]
        assert ex["lang"] == "python"
        assert ex["version"] == "3.12"
        assert ex["prompt"] == "Do stuff"  # migrated from description
        assert "description" not in ex


# ===================================================================
# _infer_lang_and_version helper
# ===================================================================

class TestInferLang:
    def test_java_from_stack(self):
        assert _infer_lang_and_version({"java": "21"}, "anything")[0] == "java"

    def test_python_from_stack(self):
        assert _infer_lang_and_version({"python": "3.12"}, "anything")[0] == "python"

    def test_python_from_topic(self):
        assert _infer_lang_and_version({}, "Python basics")[0] == "python"

    def test_java_from_topic(self):
        assert _infer_lang_and_version({}, "Spring Boot REST")[0] == "java"

    def test_default_python(self):
        assert _infer_lang_and_version({}, "Machine Learning")[0] == "python"


# ===================================================================
# POST /decks endpoint (integration test, uses deterministic fallback)
# ===================================================================

class TestCreateDeck:
    def test_create_deck_returns_deck_id(self):
        r = client.post("/decks", json={
            "topic": "Python basics",
            "level": "beginner",
            "minutes": 30,
        })
        assert r.status_code == 202
        data = r.json()
        assert "deck_id" in data
        assert data["deck_id"].startswith("d_")

    def test_created_deck_is_retrievable(self):
        r = client.post("/decks", json={
            "topic": "Python testing",
            "level": "intermediate",
            "minutes": 45,
        })
        deck_id = r.json()["deck_id"]

        r2 = client.get(f"/decks/{deck_id}")
        assert r2.status_code == 200
        deck = r2.json()
        assert deck["deck_id"] == deck_id
        assert deck["topic"] == "Python testing"

    def test_created_deck_passes_schema(self):
        r = client.post("/decks", json={
            "topic": "FastAPI development",
            "level": "beginner",
            "minutes": 30,
            "stack": {"python": "3.12"},
        })
        deck_id = r.json()["deck_id"]
        deck = client.get(f"/decks/{deck_id}").json()
        errors = deck_errors(deck)
        assert errors == [], f"Schema errors: {errors}"

    def test_create_deck_java_topic(self):
        r = client.post("/decks", json={
            "topic": "Spring Boot 3 REST APIs",
            "level": "beginner",
            "minutes": 90,
            "stack": {"java": "21", "spring_boot": "3.3"},
        })
        assert r.status_code == 202
        deck_id = r.json()["deck_id"]
        deck = client.get(f"/decks/{deck_id}").json()
        errors = deck_errors(deck)
        assert errors == [], f"Schema errors: {errors}"

    def test_create_deck_requires_topic(self):
        r = client.post("/decks", json={})
        assert r.status_code == 422

    def test_get_nonexistent_deck(self):
        r = client.get("/decks/d_nonexistent")
        assert r.status_code == 404


# ===================================================================
# Schema validation tests (existing, updated)
# ===================================================================

class TestSchemaValidation:
    def test_sample_deck_validates(self):
        """The hand-written sample_deck.json must pass schema validation."""
        from apps.api.config import settings
        sample = settings.SAMPLES_DIR / "sample_deck.json"
        if sample.exists():
            deck = json.loads(sample.read_text(encoding="utf-8"))
            errors = deck_errors(deck)
            assert errors == [], f"sample_deck.json errors: {errors}"

    def test_spring_boot_deck_validates(self):
        """The spring_boot_deck.json sample must pass schema validation."""
        from apps.api.config import settings
        sample = settings.SAMPLES_DIR / "spring_boot_deck.json"
        if sample.exists():
            deck = json.loads(sample.read_text(encoding="utf-8"))
            errors = deck_errors(deck)
            assert errors == [], f"spring_boot_deck.json errors: {errors}"
