"""
Stage 1 – Universal Course Planner
==================================
Generates an educational, level-adaptive course outline for ANY given topic.

AI Priority:
  1. Google Gemini 3.8 Flash (via GEMINI_API_KEY in .env)
  2. Anthropic Claude 3.5    (via ANTHROPIC_API_KEY in .env)
  3. Dynamic Deterministic Fallback (topic-aware & level-adaptive)
"""

import json
import re
import uuid
from typing import Any, Dict, List, Optional

from apps.api.config import settings

_PLAN_PROMPT = """\
You are a distinguished Principal Software Engineering Educator and Curriculum Architect.
Design a highly informative, production-grade course presentation outline for:

Topic          : {topic}
Audience Level : {level} (beginner | intermediate | advanced)
Duration       : {minutes} minutes
Tech Stack     : {stack}

Level Pedagogy Directives:
- BEGINNER:
  Focus on mental models, core intuitions, zero-assumption step-by-step concepts, clear analogies,
  annotated code syntax, and common rookie pitfalls to avoid.
- INTERMEDIATE:
  Focus on real-world production architectures, validation boundaries, structured error envelopes,
  concurrency, caching, pagination, idiomatic patterns, and unit/integration testing strategies.
- ADVANCED:
  Focus on runtime internals, memory/thread execution models, distributed systems invariants (CAP, PACELC, idempotency),
  low-level profiling, failure domain isolation (circuit breakers, bulkheads, backpressure), and high-throughput trade-offs.

CRITICAL TITLE & SPECIFICATION RULE:
Every slide title in "slide_specs" MUST be specific and concrete to "{topic}".
Do NOT use generic placeholders like "System Topology & Core Mental Model" or "First Runnable Core Implementation".
Instead use domain-specific titles (e.g. for "Kubernetes": "Cluster Topology: Pods, ReplicaSets & CNI Overlay", "Production Pod Manifest & Health Probes", "Ingress Controllers & Service Routing", etc.).

Output STRICT JSON only (no markdown code blocks, no prose):
{{
  "deck_id": "d_{short_id}",
  "topic": "{topic}",
  "level": "{level}",
  "minutes": {minutes},
  "stack": {{"language_or_framework": "version"}},
  "primary_lang": "e.g. python, java, typescript, rust, go, cpp, sql, etc.",
  "learning_objectives": [
    "Specific objective 1 for {level} students on {topic}",
    "Specific objective 2 for {level} students on {topic}",
    "Specific objective 3 for {level} students on {topic}"
  ],
  "slide_specs": [
    {{"id": "s_001", "type": "title",    "title": "{topic}: Hero Title & Foundations", "focus": "Course objectives, roadmap, prerequisites"}},
    {{"id": "s_002", "type": "overview", "title": "{topic}: Architecture & Core Mental Model", "focus": "Architectural breakdown and layered concerns"}},
    {{"id": "s_003", "type": "code",     "title": "{topic}: Primary Runnable Implementation", "focus": "Foundational implementation with explicit typing and structure"}},
    {{"id": "s_004", "type": "code",     "title": "{topic}: Defensive Validation & Failure Boundaries", "focus": "Input sanitization, boundary checks, and error contracts"}},
    {{"id": "s_005", "type": "concept",  "title": "{topic}: Execution Lifecycle & Runtime Flow", "focus": "Visual request lifecycle, async/thread flow, and data routing"}},
    {{"id": "s_006", "type": "code",     "title": "{topic}: Domain Operations & Integration", "focus": "Data access, atomic transactions, or domain orchestration"}},
    {{"id": "s_007", "type": "concept",  "title": "{topic}: Performance Optimization & Telemetry", "focus": "Latency optimization, cache-aside, metrics, and structured logs"}},
    {{"id": "s_008", "type": "exercise", "title": "Hands-On Lab: {topic} Challenge", "focus": "Real-world implementation problem testing core invariants"}},
    {{"id": "s_009", "type": "quiz_review", "title": "Knowledge Check: {topic} Review", "focus": "3 deep conceptual questions testing understanding and edge cases"}},
    {{"id": "s_010", "type": "summary",  "title": "Production Readiness Checklist & {topic} Best Practices", "focus": "Checklist, anti-patterns to avoid, and reference architecture"}}
  ],
  "exercise_spec": {{
    "id": "e_001",
    "title": "{topic} Hands-on Implementation",
    "language": "primary language",
    "difficulty": "{level}",
    "objective": "Description of the student implementation goal for {topic}"
  }}
}}
"""


