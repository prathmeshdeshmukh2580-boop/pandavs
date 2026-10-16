"""
Generator: outline -> full deck JSON.
Uses Google Gemini API (primary) or Anthropic Claude (legacy) for content generation.
Falls back to deterministic generation when no LLM is available.
"""
import os
import re
import json
import logging
import time
import uuid
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

try:
    from apps.api.config import settings
except ImportError:
    import config as _cfg

    class _Settings:
        ANTHROPIC_API_KEY = getattr(_cfg, "ANTHROPIC_API_KEY", "")
        CLAUDE_MODEL = getattr(_cfg, "CLAUDE_MODEL", "")
        GEMINI_API_KEY = getattr(_cfg, "GEMINI_API_KEY", "")
        GEMINI_MODEL = getattr(_cfg, "GEMINI_MODEL", "gemini-2.0-flash")

    settings = _Settings()

# ---------------------------------------------------------------------------
# Gemini SDK (lazy, optional)
# ---------------------------------------------------------------------------
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def _gemini_model():
    """Return a configured Gemini GenerativeModel, or None."""
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key or not GEMINI_AVAILABLE:
        return None
    genai.configure(api_key=api_key)
    model_name = getattr(settings, "GEMINI_MODEL", "gemini-2.0-flash")
    return genai.GenerativeModel(model_name)


# ---------------------------------------------------------------------------
# Prompt builder — topic-aware, not hardcoded to Java/Spring Boot
# ---------------------------------------------------------------------------

def _infer_lang_and_version(stack: Dict[str, str], topic: str) -> tuple:
    """Decide language and version from stack dict and topic string."""
    topic_lower = topic.lower()
    if any(k in stack for k in ("java", "spring_boot")):
        return "java", stack.get("java", "21")
    if any(k in stack for k in ("python",)):
        return "python", stack.get("python", "3.12")
    # heuristic from topic text
    if "python" in topic_lower or "fastapi" in topic_lower or "django" in topic_lower or "flask" in topic_lower:
        return "python", "3.12"
    if "java" in topic_lower or "spring" in topic_lower:
        return "java", "21"
    # default to python for anything not explicitly Java
    return "python", "3.12"


def _build_gemini_prompt(topic: str, level: str, minutes: int,
                         stack: Dict[str, str], lang: str, version: str) -> str:
    """Build a Gemini prompt that produces schema-valid deck JSON."""
    deck_id = f"d_{uuid.uuid4().hex[:8]}"
    kind_hint = "plain" if lang == "python" else "plain or spring-fragment"

    return f"""You are a course-material generator for the Verified Course Material Studio.
Generate a complete lesson deck about "{topic}" for {level} students ({minutes} min).

Return **only** a JSON object (no markdown fences, no commentary).

The JSON **must** have this exact top-level shape:
{{
  "deck_id": "{deck_id}",
  "topic": "{topic}",
  "level": "{level}",
  "minutes": {minutes},
  "stack": {json.dumps(stack)},
  "slides": [ ... ],
  "exercises": [ ... ],
  "quiz": [ ... ],
  "cheat_sheet": "...",
  "meta": {{ "source": "gemini-generated", "model": "{getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')}" }}
}}

### Slide rules
Each slide object must have **exactly** these keys (no extra keys):
  id (string, pattern s_NNN), type, title, bullets, code, diagram, notes

- type must be one of: "title", "section", "content", "code", "diagram", "exercise", "summary"
- bullets: array of strings (max 5 items, each ≤120 chars)
- title: string, max 90 chars
- code: an array (may be empty). Each element:
    {{ "id": "c_NNN", "lang": "{lang}", "version": "{version}",
       "kind": "{kind_hint}", "source": "...", "expected_output": null,
       "verified": "unverified", "attempts": 0 }}
- diagram: either null or {{ "id": "g_NNN", "kind": "mermaid", "source": "..." }}
- notes: string (speaker notes)

### Exercise rules
Each exercise must have **exactly** these keys:
  id (pattern e_NNN), title, lang, version, prompt, starter, tests, reference, naive, proof
- lang must be "{lang}", version must be "{version}"
- proof: {{ "reference_passes": null, "naive_fails": null }}

### Quiz rules
Each quiz item must have **exactly** these keys:
  id (pattern q_NNN), question, options (2-6 strings), answer_index (int 0-5), explanation

### Content guidelines
- Generate 5-7 slides with varied types.
- All code must be {lang.upper()} {version}. Write real, correct, runnable code.
- If lang is python use kind "plain". If lang is java, "plain" for standalone programs or "spring-fragment" for Spring Boot fragments.
- Include at least 1 exercise and at least 3 quiz questions.
- Make content appropriate for {level} level and {minutes} minutes.

Respond with ONLY the JSON object."""


