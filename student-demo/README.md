# Student Demo Data Contribution

This folder adds structured sample learning content for the Verified Course Material Studio.

## Files
- `data/lessons.json`: lesson packs, objectives, explanations, examples, and cheat sheets.
- `data/quizzes.json`: multiple-choice questions with answer keys and explanations.
- `data/exercises.json`: programming tasks, starter/reference code, and expected test cases.

## Included topics
- Binary Search (DSA)
- DBMS Normalization
- Operating System Processes
- Python Functions

## Integration and safety notes
- These JSON files are sample content. The app must load them or import them into its data store.
- Keep quiz answer keys server-side if answers should remain hidden before submission.
- Do not expose exercise reference solutions before students submit.
- Never execute untrusted submitted/generated code inside the API process. Use the repository's isolated sandbox/verifier with resource limits and no network access.
- Invalidate verification results whenever the tested code changes.

## Scope
This is a sample-data contribution. These files alone do not implement AI generation, sandbox execution, or PPT/PDF rendering.
