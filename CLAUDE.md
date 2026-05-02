# CLAUDE.md — RaLHF Plugin

This file has two parts:

1. **Runtime rules** — how Claude must behave when this plugin is loaded into a user's session.
2. **Developer guide** — how to navigate, modify, and extend the plugin's source.

If you're modifying the plugin, scroll to **§ Developer guide**. If you're using the plugin (or testing it), the runtime rules in §1 are load-bearing — do not relax them without understanding why they exist.

---

## § 1. Runtime rules

### Mandatory: RaLHF skill first

Before responding to ANY user message, invoke the `ralhf:ralhf` skill.

This is not optional. This is not conditional. Every user turn begins with context planning.

- Do NOT answer the user's question first and then invoke the skill
- Do NOT skip the skill because you think you already have enough context
- Do NOT read files, search the web, or call any other tool before invoking the skill
- Do NOT reason that "this is just a conversation" or "this is a simple question" — the skill handles that judgment, not you
- `AskUserQuestion` is **blocked** by a PreToolUse hook. Clarifications happen inside the skill's Phase 2 staged check-ins as plain text.

**Exceptions (the only ones):**

1. The user is already inside a RaLHF phase (responding to a confirmation prompt, or mid-Execute / Remember).
2. The user explicitly says "skip context" or "no RaLHF" on this turn.
3. The user is asking a meta-question about the skill/plugin itself (e.g., "how does RaLHF work?", "what does this hook do?", or anything development-related — see §2).
4. Pure trivia with zero task ("capital of France?", "what's 2+2").

### Why the rule exists

RaLHF's value proposition is that every task is informed by the user's personal context. Without the gate, responses are generic — exactly the failure mode the plugin exists to prevent. The confirmation gate also keeps the user in the loop on which connectors get queried (Gmail, Calendar, Drive, etc.) and lets them shape the package before Claude spends tokens.

### The hard gate

The hard gate sits at the **end of Phase 3** (final pre-handoff check-in, plus Library refresh ask when the source-promotion queue is non-empty). Do not start executing before the user confirms the package.

---

## § 2. Developer guide

### Plugin identity

| Field | Value |
|---|---|
| Name | `ralhf` |
| Version | `2.4.3` (in [`.claude-plugin/plugin.json`](./.claude-plugin/plugin.json)) |
| Author | Bot Food Corporation |
| MCP backend | `https://backend.ralhf.ai/mcp` (in [`.mcp.json`](./.mcp.json)) |

Bump the version in `plugin.json` whenever you ship a meaningful behavior change. Patch for wording / prompt tuning, minor for new phases or hooks, major for breaking flow changes.

### Canonical source of truth

> **`skills/ralhf/SKILL.md` is canonical.** If `PHASES.md`, `README.md`, or this file disagrees with `SKILL.md`, **`SKILL.md` wins.** Update the canonical first, then propagate.

| Doc | Role |
|---|---|
| [`skills/ralhf/SKILL.md`](./skills/ralhf/SKILL.md) | Canonical spec — persona, five-phase flow, key rules, worked examples |
| [`PHASES.md`](./PHASES.md) | One-page orientation map. Defers to `SKILL.md` |
| [`README.md`](./README.md) | External-facing intro and submission doc |
| `CLAUDE.md` (this file) | Runtime rules + developer guide |
| `skills/ralhf/references/*.md` | Detailed protocols (feedback, Gmail, connectors, decomposition) |

### Repo layout

```
RaLHF/
├── .claude-plugin/plugin.json    # Plugin manifest (name, version, author, keywords)
├── .mcp.json                     # RaLHF MCP server connection
├── skills/
│   ├── ralhf/                    # Core skill — five-phase flow + persona
│   │   ├── SKILL.md              # Canonical spec
│   │   └── references/
│   │       ├── context-decomposition.md
│   │       ├── feedback-protocol.md
│   │       ├── gmail-supplementation.md
│   │       └── connector-patterns.md
│   ├── learn/SKILL.md            # /ralhf:learn — one-shot fact save
│   ├── personalize/SKILL.md      # /ralhf:personalize — manual Phase 1
│   ├── sync-back/SKILL.md        # /ralhf:sync-back — manual Phase 5 with review
│   └── feed-ralhf/SKILL.md       # /ralhf:feed-ralhf — end-of-session dump
├── hooks/
│   ├── hooks.json                # Wires events to scripts/markdown
│   ├── ralhf-init.md             # SessionStart primer
│   ├── user-prompt-gate.md       # UserPromptSubmit gate text
│   └── pretool-askuser-block.json# PreToolUse block reason
├── scripts/
│   ├── print-hook.py             # Reads a file and prints it (used by SessionStart, UserPromptSubmit, PreToolUse)
│   ├── track-context-tool.py     # PostToolUse — flags that a context tool ran
│   ├── track-feedback-saved.py   # PostToolUse — flags that save_context_feedback ran
│   ├── prompt-context-feedback.py# Stop hook — blocks exit until feedback saved
│   └── cleanup-session.py        # SessionEnd — temp file cleanup
├── PHASES.md
├── README.md
└── CLAUDE.md
```

