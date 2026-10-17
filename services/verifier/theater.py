"""
AI Code Verification & Self-Healing Theater
==========================================
Coordinates real sandbox execution, failure detection, Qwen3 / deterministic
self-repair, line-by-line diffing, and real-time SSE event streaming for the
"Watch AI Fix Its Own Code" interactive demonstration.
"""

import asyncio
import datetime
import difflib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from apps.api.config import settings

# ── Allowlisted Controlled Failure Demonstrations ───────────────────────────
DEMO_EXAMPLES: Dict[str, Dict[str, Any]] = {
    "python_add": {
        "id": "python_add",
        "name": "Arithmetic Operator Bug",
        "description": "Addition function incorrectly computes subtraction (return a - b), failing unit assertions.",
        "lang": "python",
        "version": "3.12",
        "original_code": (
            "def add(a: int, b: int) -> int:\n"
            "    \"\"\"Adds two integers and returns their sum.\"\"\"\n"
            "    return a - b\n"
        ),
        "test_code": (
            "def test_add():\n"
            "    assert add(2, 3) == 5, f\"Expected 5, received {add(2, 3)}\"\n"
            "    assert add(-1, 1) == 0, f\"Expected 0, received {add(-1, 1)}\"\n"
            "    assert add(0, 0) == 0, f\"Expected 0, received {add(0, 0)}\"\n"
            "    assert add(10, -5) == 5, f\"Expected 5, received {add(10, -5)}\"\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    test_add()\n"
            "    print('ALL_TESTS_PASSED')\n"
        ),
        "deterministic_repair": (
            "def add(a: int, b: int) -> int:\n"
            "    \"\"\"Adds two integers and returns their sum.\"\"\"\n"
            "    return a + b\n"
        ),
    },
    "python_boundary": {
        "id": "python_boundary",
        "name": "Off-by-One Loop Boundary Bug",
        "description": "Summation loop uses range(1, n) which omits the upper bound n, failing summation assertions.",
        "lang": "python",
        "version": "3.12",
        "original_code": (
            "def sum_to_n(n: int) -> int:\n"
            "    \"\"\"Calculates the sum of integers from 1 up to and including n.\"\"\"\n"
            "    total = 0\n"
            "    for i in range(1, n):\n"
            "        total += i\n"
            "    return total\n"
        ),
        "test_code": (
            "def test_sum_to_n():\n"
            "    assert sum_to_n(1) == 1, f\"Expected 1, received {sum_to_n(1)}\"\n"
            "    assert sum_to_n(5) == 15, f\"Expected 15, received {sum_to_n(5)}\"\n"
            "    assert sum_to_n(10) == 55, f\"Expected 55, received {sum_to_n(10)}\"\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    test_sum_to_n()\n"
            "    print('ALL_TESTS_PASSED')\n"
        ),
        "deterministic_repair": (
            "def sum_to_n(n: int) -> int:\n"
            "    \"\"\"Calculates the sum of integers from 1 up to and including n.\"\"\"\n"
            "    total = 0\n"
            "    for i in range(1, n + 1):\n"
            "        total += i\n"
            "    return total\n"
        ),
    },
    "python_syntax": {
        "id": "python_syntax",
        "name": "Missing Colon Syntax Error",
        "description": "Function definition header is missing a colon, triggering a Python SyntaxError.",
        "lang": "python",
        "version": "3.12",
        "original_code": (
            "def greet(name: str) -> str\n"
            "    return f\"Hello, {name}!\"\n"
        ),
        "test_code": (
            "def test_greet():\n"
            "    assert greet('Alice') == 'Hello, Alice!'\n"
            "    assert greet('World') == 'Hello, World!'\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    test_greet()\n"
            "    print('ALL_TESTS_PASSED')\n"
        ),
        "deterministic_repair": (
            "def greet(name: str) -> str:\n"
            "    return f\"Hello, {name}!\"\n"
        ),
    },
}

MAX_ACTIVE_RUNS = 25
EXECUTION_TIMEOUT_SEC = 5.0
OUTPUT_MAX_CHARS = 8000


