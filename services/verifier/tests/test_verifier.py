import pytest
from services.verifier.cache import VerificationCache
from services.verifier.runner import SandboxRunner
from services.verifier.prover import ExerciseProver
from services.verifier.self_heal import SelfHealer

def test_verification_cache(tmp_path):
    db_file = str(tmp_path / "test_cache.db")
    cache = VerificationCache(db_path=db_file)
    
    # Check cache miss
    miss = cache.get("python", "3.12", "print(123)")
    assert miss is None
    
    # Store
    cache.set("python", "3.12", "print(123)", "passed", "123\n", "", 12.5)
    
    # Check cache hit
    hit = cache.get("python", "3.12", "print(123)")
    assert hit is not None
    assert hit["status"] == "passed"
    assert hit["stdout"] == "123\n"
    assert hit["cached"] is True

def test_python_snippet_runner():
    runner = SandboxRunner(timeout_sec=5)
    res = runner.verify_snippet(
        lang="python",
        version="3.12",
        code="print('verified_output')",
        expected_output="verified_output"
    )
    assert res["status"] == "passed"
    assert "verified_output" in res["stdout"]

def test_exercise_prover_tests_must_bite():
    prover = ExerciseProver(timeout_sec=5)
    
    starter = "def add(a, b): pass"
    tests = """
def test_add(func):
    assert func(2, 3) == 5
    assert func(-1, 1) == 0
"""
    reference = "def add(a, b):\n    return a + b"
    naive = "def add(a, b):\n    return a - b"  # Buggy implementation
    
    proof = prover.prove_exercise(starter, tests, reference, naive)
    assert proof["reference_passes"] is True
    assert proof["naive_fails"] is True
    assert proof["proven"] is True
    assert proof["status"] == "proven"

def test_self_heal_loop():
    runner = SandboxRunner(timeout_sec=5)
    healer = SelfHealer(runner=runner, max_attempts=3)
    
    # Snippet with Spring Boot 2 javax namespace which is invalid in Spring Boot 3
    broken_code = """
@RestController
public class OrderController {
    public void validate(@javax.validation.Valid Object req) {
    }
}
"""
    # Trigger self heal
    healed = healer.heal_snippet(
        lang="java",
        version="21",
        code=broken_code,
        kind="spring-fragment",
        initial_error="Spring Boot 3 incompatibility: javax.* namespace detected. Must use jakarta.*"
    )
    assert healed["verified"] == "passed"
    assert healed["healed"] is True
    assert "jakarta.validation.Valid" in healed["code"]
