# Schedule Frequency

Default extraction frequencies by domain category. Used by `ralhf-schedule`
to auto-suggest when adding a new entry.

## Defaults by category

| Category | Frequency | Rationale |
|----------|-----------|-----------|
| Media (video) | monthly | Watch history changes slowly |
| Media (audio) | weekly | Listening accumulates faster |
| Commerce (food delivery) | weekly | Regular ordering pattern |
| Commerce (grocery) | weekly | Weekly shops |
| Commerce (general retail) | monthly | Infrequent purchases |
| Travel (rideshare) | weekly | Frequent use |
| Travel (flights/hotels) | monthly | Infrequent bookings |
| Travel (activities) | monthly | Infrequent bookings |
| Uncategorized | weekly | Safe default |

## Lookup

Match domain against `references/domain-classification.md` to get category.
Use `media_category`, `activity_type`, or domain type to select the row
above. If no match, use `weekly`.

## Frequency values

`hourly` · `daily` · `weekdays` · `weekly` · `biweekly` · `monthly`

`hourly` is not auto-suggested. It is only used when the user explicitly
requests it (e.g., "check every hour", "hourly extractions").

## Frequency-to-hours mapping

Each frequency maps to a period in hours, used by the unified tick model:

| Frequency | Period (hours) |
|-----------|----------------|
| hourly | 1 |
| daily | 24 |
| weekdays | 24 |
| weekly | 168 |
| biweekly | 336 |
| monthly | 720 |

`weekdays` has the same period as `daily` (24h) but skips Saturday and
Sunday at runtime — the skip does not count as a run.

## Unified tick model

The scheduling system uses a single repeating tick to drive all entries.
Instead of each entry independently checking its `last_run` date, a shared
tick counter determines when entries fire.

### Tick interval

```
tick_interval_hours = min(period_hours) across all enabled entries
```

The Cowork scheduled task fires at this interval. Entries with longer
periods fire every Nth tick.

### Cycles between runs

```
cycles_between_runs = entry_period_hours / tick_interval_hours
```

This must always be a positive integer (>= 1). The tick interval is chosen
as the minimum period, so all other periods are exact multiples.

### Firing rule

An entry fires when:

```
tick_count % cycles_between_runs == 0
```

Exception: `weekdays` entries skip Saturday and Sunday even if the cycle
aligns. The skip does not count as a run — the entry fires on the next
weekday tick where the modulo condition holds.

### Tick recalculation

Recalculate the tick interval on any schedule mutation (add, remove, enable,
disable). If the interval changes:

1. Recompute `cycles_between_runs` for every enabled entry.
2. Reset `tick_count` to 0.
3. Update the Cowork scheduled task to the new interval.

If the interval does not change, only compute cycles for the affected entry.

### Examples

- Amazon (hourly) + Netflix (daily): tick = 1h, Amazon cycles = 1,
  Netflix cycles = 24. Amazon fires every tick, Netflix every 24th.
- Netflix (daily) + Spotify (weekly): tick = 24h, Netflix cycles = 1,
  Spotify cycles = 7.
- All entries monthly: tick = 720h (~30 days), all cycles = 1.

## Incremental extraction

Frequency gating and incremental are independent:
- **Frequency** = *when* to run. **Incremental** = *how much* to extract.
- Both apply. Monthly + incremental → runs once per 30 days, pulls only new records.
- First run (watermark null) → full extraction. Subsequent → delta only.
