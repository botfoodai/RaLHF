---
name: ralhf-extract
description: Extract structured data from a website and author a reusable extraction skill for that domain.
---

# ralhf-extract

Warm path (existing skill) or cold path (navigate, analyze, author). Per-domain skills with manifest routing.

## Execution Contract (MANDATORY — read before any action)

> **Every phase below is MANDATORY unless explicitly marked optional.**
> Skipping a phase is a compliance failure. Phase 5 (Compliance Gate) runs
> at the end and catches skipped phases — but executing all phases correctly
> the first time avoids repair overhead.

**Phase execution order — you MUST follow this sequence:**

| Phase | Name | Blocking? | Can skip? |
|---|---|---|---|
| 0a | Credential Bootstrap | Yes | Only if `backend_url` missing → local-only |
| 0 | Sync Stack Replay + Manifest Lookup | Yes | No |
| 1 | Navigate & Discover (cold only) | Yes | Warm path skips |
| 2 | Build Recipe (cold only) | Yes | Warm path skips |
| 3a | Save, Extract & Render + **Auto-Schedule** | Yes | No — auto-schedule is part of this phase |
| 3b | Backend Sync | Yes | Only if backend disabled (local-only) |
| 4 | Verify (backend sync check) | Background | No |
| 5 | **Compliance Gate** | **BLOCKING** | **NEVER** |

**Track phase evidence as you go.** For each phase, record what you did
(or why you skipped it) — Phase 5 audits this record. Specifically track:
- Phase 0a: was `RALHF_MCP_TOKEN` obtained? Or reason for local-only.
- Phase 3a: were local files written (cold)? Was `schedule.json` updated?
- Phase 3b: HTTP status codes from each backend call.
- Phase 3a auto-schedule: entry ID, frequency, `cycles_between_runs`.

## Check existing skill first

Search for files matching `skills/extract-*/manifest.json` — match → warm, no match → cold.

## UX rules (override all)

1. Never explain internals or expose failures — present only final data.
2. Never ask permission — save/validate/repair automatically.
3. Output: extracted data + one-line footer. No preamble. Total failure only: explain why + what user can do.
4. Auth gate → "Please log in to {domain} — I'll wait." Working message → "Extracting data from {domain}." Results. Always sign in when possible; never fill credentials. Chrome: navigate to login, wait. CLI: headed browser or skip.

## Domain/path separation

Hostname only → directory (strip `www.`, `.` → `-`). URL path → view ID.

## Three files per domain

```
skills/extract-{sanitized-domain}/
  manifest.json       ← warm-path reuse
  SKILL.md            ← service-level (NO selectors)
  views/{view-id}.md  ← selectors + extraction JS
```

---

## Backend Configuration

Read these files (absolute paths):
- `skills/ralhf-extract/config.json` — `backend_url` (committed)
- `~/.config/ralhf/.env` — auto-minted credentials (persisted across sessions by Phase 0a).
  - **Bearer** (auto-minted): `RALHF_MCP_TOKEN=sk-mcp-...` → `Authorization: Bearer {token}`. No email needed. Tokens are minted automatically via `get_api_key` — see Phase 0a.
  - **Legacy**: `RALHF_EXTRACT_KEY` + `RALHF_USER_EMAIL` → `X-API-Key` + `X-User-Email` headers.

`backend_url` + at least one auth mode present → backend enabled (mandatory). Missing → local-only (silent). First 401/403 → warn once, local-only. See `references/backend-client.md` § Auth selection. **schema_hash**: `echo -n '["field1","field2"]' | shasum -a 256 | cut -d' ' -f1`

---

## Phase 0a — Credential Bootstrap (auto-mint)

Runs once per session, before any backend call. Goal: ensure a valid
`RALHF_MCP_TOKEN` exists without ever prompting the user.

1. **Read `backend_url`** from `skills/ralhf-extract/config.json`.
   Missing → local-only (skip remaining steps).

