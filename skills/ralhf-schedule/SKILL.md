---
name: ralhf-schedule
description: >
  Manage scheduled extractions — add, remove, list, enable, and disable
  recurring data pulls. Auto-creates platform scheduled tasks when available.
user-invocable: false
---

# ralhf-schedule — Scheduled Extraction Manager

Recurring extractions on a unified tick model: one platform scheduled task
fires at the fastest entry's cadence; slower entries fire every Nth tick.

All schedule state lives in `schedule.json` — resolved automatically:
`$RALHF_PROJECT_ROOT` if set, else an existing `schedule.json` in the cwd,
else the cwd when writable, else `~/.config/ralhf/` (read-only cwds are
normal in plugin installs). It is owned by
`ralhf_schedule.py` in the **ralhf-extract** skill's `scripts/` directory
(a sibling of this skill — glob `**/ralhf-extract/scripts/ralhf_schedule.py`
if unsure). The script does the tick math, v1→v2 migration, validation, and
backend mirroring. Never
edit schedule.json by hand. Run the backend bootstrap first if this session
hasn't yet: `python3 {scripts}/ralhf_client.py bootstrap` (mint via the
`get_api_key` MCP tool if it says `need_mint`).

Every mutating command prints JSON. Two parts always need **your** action:

- **`platform_task`** — `create` → create the `ralhf-extractions` platform
  scheduled task at `interval_hours` with prompt `/ralhf-schedule-run`;
  `update` → update the existing task's interval (NEVER recreate an
  existing task); `pause_or_delete` → pause it. No platform task support
  (CLI/Codex) → ignore.
- **`ambiguous`** (exit code 2) — multiple entries matched; show them and
  re-run with `--id <entry-id>` once the user picks.

## Commands

### add — "add netflix to my schedule"

Before adding, verify a recipe exists:
`ls skills/extract-{sanitized-domain}/manifest.json`. None → tell the user
to run `/ralhf-extract <url>` first; stop. Multiple views in the manifest →
match the user's wording against view labels; ask only when genuinely
ambiguous (multi-select allowed, one entry per chosen view).

```
python3 {scripts}/ralhf_schedule.py add --url <url> [--view-id <v>] \
  --frequency hourly|daily|weekdays|weekly|biweekly|monthly \
  [--provider <NAME>] [--requires-auth]
```

`--frequency` and `--provider` are your judgment calls, made from
`ralhf-extract/references/domain-classification.md`: an explicit user
request wins ("every hour" → `hourly`, "twice a week" → closest value);
otherwise use the category default (classify unlisted domains by analogy;
never auto-pick hourly). Pass `--provider` when the domain maps to a
backend source-connection — it's stored on the entry so `remove` can
disconnect later. Pass `--requires-auth` when the manifest says so, and
warn:
> "Note: {domain} requires login. Scheduled runs use your existing browser
> session; if it expires, the extraction is skipped until you log in again."

Confirm from the output:
> "Added {domain} ({view_id}) to your extraction schedule ({frequency}),
> every {cycles_between_runs} tick(s). Tick interval: {tick_interval_hours}h."

### list

```
python3 {scripts}/ralhf_schedule.py show [--all]
```

Render as a table: Domain | View | Frequency | Cycle | Tick Interval |
Last Run | Status | Enabled. Disabled entries only with `--all`. Empty →
> "No scheduled extractions configured. Use `/ralhf-schedule add <url>`."

### remove / enable / disable

```
python3 {scripts}/ralhf_schedule.py remove|enable|disable --domain <d> \
  [--id <entry-id>] [--provider <NAME>]   # --provider: remove only
```

`remove` also handles the backend source disconnect (multi-view guard,
404-is-success, transient → queued for replay) using the provider recorded
on the entry; for older entries without one, judge the provider from
`domain-classification.md` and pass `--provider`. Report the `disconnect`
part of the output: disconnected / kept (other views remain) / queued /
skipped (no provider). Then act on `platform_task` and confirm with the
new tick interval (or "schedule is empty — task paused").

## Notes

- Both `/ralhf-extract` (auto-schedule via `ensure`) and `add` create
  enabled entries; users opt out with `disable`.
- The script validates and auto-repairs the tick model on every write and
  pushes the full schedule to the backend (sync-stack wrapped, silent on
  failure, skipped when the backend lacks schedule sync). No verification
  subagent is needed.
- Malformed `schedule.json` → the script exits with an error; warn the
  user and offer to reset it.
