# Gmail Supplementation — When and How to Use Email Context

Companion reference to SKILL.md. Defines the privacy rules and query templates for using Gmail as a supplementary context source.

Gmail is **supplementary**. RaLHF is the primary source — enriched, structured, long-term context. Gmail fills the "last mile" of recent unprocessed signals RaLHF may not have captured yet.

**Tool dependency:** Gmail tools come from a separate Gmail MCP server (typically `search_threads`, `get_thread`, `list_drafts`, etc.) — NOT from the RaLHF MCP. Before mentioning Gmail in Turn 2b or querying it in Turn 2b's connector flow, **verify Gmail's tools are present in this session's MCP tool surface** (the inventory built in Phase 1 step 4 of SKILL.md). If Gmail isn't connected, do NOT mention it as a probe — silence beats suggesting something the user can't use.

## When to Check Gmail

Check Gmail ONLY when ALL three conditions hold:

1. The task involves something **recent** (within the last 30–90 days).
2. The relevant info likely **generated an email** — bookings, confirmations, invitations, statements, RSVPs.
3. RaLHF didn't have the specific detail you need — Gmail fills gaps, not replaces RaLHF.

Do NOT check Gmail for:
- General preferences (RaLHF handles this)
- Long-term patterns (RaLHF handles this)
- Persona information (RaLHF handles this)
- Anything `personalized` rules say not to query

## Query Templates

Use the Gmail MCP's `search_threads` (or equivalent) with **targeted** queries. Keep searches specific to avoid overwhelming results.

### Travel
**When:** user mentions an upcoming or recent trip, RaLHF doesn't have booking details.

```
Queries:
- "booking confirmation [destination]"
- "flight itinerary [destination or airline]"
- "hotel reservation [destination]"
- "rental car confirmation"
Window: last 90 days
Looking for: dates, flight numbers, hotel names, confirmation numbers
```

### Shopping / Purchase
**When:** user asks about something they bought recently, or you need recent purchase history.

```
Queries:
- "order confirmation from [store]"
- "shipping notification"
- "receipt from [store or category]"
- "subscription renewal"
Window: last 30 days
Looking for: what was purchased, amounts, delivery dates
```

### Health / Medical
**When:** user mentions an upcoming appointment or recent medical event.

```
Queries:
- "appointment confirmation [doctor/clinic]"
- "prescription notification"
- "lab results"
- "appointment reminder"
Window: last 90 days
Looking for: appointment dates, provider names, follow-up instructions
```

### Social / Events
**When:** user is planning around social commitments or mentions an upcoming event.

```
Queries:
- "invitation [event type]"
- "RSVP"
- "event confirmation"
- "party [month]"
- "dinner reservation"
Window: last 30 days
Looking for: event details, dates, locations, guest lists
```

### Financial
**When:** user asks about recent spending or financial activity.

```
Queries:
- "statement from [bank/service]"
- "payment confirmation"
- "subscription charge"
- "invoice from [vendor]"
Window: last 30 days
Looking for: amounts, patterns, recurring charges
```

### Correspondence (writing-to-a-person tasks)
**When:** user is writing to a named recipient and Gmail is connected.

```
Queries:
- "from:<recipient_email>" (last 30–90 days)
- subject keywords matching the task topic
- prior thread on the same topic
Window: last 90 days
Looking for: tone match, prior context, unanswered questions
```

## How to Use Gmail Results

1. **Extract only what's relevant.** Don't dump entire emails. Pull specific facts.
2. **Cross-reference with RaLHF.** Does this confirm or update what RaLHF knows?
3. **Present naturally.** *"I see you have a flight to Denver on April 5th"* — not *"Your Gmail shows…"*.
4. **Each Gmail thread used in the package = one source-promotion queue entry.** See SKILL.md §1.5 — durable facts go via `remember(dimension=...)` mid-execution, AND the thread itself gets a pointer entry queued for the pre-handoff Library refresh ask.

## Privacy Rules

- Only search Gmail when it directly serves the user's current task.
- Never search Gmail out of curiosity or to "build a profile."
- Don't reference email content the user didn't ask about.
- Never save full thread bodies to RaLHF — extract durable facts only.
- If the user asks not to check their email, respect it immediately and `remember` the negative preference.
- Treat email content as ephemeral to this conversation unless told otherwise.