# ---------------------------------------------------------------------------
# JSON parsing helpers
# ---------------------------------------------------------------------------

def _parse_json_response(text: str) -> Optional[dict]:
    """Parse JSON from LLM output, handling code fences and stray text."""
    # 1. Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown fences
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", text, flags=re.MULTILINE)
    cleaned = re.sub(r"\n?```\s*$", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3. Find outermost { … }
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except (ValueError, json.JSONDecodeError) as exc:
        logger.error("Failed to parse JSON from LLM response: %s", exc)
        logger.debug("Raw text (first 500 chars): %s", text[:500])
        return None


# ---------------------------------------------------------------------------
# Post-processing: patch common LLM output mistakes to satisfy the schema
# ---------------------------------------------------------------------------

_VALID_SLIDE_TYPES = {"title", "section", "content", "code", "diagram", "exercise", "summary"}
_VALID_CODE_KINDS = {"plain", "spring-fragment"}


def _patch_deck(deck: dict, lang: str, version: str) -> dict:
    """Fix common LLM output mistakes so the deck passes schema validation."""
    deck.setdefault("deck_id", f"d_{uuid.uuid4().hex[:8]}")
    deck.setdefault("stack", {})
    deck.setdefault("slides", [])
    deck.setdefault("exercises", [])
    deck.setdefault("quiz", [])
    deck.setdefault("cheat_sheet", "")
    deck.setdefault("meta", {})

    # -- slides --
    for i, slide in enumerate(deck.get("slides", [])):
        slide.setdefault("id", f"s_{i + 1:03d}")
        slide.setdefault("bullets", [])
        slide.setdefault("notes", "")

        # fix invalid type
        if slide.get("type") not in _VALID_SLIDE_TYPES:
            slide["type"] = "content"

        # ensure code is always a list (never None or missing)
        if "code" not in slide or slide["code"] is None:
            slide["code"] = []
        for j, cb in enumerate(slide["code"]):
            cb.setdefault("id", f"c_{i + 1:03d}_{j + 1}")
            cb.setdefault("lang", lang)
            cb.setdefault("version", version)
            if cb.get("kind") not in _VALID_CODE_KINDS:
                cb["kind"] = "plain"
            cb.setdefault("source", "")
            cb.setdefault("expected_output", None)
            cb.setdefault("verified", "unverified")
            cb.setdefault("attempts", 0)
            # remove non-schema keys
            for bad_key in ("error_message", "description", "explanation"):
                cb.pop(bad_key, None)

        # fix diagram
        diag = slide.get("diagram")
        if diag is None:
            slide["diagram"] = None
        elif isinstance(diag, str):
            # LLM sometimes returns mermaid source as a bare string
            slide["diagram"] = {
                "id": f"g_{i + 1:03d}",
                "kind": "mermaid",
                "source": diag,
            }
        elif isinstance(diag, dict):
            diag.setdefault("id", f"g_{i + 1:03d}")
            diag.setdefault("kind", "mermaid")
            diag.setdefault("source", "")
        else:
            slide["diagram"] = None

        # truncate bullets
        slide["bullets"] = slide["bullets"][:5]
        for bi, b in enumerate(slide["bullets"]):
            if len(b) > 120:
                slide["bullets"][bi] = b[:117] + "..."

        # title length
        if len(slide.get("title", "")) > 90:
            slide["title"] = slide["title"][:87] + "..."

        # remove non-schema keys from slide
        allowed_slide_keys = {"id", "type", "title", "bullets", "code", "diagram", "notes"}
        for key in list(slide.keys()):
            if key not in allowed_slide_keys:
                del slide[key]

    # -- exercises --
    for i, ex in enumerate(deck.get("exercises", [])):
        ex.setdefault("id", f"e_{i + 1:03d}")
        ex.setdefault("title", f"Exercise {i + 1}")
        ex.setdefault("lang", lang)
        ex.setdefault("version", version)
        ex.setdefault("prompt", ex.pop("description", "") or "Complete the exercise.")
        ex.setdefault("starter", "")
        ex.setdefault("tests", "# TODO: tests")
        ex.setdefault("reference", "# TODO: reference solution")
        ex.setdefault("naive", "# TODO: naive solution")

        proof = ex.get("proof")
        if not isinstance(proof, dict):
            ex["proof"] = {"reference_passes": None, "naive_fails": None}
        else:
            # schema requires bool | null, not just bool
            if "reference_passes" not in proof:
                proof["reference_passes"] = None
            if "naive_fails" not in proof:
                proof["naive_fails"] = None

        # remove non-schema keys
        allowed_exercise_keys = {"id", "title", "lang", "version", "prompt",
                                 "starter", "tests", "reference", "naive", "proof"}
        for key in list(ex.keys()):
            if key not in allowed_exercise_keys:
                del ex[key]

    # -- quiz --
    for i, qi in enumerate(deck.get("quiz", [])):
        qi.setdefault("id", f"q_{i + 1:03d}")
        qi.setdefault("question", "")
        qi.setdefault("options", [])
        qi.setdefault("explanation", "")
        # normalise answer field name
        if "answer" in qi and "answer_index" not in qi:
            qi["answer_index"] = qi.pop("answer")
        elif "correct_answer" in qi and "answer_index" not in qi:
            qi["answer_index"] = qi.pop("correct_answer")
        elif "correct_option_index" in qi and "answer_index" not in qi:
            qi["answer_index"] = qi.pop("correct_option_index")
        qi.setdefault("answer_index", 0)
        # remove non-schema keys
        allowed_quiz_keys = {"id", "question", "options", "answer_index", "explanation"}
        for key in list(qi.keys()):
            if key not in allowed_quiz_keys:
                del qi[key]

    return deck


# ===================================================================
# Public API — preserved for backward compatibility
# ===================================================================

class CourseGenerator:
    """
    Stage 2: Generates complete slide-level JSON, code snippets, notes,
    exercises, and quiz.  Output satisfies deck.schema.json.
    """

    def __init__(self, api_key: str = ""):
        self.anthropic_key = api_key or getattr(settings, "ANTHROPIC_API_KEY", "")

    # ---- main entry point (unchanged signature) ----
    def generate_deck(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Try Gemini first, then Anthropic, then deterministic fallback."""
        topic = plan.get("topic", "Software Development")
        level = plan.get("level", "beginner")
        minutes = plan.get("minutes", 90)
        stack = plan.get("stack", {"python": "3.12"})
        lang, version = _infer_lang_and_version(stack, topic)

        # 1. Try Gemini
        gemini_key = getattr(settings, "GEMINI_API_KEY", "")
        if gemini_key and GEMINI_AVAILABLE:
            try:
                deck = self._generate_with_gemini(topic, level, minutes, stack, lang, version)
                if deck:
                    deck["deck_id"] = plan.get("deck_id", deck.get("deck_id", f"d_{uuid.uuid4().hex[:8]}"))
                    return deck
            except Exception as exc:
                logger.warning("Gemini generation failed: %s", exc)

        # 2. Try Anthropic / Claude
        if self.anthropic_key:
            try:
                deck = self._generate_with_anthropic(plan, lang, version)
                if deck:
                    return deck
            except Exception as exc:
                logger.warning("Anthropic generation failed: %s", exc)

        # 3. Deterministic fallback
        return self._generate_deterministic(plan, lang, version)

    # ---- Gemini path (new) ----
    def _generate_with_gemini(self, topic, level, minutes, stack, lang, version):
        model = _gemini_model()
        if model is None:
            return None

        prompt = _build_gemini_prompt(topic, level, minutes, stack, lang, version)
        logger.info("Calling Gemini (%s) for topic=%r …", getattr(settings, "GEMINI_MODEL", ""), topic)

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=8192,
                response_mime_type="application/json",
            ),
            request_options={"timeout": 120},
        )
        raw = _parse_json_response(response.text)
        if raw is None:
            return None
        return _patch_deck(raw, lang, version)

    # ---- Anthropic path (preserved from teammate) ----
    def _generate_with_anthropic(self, plan, lang, version):
        import httpx

        prompt = f"""
Generate full slide-level JSON for this course plan:
{json.dumps(plan, indent=2)}

CRITICAL REQUIREMENTS:
- Must adhere strictly to deck.schema.json.
- Each slide has 'id', 'type' (title|section|content|code|diagram|exercise|summary),
  'title', 'bullets' (max 5, ≤120 chars each), 'code' (array), 'diagram' (null or object), 'notes'.
- Code blocks: 'id','lang','version','kind' (plain|spring-fragment),'source','expected_output','verified':'unverified','attempts':0.
- Exercises: 'id','title','lang','version','prompt','starter','tests','reference','naive','proof'.
- Quiz items: 'id','question','options','answer_index','explanation'.
- Output ONLY the valid JSON object.
"""
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.anthropic_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": getattr(settings, "CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60.0,
        )
        if resp.status_code == 200:
            content = resp.json()["content"][0]["text"]
            raw = _parse_json_response(content)
            if raw:
                return _patch_deck(raw, lang, version)
        return None

    # ---- Deterministic fallback (schema-valid, topic-aware) ----
    def _generate_deterministic(self, plan: Dict[str, Any],
                                lang: str, version: str) -> Dict[str, Any]:
        deck_id = plan.get("deck_id", f"d_{uuid.uuid4().hex[:8]}")
        topic = plan.get("topic", "Modern Software Architecture")
        level = plan.get("level", "beginner")
        minutes = plan.get("minutes", 90)
        stack = plan.get("stack", {"python": "3.12"})
        is_java = lang == "java"

        # --- code examples (language-aware) ---
        if is_java:
            code1_source = ('public class Main {\n'
                            '    public record Greeting(String name) {}\n\n'
                            '    public static void main(String[] args) {\n'
                            '        Greeting g = new Greeting("World");\n'
                            '        System.out.println("Hello, " + g.name());\n'
                            '    }\n}')
            code1_output = "Hello, World"
            code1_kind = "plain"
            code2_source = ('@RestController\n'
                            '@RequestMapping("/api/v1")\n'
                            'public class AppController {\n'
                            '    public record HealthStatus(String status, long time) {}\n\n'
                            '    @GetMapping("/health")\n'
                            '    public HealthStatus getHealth() {\n'
                            '        return new HealthStatus("HEALTHY", System.currentTimeMillis());\n'
                            '    }\n}')
            code2_kind = "spring-fragment"
            ex_lang = "java"
            ex_version = version
            ex_prompt = (f"Implement Greeter.greet(name) so it returns "
                         f"'Hello, <name>!' and 'Hello, stranger!' for null or blank names.")
            ex_starter = ('public class Greeter {\n'
                          '    public static String greet(String name) {\n'
                          '        // TODO\n        return null;\n    }\n}')
            ex_tests = ('import org.junit.jupiter.api.Test;\n'
                        'import static org.junit.jupiter.api.Assertions.assertEquals;\n\n'
                        'class GreeterTest {\n'
                        '    @Test void greetsByName() {\n'
                        '        assertEquals("Hello, Ada!", Greeter.greet("Ada"));\n    }\n'
                        '    @Test void handlesBlank() {\n'
                        '        assertEquals("Hello, stranger!", Greeter.greet("  "));\n'
                        '        assertEquals("Hello, stranger!", Greeter.greet(null));\n    }\n}')
            ex_reference = ('public class Greeter {\n'
                            '    public static String greet(String name) {\n'
                            '        if (name == null || name.isBlank()) return "Hello, stranger!";\n'
                            '        return "Hello, " + name + "!";\n    }\n}')
            ex_naive = ('public class Greeter {\n'
                        '    public static String greet(String name) {\n'
                        '        return "Hello, " + name + "!";\n    }\n}')
        else:
            code1_source = ('from fastapi import FastAPI\n'
                            'from pydantic import BaseModel\n\n'
                            'app = FastAPI()\n\n'
                            'class HealthCheck(BaseModel):\n'
                            '    status: str\n'
                            '    active: bool\n\n'
                            '@app.get("/health", response_model=HealthCheck)\n'
                            'async def check_health():\n'
                            '    return {"status": "HEALTHY", "active": True}')
            code1_output = None
            code1_kind = "plain"
            code2_source = ('from pydantic import BaseModel, Field\n\n'
                            'class OrderItem(BaseModel):\n'
                            '    item_id: str\n'
                            '    price: float = Field(gt=0)\n'
                            '    quantity: int = Field(gt=0)\n\n'
                            'def calculate_subtotal(order: OrderItem) -> float:\n'
                            '    return round(order.price * order.quantity, 2)')
            code2_kind = "plain"
            ex_lang = "python"
            ex_version = version
            ex_prompt = ("Implement filter_active_records(records, threshold) which "
                         "returns only records where active is True and val >= threshold.")
            ex_starter = 'def filter_active_records(records, threshold):\n    pass\n'
            ex_tests = ("def test_filter(func):\n"
                        "    data = [{'id': 1, 'val': 10, 'active': True}, "
                        "{'id': 2, 'val': 2, 'active': True}, "
                        "{'id': 3, 'val': 15, 'active': False}]\n"
                        "    res = func(data, 5)\n"
                        "    assert len(res) == 1 and res[0]['id'] == 1\n"
                        "    return True\n")
            ex_reference = ("def filter_active_records(records, threshold):\n"
                            "    return [r for r in records if r.get('active') "
                            "and r.get('val', 0) >= threshold]\n")
            ex_naive = ("def filter_active_records(records, threshold):\n"
                        "    return [r for r in records if r.get('val', 0) >= threshold]\n")

        slides = [
            {
                "id": "s_001", "type": "title", "title": topic,
                "bullets": [
                    f"Comprehensive deep dive into {topic}",
                    f"Production grade patterns for {', '.join(stack.keys())}",
                    "Verified live code and proven unit tests",
                ],
                "code": [], "diagram": None,
                "notes": (f"Welcome everyone to {topic}. All material in this deck "
                          "has been compiled and verified in sandbox containers."),
            },
            {
                "id": "s_002", "type": "diagram",
                "title": "System Architecture & Foundations",
                "bullets": [
                    "Layered separation of concerns",
                    "Automated sandbox verification on every snippet",
                    "Deterministic contracts between UI, API, and Sandbox",
                ],
                "code": [],
                "diagram": {
                    "id": "g_001", "kind": "mermaid",
                    "source": ("graph LR\n  Trainer[Trainer Input] --> Orchestrator[FastAPI Orchestrator]\n"
                               "  Orchestrator --> Sandbox[Execution Sandbox]\n"
                               "  Sandbox --> PPTX[Verified Presentation]"),
                },
                "notes": "Discuss architectural layers.",
            },
            {
                "id": "s_003", "type": "code",
                "title": "Primary Controller & Routing",
                "bullets": [
                    "Clean routing and response contracts",
                    "Strongly typed DTO serialization",
                    f"Targeting {lang.upper()} {version}",
                ],
                "code": [{
                    "id": "c_001", "lang": lang, "version": version,
                    "kind": code1_kind, "source": code1_source,
                    "expected_output": code1_output,
                    "verified": "unverified", "attempts": 0,
                }],
                "diagram": None,
                "notes": "Walk through routing declarations and immutability.",
            },
            {
                "id": "s_004", "type": "code",
                "title": "Data Validation & Safety",
                "bullets": [
                    "Input constraint verification",
                    "Preventing invalid state from propagating",
                    "Declarative error mapping",
                ],
                "code": [{
                    "id": "c_002", "lang": lang, "version": version,
                    "kind": code2_kind, "source": code2_source,
                    "expected_output": None,
                    "verified": "unverified", "attempts": 0,
                }],
                "diagram": None,
                "notes": "Explain how declarative validations eliminate manual checks.",
            },
            {
                "id": "s_005", "type": "content",
                "title": "Execution Pipeline & Concurrency",
                "bullets": [
                    "Event-driven request flow through middleware",
                    "Virtual threads / async coroutines for throughput",
                    "Non-blocking I/O for scalable operations",
                ],
                "code": [],
                "diagram": {
                    "id": "g_002", "kind": "mermaid",
                    "source": ("flowchart TD\n  Req[Client Request] --> Pipe[Pipeline Filter]\n"
                               "  Pipe --> Worker[Thread Worker]\n"
                               "  Worker --> Resp[Status 200 OK]"),
                },
                "notes": "Illustrate how requests are dispatched.",
            },
            {
                "id": "s_006", "type": "exercise",
                "title": "Hands-on Lab: Business Rules Engine",
                "bullets": [
                    "Implement business logic with validation rules",
                    "Dual-prover verified: reference passes, naive fails",
                    "Run test suites locally to verify",
                ],
                "code": [], "diagram": None,
                "notes": "Give students 15 minutes for the exercise.",
            },
            {
                "id": "s_007", "type": "summary",
                "title": "Summary & Recommended Practices",
                "bullets": [
                    "Maintain strict controller / domain separation",
                    "Back educational snippets with automated tests",
                    "Download the verification report for full audit details",
                ],
                "code": [], "diagram": None,
                "notes": "Summarize key lessons and field Q&A.",
            },
        ]

        exercises = [
            {
                "id": "e_001",
                "title": f"{topic} Core Exercise",
                "lang": ex_lang,
                "version": ex_version,
                "prompt": ex_prompt,
                "starter": ex_starter,
                "tests": ex_tests,
                "reference": ex_reference,
                "naive": ex_naive,
                "proof": {"reference_passes": None, "naive_fails": None},
            }
        ]

        quiz = [
            {
                "id": "q_001",
                "question": f"What is the primary benefit of declarative validation in {topic}?",
                "options": [
                    "Separates validation rules from core business logic cleanly",
                    "Increases bytecode file size",
                    "Disables HTTP status codes",
                    "Forces all responses to be XML",
                ],
                "answer_index": 0,
                "explanation": "Declarative annotations keep methods focused on domain workflows.",
            }
        ]

        cheat_sheet = (
            f"# {topic} Quick Reference\n\n"
            f"## Core Stack\n"
            f"- Runtime: {lang.upper()} {version}\n"
            f"- Framework: {', '.join(stack.keys())}\n\n"
            f"## Key Rules\n"
            f"1. Never ship unverified code to slides.\n"
            f"2. Ensure input constraints reject bad payloads with HTTP 400.\n"
            f"3. Keep bullet points under 16 words for readability.\n"
        )

        return {
            "deck_id": deck_id,
            "topic": topic,
            "level": level,
            "minutes": minutes,
            "stack": stack,
            "slides": slides,
            "exercises": exercises,
            "quiz": quiz,
            "cheat_sheet": cheat_sheet,
        }
