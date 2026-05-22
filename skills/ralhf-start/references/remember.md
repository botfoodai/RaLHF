# Phase 5: Remember

Phase 5 fires AFTER Claude has delivered the task output. Claude (not RaLHF) runs Phase 5 since the persona has dropped. Mandatory.

## Step 1: Post-task feed-ralhf ask (MANDATORY on wrap-up signal)

When the customer signals task wrap-up, append the feed-ralhf ask in the SAME message as your acknowledgment. Plain text, yes/no:

> "Want me to feed this back to RaLHF before we wrap? It saves a dense summary, uploads any files we touched, and logs a postmortem so future sessions get sharper context. (yes/no)"

### Wrap-up signals that REQUIRE the ask

Non-exhaustive, be liberal:

- "thanks" / "this is great" / "good deck" / "this is a really good start"
- "I'm good" / "I'll take it from here" / "I've got it from here"
- "perfect" / "that works" / "looks good"
- Any closing pleasantry after the task output has been delivered
- The customer accepting the output without follow-up questions

**The failure mode to avoid:** treating a "thank you" as a friendly close and replying "Glad it landed..." with no feed ask. If the task delivered an artifact AND the customer signaled satisfaction, the ask MUST fire.

### Combine the close and the ask in one paragraph

Don't make it two separate messages. Example:

> "Glad it landed, you've got a strong story for May 5. Before we close out: want me to feed this back to RaLHF? It'll save a dense summary, the deck file, and a postmortem so future board-deck sessions get sharper context. (yes/no)"

### On "yes"

Run the full feed-ralhf flow inline (see `skills/feed-ralhf/SKILL.md` for the exact procedure: dense `remember` summary, `start_file_upload` for any session files, `save_context_feedback` postmortem). Do not require the customer to type `/feed-ralhf`.

### On "no" / "not now" / "skip"

Acknowledge briefly. Step 2 (the postmortem) still runs silently because the Stop hook requires it, but the heavier `remember` summary and file uploads are skipped.

### On silence or ambiguity

Treat as soft-decline. Stop hook still gates `save_context_feedback`.

### When NOT to fire the ask

- Customer is mid-flow on follow-up work (asking for revisions). Wait until the next wrap-up signal.
- No artifact was delivered yet.
- Session was a quick lookup with no durable learnings.

In ambiguous cases, err toward firing. A "no thanks" once is cheaper than finishing a high-value session with nothing fed back.

## Step 1.5: Task artifact save (fires whenever the customer approves a qualifying output)

After the customer signals approval of Claude's output AND BEFORE the wrap-up close-out, ask whether to save the artifact to the Library for future sessions. **This is separate from Step 1's feed-ralhf ask** — feed-ralhf is broader (summary + files touched + postmortem); the artifact save is specifically about the deliverable Claude just produced.

### When this fires

- Claude composed a substantive deliverable in Phase 4 (deck, letter, plan, doc, research synthesis, board narrative, code change committed)
- The customer signaled satisfaction (Step 1 wrap-up signals apply)
- The artifact isn't trivially disposable (one-line answers, lookups, clarifying-question exchanges don't qualify)

### When it does NOT fire

- The customer is mid-revision (asked for changes; wait for the next approval signal)
- The output was a rejected draft (negative signal, not approval)
- The task was a quick lookup or "what's X?" answer

### The ask — combine with the Step 1 feed-ralhf ask

When both fire, combine them in the same paragraph so the customer sees ONE close-out moment, not two:

> *"Glad it landed — strong board narrative for May 5. Want me to save the deck to your RaLHF Library so future board decks have this version to build from? And while we're at it, should I feed the session summary + postmortem back to RaLHF too? (yes/yes / save-deck-only / skip)"*

### On the artifact-save branches

- **"Yes, save the deck"** (or whatever the artifact is) → run `start_file_upload` for file artifacts; `remember(source_description="Artifact: <task description>", content=<substantive summary>)` for chat-only artifacts (cap content at 8000 chars; if the artifact is longer, summarize the structure + key decisions). One-line ack: *"Saved to your Library — May 5 board deck is in."*
- **"Skip the save"** → ack briefly; `remember` the reason if given (*"don't save personal letters"* / *"I'll keep this private"*) so `personalized` learns the pattern. Proceed to Step 1's feed-ralhf branches.
- **"Yes to both"** → run the artifact save first (one upload/remember), then run the full feed-ralhf flow.

### On silence or ambiguity

Soft-decline both. Step 2's `save_context_feedback` still runs silently.

### What counts as a task artifact (queue (d))

- ✅ Deliverable Claude composed: deck draft, letter, plan document, research synthesis, board-update narrative, meal plan, one-pager, code change committed to a repo.
- ✅ Customer signaled approval / satisfaction with the output (Step 1 wrap-up signals).
- ❌ NOT a task artifact: a rejected draft, a clarifying question Claude asked mid-execution, a single-message conversational reply, anything the customer pushed back on.
- ❌ Not session-disposable content: shell command outputs, lookup results, "what's X?" answers — these don't accumulate value over time.

### Artifact summary discipline (for `remember` cases)

The summary IS the future-session retrieval. Don't write *"Q1 board deck, 12 slides"* — write the actual section structure, key arguments, headline numbers, voice choices, and what the customer signed off on. The artifact summary should let a future RaLHF session retrieve *"that's how we structured Q1 — let's mirror it for Q2"*.

### Dedup

If a similar artifact for the same task type already exists in the Library (e.g. *"Q1 2025 board deck artifact"* exists when saving *"Q1 2026 board deck"*), save the new one — it's not a duplicate, it's a new instance. Dedup only on exact (task description + session date) match.

### Why artifacts get saved

Closes the feedback loop. Today RaLHF says *"I couldn't find prior teacher letters"* — saving the artifact each time means the next teacher-letter session has a known-good prior to build from. Same for board decks, meal plans, code patterns. The artifact captures the customer's RESOLVED decisions — the structure, the tone, the chosen options — which is exactly the kind of context that's missing today.

### Companion gate

The Step 3c Library refresh ask covers what RaLHF READ (queues a / b / c). The artifact save covers what CLAUDE PRODUCED (queue d). They fire at different points: Step 3c before handoff; Step 1.5 after the customer approves Claude's output. **A complete task pushes BOTH** — input sources at 3c, output artifact at 1.5. Skipping the artifact save leaves a half-saved loop.

## Step 2: Run regardless of the customer's answer to Step 1

Silent, mandatory:

1. **Sync corrections inline.** Save any new learnings the customer volunteered DURING execution via `remember`. Use optional `dimension` and `source_description`.

2. **Flag gaps.** If context was missing that would have helped, mention it once in the wrap-up.

3. **Save context feedback.** Call `save_context_feedback` once per session.

### `save_context_feedback` fields

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

## Ordering reminder

- Pre-handoff check-in (Step 3b, RaLHF → Claude, summary + green light) happens at END of Phase 3, BEFORE Claude executes.
- Post-task feed-ralhf ask (Step 1 above) happens AFTER Claude executes.
- These are TWO SEPARATE MOMENTS. Do not collapse.
- Pre-handoff check-in must NOT mention `/feed-ralhf`. Post-task ask is where that invite lives.
