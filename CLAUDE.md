# RaLHF — Plugin Rules

## Invoke the `ralhf` Skill Only on Explicit Request

RaLHF does NOT auto-fire. Invoke the `ralhf:ralhf` skill when, and only when, the user explicitly asks for it — and handle every other task normally, without the skill.

Explicit requests look like: the user types `/ralhf`, says "use ralhf" / "use RaLHF for this" / "ralhf this", asks you to "pull my context" / "gather context first" / "have RaLHF look at this", or makes a similar clear request to bring in their personal/work context before the task.

- Do NOT invoke the skill on ordinary task messages where the user did not ask for RaLHF.
- Do NOT ask the user, on every task, whether they want to use RaLHF — there is no per-task yes/no gate anymore. Wait for them to invoke it.
- Once the user does invoke it, hand control to the skill immediately, before reading files or calling other tools — the skill owns context gathering from that point.

**Also skip the skill when:**
1. The user is already inside a RaLHF phase (responding to a confirmation prompt, or mid-Execute/Remember).
2. The user is asking about the skill/plugin itself (meta-questions).

## Why this rule exists

RaLHF makes sure a task doesn't go to the assistant blind when the user's personal context would improve it — but the user, not the plugin, decides when to bring it in. Invoking the skill IS the opt-in: there is no per-task interruption asking whether to use it. When invoked, the skill goes straight to pulling context — loading the wiki, files, memory, and connected sources, assembling the relevant material, and letting the user confirm the package before the assistant executes.

This keeps the user in control of when their sources get queried — especially connectors like Gmail, Calendar, or Drive — and keeps ordinary tasks fast and uninterrupted when context isn't wanted.

## Mandatory: Route Feedback Through a Classifier Subagent

Whenever the user gives **feedback** — a correction, a complaint, a "you missed X" / "that's wrong" / "also get Y", a preference, or any signal about how something went — you MUST NOT decide where it goes yourself, and you MUST NOT reach for a memory or feedback tool directly. Feedback that sounds personal is very often an extraction-quality signal, and the two go to completely different places. Guessing sends extractor corrections into the personal wiki, where they vanish — they never reach the recipe-refinement loop.

So you do not route feedback. **Spawn a subagent with fresh context** (the `Agent` tool, `general-purpose`) and let it classify and route. Fresh context is the point: the main conversation biases the judgment toward "this is about the user," which is exactly the mistake. The subagent judges from the feedback text plus the minimal facts you pass it.

Hand the subagent:
- the user's **verbatim feedback**;
- whether an **extraction ran this session** and, if so, its domain / view-id / recipe-id / recipe-version;
- an instruction to **read and apply `skills/ralhf/references/feedback-routing.md`** (its rubric) and nothing else.

The subagent decides between exactly two sinks — the **extractor feedback endpoint** (`ralhf-extract` skill → `ralhf_client.py feedback`) and **RaLHF's Remember flow** (`ralhf`, `references/remember.md`) — records via the chosen path, and returns a one-line result. If it reports `needs_recipe_work`, run the `ralhf-extract` correction flow yourself. You never name or call the memory/feedback tool directly — the subagent owns that decision.

## Where the flow lives

- **`SKILL.md`** — canonical full skill specification (persona, five-phase flow, key rules, worked examples)
- **`PHASES.md`** — orientation map for developers browsing the repo (phase table, hook list, ASCII diagram). Defers to SKILL.md for detail.
- **`skills/ralhf/references/`** — feedback-routing rubric (the classifier subagent's spec), feedback protocol, Gmail query templates, connector pattern table, and other skill subpages

Follow RaLHF's lead through all five phases. Do not shortcut the flow. In particular: **do not start executing before the user confirms the plan.**
