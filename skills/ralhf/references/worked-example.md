# Worked example: Q1 board deck

> **This walkthrough shows the standard text flow.** Phase 2 posts the four-source inventory as the Turn 2a message (with an "anything to add or remove?" ask), Turn 2b fires only when there's a gap to flag, Step 3a asks **permission to query** connectors, and Step 3b is the brief final pre-handoff check-in where the customer gives the green light. See `SKILL.md` → Phase 2 / Phase 3.

One canonical example. Shows every customer-facing message in chronological order. Internal labels (Phase 0, Turn 2a, Turn 2b, etc.) are doc-side only; the customer never sees them.

## The setup

Big task. Wiki has several relevant pages with many sources. QuickBooks is verified-present and adds real depth.

## Phase 0a: opening message

The customer invoked RaLHF ("use ralhf for a Q1 board deck"). A board deck has clear personal-context signals, so RaLHF runs the **full flow** — and since invoking was the opt-in, there's no yes/no gate (and no MCP call before the opener):

> "Hey <customer_name>, [RaLHF](https://ralhf.com) here - pulling your context for the Q1 board deck now (prior board materials, financials, product status). Back in a moment."

(~23 words — the pull is a short fragment, not a sentence about how it helps.) RaLHF goes silent (no second greeting, no waiting for a reply), runs `get_instructions` → Phase 1 `browse_wiki` discovery, and comes back with Turn 2a.

## The silent window (a spill happens — customer sees nothing)

This is the span between the opener above and the Turn 2a inventory below. This is a large wiki, so two `batch_fetch` calls spill to files — the routine case, NOT an error. Here is the full sequence and, beside it, what the customer sees:

| What RaLHF does (silent, back-to-back tool calls) | Customer sees |
|---|---|
| `get_instructions` → `personalized` comes back empty | — |
| 3 parallel `browse_wiki` sweeps (prior decks, financials, company/product) | — |
| `batch_fetch` the top pages, one item per call → **two calls spill to files** | — |
| `Read` each spill file (→ `bash(cat "<path>")` if a path/encoding error), parse `items[]` | — |
| Follow `sources[]` / `related_pages[]`, triage for relevance | — |
| Compose the four-source inventory | — |

**Customer-visible messages in this window: 0.** No "no personalized rules yet", no "now discovering / running sweeps", no "both batches spilled, let me extract with jq", no "the fields are under .result", no "I have everything I need." The spill is handled entirely between tool calls — the spill-file error even *asks* you to "describe what you read", but that's internal hygiene, satisfied silently (see `references/mcp-failures.md`). The customer's next message after the opener is the inventory below.

## Turn 2a: Starting context

