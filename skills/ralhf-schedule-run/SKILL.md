---
name: ralhf-schedule-run
description: >
  Execute all enabled scheduled extractions and cache results.
  Designed to be invoked by the platform scheduler, automation, or manually.
user-invocable: false
allowed_tools:
  # Claude/Cowork: mcp__Claude_in_Chrome__* tools
  # Codex: uses Chrome extension tools (navigate, click, type, screenshot)
  - mcp__Claude_in_Chrome__navigate
  - mcp__Claude_in_Chrome__read_page
  - mcp__Claude_in_Chrome__click
  - mcp__Claude_in_Chrome__find_in_page
  - mcp__Claude_in_Chrome__javascript_tool
  - mcp__Claude_in_Chrome__get_page_text
---

# ralhf-schedule-run — Scheduled Extraction Executor

> **Internal skill.** Invoked by the platform scheduler, automation, or
> manually. Not meant to be called directly by users.
> Users manage their schedule via the schedule skill.

Runs all enabled scheduled extractions using tick-based scheduling
and caches results via the backend.

## Invocation

Called automatically by the platform scheduler or manually. Supports an optional
`--frequency` flag to filter entries:
```
Run /ralhf-schedule-run --frequency daily
```
Without the flag, all enabled entries that are due on this tick run.

## Flow

### Step 1 — Load schedule and reconcile sources

> **MANDATORY**: Execute **Phase A** (reconciliation) BEFORE **Phase B**
> (empty check). Do NOT skip or reorder these phases.

#### Phase A — Reconcile with backend sources

Reconcile the local schedule with the user's connected sources on the
backend. This is two-directional:
- **Prune** — drop entries for sources the user removed on the website.
- **Import** — add entries for sources the user added on the website (the
  reverse flow: website → your sources → Claude picks it up here).

1. **Read credentials** from `skills/ralhf-extract/.env`, `~/.config/ralhf/.env`,
   and `config.json`.

   No credentials present → **attempt auto-mint** before giving up:
   run the same credential bootstrap as `ralhf-extract/SKILL.md` § Phase 0a
   (read `backend_url` from `config.json`, call `mcp__ralhf_mcp__get_api_key`
   with `ttl_hours=720, name="ralhf-extract-auto"`, persist to
   `~/.config/ralhf/.env` or `skills/ralhf-extract/.env`).

   Auto-mint succeeds → use the new token, proceed to step 2.
   Auto-mint fails (no MCP server, tool unavailable, or mint error) AND
   no legacy credentials → skip to Phase B.

2. **Fetch connected sources** — call:
   ```bash
   curl -s -X GET "{backend_url}/source-connection" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer {RALHF_MCP_TOKEN}"
   ```
   Use legacy auth headers if bearer token is not available (same selection
   logic as `references/backend-client.md` § Auth selection).

   On failure or timeout → log warning, skip reconciliation. Proceed to
   Phase B. Do not block extractions.

3. **Build connected domain set** — from the response's `datasources[]`
   array, collect the `domain` field of each entry into a set of connected
   domains.

4. **Mark entries for removal** — read `schedule.json` (create empty if
   missing). For each schedule entry where `last_status` is `"ok"` or
   `"partial"`:
   - **Protected entries:** Skip entries with `last_status` of
     `"never_run"`, `"error"`, or `"auth_needed"` — they may not have
     synced to the backend yet.
   - **Website-sourced entries** (`source` is `"website"`): check the
     entry's `domain` directly against the connected domain set. If the
     domain is NOT in the connected set → mark for removal. (No
     `domain-classification.md` lookup needed — these entries came from
     the backend, so the connected set is authoritative.)
   - **Locally-added entries** (no `source` field or `source` is not
     `"website"`): look up the entry's `domain` in
     `references/domain-classification.md` to get its `Provider`. If not
     found → skip (unclassified locally-added domains have no
     source-connection). If the entry's `domain` is NOT in the connected
     domain set → mark for removal.

5. **Remove marked entries.** If any entries were removed:
   - Recalculate tick interval from remaining enabled entries (same logic
     as the remove command step 5 in `ralhf-schedule/SKILL.md`).
   - Write `schedule.json`.
   - Log: `[Reconciliation: removed {count} entries: {domains}]`

