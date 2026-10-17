# Verified Course Material Studio - Gemini Generator Fix Summary

This document details all changes, bug fixes, schema alignments, and verification steps implemented for the Gemini lesson generator and the `POST /decks` API endpoint.

---

## 1. Overview of Problems Identified & Solved

| Problem Area | Root Cause | Solution |
| :--- | :--- | :--- |
| **Gemini 504 Timeouts & Slow JSON** | Gemini calls lacked request timeout boundaries and explicit JSON formatting response mime types, hanging the server when Gemini took too long or produced truncated answers. | Configured `genai.GenerationConfig` with `response_mime_type="application/json"`, `temperature=0.7`, and added an explicit 120s timeout in `request_options={"timeout": 120}`. |
| **Model & SDK Configuration** | Gemini API keys were missing from `apps/api/config.py`, `.env.example`, and requirements. Legacy code was hard-coded to Anthropic Claude. | Added `GEMINI_API_KEY` and `GEMINI_MODEL="gemini-2.0-flash"` to `config.py` and `.env.example`. Added `google-generativeai>=0.8.0` to `apps/api/requirements.txt`. |
| **Hardcoded Spring Boot / Java** | The generator only returned Java 21 / Spring Boot 3 examples regardless of the requested topic or stack. | Implemented dynamic language and stack inference (`_infer_lang_and_version`). Automatically selects Python 3.12 (FastAPI / Pydantic snippets) or Java 21 (Spring Boot snippets) based on the input topic and stack dictionary. |
| **Pydantic Model Misalignments** | `apps/api/models.py` had invalid types: `Slide.diagram` was `Optional[str]` (violating schema object def), `Exercise` missed `lang`, `version`, `prompt`, `QuizQuestion` used `answer` instead of `answer_index`, and `CodeBlock` contained an invalid `error_message` attribute. | Aligned all Pydantic models directly with `schema/deck.schema.json`. Added `Diagram`, `QuizItem`, and fixed `Exercise` and `Slide` models. |
| **Schema Strictness (`additionalProperties: false`)** | Both the deterministic generator and orchestrator were adding `error_message` and `description` fields to code blocks and exercises, triggering JSON schema validation failures. | Filtered and normalized all output via `_patch_deck` in the generator and ensured `orchestrator.py` removes transient verification properties before serializing to SQLite / disk. |
| **Diagram Object vs String** | The schema requires Mermaid diagrams as `{ "id": "g_...", "kind": "mermaid", "source": "..." }`, but LLM or raw templates frequently returned plain Mermaid strings. | Normalized diagrams in `_patch_deck`: plain string diagrams are automatically wrapped in a valid `diagram` object with proper ID and `kind: "mermaid"`. |
| **Docker-Dependent Imports in API** | In lightweight / local test mode, missing external services or renderers could prevent the FastAPI server from booting. | Wrapped heavy dependencies gracefully with fallback handling in `main.py`, allowing the API to run in lightweight synchronous mode when isolated from Docker sandboxes. |

---

## 2. File-by-File Summary of Changes

### 1. `apps/api/config.py`
- Added `GEMINI_API_KEY` (reads `GEMINI_API_KEY` or `GOOGLE_API_KEY` from `.env`).
- Added `GEMINI_MODEL` (defaults to `gemini-2.0-flash`).

### 2. `apps/api/models.py`
- Updated `CodeBlock` to strictly follow schema properties: `id`, `lang`, `version`, `kind`, `source`, `expected_output`, `verified`, `attempts`.
- Added `Diagram` model (`id`, `kind="mermaid"`, `source`).
- Updated `Slide` to support `diagram: Optional[Diagram]`.
- Updated `Exercise` to include required fields: `id`, `title`, `lang`, `version`, `prompt`, `starter`, `tests`, `reference`, `naive`, `proof`.
- Updated `QuizItem` to use `answer_index: int` (0–5) and include `id`.

### 3. `apps/api/generator/__init__.py`
- Added `CourseGenerator` with dual-engine support: **Google Gemini API** (primary), **Anthropic Claude** (secondary), and a **deterministic fallback** (offline / local testing).
- Created `_build_gemini_prompt` to dynamically construct system prompts based on user topic, duration, and runtime language.
- Added robust JSON parsing (`_parse_json_response`) handling direct JSON, markdown code fence stripping, and substring boundary extraction.
- Added `_patch_deck` post-processor to automatically repair common LLM schema violations (e.g. invalid slide types, string diagrams, extra keys).
- Implemented language-aware fallback snippets for both **Python 3.12** and **Java 21**.

### 4. `apps/api/orchestrator.py`
- Cleaned up transient execution metadata (`error_message`) from code blocks before committing decks to database storage so they strictly comply with `deck.schema.json`.

### 5. `apps/api/main.py`
- Updated `POST /decks` to handle both full background worker pipelines (with SSE) and synchronous lightweight generation.
- Exposed `gemini_available` and `orchestrator_available` flags in `GET /health`.
- Ensured consistent `"status": "healthy"` return across all health check endpoints.

### 6. `.env.example` & `apps/api/requirements.txt`
- Documented `GEMINI_API_KEY` and `GEMINI_MODEL`.
- Added `google-generativeai>=0.8.0`, `jsonschema>=4.23.0`, `python-pptx>=1.0.0`, and `pillow>=10.0.0`.

### 7. `apps/api/tests/test_decks.py`
- Created comprehensive test suite (29 tests) verifying:
  - Health check endpoint flags.
  - Deterministic generation for both Python and Java.
  - JSON schema conformance via `jsonschema.Draft202012Validator`.
  - Proper formatting of diagrams, exercises, code blocks, and quiz items.
  - `POST /decks` synchronous creation and `GET /decks/{deck_id}` retrieval.

---

## 3. Test Results

All **44 test cases** pass with zero failures:
```text
======================= 44 passed, 34 warnings in 5.22s =======================
```
- `apps/api/tests/test_api.py` (9 passed)
- `apps/api/tests/test_decks.py` (29 passed)
- `apps/api/tests/test_health.py` (1 passed)
- `apps/api/tests/test_schema.py` (5 passed)

---

## 4. How to Run & Verify Locally

1. **Activate virtual environment**:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

2. **Configure `.env`**:
   Copy `.env.example` to `.env` and supply your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.0-flash
   ```

3. **Run the API server**:
   ```powershell
   python apps/api/main.py
   ```

4. **Test Deck Generation via `POST /decks`**:
   ```powershell
   curl -X POST http://localhost:8000/decks `
     -H "Content-Type: application/json" `
     -d '{"topic": "Python FastAPI Async APIs", "level": "beginner", "minutes": 45}'
   ```

5. **Run test suite**:
   ```powershell
   .venv\Scripts\pytest.exe apps/api/tests/ -v -c pytest.ini
   ```

---

## 5. Next Git Steps

The changes have been committed and pushed to the remote branch:
- **Branch**: `fix/gemini-deck-generator`
- **GitHub Pull Request Link**:
  [https://github.com/prathmeshdeshmukh2580-boop/pandavs/pull/new/fix/gemini-deck-generator](https://github.com/prathmeshdeshmukh2580-boop/pandavs/pull/new/fix/gemini-deck-generator)

To merge into `main`:
```bash
git checkout main
git pull origin main
git merge fix/gemini-deck-generator
git push origin main
```