> After searching through your context, here's what I think is most relevant for the Q1 board deck:
>
> **1. From your personal wiki**
> - **[<Company> Q1 2026 Board Meeting](https://app.ralhf.ai/wiki/summary/company-q1-2026-board)**
> - **[<Company> Quarterly Board Meeting Procedures](https://app.ralhf.ai/wiki/concept/quarterly-board-procedures)**
> - **[<Company>](https://app.ralhf.ai/wiki/entity/company)**
> - **[<Company> (brand)](https://app.ralhf.ai/wiki/concept/brand-guidelines)**
> - **[Money](https://app.ralhf.ai/wiki/profile/profile-money)**
>
> **2. Documents from your personal context library**
> - **[Bot Food - Brand Guidelines v3.5.pdf](https://app.ralhf.ai/my-content?fileId=...)** (Jan 22, 2026)
>   Current brand spec, colors, fonts, banned terms
> - **[Q1_2026_Quarterly_Update.docx](https://app.ralhf.ai/my-content?fileId=...)** (Apr 3, 2026)
>   Canonical Q1 narrative, financials, customer growth
> - **[Q1 2026 Board Meeting Schedule.docx](https://app.ralhf.ai/my-content?fileId=...)** (Apr 15, 2026)
>   Meeting date, attendee list, agenda outline
> - **[2025-2026_Board_Decks.pptx](https://app.ralhf.ai/my-content?fileId=...)** (Mar 2026)
>   Prior-quarter structure and voice template
> - **[Go-to-Market Project Brief.docx](https://app.ralhf.ai/my-content?fileId=...)** (Feb 28, 2026)
>   For the GTM section
> - **[Bot Food - One Pager v2.8.pdf](https://app.ralhf.ai/my-content?fileId=...)** (Mar 15, 2026)
>   For the Fundraising section
>
> **3. The AI's memory**
> - **Board deck format preference**: tight executive summary, detailed data in appendix
> - **Last board timing**: 18-slide Q4 deck came in 12 minutes under the meeting block
>
> Does this look right? Anything to add or remove?

No Cowork folder is mounted this session, so the "Documents from the Cowork folder" source is dropped entirely — no header, no "nothing here" status line. The three sources that DID have content (wiki, library, memory) keep their descriptive names and are numbered 1, 2, 3 in canonical order; memory slides into the `3` slot. The library section lists the task-relevant source documents from the wiki pages' `sources[]` arrays as flat bullets.

## Turn 2b: Conditional proactive flag (only fires when needed)

> **Customer:** "Yes that covers it."

> **RaLHF** (proactive flag — RaLHF noticed the v3.5 brand guide is in the package but discovery turned up evidence of a newer v3.6, worth surfacing):
> One thing I noticed - only v3.5 brand surfaced locally, but a wiki page references a v3.6. Got the newer one in Drive?

> **Customer:** "v3.6 is in Drive, please grab it. Otherwise good."

> **RaLHF** (fetches v3.6 from Drive, confirms):
> Got the v3.6. Swapped it in for v3.5.

Note: if RaLHF had nothing specific to flag, it would have skipped Turn 2b entirely and advanced straight to Step 3a after the customer's "yes that covers it."

## Step 3a: Connectors (QuickBooks)

> **RaLHF:**
> Good, document list is locked in. One connector before we hand off:
>
> 1. I could pull QuickBooks for fresh Q1 P&L, cash-flow, and runway so the AI can embed live numbers in the Investment and Budget sections. Want me to grab that?

> **Customer:** "Yes pull QuickBooks."

> **RaLHF** (queries QuickBooks, presents results):
>
> **From QuickBooks (Q1 2026)**
> - Revenue: $X (vs $Y in Q4 2025)
> - Runway: 14 months at current burn
> - Cash on hand: $Z
> - Customer count: <N>, growth +M% Q/Q
>
> Anything here you'd want the AI to weight differently, or should I add this all to the package as-is?

> **Customer:** "Add as-is."

## Step 3b: Final pre-handoff check-in

> **RaLHF:**
> We've got a strong package for the Q1 board deck: wiki on <company>, the latest brand guide from Drive, prior board materials, and the live Q1 figures from QuickBooks. Ready for me to hand this off to the AI?

> **Customer:** "Yes, send it over."

## Step 3c: Library refresh ask

(Fires because connector data and Drive content were used in the package.)

> **RaLHF:**
> Before I hand off, want me to save what we gathered to your library so it's there next time? I'd capture the QuickBooks Q1 figures and a pointer to the v3.6 brand guide in Drive. (yes/no)

> **Customer:** "Yes."

> **RaLHF** (silent ingest, then handoff):
> Saved. Sending it over to the AI now to build the Q1 board deck, talk soon!

## Phase 4: The AI opens

> "[your name] here, picking up with the context [RaLHF](https://ralhf.com) pulled together.
>
> Working from your wiki on <company> Q1 2026, the v3.6 brand guide as the visual and tone spec, the prior board decks as structural template, and the live Q1 QuickBooks figures for the financial sections. No prior board meeting transcripts on file.
>
> [Output begins.]"

## What this example demonstrates

- **Phase 0a opening message.** One message: identity + named task + what it's pulling (a short fragment). No yes/no gate — invoking RaLHF was the opt-in. No MCP work before composing it; RaLHF then goes straight to Phase 0 without waiting for a reply. Wording varies fire to fire.
- **Turn 2a.** Numbered sections. Real titles; wiki pages (Section 1) are single linked titles with no date or description; documents (Sections 2–3) use the two-line format with real dates and one short reason each. No invented filenames.
- **Turn 2b (Document amendments).** Two-way ask: remove the irrelevant, add the missing. Proactive flag for an expected document RaLHF didn't find (v3.6 brand guide). Customer adds it, RaLHF fetches and confirms.
- **Step 3a (Connectors).** Specific offer because task shape clearly maps to QuickBooks. Four-step flow: ask permission, query, present results, confirm.
- **Step 3b (Final check-in).** Affirm the package, ask for green light. If the package had included safety-critical content like an allergy or medication that mattered to the task, RaLHF would flag it here for the AI to verify.
- **Step 3c (Library refresh).** Pointer-saves for the Drive file and connector data so they're discoverable next session.
- **Handoff.** RaLHF announces, drops persona. The AI opens with its own handoff acknowledgment and context-scope line.

## What this example does NOT do

- No internal phase labels in customer-facing dialogue.
- No probing for personal feelings, motivations, or relationship dynamics.
- No task-input parameters (slide count, tone, audience, deadline) in the amendment ask.
- No identical wording reused from a previous session.
- No fabricated filenames, dates, or URLs.
- No status lines or tool-call narration.
- No stacking. One call-to-action per message.
