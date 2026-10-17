"""
Tests for Qwen/Ollama integration in the CourseGenerator.
Covers: success, unavailable, invalid JSON, timeout, deterministic fallback,
and PPTX export compatibility.
"""
import json
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import httpx

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from apps.api.generator import (
    CourseGenerator, _parse_json_response, _patch_deck,
    _infer_lang_and_version, check_ollama_health,
)
from apps.api.schema_util import deck_errors


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_valid_deck_json(topic="Test Topic", source="qwen-ollama"):
    """Return a minimal but schema-valid deck dict."""
    return {
        "deck_id": "d_test0001",
        "topic": topic,
        "level": "beginner",
        "minutes": 30,
        "stack": {"python": "3.12"},
        "slides": [
            {
                "id": "s_001", "type": "title", "title": topic,
                "bullets": ["Intro bullet"],
                "code": [], "diagram": None, "notes": "Welcome."
            },
            {
                "id": "s_002", "type": "code", "title": "Code Example",
                "bullets": ["A code slide"],
                "code": [{
                    "id": "c_001", "lang": "python", "version": "3.12",
                    "kind": "plain", "source": "print('hello')",
                    "expected_output": None, "verified": "unverified", "attempts": 0
                }],
                "diagram": None, "notes": "Code walkthrough."
            },
        ],
        "exercises": [{
            "id": "e_001", "title": "Exercise 1",
            "lang": "python", "version": "3.12",
            "prompt": "Write a function.", "starter": "",
            "tests": "assert True", "reference": "def f(): pass",
            "naive": "def f(): return 1",
            "proof": {"reference_passes": None, "naive_fails": None},
        }],
        "quiz": [{
            "id": "q_001", "question": "What is Python?",
            "options": ["A language", "A snake", "A framework"],
            "answer_index": 0, "explanation": "Python is a programming language."
        }],
        "cheat_sheet": "# Quick ref",
        "meta": {"source": source, "model": "qwen3:8b"}
    }


def _mock_ollama_success_response(deck_dict=None):
    """Return a mock httpx.Response mimicking a successful Ollama /api/chat reply."""
    deck = deck_dict or _make_valid_deck_json()
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "message": {"content": json.dumps(deck)}
    }
    return mock_resp


# ===================================================================
# Test: Qwen/Ollama success path
# ===================================================================

class TestQwenSuccess:
    def test_qwen_generates_valid_deck(self):
        """When Ollama returns valid JSON, the generator produces a schema-valid deck."""
        valid_deck = _make_valid_deck_json(topic="Python Variables")
        mock_resp = _mock_ollama_success_response(valid_deck)

        with patch("apps.api.generator.httpx.post", return_value=mock_resp):
            gen = CourseGenerator()
            deck = gen.generate_deck({
                "topic": "Python Variables",
                "level": "beginner",
                "minutes": 10,
                "stack": {"python": "3.12"},
            })

        assert deck is not None
        assert deck["meta"]["source"] == "qwen-ollama"
        assert deck["meta"]["model"] == "qwen3:8b"
        errors = deck_errors(deck)
        assert errors == [], f"Schema errors: {errors}"

    def test_qwen_response_with_think_tags(self):
        """Qwen sometimes wraps output in <think> tags; parser must handle this."""
        valid_deck = _make_valid_deck_json()
        raw_text = '<think>Let me think about this...</think>\n' + json.dumps(valid_deck)
        parsed = _parse_json_response(raw_text)
        assert parsed is not None
        assert parsed["deck_id"] == "d_test0001"

    def test_qwen_response_with_markdown_fences(self):
        """Parser handles JSON wrapped in markdown code fences."""
        valid_deck = _make_valid_deck_json()
        raw_text = '```json\n' + json.dumps(valid_deck) + '\n```'
        parsed = _parse_json_response(raw_text)
        assert parsed is not None
        assert parsed["deck_id"] == "d_test0001"


# ===================================================================
# Test: Qwen/Ollama unavailable -> fallback
# ===================================================================

class TestQwenUnavailable:
    def test_connection_refused_falls_back(self):
        """When Ollama is unreachable, generator uses deterministic fallback."""
        with patch("apps.api.generator.httpx.post", side_effect=httpx.ConnectError("Connection refused")):
            gen = CourseGenerator()
            deck = gen.generate_deck({
                "topic": "Python Variables",
                "level": "beginner",
                "minutes": 10,
                "stack": {"python": "3.12"},
            })

        assert deck is not None
        assert deck["meta"]["source"] == "deterministic-fallback"
        errors = deck_errors(deck)
        assert errors == [], f"Schema errors: {errors}"

    def test_ollama_500_falls_back(self):
        """When Ollama returns HTTP 500, generator uses deterministic fallback."""
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"

        with patch("apps.api.generator.httpx.post", return_value=mock_resp):
            gen = CourseGenerator()
            deck = gen.generate_deck({
                "topic": "Python Variables",
                "level": "beginner",
                "minutes": 10,
                "stack": {"python": "3.12"},
            })

        assert deck["meta"]["source"] == "deterministic-fallback"


# ===================================================================
# Test: Qwen returns invalid JSON -> fallback
# ===================================================================

