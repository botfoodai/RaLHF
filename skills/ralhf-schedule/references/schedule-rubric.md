# Schedule Verification Rubric

Verification checks for the schedule consistency subagent. Spawned in the
background after any schedule mutation (add, remove, enable, disable).

## Inputs

The subagent receives the path to `schedule.json` and reads it directly.

## Checks

Run all seven checks. Report the first failure found and auto-repair.

| # | Check | Pass condition |
|---|---|---|
| 1 | Tick interval correct | `tick_interval_hours` equals `min(period_hours)` across all enabled entries. If no enabled entries, `tick_interval_hours` is `null`. |
| 2 | Cycles correct | Each enabled entry's `cycles_between_runs` equals `period_hours / tick_interval_hours` (integer division, exact). Disabled entries have `cycles_between_runs: null`. |
| 3 | No fractional cycles | All enabled entries have `cycles_between_runs >= 1` and the value is an integer (no remainder in the division). |
| 4 | Unique IDs | No duplicate `id` values across all entries (enabled and disabled). |
| 5 | Tick count consistent | `tick_count` is a non-negative integer. If `tick_interval_hours` is `null` (no enabled entries), `tick_count` is 0. |
| 6 | Cowork task matches | The Cowork scheduled task `ralhf-extractions` has an interval matching `tick_interval_hours`. If `tick_interval_hours` is `null`, the task should be paused or absent. |
| 7 | Cadence valid | Each entry's `frequency` matches the expected default for its domain category (per `references/domain-classification.md` → `references/schedule-frequency.md`). User-overridden frequencies are exempt — skip this check if the entry was added with an explicit user frequency. |

## Frequency-to-hours reference

| Frequency | Period (hours) |
|-----------|----------------|
| hourly | 1 |
| daily | 24 |
| weekdays | 24 |
| weekly | 168 |
| biweekly | 336 |
| monthly | 720 |

## Fail action

On any check failure:

1. Auto-repair `schedule.json`:
   - Check 1: recompute `tick_interval_hours` from enabled entries.
   - Check 2: recompute `cycles_between_runs` for all enabled entries.
   - Check 3: same as check 2 (recompute cycles).
   - Check 4: deduplicate by keeping the most recent entry (latest `added_at`).
   - Check 5: reset `tick_count` to 0.
   - Check 6: update or create the Cowork task with the correct interval.
   - Check 7: update entry's `frequency` to the domain category default
     and recompute `cycles_between_runs`. Log the mismatch.

2. Write repaired `schedule.json`.

3. Log: `[Schedule repaired — {detail}]` where `{detail}` describes the
   fix (e.g., "tick_interval recalculated from 24h to 1h",
   "duplicate ID netflix-com--viewing-activity removed",
   "tick_count reset to 0").

## Pass action

All checks pass → no output. Silent success.
