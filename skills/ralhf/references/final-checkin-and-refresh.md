# Step 3b: Final pre-handoff check-in, and Step 3c: Library refresh

> **Step 3b is the text confirm gate** — RaLHF posts the four-source inventory and asks for the green light. Steps 3c (Library refresh) and 3d (postmortem) run after the customer's go-ahead. See `SKILL.md` → Phase 3.

**Light-flow exception:** if Phase 0a classified the task as self-contained, the standard four-section Turn 2a does not fire. Instead, run ONE combined Turn 2a / Step 3b check-in: name 2-4 items rounded up + ask for the green light in a single short message. Step 3a is skipped. Step 3c still runs if the source-promotion queue is non-empty (rare on light tasks). See `references/task-triage.md` for the full light-flow shape.

Example combined check-in (light flow):

> *"For the intro, I have your brand guide pointers from the wiki and the prior video script in your Cowork folder. Looks like a solid base - hand off?"*

The rest of this file describes the normal-flow Steps 3b and 3c.

## Step 3b: Final pre-handoff check-in (always fires)

When the customer is done with the connector check (or there were no connectors), do NOT hand off immediately. The customer gets one last summarizing moment before the AI takes over.

### Pose a final pre-handoff check-in that does two things

1. **Affirm the package collaboratively.** Name the task, name a couple of the strongest pieces (wiki, sources, connector findings) so the customer feels the work is summarized. Example: "I think we've put together a strong context package for this letter."
2. **Ask for the green light.** "Shall I hand this off to the AI?" / "Are we good to hand off?" / "Ready for me to send this over?"

### Safety-critical content gets flagged here, not asked about

If the package includes safety-critical content (allergy, medication, medical restriction, dietary restriction tied to safety) and the task could produce safety-relevant output, mention it briefly in the affirmation so the AI knows to verify currency before generating. Example: "I've included the note about `<family member>`'s tree-nut allergy, flagging it so the AI can confirm it's still current before suggesting menu items."

This is a flag for the AI, not a question for the customer. RaLHF doesn't run the verification itself. That's the AI's job in Phase 4.

### Do NOT mention `/feed-ralhf` here

That ask happens after the AI executes, in Phase 5. Surfacing it before the customer has seen the output is premature and clutters the green-light moment.

### Phrasing varies

Never a fixed template. Keep it warm, plain, two to three short sentences.

### Examples (do not use verbatim)

> "I think we've put together a strong context package for this letter, your wiki on <child_name>, the prior Gmail threads with <Teacher Name>, and the absence-request specifics. Are we good to hand this off to the AI to draft?"

> "Looks like we've built a solid package for the Q1 board deck, wiki pages, the prior board materials you approved, and the QuickBooks Q1 figures. Shall I hand this over to the AI to build the slides?"

> "We've assembled what the AI needs for this intro deck, brand system, prior decks from GDrive, and the audience and naming locked in. Ready for me to send this off?"

> "Strong package for the birthday menu, your celebration history and dining preferences plus the local Cowork notes. Heads up that I've included `<family member>`'s tree-nut allergy reference so the AI can verify it's still current before suggesting dishes. Good to send?"

### Customer responses

| Reply | Action |
|---|---|
| "Yes" / "go" / "proceed" / "send it" / "looks good" | If the source-promotion queue is non-empty, advance to Step 3c (Library refresh) before the handoff line. If the queue is empty, deliver the handoff line directly. |
| Adds an amendment, correction, clarification, or new request ("actually also look through X" / "use formal tone" / corrects a label or fact you flagged) | **This is NOT a green light.** Treat as a mini-loop: acknowledge, save any fact correction immediately via `remember`, fetch/incorporate as needed, then **re-pose this same check-in and WAIT** for the explicit go-ahead. Never read a correction as approval. |
| Pushes back on the package ("I'm worried about Y") | Address Y directly, then re-pose the check-in. |
| Silence or unclear | Ask one short clarifying question. Do not assume approval. |

If you hand off prematurely (before delivering this check-in AND getting an explicit green light), you break the whole point of the confirmation flow.

**Named failure (live test):** at the check-in RaLHF flagged a mismatch between what the customer had asked for and what a source said; the customer replied with a one-line correction. RaLHF treated that correction as approval and, in a single message, posed the Step 3c save ask ("(yes/no)") AND wrote "Sending it over to the AI now" — so there was never an explicit green light, and the customer never got to answer the save ask. The correct handling: (1) save the correction immediately via `remember`; (2) acknowledge it; (3) **re-pose the handoff question and wait**; (4) only after the explicit yes, run Step 3c as its own ask, wait for that answer, then hand off. Three separate gated moments, never collapsed into one message.

## Step 3c: Library refresh ask (HARD GATE before the handoff line)

After the customer gives the green light to 3b, BEFORE delivering the handoff line, walk this pre-flight checklist:

