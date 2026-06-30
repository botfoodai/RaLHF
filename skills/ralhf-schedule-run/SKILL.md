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
> manually — not by users. Users manage their schedule via ralhf-schedule.

Runs due extractions on the unified tick model. All mechanical steps go
through the ralhf-extract skill's scripts (`{scripts}` =
`**/ralhf-extract/scripts/`, run with `python3`). Optional
`--frequency <f>` flag filters due entries.

## Flow

### Step 1 — Bootstrap + reconcile

```
python3 {scripts}/ralhf_client.py bootstrap
python3 {scripts}/ralhf_schedule.py reconcile
```

Bootstrap says `need_mint: true` → call the MCP tool ending in
`get_api_key` (`ttl_hours=24` — the backend max — `name="ralhf-extract-auto"`)
and re-run with
`--token`. Unavailable → continue local-only (reconcile is skipped
automatically).

`reconcile` is two-directional and fully scripted: pulls the backend
schedule (fresh-machine adopt or merge-by-id, local wins), prunes entries
whose source was disconnected on the website (never-run/error/auth_needed
entries are protected; only entries with a recorded `provider` or
`source: website` are prunable), and imports newly connected sources as
`never_run` entries (cadence from the source's own hint, else `weekly`).
For imported entries, review the cadence with your judgment
(`ralhf-extract/references/domain-classification.md` § Default cadence) and
adjust obviously-wrong ones via `add --frequency` (same id = update). Act
on its `platform_task` output (create/update/pause the `ralhf-extractions`
task — never recreate an existing one). Report its `log` lines if any.

### Step 2 — Tick

```
python3 {scripts}/ralhf_schedule.py tick [--frequency <f>]
```

Increments and persists the tick counter (crash-safe), applies the
modulo/weekday/never-run rules, and returns the `due` entries. Empty `due`
→ report "Tick {tick_count} — no enabled extractions are due." and stop.

### Step 3 — Execute each due entry (sequentially)

1. **No manifest** (`skills/extract-{sanitized-domain}/manifest.json`
   missing — normal for website-imported sources) → cold-author by
   invoking `/ralhf-extract {url}`. Two-strike failure → record `error`;
   auth wall → record `auth_needed`. Success counts as this entry's run.
2. **`requires_auth: true`** and no active browser session → record
   `auth_needed` and skip. Unattended runs NEVER prompt for login; session
   cookies from prior logins are reused until they expire.
3. Otherwise invoke `/ralhf-extract {url}` (silent flow). The extract skill
   handles incremental/watermark logic per partition itself.
4. Record the outcome (also updates watermarks and mirrors to the backend):

```
python3 {scripts}/ralhf_schedule.py record-run --id {entry-id} \
  --status ok|partial|auth_needed|error \
  [--watermark '{"partition":"{pid}","value":"...","field":"...","record_id":"..."}']...
```

Statuses: `ok` extraction succeeded · `partial` extraction ok, backend
sync incomplete · `auth_needed` login required, no session · `error`
extraction failed. One failure never stops the loop — continue to the
next entry.

### Step 4 — Summary

> Tick {tick_count} (interval: {tick_interval_hours}h)

| Domain | View | Cycle | Status | Records | Watermark |
|---|---|---|---|---|---|

Include the Watermark column only when an entry ran incrementally (show the
newest partition's value). Any `auth_needed` → append:
> "Some extractions were skipped because they require login. Run
> `/ralhf-schedule-run` manually when you're at your computer."

### Step 5 — Final sync

```
python3 {scripts}/ralhf_schedule.py sync
```

Pushes the final schedule state (tick counter, statuses, watermarks).
Failures are silent — transient errors stay queued on the sync stack and
replay on the next bootstrap.

## Error handling

- All entries failing → still present the summary table.
- Malformed `schedule.json` → the scripts exit with an error; warn and stop.
