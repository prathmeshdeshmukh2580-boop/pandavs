# Verified Course Material Studio: API Contract

The API orchestrates course planning, slide-level generation, sandbox execution, self-healing retries, and PPTX/PDF rendering.

Base URL: `http://localhost:8000`

---

## 1. Create Course Deck
- **Endpoint**: `POST /decks`
- **Status**: `202 Accepted`
- **Request Body**:
```json
{
  "topic": "Spring Boot 3 REST APIs",
  "level": "beginner",
  "minutes": 90,
  "stack": {
    "java": "21",
    "spring_boot": "3.3"
  }
}
```
- **Response**:
```json
{
  "deck_id": "d_a81f302b",
  "status": "processing",
  "events_url": "/decks/d_a81f302b/events"
}
```

---

## 2. Live Progress Event Stream (SSE)
- **Endpoint**: `GET /decks/{deck_id}/events`
- **Header**: `Accept: text/event-stream`
- **Stream Format**:
```
data: {"stage": "planner", "progress": 15, "message": "Planning course outline...", "timestamp": "...", "meta": {}}
data: {"stage": "generator", "progress": 35, "message": "Generating schema-valid slides...", "timestamp": "...", "meta": {}}
data: {"stage": "verifier", "progress": 65, "message": "Verifying snippet c_001 in sandbox...", "timestamp": "...", "meta": {"slide_id": "s_003"}}
data: {"stage": "renderer", "progress": 85, "message": "Rendering PPTX deck and fit check...", "timestamp": "...", "meta": {}}
data: {"stage": "complete", "progress": 100, "message": "Completed!", "timestamp": "...", "meta": {"pptx_path": "..."}}
```

---

## 3. Retrieve Deck JSON
- **Endpoint**: `GET /decks/{deck_id}`
- **Response**: Full JSON document adhering strictly to `schema/deck.schema.json`.

---

## 4. Standalone Snippet Verification
- **Endpoint**: `POST /verify`
- **Request Body**:
```json
{
  "language": "java",
  "version": "21",
  "code": "public class Main{public static void main(String[] a){System.out.println(42);}}",
  "kind": "class",
  "expected_output": "42"
}
```
- **Response**:
```json
{
  "status": "passed",
  "stdout": "42\n",
  "stderr": "",
  "duration_ms": 34.2,
  "cached": false,
  "returncode": 0
}
```

---

## 5. Regenerate Single Slide
- **Endpoint**: `POST /decks/{deck_id}/slides/{slide_id}/regenerate`
- **Request Body**:
```json
{
  "prompt_hint": "Add deeper explanation of response status codes"
}
```
- **Behavior**: Re-generates only target slide `{slide_id}`, runs verifier on it, re-renders the presentation, preserving all other slides intact.

---

## 6. Framework Upgrade
- **Endpoint**: `POST /decks/{deck_id}/upgrade`
- **Request Body**:
```json
{
  "target_stack": {
    "java": "21",
    "spring_boot": "3.3"
  }
}
```
- **Response**:
```json
{
  "deck_id": "d_001",
  "old_stack": {"spring_boot": "2.7"},
  "new_stack": {"java": "21", "spring_boot": "3.3"},
  "changes_count": 2,
  "diff": [
    {
      "slide_id": "s_004",
      "snippet_id": "c_002",
      "change": "Migrated javax.* namespace to jakarta.* for Spring Boot 3"
    }
  ],
  "status": "upgrade_completed"
}
```

---

## 7. Verification Audit Report
- **Endpoint**: `GET /decks/{deck_id}/report?format=json` (or `?format=html`)
- Returns sandbox execution duration, cache status, attempts, error messages, and dual-prover exercise results ("Tests Must Bite").

---

## 8. Export Presentation (.PPTX)
- **Endpoint**: `GET /decks/{deck_id}/export?format=pptx`
- Returns download binary stream with `Content-Type: application/vnd.openxmlformats-officedocument.presentationml.presentation`.
