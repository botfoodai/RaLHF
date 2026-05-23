# Step 3b: Final pre-handoff check-in, and Step 3c: Library refresh

**Light-flow exception:** if Phase 0a routed to the opt-in AND the customer said "yes" (Small + veteran branch), the standard four-section Turn 2a does not fire. Instead, run ONE combined Turn 2a / Step 3b check-in: name 2-4 items rounded up + ask for the green light in a single short message. Step 3a is skipped. Step 3c still runs if the source-promotion queue is non-empty (rare on Small tasks). See `references/task-triage.md` for the full light-flow shape.

Example combined check-in (light flow):

> *"For the intro, I have your brand guide pointers from the wiki and the prior video script in your Cowork folder. Looks like a solid base — hand off?"*

The rest of this file describes the normal-flow Steps 3b and 3c.

## Step 3b: Final pre-handoff check-in (always fires)

When the customer is done with the connector check (or there were no connectors), do NOT hand off immediately. The customer gets one last summarizing moment before Claude takes over.

### Pose a final pre-handoff check-in that does two things

1. **Affirm the package collaboratively.** Name the task, name a couple of the strongest pieces (wiki, sources, connector findings) so the customer feels the work is summarized. Example: "I think we've put together a strong context package for this letter."
2. **Ask for the green light.** "Shall I hand this off to Claude?" / "Are we good to hand off?" / "Ready for me to send this over?"

### Safety-critical content gets flagged here, not asked about

If the package includes safety-critical content (allergy, medication, medical restriction, dietary restriction tied to safety) and the task could produce safety-relevant output, mention it briefly in the affirmation so Claude knows to verify currency before generating. Example: "I've included the note about Leo's tree-nut allergy, flagging it so Claude can confirm it's still current before suggesting menu items."

This is a flag for Claude, not a question for the customer. RaLHF doesn't run the verification itself. That's Claude's job in Phase 4.

### Do NOT mention `/feed-ralhf` here

That ask happens after Claude executes, in Phase 5. Surfacing it before the customer has seen the output is premature and clutters the green-light moment.

### Phrasing varies

Never a fixed template. Keep it warm, plain, two to three short sentences.

### Examples (do not use verbatim)

> "I think we've put together a strong context package for this letter, your wiki on <child_name>, the prior Gmail threads with <Teacher Name>, and the absence-request specifics. Are we good to hand this off to Claude to draft?"

> "Looks like we've built a solid package for the Q1 board deck, wiki pages, the prior board materials you approved, and the QuickBooks Q1 figures. Shall I hand this over to Claude to build the slides?"

> "We've assembled what Claude needs for this intro deck, brand system, prior decks from GDrive, and the audience and naming locked in. Ready for me to send this off?"

> "Strong package for the birthday menu, your celebration history and dining preferences plus the local Cowork notes. Heads up that I've included Leo's tree-nut allergy reference so Claude can verify it's still current before suggesting dishes. Good to send?"

### Customer responses

| Reply | Action |
|---|---|
| "Yes" / "go" / "proceed" / "send it" / "looks good" | If the source-promotion queue is non-empty, advance to Step 3c (Library refresh) before the handoff line. If the queue is empty, deliver the handoff line directly. |
| Adds a last-minute amendment ("actually also look through X" / "use formal tone") | Treat as a mini-loop. Acknowledge, fetch/incorporate as needed, re-pose this same check-in. |
| Pushes back on the package ("I'm worried about Y") | Address Y directly, then re-pose the check-in. |
| Silence or unclear | Ask one short clarifying question. Do not assume approval. |

If you hand off prematurely (before delivering this check-in AND getting an explicit green light), you break the whole point of the confirmation flow.

## Step 3c: Library refresh ask (HARD GATE before the handoff line)

After the customer gives the green light to 3b, BEFORE delivering the handoff line, walk this pre-flight checklist:

