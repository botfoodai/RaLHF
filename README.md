# RaLHF — Personal Context Engineer for Claude (dev variant)

> Turns Claude into your personal context engineer. Before any task, RaLHF assembles a context package from your personal wiki, Claude's memory, local files, and connected apps — and shows you the plan before Claude touches the work.

Built by [Bot Food](https://botfood.ai) on the [RaLHF](https://ralhf.ai) MCP server.

[![Version](https://img.shields.io/badge/version-3.8.5-blue.svg)](.claude-plugin/plugin.json)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](./LICENSE)
[![MCP](https://img.shields.io/badge/MCP-backend.ralfh--dev.com-orange.svg)](https://backend.ralhf.ai/mcp)

> **Dev canonical.** This is the canonical source for the ralhf variant family — `plugins/ralhf/` (prod) is generated from this directory via `scripts/sync-plugin-variants.py`. It points at the dev RaLHF MCP (`backend.ralfh-dev.com`) so iteration here doesn't affect prod customers. **Edit here, sync to prod when ready.**

---

## Why this exists

Generic AI answers are the default failure mode of every assistant. The model has no idea who you are, what you've already decided, what your team calls things, or which of your past projects matter. So it produces something competent but anonymous — and you spend the next five turns correcting it.

**RaLHF fixes that by intervening *before* Claude executes.** On every user message, RaLHF runs a five-phase flow that gathers everything relevant to the task — from your RaLHF wiki, Claude's memory, your local project, and your connected apps — proposes a plan, and waits for your green light before handing the assembled package to Claude.

---

## The flow

**Load → Discover → Propose → Confirm → Execute → Remember**

| Phase | What happens |
|---|---|
| **0 — Load** | Greeting + silent pull of personalized retrieval rules (`get_instructions`) and full wiki map (`get_wiki_catalog`). Greeting tier (full / familiar / one-liner) is gated on `get_my_mcp_usage`. |
| **1 — Discover** | Parallel drill: relevant wiki pages, Claude's existing memory, local project files, session state, and the MCP connector surface. Follows wikilinks and triages source documents. |
| **2 — Propose** | Staged check-ins (Turn 2a / 2b / 2c) — one ask per message. Soft asks first, then connector flow when Gmail / Calendar / Drive / Jira / etc. could help. |
| **3 — Confirm** | Surfaces gaps + final pre-handoff check-in. **Hard gate.** No execution until the user says go. |
| **4 — Execute** | Hands the assembled package to Claude with citations and scope notes. |
| **5 — Remember** | Post-task `feed-ralhf` ask captures durable facts + structured postmortem (`save_context_feedback`). |

See [`PHASES.md`](./PHASES.md) for the orientation map and [`skills/ralhf-start/SKILL.md`](./skills/ralhf-start/SKILL.md) for the canonical spec.

---

## Skills

| Skill | Trigger | What it does |
|---|---|---|
| `ralhf-start` | Auto-fires on every user task | The main five-phase flow |
| `ralhf-learn` | `/ralhf:ralhf-learn <fact>` | One-shot save of a preference, fact, constraint, or goal |
| `ralhf-sync` | `/ralhf:ralhf-sync` | Manual Phase 5 with a review gate before saves |
| `ralhf-intro` | `/ralhf:ralhf-intro` | First-run setup check + onboarding intro |
| `feed-ralhf` | `/ralhf:feed-ralhf` | Autonomous end-of-session dump: dense summary + file uploads + postmortem |
| `ralhf-extract` | `/ralhf:ralhf-extract <url>` | Extract structured data from a webpage and author a reusable skill |
| `ralhf-schedule` | `/ralhf:ralhf-schedule add <url>` | Manage scheduled recurring extractions (add/remove/list/enable/disable) |
| `ralhf-schedule-run` | Internal (scheduled task) | Execute due scheduled extractions and cache results |

---

## Installation (dev variant)

This dev variant points at `backend.ralfh-dev.com/mcp`. Install via the internal `botfoodai/claude-plugins` marketplace.

For the production variant (points at `backend.ralhf.ai/mcp`), see `plugins/ralhf/` or install from [`botfoodai/RaLHF`](https://github.com/botfoodai/RaLHF).

---

## Architecture

```
plugins/ralhf/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json                       # dev MCP URL
├── CLAUDE.md                       # plugin-level rules (skill-first, AskUserQuestion ban)
├── PHASES.md                       # orientation map
├── README.md                       # this file
├── LICENSE / NOTICE / TRADEMARK.md
├── hooks/
│   ├── hooks.json                  # SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / Stop / SessionEnd
│   ├── ralhf-init.md               # SessionStart primer
│   ├── extractor-init.md           # SessionStart primer (extraction skills)
│   ├── user-prompt-gate.md         # per-turn skill-invocation gate
│   └── pretool-askuser-block.json  # AskUserQuestion deny
├── platform/
│   └── claude.md                   # tool mappings for Claude Code / Cowork (extraction)
├── scripts/                        # python hook helpers (require python on PATH)
│   ├── print-hook.py
│   ├── track-context-tool.py
│   ├── track-feedback-saved.py
│   ├── prompt-context-feedback.py
│   └── cleanup-session.py
└── skills/
    ├── ralhf-start/                # the main five-phase skill
    │   ├── SKILL.md
    │   └── references/             # decomposed sub-pages (15 files)
    ├── ralhf-learn/SKILL.md        # /ralhf:ralhf-learn — teach RaLHF a new fact
    ├── ralhf-sync/SKILL.md         # /ralhf:ralhf-sync — manual Phase 5 with review
    ├── ralhf-intro/SKILL.md        # /ralhf:ralhf-intro — setup check + intro
    ├── feed-ralhf/SKILL.md         # /ralhf:feed-ralhf — session dump
    ├── ralhf-extract/              # /ralhf:ralhf-extract — web data extraction
    │   ├── SKILL.md
    │   ├── config.json
    │   └── references/             # extraction sub-pages (16 files)
    ├── ralhf-schedule/             # /ralhf:ralhf-schedule — schedule manager
    │   ├── SKILL.md
    │   └── references/
    └── ralhf-schedule-run/SKILL.md # internal scheduled extraction executor
```

---

## License

Apache-2.0 — see [LICENSE](./LICENSE). Trademark and usage policy in [TRADEMARK.md](./TRADEMARK.md).