6. **Import newly-connected sources.** Using the same `datasources[]`
   response already fetched, for each connected source with a **non-empty
   `domain`** that has **no matching `schedule.json` entry** (compare bare
   domain, `www.` stripped, lowercased), create a new entry:

   a. **Resolve frequency** for the source:
      - If the source's `default_extraction_frequency` (days) is set,
        convert to hours (`days × 24`) and pick the closest `frequency`
        from `references/schedule-frequency.md` § Frequency-to-hours mapping
        (never pick `hourly` from this path).
      - Else, look up the bare domain's category in
        `references/domain-classification.md` and use the category default
        from `references/schedule-frequency.md`.
      - Else, fall back to `weekly`.

   b. **Create the entry** (extraction target is the domain only — the
      cold path resolves the specific page(s) on first run):
      ```json
      {
        "id": "{sanitized-domain}--index",
        "domain": "{bare-domain}",
        "url": "https://{bare-domain}/",
        "view_id": "index",
        "frequency": "{resolved frequency}",
        "cycles_between_runs": {computed},
        "enabled": true,
        "added_at": "{today YYYY-MM-DD}",
        "last_run_tick": null,
        "last_run": null,
        "last_status": "never_run",
        "source": "website",
        "watermark": null
      }
      ```
      (`{sanitized-domain}` = bare domain with non-alphanumerics replaced by
      `-`, same rule as ralhf-extract Phase 0.)

   c. **Recompute ticks** — after adding all imported entries, recompute
      `tick_interval_hours` and `cycles_between_runs` across all enabled
      entries using the same tick logic as `ralhf-schedule/SKILL.md` add
      steps 5–6. Create or update the `ralhf-extractions` scheduled task to the
      new interval. **Reset `tick_count` to 0 if the interval changed** —
      this also makes the new imports due on the next tick.

   d. Write `schedule.json`.

   e. Log: `[Reconciliation: imported {count} sources from website: {domains}]`

#### Phase B — Load schedule

Read `schedule.json` from the project root (not the skill install directory).

If missing or empty **and Phase A did not import any entries**:
> "No scheduled extractions configured. Use `/ralhf-schedule add <url>`
> to set one up."
Stop.

Proceed to Step 2.

### Step 2 — Tick and filter (tick-based scheduling)

1. **Auto-migrate v1→v2** — if `schedule.json` has `"version": 1` (or no
   `version` field), run the migration described in
   `ralhf-schedule/SKILL.md` § v1→v2 migration before proceeding.

2. **Increment tick** — add 1 to `tick_count` and set `last_tick_at` to
   the current ISO timestamp.

3. **Persist immediately** — write the updated `tick_count` and
   `last_tick_at` to `schedule.json` now, before executing any
   extractions. This ensures the counter survives crashes.

4. **Filter due entries** — from enabled entries, select those where:
   ```
   last_status == "never_run"  OR  tick_count % cycles_between_runs == 0
   ```
   Entries with `last_status: "never_run"` are **always due** regardless of
   the modulo — their first extraction runs on the first tick after import.
   This ensures newly connected sources are extracted immediately, not
   deferred to a future tick alignment.

5. **Weekday filter** — for entries with `frequency: "weekdays"`, check
   today's day of the week. If Saturday or Sunday, remove from the due
   list. The skip does not count as a run — the entry will fire on the
   next weekday tick where the modulo condition holds.

6. **Optional frequency filter** — if `--frequency` flag is provided,
   further filter to entries where `frequency` matches the flag value.

7. If no entries remain after filtering:
   > "Tick {tick_count} — no enabled extractions are due."
   Stop.

### Step 3 — Execute extractions

For each entry **sequentially**:

1. **Check auth requirement** — read `skills/extract-{sanitized-domain}/manifest.json`.
   If missing:
   - **Cold-author the recipe.** Invoke `/ralhf-extract {url}` — the cold
     path authors a recipe via intent resolution (wiki-intent / page
     discovery). This is the normal path for sources imported from the
     website (Phase A), which arrive without a recipe.
     - Respect the **two-strike limit** in `ralhf-extract/SKILL.md`: if the
       cold path fails to produce a recipe, set `last_status: "error"`,
       `last_run` to today, `last_run_tick` to `tick_count`, and skip to the
       next entry.
     - If the cold path hits an auth wall, set `last_status: "auth_needed"`
       and skip to the next entry (unattended run — do not prompt for login).
     - On success, the cold path's Phase 3a auto-schedule updates this
       entry's `frequency`/`view_id` to the authored recipe, keeping the
       schedule consistent. The extraction performed by the cold path counts
       as this entry's run — set `last_status`/`last_run`/`last_run_tick`
       from its result and continue to the next entry.

   If `requires_auth: true` in the manifest:
   - Check whether an active browser session exists (platform browser with
     valid cookies). If no active session or cookies are expired:
     - Set `last_status: "auth_needed"`, `last_run` to today,
       `last_run_tick` to `tick_count`.
     - Skip to next entry. Do NOT prompt for login — this is an
       unattended scheduled run; the user may not be present.

