"""
Generator: outline -> full deck JSON.
Uses local Qwen3 via Ollama (primary) for content generation.
Falls back to deterministic generation when Ollama is unavailable.
"""
import os
import re
import json
import logging
import time
import uuid
from typing import Dict, Any, List, Optional

import httpx

logger = logging.getLogger(__name__)

try:
    from apps.api.config import settings
except ImportError:
    import config as _cfg

    class _Settings:
        OLLAMA_BASE_URL = getattr(_cfg, "OLLAMA_BASE_URL", "http://localhost:11434")
        OLLAMA_MODEL = getattr(_cfg, "OLLAMA_MODEL", "qwen3:8b")
        OLLAMA_TIMEOUT_SEC = getattr(_cfg, "OLLAMA_TIMEOUT_SEC", 120)

    settings = _Settings()

try:
    from apps.api.speaker_notes import build_trainer_delivery_notes
except ImportError:
    from speaker_notes import build_trainer_delivery_notes

try:
    from apps.api.generator.docker_benchmark import build_docker_benchmark_deck
except ImportError:
    try:
        from generator.docker_benchmark import build_docker_benchmark_deck
    except ImportError:
        build_docker_benchmark_deck = None

__all__ = [
    "CourseGenerator",
    "_patch_deck",
    "_infer_lang_and_version",
    "_parse_json_response",
    "_build_qwen_prompt",
    "check_ollama_health",
    "build_docker_benchmark_deck",
]


# ---------------------------------------------------------------------------
# Ollama / Qwen health check
# ---------------------------------------------------------------------------

def check_ollama_health() -> bool:
    """Return True if Ollama is reachable and the configured model is available."""
    try:
        r = httpx.get(
            f"{settings.OLLAMA_BASE_URL}/api/tags",
            timeout=5.0,
        )
        if r.status_code != 200:
            return False
        models = [m.get("name", "") for m in r.json().get("models", [])]
        target = settings.OLLAMA_MODEL
        # Match either exact name or name without tag
        return any(target in m or m.startswith(target.split(":")[0]) for m in models)
    except Exception:
        return False


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


