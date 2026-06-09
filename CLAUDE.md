# RaLHF — Plugin Rules

## Mandatory: ralhf-start Skill First

Before responding to ANY user message, you MUST invoke the `ralhf:ralhf-start` skill.

This is not optional. This is not conditional. Every user turn begins by invoking the skill — the skill then runs the **ask-first gate** (recommend pulling context or handing straight to the assistant, and ask). Invoking the skill is NOT the same as building a context package: on a real task the skill asks first and only assembles context if the user says "pull."

- Do NOT answer the user's question first and then invoke the skill
- Do NOT skip the skill because you think you already have enough context
- Do NOT read files, search the web, or call any other tool before invoking the skill
- Do NOT reason that "this is just a conversation" or "this is a simple question" — the skill handles that judgment, not you
- Do NOT decide on your own whether context is needed — that is exactly what the ask-first gate is for. Invoke the skill and let it ask.

**The only exceptions:**
1. The user is already inside a RaLHF phase (responding to the ask-first gate, a confirmation prompt, or mid-Execute/Remember)
2. The user explicitly says "skip context" or "no RaLHF"
3. The user is asking about the skill/plugin itself (meta-questions)

## Why this rule exists

RaLHF makes sure no task goes to the assistant blind when the user's personal context would improve it — but it puts the user in control of when that happens. On every real task the skill fires the **ask-first gate**: it names the task, recommends whether context would help, and asks `(yes / no)`. The recommendation is computed from the prompt alone (no lookups, no latency); the user decides.

This keeps the user in the loop on which sources get queried — especially when connectors like Gmail, Calendar, or Drive are involved — and avoids spending tokens assembling context the user didn't want. On "pull," the downstream confirmation gate still lets them shape the context package before the assistant executes.

## Where the flow lives

- **`SKILL.md`** — canonical full skill specification (persona, five-phase flow, key rules, worked examples)
- **`PHASES.md`** — orientation map for developers browsing the repo (phase table, hook list, ASCII diagram). Defers to SKILL.md for detail.
- **`skills/ralhf-start/references/`** — feedback protocol, Gmail query templates, connector pattern table, and other skill subpages

Follow RaLHF's lead through all five phases. Do not shortcut the flow. In particular: **do not start executing before the user confirms the plan.**
