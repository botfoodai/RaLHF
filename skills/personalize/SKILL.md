---
name: personalize
description: Run the full context preparation sequence for the current conversation. Assembles context from RaLHF, Claude memory, and session state, reconciles disconnects, and briefs you on what the skill knows before starting work.
---

# Personalize This Conversation

The user wants you to run the full Phase 1: Plan & Read sequence from the `ralhf` skill. This is the confidence-building context assembly — not just a data fetch, but a visible demonstration that you're grounding the session in everything you know about this person.

## What to do

### If a task or topic is active

Run the full preparation sequence:

1. **Determine required context** — What does this task need? What would you need to know about this person to do it exceptionally well?

2. **Inventory existing context** — Check what Claude already knows from memory files, session state, conversation history, open files, or project context. Note what you have.

3. **Map the RaLHF wiki** — Call `get_wiki_catalog` to get the complete map of the user's personal wiki. Read the narrative summary, scan page entries, and identify which pages, types, and tags are relevant to the task.

4. **Drill into relevant areas and check datasources** — Call `browse_wiki` to filter by relevant page types (`summary`, `entity`, `concept`, `profile`, `comparison`) or tags (e.g., `travel`, `health`, `work_and_learning`). Call `list_connected_sources` in parallel to see which external sources (Gmail, Calendar, Jira) are connected — this informs what you can check in Phase 2. The catalog enumerates every page in the wiki, so if an area isn't covered there, it's a real gap — flag it for the user rather than trying to guess at it.

5. **Retrieve details** — Issue a single `batch_fetch([{kind:"wiki", page_id}, {kind:"document", page_id}, ...])` covering every wiki page and source document you judge relevant — mix kinds in the same call, one round-trip beats many. Read enough to describe the user's situation with substance, not just page titles. When the returned pages reveal new `related_pages[]` or `sources[]` worth reading, fire a follow-up `batch_fetch` covering all of them at once.

6. **Reconcile** — Compare Claude's existing context with what you actually read from RaLHF. Identify:
   - **Disconnects** — Claude says X, RaLHF says Y. Surface these to the user.
   - **Gaps** — Neither source has something you need. State what you'd do without it.
   - **Stale signals** — Something seems outdated. Confirm quickly.
   - **Confirmations** — Both sources agree. High confidence.

7. **Clarify** — Present disconnects and gaps concisely. When the user responds:
   - Corrections → call `remember` immediately. Confirm: "Updated in RaLHF."
   - New durable facts → call `remember` immediately. Confirm: "Saved to RaLHF."

8. **Brief the user** — Share the 3-7 most relevant context points you'll use for this task. The user should read this and think: "Good — they understand my situation."

9. **Recommend enrichment** — If you found gaps that would help future sessions, suggest what the user could add to RaLHF. Offer to save it now.

10. **Handover** — Signal that preparation is complete and work begins.

### If no topic is active yet

If the user runs `/personalize` at the start of a conversation before asking for anything:

1. Call `get_wiki_catalog` to get the complete map of the user's personal wiki. Read the narrative summary for a high-level understanding.
2. In parallel: call `browse_wiki(page_type="profile")` to find the user's profile pages, `browse_wiki(page_type="summary")` for overview pages, and `list_connected_sources` to see which external sources are connected.
3. Issue a single `batch_fetch([{kind:"wiki", page_id}, ...])` covering the most relevant pages to get a persona overview. Follow up with another `batch_fetch` on `sources[]` items if deeper detail is needed.
4. Check Claude's memory for any existing knowledge about this user.
5. Present a brief that builds confidence:
   - "Here's what I have on you across RaLHF and this session: [key highlights]"
   - If there are gaps or stale-looking items: "A few things I'd want to confirm when we start working: [list]"
   - "What would you like help with? I'll assemble the specific context we need."

## Important

- This is a visible, confidence-building process — not a silent background fetch.
- Present context naturally, not as a data dump. Connect it to the task.
- Flag disconnects and gaps clearly — resolving these is the value of preparation.
- If corrections are made, update RaLHF immediately via `remember`. The user should see the system learning.
- Activate the full feedback-capture loop for the rest of the conversation (see the `ralhf` skill).