def detect_primary_language(topic: str, stack: Optional[Dict[str, str]] = None) -> str:
    """Intelligently detects primary language from topic keywords or stack."""
    if stack:
        stack_str = " ".join(f"{k} {v}" for k, v in stack.items()).lower()
        if "rust" in stack_str:
            return "rust"
        if any(k in stack_str for k in ("typescript", "react", "next", "node", "javascript", "vue", "angular")):
            return "typescript"
        if "go" in stack_str or "golang" in stack_str:
            return "go"
        if any(k in stack_str for k in ("sql", "postgres", "mysql", "database", "sqlite")):
            return "sql"
        if "c++" in stack_str or "cpp" in stack_str:
            return "cpp"
        if any(k in stack_str for k in ("java", "spring", "jvm", "kotlin")):
            return "java"
        if any(k in stack_str for k in ("python", "fastapi", "django", "pytorch")):
            return "python"

    t = topic.lower()
    if "rust" in t:
        return "rust"
    if any(k in t for k in ("react", "next.js", "nextjs", "typescript", "node", "javascript", "vue", "angular", "frontend")):
        return "typescript"
    if "golang" in t or "go " in t or t.startswith("go:"):
        return "go"
    if any(k in t for k in ("sql", "postgres", "database", "mysql", "indexing", "sqlite", "query")):
        return "sql"
    if any(k in t for k in ("c++", "cpp", "c programming")):
        return "cpp"
    if any(k in t for k in ("spring", "java ", "jvm", "kotlin")):
        return "java"
    if any(k in t for k in ("docker", "kubernetes", "k8s", "devops", "terraform", "helm", "container")):
        return "yaml"
    return "python"


def _call_gemini(prompt: str) -> Optional[str]:
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        return response.text
    except Exception as e:
        print(f"[Gemini Planner Error] {e}")
        return None


def _call_claude(prompt: str) -> Optional[str]:
    try:
        import httpx
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.CLAUDE_MODEL,
                "max_tokens": 2500,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30.0,
        )
        if resp.status_code == 200:
            return resp.json()["content"][0]["text"]
    except Exception:
        pass
    return None


def _extract_json(raw: str) -> Optional[Dict[str, Any]]:
    if not raw or not raw.strip():
        return None
    clean = re.sub(r"^```json\s*", "", raw.strip(), flags=re.MULTILINE)
    clean = re.sub(r"^```\s*$", "", clean, flags=re.MULTILINE).strip()
    try:
        return json.loads(clean)
    except Exception:
        pass

    # Extract outer {...}
    start = clean.find("{")
    end = clean.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = clean[start : end + 1]
        try:
            return json.loads(snippet)
        except Exception:
            no_comments = re.sub(r"(?<!:)\/\/.*$", "", snippet, flags=re.MULTILINE)
            no_trailing = re.sub(r",\s*([}\]])", r"\1", no_comments)
            try:
                return json.loads(no_trailing)
            except Exception:
                pass
    return None


