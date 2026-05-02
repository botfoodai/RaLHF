# RaLHF — Personal Context Engineer for Claude

RaLHF turns Claude into your personal context engineer. Before Claude touches any task, RaLHF gathers relevant material from your RaLHF wiki, Claude's own memory, your local project files, and your connected apps — then hands a complete context package back to Claude to do the work. Nothing ships until you confirm the plan.

Built by [Bot Food](https://botfood.ai) on the [RaLHF](https://ralhf.ai) MCP server.

## What it does

The flow at a glance: **Load → Discover → Propose → Confirm → Execute → Remember**.

1. **Load** — Pulls your personalized retrieval rules and a map of your RaLHF wiki.
2. **Discover** — Drills into wiki pages, Claude's memory, local files, and connected apps in parallel.
3. **Propose** — Shows what was found in up to two staged check-ins (one ask per message).
4. **Confirm** — Surfaces gaps, confirms safety-relevant details, and gets your green light. Hard gate sits here.
5. **Execute** — Hands the assembled context off to Claude with citations and scope notes.
6. **Remember** — Captures durable facts and structured feedback for next time.

See [PHASES.md](./PHASES.md) for the canonical breakdown and [skills/ralhf/SKILL.md](./skills/ralhf/SKILL.md) for the full spec.

## Documentation

| File | Purpose |
|---|---|
| **[PHASES.md](./PHASES.md)** | One-page orientation map — five phases, hook infrastructure, ASCII diagram |
| **[CLAUDE.md](./CLAUDE.md)** | Plugin-level invocation rules and exceptions |
| **[skills/ralhf/SKILL.md](./skills/ralhf/SKILL.md)** | Full skill spec — persona, key rules, worked examples |
| **[skills/ralhf/references/](./skills/ralhf/references/)** | Feedback protocol, Gmail query templates, connector pattern table |

## Layout

```
RaLHF/
├── .claude-plugin/plugin.json    # Plugin manifest
├── .mcp.json                     # RaLHF MCP server connection
├── skills/
│   ├── ralhf/                    # Core skill — five-phase flow + persona
│   │   ├── SKILL.md
│   │   └── references/           # Feedback protocol, Gmail templates, connector patterns
│   ├── learn/SKILL.md            # /learn — teach RaLHF a new fact in one step
│   ├── personalize/SKILL.md      # /personalize — manual Phase 1 top-up
│   ├── sync-back/SKILL.md        # /sync-back — manual Phase 5 with review gate
│   └── feed-ralhf/SKILL.md       # /feed-ralhf — end-of-session dump
├── hooks/                        # SessionStart, UserPromptSubmit gate, PreToolUse block, Stop feedback prompt
├── scripts/                      # Tool-use tracking + Stop-hook feedback gate
├── CLAUDE.md                     # Plugin-level rules
├── PHASES.md                     # Phase-by-phase orientation
└── README.md                     # This file
```

## Slash commands

| Command | What it does |
|---|---|
| `/personalize` | Manual Phase 1 — top up context mid-conversation |
| `/learn` | Teach RaLHF a new fact or preference in one step |
| `/sync-back` | Run Phase 5 manually with a review gate |
| `/feed-ralhf` | End-of-session dump — dense summary + file uploads + structured feedback. Also fires automatically via the Phase 5 post-task ask. |

## Requirements

- A RaLHF account — points at `https://backend.ralhf.ai/mcp`
- Optional connectors (Gmail / Calendar / Drive / Jira / QuickBooks / etc.) — queried only after you approve
