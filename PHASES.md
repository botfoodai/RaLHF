# RaLHF ralhf-start — Orientation Map

> **Canonical spec:** [`skills/ralhf-start/SKILL.md`](skills/ralhf-start/SKILL.md). This file is a one-page orientation for developers browsing the repo — the phase shape, hook wiring, and where to look. If anything here disagrees with SKILL.md, **SKILL.md wins**.

Current skill version: see [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

---

## The five-phase flow

| Phase | One-liner | Full detail |
|---|---|---|
| **0a — TRIAGE & GATE** | Mental classification + ask-first gate. Fires `get_my_mcp_usage` (tier + new-user lean), then one message that names the task, recommends pull/skip, and asks `(yes / no)`. Trivial → skip RaLHF silently, no gate. Every real task → the gate. "pull" → full or light flow; "skip"/silence → direct handoff. | [SKILL.md → PHASE 0a](skills/ralhf-start/SKILL.md) + [task-triage.md](skills/ralhf-start/references/task-triage.md) |
| **0 — LOAD** | On "pull": silent two-stage loading — `get_instructions` → READ word-for-word → `get_wiki_catalog`. No separate greeting turn (identity lives in the gate). In the light flow (pull on a self-contained task), `get_wiki_catalog` is skipped. | [SKILL.md → PHASE 0](skills/ralhf-start/SKILL.md#phase-0-load-expertise--before-anything-else) |
| **1 — DISCOVER** | Silent 7-step parallel drill: wiki + the assistant memory + local files + session state. Follow `related_pages[]`, triage `sources[]` into fetch/skip, **informally** notice deep-context thin spots (drives Turn 2b mode A offers). The formal gap list builds in Phase 3. | [SKILL.md → PHASE 1](skills/ralhf-start/SKILL.md#phase-1-discover--look-through-ralhf-inventory-available-connectors) |
| **2 — PROPOSE** | **Show what was found.** Up to two staged check-ins, **one CTA per message**: Turn 2a starting context (always) → Turn 2b proactive flag (when RaLHF noticed a specific gap not already addressed). | [SKILL.md → PHASE 2](skills/ralhf-start/SKILL.md) |
| **3 — CONFIRM** | **Asking + finalizing.** Four steps: Step 3a connector pass (fires when any non-RaLHF connector is verified-present) → Step 3b final pre-handoff check-in (always, ≤25 words) → Step 3c Library refresh ask (when source-promotion queue non-empty) → **Step 3d context-gathering postmortem** (`save_context_feedback`, silent, once per session, grades Phases 0–3 with phase_4 = N/A). Hard gate sits at 3b green light. | [SKILL.md → PHASE 3](skills/ralhf-start/SKILL.md) |
| **4 — EXECUTE** | Handoff line → drop persona. The assistant opens with handoff ack + context-scope line, flags thin context, cites wiki pages in italics, never fabricates URLs. | [SKILL.md → PHASE 4](skills/ralhf-start/SKILL.md#phase-4-execute) |
| **5 — REMEMBER** | Post-task feed-ralhf ask (summary + files + artifact save) on wrap-up signal. The postmortem already fired at Step 3d, so it is NOT re-run here. The `Stop` hook stays a backstop: it blocks exit for `save_context_feedback` only when context tools were used but no postmortem was recorded (e.g. Step 3d was interrupted before it ran). | [SKILL.md → PHASE 5](skills/ralhf-start/SKILL.md#phase-5-remember--when-task-is-done) |

The hard gate sits at the end of Phase 3 — no execution until the user has explicitly confirmed the package (Step 3b green light) and resolved the Library refresh ask (Step 3c, when the source-promotion queue is non-empty).

---

## Hook infrastructure

| Hook | File | Purpose |
|---|---|---|
| `SessionStart` | `scripts/print-hook.py hooks/ralhf-init.md` | Primer loaded at session start. |
| `UserPromptSubmit` | `scripts/print-hook.py hooks/user-prompt-gate.md` | Forces skill invocation on every user turn (covers casual framings: "lets X", "how about X", "I want to X"). |
| `PreToolUse` | `scripts/print-hook.py hooks/pretool-askuser-block.json` | Denies `AskUserQuestion` with an "invoke the skill now" reason — keeps the assistant from gathering requirements before RaLHF fires. |
| `PostToolUse` | `scripts/track-context-tool.py`, `scripts/track-feedback-saved.py` | Track which context tools were used and whether `save_context_feedback` ran. |
| `Stop` | `scripts/prompt-context-feedback.py` | Backstop: blocks exit once if context tools ran but no postmortem was recorded (quiet once Step 3d saved feedback). |
| `SessionEnd` | `scripts/cleanup-session.py` | Per-session temp-file cleanup. |

---

## Visual

```
┌──────────────────────────────────────────────────────────────┐
│ PHASE 0a: TRIAGE & ASK-FIRST GATE                            │
│   (mental, no MCP except get_my_mcp_usage)                   │
│   Trivial → skip RaLHF silently, no gate                     │
│   Real task → get_my_mcp_usage, then ONE gate message:       │
│     name task + recommend (pull|skip) + ask (yes / no)       │
│       recommend PULL if personal-context signals             │
│       recommend SKIP if self-contained; new users lean pull  │
│     end turn — no further MCP until the reply                │
│   "pull" rich → full flow ; "pull" thin → light flow         │
│   "skip" / silence → direct handoff to the assistant         │
└─────────────────────────┬────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 0: LOAD (after "pull")                                 │
│   No separate greeting (identity was in the gate).           │
│   Silent 2-stage work:                                       │
│     Stage 1: get_instructions → READ & internalize           │
│              personalized rules                              │
│     Stage 2: get_wiki_catalog (with rules in hand)           │
│   Light flow: skip Stage 2                                   │
└─────────────────────────┬────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 1: DISCOVER (silent, 7 steps)                          │
│   1. Apply personalized rules + use catalog                  │
│   2. Check trigger signals                                   │
│   3. PARALLEL drill: wiki + memory + local + session state   │
│   4. Inventory MCP tool surface                              │
│   5. Follow related_pages wikilinks                          │
│   6. Triage source docs (fetch / skip — RaLHF decides)       │
│   7. Notice deep-context thin spots (informal only) —        │
│      drives Turn 2b mode A offers; formal list in Phase 3    │
└─────────────────────────┬────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 2: PROPOSE (up to 2 stages, ONE CTA per message)       │
│   Turn 2a (always): starting context                         │
│   Turn 2b (when connectors present): connector flow          │
└─────────────────────────┬────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 3: CONFIRM (up to 3 messages, ONE CTA per message)     │
│   Step 3a (when non-RaLHF connectors verified-present):      │
│            connector pass (mode A specific offer, mode B     │
│            open-ended check, mode C skip if none present)    │
│   Step 3b (always): final pre-handoff check-in (≤25 words,   │
│            max 2 pieces named, green-light ask)              │
│   Step 3c (when source-promotion queue non-empty):           │
│            Library refresh ask                               │
│   Step 3d (always, SILENT): save_context_feedback postmortem │
│            of context gathering (Phases 0-3; phase_4 = N/A)  │
│   Green light → handoff line + drop persona                  │
└─────────────────────────┬────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 4: EXECUTE (The assistant)                             │
│   handoff ack + context-scope line + thin-context flags +    │
│   italic wiki citations + real URLs + own the output         │
└─────────────────────────┬────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 5: REMEMBER (mandatory)                                │
│   POST-TASK ASK: "want me to feed RaLHF? (yes/no)" →         │
│     yes = summary + files + artifact save; no = skip         │
│   Postmortem already saved at 3d — NOT re-run here           │
│   Stop hook backstops save_context_feedback only if context  │
│     tools ran but no postmortem was recorded (3d interrupted)│
└──────────────────────────────────────────────────────────────┘
```

---

## When modifying

| Change | Edit |
|---|---|
| Persona, greeting, phase flow, key rules, worked examples | [`skills/ralhf-start/SKILL.md`](skills/ralhf-start/SKILL.md) |
| Retrieval / MCP tool logic | SKILL.md + [`references/context-decomposition.md`](skills/ralhf-start/references/context-decomposition.md) |
| Feedback / sync behavior | [`references/feedback-protocol.md`](skills/ralhf-start/references/feedback-protocol.md) |
| Gmail query templates | [`references/gmail-supplementation.md`](skills/ralhf-start/references/gmail-supplementation.md) |
| MCP URL | [`.mcp.json`](.mcp.json) + `README.md` |
| Hooks | [`hooks/hooks.json`](hooks/hooks.json) + the file the hook references |
| Slash commands | Each lives in its own `skills/<name>/SKILL.md` (e.g., `skills/ralhf-learn/SKILL.md`) — invoked by typing `/<name>`. Update `README.md` too. |
| **This file** | Only when the phase **names**, **hook list**, or **top-level shape** changes. Per-phase detail stays in SKILL.md. |
