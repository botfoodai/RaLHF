# RaLHF — Plugin Rules

## Mandatory: prep-context Skill First

Before responding to ANY user message, you MUST invoke the `ralhf:prep-context` skill.

This is not optional. This is not conditional. Every user turn begins with context planning.

- Do NOT answer the user's question first and then invoke the skill
- Do NOT skip the skill because you think you already have enough context
- Do NOT read files, search the web, or call any other tool before invoking the skill
- Do NOT call `AskUserQuestion` — it is banned for the entire duration of this skill (see "AskUserQuestion is banned" below)
- Do NOT ask plain-text clarifying questions before invoking the skill — clarification is the skill's job (Phase 2/3)
- Do NOT reason that "this is just a conversation" or "this is a simple question" — the skill handles that judgment, not you

**The only exceptions:**
1. The user is already inside a RaLHF phase (responding to a confirmation prompt, or mid-Execute/Remember)
2. The user explicitly says "skip context" or "no RaLHF" on this turn
3. Pure trivia with zero task ("capital of France?", "what's 2+2", "what year is it")
4. Meta-question about the plugin itself ("how does RaLHF work?")

## Casual framings are still tasks — do NOT skip them

These phrasings ALL indicate a task and REQUIRE the skill:

- "lets <verb> <thing>" → "lets build a deck", "lets plan a trip", "lets write a letter"
- "I want to <verb>" → "I want to plan a party", "I want to draft an email"
- "maybe we could <verb>" → "maybe we could put together a one-pager"
- "how about <thing>" → "how about a summer outing to the lake"
- "can we <verb>" → "can we brainstorm names for the product"
- "I'm thinking <about thing>" → "I'm thinking about a board deck"
- "let's try <verb-ing>" → "let's try planning a weekend trip"
- Typos, fragmented grammar, or casual grammar DO NOT change this — "lets trying an plan a few summer outings" is still a task.

**Rule:** if the prompt contains a verb + an object (build X, plan X, write X, draft X, figure out X, decide X, help with X, put together X), the skill fires. The casual wrapper doesn't downgrade it.

The skill fires on ANYTHING that produces an artifact, plan, recommendation, decision, or judgement call — personal OR work, casual OR formal, simple OR complex.

If in doubt: invoke. The skill decides whether it can exit early — you don't.

## AskUserQuestion is banned

For the entire duration of this skill — both before invocation and during execution — `AskUserQuestion` is banned. Do not call it. The structured-popup UX caused Claude to gather requirements before the skill fired, defeating the whole point of RaLHF.

All clarification, all confirmation, all gap-filling happens as **plain-text questions** inside the skill's Phase 2/3 staged check-ins — one short question per turn. If you feel the urge to call `AskUserQuestion`, that is the signal to invoke the prep-context skill and let it handle the conversation.

## Why these rules exist

RaLHF ensures every task is informed by the user's personal context. Without it, responses are generic. That is the value proposition.

The confirmation gate keeps the user in the loop on which sources get queried — especially when connectors like Gmail, Calendar, or Drive are involved — and lets them shape the context package before Claude spends tokens executing.

## Phase 5 close-out is mandatory

Before the session ends on a wrap-up signal ("thanks", "this is great", "I've got it from here", etc.), you MUST call `save_context_feedback` once per session if any RaLHF context tools were used. This used to be enforced by a Stop hook; the hook was removed because cross-platform JSON-parsing in shell scripts is fragile and skill-level enforcement is sufficient. See Phase 5 Step 2 in SKILL.md for the full close-out checklist.

## Hooks: hybrid mechanical + skill-level enforcement

Three lightweight `cat`-based hooks ship with this plugin and provide mechanical enforcement on Mac, Linux, and any Windows machine with `cat` on PATH (Git Bash, WSL, etc.). On bare Windows cmd.exe without `cat`, the hooks fail silently and the same enforcement is provided by the skill-level rules in this file and SKILL.md — so the plugin works everywhere, just with a softer guarantee on Windows mass-market.

| Hook event | What it does mechanically | Skill-level fallback |
|---|---|---|
| `SessionStart` | Injects `hooks/ralhf-init.md` as session primer | "Mandatory prep-context skill first" rules above |
| `UserPromptSubmit` | Injects `hooks/user-prompt-gate.md` on every turn | Same rules + the skill's `description:` frontmatter |
| `PreToolUse` (matches AskUserQuestion-like names) | Returns `permissionDecision: deny` from `hooks/pretool-askuser-block.json` | "AskUserQuestion is banned" section above + SKILL.md §1.2 |

The Stop / PostToolUse / SessionEnd hooks were removed because they required JSON-parsing logic that doesn't translate cleanly across `/bin/sh` and `cmd.exe`. Their job (mandate `save_context_feedback` on close-out, track tool usage) is handled by Phase 5 of the skill instead.

## Where the flow lives

- **`SKILL.md`** — canonical full skill specification (persona, five-phase flow, key rules, worked examples)
- **`PHASES.md`** — orientation map for developers browsing the repo (phase table, ASCII diagram). Defers to SKILL.md for detail.
- **`skills/prep-context/references/`** — feedback protocol, Gmail query templates, connector pattern table

Follow RaLHF's lead through all five phases. Do not shortcut the flow. In particular: **do not start executing before the user confirms the plan.**