### The five phases — at a glance

| Phase | Code path |
|---|---|
| **0 — Load** | `get_instructions` (read word-for-word — the `personalized` block is **first-class input**, not a side-note) → `get_wiki_catalog` |
| **1 — Discover** | Parallel drill: `browse_wiki` + `batch_fetch` for wiki/docs, plus Claude memory + local files + session state. Inventory MCP connector surface. |
| **2 — Propose** | Up to 2 staged check-ins, **one CTA per message**. Turn 2a starting context (always) → Turn 2b connector flow (when verified-present). |
| **3 — Confirm** | Up to 4 messages: 3a gap pass → 3b safety re-confirm (when applicable) → 3c final pre-handoff check-in → 3d Library refresh ask (when queue non-empty). **Hard gate.** |
| **4 — Execute** | Handoff line → drop persona. Claude opens with handoff ack + scope line. |
| **5 — Remember** | Post-task `feed-ralhf` ask. Stop hook backstops `save_context_feedback`. |

### MCP tools (provided by the RaLHF backend)

Eight tools. Reference details in `SKILL.md` § "RaLHF MCP Tools".

| Tool | Phase | Notes |
|---|---|---|
| `get_instructions` | 0 | Returns generic + personalized rules. Personalized rules are **first-class**, supersede generic strategy. Quota-exempt. Call once per session. |
| `get_wiki_catalog` | 0/1 | Full grouped map. |
| `browse_wiki` | 1 | Drill by `page_type` or `tag`, paginated. Replaces the removed `search` tool. |
| `batch_fetch` | 1 | **Always returns a list**, even for one item. **Cap ~5 items per call.** Fetch wiki pages first (so `sources[]` is in hand), then documents in a separate call. Large batches can spill to a file — see SKILL.md § 2.6. |
| `remember` | 2–5 | ≤1000 chars. Optional `dimension`: `food_and_dining`, `health`, `home_and_auto`, `identity`, `money`, `shopping`, `entertainment`, `travel`, `work_and_learning`, `social_and_digital_life`. |
| `start_file_upload` | 3 | Single-use URL + bearer, expires in minutes. POST `multipart/form-data` field `file`. |
| `check_file_upload_status` | 5 | States: `pending`, `processing`, `dispatched`, `generated`, `partial`, `document_only`, `rejected`, `failed`. Don't poll tightly. |
| `save_context_feedback` | 5 | Structured postmortem. Stop hook forces this before session exit. |

### Hook architecture

| Event | File | Job |
|---|---|---|
| `SessionStart` | `scripts/print-hook.py hooks/ralhf-init.md` | Primes the session — "skill is active, invoke on every turn". |
| `UserPromptSubmit` | `scripts/print-hook.py hooks/user-prompt-gate.md` | Forces skill invocation on every user turn. Covers casual framings ("lets X", "how about X"). |
| `PreToolUse` (matcher: `[Aa]sk\|[Qq]uestion\|[Cc]larif\|[Pp]rompt[Uu]ser`) | `scripts/print-hook.py hooks/pretool-askuser-block.json` | Blocks `AskUserQuestion` so Claude can't gather requirements before the skill fires. |
| `PostToolUse` (matcher: `mcp__.*__(get_wiki_catalog\|browse_wiki\|batch_fetch)`) | `scripts/track-context-tool.py` | Marks that a context tool ran (used by Stop hook logic). |
| `PostToolUse` (matcher: `mcp__.*__save_context_feedback`) | `scripts/track-feedback-saved.py` | Marks feedback as saved (used by Stop hook logic). |
| `Stop` | `scripts/prompt-context-feedback.py` | Blocks session exit until `save_context_feedback` has run. |
| `SessionEnd` | `scripts/cleanup-session.py` | Deletes temp files. |

The trackers and Stop hook coordinate via tiny session-scoped state files — read each script before changing matchers, since the Stop hook's blocking logic depends on what `track-context-tool.py` and `track-feedback-saved.py` write.

### Where to make each kind of change

