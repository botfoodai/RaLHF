---
name: sync-back
description: Sync what was learned in this conversation back to RaLHF. Saves new preferences, corrections, and a conversation summary so future sessions are more personalized.
---

# Sync Back — Save Conversation Learnings to RaLHF

The user wants to sync what was learned during this conversation back to RaLHF.

## What to do

Follow the Phase 5 (Remember) protocol from the `prep-context` skill:

### 1. Review the conversation

Scan the full conversation for:
- **New preferences** — things the user expressed liking or disliking
- **New facts** — life changes, new information about themselves or their household
- **Corrections** — things that were wrong in RaLHF and were fixed (note these as already handled)
- **Confirmed context** — things RaLHF had right that were validated
- **Decisions made** — choices the user made and why
- **Patterns** — habits or tendencies that emerged

### 2. Present the sync summary

Show the user what you plan to save, grouped clearly:

"Here's what I'd like to save to your RaLHF from our conversation:

**New context:**
- [item 1]
- [item 2]

**Already corrected during our chat:**
- [item — already saved]

**Conversation summary:**
- [brief description of what we worked on and the outcome]

Want me to save all of this, or would you like to adjust anything?"

### 3. Wait for confirmation

Do NOT sync until the user confirms. They may want to remove items or rephrase things.

### 4. Execute the sync

- Call `remember` for each new piece of context (one call per distinct item)
- Call `remember` for the overall session summary (include a source_description like "conversation summary")
- Each note should be specific, dated, and factual

### 5. Confirm completion

"All saved to RaLHF. These will help personalize future conversations."

## If there's nothing to sync

If the conversation was purely informational or the user didn't reveal new context:
- "I didn't pick up any new context to save from our conversation. If there's anything you'd like me to remember, just let me know."

## If sync already happened

If items were already synced during the conversation (immediate corrections):
- Note what was already saved
- Only sync remaining queued items
- Don't double-save anything
