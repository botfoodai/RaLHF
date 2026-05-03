# RaLHF prep-context — Orientation Map

> **Canonical spec:** [`skills/prep-context/SKILL.md`](skills/prep-context/SKILL.md). This file is a one-page orientation for developers browsing the repo — the phase shape, hook wiring, and where to look. If anything here disagrees with SKILL.md, **SKILL.md wins**.

Current skill version: see [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

---

## The five-phase flow

| Phase | One-liner | Full detail |
|---|---|---|
| **0 — LOAD** | Greeting (3 short paragraphs, 5 ingredients on first turn) + silent two-stage loading: `get_instructions` → READ word-for-word → `get_wiki_catalog`. | [SKILL.md → PHASE 0](skills/prep-context/SKILL.md#phase-0-load-expertise--before-anything-else) |
| **1 — DISCOVER** | Silent 7-step parallel drill: wiki + Claude memory + local files + session state. Follow `related_pages[]`, triage `sources[]` into fetch/skip, **informally** notice deep-context thin spots (drives Turn 2b mode A offers). The formal gap list builds in Phase 3. | [SKILL.md → PHASE 1](skills/prep-context/SKILL.md#phase-1-discover--look-through-ralhf-inventory-available-connectors) |
| **2 — PROPOSE** | **Show what was found.** Up to two staged check-ins, **one CTA per message**: Turn 2a starting context (always) → Turn 2b connector flow (when any connector verified-present). | [SKILL.md → PHASE 2](skills/prep-context/SKILL.md#phase-2-propose--share-what-you-found-one-check-in-at-a-time) |
| **3 — CONFIRM** | **Asking + finalizing.** Up to four messages: Step 3a builds the formal deep-context gap list (1–3 rich / 4–6 thin, tagged) and surfaces it as the gap pass (always) → Step 3b safety re-confirm (only when applicable) → Step 3c final pre-handoff check-in (always) → Step 3d Library refresh ask (when source-promotion queue non-empty). Hard gate sits here. | [SKILL.md → PHASE 3](skills/prep-context/SKILL.md#phase-3-confirm--gaps-safety-final-check-in-library-refresh) |
| **4 — EXECUTE** | Handoff line → drop persona. Claude opens with handoff ack + context-scope line, flags thin context, cites wiki pages in italics, never fabricates URLs. | [SKILL.md → PHASE 4](skills/prep-context/SKILL.md#phase-4-execute) |
| **5 — REMEMBER** | Post-task feed-ralhf ask (mandatory on wrap-up signal). Stop hook backstops `save_context_feedback` if a postmortem hasn't been recorded. | [SKILL.md → PHASE 5](skills/prep-context/SKILL.md#phase-5-remember--when-task-is-done) |

The hard gate sits at the end of Phase 3 — no execution until the user has explicitly confirmed the package (Step 3c) and approved the Library refresh (Step 3d, when applicable).

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
│ PHASE 0: LOAD                                                │
│   Warm greeting → silent 2-stage work:                       │
│     Stage 1: get_instructions → READ & internalize           │
│              personalized rules                              │
│     Stage 2: get_wiki_catalog (with rules in hand)           │
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
│ PHASE 3: CONFIRM (up to 4 messages, ONE CTA per message)     │
│   Step 3a (always): build formal gap list + surface as ask   │
│            (mode A 1–6 items per rich/thin rubric, or mode B │
│             minimum "anything else?")                        │
│   Step 3b (only when applicable): safety re-confirm          │
│   Step 3c (always): final pre-handoff check-in               │
│   Step 3d (when queue non-empty): Library refresh ask        │
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
| Persona, greeting, phase flow, key rules, worked examples | [`skills/prep-context/SKILL.md`](skills/prep-context/SKILL.md) |
| Retrieval / MCP tool logic | SKILL.md + [`references/context-decomposition.md`](skills/prep-context/references/context-decomposition.md) |
| Feedback / sync behavior | [`references/feedback-protocol.md`](skills/prep-context/references/feedback-protocol.md) |
| Gmail query templates | [`references/gmail-supplementation.md`](skills/prep-context/references/gmail-supplementation.md) |
| MCP URL | [`.mcp.json`](.mcp.json) + `README.md` |
| Hooks | [`hooks/hooks.json`](hooks/hooks.json) + the file the hook references |
| Slash commands | Each lives in its own `skills/<name>/SKILL.md` (e.g., `skills/learn/SKILL.md`) — invoked by typing `/<name>`. Update `README.md` too. |
| **This file** | Only when the phase **names**, **hook list**, or **top-level shape** changes. Per-phase detail stays in SKILL.md. |
