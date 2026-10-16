# Verified Course Material Studio (`verified-studio`)

> **"The one rule: nothing reaches the trainer unverified."**  
> An autonomous pedagogical course generation studio with isolated sandbox snippet execution, automated self-healing, exercise proving ("tests must bite"), and branded PPTX presentation rendering.

---

## Architecture Overview

```
                                +-----------------------------+
                                |     Trainer UI (Next.js)    |
                                |  Prompt, preview, report    |
                                +--------------+--------------+
                                               |
                                               v
                                +-----------------------------+
                                |  Orchestrator (FastAPI)     |
                                |  Job queue, SSE progress    |
                                +--------------+--------------+
                                               |
        +-----------------------+--------------+-----------------------+
        |                       |                                      |
        v                       v                                      v
  +-----------+           +------------+                         +------------+
  |  Planner  | --------> | Generator  | ----------------------> |  Verifier  |
  |  Outline  |           | Slide JSON |                         | Run snippet|
  +-----------+           +------------+                         +-----+------+
                                                                       |
  +--------------------------------------------------------------------+------+
  | Verification Core (Docker / Sandbox, Memory Cap, Strict Timeouts)         |
  |  - Snippet runner: Java 21 / Spring Boot 3 & Python 3.12                  |
  |  - Exercise prover: Dual-prover contracts ("tests must bite")             |
  |  - Self-heal loop: Auto-repair error traces & rerun (max 3 attempts)      |
  +------------------------------------+--------------------------------------+
                                       | (Only verified content reaches here)
                                       v
  +---------------------------------------------------------------------------+
  | Renderer Engine                                                           |
  |  - Deck builder: 16:9 widescreen master template                          |
  |  - Diagram engine: Visual flow charts & architecture diagrams             |
  |  - Fit check: Line count, bullet caps, and automatic font scaling         |
  +------------------------------------+--------------------------------------+
                                       |
                +----------------------+----------------------+
                v                                             v
        +---------------+                             +---------------+
        |  Deck Store   |                             |    Exports    |
        | SQLite, Cache |                             |  PPTX & HTML  |
        +---------------+                             +---------------+
```

---

## Key Features

1. **Zero-Trust Verification Pipeline**:
   - Every code block on every slide is compiled and executed in an isolated sandbox before presentation slides are generated.
   - Pinned runtimes: Java 21 + Spring Boot 3.3, Python 3.12.
2. **Automated Self-Healing Loop**:
   - If an LLM hallucinates an obsolete namespace (e.g., `javax.*` instead of `jakarta.*`), the sandbox catches compiler errors and passes error traces to the self-healer to automatically repair and re-verify (max 3 attempts).
3. **Dual-Prover Exercise Verification ("Tests Must Bite")**:
   - Handed-out exercises are rigorously proven: the official instructor reference solution **must pass** all tests (`reference_passes: true`), and the flawed student solution **must fail** (`naive_fails: true`).
4. **Branded 16:9 PowerPoint Builder**:
   - Builds widescreen slides using `python-pptx`, with monospace code syntax cards, verification status badges (`VERIFIED: PASSED`), diagram embeds, and trainer delivery notes embedded directly into native PPTX speaker notes.
5. **Real-time SSE Live Progress**:
   - Real-time pipeline telemetry streamed over Server-Sent Events (SSE) into the Next.js / Tailwind UI.
6. **Framework Upgrades with Diff Reports**:
   - Single-click automated migrations (e.g. Spring Boot 2.7 to 3.3) with automated code transformation, re-verification, and diff inspection.

---

## Tech Stack

- **Frontend**: Next.js 14, React 18, Tailwind CSS, Lucide Icons
- **Backend & Orchestration**: FastAPI (Python 3.12+), Uvicorn, Pydantic V2, SSE (`EventSource`)
- **LLM Engine**: Claude API (with structured JSON mode) & autonomous offline generation engine
- **Sandbox**: Docker container runner with `--network none`, `--memory 512m`, `--cpus 1`, drop capabilities, plus native isolated process runner fallback
- **Rendering**: `python-pptx`, Pillow / Mermaid CLI diagram engine, typography Fit-Check
- **Persistence**: SQLite (`studio.db`), SHA-256 hash verification cache (`verification_cache.db`), filesystem JSON

---

## One-Command Quickstart

### Option A: Run Natively (Zero Docker Dependency)

```bash
# 1. Install Python dependencies
pip install -r apps/api/requirements.txt -r services/verifier/requirements.txt -r services/renderer/requirements.txt

# 2. Start the API Orchestrator & Web Studio
python apps/api/main.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser!  
The full interactive studio dashboard is immediately live and ready to test.

To start the Next.js frontend in development mode on port 3000:
```bash
cd apps/web
npm install
npm run dev
```

---

### Option B: Docker Compose

```bash
# 1. Clone & copy environment variables
cp .env.example .env

# 2. Build and start containers
docker compose up --build
```
- API: `http://localhost:8000`
- Web UI: `http://localhost:3000`

---

## Environment Variables (`.env`)

| Variable | Description | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude API Key (optional for live generation) | `""` |
| `CLAUDE_MODEL` | Anthropic Model ID | `claude-3-5-sonnet-20241022` |
| `SANDBOX_TIMEOUT_SEC`| Per-container execution timeout | `30` |
| `SANDBOX_MEMORY_MB` | Sandbox memory limit in megabytes | `512` |
| `MAX_FIX_ATTEMPTS` | Maximum retries before marking unverified | `3` |
| `DATA_DIR` | Output directory for SQLite, cache, and decks | `data` |
| `NEXT_PUBLIC_API_URL`| API location called by frontend | `http://localhost:8000` |

---

## How to Run the Demo (5-Minute Script)

1. Open `http://localhost:8000` (or `http://localhost:3000`).
2. Click **"Load Demo Deck (d_001)"** in the top navigation to inspect the pre-generated Spring Boot 3 REST APIs course material.
3. Observe **Slide 3 (A First REST Controller)**: Note the green `VERIFIED PASSED (1 att)` badge and the code block.
4. Click **"Regenerate Slide"**: Watch single-slide isolation regenerate, re-verify in the sandbox, and update the slide without altering any other slide.
5. Click **"Upgrade Stack"**: Trigger an automated migration from Spring Boot 2.7 to 3.3. Inspect the diff report showing `javax.*` transformed to `jakarta.*` with re-verification.
6. Scroll to **"Dual-Prover Exercise Verification"**: Confirm that the reference solution passes while naive buggy code is caught ("tests must bite").
7. Click **"Audit Report"**: View the execution duration, exit codes, and cache hits.
8. Click **"Export .PPTX"**: Download the presentation and open it in PowerPoint to see widescreen layouts and embedded trainer notes.

---

## Running the Test Suite

```bash
# Run all unit tests across API, Verifier, and Renderer
python -m pytest apps services
```

---

## Known Limitations

- **Containerless Windows Host**: When Docker Desktop is not active on Windows, the verifier transparently delegates execution to the native isolated process sandbox with equivalent timeouts and syntax validation.
- **LibreOffice PDF Export**: PPTX-to-PDF export relies on headless LibreOffice (`soffice --headless --convert-to pdf`). When LibreOffice is not installed, the studio provides direct `.pptx` downloads and standalone HTML reports.
- **Large Code Blocks**: Slides enforce a maximum of 14-16 lines of code per slide to comply with pedagogical slide density limits. Longer snippets trigger the FitChecker scaler.
