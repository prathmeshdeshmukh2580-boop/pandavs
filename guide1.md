# PROJECT LOCATION (IMPORTANT)
Create the whole project inside this folder (create it if missing) and save ALL files there:
`C:\Users\PRATHMESH\OneDrive\Desktop\vision`
The repo root `verified-studio/` layout below maps to this `vision` folder itself (do not nest another verified-studio folder inside it).
Environment: Windows. Use PowerShell-compatible commands, forward slashes in Docker volume paths, and tell me if Docker Desktop, Python 3.12, Node 20+, LibreOffice or Mermaid CLI are missing instead of silently skipping them.

# Verified Course Material Studio: Prototype Build Guide (for Antigravity)

## How to use this file
1. Create an empty folder `verified-studio/`, open it in Antigravity.
2. Put this file in the folder root as `GUIDE.md`.
3. Paste the **Kickoff prompt** below into the agent.
4. Then feed it ONE phase at a time (copy the phase text). Do not move on until the phase's **Exit check** passes.

---

## Kickoff prompt (paste first)

```
You are building "Verified Course Material Studio", a working prototype, by following GUIDE.md phase by phase.

Core rule: nothing reaches the user unverified. Pipeline: Planner -> Generator -> Verifier (Docker sandbox) -> Renderer.

Working rules:
- Work on ONE phase at a time. Stop after each phase and show me the exit-check result.
- Keep everything in the monorepo layout from GUIDE.md. Do not rename folders.
- schema/deck.schema.json is the single source of truth. Never change it without telling me.
- Never hardcode secrets. Read config from .env (see .env.example).
- Prefer simple, readable code. Prototype scope: no auth, no cloud deploy, runs locally via docker compose.
- After each phase: run the tests/commands in the exit check, fix failures, then summarize in 5 lines max.
- If something is ambiguous, pick the simplest option, state the assumption in one line, and continue.

Confirm you understand, then wait for Phase 0.
```

---

## Target stack
- UI: Next.js + Tailwind (port 3000)
- API/orchestrator: FastAPI, Python 3.12, live progress via SSE (port 8000)
- LLM: Claude API, structured JSON output (planner, generator, self-heal). Model name from `CLAUDE_MODEL` env var
- Sandbox: Docker, pinned images (Java 21 + Maven + Spring Boot 3; Python 3.12 + pytest)
- Rendering: python-pptx, LibreOffice headless (PDF), Mermaid CLI (diagrams)
- Storage: SQLite + filesystem
- Delivery: docker compose locally

## Repo layout (create exactly this)
```
verified-studio/
  README.md
  docker-compose.yml
  .env.example
  .gitignore
  docs/            api-contract.md, deck-schema.md, demo-script.md
  schema/          deck.schema.json
  apps/
    web/           Next.js UI
    api/           FastAPI: main.py, planner/, generator/, store/
  services/
    verifier/      snippet runner, exercise prover, self-heal
    renderer/      pptx builder, diagrams, fit check, export
  sandbox/
    java21-spring3/   Dockerfile + pre-warmed Maven cache
    python312/        Dockerfile + pytest
  templates/       branded master.pptx
  samples/         pre-generated backup deck + cached results
```

## Environment variables (`.env.example`)
| Variable | Purpose | Default |
|---|---|---|
| ANTHROPIC_API_KEY | Claude access | (empty, user fills) |
| CLAUDE_MODEL | model for generation/fixes | (user sets) |
| SANDBOX_TIMEOUT_SEC | per-container limit | 60 |
| SANDBOX_MEMORY_MB | per-container memory | 512 |
| MAX_FIX_ATTEMPTS | self-heal retries | 3 |
| DATA_DIR | decks, caches, reports | ./data |
| NEXT_PUBLIC_API_URL | UI -> API | http://localhost:8000 |

## API contract (build against this)
| Endpoint | Purpose |
|---|---|
| POST /decks | Start generation from `topic, level, minutes`; returns deck id |
| GET /decks/{id}/events | SSE stream of stage progress |
| GET /decks/{id} | Deck JSON with per-slide verification status |
| POST /verify | Run one snippet in sandbox; returns `status, stdout, stderr, duration` |
| POST /decks/{id}/slides/{sid}/regenerate | Regenerate one slide, re-verify, re-render only it |
| POST /decks/{id}/upgrade | Upgrade to newer framework version; returns diff report |
| GET /decks/{id}/report | Verification report (JSON + PDF) |
| GET /decks/{id}/export?format=pptx\|pdf | Download deck |

