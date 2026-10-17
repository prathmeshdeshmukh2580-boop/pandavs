"""
Regression tests for topic-aware course material generation.
Ensures 'Python Variables' generates relevant variable assignment, data types,
type conversion, and mutability content, and rejects generic FastAPI architecture slides.
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from apps.api.generator import CourseGenerator, _build_qwen_prompt
from apps.api.schema_util import deck_errors
from services.renderer.exporter import Exporter


class TestPythonVariablesTopicRelevance:
    @pytest.fixture(autouse=True)
    def setup_generator(self):
        self.gen = CourseGenerator()
        self.plan = {
            "topic": "Python Variables",
            "level": "beginner",
            "minutes": 10,
            "stack": {"python": "3.12"},
        }
        # Generate deterministically without requiring live Ollama
        self.deck = self.gen._generate_deterministic(self.plan, "python", "3.12")

    def test_python_variables_deck_schema_valid(self):
        """The generated deck must satisfy deck.schema.json."""
        errors = deck_errors(self.deck)
        assert errors == [], f"Schema validation errors: {errors}"

    def test_slide_titles_relevant_to_python_variables(self):
        """Slide titles must cover variables, types, and mutability, not web routing."""
        titles = [s["title"].lower() for s in self.deck["slides"]]
        all_titles_text = " ".join(titles)

        # Must mention core variable concepts
        assert "variable" in all_titles_text or "variables" in all_titles_text
        assert any("type" in t or "naming" in t or "mutability" in t for t in titles)

        # Must NOT contain generic web architecture / FastAPI titles
        for t in titles:
            assert "controller" not in t, f"Unexpected controller in title: {t}"
            assert "routing" not in t, f"Unexpected routing in title: {t}"
            assert "fastapi" not in t, f"Unexpected fastapi in title: {t}"
            assert "concurrency" not in t, f"Unexpected concurrency in title: {t}"
            assert "pipeline" not in t, f"Unexpected pipeline in title: {t}"

    def test_bullets_reject_fastapi_and_cover_variables(self):
        """Bullets must discuss variables, naming rules, data types, casting, not HTTP."""
        all_bullets = []
        for s in self.deck["slides"]:
            all_bullets.extend(s.get("bullets", []))
        bullets_text = " ".join(all_bullets).lower()

        # Topic relevance checks
        assert "variable" in bullets_text or "assignment" in bullets_text
        assert "pep 8" in bullets_text or "naming" in bullets_text
        assert any(k in bullets_text for k in ("int", "float", "str", "bool", "type"))
        assert "immutable" in bullets_text or "mutable" in bullets_text

        # Rejection of unrelated web concepts
        assert "http 400" not in bullets_text
        assert "http 422" not in bullets_text
        assert "fastapi" not in bullets_text
        assert "middleware" not in bullets_text
        assert "dto" not in bullets_text

    def test_code_blocks_demonstrate_variables_not_web_frameworks(self):
        """Code blocks must show variable assignments, types, and mutability, not FastAPI."""
        code_sources = []
        for s in self.deck["slides"]:
            for cb in s.get("code", []):
                code_sources.append(cb["source"])

        assert len(code_sources) >= 1, "Expected at least 1 code snippet in deck"
        combined_code = "\n".join(code_sources)

        # Must NOT import or use FastAPI or Pydantic
        assert "from fastapi" not in combined_code
        assert "import FastAPI" not in combined_code
        assert "from pydantic" not in combined_code
        assert "BaseModel" not in combined_code

        # Must demonstrate variable assignments and types
        assert "=" in combined_code
        assert any(t in combined_code for t in ("str", "int", "float", "bool", "append", "capitalize"))

    def test_exercise_covers_variable_normalization(self):
        """Exercise must test variable manipulation / type casting."""
        assert len(self.deck["exercises"]) >= 1
        ex = self.deck["exercises"][0]
        prompt = ex["prompt"].lower()
        tests = ex["tests"].lower()

        assert "normalize" in prompt or "cast" in prompt or "variable" in prompt or "dict" in prompt
        assert "int" in tests or "float" in tests or "isinstance" in tests
        assert "fastapi" not in prompt

    def test_quiz_covers_variable_topics(self):
        """Quiz questions must test naming rules, mutability, and type casting."""
        assert len(self.deck["quiz"]) >= 1
        questions = " ".join(q["question"].lower() for q in self.deck["quiz"])

        assert any(k in questions for k in ("variable", "name", "pep 8", "immutable", "type", "int"))
        assert "fastapi" not in questions
        assert "http" not in questions

    def test_cheat_sheet_covers_variable_rules(self):
        """Cheat sheet must provide variable syntax, types, and naming conventions."""
        sheet = self.deck["cheat_sheet"].lower()
        assert "variable" in sheet
        assert "naming" in sheet or "pep 8" in sheet
        assert "int" in sheet and "str" in sheet
        assert "immutable" in sheet or "mutable" in sheet
        assert "http 400" not in sheet

    def test_no_fabricated_sandbox_verification_claims(self):
        """Code and notes must not claim sandbox verification before actual sandbox run."""
        for s in self.deck["slides"]:
            for cb in s.get("code", []):
                assert cb["verified"] == "unverified", f"Code block {cb['id']} claimed verification before run"
                assert cb["attempts"] == 0
            notes = s.get("notes", "").lower()
            assert "compiled and verified in sandbox" not in notes

        for ex in self.deck["exercises"]:
            assert ex["proof"]["reference_passes"] is None
            assert ex["proof"]["naive_fails"] is None

    def test_pptx_export_succeeds_with_variable_deck(self, tmp_path):
        """The topic-specific Python Variables deck must export to a valid PPTX file."""
        exporter = Exporter(export_dir=str(tmp_path))
        pptx_path_str = exporter.export_pptx(self.deck)
        pptx_path = Path(pptx_path_str)
        assert pptx_path.exists()
        assert pptx_path.stat().st_size > 0


class TestQwenPromptTopicAwareness:
    def test_qwen_prompt_instructs_variables_focus(self):
        """Prompt builder must include strict topic guidance for Python Variables."""
        prompt = _build_qwen_prompt(
            topic="Python Variables",
            level="beginner",
            minutes=10,
            stack={"python": "3.12"},
            lang="python",
            version="3.12"
        )
        assert "Python Variables" in prompt
        assert "Do NOT generate web server, REST API, FastAPI" in prompt
        assert "variable assignment" in prompt
