---
name: ralhf-schedule
description: >
  Manage scheduled extractions — add, remove, list, enable, and disable
  recurring data pulls. Auto-creates platform scheduled tasks when available.
user-invocable: false
---

# ralhf-schedule — Scheduled Extraction Manager

Manage recurring extractions that run automatically via platform scheduled
tasks (when available). Uses a unified tick model: one scheduled task fires
at the fastest entry's cadence, and slower entries fire every Nth tick.

## Commands

### `add <url>` (or "add netflix to my schedule")

1. **Parse the URL** — extract hostname, strip `www.`, compute bare domain
   and sanitized domain (same rules as ralhf-extract Phase 0). Compute
   view ID from the URL path.

2. **Verify recipe exists** — check for a manifest:
   ```bash
   ls skills/extract-{sanitized-domain}/manifest.json 2>/dev/null
   ```
   If no manifest exists, tell the user:
   > "No extraction recipe found for {domain}. Run `/ralhf-extract <url>`
   > first to create one, then add it to your schedule."
   Stop.

3. **Determine what to extract** — read the manifest's `views` array.
   If only one view, skip this step. If multiple views:

   a. **Auto-resolve via local context** — check `schedule.json` for
      existing entries on this domain (the user may already track some
      views). Match the user's request text against view labels using
      keyword overlap (e.g., "schedule my Netflix history" matches
      "Viewing History"). Auto-select if one view matches clearly.

   b. **Fallback to prompt** — if no signal from schedule or keywords and
      the request is generic ("add Netflix to my schedule"), ask the user
      to choose (allow multiple selections). List each view label as an
      option.

   Create one schedule entry per selected view.

4. **Set frequency** — check whether the user explicitly requested a
   frequency ("every hour", "hourly", "twice a week", "daily"). If so,
   map to the closest `frequency` value:
   - "every hour" / "hourly" → `hourly`
   - "every day" / "daily" → `daily`
   - "weekdays" / "weekdays only" → `weekdays`
   - "every week" / "weekly" → `weekly`
   - "every two weeks" / "biweekly" → `biweekly`
   - "every month" / "monthly" → `monthly`

   If no explicit request, look up the domain in
   `references/domain-classification.md` to get its category, then read
   `references/schedule-frequency.md` for the default frequency.

5. **Tick reasoning** — compute the new tick interval and cycles.

   Read `references/schedule-frequency.md` § Frequency-to-hours mapping to
   get the new entry's `period_hours`.

   a. Read existing `schedule.json` (or treat as empty if missing).
   b. Compute `new_tick_interval = min(period_hours)` across all enabled
      entries INCLUDING the new entry.
   c. **If tick interval changed** (or this is the first entry):
      - Recompute `cycles_between_runs` for every enabled entry:
        `period_hours / new_tick_interval`.
      - Reset `tick_count` to 0.
      - Set `cowork_task_synced` to `false` (will be synced in step 6).
   d. **If tick interval unchanged**:
      - Compute only the new entry's `cycles_between_runs`:
        `period_hours / tick_interval_hours`.

   Set the new entry's fields:
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

   If an entry with the same `id` already exists, update it instead of
   duplicating.

   Write `schedule.json` with the updated entries and top-level fields.

6. **Auto-create/update platform scheduled task** (if available) — manage
   the `ralhf-extractions` scheduled task automatically.

   If platform scheduled tasks are available (Cowork):
   - **First entry** (no prior entries existed): create a scheduled task
     named `ralhf-extractions` with interval = `tick_interval_hours` hours
     and prompt to run the schedule-run skill.
   - **Tick interval changed**: update the existing task's interval to
     match the new `tick_interval_hours`.
   - **Tick interval unchanged**: no action needed — existing task is
     already correct.
   - After successful create/update, set `cowork_task_synced: true`.

   If platform scheduled tasks are not available (Codex, CLI):
   - Set `cowork_task_synced: false`.
   - `schedule.json` still tracks all state and tick counts.
   - The user invokes schedule-run manually or via platform automations.

7. **Check auth requirement** — read `requires_auth` from the manifest.
   If `true`, add `"requires_auth": true` to the schedule entry and warn:
   > "Note: {domain} requires login. Scheduled runs will use your existing
   > browser session. If your session expires, the extraction will be
   > skipped until you log in again."

8. **Spawn schedule verification agent** — launch a background verification
   agent (inline if background agents are unavailable) that reads
   `schedule.json` and validates it against `references/schedule-rubric.md`.
   The agent auto-repairs any inconsistencies. Do not wait for it (if
   running in background).

9. **Confirm**:
   > "Added {domain} ({view-id}) to your extraction schedule ({frequency}),
   > every {cycles_between_runs} tick(s). Tick interval: {tick_interval_hours}h."

