"""
Unit & Integration Tests for AI Code Verification & Self-Healing Theater
========================================================================
Validates real sandbox execution, failure detection, Qwen3 / deterministic
repair paths, SSE streaming, diffing, schema compliance, and deck integration.
"""

import json
import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from services.verifier.theater import (
    DEMO_EXAMPLES,
    compute_structured_diff,
    run_code_in_sandbox,
    theater_service,
)

client = TestClient(app)


class TestTheaterSandboxExecution:
    """Tests the real sandbox execution engine."""

    def test_original_faulty_code_genuinely_fails(self):
        example = DEMO_EXAMPLES["python_add"]
        res = run_code_in_sandbox(example["original_code"], example["test_code"])
        assert res["status"] == "failed"
        assert res["passed"] is False
        assert res["returncode"] != 0
        assert "AssertionError" in res["stderr"] or "Expected 5, received -1" in res["stderr"]

    def test_repaired_code_genuinely_passes(self):
        example = DEMO_EXAMPLES["python_add"]
        res = run_code_in_sandbox(example["deterministic_repair"], example["test_code"])
        assert res["status"] == "passed"
        assert res["passed"] is True
        assert res["returncode"] == 0
        assert "ALL_TESTS_PASSED" in res["stdout"]

    def test_infinite_loop_times_out_safely(self):
        hang_code = "while True:\n    pass\n"
        test_code = "assert True\nprint('ALL_TESTS_PASSED')"
        res = run_code_in_sandbox(hang_code, test_code, timeout_sec=0.5)
        assert res["status"] == "failed"
        assert res["passed"] is False
        assert "timed out" in res["stderr"].lower()

    def test_structured_diff_computation(self):
        before = "def add(a, b):\n    return a - b"
        after = "def add(a, b):\n    return a + b"
        diff = compute_structured_diff(before, after)
        assert len(diff) > 0
        types = [d["type"] for d in diff]
        assert "delete" in types
        assert "insert" in types
        # Check that return a - b was deleted and return a + b was inserted
        deleted_lines = [d["line"] for d in diff if d["type"] == "delete"]
        inserted_lines = [d["line"] for d in diff if d["type"] == "insert"]
        assert any("return a - b" in l for l in deleted_lines)
        assert any("return a + b" in l for l in inserted_lines)


class TestSelfHealingAPIEndpoints:
    """Tests the FastAPI routes for self-healing demonstration."""

    def test_list_examples_returns_allowlist(self):
        resp = client.get("/api/self-heal/examples")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 3
        ids = [d["id"] for d in data]
        assert "python_add" in ids
        assert "python_boundary" in ids
        assert "python_syntax" in ids

    def test_start_demo_invalid_example_rejected(self):
        resp = client.post("/api/self-heal/demo", json={"example_id": "malicious_exploit"})
        assert resp.status_code == 400
        assert "Unknown demo example" in resp.json()["detail"]

    def test_start_demo_success(self):
        resp = client.post("/api/self-heal/demo", json={"example_id": "python_add"})
        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "started"
        assert data["run_id"].startswith("sh_")
        assert data["example_id"] == "python_add"

    def test_get_nonexistent_run_returns_404(self):
        resp = client.get("/api/self-heal/sh_nonexistent999")
        assert resp.status_code == 404

    @pytest.mark.anyio
    async def test_full_theater_pipeline_execution(self):
        """Runs the complete theater pipeline asynchronously and verifies all stages."""
        run = theater_service.create_run("python_add")
        run_id = run["run_id"]

        # Execute the pipeline
        completed_run = await theater_service.run_theater_pipeline(run_id)

        assert completed_run["run_id"] == run_id
        assert completed_run["stage"] == "complete"
        assert completed_run["verified"] == "passed"
        assert completed_run["repair_attempts"] >= 1
        assert completed_run["initial_result"]["passed"] is False
        assert completed_run["final_result"]["passed"] is True
        assert len(completed_run["diff"]) > 0
        assert completed_run["repair_provider"] in ("qwen-ollama", "deterministic-fallback")

        # Verify through the API endpoint
        resp = client.get(f"/api/self-heal/{run_id}")
        assert resp.status_code == 200
        api_data = resp.json()
        assert api_data["verified"] == "passed"
        assert api_data["initial_result"]["status"] == "failed"
        assert api_data["final_result"]["status"] == "passed"

    @pytest.mark.anyio
    async def test_add_verified_example_to_deck(self):
        """Verifies adding a verified snippet to a deck produces a valid slide."""
        run = theater_service.create_run("python_add")
        run_id = run["run_id"]
        await theater_service.run_theater_pipeline(run_id)

        # Post to add-to-deck
        resp = client.post(f"/api/self-heal/{run_id}/add-to-deck", json={"deck_id": "d_001"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "added"
        assert data["deck_id"] == "d_001"
        assert "slide_id" in data

        # Check the deck in store
        deck_resp = client.get("/decks/d_001")
        assert deck_resp.status_code == 200
        deck = deck_resp.json()
        last_slide = deck["slides"][-1]
        assert "Verified" in last_slide["title"]
        assert last_slide["code"][0]["verified"] == "passed"
        assert "def add" in last_slide["code"][0]["source"]

    def test_cannot_add_unverified_run_to_deck(self):
        run = theater_service.create_run("python_add")
        run_id = run["run_id"]
        # Do not run pipeline, verified is still 'pending'
        resp = client.post(f"/api/self-heal/{run_id}/add-to-deck", json={"deck_id": "d_001"})
        assert resp.status_code == 400
        assert "Only successfully verified" in resp.json()["detail"]
