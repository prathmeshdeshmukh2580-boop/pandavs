import os
import re
import json
from typing import Dict, Any, List, Optional
from services.verifier.runner import SandboxRunner

class SelfHealer:
    """
    Self-healing loop that fixes broken snippets and re-runs them through the sandbox runner.
    Terminates after MAX_FIX_ATTEMPTS.
    If fixed, marks status as 'passed'; if still failing, marks as 'unverified'.
    """
    def __init__(self, runner: SandboxRunner, max_attempts: int = 3, anthropic_api_key: Optional[str] = None):
        self.runner = runner
        self.max_attempts = max_attempts
        self.api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")

    def heal_snippet(
        self,
        lang: str,
        version: str,
        code: str,
        kind: str,
        initial_error: str,
        expected_output: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs the self-heal loop up to max_attempts.
        """
        current_code = code
        current_error = initial_error
        attempts_history: List[Dict[str, str]] = [
            {"attempt": 1, "code": code, "error": initial_error}
        ]

        for attempt in range(2, self.max_attempts + 1):
            fixed_code = self._propose_fix(
                lang=lang,
                version=version,
                kind=kind,
                broken_code=current_code,
                error_message=current_error,
                prior_attempts=attempts_history
            )

            # Re-verify through the runner
            res = self.runner.verify_snippet(
                lang=lang,
                version=version,
                code=fixed_code,
                kind=kind,
                expected_output=expected_output
            )

            if res["status"] == "passed":
                return {
                    "code": fixed_code,
                    "verified": "passed",
                    "attempts": attempt,
                    "error_message": None,
                    "history": attempts_history,
                    "healed": True
                }
            else:
                current_code = fixed_code
                current_error = res.get("stderr", "") or "Execution failed"
                attempts_history.append({"attempt": attempt, "code": fixed_code, "error": current_error})

        # Exceeded max attempts: mark unverified!
        return {
            "code": current_code,
            "verified": "unverified",
            "attempts": self.max_attempts,
            "error_message": f"Failed self-heal after {self.max_attempts} attempts. Last error: {current_error}",
            "history": attempts_history,
            "healed": False
        }

    def _propose_fix(
        self,
        lang: str,
        version: str,
        kind: str,
        broken_code: str,
        error_message: str,
        prior_attempts: List[Dict[str, str]]
    ) -> str:
        """
        Generates fixed code snippet. If Claude API key is configured, uses Claude.
        Otherwise uses rules-based healing engine.
        """
        if self.api_key:
            try:
                import httpx
                prompt = f"""
You are a code verification self-healing agent. Fix the following {lang} snippet for version {version}.
Target framework kind: {kind}

Broken Code:
```
{broken_code}
```

Error Message from Sandbox:
{error_message}

Prior Attempts:
{json.dumps(prior_attempts, indent=2)}

Rules:
1. Output ONLY the raw corrected code inside ``` code block.
2. Ensure no markdown explanations outside the block.
3. If Java Spring Boot 3, ensure jakarta.* is used instead of javax.*.
4. Keep the snippet concise (under 14 lines).
"""
                resp = httpx.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
                        "max_tokens": 1024,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=20.0
                )
                if resp.status_code == 200:
                    data = resp.json()
                    text = data["content"][0]["text"]
                    match = re.search(r"```(?:\w+)?\n([\s\S]*?)```", text)
                    if match:
                        return match.group(1).strip()
                    return text.strip()
            except Exception:
                pass  # Fallback to local rule-based healer

        # Local rule-based self-healer engine
        fixed = broken_code

        # Fix 1: javax.* -> jakarta.* migration error
        if "javax." in fixed:
            fixed = fixed.replace("javax.validation", "jakarta.validation")
            fixed = fixed.replace("javax.persistence", "jakarta.persistence")
            fixed = fixed.replace("javax.servlet", "jakarta.servlet")
            fixed = fixed.replace("javax.annotation", "jakarta.annotation")

        # Fix 2: Unmatched brackets / parenthesis
        open_curlies = fixed.count('{')
        close_curlies = fixed.count('}')
        if open_curlies > close_curlies:
            fixed += "\n" + ("}" * (open_curlies - close_curlies))
        elif close_curlies > open_curlies:
            # remove excess trailing curlies
            diff = close_curlies - open_curlies
            for _ in range(diff):
                fixed = fixed.rstrip().rstrip('}')

        # Fix 3: Python syntax error (e.g., missing colon)
        if lang == "python":
            lines = fixed.splitlines()
            new_lines = []
            for line in lines:
                stripped = line.strip()
                if (stripped.startswith("def ") or stripped.startswith("if ") or 
                    stripped.startswith("for ") or stripped.startswith("while ") or 
                    stripped.startswith("class ")) and not stripped.endswith(":"):
                    line = line + ":"
                new_lines.append(line)
            fixed = "\n".join(new_lines)

        # Fix 4: Java missing semicolon
        if lang == "java":
            lines = fixed.splitlines()
            new_lines = []
            for line in lines:
                s = line.strip()
                if s and not s.endswith(";") and not s.endswith("{") and not s.endswith("}") and not s.startswith("@") and not s.startswith("//"):
                    if "return " in s or "System.out" in s or "=" in s:
                        line = line + ";"
                new_lines.append(line)
            fixed = "\n".join(new_lines)

        return fixed
