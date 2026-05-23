# RaLHF ralhf-start — Orientation Map

> **Canonical spec:** [`skills/ralhf-start/SKILL.md`](skills/ralhf-start/SKILL.md). This file is a one-page orientation for developers browsing the repo — the phase shape, hook wiring, and where to look. If anything here disagrees with SKILL.md, **SKILL.md wins**.

Current skill version: see [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

---

## The five-phase flow

| Phase | One-liner | Full detail |
|---|---|---|
| **0a — TRIAGE** | Mental classification: Trivial / Small / Normal. Fires `get_my_mcp_usage` to gate the Small-task opt-in (veterans only, `usage_count > 5`). Trivial → skip RaLHF. Small + veteran → opt-in question. Normal → full flow. | [SKILL.md → PHASE 0a](skills/ralhf-start/SKILL.md) + [task-triage.md](skills/ralhf-start/references/task-triage.md) |
| **0 — LOAD** | Greeting (3 short paragraphs, 5 ingredients on first turn) + silent two-stage loading: `get_instructions` → READ word-for-word → `get_wiki_catalog`. In the light flow (yes-on-Small), `get_wiki_catalog` is skipped. | [SKILL.md → PHASE 0](skills/ralhf-start/SKILL.md#phase-0-load-expertise--before-anything-else) |
| **1 — DISCOVER** | Silent 7-step parallel drill: wiki + Claude memory + local files + session state. Follow `related_pages[]`, triage `sources[]` into fetch/skip, **informally** notice deep-context thin spots (drives Turn 2b mode A offers). The formal gap list builds in Phase 3. | [SKILL.md → PHASE 1](skills/ralhf-start/SKILL.md#phase-1-discover--look-through-ralhf-inventory-available-connectors) |
| **2 — PROPOSE** | **Show what was found.** Up to two staged check-ins, **one CTA per message**: Turn 2a starting context (always) → Turn 2b proactive flag (when RaLHF noticed a specific gap not already addressed). | [SKILL.md → PHASE 2](skills/ralhf-start/SKILL.md) |
| **3 — CONFIRM** | **Asking + finalizing.** Three steps: Step 3a connector pass (fires when any non-RaLHF connector is verified-present in the session) → Step 3b final pre-handoff check-in (always, ≤25 words) → Step 3c Library refresh ask (when source-promotion queue non-empty). Hard gate sits at 3b green light. | [SKILL.md → PHASE 3](skills/ralhf-start/SKILL.md) |
| **4 — EXECUTE** | Handoff line → drop persona. Claude opens with handoff ack + context-scope line, flags thin context, cites wiki pages in italics, never fabricates URLs. | [SKILL.md → PHASE 4](skills/ralhf-start/SKILL.md#phase-4-execute) |
| **5 — REMEMBER** | Post-task feed-ralhf ask (mandatory on wrap-up signal). Stop hook backstops `save_context_feedback` if a postmortem hasn't been recorded. | [SKILL.md → PHASE 5](skills/ralhf-start/SKILL.md#phase-5-remember--when-task-is-done) |

The hard gate sits at the end of Phase 3 — no execution until the user has explicitly confirmed the package (Step 3b green light) and resolved the Library refresh ask (Step 3c, when the source-promotion queue is non-empty).

---

## Hook infrastructure

| Hook | File | Purpose |
|---|---|---|
| `SessionStart` | `hooks/ralhf-init.md` | Primer loaded at session start. |
| `UserPromptSubmit` | `hooks/user-prompt-gate.md` | Forces skill invocation on every user turn (covers casual framings: "lets X", "how about X", "I want to X"). |
| `PreToolUse` | `hooks/pretool-askuser-block.json` | Denies `AskUserQuestion` with an "invoke the skill now" reason — keeps Claude from gathering requirements before RaLHF fires. |
| `PostToolUse` | `scripts/track-context-tool.sh`, `scripts/track-feedback-saved.sh` | Track which context tools were used and whether feedback was saved. |
| `Stop` | `scripts/prompt-context-feedback.sh` | Blocks session exit until `save_context_feedback` runs. |
| `SessionEnd` | `scripts/cleanup-session.sh` | Temp file cleanup. |

---

## Visual

```
┌──────────────────────────────────────────────────────────────┐
│ PHASE 0a: TRIAGE (mental, no MCP except get_my_mcp_usage)    │
│   Classify task:                                             │
│     Trivial  → skip RaLHF entirely                           │
│     Small    + usage_count > 5 → opt-in question, end turn   │
│     Small    + usage_count ≤ 5 → full flow                   │
│     Normal   → full flow                                     │
│   Yes-on-Small → light flow (skip catalog, Turn 2b, 3a)      │
│   Skip-on-Small → direct handoff to Claude                   │
└─────────────────────────┬────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 0: LOAD                                                │
│   Warm greeting → silent 2-stage work:                       │
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
│   Step 3a (when non-RaLHF connectors verified-present):       │
│            connector pass (mode A specific offer, mode B      │
│            open-ended check, mode C skip if none present)     │
│   Step 3b (always): final pre-handoff check-in (≤25 words,    │
│            max 2 pieces named, green-light ask)              │
│   Step 3c (when source-promotion queue non-empty):            │
│            Library refresh ask                                │
│   Green light → handoff line + drop persona                  │
└─────────────────────────┬────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 4: EXECUTE (Claude)                                    │
│   handoff ack + context-scope line + thin-context flags +    │
│   italic wiki citations + real URLs + own the output         │
└─────────────────────────┬────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 5: REMEMBER (mandatory)                                │
│   POST-TASK ASK: "want me to feed RaLHF? (yes/no)" →         │
│     yes = inline feed-ralhf flow; no = skip                  │
│   Stop hook forces save_context_feedback on exit             │
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
