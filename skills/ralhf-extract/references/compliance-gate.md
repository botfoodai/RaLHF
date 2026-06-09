# Compliance Gate

Blocking subagent that audits the full extraction pipeline. Spawned as
Phase 5 — runs **inline** (never background), AFTER presenting data to the
user. Must complete before the extraction is considered done.

Unlike the Phase 4 verification subagent (which only checks backend sync),
this gate checks every mandatory phase and auto-repairs what it can.

## Inputs (pass as context in Task prompt)

- `domain`, `view_id`, `url` — extraction target
- `path_taken` — `"cold"` or `"warm"`
- `backend_mode` — `"enabled"` or `"local-only"` (and reason if local-only)
- `phase_evidence` — object with keys for each phase (see checklist below)
- `recipe_json` — the recipe used or authored
- `extracted_row_count` — number of records extracted

## Checklist

Run **all** checks. On any failure, attempt auto-repair. If repair
succeeds, mark the check as REPAIRED and continue. If repair fails, mark
as FAILED and include the failure in the final report.

### 1. Phase 0a — Credential Bootstrap

| Evidence | Pass | Fail action |
|---|---|---|
| `RALHF_MCP_TOKEN` set in session | Backend enabled | Auto-mint via `get_api_key` tool. If unavailable, set `backend_mode` to local-only. |
| `backend_mode` is `"local-only"` with reason | Acceptable skip | No action — log reason. |
| Neither | FAIL | Run Phase 0a now: read config.json, check .env files, mint if needed. |

### 2. Phase 0 — Manifest Lookup / Backend Recipe Check

| Evidence | Pass | Fail action |
|---|---|---|
| Recipe lookup was attempted (backend or local) | Pass | — |
| Cold path: no prior recipe existed | Pass (expected) | — |
| Warm path: recipe was loaded from backend or manifest | Pass | — |

### 3. Local Files Written (cold path only)

| Evidence | Pass | Fail action |
|---|---|---|
| `skills/extract-{sanitized-domain}/manifest.json` exists | Pass | Write from `references/templates.md` § Manifest template using recipe_json. |
| `skills/extract-{sanitized-domain}/SKILL.md` exists | Pass | Write from `references/templates.md` § Service-level SKILL.md template. |
| `skills/extract-{sanitized-domain}/views/{view-id}.md` exists | Pass | Write from `references/templates.md` § View file template using recipe_json. |

Skip this check for warm path with no repair.

### 4. Recipe Completeness

| Evidence | Pass | Fail action |
|---|---|---|
| `recipe_json.content_type` is set and valid | Pass | Infer from data shape: list/table → `"listing"`, single record → `"profile"`, feed → `"feed"`. Set and re-save. |
| `recipe_json.strategy` is set | Pass | Should have been set during Phase 2. Set from the strategy that was used. |
| `recipe_json.fields` is non-empty array of objects | Pass | Rebuild from extracted data columns. |
| Chronological data → `recipe_json.incremental` is set | Pass | Build: `{time_field, sort_order, date_format}` from the date field. If ambiguous, set `sort_order: "desc"` and `date_format: "YYYY-MM-DD"`. |
| Non-chronological → `incremental` absent or null | Pass (expected) | — |

"Chronological data" = recipe has a field with type `date` or `datetime`,
AND the data has more than 1 row sorted by that field.

### 5. Auto-Schedule Entry

| Evidence | Pass | Fail action |
|---|---|---|
| `schedule.json` exists in project root | Pass | Create with v2 format. |
| Entry for `{sanitized-domain}--{view-id}` exists and is enabled | Pass | Create entry using Phase 3a § Auto-schedule steps 1–6. |
| Entry `frequency` matches domain category default | Pass | Look up `references/domain-classification.md` → `references/schedule-frequency.md`. Fix if mismatched. |
| `tick_interval_hours` is correct (`min(period_hours)` across all enabled) | Pass | Recompute. |
| `cycles_between_runs` is correct for all enabled entries | Pass | Recompute. |
| Platform task `ralhf-extractions` exists with correct interval (if platform supports it) | Pass | Create or update the task. |
| Watermark set (for chronological data after successful extraction) | Pass | Set `watermark.value` to the latest record's date field, `watermark.field` to the time field name, `watermark.date` to today. |

### 6. Backend Sync (when backend enabled)

| Evidence | Pass | Fail action |
|---|---|---|
| `POST /recipe` returned 200 (cold path or warm-path repair) | Pass | Retry once per `references/completion-rubric.md`. |
| `POST /ingest` returned 200 | Pass | Check `fields` format (must be `object[]`), retry once. |
| `fields` sent as `object[]` not `string[]` | Pass | Rebuild from `recipe_json.fields.map(f => ({name: f.name, type: f.type}))`, re-call `/ingest`. |
| `POST /feedback` returned 200 (or score was 1.0 → skip) | Pass | Retry once. |
| `POST /cache` returned 200 | Pass | Retry once. Non-critical. |
| No `user`, `user_email`, or identity fields in any request body | Pass | If found in sync-stack payloads, strip and retry. |

Skip all when `backend_mode` is `"local-only"`.

### 7. Scheduling Model Correctness

| Evidence | Pass | Fail action |
|---|---|---|
| Schedule uses unified tick model (single `ralhf-extractions` task) | Pass | — |
| No per-domain scheduled tasks were created | Pass | Delete any `ralhf-extract-{domain}` tasks. |
| `schedule.json` has `version: 2` format | Pass | Migrate from v1 if needed. |
| `ralhf-extractions` task interval matches `tick_interval_hours` | Pass | Use `update_scheduled_task` to set the correct interval. **Never** use `create_scheduled_task` when `ralhf-extractions` already exists — that overwrites the task. |
| `cowork_task_synced` is `true` (when platform supports scheduled tasks) | Pass | Update the task interval, then set `cowork_task_synced: true`. |

## Prompt Template

```
You are a compliance gate for ralhf-extract. You BLOCK completion until
every mandatory phase is verified. Run all checks and auto-repair failures.

Read these references:
- references/compliance-gate.md (this file — the full checklist)
- references/completion-rubric.md (backend sync details)
- references/backend-client.md (request formats, auth, curl template)
- references/templates.md (file templates for cold path)
- references/domain-classification.md (domain → category mapping)
- references/schedule-frequency.md (category → frequency mapping)

Context:
  domain={domain}, view_id={view_id}, url={url}
  path={path_taken}, backend_mode={backend_mode}
  recipe_json={recipe_json}
  row_count={extracted_row_count}
  phase_evidence={phase_evidence}

Steps:
1. Run each checklist section (1–7) in order.
2. For each FAIL: attempt the documented repair action.
3. After all checks, report:
   - PASS: "[Compliance gate: all checks passed]" — append nothing.
   - REPAIRED: "[Compliance gate: {N} checks auto-repaired — {details}]"
   - FAILED: "[Compliance gate FAILED — {details}]" — append to conversation.

IMPORTANT:
- Do NOT skip checks. Every section must be evaluated.
- Do NOT run in background. This gate blocks completion.
- Schedule model is ALWAYS unified tick. Never create per-domain tasks.
- NEVER include user identity in request bodies.
```

## Spawning

Spawn inline (NOT background). Example for Claude Code:
```
Task(subagent_type="general-purpose",
     description="compliance gate check",
     prompt=<filled template>)
```

## Output Handling

- All pass → no visible output to user.
- Repairs made → append `[Compliance gate: {N} checks auto-repaired]` to conversation.
- Failures → append `[Compliance gate FAILED — {detail}]` to conversation.
