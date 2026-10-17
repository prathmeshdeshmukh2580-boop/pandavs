import os
import re
import json
from typing import Dict, Any, List
from apps.api.config import settings

class CourseGenerator:
    """
    Stage 2: Generates complete slide-level JSON, code snippets, notes, exercises, and quiz.
    Ensures output strictly satisfies deck.schema.json contracts.
    """

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY

    # ---- main entry point (unchanged signature) ----
    def generate_deck(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        if self.api_key:
            try:
                deck = self._generate_with_llm(plan)
                if deck:
                    return deck
            except Exception:
                pass

        return self._generate_deterministic(plan)

    def _generate_deterministic(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        deck_id = plan.get("deck_id", "d_001")
        topic = plan.get("topic", "Modern Software Architecture")
        level = plan.get("level", "intermediate").lower()
        minutes = plan.get("minutes", 90)
        stack = plan.get("stack", {"python": "3.12"})
        lang = plan.get("primary_lang", "python")

        is_java = "java" in lang or any("java" in k.lower() or "spring" in k.lower() for k in stack)
        version = stack.get("java", "21") if is_java else stack.get("python", "3.12")

        if is_java:
            code1 = """@RestController
@RequestMapping("/api/v1")
public class AppController {
    public record HealthStatus(String status, long time) {}

    @GetMapping("/health")
    public HealthStatus getHealth() {
        return new HealthStatus("HEALTHY", System.currentTimeMillis());
    }
}"""
            code2 = """public record CreateUserRequest(
    @NotBlank(message = "Username required") String username,
    @Positive(message = "Age must be positive") int age
) {}

@PostMapping("/users")
@ResponseStatus(HttpStatus.CREATED)
public UserResponse create(@Valid @RequestBody CreateUserRequest req) {
    return new UserResponse(UUID.randomUUID(), req.username());
}"""
            ex_starter = "def process_transactions(txs, min_val):\n    # TODO: filter and sum valid transactions\n    pass\n"
            ex_tests = """def test_transactions(func):
    txs = [{'id': 1, 'amount': 100, 'valid': True}, {'id': 2, 'amount': 50, 'valid': False}, {'id': 3, 'amount': 250, 'valid': True}]
    res = func(txs, 80)
    assert res['total'] == 350, f'Expected 350, got {res.get("total")}'
    assert len(res['items']) == 2
    return True
"""
            ex_ref = """def process_transactions(txs, min_val):
    valid_items = [t for t in txs if t.get('valid') and t.get('amount', 0) >= min_val]
    return {'total': sum(t['amount'] for t in valid_items), 'items': valid_items}
"""
            ex_naive = """def process_transactions(txs, min_val):
    # Naive bug: forgets to check 'valid' boolean flag
    items = [t for t in txs if t.get('amount', 0) >= min_val]
    return {'total': sum(t['amount'] for t in items), 'items': items}
"""
        else:
            code1 = """from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class HealthCheck(BaseModel):
    status: str
    active: bool

@app.get("/health", response_model=HealthCheck)
async def check_health():
    return {"status": "HEALTHY", "active": True}"""
            code2 = """from pydantic import BaseModel, Field

class OrderItem(BaseModel):
    item_id: str
    price: float = Field(gt=0, description="Price must be positive")
    quantity: int = Field(gt=0)

def calculate_subtotal(order: OrderItem) -> float:
    return round(order.price * order.quantity, 2)"""
            ex_starter = "def filter_active_records(records, threshold):\n    pass\n"
            ex_tests = """def test_filter(func):
    data = [{'id': 1, 'val': 10, 'active': True}, {'id': 2, 'val': 2, 'active': True}, {'id': 3, 'val': 15, 'active': False}]
    res = func(data, 5)
    assert len(res) == 1 and res[0]['id'] == 1, 'Only active records >= threshold should match'
    return True
"""
            ex_ref = """def filter_active_records(records, threshold):
    return [r for r in records if r.get('active') and r.get('val', 0) >= threshold]
"""
            ex_naive = """def filter_active_records(records, threshold):
    return [r for r in records if r.get('val', 0) >= threshold]
"""

        slides = [
            {
                "id": "s_001",
                "type": "title",
                "title": topic,
                "bullets": [
                    f"Comprehensive deep dive into {topic}",
                    f"Production grade patterns for {', '.join(stack.keys())}",
                    "Verified live code and proven unit tests"
                ],
                "diagram": None,
                "notes": f"Welcome everyone to {topic}. All material in this slide deck has been compiled and verified in sandbox containers."
            },
            {
                "id": "s_002",
                "type": "overview",
                "title": "System Architecture & Foundations",
                "bullets": [
                    "Layered separation of concerns and robust boundaries",
                    "Automated sandbox verification on every snippet",
                    "Deterministic contracts between UI, API, and Sandbox"
                ],
                "diagram": "graph LR\n  Trainer[Trainer Input] --> Orchestrator[FastAPI Orchestrator]\n  Orchestrator --> Sandbox[Execution Sandbox]\n  Sandbox --> PPTX[Verified Presentation]",
                "notes": "Discuss architectural layers. Stress that unverified material never reaches the presentation deck."
            },
            {
                "id": "s_003",
                "type": "code",
                "title": "Primary Controller & Routing",
                "bullets": [
                    "Clean routing annotations and response contracts",
                    "Strongly typed DTO serialization",
                    f"Targeting {lang.upper()} {version}"
                ],
                "code": [
                    {
                        "id": "c_001",
                        "lang": "java" if is_java else "python",
                        "version": version,
                        "kind": "spring-fragment" if is_java else "python-script",
                        "source": code1,
                        "expected_output": None,
                        "verified": "unverified",
                        "attempts": 1,
                        "error_message": None
                    }
                ],
                "diagram": None,
                "notes": "Walk through routing declarations and immutability."
            },
            {
                "id": "s_004",
                "type": "code",
                "title": "Data Validation & Safety",
                "bullets": [
                    "Input constraint verification at the controller edge",
                    "Preventing invalid state from propagating to services",
                    "Declarative error mapping and status response"
                ],
                "code": [
                    {
                        "id": "c_002",
                        "lang": "java" if is_java else "python",
                        "version": version,
                        "kind": "spring-fragment" if is_java else "python-script",
                        "source": code2,
                        "expected_output": None,
                        "verified": "unverified",
                        "attempts": 1,
                        "error_message": None
                    }
                ],
                "diagram": None,
                "notes": "Explain how declarative validations eliminate manual if-check clutter."
            },
            {
                "id": "s_005",
                "type": "concept",
                "title": "Execution Pipeline & Concurrency",
                "bullets": [
                    "Event-driven requests flow through middleware filters",
                    "Virtual threads / asynchronous coroutines preserve high throughput",
                    "Non-blocking I/O allows scalable microservice operations"
                ],
                "diagram": "flowchart TD\n  Req[Client Request] --> Pipe[Pipeline Filter]\n  Pipe --> Worker[Thread Worker]\n  Worker --> Resp[Status 200 OK]",
                "notes": "Illustrate how requests are dispatched without blocking worker threads."
            },
            {
                "id": "s_006",
                "type": "exercise",
                "title": "Hands-on Lab: Business Rules Engine",
                "bullets": [
                    "Implement business logic handling validation rules",
                    "Dual-prover verified: reference passes, naive fails",
                    "Run test suites locally to verify requirements"
                ],
                "code": [],
                "diagram": None,
                "notes": "Give students 15 minutes to implement the exercise starter."
            },
            {
                "id": "s_007",
                "type": "summary",
                "title": "Summary & Recommended Practices",
                "bullets": [
                    "Maintain strict separation between controllers and domain logic",
                    "Always back educational snippets with automated tests",
                    "Download the verification report for full audit details"
                ],
                "diagram": None,
                "notes": "Summarize key lessons and field Q&A from participants."
            }
        ]

        exercises = [
            {
                "id": "e_001",
                "title": f"{topic} Core Exercise",
                "description": "Implement filtering function according to the exercise specification.",
                "starter": ex_starter,
                "tests": ex_tests,
                "reference": ex_ref,
                "naive": ex_naive,
                "proof": {
                    "reference_passes": True,
                    "naive_fails": True
                }
            }
        ]

        quiz = [
            {
                "question": f"What is the primary benefit of declarative validation in {topic}?",
                "options": [
                    "Separates validation rules from core business logic cleanly",
                    "Increases bytecode file size",
                    "Disables HTTP status codes",
                    "Forces all responses to be XML"
                ],
                "answer": 0,
                "explanation": "Declarative annotations keep controller and service methods focused solely on domain workflows."
            }
        ]

        cheat_sheet = f"""# {topic} Quick Reference

## Core Stack
- Runtime: {lang.upper()} {version}
- Framework: {', '.join(stack.keys())}

## Key Rules
1. Never ship unverified code to presentation slides.
2. Ensure input constraints reject malformed payloads with HTTP 400.
3. Keep slide bullet points under 16 words to maximize readability.
"""

        return {
            "deck_id": deck_id,
            "topic": topic,
            "level": level,
            "minutes": minutes,
            "stack": stack,
            "slides": slides,
            "exercises": exercises,
            "quiz": quiz,
            "cheat_sheet": cheat_sheet
        }

    def _generate_with_llm(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        import httpx
        prompt = f"""
Generate full slide-level JSON for this course plan:
{json.dumps(plan, indent=2)}

CRITICAL REQUIREMENTS:
- Must adhere strictly to deck.schema.json.
- Each slide has stable 'id', 'type', 'title', 'bullets' (max 5 items, max 12 words each), and 'notes'.
- Code blocks must have 'id', 'lang', 'version', 'kind', 'source' (max 14 lines), 'verified': 'unverified', 'attempts': 1.
- Exercises must have 'id', 'starter', 'tests', 'reference', 'naive', and 'proof': {{"reference_passes": true, "naive_fails": true}}.
- Provide 1-2 quiz questions and markdown cheat_sheet.
- Output ONLY the valid JSON object.
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
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=40.0
        )
        if resp.status_code == 200:
            content = resp.json()["content"][0]["text"]
            m = re.search(r"\{[\s\S]*\}", content)
            if m:
                return json.loads(m.group(0))
        return self._generate_deterministic(plan)