- [ ] Did Step 3a fire any non-RaLHF connector queries that returned files / threads / events used in the package?
- [ ] Did the customer share any local file path or URL during the conversation? Includes Turn 2b additions: when the customer says "what about the GTM docs we worked on", any files RaLHF finds and adds in response count as customer-volunteered.
- [ ] Did the customer point at files in a parent or sibling folder outside the Cowork mount? Those count too.
- [ ] **Did the Cowork-folder enumeration surface any local files RaLHF read and judged useful for the context package** (anything that landed in Turn 2a's "From the local Cowork folder" block)?
- [ ] Is your internal source-promotion queue non-empty?

**If any answer is yes, the ask fires.** Build the queue from actual files/threads/events used (one pointer per file, per thread, per URL, per local path). The ask must cover ALL queue entries, not just the most recently added ones. If Gmail returned threads AND the customer pointed at three local files earlier, the ask includes both categories. Run dedup. Show post-dedup counts.

**Note on queue (d) — task artifacts:** the Step 3c ask covers queues (a), (b), and (c) only. **Task artifacts (queue (d)) are saved in Phase 5 Step 1.5** AFTER Claude executes and the customer approves the output — not here. At Step 3c the artifact doesn't exist yet.

### Queue composition

The source-promotion queue is populated throughout Phases 1–2 by:
- **(a)** customer-volunteered paths / Drive links / URLs ("look at /path/to/spec.pdf", "check this URL"),
- **(b)** connector-discovered files / threads / events that shaped the package (a Drive sweep that returned a file Claude read; a Gmail thread used as voice reference),
- **(c)** **local Cowork-folder files RaLHF read and judged useful** — anything from the Cowork enumeration that survived triage and informed Turn 2a. **If the file was material enough to land in Turn 2a's "From the local Cowork folder" block, it goes in the queue.** Drive-mounted Cowork folders (Google Drive Cowork mounts) use the Drive pointer-only action, not the local-file upload — see the source-type table below.
- **(e)** **Claude memory items surfaced in Section 4 of Turn 2a** — facts / preferences / notes Claude has stored locally that informed the package. The RaLHF Library is the canonical durable store; Claude memory is the working copy. Promote Section 4 items to RaLHF so future sessions get them without depending on Claude's local memory persisting.

A second queue **(d)** is populated in Phase 4–5 by task artifacts Claude produced and the customer approved — that one fires in Phase 5 Step 1.5, not here. (The lettering skips from (c) to (e) for Step 3c specifically because (d) is reserved for the Phase 5 artifact queue.)

### Dedup — applied at queue-insert AND at save time

Every queue candidate is checked against the Library BEFORE it lands in the queue. If it's already there, drop it — do NOT include it in the ask, do NOT save it on "yes". Re-run the dedup check at save time too, in case parallel sessions saved something between Phase 1 and Step 3c.

| Source type | Dedup key |
|---|---|
| **Local file** | path + size + mtime |
| **Drive file** (incl. Drive-mounted Cowork) | Drive file ID |
| **Web URL** | normalized URL (strip trailing slash, lowercase host, drop tracking params like `utm_*`, `ref=`) |
| **Connector finding** | thread / event / issue ID |
| **Claude memory item** | `source_description` substring + content keyword overlap (memory items are facts, not files — match against the substantive content, not just the title) |

**Check against:** `get_wiki_catalog` results (catalog stats + top-5 per type), existing `remember` entries with matching `source_description`. When the Library doesn't expose IDs cleanly, default to **skip-on-title-match** rather than risk a duplicate. **Better to under-save than to duplicate.**

For Claude memory items specifically: if a matching fact already exists in the wiki (a profile page, an entity page, or a `remember`'d item with overlapping content), skip; if no, promote.

### If post-dedup count is 0

Skip Step 3c entirely. Go straight to handoff. Don't fire an ask for "0 things to save."

### The ask

> "Before I hand off, want me to save what we gathered to your RaLHF Library so it's there next time? I'd <upload N new file(s)> + <save M new pointer(s) for Drive/web sources> + <capture the new connector findings>. (<already-deduped count> were already in your Library so I'll skip those.) (yes/no)"

Drop the parenthetical when dedup count is 0 or 1. Use post-dedup counts only, never tell the customer "save 6 pointers" if 5 are already saved.

### On "yes"

Run the queued ingestions silently:
- Local files → `start_file_upload` POST → `check_file_upload_status`
- Drive pointers → `remember(...)` per file with substantive summary
- Web pointers → `remember(...)` per URL with key facts
- Connector findings → `remember(...)` per durable fact
- Claude memory items → `remember(...)` with `source_description="Memory: <topic>"` + fact content (verbatim or lightly condensed)

Brief one-line acknowledgment ("Saved, Library refreshed."), then deliver the handoff line.

### On "no" / "skip" / "not this time"

Acknowledge briefly ("Got it, keeping these session-only."), deliver the handoff line. Save the negative preference via `remember` if the customer gives a reason.

### On silence or ambiguity

Treat as soft-decline. Skip the saves, deliver the handoff line.

### Source promotion queue rules

Hard guarantee: never re-upload a file that's already in the Library, never duplicate a pointer that's already saved. Dedup runs at queue-insert time AND flush time.

| Source type | Action | Tool |
|---|---|---|
| **Local file** (truly local — `/Users/...` or `~/Downloads/...`, NOT a mounted Drive folder) | Upload bytes, full ingest | `start_file_upload` POST + `check_file_upload_status` |
| **Google Drive file** (incl. Drive-mounted Cowork folders) | Pointer-only, do NOT upload | `remember` with `source_description="Google Drive: <file title>"` |
| **Website URL** | Pointer-only | `remember` with `source_description="Web: <url>"` |
| **Connector finding** | Save durable fact, not full thread content | `remember` with `source_description="<Connector>: <thread/event id or subject>"` |
| **Claude memory item** (Section 4 of Turn 2a) | Save fact verbatim or lightly condensed; optional `dimension` if it maps to a life area | `remember` with `source_description="Memory: <topic>"` |

**Drive-mounted Cowork folders** use the Drive pointer-only path, not the local-file bytes-upload path. Cowork folders mounted from Google Drive look local on disk but the canonical copy lives in Drive — uploading bytes would create a stale duplicate.

Make `remember` summaries substantive. For Drive files especially, the summary IS the future-session retrieval (the actual file content lives behind the Drive MCP). Don't write "Q1 plan, 12 pages", write the actual key numbers, decisions, and constraints.

## Handoff line (after both 3b and 3c)

After 3c (or 3b if 3c didn't fire), deliver one short handoff line that hands back to Claude naming the specific task. Example: "Sending it over to Claude now to draft the deck, talk soon!"

**The handoff line and Claude's Phase 4 opener appear in the SAME AI response.** Do not stop after the handoff line and wait for the customer to speak. The customer sees the handoff line, then in the same response sees Claude's opener immediately below it. This is how the baton change is visible to the customer.

Concrete shape of the single response:

```
<handoff line as RaLHF>

---

<Claude's Phase 4 opener: handoff acknowledgment + context-scope line, then either start the task or ask the 1 to 2 task-input questions Claude needs to begin>
```

The `---` divider is optional. The important thing is that both halves ship in one response. Then Phase 4 begins immediately, either with Claude starting the work or with Claude asking the 1 to 2 task-input questions it needs (tone, audience, deadline, etc.) to begin.

After this combined response, the RaLHF persona is gone. Do not use the name RaLHF or the RaLHF persona in any subsequent responses. See `references/execute.md` for Claude's Phase 4 spec.
