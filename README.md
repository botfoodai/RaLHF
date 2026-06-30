# RaLHF — Personal Context Engineer for your AI assistant

> Gives your AI assistant a personal context engineer. Ask for it — type `/ralhf` or say "use ralhf" — and RaLHF assembles a context package from your personal wiki, the assistant's memory, local files, and connected apps, then shows you the plan before the assistant touches the work.

Built by [Bot Food](https://botfood.ai) on the [RaLHF](https://ralhf.ai) MCP server.

[![Version](https://img.shields.io/badge/version-3.15.7-blue.svg)](.claude-plugin/plugin.json)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](./LICENSE)
[![MCP](https://img.shields.io/badge/MCP-backend.ralhf.ai-orange.svg)](https://backend.ralhf.ai/mcp)

> **Production plugin source.** The public production build of the RaLHF plugin for Claude and Codex, wired to the production RaLHF MCP endpoint (`https://backend.ralhf.ai/mcp`).

---

## Why this exists

Generic AI answers are the default failure mode of every assistant. The model has no idea who you are, what you've already decided, what your team calls things, or which of your past projects matter. So it produces something competent but anonymous — and you spend the next five turns correcting it.

**RaLHF fixes that by intervening *before* the assistant executes.** When you invoke it — `/ralhf` or "use ralhf" — RaLHF runs a five-phase flow that gathers everything relevant to the task — from your RaLHF wiki, the assistant's memory, your local project, and your connected apps — proposes a plan, and waits for your green light before handing the assembled package to the assistant. It stays out of the way on tasks where you don't ask for it.

---

## The flow

**Load → Discover → Propose → Confirm → Execute → Remember**

| Phase | What happens |
|---|---|
| **0a — Open & classify** | RaLHF runs only when you invoke it (`/ralhf`, "use ralhf", "pull my context"). Invoking IS the opt-in, so there's **no yes/no gate** — RaLHF gives one brief identity line naming the task, then goes straight to pulling. A fast mental classification (no MCP calls) picks the full flow vs. a leaner light flow for self-contained tasks. |
| **0 — Load** | Silent pull of personalized retrieval rules (`get_instructions`). No wiki catalog up front — discovery runs through `browse_wiki` in Phase 1, and `get_wiki_catalog` is only a fallback if `browse_wiki` comes back empty. No separate greeting — identity rode along in the opening line. |
| **1 — Discover** | Parallel drill: relevant wiki pages, the assistant's existing memory, local project files, session state, and the MCP connector surface. Follows wikilinks and triages source documents. |
| **2 — Propose** | Posts the assembled context as the **Turn 2a inventory** — the four-source list with an "anything to add or remove?" ask; a proactive gap-flag fires only when a suspected document is missing. |
| **3 — Confirm** | Connector **permission** ask, then a brief **pre-handoff check-in** — RaLHF affirms the package and asks for the green light — then the Library-refresh ask. **Hard gate.** No execution until the user gives the go-ahead. A silent postmortem (`save_context_feedback`) fires at handoff. |
| **4 — Execute** | Hands the assembled package to the assistant with citations and scope notes. |
| **5 — Remember** | Post-task `feed-ralhf` ask captures durable facts (dense summary + file uploads) and saves approved artifacts to the Library — on "yes" the saves are presented as a short text list to keep/drop/edit before saving. `/ralhf-sync` does the same; typed `/feed-ralhf` stays headless. The postmortem already fired at handoff. |

See [`PHASES.md`](./PHASES.md) for the orientation map and [`skills/ralhf/SKILL.md`](./skills/ralhf/SKILL.md) for the canonical spec.

---

## Skills

| Skill | Trigger | What it does |
|---|---|---|
| `ralhf` | `/ralhf:ralhf` or "use ralhf" / "pull my context" | The main five-phase flow |
| `ralhf-learn` | `/ralhf:ralhf-learn <fact>` | One-shot save of a preference, fact, constraint, or goal |
| `ralhf-sync` | `/ralhf:ralhf-sync` | Manual Phase 5 with a review gate before saves |
| `ralhf-intro` | `/ralhf:ralhf-intro` | First-run setup check + onboarding intro |
| `feed-ralhf` | `/ralhf:feed-ralhf` | Autonomous end-of-session dump: dense summary + file uploads + postmortem |

---

## Installation

This plugin points at the production RaLHF MCP endpoint (`https://backend.ralhf.ai/mcp`). Install from the Claude marketplace or Codex marketplace as documented below.

### Claude Code

Build the distributable zip, unzip it, then install the extracted plugin folder:

```bash
./build-plugin.sh
unzip dist/ralhf-3.15.7.zip
/plugin install ./ralhf
```

### Codex

This repo also includes `.codex-plugin/plugin.json`, so Codex can load the same `skills/` directory and `.mcp.json` server definition.

This repository is the plugin source, not the marketplace root. Keep Codex marketplace catalog metadata in `botfoodai/ralhf-codex-marketplace` so the RaLHF plugin package does not vendor marketplace state. Use that marketplace repository for Codex installation instructions. After installing or updating the plugin, start a new Codex thread so the skills and MCP tools are loaded.

Codex loads `hooks/codex-hooks.json` through `.codex-plugin/plugin.json` as plugin-bundled lifecycle hooks. The Codex hook config reuses the same scripts and hook prompt files as Claude, but keeps the Codex-specific config shape separate from Claude's `hooks/hooks.json`. On first install or after a hook change, run `/hooks` in Codex and trust the RaLHF hooks when prompted. Once installed, run `/ralhf-intro` to verify the MCP connection. When you want RaLHF to pull your context for a task, type `/ralhf` or say "use ralhf".

---

## Architecture

```
plugins/ralhf/
├── .claude-plugin/
│   └── plugin.json
├── .codex-plugin/
│   └── plugin.json
├── .mcp.json                       # production MCP URL
├── CLAUDE.md                       # plugin-level rules (invoke-on-request)
├── PHASES.md                       # orientation map
├── README.md                       # this file
├── LICENSE / NOTICE / TRADEMARK.md
├── hooks/
│   ├── hooks.json                  # Claude lifecycle hooks
│   ├── codex-hooks.json            # Codex plugin-bundled lifecycle hooks
│   └── ralhf-init.md               # SessionStart primer
├── scripts/                        # python hook helpers (require python on PATH)
│   ├── print-hook.py
│   ├── track-context-tool.py
│   ├── track-feedback-saved.py
│   ├── prompt-context-feedback.py
│   └── cleanup-session.py
└── skills/
    ├── ralhf/                      # the main five-phase skill
    │   ├── SKILL.md
    │   └── references/             # decomposed sub-pages (15 files)
    ├── ralhf-learn/SKILL.md        # /ralhf:ralhf-learn — teach RaLHF a new fact
    ├── ralhf-sync/SKILL.md         # /ralhf:ralhf-sync — manual Phase 5 with review
    ├── ralhf-intro/SKILL.md        # /ralhf:ralhf-intro — setup check + intro
    └── feed-ralhf/SKILL.md         # /ralhf:feed-ralhf — session dump
```

---

## License

Apache-2.0 — see [LICENSE](./LICENSE). Trademark and usage policy in [TRADEMARK.md](./TRADEMARK.md).
