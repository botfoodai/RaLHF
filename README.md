# RaLHF — Personal Context Engineer for your AI assistant (dev variant)

> Gives your AI assistant a personal context engineer. Before any task, RaLHF assembles a context package from your personal wiki, the assistant's memory, local files, and connected apps — and shows you the plan before the assistant touches the work.

Built by [Bot Food](https://botfood.ai) on the [RaLHF](https://ralhf.ai) MCP server.

[![Version](https://img.shields.io/badge/version-3.6.5-blue.svg)](.claude-plugin/plugin.json)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](./LICENSE)
[![MCP](https://img.shields.io/badge/MCP-backend.ralfh--dev.com-orange.svg)](https://backend.ralhf.ai/mcp)

> **Dev canonical.** This is the canonical source for the ralhf variant family — `plugins/ralhf/` (prod) is generated from this directory via `scripts/sync-plugin-variants.py`. It points at the dev RaLHF MCP (`backend.ralfh-dev.com`) so iteration here doesn't affect prod customers. **Edit here, sync to prod when ready.**

---

## Why this exists

Generic AI answers are the default failure mode of every assistant. The model has no idea who you are, what you've already decided, what your team calls things, or which of your past projects matter. So it produces something competent but anonymous — and you spend the next five turns correcting it.

**RaLHF fixes that by intervening *before* the assistant executes.** On every user message, RaLHF runs a five-phase flow that gathers everything relevant to the task — from your RaLHF wiki, the assistant's memory, your local project, and your connected apps — proposes a plan, and waits for your green light before handing the assembled package to the assistant.

---

## The flow

**Load → Discover → Propose → Confirm → Execute → Remember**

| Phase | What happens |
|---|---|
| **0a — Triage & ask-first gate** | On every real task, RaLHF names the task, **recommends** whether to pull context or hand straight to the assistant, and asks `(yes / no)` — then waits. The recommendation is computed from the prompt (no lookups): personal-context signals → pull; self-contained tasks → skip; new users lean pull. Trivia / plugin meta-questions skip the gate silently. Only `get_my_mcp_usage` runs before the reply. |
| **0 — Load** | On "pull": silent pull of personalized retrieval rules (`get_instructions`) and the wiki map (`get_wiki_catalog`). No separate greeting — identity rode along in the gate. The light flow (pull on a self-contained task) skips the catalog. |
| **1 — Discover** | Parallel drill: relevant wiki pages, the assistant's existing memory, local project files, session state, and the MCP connector surface. Follows wikilinks and triages source documents. |
| **2 — Propose** | Staged check-ins (Turn 2a / 2b / 2c) — one ask per message. Soft asks first, then connector flow when Gmail / Calendar / Drive / Jira / etc. could help. |
| **3 — Confirm** | Surfaces gaps + final pre-handoff check-in + Library-refresh ask (promotes new Drive/Cowork/memory items via upload/`remember`). **Hard gate.** No execution until the user says go. A silent context-gathering postmortem (`save_context_feedback`) fires here at handoff. |
| **4 — Execute** | Hands the assembled package to the assistant with citations and scope notes. |
| **5 — Remember** | Post-task `feed-ralhf` ask captures durable facts (dense summary + file uploads) and saves approved artifacts to the Library. The postmortem already fired at handoff. |

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

---

## Installation (dev variant)

This dev variant points at `backend.ralfh-dev.com/mcp`. Install via the internal `botfoodai/claude-plugins` marketplace.

For the production variant (points at `backend.ralhf.ai/mcp`), see `plugins/ralhf/` or install from [`botfoodai/RaLHF`](https://github.com/botfoodai/RaLHF).

### Claude Code

Build the distributable zip, unzip it, then install the extracted plugin folder:

```bash
./build-plugin.sh
unzip dist/ralhf-3.10.1.zip
/plugin install ./ralhf
```

### Codex

This repo also includes `.codex-plugin/plugin.json`, so Codex can load the same `skills/` directory and `.mcp.json` server definition.

For local development, register this repo as the marketplace root, then install `ralhf` from it:

```bash
codex plugin marketplace add .
codex plugin add ralhf@ralhf
```

For GitHub installs:

```bash
codex plugin marketplace add botfoodai/RaLHF --ref main
codex plugin add ralhf@ralhf
```

The marketplace entry points `./plugins/ralhf` back to this repo through a local symlink, so Codex installs the existing RaLHF plugin source instead of a copied snapshot. After installing or updating the plugin, start a new Codex thread so the skills and MCP tools are loaded.

Codex loads the root `hooks.json` file through `.codex-plugin/plugin.json` as plugin-bundled lifecycle hooks. On first install or after a hook change, run `/hooks` in Codex and trust the RaLHF hooks when prompted. Once installed, run `/ralhf-intro` to verify the MCP connection. Normal tasks should use `ralhf-start`; if it does not auto-fire, type `/ralhf-start`.

---

## Architecture

```
plugins/ralhf/
├── .claude-plugin/
│   └── plugin.json
├── .codex-plugin/
│   └── plugin.json
├── .agents/plugins/marketplace.json # Codex marketplace catalog
├── .mcp.json                       # dev MCP URL
├── hooks.json                      # Codex plugin-bundled lifecycle hooks
├── CLAUDE.md                       # plugin-level rules (skill-first, AskUserQuestion ban)
├── PHASES.md                       # orientation map
├── README.md                       # this file
├── LICENSE / NOTICE / TRADEMARK.md
├── hooks/
│   ├── hooks.json                  # SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / Stop / SessionEnd
│   ├── ralhf-init.md               # SessionStart primer
│   ├── user-prompt-gate.md         # per-turn skill-invocation gate
│   └── pretool-askuser-block.json  # AskUserQuestion deny
├── scripts/                        # python hook helpers (require python on PATH)
│   ├── print-hook.py
│   ├── track-context-tool.py
│   ├── track-feedback-saved.py
│   ├── prompt-context-feedback.py
│   └── cleanup-session.py
├── plugins/ralhf -> ..             # Codex marketplace pointer to this plugin
└── skills/
    ├── ralhf-start/                # the main five-phase skill
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
