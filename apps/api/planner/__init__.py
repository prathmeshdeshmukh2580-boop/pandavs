import os
import json
import uuid
from typing import Dict, Any, List
from apps.api.config import settings

class CoursePlanner:
    """
    Stage 1: Generates course outline, pedagogy sequence, and exercise specifications.
    """
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY

    def plan_course(self, topic: str, level: str, minutes: int, stack: Dict[str, str]) -> Dict[str, Any]:
        """
        Plans course outline with slide list, learning objectives, and exercise concepts.
        """
        if self.api_key:
            try:
                plan = self._plan_with_llm(topic, level, minutes, stack)
                if plan:
                    return plan
            except Exception:
                pass

        return self._plan_deterministic(topic, level, minutes, stack)

    def _plan_deterministic(self, topic: str, level: str, minutes: int, stack: Dict[str, str]) -> Dict[str, Any]:
        primary_lang = "java" if any("java" in k.lower() or "spring" in k.lower() for k in stack) else "python"
        
        slide_specs = [
            {"id": "s_001", "type": "title", "title": f"{topic}", "focus": "Course introduction and objectives"},
            {"id": "s_002", "type": "overview", "title": "Architecture & Core Concepts", "focus": "System overview & components"},
            {"id": "s_003", "type": "code", "title": "Building the Core Handler", "focus": "First runnable code implementation"},
            {"id": "s_004", "type": "code", "title": "Validation & Error Boundaries", "focus": "Robust input processing & status codes"},
            {"id": "s_005", "type": "concept", "title": "Data Flow & Execution Model", "focus": "Execution sequence diagram"},
            {"id": "s_006", "type": "exercise", "title": "Hands-on Exercise: Core Logic", "focus": "Student implementation challenge"},
            {"id": "s_007", "type": "summary", "title": "Summary & Next Steps", "focus": "Review & best practices"}
        ]

        return {
            "deck_id": f"d_{uuid.uuid4().hex[:6]}",
            "topic": topic,
            "level": level,
            "minutes": minutes,
            "stack": stack,
            "primary_lang": primary_lang,
            "slide_specs": slide_specs,
            "exercise_spec": {
                "id": "e_001",
                "title": f"{topic} Challenge",
                "language": primary_lang
            }
        }

    def _plan_with_llm(self, topic: str, level: str, minutes: int, stack: Dict[str, str]) -> Dict[str, Any]:
        import httpx
        prompt = f"""
Plan a technical course presentation for:
Topic: {topic}
Audience Level: {level}
Duration: {minutes} minutes
Tech Stack: {json.dumps(stack)}

Return strict JSON with this shape:
{{
  "deck_id": "d_xxx",
  "topic": "{topic}",
  "level": "{level}",
  "minutes": {minutes},
  "stack": {json.dumps(stack)},
  "primary_lang": "java or python",
  "slide_specs": [
    {{"id": "s_001", "type": "title", "title": "...", "focus": "..."}},
    {{"id": "s_002", "type": "overview", "title": "...", "focus": "..."}},
    {{"id": "s_003", "type": "code", "title": "...", "focus": "..."}},
    {{"id": "s_004", "type": "code", "title": "...", "focus": "..."}},
    {{"id": "s_005", "type": "concept", "title": "...", "focus": "..."}},
    {{"id": "s_006", "type": "exercise", "title": "...", "focus": "..."}},
    {{"id": "s_007", "type": "summary", "title": "...", "focus": "..."}}
  ],
  "exercise_spec": {{"id": "e_001", "title": "...", "language": "..."}}
}}
"""
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": settings.CLAUDE_MODEL,
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=25.0
        )
        if resp.status_code == 200:
            content = resp.json()["content"][0]["text"]
            import re
            m = re.search(r"\{[\s\S]*\}", content)
            if m:
                return json.loads(m.group(0))
        return self._plan_deterministic(topic, level, minutes, stack)