### `list`

1. Read `schedule.json`. If missing or empty:
   > "No scheduled extractions configured. Use `/ralhf-schedule add <url>`
   > to add one."

2. Auto-migrate v1→v2 if needed (see migration section below).

3. Display as a markdown table:

   | Domain | View | Frequency | Cycle | Tick Interval | Last Run | Status | Enabled |
   |---|---|---|---|---|---|---|---|
   | {domain} | {view_id} | {frequency} | {cycles_between_runs} | {tick_interval_hours}h | {last_run or "never"} | {last_status} | {enabled ? "yes" : "no"} |

   The Tick Interval column is the same for all rows (global value). The
   Cycle column shows how many ticks between runs for that entry.

   Omit `enabled: false` entries unless `--all` is passed.

### `remove <domain>`

1. Read `schedule.json`.
2. Match entries by domain (fuzzy — `netflix` matches `netflix.com`).
3. If multiple matches, show them and ask the user to pick.
4. Remove the matched entry.

4a. **Map domain to provider** — look up the removed entry's `domain` in
    `references/domain-classification.md` to get the `Provider` column value
    (e.g., `netflix.com` → `NETFLIX`). If the domain is not found in the
    classification table → skip step 4b (unclassified domains never create
    source-connections).

4b. **Disconnect from backend** — remove the source-connection so the
    website reflects the removal.

    1. Read credentials from `skills/ralhf-extract/.env` and `config.json`.
       If no credentials are present → skip (local-only mode).

    2. **Multi-view guard** — check whether other enabled entries in
       `schedule.json` map to the same provider (e.g., two Amazon views
       both map to `AMAZON_USA`). Look up each remaining enabled entry's
       domain in `references/domain-classification.md`. If any remaining
       entry maps to the same provider → skip DELETE (the connection is
       still needed for the other entry).

    3. Call:
       ```bash
       curl -s -X DELETE "{backend_url}/source-connection" \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer {RALHF_MCP_TOKEN}" \
         -d '{"source_name": "{PROVIDER}"}'
       ```
       Use legacy auth headers if bearer token is not available (same
       selection logic as `references/backend-client.md` § Auth selection).

    4. Handle response:
       - **200** (success) or **404** (already disconnected): continue.
       - **401/403**: warn user about expired credentials, switch to
         local-only for the rest of the session. Continue with removal.
       - **Other failure** (transient): push to the sync stack with
         `op: "disconnect"` (see `references/sync-stack.md` § Disconnect
         operation). Continue with removal.

5. **Recalculate tick interval** from remaining enabled entries:
   - If enabled entries remain:
     - `new_tick_interval = min(period_hours)` across remaining enabled.
     - **If tick changed**: recompute all `cycles_between_runs`, reset
       `tick_count` to 0, update platform scheduled task (if available).
     - **If unchanged**: no recalculation needed.
   - If no enabled entries remain (schedule empty or all disabled):
     - Set `tick_interval_hours` to `null`, `tick_count` to 0.
     - Pause or delete the `ralhf-extractions` scheduled task (if available).
6. Write updated `schedule.json`.
7. **Spawn schedule verification agent** (background; inline if unavailable).
8. Confirm:
   - If schedule empty and backend disconnected:
     > "Removed {domain} ({view_id}) and disconnected {PROVIDER} from
     > backend. Schedule is empty. The 'ralhf-extractions' scheduled task
     > has been paused."
   - If schedule empty, no disconnect (skipped or local-only):
     > "Schedule is empty. The 'ralhf-extractions' scheduled task has been
     > paused."
   - If entries remain and backend disconnected:
     > "Removed {domain} ({view_id}) and disconnected {PROVIDER} from
     > backend. Tick interval: {tick_interval_hours}h."
   - If entries remain, disconnect skipped (multi-view guard):
     > "Removed {domain} ({view_id}). Other {PROVIDER} views remain —
     > backend connection kept. Tick interval: {tick_interval_hours}h."
   - If entries remain, disconnect queued (transient failure):
     > "Removed {domain} ({view_id}). Backend disconnect queued for retry.
     > Tick interval: {tick_interval_hours}h."
   - If entries remain, no disconnect (local-only or unclassified):
     > "Removed {domain} ({view_id}). Tick interval: {tick_interval_hours}h."

### `enable <domain>` / `disable <domain>`