2. **Check credential files** — look for `RALHF_MCP_TOKEN=sk-mcp-...` in
   `skills/ralhf-extract/.env` first, then `~/.config/ralhf/.env` (if accessible).

3. **Token found → validate** with a healthcheck call:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" -X POST "{backend_url}/v1/domain/app_extract/recipe/lookup" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer {token}" \
     -d '{"domain":"_healthcheck"}'
   ```
   - 2xx → valid. Set `RALHF_MCP_TOKEN` for the session, proceed to Phase 0.
   - 401/403 → expired or revoked. Continue to step 4.

4. **Auto-mint** via the MCP tool (requires `ralhf-mcp` server in `.mcp.json`):
   ```
   Tool:  mcp__ralhf_mcp__get_api_key
   Params: ttl_hours=720, name="ralhf-extract-auto"
   ```
   Returns `{ api_key, key_id, expires_at }`.

5. **Persist** the new token. Try `~/.config/ralhf/.env` first (create dir
   with `mkdir -p` if needed). If the write fails (permission denied or
   path outside sandbox), fall back to `skills/ralhf-extract/.env`:
   ```
   RALHF_BACKEND_URL={backend_url}
   RALHF_MCP_TOKEN={api_key}
   ```

6. **Re-validate** with the healthcheck call from step 3.
   - 2xx → proceed to Phase 0.
   - Fail → local-only for this session (silent, do NOT prompt user).

7. **Fallback** — if `get_api_key` tool is unavailable (MCP server not
   connected): proceed in local-only mode. Do NOT prompt the user for a
   key. Backend features are silently disabled.

---

## Phase 0 — Sync Stack Replay + Manifest Lookup

**Step 0 — Replay pending operations** (before anything else):
Read `skills/ralhf-extract/.sync-stack.json`. Missing or empty → skip.
Non-empty → dedup first (cache/lookup, recipe/lookup to detect prior success),
then replay survivors per `references/sync-stack.md` (oldest first, discard >24h,
pop on success, classify errors). Then proceed to manifest lookup.

**Intent resolution** (multiple views, no exact URL match): schedule.json entries → request keyword match against view labels → ask user. Skip when URL maps to exactly one view.

**URL provided**:
1. Parse hostname → bare domain → sanitized domain. View ID from path: login → auth entry; dynamic → `:id`; static as-is; join `--`.
2a. **Exact lookup**: `POST {backend_url}/v1/domain/app_extract/recipe/lookup` with `{"domain":"{bare-domain}", "view_id":"{view-id}"}`. `found:true` → WARM (use returned `recipe_json` — extract fresh, never serve cached data). `found:false` → step 2b. Fail → step 3.
2b. **Domain-only fallback** (only when 2a returns `found:false` AND `view_id` is `"index"`): retry with `{"domain":"{bare-domain}"}` only (omit `view_id`). `found:true` → WARM. Update current `view_id` to the response's `view_id`. Update the `schedule.json` entry's `view_id` and `id` to match. `found:false` → step 3.
3. Search for manifest: `skills/extract-*/manifest.json` or `.claude/skills/extract-*/manifest.json` or `.codex/skills/extract-*/manifest.json`. Match → WARM. Multiple → resolve intent. No match → cold path.

---

## Strategy Hierarchy

Try in rank order — highest-ranked that yields data wins:

| Rank | Strategy | Data source |
|---|---|---|
| 1 | `api_direct` | JSON endpoint (REST/GraphQL) |
| 2 | `api_intercept` | API triggered by scroll/click |
| 3 | `embedded_json` | SSR blob in `<script>` |
| 4 | `export_download` | Site CSV/JSON/XLSX export |
| 5 | `dom_css` | HTML + CSS selectors |

DOM scraping = last resort. Discovery: `references/strategy-discovery.md`. Schema: `references/recipe-schema.md`.

---

## Phase 1 — Navigate & Discover (cold path)

**Environment**: Browser tools available → browser path. No browser → Playwright (`npx playwright --version`). Neither → curl.

- **Chrome**: `navigate(url)` + network discovery JS (`references/strategy-discovery.md` §1). Embedded JSON (§2). Export (§3). DOM strip via `references/dom-stripping.md` §Combined → `{dom, hints}`. Strategy decision from results.
- **CLI**: `curl -sL -H "User-Agent: Mozilla/5.0" -o /tmp/ralhf-page.html -w "%{url_effective}" "<url>"`. Login redirect → Playwright. SPA → Playwright. Strip HTML, embedded JSON grep. curl fails → report failure to user.
- **Playwright**: follow `references/playwright-extract.md` exactly. Each step = separate Bash call.

Auth → wait (Chrome/Playwright) or suggest Playwright (CLI). SPA → re-strip or Playwright. Rate limit → tell user. >80K → focus `main`/`article`/`[role="main"]`.

---

## Phase 2 — Build Recipe (cold path)

**Two-strike limit**: two failures → stop, raw text, tell user.

- **`api_direct` / `api_intercept`**: Identify endpoint, method, headers, response structure. Map fields. Test via `javascript_tool`. Build recipe per `references/recipe-schema.md`.
- **`embedded_json`**: Identify blob source + selector + `json_path`. Map fields. Test. Build recipe.
- **`export_download`**: Identify trigger, format, interception. Map `source_key` per field. Build recipe.
- **`dom_css`**: Use Phase 1 hints. Selector stability: `data-testid` > `id` > `aria-label`/`role` > tag+class > positional. Content type → CSS selectors → pagination → recipe fields → context fingerprint (`references/context-fingerprint.md`) → validate (`references/recipe-schema.md`) → test (`javascript_tool`, >30% fail → strike) → extract.

---

## Phase 3a — Save, Extract & Render

### Cold — new domain

Auto-save. `mkdir -p skills/extract-{sanitized-domain}/views`. Write manifest, SKILL.md, view file using `references/templates.md`. Present data + footer.

### Cold — new view

Write view file → append to manifest → present data + footer.

### Warm — existing view

1. Read recipe from backend or local view file(s), note strategy. If recipe has `incremental`, read `schedule.json` from the project root for a matching entry's `watermark`.
2. Extract fresh data by strategy. **Never serve cached data — always extract from the live page.**
   - **If incremental mode is active** (see below), apply early-stop logic during extraction.
3. Validate: type check, list consistency (required empty >30% → fail), semantic spot-check.
4. Evaluate: all pass → present. >80% fail → raw text fallback. ≤30% required fail → repair. >30% → context comparison (match → repair, different file → switch+retry, no match → new variant `{view-id}--v{N}.md`).
5. Repair by strategy: dom → re-derive selectors. api → check schema. json → check structure. export → check trigger.
6. Auto-save. Present data. Footer: `Extracted from {domain} -- view {view-id} ({field_count} fields).`
   - Incremental: `Extracted {n} new records from {domain} -- view {view-id} (incremental, {field_count} fields).`

### Incremental mode (warm path)

Requires **both**: recipe has `incremental` AND a watermark exists. Either missing → full extraction. Watermark source: `schedule.json` in the project root (not the skill install directory — skill directories may be read-only).

**Flow:**

1. Parse each record's `time_field` using `date_format`.
2. Compare against watermark:
   - `desc` → stop when `time_field` ≤ watermark.
   - `asc` → skip records where `time_field` ≥ watermark.
3. **Boundary dedup**: include `time_field == watermark.value` UNLESS `id_field == watermark.record_id`. No `id_field` → hash dedup.
4. **Pagination early-stop**: all records on page at/past boundary → stop fetching.
5. Empty delta = `ok`, not an error.
6. After ingestion, update watermark in `schedule.json` in the project root. If no entry exists for this domain/view, auto-scheduling (see § Auto-schedule above) will have already created an enabled entry — just update its watermark. If for any reason no entry exists (e.g., auto-schedule was skipped due to error), create one with `enabled: true` using v2 entry format — include `cycles_between_runs` (computed from tick interval) and `last_run_tick: null`. If `schedule.json` doesn't exist, create it with v2 format (`version: 2`, `tick_interval_hours` computed from this entry's period, `tick_count: 0`, `last_tick_at: null`, `cowork_task_synced: false`).

**Per-strategy early-stop:**

| Strategy | Mechanism |
|---|---|
| `dom_css` | Stop scrolling/paginating when full page is past watermark |
| `api_direct` | Inject watermark as `since`/`after` param if supported; else post-filter + early-stop |
| `api_intercept` | Watermark comparison in `stop_condition`; stop triggering at boundary |
| `embedded_json` | Post-filter parsed array |
| `export_download` | Post-filter parsed rows |

**Fallbacks**: date parse failure → full extraction + warn.

**Presentation**: single record → key-value. List → markdown table. Complex → JSON.

### Auto-schedule (after successful extraction)

After presenting data (cold or warm path), automatically add the domain/view
to the extraction schedule. Do NOT ask the user — scheduling is automatic.

1. **Check schedule.json** — read from the project root. If missing, create
   with v2 format.

2. **Look up existing entry** — find by ID (`{sanitized-domain}--{view-id}`).
   - **Already enabled** → skip scheduling (already tracked). Update
     watermark if applicable.
   - **Exists but disabled** → enable it and proceed to step 3.
   - **Not found** → create new entry and proceed to step 3.

3. **Set frequency** — look up the domain in
   `references/domain-classification.md` to get its category, then read
   `references/schedule-frequency.md` for the default frequency. Use it
   directly — do not ask the user.

4. **Tick reasoning** — same logic as `ralhf-schedule` add step 5:
   - Get `period_hours` from `references/schedule-frequency.md`
     § Frequency-to-hours mapping.
   - Compute `tick_interval_hours = min(period_hours)` across all enabled
     entries including this one.
   - If tick changed or first entry: recompute all `cycles_between_runs`,
     reset `tick_count` to 0.
   - If unchanged: compute only this entry's cycles.

5. **Write entry** with v2 fields:
   ```json
   {
     "id": "{sanitized-domain}--{view-id}",
     "domain": "{bare-domain}",
     "url": "{full-url}",
     "view_id": "{view-id}",
     "frequency": "{frequency}",
     "cycles_between_runs": {computed},
     "enabled": true,
     "added_at": "{YYYY-MM-DD}",
     "last_run_tick": null,
     "last_run": null,
     "last_status": "never_run",
     "watermark": null
   }
   ```

6. **Auto-create/update platform scheduled task** (if available) — same
   logic as `ralhf-schedule` add step 6. First entry → create
   `ralhf-extractions` task. Tick changed → update interval. Unchanged →
   no action. If platform scheduled tasks are not available (Codex, CLI),
   set `cowork_task_synced: false` — `schedule.json` still tracks all
   state and the user invokes schedule-run manually.

7. **Spawn cadence verification agent** — launch a background verification
   agent (inline if background agents are unavailable) that reads
   `schedule.json` and validates it against `references/schedule-rubric.md`.
   The agent also validates that this specific entry's cadence matches its
   domain category default (see schedule-rubric.md § Cadence validation).
   Do not wait for it (if running in background).

8. **Footer addendum** — append to the extraction footer:
   > Scheduled ({frequency}), every {cycles_between_runs} tick(s).

---

## Phase 3b — Backend Sync (mandatory when credentials present)

> **NEVER include user identity in request bodies.** Do not add `user`,
> `user_email`, or `RALHF_USER_EMAIL` to JSON payloads. User identity
> comes from auth headers only.

Run these steps **after extraction, before verification**. Present results to the user immediately — do not wait for backend calls to complete. All calls use the curl template and auth headers from `references/backend-client.md`.

**Sync stack**: wrap each call with push/pop per `references/sync-stack.md`:
1. Write payload to `skills/ralhf-extract/.sync-payloads/{epoch}-{op}.json`
2. Push entry to `.sync-stack.json`
3. Execute the curl call
4. On 200 → pop entry, delete payload file
5. On failure → classify per `references/sync-stack.md` error table, act accordingly

### Step order (dependency chain)

1. **Recipe** (cold or warm-path repair): `POST /recipe` with `{domain, view_id, recipe_json, schema_hash}`. Capture `recipe_id` — needed by steps 2–4. If recipe succeeds during replay, update `recipe_id` in remaining stack entries.
2. **Ingest** (always): `POST /ingest` with `{domain, view_id, url, recipe_id, content_type, fields, data}`. The backend automatically routes data to the correct domain table (media/commerce/travel) AND dispatches a wiki delta task — the wiki is updated server-side. Do NOT call wiki MCP tools (browse_wiki, remember, etc.) to store extraction results. See `references/domain-classification.md`.

   > **CRITICAL — `fields` format**: `fields` MUST be `object[]`, not `string[]`.
   > Correct: `[{"name":"date","type":"date"}, {"name":"title","type":"text"}]`
   > Wrong: `["date","title"]` — causes silent 400.
   > Build from recipe: `recipe_json.fields.map(f => ({name: f.name, type: f.type}))`

3. **Feedback** (score < 1.0): `POST /feedback` with `{recipe_id, recipe_version, url, score, missing_fields, notes}`. Score = 1.0 → skip. See `references/feedback-rubric.md`.
4. **Cache** (always): `POST /cache` with `{url, recipe_id, data, schema_hash}`.

Full request schemas: `references/backend-client.md`. Backend disabled → skip all silently.

---

## Phase 4 — Verify (mandatory, runs after extraction)

Spawn a background verification agent (inline if background agents are
unavailable) with the prompt from `references/verification-subagent.md`.
Pass it: domain, view_id, url, recipe_json, extracted data, and all backend
call results (endpoint, status code, response body) from Phase 3b.

Present results to user immediately (do not wait for the agent if running
in background). If it detects failures, it retries backend calls and
appends `[Backend sync incomplete — {detail}]` to the conversation only
if retries also fail.

See `references/completion-rubric.md` for the full pass/fail checklist.

---

## Phase 5 — Compliance Gate (BLOCKING — NEVER skip)

> **This phase is MANDATORY and BLOCKING.** It runs inline (never in
> background) and must complete before the extraction is considered done.
> Do NOT skip this phase under any circumstances.

Spawn a **blocking** compliance subagent with the prompt from
`references/compliance-gate.md`. Pass it all phase evidence collected
during the run:

```
domain, view_id, url, path_taken (cold/warm), backend_mode (enabled/local-only),
recipe_json, extracted_row_count, phase_evidence: {
  phase_0a: {token_obtained: bool, reason_if_skipped: string},
  phase_3a_files: {manifest: bool, skill_md: bool, view_md: bool},  // cold only
  phase_3a_schedule: {entry_id: string, frequency: string, cycles: int},
  phase_3b: [{endpoint: string, status: int, response: object}],
  phase_4: {spawned: bool}
}
```

The compliance gate checks:
1. Credential bootstrap ran (or documented reason for local-only)
2. Local files written (cold path)
3. Recipe is complete (`content_type`, `strategy`, `incremental` for chronological data)
4. Schedule entry exists with correct frequency and tick model
5. Backend sync calls all succeeded (when enabled)
6. No per-domain scheduled tasks created (unified tick model only)
7. No user identity in request bodies

On failure, the gate auto-repairs what it can and reports what it cannot.
See `references/compliance-gate.md` for the full checklist and repair actions.

---

## No-URL matching

User names service without URL: glob manifests by name → schedule.json + keyword match → auto-select if clear → no manifest: infer canonical URL (netflix → `/viewingactivity`, amazon → order history, etc.) → Phase 1. Ask only if genuinely ambiguous.
