# RaLHF — Personal Context Engineer for Claude

> Turns Claude into your personal context engineer. Before any task, RaLHF assembles a context package from your personal wiki, Claude's memory, local files, and connected apps — and shows you the plan before Claude touches the work.

Built by [Bot Food](https://botfood.ai) on the [RaLHF](https://ralhf.ai) MCP server.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](.claude-plugin/plugin.json)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](./LICENSE)
[![MCP](https://img.shields.io/badge/MCP-backend.ralhf.ai-green.svg)](https://backend.ralhf.ai/mcp)

---

## Why this exists

Generic AI answers are the default failure mode of every assistant. The model has no idea who you are, what you've already decided, what your team calls things, or which of your past projects matter. So it produces something competent but anonymous — and you spend the next five turns correcting it.

**RaLHF fixes that by intervening *before* Claude executes.** On every user message, RaLHF runs a five-phase flow that gathers everything relevant to the task — from your RaLHF wiki, Claude's memory, your local project, and your connected apps — proposes a plan, and waits for your green light before handing the assembled package to Claude. Nothing ships until you confirm.

The result: Claude's first attempt is grounded in *your* context, not a generic prior.

---

## The flow

**Load → Discover → Propose → Confirm → Execute → Remember**

| Phase | What happens |
|---|---|
| **0 — Load** | Warm three-paragraph greeting. Silently pulls your personalized retrieval rules (`get_instructions`) and a full map of your wiki (`get_wiki_catalog`). |
| **1 — Discover** | Parallel drill: relevant wiki pages, Claude's existing memory, local project files, session state, and the connector inventory. Follows wikilinks and triages source documents. |
| **2 — Propose** | Shows what was found in up to two staged check-ins — one ask per message. First the starting context, then a connector flow when Gmail / Calendar / Drive / Jira / etc. could help. |
| **3 — Confirm** | Surfaces gaps as a structured list, re-confirms safety-relevant details, and poses the final pre-handoff check-in. **Hard gate sits here.** No execution until you say go. |
| **4 — Execute** | Hands the assembled package to Claude with citations and scope notes. Claude opens with a handoff acknowledgment, flags thin context, and cites wiki pages in italics. |
| **5 — Remember** | Post-task `feed-ralhf` ask captures durable facts and a structured postmortem (`save_context_feedback`) so the next session is sharper. A Stop hook backstops the feedback save. |

See [`PHASES.md`](./PHASES.md) for the orientation map and [`skills/ralhf/SKILL.md`](./skills/ralhf/SKILL.md) for the canonical spec.

---

## Installation

RaLHF is a Claude Code plugin. Drop the folder into your plugins directory and Claude Code will auto-discover the manifest, skills, hooks, and MCP server config.

**Requirements:**
- A [RaLHF account](https://ralhf.ai) — the plugin points at `https://backend.ralhf.ai/mcp`
- Python 3 on PATH (used by the hooks)
- Optional connectors authorized in your RaLHF account (Gmail, Calendar, Drive, Jira, QuickBooks, etc.) — RaLHF only queries what you approve

The MCP server is wired up in [`.mcp.json`](./.mcp.json):

```json
{
  "mcpServers": {
    "ralhf-mcp": {
      "type": "http",
      "url": "https://backend.ralhf.ai/mcp"
    }
  }
}
```

---

## Slash commands

> **Note on naming:** Once installed, slash commands are namespaced under the plugin. Type `/ralhf:learn`, `/ralhf:personalize`, etc. The shorthand `/learn` used below means `/ralhf:learn` in your session.

| Command | What it does |
|---|---|
| `/ralhf:personalize` | Manual Phase 1 — top up context mid-conversation when the topic shifts |
| `/ralhf:learn <fact>` | Teach RaLHF something new in one step (preferences, allergies, life events, constraints) |
| `/ralhf:sync-back` | Run Phase 5 manually with a review gate — preview what gets saved before it ships |
| `/ralhf:feed-ralhf` | End-of-session dump — dense summary + file uploads + structured feedback. Also fires automatically via the Phase 5 post-task ask |

---

## What's in the box

### Skills
- **`skills/ralhf/`** — the core skill. The five-phase persona, key rules, worked examples, and references for feedback protocol, Gmail query templates, connector pattern table, and context decomposition.
- **`skills/personalize/`**, **`skills/learn/`**, **`skills/sync-back/`**, **`skills/feed-ralhf/`** — slash-command skills that expose specific phases as one-shot actions.

### Hooks
| Event | File | Job |
|---|---|---|
| `SessionStart` | `hooks/ralhf-init.md` | Primer loaded at session start |
| `UserPromptSubmit` | `hooks/user-prompt-gate.md` | Forces skill invocation on every turn — covers casual phrasings ("lets X", "how about Y", "I want to Z") |
| `PreToolUse` | `hooks/pretool-askuser-block.json` | Denies `AskUserQuestion` until the skill has fired — prevents Claude from gathering requirements before context is assembled |
| `PostToolUse` | `scripts/track-context-tool.py`, `scripts/track-feedback-saved.py` | Tracks which RaLHF tools ran and whether feedback was saved |
| `Stop` | `scripts/prompt-context-feedback.py` | Blocks session exit until `save_context_feedback` runs |
| `SessionEnd` | `scripts/cleanup-session.py` | Temp file cleanup |

### MCP tools (provided by the RaLHF backend)
| Tool | Purpose |
|---|---|
| `get_instructions` | Returns generic + personalized retrieval rules learned from this user's prior sessions |
| `get_wiki_catalog` | Full grouped map of the user's wiki — narrative, page IDs, tags, wikilinks |
| `browse_wiki` | Drill into the catalog by `page_type` or `tag` with pagination |
| `batch_fetch` | Read full content for one or many wiki pages / source documents in a single round-trip |
| `remember` | Save a fact, preference, or correction (≤1000 chars), optionally tagged with a life-area dimension |
| `start_file_upload` | Get a short-lived upload URL + bearer token to ingest a user file |
| `check_file_upload_status` | Poll the status of an uploaded file |
| `save_context_feedback` | Submit a structured postmortem on how context assembly went |

---

## Layout

```
RaLHF/
├── .claude-plugin/plugin.json    # Plugin manifest
├── .mcp.json                     # RaLHF MCP server connection
├── skills/
│   ├── ralhf/                    # Core skill — five-phase flow + persona
│   │   ├── SKILL.md
│   │   └── references/           # Feedback protocol, Gmail templates,
│   │                             # connector patterns, context decomposition
│   ├── learn/SKILL.md            # /ralhf:learn — teach RaLHF a new fact
│   ├── personalize/SKILL.md      # /ralhf:personalize — manual Phase 1 top-up
│   ├── sync-back/SKILL.md        # /ralhf:sync-back — manual Phase 5 with review
│   └── feed-ralhf/SKILL.md       # /ralhf:feed-ralhf — end-of-session dump
├── hooks/                        # SessionStart, UserPromptSubmit, PreToolUse,
│   │                             # Stop, SessionEnd
│   └── hooks.json
├── scripts/                      # Tool tracking + Stop-hook feedback gate
├── CLAUDE.md                     # Plugin-level invocation rules
├── PHASES.md                     # Phase-by-phase orientation map
└── README.md                     # This file
```

---

## Design principles

- **Maximum Relevant Context (MRC).** RaLHF is generous, not conservative. If there's a 30% chance a piece of context helps, it goes in. The downstream model can ignore what it doesn't need — but it can't use what it doesn't have.
- **Show the plan, don't just execute.** The whole point of the confirmation gate is that you see what's being assembled and have the final say. No silent assumptions about what your task needs.
- **One ask per message.** Stacked questions get ignored. Every check-in carries a single CTA.
- **Cite, don't fabricate.** Wiki pages get cited in italics; URLs are never invented. If something is thin, RaLHF flags it instead of glossing.
- **Persona drops at handoff.** RaLHF does the context work. Claude does the task. The baton change is explicit on both sides.
- **Capture is mandatory, not aspirational.** A Stop hook ensures `save_context_feedback` runs before exit. Next session is always sharper than the last.

---

## Documentation

| File | Purpose |
|---|---|
| [`PHASES.md`](./PHASES.md) | One-page orientation map — five phases, hook infrastructure, ASCII diagram |
| [`CLAUDE.md`](./CLAUDE.md) | Plugin-level invocation rules and exceptions |
| [`skills/ralhf/SKILL.md`](./skills/ralhf/SKILL.md) | Full skill spec — persona, key rules, worked examples |
| [`skills/ralhf/references/feedback-protocol.md`](./skills/ralhf/references/feedback-protocol.md) | How `save_context_feedback` is structured |
| [`skills/ralhf/references/gmail-supplementation.md`](./skills/ralhf/references/gmail-supplementation.md) | Gmail query templates for the connector flow |
| [`skills/ralhf/references/connector-patterns.md`](./skills/ralhf/references/connector-patterns.md) | When and how to query each connector |
| [`skills/ralhf/references/context-decomposition.md`](./skills/ralhf/references/context-decomposition.md) | How tasks decompose into context dimensions |

---

## License

The plugin source code in this repository is licensed under the [Apache License, Version 2.0](./LICENSE). See [`NOTICE`](./NOTICE) for attribution requirements.

**Trademarks are separate.** "RaLHF" and "Bot Food" are trademarks of Bot Food Corporation. The Apache 2.0 license does not grant rights to use these marks — see [`TRADEMARK.md`](./TRADEMARK.md) for the full policy. In short: fork the code freely, but pick a different name for your fork.

The **RaLHF backend service** at `backend.ralhf.ai` is a separate, proprietary service governed by the Terms of Service at [ralhf.ai](https://ralhf.ai), not by this repository's license.

## Author

Built by [Bot Food Corporation](https://botfood.ai). The MCP backend lives at [ralhf.ai](https://ralhf.ai).

For questions, feedback, or to report issues, reach out at the RaLHF site.