1. Read `schedule.json`.
2. Match entries by domain (fuzzy).
3. Toggle the `enabled` field.
4. **Recalculate tick interval** — same logic as `remove`:
   - Compute `new_tick_interval = min(period_hours)` across all enabled
     entries after the toggle.
   - If tick changed: recompute all cycles, reset `tick_count`, update
     platform scheduled task (if available).
   - If no enabled entries remain: set `tick_interval_hours` to `null`,
     `tick_count` to 0, pause scheduled task (if available).
   - Disabled entries get `cycles_between_runs: null`.
   - Re-enabled entries get `cycles_between_runs` recomputed.
5. Write updated `schedule.json`.
6. **Spawn schedule verification subagent** (background).
7. Confirm:
   > "{domain} ({view_id}) is now {enabled/disabled}. Tick interval:
   > {tick_interval_hours}h."

## schedule.json v2 format

Located in the **project root** (the connected workspace folder), not the
skill install directory. Skill directories may be read-only. Created at
runtime. Gitignored.

Entries are created automatically by `/ralhf-extract` after successful
extraction (`enabled: true`, auto-scheduled) or by `/ralhf-schedule add`.
Both paths create enabled entries with tick reasoning. Users can disable
entries via `/ralhf-schedule disable`. `/ralhf-schedule list` should omit
`enabled: false` entries unless `--all` is passed.

```json
{
  "version": 2,
  "tick_interval_hours": 1,
  "tick_count": 0,
  "last_tick_at": null,
  "cowork_task_synced": true,
  "entries": [
    {
      "id": "amazon-com--order-history",
      "domain": "amazon.com",
      "url": "https://www.amazon.com/gp/css/order-history",
      "view_id": "order-history",
      "frequency": "hourly",
      "cycles_between_runs": 1,
      "enabled": true,
      "added_at": "2026-05-26",
      "last_run_tick": null,
      "last_run": null,
      "last_status": "never_run",
      "watermark": null
    }
  ]
}
```

### Top-level fields

| Field | Type | Description |
|---|---|---|
| `version` | number | Schema version. Always `2`. |
| `tick_interval_hours` | number or null | Hours between ticks. `null` when no enabled entries. |
| `tick_count` | number | Current tick counter. Incremented by `ralhf-schedule-run`. |
| `last_tick_at` | string or null | ISO timestamp of last tick. |
| `cowork_task_synced` | boolean | Whether the platform scheduled task interval matches `tick_interval_hours`. |

### Entry fields

| Field | Type | Description |
|---|---|---|
| `id` | string | `{sanitized-domain}--{view-id}`. Unique. |
| `domain` | string | Bare domain (e.g., `amazon.com`). |
| `url` | string | Full URL for extraction. |
| `view_id` | string | View identifier from the URL path. |
| `frequency` | string | One of: `hourly`, `daily`, `weekdays`, `weekly`, `biweekly`, `monthly`. |
| `cycles_between_runs` | number or null | Ticks between runs. `null` for disabled entries. |
| `enabled` | boolean | Whether this entry is picked up by scheduled runs. |
| `added_at` | string | Date added (`YYYY-MM-DD`). |
| `last_run_tick` | number or null | Tick count at last successful run. |
| `last_run` | string or null | Date of last run (`YYYY-MM-DD`), for readability. |
| `last_status` | string | `never_run`, `ok`, `partial`, `auth_needed`, or `error`. |
| `watermark` | object or null | Incremental extraction position. |

### Watermark format

```json
{
  "watermark": {
    "value": "{newest record's time_field value}",
    "field": "{time_field name}",
    "record_id": "{id_field value, or null}",
    "updated_at": "{YYYY-MM-DD}"
  }
}
```

## v1 → v2 migration

Auto-migrate on read. When `schedule.json` has `"version": 1` (or no
`version` field):

1. Compute `tick_interval_hours` from enabled entries:
   - Map each enabled entry's `frequency` to `period_hours` using
     `references/schedule-frequency.md` § Frequency-to-hours mapping.
   - `tick_interval_hours = min(period_hours)`. No enabled entries → `null`.

2. Compute `cycles_between_runs` for each enabled entry:
   - `period_hours / tick_interval_hours`. Disabled entries → `null`.

3. Add missing fields to each entry:
   - `cycles_between_runs`: computed above.
   - `last_run_tick`: `null`.

4. Add top-level fields:
   - `tick_interval_hours`: computed above.
   - `tick_count`: `0`.
   - `last_tick_at`: `null`.
   - `cowork_task_synced`: `false`.

5. Set `version` to `2`.

6. Write the migrated `schedule.json`.

7. Log: `[Schedule migrated from v1 to v2 — tick interval: {tick_interval_hours}h]`

## Error handling

- If `schedule.json` is malformed, warn the user and offer to reset it.
- If a recipe was deleted after being scheduled, `remove` still works.
  `/ralhf-schedule-run` will skip entries with missing recipes and set
  `last_status: "error"`.