def _build_qwen_prompt(topic: str, level: str, minutes: int,
                       stack: Dict[str, str], lang: str, version: str) -> str:
    """Build a prompt for Qwen/Ollama that produces schema-valid deck JSON."""
    deck_id = f"d_{uuid.uuid4().hex[:8]}"
    kind_hint = "plain" if lang == "python" else "plain or spring-fragment"
    topic_lower = topic.lower()

    if any(k in topic_lower for k in ("variable", "datatype", "data type", "naming rule", "type conversion", "mutability")):
        topic_guidance = (
            "CRITICAL TOPIC REQUIREMENTS (Python Variables & Fundamentals):\n"
            "- Focus strictly on variable assignment, naming rules (PEP 8), data types (int, float, str, bool),\n"
            "  type conversion (casting), and mutability vs immutability.\n"
            "- Do NOT generate web server, REST API, FastAPI, or microservice architecture slides.\n"
            "- Code examples must directly show variable assignments, type conversions, and mutability behavior.\n"
        )
    elif any(k in topic_lower for k in ("fastapi", "rest", "api", "microservice")):
        topic_guidance = (
            f"CRITICAL TOPIC REQUIREMENTS ({topic}):\n"
            "- Focus on REST API endpoints, request handling, response models, and data validation.\n"
        )
    elif any(k in topic_lower for k in ("docker", "container", "containerization", "podman", "cgroup", "namespaces", "oci")):
        topic_guidance = (
            f"CRITICAL TOPIC REQUIREMENTS (Docker Masterclass - {topic}):\n"
            "- Structure content across real modules: architecture (dockerd/containerd/runc), namespaces & cgroups,\n"
            "  image layers & overlay2 CoW, Dockerfile hygiene (BuildKit, multi-stage), port publishing, volumes vs bind mounts,\n"
            "  networking drivers (bridge, host, overlay), troubleshooting runbooks, and guided hands-on lab.\n"
            "- Do NOT generate generic or irrelevant code; use real Docker instructions or real microservice code.\n"
        )
    else:
        topic_guidance = (
            f"CRITICAL TOPIC REQUIREMENTS:\n"
            f"- All slide titles, bullet points, code examples, exercises, and quiz items MUST strictly pertain to '{topic}'.\n"
            "- Do NOT generate generic or unrelated web frameworks unless explicitly requested in the topic.\n"
        )

    target_slides = "20-25" if minutes >= 75 else ("12-16" if minutes >= 45 else "6-10")

    return f"""You are a course-material generator for the Verified Course Material Studio.
Generate a complete, high-quality lesson deck about "{topic}" for {level} students ({minutes} min).

/no_think

{topic_guidance}
Return **only** a JSON object (no markdown fences, no commentary, no thinking tags).

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
  "meta": {{ "source": "qwen-ollama", "model": "{settings.OLLAMA_MODEL}" }}
}}

### Slide rules
Each slide object must have **exactly** these keys (no extra keys):
  id (string, pattern s_NNN), type, title, bullets, code, diagram, notes

- type must be one of: "title", "section", "content", "code", "diagram", "exercise", "summary"
- bullets: array of strings (max 5 items, each <=120 chars)
- title: string, max 90 chars
- code: an array (may be empty). Each element:
    {{ "id": "c_NNN", "lang": "{lang}", "version": "{version}",
       "kind": "{kind_hint}", "source": "...", "expected_output": null,
       "verified": "unverified", "attempts": 0 }}
- diagram: either null or {{ "id": "g_NNN", "kind": "mermaid", "source": "..." }}
- notes: string (detailed trainer speaker notes for delivery, min 80-150 words with explanation, key questions, and troubleshooting)

### Exercise rules
Each exercise must have **exactly** these keys:
  id (pattern e_NNN), title, lang, version, prompt, starter, tests, reference, naive, proof
- lang must be "{lang}", version must be "{version}"
- proof: {{ "reference_passes": null, "naive_fails": null }}

### Quiz rules
Each quiz item must have **exactly** these keys:
  id (pattern q_NNN), question, options (2-6 strings), answer_index (int 0-5), explanation

### Content guidelines
- Generate {target_slides} slides with varied types to thoroughly cover the topic for the allocated {minutes} minutes.
- All code must be {lang.upper()} {version}. Write real, correct, runnable code.
- If lang is python use kind "plain". If lang is java, "plain" for standalone programs or "spring-fragment" for Spring Boot fragments.
- Include at least 1 exercise and at least 3 quiz questions directly testing "{topic}".
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

    # 3. Strip <think>...</think> tags (Qwen3 thinking mode)
    no_think = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    no_think = no_think.strip()
    if no_think != text:
        try:
            return json.loads(no_think)
        except json.JSONDecodeError:
            pass
        # try fences on the stripped text
        cleaned2 = re.sub(r"^```(?:json)?\s*\n?", "", no_think, flags=re.MULTILINE)
        cleaned2 = re.sub(r"\n?```\s*$", "", cleaned2, flags=re.MULTILINE)
        cleaned2 = cleaned2.strip()
        try:
            return json.loads(cleaned2)
        except json.JSONDecodeError:
            pass

    # 4. Find outermost { ... }
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

    # Normalize top-level fields
    level = str(deck.get("level", "beginner")).lower()
    deck["level"] = level if level in {"beginner", "intermediate", "advanced"} else "beginner"
    try:
        deck["minutes"] = int(deck.get("minutes", 60))
    except (ValueError, TypeError):
        deck["minutes"] = 60
    if not deck.get("topic"):
        deck["topic"] = "Software Development"

    # -- slides --
    for i, slide in enumerate(deck.get("slides", [])):
        slide.setdefault("id", f"s_{i + 1:03d}")
        slide.setdefault("bullets", [])
        slide.setdefault("notes", "")

        # Ensure substantive notes (trainer-grade depth)
        current_notes = slide.get("notes", "")
        if (not current_notes or len(current_notes.split()) < 35) and build_trainer_delivery_notes is not None:
            slide["notes"] = build_trainer_delivery_notes(
                slide_title=slide.get("title", f"Slide {i + 1}"),
                slide_type=slide.get("type", "content"),
                bullets=slide.get("bullets", []),
                topic=deck.get("topic", "Software Engineering"),
                level=deck.get("level", "intermediate"),
                time_minutes=max(2, deck.get("minutes", 60) // max(len(deck.get("slides", [1])), 1)),
                custom_guidance={"explanation": current_notes} if current_notes else None,
            )

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

        # title ensure present and length
        if "title" not in slide or not slide["title"]:
            slide["title"] = f"Slide {i + 1}"
        elif len(slide["title"]) > 90:
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

        # Ensure code strings are strings, not arrays
        for str_field in ("starter", "tests", "reference", "naive"):
            val = ex.get(str_field)
            if isinstance(val, list):
                ex[str_field] = "\n".join(str(x) for x in val)
            elif val is None:
                ex[str_field] = ""
            else:
                ex[str_field] = str(val)

        if not ex["tests"]:
            ex["tests"] = "# TODO: tests"
        if not ex["reference"]:
            ex["reference"] = "# TODO: reference solution"
        if not ex["naive"]:
            ex["naive"] = "# TODO: naive solution"

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


# ---------------------------------------------------------------------------
# Topic-aware Deterministic Deck Builders
# ---------------------------------------------------------------------------

def _build_python_variables_deck(deck_id: str, topic: str, level: str, minutes: int,
                                 stack: Dict[str, str], version: str) -> Dict[str, Any]:
    """Deterministic, pedagogically sound deck specifically for Python Variables."""
    code1_source = (
        '# Variable assignment and primitive data types\n'
        'student_name: str = "Ada Lovelace"\n'
        'student_age: int = 24\n'
        'gpa_score: float = 3.92\n'
        'is_enrolled: bool = True\n\n'
        '# Dynamic re-assignment (re-binding the label)\n'
        'current_status = "active"\n'
        'print(f"{student_name} status: {current_status} ({type(current_status).__name__})")\n\n'
        'current_status = 200  # valid in Python (dynamic typing)\n'
        'print(f"Updated status code: {current_status} ({type(current_status).__name__})")\n'
    )
    code1_output = (
        'Ada Lovelace status: active (str)\n'
        'Updated status code: 200 (int)'
    )

    code2_source = (
        '# Type conversion (explicit casting)\n'
        'raw_entry = "42"\n'
        'numeric_id = int(raw_entry)\n'
        'str_id = str(numeric_id)\n'
        'float_val = float("3.14159")\n\n'
        '# Mutability vs Immutability\n'
        'title = "python"\n'
        '# Strings are immutable: title[0] = "P" raises TypeError\n'
        'title = title.capitalize()  # creates a new string object\n\n'
        '# Lists are mutable: modified in-place\n'
        'scores = [88, 92]\n'
        'scores.append(95)\n'
        'print(f"Capitalized: {title}, Final scores: {scores}")\n'
    )
    code2_output = 'Capitalized: Python, Final scores: [88, 92, 95]'

    slides = [
        {
            "id": "s_001",
            "type": "title",
            "title": topic,
            "bullets": [
                "Understanding variable assignment and dynamic typing in Python",
                "PEP 8 identifier naming rules and reserved keywords",
                "Primitive data types, type conversion, and mutability concepts",
            ],
            "code": [],
            "diagram": None,
            "notes": (
                f"Welcome to {topic}. In this session, we will cover how Python binds labels to "
                "objects in memory, naming conventions, core data types, and type conversion."
            ),
        },
        {
            "id": "s_002",
            "type": "content",
            "title": "Variable Assignment & Naming Rules",
            "bullets": [
                "Variables are created automatically upon first assignment with '='",
                "Identifiers must start with a letter (a-z, A-Z) or underscore (_)",
                "Names cannot begin with a number and cannot contain hyphens or spaces",
                "Variable names are case-sensitive: count, Count, and COUNT are distinct",
                "Cannot use reserved keywords such as if, for, class, def, or return",
            ],
            "code": [],
            "diagram": None,
            "notes": (
                "Emphasize that variables in Python do not have fixed types; they are references "
                "pointing to typed objects in heap memory."
            ),
        },
        {
            "id": "s_003",
            "type": "code",
            "title": "Variable Assignment & Primitive Types",
            "bullets": [
                "Core primitive types: int, float, str, and bool",
                "Type hints (PEP 484) document intended types clearly",
                "Use type() to inspect runtime type and verify behavior",
            ],
            "code": [{
                "id": "c_001", "lang": "python", "version": version,
                "kind": "plain", "source": code1_source,
                "expected_output": code1_output,
                "verified": "unverified", "attempts": 0,
            }],
            "diagram": None,
            "notes": "Walk through each assignment. Contrast dynamic typing with statically typed languages.",
        },
        {
            "id": "s_004",
            "type": "code",
            "title": "Type Conversion & Mutability Concepts",
            "bullets": [
                "Explicit conversion functions: int(), float(), str(), bool()",
                "Immutable objects (int, float, str, tuple) cannot be modified in-place",
                "Mutable objects (list, dict, set) can be mutated without changing identity",
                "Reassignment creates a new object binding in memory",
            ],
            "code": [{
                "id": "c_002", "lang": "python", "version": version,
                "kind": "plain", "source": code2_source,
                "expected_output": code2_output,
                "verified": "unverified", "attempts": 0,
            }],
            "diagram": None,
            "notes": "Explain why attempting in-place modification on strings raises a TypeError.",
        },
        {
            "id": "s_005",
            "type": "diagram",
            "title": "Python Memory Model: Object References",
            "bullets": [
                "Variables are named references (pointers) to objects in heap memory",
                "Assignment binds a variable name to an object address",
                "Multiple variables can point to the same immutable or mutable object",
            ],
            "code": [],
            "diagram": {
                "id": "g_001",
                "kind": "mermaid",
                "source": (
                    "flowchart LR\n"
                    "  VarA[Variable: student_name] --> Obj1[str: 'Ada Lovelace']\n"
                    "  VarB[Variable: age] --> Obj2[int: 24]\n"
                    "  VarC[Variable: scores] --> Obj3[list: 88, 92, 95]"
                ),
            },
            "notes": "Illustrate how variables reference objects rather than allocating physical memory slots directly.",
        },
        {
            "id": "s_006",
            "type": "exercise",
            "title": "Hands-on Lab: Normalize User Profile Variables",
            "bullets": [
                "Write a function to sanitize raw string inputs into typed variables",
                "Convert string numeric values to int and float safely",
                "Dual-prover verified: reference implementation passes, naive fails",
            ],
            "code": [],
            "diagram": None,
            "notes": "Give students 10 minutes to complete the variable normalization lab.",
        },
        {
            "id": "s_007",
            "type": "summary",
            "title": "Summary & Common Mistakes to Avoid",
            "bullets": [
                "Never shadow built-in names like 'list', 'str', 'id', or 'type'",
                "Always assign variables before referencing them to avoid NameError",
                "Follow snake_case naming conventions for readable, idiomatic code",
                "Distinguish between in-place mutation and variable re-assignment",
            ],
            "code": [],
            "diagram": None,
            "notes": "Review key takeaways and field questions from students.",
        },
    ]

    exercises = [
        {
            "id": "e_001",
            "title": "Normalize Profile Variables",
            "lang": "python",
            "version": version,
            "prompt": (
                "Implement normalize_profile(name_raw, age_raw, score_raw) so it returns a dict "
                "with 'name' (stripped string), 'age' (int), and 'score' (float)."
            ),
            "starter": "def normalize_profile(name_raw, age_raw, score_raw):\n    # TODO: cast types and return normalized dict\n    pass\n",
            "tests": (
                "def test_normalize(func):\n"
                "    data = func('  Ada Lovelace ', '24', '98.5')\n"
                "    assert data == {'name': 'Ada Lovelace', 'age': 24, 'score': 98.5}\n"
                "    assert isinstance(data['age'], int)\n"
                "    assert isinstance(data['score'], float)\n"
                "    assert isinstance(data['name'], str)\n"
                "    return True\n"
            ),
            "reference": (
                "def normalize_profile(name_raw, age_raw, score_raw):\n"
                "    return {\n"
                "        'name': str(name_raw).strip(),\n"
                "        'age': int(age_raw),\n"
                "        'score': float(score_raw),\n"
                "    }\n"
            ),
            "naive": (
                "def normalize_profile(name_raw, age_raw, score_raw):\n"
                "    # Naive bug: forgets to cast types and strip whitespace\n"
                "    return {'name': name_raw, 'age': age_raw, 'score': score_raw}\n"
            ),
            "proof": {"reference_passes": None, "naive_fails": None},
        }
    ]

    quiz = [
        {
            "id": "q_001",
            "question": "Which of the following is a valid Python variable name following PEP 8 conventions?",
            "options": [
                "user_total_count",
                "2nd_variable",
                "user-total-count",
                "class",
            ],
            "answer_index": 0,
            "explanation": "Identifiers must start with a letter or underscore, cannot contain hyphens, and cannot be reserved keywords like 'class'.",
        },
        {
            "id": "q_002",
            "question": "Which of the following data types in Python is immutable?",
            "options": [
                "str (String)",
                "list (List)",
                "dict (Dictionary)",
                "set (Set)",
            ],
            "answer_index": 0,
            "explanation": "Strings, integers, floats, and tuples are immutable in Python; their contents cannot be changed in-place.",
        },
        {
            "id": "q_003",
            "question": "What is the return value of type(int('42')) in Python 3?",
            "options": [
                "<class 'int'>",
                "<class 'str'>",
                "<class 'float'>",
                "TypeError",
            ],
            "answer_index": 0,
            "explanation": "int('42') explicitly converts the string into an integer object of type int.",
        },
    ]

    cheat_sheet = (
        f"# {topic} Quick Reference (Python {version})\n\n"
        "## Variable Assignment & Rules\n"
        "- Assignment: `name = value` binds a variable name to an object in memory.\n"
        "- Naming: Start with `[a-zA-Z_]`, followed by letters, digits, or underscores.\n"
        "- Convention: Use `snake_case` for variables and function names (PEP 8).\n"
        "- Reserved keywords: Cannot name variables `if`, `else`, `while`, `def`, `class`, `import`, etc.\n\n"
        "## Core Built-in Types\n"
        "- `int`: Whole numbers (`42`, `-7`)\n"
        "- `float`: Decimal numbers (`3.14159`)\n"
        "- `str`: Text sequence (`'hello'`, `\"world\"`)\n"
        "- `bool`: Logical values (`True`, `False`)\n\n"
        "## Type Conversion Functions\n"
        "- `int(x)`: Converts to integer (e.g. `int('10') -> 10`)\n"
        "- `float(x)`: Converts to float (e.g. `float('3.5') -> 3.5`)\n"
        "- `str(x)`: Converts to string (e.g. `str(25) -> '25'`)\n"
        "- `bool(x)`: Converts to boolean (truthiness check)\n\n"
        "## Mutability\n"
        "- **Immutable**: `int`, `float`, `str`, `tuple`, `frozenset`\n"
        "- **Mutable**: `list`, `dict`, `set`\n"
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
        "meta": {
            "source": "deterministic-fallback",
            "model": "none",
            "notice": "Offline deterministic generator used (Qwen/Ollama was unavailable)."
        }
    }


def _build_python_fastapi_deck(deck_id: str, topic: str, level: str, minutes: int,
                               stack: Dict[str, str], version: str) -> Dict[str, Any]:
    """Deterministic deck for FastAPI / REST API topics."""
    code1_source = (
        'from fastapi import FastAPI\n'
        'from pydantic import BaseModel\n\n'
        'app = FastAPI(title="Course Service")\n\n'
        'class HealthCheck(BaseModel):\n'
        '    status: str\n'
        '    active: bool\n\n'
        '@app.get("/health", response_model=HealthCheck)\n'
        'async def check_health():\n'
        '    return {"status": "HEALTHY", "active": True}\n'
    )
    code2_source = (
        'from pydantic import BaseModel, Field\n\n'
        'class OrderItem(BaseModel):\n'
        '    item_id: str\n'
        '    price: float = Field(gt=0, description="Price must be positive")\n'
        '    quantity: int = Field(gt=0, description="Quantity must be at least 1")\n\n'
        'def calculate_subtotal(order: OrderItem) -> float:\n'
        '    return round(order.price * order.quantity, 2)\n'
    )

    slides = [
        {
            "id": "s_001", "type": "title", "title": topic,
            "bullets": [
                f"Comprehensive deep dive into {topic}",
                "Production-grade FastAPI routing and Pydantic validation patterns",
                "Structured unit tests and verifiable code examples",
            ],
            "code": [], "diagram": None,
            "notes": f"Welcome to {topic}. In this session we explore high-performance REST APIs with FastAPI.",
        },
        {
            "id": "s_002", "type": "diagram",
            "title": "System Architecture & Request Flow",
            "bullets": [
                "Layered separation of concerns and ASGI routing",
                "Automated request validation before business execution",
                "Type-safe contracts between client and server",
            ],
            "code": [],
            "diagram": {
                "id": "g_001", "kind": "mermaid",
                "source": (
                    "graph LR\n"
                    "  Client[HTTP Client] --> Router[FastAPI Router]\n"
                    "  Router --> Model[Pydantic Validation]\n"
                    "  Model --> Handler[Async Endpoint Handler]"
                ),
            },
            "notes": "Discuss architectural layers and ASGI middleware flow.",
        },
        {
            "id": "s_003", "type": "code",
            "title": "Primary Controller & Routing",
            "bullets": [
                "Declarative route decorators and HTTP status codes",
                "Strongly typed response models and OpenAPI schema generation",
                f"Targeting Python {version} and modern async/await syntax",
            ],
            "code": [{
                "id": "c_001", "lang": "python", "version": version,
                "kind": "plain", "source": code1_source,
                "expected_output": None,
                "verified": "unverified", "attempts": 0,
            }],
            "diagram": None,
            "notes": "Walk through routing declarations and async coroutines.",
        },
        {
            "id": "s_004", "type": "code",
            "title": "Data Validation & Safety with Pydantic",
            "bullets": [
                "Input constraint enforcement at the request boundary",
                "Field-level constraints preventing invalid state",
                "Automatic HTTP 422 error payloads for invalid inputs",
            ],
            "code": [{
                "id": "c_002", "lang": "python", "version": version,
                "kind": "plain", "source": code2_source,
                "expected_output": None,
                "verified": "unverified", "attempts": 0,
            }],
            "diagram": None,
            "notes": "Explain how declarative validations eliminate manual validation checks.",
        },
        {
            "id": "s_005", "type": "content",
            "title": "Execution Pipeline & Concurrency",
            "bullets": [
                "Non-blocking asynchronous I/O with asyncio event loop",
                "Dependency injection system for database and auth sessions",
                "High throughput request concurrency under load",
            ],
            "code": [],
            "diagram": {
                "id": "g_002", "kind": "mermaid",
                "source": (
                    "flowchart TD\n"
                    "  Req[Incoming HTTP Request] --> Dep[Dependency Injector]\n"
                    "  Dep --> Work[Async Worker Task]\n"
                    "  Work --> Resp[JSON Response 200 OK]"
                ),
            },
            "notes": "Illustrate how requests are dispatched without blocking thread execution.",
        },
        {
            "id": "s_006", "type": "exercise",
            "title": "Hands-on Lab: Business Rules Filter",
            "bullets": [
                "Implement business logic handling record validation",
                "Dual-prover verified: reference passes, naive fails",
                "Run test suites locally to verify requirements",
            ],
            "code": [], "diagram": None,
            "notes": "Give students 15 minutes for the exercise.",
        },
        {
            "id": "s_007", "type": "summary",
            "title": "Summary & Recommended Practices",
            "bullets": [
                "Maintain strict controller / domain separation",
                "Leverage Pydantic models for all external input boundaries",
                "Write comprehensive test assertions for edge cases",
            ],
            "code": [], "diagram": None,
            "notes": "Summarize key lessons and field Q&A.",
        },
    ]

    exercises = [
        {
            "id": "e_001",
            "title": f"{topic} Core Exercise",
            "lang": "python",
            "version": version,
            "prompt": "Implement filter_active_records(records, threshold) which returns only records where active is True and val >= threshold.",
            "starter": "def filter_active_records(records, threshold):\n    pass\n",
            "tests": (
                "def test_filter(func):\n"
                "    data = [{'id': 1, 'val': 10, 'active': True}, "
                "{'id': 2, 'val': 2, 'active': True}, "
                "{'id': 3, 'val': 15, 'active': False}]\n"
                "    res = func(data, 5)\n"
                "    assert len(res) == 1 and res[0]['id'] == 1\n"
                "    return True\n"
            ),
            "reference": (
                "def filter_active_records(records, threshold):\n"
                "    return [r for r in records if r.get('active') and r.get('val', 0) >= threshold]\n"
            ),
            "naive": (
                "def filter_active_records(records, threshold):\n"
                "    return [r for r in records if r.get('val', 0) >= threshold]\n"
            ),
            "proof": {"reference_passes": None, "naive_fails": None},
        }
    ]

    quiz = [
        {
            "id": "q_001",
            "question": f"What is the primary benefit of declarative Pydantic validation in {topic}?",
            "options": [
                "Separates validation rules from core business logic cleanly",
                "Increases bytecode file size",
                "Disables HTTP status codes",
                "Forces all responses to be XML",
            ],
            "answer_index": 0,
            "explanation": "Declarative annotations keep methods focused on domain workflows while automating validation.",
        }
    ]

    cheat_sheet = (
        f"# {topic} Quick Reference\n\n"
        f"## Core Stack\n"
        f"- Runtime: Python {version}\n"
        f"- Framework: {', '.join(stack.keys())}\n\n"
        "## Key Rules\n"
        "1. Define response models explicitly for OpenAPI schema generation.\n"
        "2. Ensure input constraints reject bad payloads with HTTP 422.\n"
        "3. Use async def for I/O-bound endpoints.\n"
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
        "meta": {
            "source": "deterministic-fallback",
            "model": "none",
            "notice": "Offline deterministic generator used (Qwen/Ollama was unavailable)."
        }
    }


def _build_java_spring_deck(deck_id: str, topic: str, level: str, minutes: int,
                            stack: Dict[str, str], version: str) -> Dict[str, Any]:
    """Deterministic deck for Java / Spring Boot topics."""
    code1_source = (
        '@RestController\n'
        '@RequestMapping("/api/v1")\n'
        'public class AppController {\n'
        '    public record HealthStatus(String status, long time) {}\n\n'
        '    @GetMapping("/health")\n'
        '    public HealthStatus getHealth() {\n'
        '        return new HealthStatus("HEALTHY", System.currentTimeMillis());\n'
        '    }\n}'
    )
    code2_source = (
        'public class Main {\n'
        '    public record Greeting(String name) {}\n\n'
        '    public static void main(String[] args) {\n'
        '        Greeting g = new Greeting("World");\n'
        '        System.out.println("Hello, " + g.name());\n'
        '    }\n}'
    )

    slides = [
        {
            "id": "s_001", "type": "title", "title": topic,
            "bullets": [
                f"Comprehensive deep dive into {topic}",
                "Production-grade Spring Boot 3 controllers and Java 21 records",
                "Strongly typed DTO serialization and REST architecture",
            ],
            "code": [], "diagram": None,
            "notes": f"Welcome everyone to {topic}. In this session we cover enterprise Java patterns.",
        },
        {
            "id": "s_002", "type": "diagram",
            "title": "System Architecture & Request Dispatch",
            "bullets": [
                "Layered separation of concerns in Spring MVC",
                "DispatcherServlet request routing and handler mapping",
                "Declarative validation contracts",
            ],
            "code": [],
            "diagram": {
                "id": "g_001", "kind": "mermaid",
                "source": (
                    "graph LR\n"
                    "  Client[HTTP Client] --> Dispatcher[DispatcherServlet]\n"
                    "  Dispatcher --> Controller[Spring Controller]\n"
                    "  Controller --> Service[Domain Service]"
                ),
            },
            "notes": "Discuss Spring MVC architectural layers.",
        },
        {
            "id": "s_003", "type": "code",
            "title": "Primary Controller & Routing",
            "bullets": [
                "Clean routing annotations and response contracts",
                "Strongly typed DTO serialization with Java records",
                f"Targeting Java {version} and Spring Boot 3",
            ],
            "code": [{
                "id": "c_001", "lang": "java", "version": version,
                "kind": "spring-fragment", "source": code1_source,
                "expected_output": None,
                "verified": "unverified", "attempts": 0,
            }],
            "diagram": None,
            "notes": "Walk through routing declarations and immutability.",
        },
        {
            "id": "s_004", "type": "code",
            "title": "Immutable Domain Records",
            "bullets": [
                "Compact record constructors and immutability",
                "Thread-safe data transfer objects",
                "Clean integration with modern Java language features",
            ],
            "code": [{
                "id": "c_002", "lang": "java", "version": version,
                "kind": "plain", "source": code2_source,
                "expected_output": "Hello, World",
                "verified": "unverified", "attempts": 0,
            }],
            "diagram": None,
            "notes": "Explain how records simplify immutable domain models.",
        },
        {
            "id": "s_005", "type": "summary",
            "title": "Summary & Best Practices",
            "bullets": [
                "Maintain strict controller / service separation",
                "Use Java records for immutable request and response DTOs",
                "Cover edge cases with thorough JUnit 5 tests",
            ],
            "code": [], "diagram": None,
            "notes": "Summarize key lessons and field Q&A.",
        },
    ]

    exercises = [
        {
            "id": "e_001",
            "title": f"{topic} Core Exercise",
            "lang": "java",
            "version": version,
            "prompt": "Implement Greeter.greet(name) so it returns 'Hello, <name>!' and 'Hello, stranger!' for null or blank names.",
            "starter": "public class Greeter {\n    public static String greet(String name) {\n        // TODO\n        return null;\n    }\n}",
            "tests": (
                "import org.junit.jupiter.api.Test;\n"
                "import static org.junit.jupiter.api.Assertions.assertEquals;\n\n"
                "class GreeterTest {\n"
                "    @Test void greetsByName() {\n"
                "        assertEquals(\"Hello, Ada!\", Greeter.greet(\"Ada\"));\n    }\n"
                "    @Test void handlesBlank() {\n"
                "        assertEquals(\"Hello, stranger!\", Greeter.greet(\"  \"));\n"
                "        assertEquals(\"Hello, stranger!\", Greeter.greet(null));\n    }\n}"
            ),
            "reference": (
                "public class Greeter {\n"
                "    public static String greet(String name) {\n"
                "        if (name == null || name.isBlank()) return \"Hello, stranger!\";\n"
                "        return \"Hello, \" + name + \"!\";\n    }\n}"
            ),
            "naive": (
                "public class Greeter {\n"
                "    public static String greet(String name) {\n"
                "        return \"Hello, \" + name + \"!\";\n    }\n}"
            ),
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
        f"- Runtime: Java {version}\n"
        f"- Framework: {', '.join(stack.keys())}\n\n"
        "## Key Rules\n"
        "1. Prefer immutable Java records for DTOs.\n"
        "2. Ensure input constraints reject bad payloads with HTTP 400.\n"
        "3. Use descriptive method names and clear return types.\n"
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
        "meta": {
            "source": "deterministic-fallback",
            "model": "none",
            "notice": "Offline deterministic generator used (Qwen/Ollama was unavailable)."
        }
    }


# ===================================================================
# Public API — preserved for backward compatibility
# ===================================================================

class CourseGenerator:
    """
    Stage 2: Generates complete slide-level JSON, code snippets, notes,
    exercises, and quiz. Output satisfies deck.schema.json.

    Provider chain:
      1. Qwen3 via Ollama (local)
      2. Deterministic fallback (topic-aware, no external LLM needed)
    """

    # Expose helper methods on the class for backward compatibility
    _patch_deck = staticmethod(_patch_deck)
    _infer_lang_and_version = staticmethod(_infer_lang_and_version)

    def __init__(self, api_key: str = ""):
        # api_key kept for backward-compatible signature but is unused
        pass

    # ---- main entry point ----
    def generate_deck(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Try Qwen/Ollama first, then deterministic fallback."""
        topic = plan.get("topic", "Software Development")
        level = plan.get("level", "beginner")
        minutes = plan.get("minutes", 90)
        stack = plan.get("stack", {"python": "3.12"})
        lang, version = _infer_lang_and_version(stack, topic)

        # 1. Try Qwen / Ollama
        try:
            deck = self._generate_with_qwen(topic, level, minutes, stack, lang, version)
            if deck:
                deck["deck_id"] = plan.get("deck_id", deck.get("deck_id", f"d_{uuid.uuid4().hex[:8]}"))
                return deck
        except Exception as exc:
            logger.warning("Qwen/Ollama generation failed: %s", exc)

        # 2. Deterministic fallback
        return self._generate_deterministic(plan, lang, version)

    # ---- Qwen / Ollama path ----
    def _generate_with_qwen(self, topic, level, minutes, stack, lang, version):
        """Call Ollama /api/chat with Qwen model. Returns patched deck or None."""
        prompt = _build_qwen_prompt(topic, level, minutes, stack, lang, version)
        model = settings.OLLAMA_MODEL
        base_url = settings.OLLAMA_BASE_URL
        timeout = getattr(settings, "OLLAMA_TIMEOUT_SEC", 120)

        logger.info("Calling Qwen/Ollama (%s) at %s for topic=%r ...", model, base_url, topic)
        t0 = time.time()

        response = httpx.post(
            f"{base_url}/api/chat",
            json={
                "model": model,
                "stream": False,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=float(timeout),
        )

        elapsed = time.time() - t0
        logger.info("Ollama responded in %.1fs (status %d)", elapsed, response.status_code)

        if response.status_code != 200:
            logger.warning("Ollama returned status %d: %s", response.status_code, response.text[:300])
            return None

        data = response.json()
        content = data.get("message", {}).get("content", "")
        if not content:
            logger.warning("Ollama returned empty content")
            return None

        raw = _parse_json_response(content)
        if raw is None:
            logger.warning("Failed to parse JSON from Qwen response")
            return None

        # Ensure meta reflects the provider
        raw.setdefault("meta", {})
        raw["meta"]["source"] = "qwen-ollama"
        raw["meta"]["model"] = model
        raw["meta"]["generation_time_sec"] = round(elapsed, 2)

        return _patch_deck(raw, lang, version)

    # ---- Deterministic fallback (schema-valid, topic-aware) ----
    def _generate_deterministic(self, plan: Dict[str, Any],
                                lang: str, version: str) -> Dict[str, Any]:
        deck_id = plan.get("deck_id", f"d_{uuid.uuid4().hex[:8]}")
        topic = plan.get("topic", "Modern Software Architecture")
        level = plan.get("level", "beginner")
        minutes = plan.get("minutes", 90)
        stack = plan.get("stack", {"python": "3.12"})

        topic_lower = topic.lower()
        stack_keys = " ".join(stack.keys()).lower()

        # Route to appropriate topic-specific builder
        if lang == "java" or "java" in topic_lower or "spring" in topic_lower or "java" in stack_keys:
            return _build_java_spring_deck(deck_id, topic, level, minutes, stack, version)

        # Check for Docker / Containerization topics
        if any(k in topic_lower for k in ("docker", "container", "containerization", "podman", "cgroup", "namespaces", "oci", "image")) and build_docker_benchmark_deck is not None:
            return build_docker_benchmark_deck(deck_id, topic, level, minutes, stack, version)

        # Check for Python Variables / Fundamentals
        if any(k in topic_lower for k in ("variable", "datatype", "data type", "naming rule", "type conversion", "mutability")):
            return _build_python_variables_deck(deck_id, topic, level, minutes, stack, version)

        # Check for FastAPI / REST / API topics
        if any(k in topic_lower for k in ("fastapi", "rest", "api", "microservice", "route", "controller", "pydantic", "endpoint")):
            return _build_python_fastapi_deck(deck_id, topic, level, minutes, stack, version)

        # Default for Python basics / general beginner Python
        if "python" in topic_lower and any(k in topic_lower for k in ("basic", "intro", "beginner", "fundamental", "syntax")):
            return _build_python_variables_deck(deck_id, topic, level, minutes, stack, version)

        # General Python fallback
        return _build_python_variables_deck(deck_id, topic, level, minutes, stack, version)
