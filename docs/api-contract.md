# API Contract

Base URL: `http://localhost:8000` (from `NEXT_PUBLIC_API_URL`). All bodies are JSON unless noted.

> `/verify` runs code via the Docker socket. Keep the API internal; never expose it publicly.

| Endpoint | Purpose | Phase |
|---|---|---|
| `GET /health` | Liveness check, returns `{"status": "ok"}` | 0 |
| `POST /decks` | Start generation from `topic, level, minutes`; returns deck id | 3/5 |
| `GET /decks/{id}/events` | SSE stream of stage progress | 5 |
| `GET /decks/{id}` | Deck JSON with per-slide verification status | 3 |
| `POST /verify` | Run one snippet in sandbox | 2 |
| `POST /decks/{id}/slides/{sid}/regenerate` | Regenerate one slide, re-verify, re-render only it | 8 |
| `POST /decks/{id}/upgrade` | Upgrade to newer framework version; returns diff report | 8 |
| `GET /decks/{id}/report` | Verification report (JSON, or PDF with `?format=pdf`) | 4 |
| `GET /decks/{id}/export?format=pptx\|pdf` | Download deck | 6 |

## Shapes

### `POST /decks`
Request:
```json
{ "topic": "Spring Boot 3 REST APIs", "level": "beginner", "minutes": 90 }
```
Response `202`:
```json
{ "deck_id": "d_ab12cd34", "status": "queued" }
```

### `GET /decks/{id}/events` (text/event-stream)
```
event: stage
data: {"stage": "verifying", "done": 3, "total": 8}
```
Stages, in order: `planning`, `generating`, `verifying`, `rendering`, `done` (or `error` with `message`).

### `GET /decks/{id}`
Returns a deck matching [`schema/deck.schema.json`](../schema/deck.schema.json), plus HTTP `404` if unknown.

### `POST /verify`
Request:
```json
{ "language": "java", "version": "21", "code": "public class Main{...}", "kind": "plain" }
```
`kind` is optional (`plain` default, or `spring-fragment` for Java).
Response:
```json
{ "status": "passed", "stdout": "42\n", "stderr": "", "duration": 1.84, "cached": false }
```
`status` is one of `passed | failed | timeout`.

### `POST /decks/{id}/upgrade`
Request: `{ "target": {"spring_boot": "3.3"} }`. Response: diff report listing changed blocks and their new status.

### Errors
`{"detail": "message"}` with a suitable 4xx/5xx code.