def compute_structured_diff(before: str, after: str) -> List[Dict[str, Any]]:
    """
    Computes a line-by-line structured diff between before and after code.
    Returns list of {'type': 'equal'|'insert'|'delete', 'line': str, 'line_num': int}.
    """
    before_lines = before.splitlines()
    after_lines = after.splitlines()

    matcher = difflib.SequenceMatcher(None, before_lines, after_lines)
    diff_entries: List[Dict[str, Any]] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for idx, line in enumerate(before_lines[i1:i2], start=i1 + 1):
                diff_entries.append({"type": "equal", "line": line, "line_num": idx})
        elif tag == "delete":
            for idx, line in enumerate(before_lines[i1:i2], start=i1 + 1):
                diff_entries.append({"type": "delete", "line": line, "line_num": idx})
        elif tag == "insert":
            for idx, line in enumerate(after_lines[j1:j2], start=j1 + 1):
                diff_entries.append({"type": "insert", "line": line, "line_num": idx})
        elif tag == "replace":
            for idx, line in enumerate(before_lines[i1:i2], start=i1 + 1):
                diff_entries.append({"type": "delete", "line": line, "line_num": idx})
            for idx, line in enumerate(after_lines[j1:j2], start=j1 + 1):
                diff_entries.append({"type": "insert", "line": line, "line_num": idx})

    return diff_entries


def run_code_in_sandbox(code: str, test_code: str, timeout_sec: float = EXECUTION_TIMEOUT_SEC) -> Dict[str, Any]:
    """
    Executes code combined with test harness inside an isolated temporary directory.
    Enforces strict timeouts, output truncation, and returncode checking.
    """
    combined = f"{code}\n\n{test_code}\n"
    start_time = time.perf_counter()

    with tempfile.TemporaryDirectory() as tmpdir:
        target_file = os.path.join(tmpdir, "solution.py")
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(combined)

        env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONUNBUFFERED": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
            "TEMP": tmpdir,
            "TMP": tmpdir,
        }

        try:
            proc = subprocess.run(
                [sys.executable, target_file],
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                timeout=timeout_sec,
            )
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            stdout = proc.stdout[:OUTPUT_MAX_CHARS]
            stderr = proc.stderr[:OUTPUT_MAX_CHARS]
            passed = (proc.returncode == 0) and ("ALL_TESTS_PASSED" in stdout)

            return {
                "status": "passed" if passed else "failed",
                "passed": passed,
                "stdout": stdout,
                "stderr": stderr,
                "returncode": proc.returncode,
                "duration_ms": duration_ms,
            }
        except subprocess.TimeoutExpired:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "failed",
                "passed": False,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout_sec} seconds.",
                "returncode": -1,
                "duration_ms": duration_ms,
            }
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "failed",
                "passed": False,
                "stdout": "",
                "stderr": f"Sandbox execution error: {str(exc)}",
                "returncode": -1,
                "duration_ms": duration_ms,
            }


