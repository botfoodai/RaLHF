# Wiki Intent Resolution

Resolve ambiguous user intent by querying the RaLHF wiki before falling
back to interactive prompts. This keeps the extraction flow silent
(consistent with UX rule 2: never ask permission) when wiki context
provides enough signal to auto-select.

## When to use

- User names a domain without a URL ("show my Netflix history")
- URL matches multiple views in the manifest
- User request is ambiguous ("get my data from LinkedIn")
- Scheduling a domain with multiple views

Skip this entirely when:
- User provided a URL that matches exactly one view
- Only one view exists for the domain
- The skill is running unattended (schedule-run)

## Resolution hierarchy

Check sources in order. Stop at the first source that gives a clear signal.

### 1. Local schedule (cheapest — file read)

Read `schedule.json` from the plugin root. Filter entries by domain.

```
entries where domain == "{bare-domain}" and enabled == true
```

Each entry has `view_id`, `wiki_target`, and `notes`. If entries exist:
- Single entry → auto-select that view.
- Multiple entries → user actively tracks multiple views. Use the
  user's natural-language request to match against `notes` and
  `wiki_target` values. Exact keyword overlap wins.

### 2. Request keyword matching (free — text analysis)

Match keywords in the user's natural-language request against view labels
in the manifest. Case-insensitive partial matching (e.g., "history" matches
"Viewing History").

If only one view label matches → auto-select. Multiple matches → fallback.

### 3. Fallback — ask the user

If none of the above sources resolve to a single view:
- Multiple views, no signal → `AskUserQuestion` with view labels.
- No URL and no manifest → ask for URL.

This is the only case where the user sees a prompt during intent
resolution. The question should be minimal: view labels only, no
explanation of internals.

## Auto-selection rules

When a source provides signal, apply these rules:

| Signal | Confidence | Action |
|---|---|---|
| Schedule entry matches exactly one view | High | Auto-select |
| Request keywords match exactly one view label | High | Auto-select |
| Request keywords match multiple view labels | Low | Ask user |
| No signal from any source | None | Ask user |

"Match" means keyword overlap between the signal text and the view's
`label` field in the manifest. Case-insensitive. Partial matches count
(e.g., "history" matches "Viewing History").

## What feeds this loop

Intent resolution improves over time because extraction writes context
back:

1. **`ralhf-schedule add`** creates `schedule.json` entries with
   `wiki_target` and `notes` → direct signal for source 1.
2. **Manual extractions** create recipe files and manifests → grows the
   local signal for source 1 even without scheduling.

First extraction for a new domain will always hit fallback (source 4).
Every subsequent interaction gets faster and more accurate.

## Caller reference

| Skill | Where to call | What it replaces |
|---|---|---|
| `ralhf-extract` | Phase 0, before manifest URL matching | "No URL provided" view picker; multi-view disambiguation |
| `ralhf-schedule` | `add` command, Step 3 | `AskUserQuestion` for multi-view selection |
| `ralhf-schedule-run` | Not applicable | Runs unattended — no disambiguation needed |