## Deck JSON (minimum shape)
```json
{
  "deck_id": "d_001",
  "topic": "Spring Boot 3 REST APIs",
  "level": "beginner",
  "minutes": 90,
  "stack": {"java": "21", "spring_boot": "3.3"},
  "slides": [{
    "id": "s_007", "type": "code", "title": "A first controller",
    "bullets": ["Maps GET /hello", "Returns a String"],
    "code": [{"id": "c_012", "lang": "java", "version": "21", "kind": "spring-fragment",
              "source": "...", "expected_output": null, "verified": "passed", "attempts": 1}],
    "diagram": null, "notes": "Trainer notes"
  }],
  "exercises": [{"id": "e_003", "starter": "...", "tests": "...", "reference": "...", "naive": "...",
                 "proof": {"reference_passes": true, "naive_fails": true}}],
  "quiz": [], "cheat_sheet": ""
}
```
Schema rules: every slide and code block has a stable `id`; code blocks carry `lang`, `version`, `kind`; `verified` ∈ `passed | failed | unverified`; max ~5 bullets per slide, ~12 words each; code max ~14 lines per slide.

---

# PHASES

## Phase 0: Skeleton
**Do:**
- Create the full folder layout, `.gitignore` (Python, Node, `.env`, `node_modules`, `__pycache__`, build output, `data/`), `.env.example`, a short README.
- Write `schema/deck.schema.json` from the deck shape above, plus `docs/api-contract.md` and `docs/deck-schema.md`.
- Create one valid sample deck in `samples/sample_deck.json` that passes the schema.
- FastAPI app with a `GET /health` endpoint; Next.js app with a blank home page; `docker-compose.yml` with `api` and `web`.
- `git init`, first commit.

**Exit check:** `docker compose up --build` serves the web on :3000 and `curl localhost:8000/health` returns ok. Sample deck validates against the schema (use `jsonschema` in a pytest).

## Phase 1: Sandbox images
**Do:**
- `sandbox/python312/Dockerfile`: Python 3.12, pytest, non-root user.
- `sandbox/java21-spring3/Dockerfile`: Java 21 + Maven, a template Spring Boot 3 project already in the image with all dependencies downloaded (pre-warmed `~/.m2`) so snippets run with `mvn -o` in seconds. Non-root user.
- Build as `studio-java21` and `studio-python312`.

**Exit check:** running a hello-world in each image works offline (`--network none`); the Java one finishes in seconds, not minutes.

## Phase 2: Snippet runner and /verify
**Do (in `services/verifier/`):**
- A runner that executes code in a throwaway container with: `--network none`, `--read-only` root, tmpfs work dir, `--memory 512m`, `--cpus 1`, `--pids-limit 128`, `--cap-drop ALL`, non-root user, and a hard timeout (`SANDBOX_TIMEOUT_SEC`). Kill and clean up the container on timeout.
- Support `lang=java` (plain class, and `kind: spring-fragment` dropped into the template project) and `lang=python`.
- Result: `{status: passed|failed|timeout, stdout, stderr, duration}`.
- Cache results by hash of `(code + lang + version)`.
- Expose `POST /verify` in the API.
- Tests (mark real-Docker tests `@pytest.mark.slow`).

**Exit check:**
```bash
curl -X POST localhost:8000/verify -H "Content-Type: application/json" \
 -d '{"language":"java","version":"21","code":"public class Main{public static void main(String[] a){System.out.println(42);}}"}'
```
returns `status: passed`, stdout `42`. An infinite loop is killed cleanly with `timeout`. Second identical call returns instantly from cache.

## Phase 3: Planner and Generator
**Do (in `apps/api/`):**
- Claude API client (key and model from env). Ask for **structured JSON only**; validate every response against `deck.schema.json`; on invalid output retry once, passing the validation error back.
- Planner: input `topic, level, minutes` -> outline (slide list with types and goals).
- Generator: outline -> full deck JSON (slides, code blocks with stable ids, notes, exercises, quiz, cheat sheet). Enforce bullet and code-length caps in the prompt.
- Store decks (SQLite + files under `DATA_DIR`).
- Implement `POST /decks` and `GET /decks/{id}`. Code blocks start as `verified: unverified`.

**Exit check:** posting a topic produces a schema-valid deck JSON saved to disk. Malformed LLM output triggers one retry (test with a mocked bad response).

## Phase 4: Verification pipeline and self-heal
**Do (in `services/verifier/` + orchestrator):**
- For every code block: run in sandbox. If it fails, send the **full error plus all prior attempts** to Claude for a fix, re-run. Stop at `MAX_FIX_ATTEMPTS`; if still failing, mark `unverified` (never ship it as passed). Record `attempts`.
- After a fix, **regenerate the slide's bullets and notes from the final verified code** so prose matches code.
- Exercise prover: run the `tests` against `reference` (must pass) and against `naive` (must fail). Fill `proof`.
- Verification report JSON per deck (per-block status, attempts, durations). `GET /decks/{id}/report`.
- Run verifications in parallel with a concurrency cap.

