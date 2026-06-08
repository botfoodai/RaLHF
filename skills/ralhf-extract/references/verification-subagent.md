# Verification Subagent

Prompt template for the verification agent spawned after extraction (Phase 4).
Runs in background after every extraction (inline if background agents are
unavailable) — do not wait for it when running in background.

## Inputs (pass as context in Task prompt)

`domain`, `view_id`, `url`, `recipe_json`, `extracted_data` (row count),
`backend_results` — array of `{endpoint, status_code, response_body}` from Phase 3b.

## Prompt Template

```
You are a verification agent for ralhf-extract. Check that all backend
calls completed successfully after an extraction.

Read the completion rubric at: references/completion-rubric.md

Context: domain={domain}, view_id={view_id}, url={url},
recipe_json={recipe_json}, row_count={row_count},
backend_results={backend_results}

Steps:
1. Evaluate each rubric check against backend_results.
2. For any FAILED check:
   a. Read references/backend-client.md for correct request format.
   b. CRITICAL: /ingest fields MUST be object[] [{"name":"...","type":"..."}],
      NOT string[]. Build: recipe_json.fields.map(f => ({name: f.name, type: f.type}))
   c. Retry via curl (backend-client.md § Curl Template).
3. Check sync stack: read skills/ralhf-extract/.sync-stack.json.
   Empty or missing → pass. Non-empty → log which operations are still pending.
4. Return: all pass + stack empty → "All backend checks passed."
   Any fail after retry → "[Backend sync incomplete — {detail}]"
   Stack non-empty → append "[Sync stack: {N} operations pending for next session]"
```

## Spawning

Spawn a background agent or run inline (see `platform/` bindings for the
concrete tool). Example for Claude Code:
```
Task(subagent_type="Bash", description="verify backend sync",
     prompt=<filled template>, run_in_background=true)
```
If background agents are unavailable (Codex), run the verification steps
inline after extraction.

## Output Handling

- "All backend checks passed." → no action.
- `[Backend sync incomplete — ...]` → append to conversation.