class CoursePlanner:
    """
    Stage 1: Generates course outline, pedagogy sequence, and exercise specifications
    for ANY arbitrary technology topic and student level.
    """

    def plan_course(
        self,
        topic: str,
        level: str,
        minutes: int,
        stack: Dict[str, str],
    ) -> Dict[str, Any]:
        detected_lang = detect_primary_language(topic, stack)
        short_id = uuid.uuid4().hex[:6]
        lvl = level.lower() if level else "intermediate"

        # Provide a default intelligent stack if empty or generic
        if not stack or stack == {"python": "3.12"} or stack == {"java": "21"}:
            if detected_lang == "rust":
                stack = {"rust": "1.75", "edition": "2021"}
            elif detected_lang == "typescript":
                stack = {"typescript": "5.5", "node": "20"}
            elif detected_lang == "go":
                stack = {"go": "1.22"}
            elif detected_lang == "sql":
                stack = {"postgresql": "16"}
            elif detected_lang == "java":
                stack = {"java": "21", "spring_boot": "3.3"}
            elif detected_lang == "cpp":
                stack = {"c++": "20", "compiler": "clang-18"}
            elif detected_lang == "yaml":
                stack = {"kubernetes": "1.30", "docker": "26.0"}
            else:
                stack = {"python": "3.12", "runtime": "asyncio"}

        prompt = _PLAN_PROMPT.format(
            topic=topic,
            level=lvl,
            minutes=minutes,
            stack=json.dumps(stack),
            short_id=short_id,
        )

        # 1. Primary: Google Gemini 3.8 Flash
        if settings.GEMINI_API_KEY:
            raw = _call_gemini(prompt)
            if raw:
                plan = _extract_json(raw)
                if plan and plan.get("slide_specs") and len(plan.get("slide_specs", [])) >= 5:
                    plan.setdefault("primary_lang", detected_lang)
                    plan.setdefault("stack", stack)
                    return plan

        # 2. Secondary: Anthropic Claude
        if settings.ANTHROPIC_API_KEY:
            raw = _call_claude(prompt)
            if raw:
                plan = _extract_json(raw)
                if plan and plan.get("slide_specs"):
                    plan.setdefault("primary_lang", detected_lang)
                    plan.setdefault("stack", stack)
                    return plan

        # 3. Dynamic Universal Deterministic Fallback
        return self._plan_deterministic(topic, lvl, minutes, stack, detected_lang)

    def _plan_deterministic(
        self,
        topic: str,
        level: str,
        minutes: int,
        stack: Dict[str, str],
        primary_lang: str,
    ) -> Dict[str, Any]:
        lvl = level.lower()
        short_id = uuid.uuid4().hex[:6]

        level_focus = {
            "beginner": "Foundations, mental models, syntax explanations, and zero-assumption walk-throughs",
            "intermediate": "Production patterns, validation boundaries, caching, pagination, and error contracts",
            "advanced": "Internal runtimes, concurrency/thread models, distributed guarantees, and resilience",
        }.get(lvl, "Practical development and production architecture")

        slide_specs = [
            {
                "id": "s_001",
                "type": "title",
                "title": f"{topic}: Foundations & Roadmap",
                "focus": f"Course introduction, prerequisites, and roadmap for {lvl} engineers",
            },
            {
                "id": "s_002",
                "type": "overview",
                "title": f"{topic}: Architecture & Core Mental Model",
                "focus": f"Layered separation, system boundaries, and foundational concepts ({level_focus})",
            },
            {
                "id": "s_003",
                "type": "code",
                "title": f"{topic}: Primary Core Implementation",
                "focus": f"Runnable {primary_lang.upper()} implementation demonstrating fundamental primitives",
            },
            {
                "id": "s_004",
                "type": "code",
                "title": f"{topic}: Defensive Validation & Failure Boundaries",
                "focus": "Sanitizing inputs, declarative constraints, and explicit failure contracts",
            },
            {
                "id": "s_005",
                "type": "concept",
                "title": f"{topic}: Execution Lifecycle & Runtime Flow",
                "focus": "Sequence execution, async pipelines, and state transitions",
            },
            {
                "id": "s_006",
                "type": "code",
                "title": f"{topic}: Domain Operations & Integration",
                "focus": "Separation of concerns, atomic operations, and domain services",
            },
            {
                "id": "s_007",
                "type": "concept",
                "title": f"{topic}: Performance Optimization & Telemetry",
                "focus": "Caching strategies, indexing, metrics, and structured telemetry",
            },
            {
                "id": "s_008",
                "type": "exercise",
                "title": f"Hands-on Lab: {topic} Challenge",
                "focus": f"Students implement domain logic with automated test suite verification ({lvl})",
            },
            {
                "id": "s_009",
                "type": "quiz_review",
                "title": f"Knowledge Check: {topic} Conceptual Review",
                "focus": "3 multi-choice conceptual questions analyzing trade-offs and edge cases",
            },
            {
                "id": "s_010",
                "type": "summary",
                "title": f"Production Readiness Checklist & {topic} Best Practices",
                "focus": "Key design principles, anti-patterns to avoid, and reference architecture",
            },
        ]

        return {
            "deck_id": f"d_{short_id}",
            "topic": topic,
            "level": lvl,
            "minutes": minutes,
            "stack": stack,
            "primary_lang": primary_lang,
            "learning_objectives": [
                f"Master core concepts and architectural invariants of {topic}",
                f"Implement production-grade {primary_lang.capitalize()} code with robust error handling",
                f"Apply best practices and design patterns tailored for {lvl} level",
            ],
            "slide_specs": slide_specs,
            "exercise_spec": {
                "id": "e_001",
                "title": f"{topic} Core Exercise",
                "language": primary_lang,
                "difficulty": lvl,
            },
        }
