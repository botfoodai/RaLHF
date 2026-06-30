# RaLHF — Orientation Map

> **Canonical spec:** [`skills/ralhf/SKILL.md`](skills/ralhf/SKILL.md). This file is a one-page orientation for developers browsing the repo — the phase shape, hook wiring, and where to look. If anything here disagrees with SKILL.md, **SKILL.md wins**.

Current skill version: see [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

RaLHF is **invoke-on-request**: it runs only when the user explicitly asks for it (`/ralhf`, "use ralhf", "pull my context"). It does not auto-fire on ordinary tasks. Invoking it IS the opt-in — there is no per-task yes/no gate.

---

## The five-phase flow

| Phase | One-liner | Full detail |
|---|---|---|
| **0a — OPEN & CLASSIFY** | Reached only because the user invoked RaLHF. **No MCP calls.** Confirm a task exists (else ask, pull nothing) and confirm an ambiguous subject inference, then ONE brief identity line naming the task and what it's pulling — **no yes/no gate** (invoking is the opt-in). A fast mental classification picks full flow vs. light flow (self-contained tasks). | [SKILL.md → PHASE 0a](skills/ralhf/SKILL.md) + [task-triage.md](skills/ralhf/references/task-triage.md) |
| **0 — LOAD** | Silent: `get_instructions` only (READ word-for-word). **No catalog** — discovery runs through `browse_wiki` in Phase 1; `get_wiki_catalog` is only a fallback when `browse_wiki` comes back empty. No separate greeting turn (identity lived in the opening line). | [SKILL.md → PHASE 0](skills/ralhf/SKILL.md#phase-0-load-expertise--before-anything-else) |
| **1 — DISCOVER** | Silent 7-step parallel drill: wiki + the assistant memory + local files + session state. Follow `related_pages[]`, triage `sources[]` into fetch/skip, **informally** notice deep-context thin spots (drives Turn 2b mode A offers). The formal gap list builds in Phase 3. | [SKILL.md → PHASE 1](skills/ralhf/SKILL.md#phase-1-discover--look-through-ralhf-inventory-available-connectors) |
| **2 — PROPOSE** | **Post the four-source inventory as the Turn 2a message** (canonical order + "anything to add or remove?" ask). Turn 2b fires only as a proactive gap-flag for a suspected-missing doc. | [SKILL.md → PHASE 2](skills/ralhf/SKILL.md) |
| **3 — CONFIRM** | **Asking + finalizing.** Step 3a connector **permission** (query approved connectors → add findings to the package as `connector` items) → **Step 3b final pre-handoff check-in** (affirm the package + ask for the green light) → Step 3c Library refresh ask → **Step 3d postmortem** (`save_context_feedback`, silent). Hard gate = the Step 3b green light. | [SKILL.md → PHASE 3](skills/ralhf/SKILL.md) |
| **4 — EXECUTE** | Handoff line → drop persona. The assistant opens with handoff ack + context-scope line, flags thin context, cites wiki pages in italics, never fabricates URLs. | [SKILL.md → PHASE 4](skills/ralhf/SKILL.md#phase-4-execute) |
| **5 — REMEMBER** | Post-task feed-ralhf + artifact-save ask; on "yes" the saves are presented as a short text list (keep/drop/edit → confirm → save the confirmed set). `/ralhf-sync` does the same; typed `/feed-ralhf` stays headless. The postmortem already fired at Step 3d, so it is NOT re-run here. The `Stop` hook stays a backstop for `save_context_feedback`. | [SKILL.md → PHASE 5](skills/ralhf/SKILL.md#phase-5-remember--when-task-is-done) |

The hard gate sits at Step 3b — no execution until the user has given the green light at the pre-handoff check-in and resolved the Library refresh ask (Step 3c, when the source-promotion queue is non-empty).

---

## Hook infrastructure

| Hook | File | Purpose |
|---|---|---|
| `SessionStart` | `scripts/print-hook.py hooks/ralhf-init.md` | Primer loaded at session start — explains RaLHF is invoke-on-request. |
| `PostToolUse` | `scripts/track-context-tool.py`, `scripts/track-feedback-saved.py` | Track which context tools were used and whether `save_context_feedback` ran. |
| `Stop` | `scripts/prompt-context-feedback.py` | Backstop: blocks exit once if context tools ran but no postmortem was recorded (quiet once Step 3d saved feedback). |
| `SessionEnd` | `scripts/cleanup-session.py` | Per-session temp-file cleanup. |

There is **no** `UserPromptSubmit` skill-forcing hook and **no** `PreToolUse` AskUserQuestion deny anymore — RaLHF only runs when the user invokes it, so nothing needs forcing and clarifying questions are no longer blocked.

---

## Visual

```
┌──────────────────────────────────────────────────────────────┐
│ PHASE 0a: OPEN & CLASSIFY                                    │
│   (reached only because the user invoked RaLHF)              │
│   no MCP calls here; then ONE opening line:                  │
│     identity + name task + what it's pulling                 │
│     NO yes/no gate — invoking is the opt-in                  │
│   mental classify: rich → full flow ; thin → light flow      │
└─────────────────────────┬────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 0: LOAD                                                │
│   No separate greeting (identity was in the opening line).   │
│   Silent: get_instructions → READ & internalize rules        │
│   NO catalog — browse_wiki drives discovery in Phase 1;      │
│   get_wiki_catalog is a fallback only if browse_wiki empty   │
└─────────────────────────┬────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 1: DISCOVER (silent, 7 steps)                          │
│   1. Apply personalized rules + browse_wiki (filtered)       │
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
│ PHASE 2: PROPOSE                                             │
│   Turn 2a: post the four-source inventory as a message       │
│            + an "anything to add or remove?" ask             │
│   Turn 2b (optional): proactive gap-flag for a suspected     │
│            missing doc                                       │
└─────────────────────────┬────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ PHASE 3: CONFIRM                                             │
│   Step 3a (connectors present): permission to QUERY only —   │
│            approved findings added to package as connector   │
│   Step 3b (always): final pre-handoff check-in —             │
│            affirm the package, ask for the green light       │
│            (Turn 2a already showed the inventory)            │
│   Step 3c (promotion queue non-empty): Library refresh ask   │
│   Step 3d (always, SILENT): save_context_feedback postmortem │
│            of context gathering (Phases 0-3; phase_4 = N/A)  │
│   Confirm → handoff line + drop persona                      │
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
| Persona, greeting, phase flow, key rules, worked examples | [`skills/ralhf/SKILL.md`](skills/ralhf/SKILL.md) |
| Retrieval / MCP tool logic | SKILL.md + [`references/context-decomposition.md`](skills/ralhf/references/context-decomposition.md) |
| Feedback / sync behavior | [`references/feedback-protocol.md`](skills/ralhf/references/feedback-protocol.md) |
| Gmail query templates | [`references/gmail-supplementation.md`](skills/ralhf/references/gmail-supplementation.md) |
| MCP URL | [`.mcp.json`](.mcp.json) + `README.md` |
| Hooks | [`hooks/hooks.json`](hooks/hooks.json) + the file the hook references |
| Slash commands | Each lives in its own `skills/<name>/SKILL.md` (e.g., `skills/ralhf-learn/SKILL.md`) — invoked by typing `/<name>`. Update `README.md` too. |
| **This file** | Only when the phase **names**, **hook list**, or **top-level shape** changes. Per-phase detail stays in SKILL.md. |
