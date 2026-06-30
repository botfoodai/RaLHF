---
name: ralhf-sync
description: This skill should be used when the customer wants to manually save what was learned in the current session back to RaLHF. Trigger phrases include "/ralhf-sync", "sync back", "save what we learned", or any request to persist session learnings before the conversation ends.
---

# Sync Back — Save Conversation Learnings to RaLHF

The user wants to sync what was learned during this conversation back to RaLHF.

## What to do

Follow the Phase 5 (Remember) protocol from the `ralhf` skill:

### 1. Review the conversation

Scan the full conversation for:
- **New preferences** — things the user expressed liking or disliking
- **New facts** — life changes, new information about themselves or their household
- **Corrections** — things that were wrong in RaLHF and were fixed (note these as already handled)
- **Confirmed context** — things RaLHF had right that were validated
- **Decisions made** — choices the user made and why
- **Patterns** — habits or tendencies that emerged

### 2. Present the proposed saves as a text list

Show the user a short grouped text list of what you propose to save so they can keep/drop/edit each item before anything is saved:
- A **"New facts & preferences"** group — new facts/preferences/corrections (note the `dimension` where it maps).
- A **"Conversation summary"** group — one summary item.

Dedup against the Library first (don't propose items already saved, and don't double-save anything synced live during the chat). Ask the user to confirm or trim the list.

### 3. Wait for confirmation

Wait for the user's kept/edited set. Do NOT save until they confirm.

### 4. Save the confirmed set

- Save ONLY the confirmed (possibly edited) items, using each one's `content` + `dimension`.
- `remember` for facts/preferences/summaries; `start_file_upload` for any real shared files.
- Each note should be specific, dated, and factual.

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