**Exit check:** one topic yields a deck where every code block is `passed` or honestly `unverified`; a deliberately broken snippet gets healed; an unfixable one stays `unverified`; report JSON exists.

## Phase 5: Orchestrator and live progress
**Do:**
- Chain Planner -> Generator -> Verifier -> Renderer as a background job per deck.
- `GET /decks/{id}/events`: SSE emitting stage events (`planning`, `generating`, `verifying n/total`, `rendering`, `done`, `error`).

**Exit check:** `curl -N localhost:8000/decks/<id>/events` streams stages in order and ends with `done`.

## Phase 6: Renderer
**Do (in `services/renderer/`):**
- Build `.pptx` from deck JSON using `templates/master.pptx` (create a simple branded master: title, content, code layouts). Code slides use a monospace font with a verified badge (passed / unverified).
- Trainer notes into speaker notes; quiz and cheat sheet as extra slides or separate export.
- Diagrams: Mermaid CLI -> PNG, placed on slides.
- Fit check: detect text overflow / too-long code; auto-shrink or split the slide.
- PDF export via LibreOffice headless (one `soffice` at a time, separate profile dir).
- `GET /decks/{id}/export?format=pptx|pdf`.

**Exit check:** exported PPTX and PDF open correctly for the sample deck and a generated deck: no overflow, readable code, diagrams visible.

## Phase 7: UI
**Do (in `apps/web/`, Tailwind):**
- Home: prompt form (topic, level, minutes) -> starts a deck.
- Progress view consuming SSE.
- Deck viewer: slides list, per-slide verification badge (passed/failed/unverified), code shown, notes.
- Verification report page.
- Buttons: export PPTX / PDF, regenerate slide, upgrade.
- Clear error and loading states.

**Exit check:** full flow in the browser: enter topic -> watch progress -> view deck with badges -> download PPTX and PDF.

## Phase 8: Regenerate and Upgrade
**Do:**
- `POST /decks/{id}/slides/{sid}/regenerate`: regenerate only that slide (stable ids), re-verify, re-render only it; other slides must be byte-identical.
- `POST /decks/{id}/upgrade` (e.g. Spring Boot 2 -> 3): re-generate affected code, re-verify, return a **diff report** (what changed, what failed).

**Exit check:** regenerating one slide leaves all others unchanged; the upgrade returns a readable diff report.

## Phase 9: Hardening and demo readiness
**Do:**
- Failure tests: break a snippet on purpose (self-heal fixes it); unfixable snippet shows `unverified`; infinite loop and memory hog killed cleanly; malformed LLM JSON retried.
- Rate-limit `POST /decks` and cap input length.
- Generate one full deck end to end 3 times in a row without errors.
- Save a backup deck, its report, and cached results in `samples/`.
- Write `docs/demo-script.md` (5-minute demo) and finish `README.md`: what it does, one-command start, env vars, demo steps, architecture diagram, known limitations.
- Add GitHub Actions `ci.yml` (ruff + pytest `-m "not slow"`, web lint/build, validate `samples/*.json` against the schema). No live LLM or full Maven build in CI.

**Exit check:** fresh clone -> `cp .env.example .env` -> add key -> `docker compose up --build` -> smoke test (the /verify curl above) passes -> one deck generates end to end.

---

## Security notes (keep in mind throughout)
- Mounting the Docker socket gives the API host-level power: keep `/verify` internal, never expose it publicly.
- Never commit API keys; search the repo for `sk-` before pushing.
- Sandbox flags in Phase 2 are mandatory, not optional.

## Troubleshooting cheat sheet
| Symptom | Fix |
|---|---|
| Java snippet takes minutes | Use the pre-warmed image and `mvn -o`; never create a fresh project per snippet |
| Spring snippet won't compile | It's a fragment: drop into template project (`kind: spring-fragment`) |
| LLM returns invalid JSON | Validate against schema, retry once with the error |
| Self-heal loops forever | Cap at `MAX_FIX_ATTEMPTS`, include full error and prior attempts, then mark `unverified` |
| Text overflows after export | Enforce caps in schema; run the fit check |
| PDF export fails | Install `libreoffice-impress`; one `soffice` at a time, separate profile dir |
| Prose doesn't match fixed code | Regenerate bullets/notes from the final verified code |
| permission denied on Docker socket | Add user to `docker` group, re-login |

## If time is short, cut in this order
1. Trainer style learning, recording-to-notes, syllabus map (stretch)
2. Upgrade endpoint polish, diagrams
3. CI and deploy

**Never cut:** sandbox verification, self-heal, the `unverified` honesty rule, and the schema.