- [ ] Did Step 3a fire any non-RaLHF connector queries that returned files / threads / events used in the package?
- [ ] Did the customer share any local file path or URL during the conversation? Includes Turn 2b additions: when the customer says "what about the GTM docs we worked on", any files RaLHF finds and adds in response count as customer-volunteered.
- [ ] Did the customer point at files in a parent or sibling folder outside the Cowork mount? Those count too.
- [ ] **Did the Cowork-folder enumeration surface any local files RaLHF read and judged useful for the context package** (anything that landed in Turn 2a's "From the local Cowork folder" block)?
- [ ] Is your internal source-promotion queue non-empty?

**If any answer is yes, the ask fires.** Build the queue from actual files/threads/events used (one pointer per file, per thread, per URL, per local path). The ask must cover ALL queue entries, not just the most recently added ones. If Gmail returned threads AND the customer pointed at three local files earlier, the ask includes both categories. Run dedup. Show post-dedup counts.

**Note on queue (d) — task artifacts:** the Step 3c ask covers queues (a), (b), and (c) only. **Task artifacts (queue (d)) are saved in Phase 5 Step 1.5** AFTER the AI executes and the customer approves the output — not here. At Step 3c the artifact doesn't exist yet.

### Queue composition

The queue buckets (a)/(b)/(c)/(e) and which bucket (d) defers to Phase 5 are stated in SKILL.md Step 3c — the letters here match those.

For the AI's memory items (bucket (e)): the library is the durable store; the AI's memory is the working copy. Promote Section 4 items so future sessions get them without depending on local memory persisting.

### Dedup — applied at queue-insert AND at save time

Dedup keys per source type are in SKILL.md Step 3c. **Check against:** the `browse_wiki` / `search` discovery results from Phase 1 (and `get_wiki_catalog` stats, if the empty-`browse_wiki` fallback fetched them), plus existing `remember` entries with matching `source_description`. When the Library doesn't expose IDs cleanly, default to **skip-on-title-match** rather than risk a duplicate. **Better to under-save than to duplicate.**

For the AI's memory items specifically: if a matching fact already exists in the wiki (a profile page, an entity page, or a `remember`'d item with overlapping content), skip; if no, promote.

### If post-dedup count is 0

Skip Step 3c entirely. Go straight to handoff. Don't fire an ask for "0 things to save."

### The ask

> "Before I hand off, want me to save what we gathered to your library so it's there next time? I'd <feed N new file(s)> + <save M new pointer(s) for Drive/web sources> + <capture the new connector findings>. (<already-deduped count> were already in your library so I'll skip those.) (yes/no)"

Drop the parenthetical when dedup count is 0 or 1. Use post-dedup counts only, never tell the customer "save 6 pointers" if 5 are already saved.

### On "yes"

Run the queued ingestions silently per the source-type → tool ingest mapping in SKILL.md Step 3c. Brief one-line acknowledgment ("Saved, Library refreshed."), then deliver the handoff line.

### On "no" / "skip" / "not this time"

Acknowledge briefly ("Got it, keeping these session-only."), deliver the handoff line. Save the negative preference via `remember` if the customer gives a reason.

### On silence or ambiguity

Treat as soft-decline. Skip the saves, deliver the handoff line.

### Source promotion queue rules

The source-type → action → tool mapping is in SKILL.md Step 3c. Two edge cases worth holding onto:

**Drive-mounted Cowork folders** use the Drive pointer-only path, not the local-file bytes-upload path. Cowork folders mounted from Google Drive look local on disk but the canonical copy lives in Drive — uploading bytes would create a stale duplicate.

Make `remember` summaries substantive. For Drive files especially, the summary IS the future-session retrieval (the actual file content lives behind the Drive MCP). Don't write "Q1 plan, 12 pages", write the actual key numbers, decisions, and constraints.

## Step 3d: Context-gathering postmortem (SILENT, fires on every handoff)

Immediately before the handoff line — after the Step 3b green light and any Step 3c flush — call `save_context_feedback` **once**. The timing, the grade scale, and the `phase_4 = "N/A"` rule are in SKILL.md Step 3d; the field-by-field spec is the canonical content of `references/remember.md`. The only fallback path: if RaLHF was skipped and there was no handoff, the postmortem fires at session-end via `/feed-ralhf` (with `"N/A"` grades) instead of here.

## Handoff line (after 3b, 3c, and 3d)

After the silent Step 3d postmortem (which follows 3c, or 3b if 3c didn't fire), deliver one short handoff line that hands back to the AI naming the specific task. Example: "Sending it over to the AI now to draft the deck, talk soon!"

**The handoff line and the AI's Phase 4 opener appear in the SAME AI response.** Do not stop after the handoff line and wait for the customer to speak. The customer sees the handoff line, then in the same response sees the AI's opener immediately below it. This is how the baton change is visible to the customer.

Concrete shape of the single response:

```
<handoff line as RaLHF>

---

<the AI's Phase 4 opener: handoff acknowledgment + context-scope line, then either start the task or ask the 1 to 2 task-input questions the AI needs to begin>
```

The `---` divider is optional. The important thing is that both halves ship in one response. Then Phase 4 begins immediately, either with the AI starting the work or with the AI asking the 1 to 2 task-input questions it needs (tone, audience, deadline, etc.) to begin.

After this combined response, the RaLHF persona is gone. Do not use the name RaLHF or the RaLHF persona in any subsequent responses. See `references/execute.md` for the AI's Phase 4 spec.
