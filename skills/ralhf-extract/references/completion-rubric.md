# Completion Rubric

Pass/fail checklist for every extraction run. Evaluate **after** presenting
results to the user. Backend disabled (credentials missing) → backend
checks (1–5) auto-pass. Pipeline checks (6–10) always apply.

## Backend Sync Checks

| # | Check | Pass | Fail action |
|---|---|---|---|
| 1 | Recipe saved | `POST /recipe` returned 200 (cold path or warm-path repair). Warm path with no repair: auto-pass. | Retry once. Log error if retry fails. |
| 2 | Ingest called | `POST /ingest` returned 200. | Check `fields` format (see #3), retry once. |
| 3 | Fields format correct | `fields` is `object[]`: `[{"name":"...","type":"..."}, ...]`. Each object has `name` (string) and `type` (string). | Rebuild `fields` from `recipe_json.fields` — map each to `{"name": f.name, "type": f.type}`. Re-call `/ingest`. |
| 4 | Feedback filed | Score < 1.0 → `POST /feedback` returned 200. Score = 1.0 → skip (auto-pass). | Retry once. Log error if retry fails. |
| 5 | Data cached | `POST /cache` returned 200. | Retry once. Non-critical — log and continue. |

## Pipeline Checks (always required)

| # | Check | Pass | Fail action |
|---|---|---|---|
| 6 | Local files saved | Skill files written to disk (cold path) or unchanged (warm path). | Re-save from in-memory recipe using `references/templates.md`. |
| 7 | Recipe complete | `content_type` set, `strategy` set, `fields` non-empty. Chronological data has `incremental` object. | Infer missing fields. See `references/compliance-gate.md` § Recipe Completeness. |
| 8 | Auto-schedule entry | `schedule.json` has enabled entry for this domain/view with correct frequency from `references/domain-classification.md`. | Create entry per Phase 3a § Auto-schedule. |
| 9 | Scheduling model | Single `ralhf-extractions` platform task (unified tick). No per-domain tasks. Interval matches `tick_interval_hours`. `cowork_task_synced` is `true`. | Delete per-domain tasks. Use `update_scheduled_task` to fix interval (never `create_scheduled_task` when task exists). Set `cowork_task_synced: true`. |
| 10 | No identity leak | No `user`, `user_email`, or identity fields in any backend request body. | Strip from sync-stack payloads and retry. |

## Fields Format — CRITICAL

The `/ingest` endpoint requires `fields` as an **array of objects**, not
an array of strings.

**Correct:**
```json
"fields": [
  {"name": "date", "type": "date"},
  {"name": "title", "type": "text"}
]
```

**Wrong (causes silent 400):**
```json
"fields": ["date", "title"]
```

Build `fields` from the recipe: `recipe_json.fields.map(f => ({name: f.name, type: f.type}))`.

## Retry Policy

- Max 1 retry per check.
- Retries run in background (do not block user output).
- If retry also fails, append `[Backend sync incomplete — {check name}: {error}]`
  to the conversation.
