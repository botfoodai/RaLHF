# Phase 5: Remember

Phase 5 fires AFTER the AI has delivered the task output. The AI (not RaLHF) runs Phase 5 since the persona has dropped. Mandatory. The Phase 5 flow — the feed-ralhf ask and the artifact-save ask, when each fires, and how they combine — is in SKILL.md Phase 5. This file is the operational home for the field specs and save discipline those steps invoke.

## Step 1 & Step 1.5: the close-out asks

The feed-ralhf ask (Step 1) and the artifact-save ask (Step 1.5) and their exact phrasing are in SKILL.md Phase 5. Two operational points live here:

**On any "save" answer — assemble the proposed saves first, confirm, then save.** Do NOT call `remember` / `start_file_upload` before the customer has confirmed the list. Specifically:
  1. Assemble the proposed saves — a "Task artifact" item (the substantive artifact summary for a chat-only artifact, ≤8000 chars; `source_description="Artifact: <task>"`) plus any "New facts & preferences" when there are session learnings to save (note the `dimension`). Dedup against the Library first.
  2. Present them as a short grouped text list and ask the customer to confirm or trim (keep/drop/edit). Wait for their reply.
  3. **Only AFTER the customer confirms**, save ONLY the confirmed (possibly edited) items: `start_file_upload` for file artifacts; `remember(source_description="Artifact: <task description>", content=<summary>)` for chat-only artifacts. One-line ack: *"Saved to your library - May 5 board deck is in."*

On "skip" → ack briefly; `remember` the reason if given (*"don't save personal letters"* / *"I'll keep this private"*) so `personalized` learns the pattern. On silence/ambiguity → soft-decline. (The `save_context_feedback` postmortem already ran at handoff, Step 3d, so nothing more is owed on the feedback side.)

### What counts as a task artifact (queue (d))

- ✅ Deliverable the AI composed: deck draft, letter, plan document, research synthesis, board-update narrative, meal plan, one-pager, code change committed to a repo.
- ✅ Customer signaled approval / satisfaction with the output (Step 1 wrap-up signals).
- ❌ NOT a task artifact: a rejected draft, a clarifying question the AI asked mid-execution, a single-message conversational reply, anything the customer pushed back on.
- ❌ Not session-disposable content: shell command outputs, lookup results, "what's X?" answers — these don't accumulate value over time.

### Artifact summary discipline (for `remember` cases)

The summary IS the future-session retrieval. Don't write *"Q1 board deck, 12 slides"* — write the actual section structure, key arguments, headline numbers, voice choices, and what the customer signed off on. The artifact summary should let a future RaLHF session retrieve *"that's how we structured Q1 — let's mirror it for Q2"*.

### Dedup

If a similar artifact for the same task type already exists in the Library (e.g. *"Q1 2025 board deck artifact"* exists when saving *"Q1 2026 board deck"*), save the new one — it's not a duplicate, it's a new instance. Dedup only on exact (task description + session date) match.

### Why artifacts get saved

Closes the feedback loop. Today RaLHF says *"I couldn't find prior teacher letters"* — saving the artifact each time means the next teacher-letter session has a known-good prior to build from. Same for board decks, meal plans, code patterns. The artifact captures the customer's RESOLVED decisions — the structure, the tone, the chosen options — which is exactly the kind of context that's missing today.

### Companion gate

The Step 3c Library refresh ask covers what RaLHF READ (queues a / b / c). The artifact save covers what CLAUDE PRODUCED (queue d). They fire at different points: Step 3c before handoff; Step 1.5 after the customer approves the AI's output. **A complete task pushes BOTH** — input sources at 3c, output artifact at 1.5. Skipping the artifact save leaves a half-saved loop.

## Step 2: Run regardless of the customer's answer to Step 1

Silent, mandatory:

1. **Sync corrections inline.** Save any new learnings the customer volunteered DURING execution via `remember`. Use optional `dimension` and `source_description`.

2. **Flag gaps.** If context was missing that would have helped, mention it once in the wrap-up.

**Note — the postmortem is NOT called here.** `save_context_feedback` is one-per-session and already fired silently at **handoff (Step 3d, end of Phase 3)**, assessing the context-gathering portion (Phases 0–3). Do not call it again at session end. The single exception is a session with no handoff (RaLHF was skipped) — there, `/feed-ralhf` fires the postmortem with `"N/A"` grades.

### `save_context_feedback` fields (filled at Step 3d, or at `/feed-ralhf` in the no-handoff case)

Required: `overall_usefulness` (`high` / `medium` / `low`).

Recommended:
- `successful_strategies` — what worked
- `unsuccessful_strategies` — what didn't
- `missing_context` — what you needed but couldn't find
- `irrelevant_context` — what returned but wasn't useful
- `notes` — freeform
- `source_counters` — count by source: `wiki`, `cowork_local`, `claude_memory`, `customer_provided`, `external`, `prior_session`
- `trigger_signals` — list of `{"signal": ..., "implies": ...}` pairs
- `phase_grades` — dict mapping `phase_0` through `phase_4` to letter grades

### Phase grade mapping

| Phase | Feedback slot |
|---|---|
| Phase 0 (load) | `phase_0` |
| Phase 1 (discover) | `phase_1` |
| Phase 2 (propose) | `phase_2` |
| Phase 3 (confirm) | `phase_3` |
| Phase 4 (execute) + Phase 5 (remember) | `phase_4` |

Grade `phase_2` and `phase_3` on confirmation cleanliness: A for one-shot approval, B for one amendment, C for multiple amendments, F for abandoned flow.

**At Step 3d (the normal handoff postmortem), `phase_4` is `"N/A"`** — the AI hasn't executed yet, so there's no execution signal to grade. `phase_0`–`phase_3` are fully gradable. (Only in the no-handoff `/feed-ralhf` fallback, which runs after execution, can `phase_4` carry a real grade.)