2. **Run extraction** — invoke `/ralhf-extract {url}`. This follows the
   silent background flow. Capture the extracted data from the output.
   - If extraction hits an auth wall at runtime (even if manifest didn't
     flag it), set `last_status: "auth_needed"` and skip to next entry.

2a. **Pass incremental context** — if entry has non-null `watermark` AND
   recipe has `incremental`, add to the invocation prompt:
   > "Incremental mode: extract only records newer than {watermark.value}
   > on field {watermark.field}. Stop when you reach this boundary."
   Otherwise → full extraction.

3. **Update schedule.json** — set `last_run` to today's date
   (`YYYY-MM-DD`), `last_run_tick` to `tick_count`, and `last_status`
   to the appropriate value:
   - `"ok"` — extraction succeeded
   - `"partial"` — extraction succeeded but backend cache failed
   - `"auth_needed"` — skipped because login was required and no session
   - `"error"` — extraction failed

3a. **Update watermark** — on `ok` status, if recipe has `incremental`:
   set `watermark` to newest record's `time_field`/`id_field` and today's
   date. Empty delta → watermark unchanged, status still `ok`.

### Step 4 — Summary

Present a summary table with tick info:

> Tick {tick_count} (interval: {tick_interval_hours}h)

| Domain | View | Cycle | Status | Records | Watermark |
|---|---|---|---|---|---|
| {domain} | {view_id} | {cycles_between_runs} | {ok/partial/auth_needed/error} | {count or "—"} | {watermark.value or "—"} |

The Cycle column shows each entry's `cycles_between_runs` value. Include
the Watermark column when any entry in the run uses incremental mode.
Omit it when no entries have incremental recipes (keep the table compact).

If any entries have `auth_needed` status, append:
> "Some extractions were skipped because they require login. Run
> `/ralhf-schedule-run` manually when you're at your computer to
> complete them."

### Step 5 — Backend sync

> **NEVER include user identity in request bodies.** Do not add `user`,
> `user_email`, or `RALHF_USER_EMAIL` to JSON payloads. User identity
> comes from auth headers only.

If backend is enabled (`RALHF_MCP_TOKEN` is set, or legacy
`RALHF_EXTRACT_KEY` + `RALHF_USER_EMAIL` are set), cache extracted data
via the backend. Auth selection follows `references/backend-client.md`
§ Auth selection — bearer token (`RALHF_MCP_TOKEN`) is preferred over
legacy keys. Failures are silent.

## Tick-based scheduling

A single platform scheduled task (`ralhf-extractions`) fires at
`tick_interval_hours` — the minimum period across all enabled entries.
On each invocation, Step 2 increments the tick counter and checks each
enabled entry's `cycles_between_runs` to determine whether it fires.

The tick model replaces the old date-based frequency gating. Instead of
comparing `last_run` against a minimum gap, entries fire deterministically
based on the tick counter modulo their cycle count. This enables sub-daily
frequencies (hourly) and ensures a unified cadence across all entries.

See `references/schedule-frequency.md` § Unified tick model for the full
specification.

The `--frequency` flag is optional — it further filters to only entries
matching the specified frequency, after tick-based filtering.

## Auth-gated sites and unattended runs

Scheduled tasks fire automatically — the user may not be at their computer.
Auth-gated sites (LinkedIn, Netflix, etc.) need an active browser session
with valid cookies. When running unattended:

- If the manifest says `requires_auth: true` and no active browser session
  is detected, the entry is **skipped** with status `auth_needed`.
- If extraction hits a login wall at runtime, same behavior — skip, don't
  block waiting for a login that won't happen.
- The summary table calls out `auth_needed` entries and suggests a manual
  run when the user is present.

Session cookies from the platform browser persist across runs (same browser
profile). Once the user logs in during any extraction, subsequent scheduled
runs reuse that session until it expires.

## Error handling

- Missing recipe → cold-author via `/ralhf-extract {url}`. Only set status
  to `error` if the cold path fails to produce a recipe (two-strike limit).
- Auth required + no session → skip entry, set status to `auth_needed`.
- Extraction failure → set status to `error`, continue to next entry.
- Backend cache failure → set status to `partial`, continue.
- All entries error → still present the summary table showing failures.
- `schedule.json` malformed → warn and stop.
