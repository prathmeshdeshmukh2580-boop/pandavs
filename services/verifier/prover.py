import tempfile
import subprocess
import sys
import os
from typing import Dict, Any

class ExerciseProver:
    """
    Validates exercise test suites using the dual-prover principle:
    1. Reference solution MUST pass the test suite (reference_passes == True)
    2. Naive/buggy solution MUST fail the test suite (naive_fails == True)
    Ensures that exercises do not ship with ineffective, broken, or trivial tests ("Tests must bite").
    """
    def __init__(self, timeout_sec: int = 10):
        self.timeout_sec = timeout_sec

    def prove_exercise(self, starter: str, tests: str, reference: str, naive: str) -> Dict[str, Any]:
        ref_passes, ref_err = self._run_solution_with_tests(reference, tests)
        naive_passes, naive_err = self._run_solution_with_tests(naive, tests)

        # Naive must fail, so naive_fails is True if naive_passes is False
        naive_fails = not naive_passes
        proven = (ref_passes is True) and (naive_fails is True)

        return {
            "reference_passes": ref_passes,
            "naive_fails": naive_fails,
            "proven": proven,
            "reference_error": ref_err if not ref_passes else None,
            "naive_caught_by_test": naive_err if naive_fails else None,
            "status": "proven" if proven else "unproven"
        }

    def _run_solution_with_tests(self, solution_code: str, test_code: str) -> tuple[bool, str]:
        """
        Combines solution and test harness into a temporary python execution.
        Returns (passed, error_output).
        """
        combined = f"""
import sys

# Student / Reference Implementation
{solution_code}

# Test Harness
{test_code}

if __name__ == '__main__':
    # Find functions starting with test_
    tested = False
    for name, obj in list(globals().items()):
        if name.startswith('test_') and callable(obj):
            tested = True
            # Check if function takes an argument (like func)
            import inspect
            sig = inspect.signature(obj)
            if len(sig.parameters) == 1:
                # Find the primary solution function
                sol_func = None
                for fn_name, fn in list(globals().items()):
                    if callable(fn) and not fn_name.startswith('test_') and fn_name not in ('print', 'round', 'dict', 'list'):
                        sol_func = fn
                        break
                obj(sol_func)
            else:
                obj()
    if not tested:
        # Default run
        pass
    print("ALL_TESTS_PASSED")
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_run.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(combined)

            try:
                proc = subprocess.run(
                    [sys.executable, file_path],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout_sec
                )
                if proc.returncode == 0 and "ALL_TESTS_PASSED" in proc.stdout:
                    return True, ""
                else:
                    err = proc.stderr.strip() or proc.stdout.strip()
                    return False, err
            except subprocess.TimeoutExpired:
                return False, f"Timeout after {self.timeout_sec}s"
            except Exception as e:
                return False, str(e)
