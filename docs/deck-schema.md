# Deck Schema Specification

The single source of truth for all course materials generated, verified, and rendered by Verified Course Material Studio is defined in `schema/deck.schema.json`.

## Core Principles
1. **Stable IDs**: Every slide (`s_001`, `s_002`) and code snippet (`c_001`, `c_002`) carries a stable deterministic ID. This enables targeted single-slide regeneration and version upgrade diffs without altering the rest of the deck.
2. **Runtime Metadata**: Every code block must declare `lang`, `version`, and `kind` (e.g. `spring-fragment`, `python-script`, `class`).
3. **Verification State**: The `verified` field is strictly one of `passed`, `failed`, or `unverified`. Only `passed` snippets reach exported presentation slides.
4. **Pedagogical Constraints**:
   - Bullets: Capped at maximum 6 bullets per slide (~12 words each).
   - Code: Capped at approximately 14 lines per slide to prevent visual cognitive overload.
5. **Dual-Prover Exercise Verification ("Tests Must Bite")**:
   - `reference_passes`: true (Instructor code passes all tests).
   - `naive_fails`: true (Flawed student code is caught by tests).
