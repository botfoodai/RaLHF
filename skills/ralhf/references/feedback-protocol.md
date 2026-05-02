# Feedback Protocol — Detection Patterns & Sync Rules

Companion reference to SKILL.md. Defines how to detect corrections, confirmations, and new information during a session, and when each type gets synced back to RaLHF.

## Detection Patterns

### Corrections (user is fixing something wrong)

**Explicit signals:**
- *"Actually, [correct info]"* — *"Actually, I'm allergic to shellfish now"*
- *"That's wrong / not right / incorrect"*
- *"No, [correct info]"* — *"No, we have three kids, not two"*
- *"I don't [thing]"* / *"Not anymore"* / *"No longer"*
- *"It's X, not Y"*

**Implicit signals:**
- User provides info that contradicts what was retrieved (watch when presenting Turn 2a context)
- User consistently ignores or replaces a specific suggestion type — may indicate a stale preference

**Action:** Sync IMMEDIATELY via `remember`. Don't queue corrections.

### Confirmations (user validates context)

**Explicit:** *"Yes that's right"* / *"Exactly"* / *"You got it"* / *"Still accurate"* / *"Nothing has changed"*

**Implicit:** user proceeds without correcting; user enthusiastically accepts a recommendation derived from context; user builds on a suggestion without modification.

**Action:** Optional — note as a strengthening signal in `save_context_feedback` (`successful_strategies`). Don't `remember` raw confirmations.

### New Information (user shares something RaLHF doesn't have)

**Explicit:** *"By the way…"* / *"I should mention"* / *"You should know"* / *"I recently…"* / *"We just…"*

**Implicit:** user volunteers a preference or constraint while discussing the task that RaLHF didn't have; user casually reveals family/work/lifestyle info; user mentions a recent experience that shaped a new preference.

**Action:** Safety-critical info → `remember` IMMEDIATELY. Preferences/patterns → `remember` (substantive, dated, with `dimension` set).

### Preferences

**Positive:** *"I love X"* / *"I really like X"* / *"X is great"* / *"More of this"* / *"Exactly what I wanted"* / *"I've been into X lately"*

**Negative:** *"I don't like X"* / *"Too [adjective]"* / *"X isn't really my thing"* / *"I'd never do X"*

**Action:** `remember` with substantive context. Be specific — *"User prefers couples-only weekend trips when children stay with grandparents"* beats *"likes trips without kids"*.

---

## Sync Decision Matrix

| What happened | Urgency | Tool | When |
|---|---|---|---|
| Allergy / medical correction | IMMEDIATE | `remember` | Right now, mid-execution |
| Factual correction (wrong name/city/job) | IMMEDIATE | `remember` | Right now |
| New safety info (new allergy, new medication) | IMMEDIATE | `remember` | Right now |
| New factual info (moved, new job, new family member) | IMMEDIATE | `remember` | Right now |
| Preference update | NEAR-TERM | `remember` | Mid-execution or at the Phase 5 post-task ask |
| New preference discovered | NEAR-TERM | `remember` | Phase 5 post-task ask |
| Implicit confirmation | OPTIONAL | `save_context_feedback` | Phase 5 |
| Implicit rejection / negative preference | NEAR-TERM | `remember` | Phase 5 |
| Habit or pattern revealed | NEAR-TERM | `remember` | Phase 5 |
| Task outcome and decisions | NEAR-TERM | `remember` | Phase 5 (in the dense session summary on `/feed-ralhf` yes) |

---

## Immediate Sync Protocol

When you detect something that needs immediate sync:

1. **Acknowledge naturally.** *"Got it, noted."* / *"Important to know."*
2. **Call `remember`** with substantive content, `dimension`, and `source_description`.
3. **Confirm briefly.** *"Updated your RaLHF profile."* — keep it short.
4. **Continue the conversation.** Don't make a big deal of it.

Example:
> User: *"Actually, my son is allergic to peanuts — I should have mentioned that"*
>
> RaLHF: *"Important to know — adding that to your RaLHF profile right now. Adjusting recommendations to exclude peanuts and peanut derivatives."* → `remember(content="Son <name> has peanut allergy as of <date>", dimension="health", source_description="user correction during <task>")`

---

## What NOT to Sync

- **Temporary logistics** — *"I'm free Thursday"* (only relevant this week)
- **User explicitly said not to save** — always respect opt-outs
- **Speculative inferences** — *"They seem stressed"* (only save stated facts)
- **External connector raw content** without explicit permission — Gmail thread bodies, full Drive file contents, Calendar event payloads. Save the *durable fact* extracted from them, not the payload itself. Source pointers to the file/thread/event are a different obligation — see SKILL.md §1.6.
- **Duplicate information** — if `get_wiki_catalog` shows it's already in the wiki, don't re-save
- **Trivial preferences from single instances** — *"They chose blue once"* doesn't mean *"they prefer blue"*

## Handling "Don't Save That"

1. Acknowledge immediately: *"Understood, won't save that."*
2. Remove from your sync queue.
3. Do NOT reference it in the conversation summary that gets fed back via `/feed-ralhf`.
4. Do NOT save it in a different form.
5. Optionally `remember` the negative preference itself when the user gave a reason: *"User prefers not to ingest one-off confidential PDFs"* — so personalized rules learn the pattern.
