# Step 3a: Connectors

> **Step 3a is permission-to-QUERY only.** Ask whether to query each connector; on yes, query it, briefly name what came back, and **add the findings to the package as `source_type: connector` items**. The findings are then affirmed (with everything else) at the Step 3b pre-handoff check-in — keep the Step 3a presentation short, not a full item-by-item pick.

After Phase 2's silent assembly, RaLHF inventories which verified-present connectors are in the session, decides which to offer (or whether to ask open-endedly), and runs the connector permission flow.

Connector queries are a deliberate customer-in-the-loop stage, not silent background work.

## Firing rule

SKILL.md Step 3a has the firing rule, the "verified-present" definition (including the `list_connected_sources` warning), and the Mode A/B/C definitions. This file holds the operational detail: the four-step flow, presentation rules, and example asks.

**The failure mode the firing rule prevents:** RaLHF judges "no connector plausibly helps this task" and skips silently, even though Gmail, Drive, and Calendar were all connected. The customer never gets asked. Always ask. The customer decides.

If you skip the connector ask, you must be able to answer: "Were zero connectors verified-present in this session?" If the answer is anything other than yes, fire mode B at minimum.

## The four-step flow

**Step 1: Identify and ask permission.** Match task shape to connector category (see `references/connector-patterns.md`), filter to verified-present servers, cap at 2 connectors. Pose a single short ask:

```
Good, document list is locked in. Two connectors could add real depth before we hand off:

1. I could check <Connector A> for <specific value, prior threads, recent file, calendar context>. Want me to?
2. I could pull <Connector B> for <specific value>.

Either, both, or skip, your call.
```

**Step 2: Query each approved connector.** Use the tightest possible query (one Gmail search, one Calendar lookup for the relevant date range, one Jira issue fetch). Don't do a broad sweep.

**Step 3: Present results numbered, two lines max per item, easy to reference.** Group under a "From <Gmail / GDrive / Calendar>" header. Number every item starting at 1 within each group so the customer can reply "add 1 and 3" or "skip 2". Hard cap: TWO LINES MAX per item. Line 1 = title with date and link. Line 2 = sender and/or one-line gist. Cut ruthlessly — the customer is scanning, not reading.

```
**From recent Gmail**
1. **Re: Permission form for field trip** [Mar 15, 2026 · <thread-url>]
   From: <teacher_email>. Field trip permission slip due Mar 22.
2. **<Child Name> — reading group update** [Apr 2, 2026 · <thread-url>]
   From: <teacher_email>. Reading group reassignments for Q2.

**From your GDrive**
3. **<Company> Brand Guide** (brand-guide.pptx) [Apr 18, 2026 · <drive-url>]
   Current brand spec, replaces v3.5.
```

Numbering is continuous across groups so the customer never has to disambiguate ("Gmail #2 or Drive #2?"). If something contradicts or enriches earlier findings, that's one extra line under the affected item — not a separate paragraph.

**Step 4: Simple add-or-skip ask.** ONE short question. Customer references items by number:

```
Add any of these? (e.g., "1 and 3", "all", "skip")
```

Variants:
> "Want any of these in the package? Reply with numbers or 'all'/'skip'."
> "Which of these should the AI have? Numbers or 'skip'."

**Banned in Step 3 presentation:**
- Item descriptions over two lines. Cut them.
- Unnumbered bullets — the customer can't reference them quickly.
- Quotes from the email body. A 30-word gist is fine; a 30-word quote is not.
- Multi-sentence explanations of why an item might or might not be relevant. Let the title and one-line gist do the work.
- Compound asks ("Anything here you'd want the AI to weight differently, or should I add this all to the package as-is?"). Just ask the simple add-or-skip question.

**The two-line/numbered/simple-ask rule applies to ALL Step 3a output, not just the initial Mode A offer.** When you present query results — Gmail threads, Drive files, Chrome page pulls, Calendar events, any connector return — the rule holds:

- Numbered items (1, 2, 3...)
- Two lines max per item
- Bullets only; no narrative paragraphs explaining what the items mean
- One simple add-or-skip ask at the end

**Specific banned pattern for tension/conflict surfacing in results:** if you find a conflict in the connector results (e.g., pricing discrepancy across sources), DO NOT explain it in a multi-sentence paragraph. ONE short flag line, then the simple add-or-skip ask. Example:

- **Banned:** "The conflict: the May 13 page is a single $5 plan with no tiers; the May 2 GTM model used $10 with the freemium tier doing the conversion. If $5 is the current pricing, the Year 1 ARR math on the deck needs to change (or the user count target doubles to 20K paid to hold $600K). The RaLHF Subscription page also says 'seeking $3M in 2026' vs the GTM page's 'US$2M extends past 2 years.'" (60+ words, narrative)
- **Good:** "Flag: $5 vs $10 pricing conflict across sources. Want me to add these three pages and pass the conflict to the AI?" (20 words, one flag, simple ask)

### On customer reply

| Reply | Action |
|---|---|
| "Add it / looks good / proceed" | Add to the package. Advance to the final pre-handoff check-in (Step 3b). |
| "Skip the <X thread>" / "weight <Y> higher" | Adjust the package per the customer's amendment, advance. |
| "Look further: also check <other connector>" | Iterate. Query the additional connector, present, re-pose this confirmation. Soft cap: 3 connector iterations before forcing advance. |
| "Skip everything, move on" | Discard the connector findings, advance. |

## Mode B (open-ended) format

When connectors are present but task shape doesn't map cleanly to specific offers, fire mode B as Step 1 instead of mode A:

```
Good, document list is locked in. You have <Gmail, GDrive, Calendar> connected, anything in those you'd like me to look through before we hand off? Recent threads, files, calendar context, anything you think might shape the output.

If nothing comes to mind, just say "skip" and we'll move to the final check.
```

The customer can name a specific connector ("yes check Gmail for X"), name a topic ("look in Drive for the budget spreadsheet"), or skip. Even on tasks where RaLHF can't predict what will help, the open-ended check is mandatory whenever any connector is present.

## Connector-suggestion rules

- **Only mention connectors actually present in THIS session's MCP tool surface.** Either it's in your runtime or you don't mention it. Never "I could check Gmail if you have it connected", that's a probe.
- **Task shape maps to connector category, not Gmail specifically.** Writing to a person → email or messaging connector that's present. Continuing a series → docs or drive connector that's present. See `references/connector-patterns.md`.
- **Cap at 2 connectors per mode-A Step 1 ask** even if more are present. Top two that most directly add depth. (Mode B can list 3+ since it's open-ended.)
- **Skip the connector ask ONLY when zero connectors are verified-present.** This is rare. Don't skip because "I don't think any of them help", the customer decides.
- **Optional: flag a missing-but-useful connector** once per task as a soft suggestion in Turn 2b ("If you connect Notion, I could look through your meeting notes next time"). One-shot, no looping.
