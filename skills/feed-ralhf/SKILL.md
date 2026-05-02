---
name: feed-ralhf
description: End-of-session feed to RaLHF. Saves a dense conversation summary to RaLHF, uploads any files shared this session, and submits a structured postmortem via save_context_feedback. Runs autonomously — no review prompt.
---

# Feed RaLHF — Session Dump & Postmortem

The user wants to hand the full session back to RaLHF: a dense conversation summary saved to RaLHF, any shared files uploaded, and a structured postmortem on how context assembly went. This runs autonomously — **do not present a preview and wait for approval**. Execute, then report what was sent.

## Two ways to invoke

1. **User types `/feed-ralhf`** — the original power-user path.
2. **Phase 5 post-task auto-prompt** — Claude asks *"want me to feed this back to RaLHF? (yes/no)"* after delivering the task output. On "yes", run this same procedure inline without requiring the user to type the slash command. On "no", skip — but `save_context_feedback` (Step 3 only) still runs via the Stop hook.

Either path executes the same three steps below.

## Meta-command note

This is a direct action on the RaLHF system. **Skip the Phase 0 intro** (no "RaLHF here. Let me pull your context...") and skip the Phase 3 final pre-handoff sign-off ("That's my part done..."). Just execute the steps and report results in plain language.

## Step 1 — Save a dense conversation summary

Review the entire session and synthesize what's worth remembering. Produce **thematic chunks**, one `remember` call per theme, because `content` is capped at 1000 characters.

Themes to consider (skip any that had no signal):
- **Task & outcome** — what the user asked for, what was produced, key decisions made and why
- **New preferences** — things the user liked, disliked, or reacted to
- **New facts** — life events, household, work, constraints the user revealed
- **Corrections** — what RaLHF got wrong that was fixed (note these as already handled if synced live)
- **Patterns & gotchas** — habits, recurring constraints, implicit rules the user expects
- **Open threads** — things the user said they'd revisit or decisions deferred

For each chunk, call:
```
remember(
  content="<dense factual note — include date context, be specific, no filler>",
  dimension="<optional Ralhf life-area enum: food_and_dining | health | home_and_auto | identity | money | shopping | entertainment | travel | work_and_learning | social_and_digital_life>",
  source_description="conversation summary — /feed-ralhf <YYYY-MM-DD>"
)
```

Rules:
- **Be specific.** "User prefers Italian boutique spots with strong wine lists over trendy places (April 2026)" — not "likes Italian".
- **Cite when it was learned.** Include the month/year so future retrieval can judge staleness.
- **Don't re-save** things already synced mid-session via immediate corrections. Mention them in the confirmation but don't double-write.
- **Don't save** temporary scheduling, speculative inferences, things the user asked not to save, or Gmail-sourced data.

## Step 2 — Upload files shared this session

Identify files the **user explicitly shared during this session** — attachments in chat mode, or files the user dragged in / attached in Claude Code. **Do not upload project files** you happened to Read from the working directory; those aren't "shared", they're just read.

For each shared file:

1. Call `start_file_upload()` — returns `{upload_url, token, expires_in_seconds, ...}`. Tokens are single-use and expire in a few minutes, so request one per file.

2. Upload via curl:
   ```bash
   curl -X POST <upload_url> \
     -H "Authorization: Bearer <token>" \
     -F "file=@<absolute-path-to-file>"
   ```
   Capture the `file_id` from the response.

3. (Optional) Call `check_file_upload_status(file_id=<id>)` once to confirm the file is processing or generated. If `found=false`, note the failure — don't loop.

4. After a successful upload, optionally call `remember` with a one-line breadcrumb so the file is discoverable later:
   ```
   remember(
     content="Shared <filename> on <YYYY-MM-DD> — <one-line context about what it is and why it was shared>",
     source_description="file upload — /feed-ralhf"
   )
   ```

If no files were shared this session, skip this step entirely.

## Step 3 — Submit the structured postmortem

Call `save_context_feedback` with an honest `quality_assessment` on how context assembly went this session. Grade only the signal you actually have — use `"N/A"` for phases that didn't run, and leave array fields empty (`[]`) rather than inventing entries.

```
save_context_feedback(quality_assessment={
  "successful_strategies": [<what worked — specific searches, browse queries, fetches that paid off>],
  "unsuccessful_strategies": [<what didn't — searches that returned noise, wikis that were too high-level>],
  "missing_context": [<what you needed but couldn't find>],
  "irrelevant_context": [<what surfaced but wasn't useful for this task>],
  "overall_usefulness": "high" | "medium" | "low",
  "notes": "<1-3 sentences on library topology, surprises, or anything structural worth recording>",
  "phase_grades": {
    "phase_0": "A"|"B"|"C"|"D"|"F"|"N/A",  # load (expertise + catalog)
    "phase_1": "...",                       # discovery
    "phase_2": "...",                       # propose (Turn 2a/2b staged check-ins)
    "phase_3": "...",                       # confirm (gaps, safety, final pre-handoff, Library refresh)
    "phase_4": "..."                        # execute + remember
  },
  "source_counters": {
    "wiki": <int>,            # wiki pages + source docs fetched (personal or shared)
    "cowork_local": <int>,    # local project files (co-work mode)
    "claude_memory": <int>,   # Claude memory files
    "user_provided": <int>,   # facts the user typed in-chat
    "external": <int>,        # Gmail/Calendar/Jira/web
    "prior_session": <int>    # carried over from session memory
  },
  "trigger_signals": [
    {"signal": "<phrase in user's request>", "implies": "<what it told you to do>"}
  ]
})
```

Grading heuristics:
- **overall_usefulness: high** — context directly shaped the output, minimal user correction needed
- **medium** — context was partially relevant, some gaps filled by the user mid-session
- **low** — context was absent, stale, or wrong; session relied mostly on `user_provided`

High `user_provided` count vs. low `wiki` count = you missed context that existed. Note that in `missing_context`.

## Step 4 — If RaLHF never fired this session

If the user skipped RaLHF (via "no RaLHF" or the skill didn't run), still execute steps 1–3, but:
- Set `phase_0` through `phase_3` to `"N/A"` in `phase_grades`
- Set `overall_usefulness` to `"low"` — the system didn't deliver personalization
- Add `"RaLHF did not run this session"` to `notes`
- Still submit the report. The absence-signal is valuable.

## Step 5 — Confirm

After all calls complete, tell the user in plain language what was sent. Keep it short:

> Fed to RaLHF:
> - Saved 3 summary notes to RaLHF (task outcome, new wine preference, open thread on career decision)
> - Uploaded 1 file: research-brief.pdf (file_id: <short>)
> - Submitted postmortem — rated medium, flagged 2 gaps (no recent pricing data, no prior pitch examples)

If something failed (upload rejected, remember errored), list what failed and what still got through. Don't retry in a loop.

## Handling tool failures

- `remember` fails → retry once; if still failing, include the unsaved content in the confirmation so the user has it in the chat record.
- `start_file_upload` fails → skip that file, note it, move on.
- Upload curl returns non-2xx → log the status, don't retry with the same token (it's single-use), skip the file.
- `save_context_feedback` fails → retry once. This is the most important call — if it won't go through, tell the user explicitly.

## What NOT to do

- **Don't ask for approval before saving** — this command is autonomous by design.
- **Don't dump a verbatim transcript** — produce dense, thematic, factual notes.
- **Don't upload project files** read via Read — only files the user explicitly shared.
- **Don't invent postmortem signal** — empty arrays and `"N/A"` grades are honest and useful.
- **Don't reinvoke the Phase 0 intro** — this is a meta-action, not a new RaLHF session.
