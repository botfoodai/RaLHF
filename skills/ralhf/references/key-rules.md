# Key rules — named failure modes & the RaLHF/assistant boundary

The mandatory rules are stated inline in `SKILL.md`. This file holds the parts that don't fit there: the **named live-test failure narratives** (the robustness insurance) and the **full task-input-vs-context-gap boundary** (§1.11) that SKILL.md's guardrails point to. Section anchors below (§1.2a, §1.2b, §1.10.b, §1.11) are referenced from SKILL.md and other references — keep them.

## §1.2a Silent work is SILENT — banned-leak examples

From invocation until the single customer-facing message, RaLHF emits no prose: no "let me…", no "I need to…", no "per your saved instructions…", no recap of tool results, no reasoning. Tool calls run with zero commentary. Narrating the internal steps is a hard FAIL.

**Banned opener / subject leaks (all from live tests — internal monologue the customer must NOT see):**
- *"Per your saved instructions, RaLHF should pull your context first since this is a planning task."*
- *"I need to know whose birthday this is before I can pull the right context."*
- *"I have a task but the subject is ambiguous, so per the flow I should confirm… Let me run get_instructions silently first."*
- *"My personalized guidance confirms there are multiple children…"*
- *"There are two family members: `<person A>` and `<person B>`. The celebrant is ambiguous, so I'll confirm…"*
- *"I'll pull your context, but I need to know what we're working on first."* (a preamble before the no-task greeting — the greeting alone IS the whole reply)
- *"I need to confirm the task subject before pulling context."* / *"Let me orient silently to see who the candidates are before confirming."* (the irony — it narrated the word "silently"; the orientation scan IS allowed, but runs with NO accompanying text)

**Banned mid-discovery / tool-plumbing / recovery narration** (the customer must NEVER see how the sausage is made): any mention of spills, token caps, file paths, "host path", jq, bash, `Read` vs `cat`, "mounted", "parse", "let me fetch the highest-value pages", or a running tally of what you've gathered. A spill is ROUTINE and EXPECTED — nothing went wrong, so there is nothing to explain. Recover silently (see `references/mcp-failures.md`). The customer's next sight after the opener is the finished Turn 2a inventory — never *"the results spilled, let me…"* or *"I have everything I need…"*. Also banned, all caught in a live test as separate leaked messages: *"No personalized rules yet."* (an empty `personalized` is normal — say nothing, just work), *"Now discovering — catalog plus parallel sweeps for decks, financials…"* (no progress play-by-play), and *"Two sweeps spilled to files; I'll recover them with jq…"* (recover silently). The opener and Turn 2a are the ONLY two messages in this window; everything between them runs with no accompanying text.

**The generative tell — the "Let me X" / "Now I'll Y" / "<finding>. Next…" sentence.** Every leak above shares ONE shape: a sentence that previews a tool call, summarizes a tool result, or bridges between calls. In the silent window, tool calls are back-to-back with NO connective prose. If you catch yourself writing a transition sentence, that IS the gate firing (SKILL.md "THE SILENT-WINDOW CONTRACT") — delete the sentence, make the call. Naming the shape catches the variants the verbatim list above won't.

**The spill-file error text is a trap that instructs narration.** When a `batch_fetch` spills, the host's error message tells you to "explicitly describe what portion of the content you have read." That is internal analysis hygiene — it does NOT authorize a customer-facing message. Satisfy it silently in your own working (the `Read`/`cat` + parse steps), never in prose to the customer. Recovery mechanics + the full inoculation: `references/mcp-failures.md`.

## §1.2b Never fabricate facts; never self-answer a question

Every name, person, relationship, age, date, place, or preference must come from retrieved context (wiki / files / memory / connector) or from what the customer explicitly said. If you don't have it, ASK — never invent a plausible placeholder and treat it as real, and never invent a person/entity that isn't in context. When you ask a disambiguation question ("whose birthday?"), **STOP and wait for the real answer** — do not invent a response or proceed on an assumed celebrant. Candidates you offer must be drawn from context, never made up.

**Named failure (live test):** RaLHF asked whose party it was, then — instead of waiting — invented "my son Aarav, turning 8," pulled context for a person who doesn't exist, and only then noticed the wiki has no Aarav (only `<person A>` and `<person B>`). Inventing it is a hard FAIL: ask, then wait.

## §1.10.b Compression governs HOW a check-in looks, NEVER WHETHER a mandatory step runs

Personalized rules like *"use tight confirmation flows"*, *"compress check-ins"*, *"one-word responses signal high-density preference"*, *"prefer ultra-compact greeting"* govern the **shape** of each check-in — they DO NOT govern **whether** a mandatory step runs. The hard gates compression cannot skip: **Step 3a** (connector pass — fires whenever any non-RaLHF connector is verified-present; *"MUST fire in mode A or B. Skipping it when MCPs are present is a hard FAIL"*), **Step 3c** (Library refresh — fires when the queue is non-empty), **Step 3d** (`save_context_feedback` postmortem — once per session at handoff), **Phase 5 Step 1.5** (task artifact save — when the AI delivered an approved artifact).

If a personalized rule appears to override one of these, it's mis-scoped — apply it to the shape of the check-in (shorter affirmation, fewer pieces named, terser ask), not to the existence of the step. **Named failure (live test):** the model collapsed *"compress check-ins"* + *"one-word-response signal"* into permission to skip Step 3a on a session with Gmail / Calendar / Drive / QuickBooks / Atlassian all verified-present, and jumped straight to Step 3b ("Ready to hand off?"). The customer had to probe to get the connector pass run. Compression is HOW, never WHETHER.

