# Backup Screen Recording & Offline Walkthrough

In the event of venue network failure or blocked Wi-Fi during judging:

1. **Pre-Cached Deck**:
   - `samples/spring_boot_deck.json` contains a pre-generated 7-slide deck.
   - `samples/verification_report.json` contains the complete audit log.
   - Clicking **"Load Demo Deck (d_001)"** in the top navigation immediately restores full functionality without making external LLM network calls.

2. **Offline Verification**:
   - Verification cache hashes ensure that all sample snippets return status `passed` instantly (<5ms) from `data/verification_cache.db`.

3. **Presentation Artifact**:
   - The pre-built `.pptx` can be generated directly using `python services/renderer/exporter.py` or downloaded via the UI.
