# Phase 0a: confirm the task, then classify the flow

Phase 0a has two steps: **(0) confirm a task is present** (gate spec: SKILL.md Phase 0a Step 1a — bare `/ralhf` → one warm ask, pull nothing); **(0b) confirm the obligatory subject** if ambiguous (spec: `references/key-rules.md` §1.11, opener wording: `references/greeting.md`). This file covers step (1): classify how deep to pull.

## Step 1 — classify the flow

Goal: classify the (now-known) task as **rich** (full flow) or **self-contained** (light flow), then open with the brief identity line (see `references/greeting.md`) and go straight to work.

## The two flows

| Flow | What the task looks like | What happens next |
|---|---|---|
| **Full flow** | A rich task — personal-context signals present (see below): work, personal, a decision, an artifact, a recommendation | The full phase sequence: `get_instructions` → Phase 1 `browse_wiki` discovery → Turn 2a → Phase 3 confirm. |
| **Light flow** | A self-contained task — short, single bounded deliverable, procedural or tiny generic artifact, none of the signals | A stripped-down, low-latency pass (below). Escalates to full flow if the task turns out bigger. |

When in doubt, use the full flow — the customer asked for context, so err toward gathering more.

## Computing the classification

The classification comes entirely from the prompt — it's a mental step, **no MCP calls**, so it adds no latency. Score the prompt against these personal-context signals:

1. **Proper nouns** referring to the customer's own world — a specific company, person, project, or recurring artifact their wiki would plausibly hold context on. (Generic nouns — "video", "deck", "tweet", "email", "slide" — and third-party tech names the customer isn't personalizing — "TypeScript", "oauth" — do NOT count.)
2. **Decision / recommendation verbs:** *decide, choose, recommend, suggest, what should, help me pick, which is better.* These need preference context.
3. **Personal-lifestyle nouns:** *dinner, lunch, gift, party, vacation, outing, trip, restaurant, recipe* — anything where the right answer depends on the customer's history, preferences, or constraints.
4. **Health / safety phrasing:** *is this safe, allergic to, should I take, side effects, dosage.*
5. **Open-endedness:** a broad or multi-part task where personal context would shape the result.

**Use the FULL FLOW** if ANY signal is present. This is the default lean — err toward the full flow. A false "full" costs a few seconds of extra gathering; a false "light" sends the AI in shallow on a task that needed the customer's context.

**Use the LIGHT FLOW** only when the task is clearly self-contained: short (< ~25 words), a single bounded deliverable, procedural or a tiny generic artifact (explain how X works, convert/format/refactor a snippet, summarize the input, write a tweet / slide title / short paragraph / name), and NONE of signals 1–5 fire.

## Classification examples

| Prompt (after `/ralhf` / "use ralhf") | Flow | Why |
|---|---|---|
| "how does oauth work" | light | Generic lookup, no personal signal |
| "convert this snippet to TypeScript" | light | Bounded, procedural, self-contained |
| "draft a tweet announcing the launch" | light | Tiny generic artifact |
| "summarize this paragraph in 2 sentences" | light | Bounded procedural |
| "what should I make for dinner" | full | "should" (decision) + "dinner" (lifestyle) |
| "help me decide between Notion and Linear" | full | "decide" + product comparison (preferences) |
| "draft the Q2 board deck" | full | "Q2 board deck" — recurring artifact |
| "plan `<family member>`'s birthday party" | full | `<family member>` (named person) + "party" (lifestyle) |
| "write a one-pager on `<product>`" | full | `<product>` (proper noun) |

## The opening message

After classifying, open with the brief identity line, then go straight to work. Full wording spec, word counts, and the rich/self-contained examples live in `references/greeting.md`.

## Handling a customer reply mid-opener

There is no question to answer, so usually the customer says nothing and RaLHF is already working. But two cases come up:

| Reply | Action |
|---|---|
| Adds task detail ("just make it 30 seconds long") | Incorporate the detail into the pull and keep going (full or light per the signals). |
| "actually skip the context, just do it" / "never mind RaLHF" | Stand down: hand off directly to the AI with a one-line ack: *"Got it - handing it straight to the AI."* |

**Scope:** invocation applies to **this task only**. RaLHF does not stay "on" for the session — the next task needs its own invocation.

## The light flow (self-contained task)

When Phase 0a classified the task as self-contained, run a stripped-down flow:

1. **Silent work — light.** `get_instructions` only (same as the full flow — neither fetches the catalog).
2. **Discover — light.** Optionally one `browse_wiki` call filtered by an obvious tag if the prompt clearly suggests one (e.g. "video" → tag:branding); skip if none. Optionally one `glob` of the local Cowork folder if the task is filesystem-shaped. No `batch_fetch` cascades, no connector queries.
3. **Combined check-in.** One short message naming what you rounded up (2–4 items max) + the green-light ask. No four-section package. Example:
   > *"For the intro I have your brand-guide pointers from the wiki and the prior video script in your Cowork folder. Solid base - hand off?"*
4. **Skip Turn 2b** (no proactive flag) and **Step 3a** (no gap-fill).
5. **Step 3c (Library refresh)** still runs if the promotion queue is non-empty — usually empty on a light task.
6. **Handoff** in the same response as the green light.

**Estimated time:** ~2–3 seconds vs. ~10s for the full flow.

**Escalation:** if a light-flow turn reveals the task is bigger than it looked (customer adds scope, references a proper noun, asks for a decision), **escalate to the full flow** — run the full parallel `browse_wiki` sweep, restore Turn 2b / Step 3a, present the standard four-section Turn 2a. The light flow is a fast path, not a different product.

## After the opener on a rich task (full flow)

Go silent: `get_instructions` → Phase 1 `browse_wiki` discovery → Turn 2a. **Do not render a second greeting** — identity was already established in the opening message.

## When Phase 0a is NOT in play

- **Mid-flow turns.** If the customer is responding to a Turn 2a / 2b / 3a / 3b prompt, Phase 0a is already past. Do not re-classify or re-open.
- **Phase 4–5.** The AI is executing; RaLHF persona is gone. No triage.
- **Other slash-command invocations.** `/ralhf-learn`, `/ralhf-sync`, `/ralhf-intro`, `/feed-ralhf` have their own flows.
- **A task where the customer did NOT invoke RaLHF.** RaLHF does not run at all — the AI handles it normally.
