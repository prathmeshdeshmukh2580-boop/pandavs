# Deck Schema

Source of truth: [`schema/deck.schema.json`](../schema/deck.schema.json) (JSON Schema 2020-12).
Do not change it without telling everyone; LLM output, the verifier and the renderer all depend on it.

## Top level
| Field | Type | Notes |
|---|---|---|
| `deck_id` | id (`d_...`) | Stable |
| `topic` | string | 3-200 chars |
| `level` | `beginner \| intermediate \| advanced` | |
| `minutes` | int | 5-480 |
| `stack` | map string -> string | e.g. `{"java": "21", "spring_boot": "3.3"}` |
| `slides` | Slide[] | at least 1 |
| `exercises` | Exercise[] | |
| `quiz` | QuizItem[] | |
| `cheat_sheet` | string | plain text, one item per line |
| `meta` | object | optional, not rendered |

## Slide
`id` (`s_...`), `type` (`title | section | content | code | diagram | exercise | summary`), `title` (<= 90 chars),
`bullets` (max 5, each <= 120 chars, aim for ~12 words), `code` (max 2 blocks), `diagram` (null or Mermaid), `notes` (trainer notes -> speaker notes).

## Code block
| Field | Notes |
|---|---|
| `id` | `c_...`, stable across regenerations |
| `lang` | `java \| python` |
| `version` | e.g. `"21"`, `"3.12"` |
| `kind` | `plain` (self-contained program) or `spring-fragment` (dropped into the template Spring Boot project) |
| `source` | aim for <= 14 lines; the renderer fit check splits/shrinks longer code |
| `expected_output` | string or null; when set, stdout must match (trimmed) |
| `verified` | `passed \| failed \| unverified` |
| `attempts` | number of sandbox runs used (0 = never run) |

**Honesty rule:** a block is `passed` only if the sandbox actually ran it successfully. If self-heal gives up it is `unverified`, never `passed`.

## Exercise
`id` (`e_...`), `title`, `lang`, `version`, `prompt`, `starter`, `tests`, `reference`, `naive`,
`proof: {reference_passes, naive_fails}` (booleans, or null before proving). A good exercise has `reference_passes = true` and `naive_fails = true`.

## Quiz item
`id` (`q_...`), `question`, `options` (2-6), `answer_index`, `explanation`.

## Assumptions vs. the guide's minimum shape
- Added `lang`, `version`, `title`, `prompt` to exercises (the prover needs the language).
- Added `diagram` object `{id, kind: "mermaid", source}` and optional top-level `meta`.
- The 14-line code cap is enforced by the renderer fit check, not the schema (keeps LLM retries low).
