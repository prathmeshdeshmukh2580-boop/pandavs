# 5-Minute Hackathon Demo Script

Follow this script to rehearse and deliver a seamless 5-minute demonstration to judges.

---

### Minute 0:00 - 1:00 | The Problem & The Core Principle
- **The Hook**: "Every developer trainer has suffered the horror of showing sample code during a live workshop that fails to compile because of a minor version upgrade or a typo."
- **The Core Rule**: "Our rule is simple: **Nothing reaches the trainer unverified.** Every snippet, exercise, and diagram either feeds or protects the verification pipeline."
- **Architecture**: Show the 4-stage pipeline diagram: Planner ➔ Generator ➔ Verifier (Sandbox) ➔ Renderer.

---

### Minute 1:00 - 2:30 | Live Generation & SSE Stream
- Open the UI at `http://localhost:8000` (or `http://localhost:3000`).
- Show the **Course Generator** form:
  - Topic: "Spring Boot 3 REST APIs & Architecture"
  - Stack: Java 21 / Spring Boot 3.3
  - Duration: 90 mins
- Click **"Generate Verified Deck"**:
  - Point to the live SSE progress indicator: Planner ➔ Generator ➔ Verifier ➔ Renderer.
  - Explain: "Notice the Verifier step executing each snippet in an isolated sandbox with memory limits and zero network access."

---

### Minute 2:30 - 3:30 | The Verification Core & Self-Heal Loop
- Point to **Slide 3 (A First REST Controller)** and **Slide 4 (Request Validation)**:
  - Show the green `VERIFIED PASSED (1 att)` badge.
  - Open the **Audit Report modal**: Explain execution time, sandbox safety, and cache hit acceleration (<5ms on repeats).
- Explain the **Self-Healing Loop**:
  - "If an LLM hallucinates an old `javax.validation` annotation or misses a bracket, our self-healing loop catches the compiler error, feeds the trace to the repair agent, and re-runs. If it doesn't converge within 3 attempts, it is flagged as `UNVERIFIED` and barred from shipping."

---

### Minute 3:30 - 4:15 | Exercise Prover ("Tests Must Bite") & Framework Upgrade
- Scroll down to the **Dual-Prover Exercise card**:
  - Show that `reference_passes` is true AND `naive_fails` is true.
  - "Trivial tests that pass on broken code are rejected before the class starts."
- Click **"Upgrade Stack"**:
  - Watch the automated migration from Spring Boot 2 to 3.3.
  - Show the diff report showing `javax.*` upgraded to `jakarta.*` with all tests passing.

---

### Minute 4:15 - 5:00 | One-Click Export & Conclusion
- Click **"Export .PPTX"**:
  - Open the downloaded PowerPoint presentation.
  - Show the 16:9 widescreen layout, dark syntax theme, and embedded trainer speaking notes.
- Click **"Audit Report" ➔ "View Standalone HTML Report"**:
  - Show the audit trail for enterprise training organizations.
- Wrap up: "A complete zero-trust studio producing production-ready training material in under 2 minutes."