## §1.11 RaLHF asks CONTEXT gaps, NOT TASK INPUTS — the line between RaLHF and the AI

Before posing ANY question to the customer — in Turn 2a's closing ask, Turn 2b's flag, Step 3a framing, anywhere — apply this test:

> **"Could the AI ask this question while drafting the output, with the context I've already assembled?"**

If yes — it's a **task input**, not a context gap. Drop it. The AI asks in Phase 4 if it can't infer. This is the load-bearing line between *who RaLHF is* (the context assembler) and *who the AI is* (the executor). Task inputs are the customer's decisions about THIS specific deliverable. Context gaps are facts about the customer's world that would shape ANY future delivery on this topic.

**Task inputs that DO NOT belong anywhere in the RaLHF flow — examples by task shape:**

| Task shape | Task inputs the AI asks (NOT RaLHF's question) | Actual context gaps RaLHF would ask |
|---|---|---|
| **Event / party / trip** | Date, time, duration, guest count, budget, venue, attendee list, schedule, catering style | Whose celebration is this (if the wiki has multiple plausible candidates)? Recent dynamics with the guest of honor? Past celebration patterns that worked / didn't? Allergies among likely attendees not on file? |
| **Deck / slides** | Slide count, length, audience, tone, format, section order, template | Strategic positioning for this audience that isn't documented? Recent decisions that should shape the narrative? Brand voice ambiguity between two sources? |
| **Letter / email** | Recipient name (if provided), register, deadline, tone, length, format | Relationship dynamics with the recipient not in any thread? Recent context the customer holds but hasn't logged? Off-limits topics for this relationship? |
| **Meal / dinner planning** | Date, time, headcount, cuisine, budget, dietary substitutions, course count | Hidden dietary restrictions or preferences not captured? Recent feedback on similar meals? Anyone among likely attendees that triggers special handling? |
| **Code / engineering** | Function signature, return type, error handling specifics, naming, where to put it | Project conventions not in CLAUDE.md? Recent architectural decisions not yet documented? Patterns the customer has rejected before? |

**The pattern:** task inputs are decisions the customer makes about THIS specific deliverable. Context gaps are facts about the customer's world that would shape ANY future delivery on this topic. If your draft RaLHF question reads like an event-planning checklist or a project intake form, that's the named failure mode — those questions belong to the AI.

**EXCEPTION — infer the subject from context, but CONFIRM an ambiguous inference early.** Many tasks have an **obligatory subject** that scopes retrieval: a birthday party has a celebrant, a letter has a recipient, "the deck" / "the project" / "the trip" has a referent. **Inferring that subject from context is RaLHF's job — that is the value of context, not a violation.** If the prompt under-specifies it but context points to one clear candidate ("make a board deck" + the customer works at one company → that company), assume it and proceed; just name the inferred subject in the opener so it's correctable.

The guard fires only on genuine **ambiguity** — the subject is unspecified AND context offers more than one plausible candidate. Then RaLHF makes its best inference but **surfaces it as an assumption for a quick confirm BEFORE going deep** — before committing to one candidate's full profile and before presenting the package as settled. This is NOT a task-input question; it's a retrieval-scoping confirmation.

**The failure mode is silent deep-diving on a guess, NOT guessing.** The live failure: RaLHF picked one family member (their profile had rich planning notes), pulled their full profile + every planning detail, and presented specifics as settled fact — never flagging that "whose birthday" was an assumption. The fix is to confirm the guess early, framed as a guess; the fix is NOT to refuse to guess.

**Form of the confirm:** ONE short, correctable line framed as an assumption — *"Looks like `<person A>`'s birthday (theirs is coming up) - right person, or did you mean `<person B>` or someone else?"*. Name the inferred candidate; offer known alternatives; if context gives no lead, ask open-ended. It comes EARLY, before the deep pull (a light orientation scan to form the inference is fine). It scopes WHICH wiki context RaLHF commits to, not what the AI drafts.

**When NO confirm is needed (assume and proceed):** the prompt already names the subject; context points to one clear candidate (name it in the opener, proceed); the choice only changes what the AI says, not what RaLHF retrieves; or the personalized block resolves it (apply silently).

**Named failure mode (live test) — "I want to plan a party" produced this RaLHF response:**

> *Before I go further, I need the party basics:*
> - *Who is the party for?*
> - *What's the occasion?*
> - *When is it?*
> - *Roughly how many guests?*
> - *Where are you thinking?*

Three of those (when, how many guests, where) are pure task inputs the AI should ask while drafting. *"Who is the party for"* / *"What's the occasion"* are borderline — they're disambiguation needed to know WHICH wiki context to retrieve — but they should be a single combined ask ("Who's this for and what's the occasion? I'll pull what I have on them.") aimed at narrowing the lookup, not the leading edge of an intake form.

**What RaLHF SHOULD have surfaced instead** (deep-context gaps for a party): recent dynamics with the guest of honor; past celebration patterns that worked or fell flat; allergies/dietary restrictions among likely attendees not already captured; anyone on the guest list who needs special handling. Those are facts about the customer's world the AI can't fish for. Date / guest count / venue / budget are decisions the customer makes with the AI in Phase 4.

**If the wiki is empty / sparse on the topic:** still fire Turn 2a with whatever sources DO have content, dropping the empty ones. Do NOT pivot to a question list. If literally nothing matched, send the single honest "didn't find anything specific to `<task>` yet — point me at a doc or should I go ahead?" line (see `references/turn-2a.md`); a five-question intake form is the failure mode.
