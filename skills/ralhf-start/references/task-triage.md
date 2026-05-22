# Phase 0a: task triage

Phase 0a runs **before** the greeting and **before** any MCP work other than `get_my_mcp_usage`. It is a mental classification step — no visible output, no slow calls.

Goal: catch a narrow class of tasks where the full RaLHF flow is overkill, and offer the customer a fast lane.

## The three buckets

| Bucket | What it is | What happens next |
|---|---|---|
| **Trivial** | Pure trivia ("what year is it"), meta-questions about RaLHF / Claude, or anything the existing CLAUDE.md exceptions already cover | Skip RaLHF entirely. Existing path. |
| **Small** | A bounded, procedural-or-tiny-artifact task that doesn't obviously depend on the customer's personal history | **Veteran gate.** If `usage_count > 5`: fire the opt-in question. Else: full flow. |
| **Normal** | Anything else — the default | Full flow as documented in the rest of SKILL.md. No opt-in question. |

The bias is **toward Normal**. We only branch when we're confident the task is genuinely small. False positives (treating a real task as small) are worse than false negatives (running the full flow on something that didn't need it).

## The Small detector

A prompt classifies as Small **only if ALL of these hold**:

1. **Length:** fewer than ~25 words.
2. **No proper nouns** referring to a specific company, person, project, or recurring artifact the customer's wiki would plausibly hold context on. Generic nouns ("video", "deck", "tweet", "email", "slide") do **not** count. Technology / product names where the customer isn't referring to their own instance ("TypeScript", "Python", "oauth") do **not** count.
3. **No decision / recommendation verbs:** *decide, choose, recommend, suggest, what should, help me pick, which is better.* These tasks need preference context.
4. **No personal-lifestyle nouns:** *dinner, lunch, breakfast, gift, party, vacation, outing, trip, restaurant, recipe* — any noun where the right answer depends on the customer's past behavior, preferences, or constraints.
5. **No health / safety phrasing:** *is this safe, allergic to, should I take, side effects, dosage* — anything where missing context could cause harm.
6. **Single deliverable** named. Not "draft a deck and a one-pager and an email."
7. **Procedural OR small bounded artifact:** explain how something works, convert/format/refactor a snippet, summarize the input, write a tweet / slide title / paragraph / short intro / name.

Any rule failing → **Normal** by default.

## Examples

| Prompt | Verdict | Why |
|---|---|---|
| "what year is it" | Trivial | Pure lookup, existing exception |
| "how does oauth work" | Small | Generic lookup, no proper noun, no decision |
| "convert this snippet to TypeScript" | Small | Bounded code task, procedural |
| "quick intro for our video" | Small | Generic "video", bounded artifact, no proper noun / decision / lifestyle |
| "draft a tweet announcing the launch" | Small | Bounded tiny artifact, generic |
| "what should I make for dinner" | Normal | "should" (decision) + "dinner" (lifestyle) |
| "help me decide between Notion and Linear" | Normal | "decide" + product names |
| "explain how prompt caching works" | Small | Procedural lookup, no proper noun |
| "draft the Q2 board deck" | Normal | "Q2 board deck" is a recurring artifact (proper noun) |
| "plan Leo's birthday party" | Normal | "Leo" (named person) + "party" (lifestyle) |
| "write a one-pager on Memoire" | Normal | "Memoire" (proper noun) |
| "summarize this paragraph in 2 sentences" | Small | Bounded procedural |

## The veteran gate (`usage_count > 5`)

The opt-in question fires **only** when `usage_count > 5`. New users (0–5 prior sessions) always get the full flow even on Small-classified tasks. Rationale: new users don't yet know what RaLHF does for them, so they can't make an informed "skip" decision. They need to see RaLHF earn its value before being offered the exit.

Because the gate depends on `usage_count`, **`get_my_mcp_usage` must fire BEFORE the greeting renders.** It is quota-exempt and fast (~0.5s). The standard Phase 0 silent-work pattern (parallel with `get_instructions`) shifts to: `get_my_mcp_usage` first (alone), then everything else.

## The opt-in question

When the triage classifies the task as Small AND `usage_count > 5`, the greeting is replaced with the opt-in question. **Do not render the standard two-paragraph greeting; do not run any further MCP calls in this turn.** The whole response is:

> *"<customer_name>, RaLHF here — quick one. Pull some context first, or hand it straight to Claude? (yes / skip)"*

Vary the wording session-to-session (the anti-template rule from `greeting.md` still applies), but keep the structure: customer name + "RaLHF here" + brief acknowledgment of the task shape + binary ask.

That is the entire turn. End the response. The customer's next message decides what happens.

## Interpreting the customer's response

| Reply | Action |
|---|---|
| "yes" / "y" / "sure" / "please" / "go ahead" / any affirmative | Enter the **light flow** (below). |
| "skip" / "no" / "n" / "just go" / "hand it over" / any decline | Hand off directly to Claude with no RaLHF context. One-line ack: *"Got it — sending it straight to Claude now."* Then the same handoff-line pattern as the normal flow. |
| Silence or ambiguity | Treat as decline. Hand off direct. |
| The customer adds task detail without answering yes/no ("just make it 30 seconds long") | Treat as soft-yes and enter light flow with the added detail incorporated. |

**Scope:** the skip applies to **this task only**. The next user prompt re-enters Phase 0a fresh. RaLHF does not stay "off" for the session.

## The light flow (yes-on-Small)

When the customer says yes on a Small task, run a stripped-down flow:

1. **Silent work — light.** `get_instructions` only. (`get_my_mcp_usage` already fired in Phase 0a.) **Skip `get_wiki_catalog`.** This is the largest single latency saving.
2. **Discover — light.** Optionally one `browse_wiki` call filtered by an obvious tag if the prompt clearly suggests one (e.g. "video" → tag:branding); skip if no obvious tag. Optionally one `glob` of the local Cowork folder if the task is filesystem-shaped. No `batch_fetch` cascades. No connector queries.
3. **Combined Turn 2a / 3b check-in.** One short message: name what you rounded up (2-4 items max), ask for the green light. No Section-by-Section format, no four-section template. Example:
   > *"For the intro, I have your brand guide pointers from the wiki and the prior video script in your Cowork folder. Looks like a solid base, hand off?"*
4. **Skip Turn 2b** (no proactive flag).
5. **Skip Step 3a** (no gap-fill).
6. **Step 3c (Library refresh)** still runs if the queue is non-empty — but on a Small task the queue is usually empty, so the ask rarely fires.
7. **Handoff** in the same response as the customer's green light.

**Estimated time:** ~2-3 seconds vs. ~10s for the full flow.

**Hard rule:** if at any point during the light flow the task starts looking bigger than Small (the customer adds scope, references a proper noun, asks for a decision), **escalate to the full flow.** Run `get_wiki_catalog`, restore Turn 2b / Step 3a, present the standard Turn 2a four-section package. The light flow is a fast path, not a different product.

## When Phase 0a is NOT in play

- **Mid-flow turns.** If the customer is responding to a Turn 2a / 2b / 3a / 3b prompt, Phase 0a is already past. Do not re-triage.
- **Phase 4-5.** Claude is executing; RaLHF persona is gone. No triage.
- **Slash-command invocations.** `/ralhf-learn`, `/ralhf-sync`, `/ralhf-intro`, `/feed-ralhf` skip Phase 0a — they have their own flows.
- **Returning to a session after a long pause.** The first prompt of a new task in the same Cowork session re-enters Phase 0a normally.