class TestQwenInvalidJSON:
    def test_garbage_response_falls_back(self):
        """When Ollama returns unparseable text, generator falls back."""
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "message": {"content": "This is not JSON at all, just rambling text..."}
        }

        with patch("apps.api.generator.httpx.post", return_value=mock_resp):
            gen = CourseGenerator()
            deck = gen.generate_deck({
                "topic": "Python Variables",
                "level": "beginner",
                "minutes": 10,
                "stack": {"python": "3.12"},
            })

        assert deck["meta"]["source"] == "deterministic-fallback"

    def test_partial_json_falls_back(self):
        """When Ollama returns truncated/partial JSON, generator falls back."""
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "message": {"content": '{"deck_id": "d_abc", "topic": "Incomplete'}
        }

        with patch("apps.api.generator.httpx.post", return_value=mock_resp):
            gen = CourseGenerator()
            deck = gen.generate_deck({
                "topic": "Python Variables",
                "level": "beginner",
                "minutes": 10,
                "stack": {"python": "3.12"},
            })

        assert deck["meta"]["source"] == "deterministic-fallback"


# ===================================================================
# Test: Qwen timeout -> fallback
# ===================================================================

class TestQwenTimeout:
    def test_timeout_falls_back(self):
        """When Ollama times out, generator uses deterministic fallback."""
        with patch("apps.api.generator.httpx.post", side_effect=httpx.ReadTimeout("Timed out")):
            gen = CourseGenerator()
            deck = gen.generate_deck({
                "topic": "Python Variables",
                "level": "beginner",
                "minutes": 10,
                "stack": {"python": "3.12"},
            })

        assert deck is not None
        assert deck["meta"]["source"] == "deterministic-fallback"
        errors = deck_errors(deck)
        assert errors == [], f"Schema errors: {errors}"


# ===================================================================
# Test: Deterministic fallback produces valid schema
# ===================================================================

class TestDeterministicFallback:
    def test_deterministic_python_valid(self):
        gen = CourseGenerator()
        deck = gen._generate_deterministic(
            {"topic": "Python Variables", "level": "beginner", "minutes": 10,
             "stack": {"python": "3.12"}},
            "python", "3.12"
        )
        assert deck["meta"]["source"] == "deterministic-fallback"
        errors = deck_errors(deck)
        assert errors == [], f"Schema errors: {errors}"

    def test_deterministic_java_valid(self):
        gen = CourseGenerator()
        deck = gen._generate_deterministic(
            {"topic": "Spring Boot", "level": "intermediate", "minutes": 90,
             "stack": {"java": "21", "spring_boot": "3.3"}},
            "java", "21"
        )
        assert deck["meta"]["source"] == "deterministic-fallback"
        errors = deck_errors(deck)
        assert errors == [], f"Schema errors: {errors}"


# ===================================================================
# Test: PPTX export still works (via API endpoint, lightweight mode)
# ===================================================================

class TestPPTXExport:
    def test_deterministic_deck_has_required_pptx_fields(self):
        """Ensure the deck structure is compatible with PPTX export."""
        gen = CourseGenerator()
        deck = gen._generate_deterministic(
            {"topic": "Python Variables", "level": "beginner", "minutes": 10,
             "stack": {"python": "3.12"}},
            "python", "3.12"
        )
        # PPTX builder needs: slides with title/bullets/code/diagram/notes
        for slide in deck["slides"]:
            assert "title" in slide
            assert "bullets" in slide
            assert "code" in slide
            assert "notes" in slide

    def test_qwen_deck_has_required_pptx_fields(self):
        """When Qwen succeeds, deck structure is compatible with PPTX export."""
        valid_deck = _make_valid_deck_json(topic="Python Variables")
        mock_resp = _mock_ollama_success_response(valid_deck)

        with patch("apps.api.generator.httpx.post", return_value=mock_resp):
            gen = CourseGenerator()
            deck = gen.generate_deck({
                "topic": "Python Variables",
                "level": "beginner",
                "minutes": 10,
                "stack": {"python": "3.12"},
            })

        for slide in deck["slides"]:
            assert "title" in slide
            assert "bullets" in slide
            assert "code" in slide
            assert "notes" in slide


# ===================================================================
# Test: Gemini is fully disabled
# ===================================================================

class TestGeminiDisabled:
    def test_no_gemini_import_in_generator(self):
        """The generator module should not import google.generativeai."""
        import apps.api.generator as gen_module
        source = Path(gen_module.__file__).read_text(encoding="utf-8")
        assert "google.generativeai" not in source
        assert "GEMINI_API_KEY" not in source

    def test_no_gemini_call_during_generation(self):
        """During deck generation, no Gemini-related HTTP calls are made."""
        valid_deck = _make_valid_deck_json()
        mock_resp = _mock_ollama_success_response(valid_deck)

        with patch("apps.api.generator.httpx.post", return_value=mock_resp) as mock_post:
            gen = CourseGenerator()
            gen.generate_deck({
                "topic": "Python Variables",
                "level": "beginner",
                "minutes": 10,
                "stack": {"python": "3.12"},
            })

        # The only HTTP call should be to Ollama, not Gemini/Anthropic
        for call in mock_post.call_args_list:
            url = call[0][0] if call[0] else call[1].get("url", "")
            assert "generativelanguage.googleapis.com" not in str(url)
            assert "anthropic.com" not in str(url)


# ===================================================================
# Test: Ollama health check
# ===================================================================

class TestOllamaHealthCheck:
    def test_health_check_returns_true_when_available(self):
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "models": [{"name": "qwen3:8b"}]
        }
        with patch("apps.api.generator.httpx.get", return_value=mock_resp):
            assert check_ollama_health() is True

    def test_health_check_returns_false_when_down(self):
        with patch("apps.api.generator.httpx.get", side_effect=httpx.ConnectError("refused")):
            assert check_ollama_health() is False

    def test_health_check_returns_false_on_500(self):
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 500
        with patch("apps.api.generator.httpx.get", return_value=mock_resp):
            assert check_ollama_health() is False
