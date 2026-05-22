# RaLHF — Plugin Rules

## Mandatory: ralhf-start Skill First

Before responding to ANY user message, you MUST invoke the `ralhf:ralhf-start` skill.

This is not optional. This is not conditional. Every user turn begins with context planning.

- Do NOT answer the user's question first and then invoke the skill
- Do NOT skip the skill because you think you already have enough context
- Do NOT read files, search the web, or call any other tool before invoking the skill
- Do NOT reason that "this is just a conversation" or "this is a simple question" — the skill handles that judgment, not you

**The only exceptions:**
1. The user is already inside a RaLHF phase (responding to a confirmation prompt, or mid-Execute/Remember)
2. The user explicitly says "skip context" or "no RaLHF"
3. The user is asking about the skill/plugin itself (meta-questions)

## Why this rule exists

RaLHF ensures every task is informed by the user's personal context. Without it, responses are generic. That is the value proposition.

The confirmation gate keeps the user in the loop on which sources get queried — especially when connectors like Gmail, Calendar, or Drive are involved — and lets them shape the context package before Claude spends tokens executing.

## Where the flow lives

- **`SKILL.md`** — canonical full skill specification (persona, five-phase flow, key rules, worked examples)
- **`PHASES.md`** — orientation map for developers browsing the repo (phase table, hook list, ASCII diagram). Defers to SKILL.md for detail.
- **`skills/ralhf-start/references/`** — feedback protocol, Gmail query templates, connector pattern table, and other skill subpages

Follow RaLHF's lead through all five phases. Do not shortcut the flow. In particular: **do not start executing before the user confirms the plan.**