| Change | Edit |
|---|---|
| Persona, greeting, phase flow, key rules, worked examples | [`skills/ralhf/SKILL.md`](./skills/ralhf/SKILL.md) |
| Retrieval / MCP tool logic | `SKILL.md` + [`references/context-decomposition.md`](./skills/ralhf/references/context-decomposition.md) |
| Feedback / sync behavior | [`references/feedback-protocol.md`](./skills/ralhf/references/feedback-protocol.md) |
| Gmail query templates | [`references/gmail-supplementation.md`](./skills/ralhf/references/gmail-supplementation.md) |
| Connector pattern table | [`references/connector-patterns.md`](./skills/ralhf/references/connector-patterns.md) |
| MCP backend URL | [`.mcp.json`](./.mcp.json) + update `README.md` if user-visible |
| Hook wiring | [`hooks/hooks.json`](./hooks/hooks.json) + the file the hook references |
| New slash command | New `skills/<name>/SKILL.md` directory. Invoked by typing `/<name>`. Update `README.md` slash-command table. |
| Plugin metadata (name, version, keywords) | [`.claude-plugin/plugin.json`](./.claude-plugin/plugin.json) |
| Phase **names**, **hook list**, or **top-level shape** | `PHASES.md` (otherwise leave it alone — per-phase detail belongs in `SKILL.md`) |
| External-facing description | `README.md` |

### Conventions to preserve

- **One ask per message in Phases 2 and 3.** Stacked CTAs get ignored. Every check-in carries a single ask.
- **Persona is RaLHF, not Claude, until handoff.** Phases 0–3 stay in character. Phase 4 opens with Claude's own handoff acknowledgment.
- **Cite, don't fabricate.** Wiki pages get cited in italics; URLs are never invented. Thin context gets flagged, not glossed.
- **Personalized rules from `get_instructions` are first-class.** Apply them in every phase. They supersede the generic strategy.
- **Maximum Relevant Context (MRC).** Generous, not conservative. 30%-relevance threshold. The downstream model can ignore what it doesn't need.
- **Gmail-sourced data is not saved via `remember`.** See `feed-ralhf/SKILL.md` and `references/gmail-supplementation.md` for the rules.
- **Topics on `remember`:** Auto-extracted. Only manually tag for status (`completed`, `in-progress`, `blocked`) or component names. Don't tag generic topics like `debugging` or `authentication` — extraction handles those.
- **`batch_fetch` discipline:** wiki pages first, documents second, ~5 items per call. Always returns a list.

### Things to avoid

- **Don't shortcut the flow.** No executing before Phase 3 confirmation. The hard gate is the product.
- **Don't add `AskUserQuestion` calls.** It's blocked by hook for a reason — clarifications belong in Phase 2 staged plain-text check-ins.
- **Don't bypass the Stop hook.** `save_context_feedback` is mandatory; if it's painful, fix the prompt, don't disable the gate.
- **Don't drop the persona early.** RaLHF stays in character through Phase 3. Premature handoff confuses the user.
- **Don't restate `feed-ralhf` pre-handoff.** That ask happens in Phase 5, after the user sees Claude's output. Surfacing it pre-handoff clutters the green-light moment.
- **Don't duplicate spec content across files.** `SKILL.md` is canonical. `PHASES.md` and `README.md` link to it; they don't restate it.

### Testing the plugin

There is no automated test suite. Manual loop:

1. Reload the plugin in a Claude Code session (or fresh session if hooks changed).
2. Trigger each phase with a representative task (work / personal / safety-relevant / casual framing).
3. Verify the SessionStart and UserPromptSubmit primers fire.
4. Verify `AskUserQuestion` is blocked when Claude tries it.
5. Verify the Stop hook blocks exit until `save_context_feedback` runs.
6. Check the `/ralhf:learn`, `/ralhf:personalize`, `/ralhf:sync-back`, `/ralhf:feed-ralhf` slash commands each work end-to-end (plugin skills are namespaced).

When you change a hook script, restart the Claude Code session — hook commands are spawned fresh per event, but the matcher/wiring in `hooks.json` is read at session start.

### Helpful entry points when modifying

- **Adding a new MCP tool:** declare it in the `RaLHF MCP Tools` table in `SKILL.md`, then thread its usage into the relevant phase. If it needs a tracker, mirror `track-context-tool.py` / `track-feedback-saved.py`.
- **Adding a new slash command:** create `skills/<name>/SKILL.md` with frontmatter (`name`, `description`). Keep the description tight — it's how the user discovers the command. Update `README.md`.
- **Tuning the prompt gate:** edit `hooks/user-prompt-gate.md`. The casual-framing examples are load-bearing — they prevent Claude from rationalizing skip on phrasings like "lets try X".
- **Tuning the SessionStart primer:** edit `hooks/ralhf-init.md`. Keep it short and imperative.

### When in doubt

Re-read `skills/ralhf/SKILL.md`. It is the source of truth. Everything else exists to support it.
