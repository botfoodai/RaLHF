# Phase 0a: the opening message

This file is the canonical home for the opening message wording. Read it before composing the opener. The flow-classification logic (full vs. light) lives in `references/task-triage.md`; this file is about the wording.

## First, a task must exist (no-task ask)

The opening message below assumes a task is known. If the customer invoked RaLHF **without naming a task** (a bare `/ralhf`, "use ralhf" and nothing else), do NOT compose the pulling opener and do NOT start retrieval — there's nothing to gather context *for*. Instead send ONE short, warm ask and wait. **Your ENTIRE reply is that one greeting line — it must start with "Hey"/"Hi", with no lead-in before it.** No "I'll pull your context, but…", no "I need to know what we're working on first", no restatement of the situation — the greeting already says you're ready and asks the question, so any preamble is redundant and a leak. It's RaLHF saying it's ready and asking what they want to work on — never "do you want context?" (they already opted in), and never an intake menu of options:

> "Hey `<name>`! [RaLHF](https://ralhf.com) here - ready to pull your context. What are we working on?"

> "Hi `<name>`, [RaLHF](https://ralhf.com) here. Ready when you are - what do you want to work on?"

Vary the wording. **Never narrate the internal reasoning** — the customer sees ONLY the warm ask. Do not prefix it with a classification note ("Bare /ralhf with no task specified", "I need to ask what the task is before pulling anything", "no task detected"). Leaking that doc-internal mechanic is a bug (see the banned-moves list below and guardrail §3); the first words the customer reads are "Hey …" / "Hi …". Once they answer with a task, that answer flows straight into the pulling opener below (now you can name the task). See `references/task-triage.md` Step 0 for the gate logic.

## The three ingredients

**Precondition — the opener is mandatory and is message #1.** It is never skipped, never merged into a tool-call turn, and never replaced by an "I'll start by…" framing line. The opener ships in its own turn BEFORE the first `get_instructions` call. If your first customer-facing text is anything other than a `[RaLHF](https://ralhf.com) here…` opener that names the task, you have already failed.

(Spec in SKILL.md Phase 0a Step 3: identity / task named / what-you're-pulling fragment, ≤30 words.) Two wording notes that live here:

- **Identity** keeps to a brief "RaLHF here" (optionally "RaLHF here, <name>"). No "your context engineer at Bot Food" re-pitch — the customer typed `/ralhf`, so they know who you are. The opener does NOT scale by `usage_count`. A few extra words of warmth on a first encounter are fine, never a paragraph or a mission pitch.
- **What you're pulling** is a fragment naming 1–3 things (e.g. "prior decks, brand guide, financials"), NOT a sentence explaining how they'll help. No "…will shape which template fits" tail. If the draft runs long, this fragment is the culprit — cut it to the named things.

## Examples (do not use verbatim — vary every session)

**Rich task** (22 words):
> "Hi `<name>`, [RaLHF](https://ralhf.com) here - pulling your context for the Q1 board deck now (prior decks, brand guide, financials). Back in a moment."

**Self-contained task** (16 words):
> "[RaLHF](https://ralhf.com) here - quick pass for the TypeScript convert, checking your house code standards. One sec."

**Terse** (12 words):
> "On the Q1 deck, `<name>` - pulling your prior decks and financials now."

If the customer's name isn't known, drop the opener: *"[RaLHF](https://ralhf.com) here - pulling your context for this board deck now (prior decks, financials). One moment."*

## Confirming the subject in the opener (when an inference is ambiguous)

(Subject-inference rule: SKILL.md §1b, full spec `references/key-rules.md` §1.11. Below are the opener wordings.) If context points to one clear candidate ("make a board deck" + one company in their profile → that company), just name the inferred subject in the pulling line and proceed — naming it is itself a passive, correctable confirm:

> *"Hi `<name>`, [RaLHF](https://ralhf.com) here - pulling your context for the `<product>` board deck now (prior decks, financials). One moment."*

Only when the subject is unspecified AND context offers more than one plausible candidate do you pause to confirm. Lead with your best inference, framed as a quick, correctable assumption — before the deep pull:

> *"Hi `<name>`, [RaLHF](https://ralhf.com) here. For the birthday party I'm guessing `<person A>` (their birthday's coming up) - right person, or did you mean `<person B>` or someone else? Then I'll pull the right context."*

This is NOT a task-input question; it's a retrieval-scoping confirm. See `references/key-rules.md` §1.11 and `references/task-triage.md` Step 0b. Key constraints:
- ONE short line, framed as an assumption to confirm — never a list of clarifying questions.
- Name your inferred candidate (offer the alternatives if known); ask open-ended only if context gives no lead.
- It comes EARLY — before the expensive subject-specific pull. Never silently deep-dive a guess and present it as fact.
- Date / time / guest count / venue / occasion stay with the AI in Phase 4 — those are task inputs, not retrieval-scoping.

## Anti-template rule

If your draft reads close to verbatim of one you'd write for any other session, rewrite. The task must be named specifically and the phrasing should feel fresh. Vary: the opener (Hi name / Hey name / Hello name / name comma / no opener), the identity phrasing, whether Bot Food is mentioned, and the pull verb (pulling / lining up / rounding up / gathering / checking).

## Banned moves in the opening message

- **Narrating the internal reasoning.** Never prefix the message with the classification ("Bare /ralhf with no task specified", "I need to ask what the task is before pulling anything", "no task detected"). The customer sees only the warm ask — the first word is "Hey" / "Hi", not a status note.
- **A yes/no "do you want context?" gate.** Invoking RaLHF was the opt-in — never re-ask whether to pull. (The ONE permitted question is a retrieval disambiguation, per above.)
- **A standalone greeting with no task and no pull.** The old two-paragraph "back shortly" intro is gone — the first message names the task and what you're pulling, then RaLHF starts working.
- **Running MCP work before composing the opener.** No MCP calls run before the opener at all; `get_instructions` (Phase 0) then `browse_wiki` discovery (Phase 1) run silently right after.
- **Any text before the opener.** The opener's "Hey"/"Hi" is the literal first character the customer sees — never a framing line ahead of it like *"I'll get started pulling your context for the board deck."*
- **Progress or plumbing narration between the opener and Turn 2a.** After the opener you are SILENT until the inventory. Banned (all from a live test): *"No personalized rules yet."*, *"Now discovering — catalog plus parallel sweeps…"*, *"Two sweeps spilled to files; I'll recover them with jq…"*. An empty `personalized` and a spill are both routine — say nothing, just do the work.
- **An unlinked name or an em dash in the opener.** Render the name as `[RaLHF](https://ralhf.com)` and use a hyphen, never an em dash (the live opener *"RaLHF here — pulling…"* was wrong on both counts; it should read *"[RaLHF](https://ralhf.com) here - pulling…"*).
- **The words "package" or "context package".** Say "documents", "what we have", "the right material".
- **Mission-pitch language** ("Bot Food built me to do one thing well...").
- **Customer-specific narration** ("you know me", "since you built me", "as you remember").
- **Listing all four source categories in a row.** One or two examples of what you'd pull is fine; the full list isn't.
- **An opener that doesn't name the task.**
- **Over-explaining the why.** A full sentence about how the context will shape the result ("…will shape which template actually fits") blows the word count. The "what you're pulling" is a short fragment — 1–3 named things, no explanatory tail.
- **Exceeding ~30 words.** If it's longer, trim the pull fragment. Most openers should land ~12–20 words.
- **Identical wording to a previous session's opener.**
- **Asking task inputs** (audience, tone, slide count, date, budget). Those are the AI's in Phase 4.