class SelfHealingTheater:
    """
    Manages active self-healing runs, SSE event queues, and live execution.
    """

    def __init__(self):
        self.runs: Dict[str, Dict[str, Any]] = {}
        self.event_queues: Dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()

    def get_queue(self, run_id: str) -> asyncio.Queue:
        if run_id not in self.event_queues:
            self.event_queues[run_id] = asyncio.Queue()
        return self.event_queues[run_id]

    async def emit_event(
        self,
        run_id: str,
        stage: str,
        progress: int,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
    ):
        q = self.get_queue(run_id)
        now_iso = datetime.datetime.now(datetime.UTC).isoformat()
        event = {
            "run_id": run_id,
            "stage": stage,
            "progress": progress,
            "message": message,
            "timestamp": now_iso,
            "meta": meta or {},
        }
        if run_id in self.runs:
            self.runs[run_id]["stage"] = stage
            self.runs[run_id]["progress"] = progress
            self.runs[run_id]["logs"].append(f"[{stage.upper()}] {message}")
            if meta:
                self.runs[run_id]["meta"].update(meta)
        await q.put(event)

    async def stream_events(self, run_id: str) -> AsyncGenerator[str, None]:
        q = self.get_queue(run_id)
        while True:
            try:
                event = await asyncio.wait_for(q.get(), timeout=20.0)
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("stage") in ("complete", "failed"):
                    break
            except asyncio.TimeoutError:
                # SSE heartbeat comment
                yield ": ping\n\n"

    def create_run(self, example_id: str = "python_add") -> Dict[str, Any]:
        if example_id not in DEMO_EXAMPLES:
            raise ValueError(f"Unknown demo example: '{example_id}'. Allowlisted examples: {list(DEMO_EXAMPLES.keys())}")

        # Evict old runs if capacity reached
        if len(self.runs) >= MAX_ACTIVE_RUNS:
            oldest_key = next(iter(self.runs))
            del self.runs[oldest_key]
            self.event_queues.pop(oldest_key, None)

        run_id = f"sh_{uuid.uuid4().hex[:10]}"
        example = DEMO_EXAMPLES[example_id]

        run_data: Dict[str, Any] = {
            "run_id": run_id,
            "example_id": example_id,
            "example_name": example["name"],
            "description": example["description"],
            "demo_type": "controlled_failure_demo",
            "lang": example["lang"],
            "version": example["version"],
            "original_code": example["original_code"],
            "test_code": example["test_code"],
            "stage": "initializing",
            "progress": 0,
            "initial_result": None,
            "repaired_code": None,
            "repair_provider": None,
            "repair_model": None,
            "repair_attempts": 0,
            "final_result": None,
            "verified": "pending",
            "diff": [],
            "logs": [],
            "meta": {},
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "completed_at": None,
        }
        self.runs[run_id] = run_data
        return run_data

    async def run_theater_pipeline(self, run_id: str) -> Dict[str, Any]:
        """
        Executes the full controlled failure & self-healing sequence asynchronously.
        """
        run = self.runs.get(run_id)
        if not run:
            raise ValueError(f"Run {run_id} not found")

        example = DEMO_EXAMPLES[run["example_id"]]
        original_code = example["original_code"]
        test_code = example["test_code"]
        deterministic_repair = example["deterministic_repair"]

        try:
            # Stage 1: Initializing
            await self.emit_event(
                run_id, "initializing", 10,
                f"Initializing {example['name']} sandbox environment...",
                {"example_name": example["name"], "lang": example["lang"]}
            )
            await asyncio.sleep(0.4)

            # Stage 2: Executing original faulty code in sandbox
            await self.emit_event(
                run_id, "executing_original", 25,
                "Executing original code against test assertions in sandbox...",
                {"code": original_code}
            )
            await asyncio.sleep(0.3)

            # Run in sandbox
            initial_res = await asyncio.to_thread(run_code_in_sandbox, original_code, test_code)
            run["initial_result"] = initial_res

            # Stage 3: Verification Failed
            first_err = initial_res.get("stderr", "").strip() or "Test assertions failed"
            err_snippet = first_err.splitlines()[-1] if first_err.splitlines() else first_err
            await self.emit_event(
                run_id, "verification_failed", 45,
                f"Real sandbox failure detected: {err_snippet}",
                {
                    "returncode": initial_res.get("returncode"),
                    "stderr": initial_res.get("stderr"),
                    "stdout": initial_res.get("stdout"),
                    "duration_ms": initial_res.get("duration_ms"),
                }
            )
            await asyncio.sleep(0.5)

            # Stage 4: Self-Healing / Proposing Repair
            await self.emit_event(
                run_id, "repairing", 65,
                "Invoking Self-Healing agent with failure trace...",
            )

            repaired_code, provider, model = await self._propose_repair(
                example=example,
                broken_code=original_code,
                error_trace=initial_res.get("stderr", ""),
            )
            run["repaired_code"] = repaired_code
            run["repair_provider"] = provider
            run["repair_model"] = model
            run["repair_attempts"] = 1
            run["diff"] = compute_structured_diff(original_code, repaired_code)

            await self.emit_event(
                run_id, "repairing", 75,
                f"Candidate fix proposed via {provider} ({model}). Generating diff...",
                {
                    "repaired_code": repaired_code,
                    "repair_provider": provider,
                    "repair_model": model,
                    "diff": run["diff"],
                }
            )
            await asyncio.sleep(0.5)

            # Stage 5: Re-executing repaired code in sandbox
            await self.emit_event(
                run_id, "executing_repair", 85,
                "Re-running test assertions against repaired candidate in sandbox...",
                {"repaired_code": repaired_code}
            )

            final_res = await asyncio.to_thread(run_code_in_sandbox, repaired_code, test_code)
            run["final_result"] = final_res

            if final_res.get("passed"):
                run["verified"] = "passed"
                await self.emit_event(
                    run_id, "verification_passed", 95,
                    "VERIFIED — ALL TESTS PASSED in isolated sandbox!",
                    {
                        "verified": "passed",
                        "final_result": final_res,
                        "duration_ms": final_res.get("duration_ms"),
                    }
                )
            else:
                run["verified"] = "failed"
                await self.emit_event(
                    run_id, "verification_failed_final", 95,
                    f"Re-verification failed: {final_res.get('stderr', '')[:100]}",
                    {
                        "verified": "failed",
                        "final_result": final_res,
                    }
                )

            # Terminal stage
            await asyncio.sleep(0.3)
            run["completed_at"] = datetime.datetime.now(datetime.UTC).isoformat()
            await self.emit_event(
                run_id, "complete", 100,
                "Theater execution finished. Ready for inspection or slide export.",
                {
                    "verified": run["verified"],
                    "repair_provider": provider,
                    "repair_model": model,
                }
            )
            return run

        except Exception as exc:
            run["stage"] = "failed"
            run["verified"] = "failed"
            err_msg = f"Self-healing theater pipeline aborted: {str(exc)}"
            await self.emit_event(run_id, "failed", 100, err_msg)
            return run

    async def _propose_repair(
        self,
        example: Dict[str, Any],
        broken_code: str,
        error_trace: str,
    ) -> tuple[str, str, str]:
        """
        Attempts Qwen3 via Ollama first. If unavailable, times out, or fails,
        falls back to deterministic repair with honest provider labeling.
        """
        base_url = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
        model = getattr(settings, "OLLAMA_MODEL", "qwen3:8b")

        # Check if Ollama is accessible
        try:
            client = httpx.AsyncClient(timeout=10.0)
            health = await client.get(f"{base_url}/api/tags")
            if health.status_code == 200:
                prompt = (
                    f"Fix this {example['lang']} code snippet.\n\n"
                    f"Broken Code:\n```python\n{broken_code}```\n\n"
                    f"Error Trace from Sandbox Execution:\n{error_trace}\n\n"
                    f"Rules:\n"
                    f"1. Output ONLY the raw corrected Python code inside a single ```python code block.\n"
                    f"2. No conversational text, no explanations.\n"
                )
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a code verification agent. Return ONLY corrected code inside markdown code fences."},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                }
                resp = await client.post(f"{base_url}/api/chat", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data.get("message", {}).get("content", "")
                    # Strip <think> tags
                    content = re.sub(r"<think>[\s\S]*?</think>", "", content).strip()
                    # Extract from ``` blocks
                    match = re.search(r"```(?:python)?\s*\n([\s\S]*?)```", content)
                    if match:
                        candidate = match.group(1).strip() + "\n"
                        # Quick sanity check: must define the function
                        if "def " in candidate:
                            return candidate, "qwen-ollama", model
            await client.aclose()
        except Exception:
            pass  # Fall back to deterministic repair cleanly

        # Deterministic repair fallback (honest attribution)
        return example["deterministic_repair"], "deterministic-fallback", "deterministic-rule"


# Global singleton theater instance
theater_service = SelfHealingTheater()
