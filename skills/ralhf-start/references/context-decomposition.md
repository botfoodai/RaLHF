# Context Decomposition — How to Break a Task into Retrieval Calls

Companion reference to SKILL.md. Internal thinking only — never present this decomposition to the user. The output of this step is your Phase 1 retrieval plan, not a chat message.

## The internal checklist

For any task, walk through these questions in your head before firing tools:

1. **What's the action?** — write, plan, build, decide, debug, draft, recap.
2. **What domains does this touch?** — work, personal, family, financial, health, technical, relational. (RaLHF dimensions: `food_and_dining`, `health`, `home_and_auto`, `identity`, `money`, `shopping`, `entertainment`, `travel`, `work_and_learning`, `social_and_digital_life`.)
3. **What do I already have in context?** — the assistant's memory, prior conversation, session state. Don't re-fetch what's already loaded.
4. **What does RaLHF have?** — based on `get_wiki_catalog`, which `page_type`s and `tags` apply? Which specific wiki pages look directly relevant?
5. **What's the right batch?** — which 3–5 wiki pages do I `batch_fetch` first? Which `sources[]` do I expect RaLHF to read and surface as relevant Library docs in Turn 2a?
6. **Any conflicts likely?** — wiki + connector + local file all pointing to the same artifact? Apply Band-1/2/3 conflict resolution from §4.5.
7. **Which connectors plausibly help?** — match task shape to category (see `connector-patterns.md`), then match category to verified-present servers in this session.

## Tool sequence — canonical pattern

```
1. get_instructions                                    → personalized rules (READ word-for-word)
2. get_wiki_catalog                                    → ORIENTATION ONLY (narrative summary,
                                                          page-type counts, top tags, top-5 per
                                                          type). Page lists are TRUNCATED — not
                                                          the discovery surface.
3. browse_wiki(page_type=…, search_text=…) (parallel)  → primary discovery. Combine page_type +
   browse_wiki(tag=…, search_text=…)        ×N           tag + search_text for max precision.
   browse_wiki(page_type=…, offset=N, limit=100)         Paginate for full category sweeps.
4. search(query="…") (only if needed)                  → narrow-target backstop. Use ONLY for
                                                          a specific name/phrase that didn't
                                                          surface via browse_wiki(search_text=…).
5. batch_fetch([{kind:"wiki", page_id}, ...]) (1 item   → read the relevant wiki pages.
   per call, fired parallel for N pages)
6. Triage sources[] from returned pages                → auto-fetch / opt-in / skip per §2.9
7. batch_fetch([{kind:"document", page_id}, ...])      → pull the auto-fetch document bucket
   (1 item per call, parallel)
8. (Turn 2b only, after user approval)                 → connector queries (Gmail/Drive/etc.)
```

In parallel with steps 3–7: scan the assistant's memory, local project files (co-work mode), and any session state already loaded.

### Why this order

- **Catalog is orientation, not enumeration.** Its page lists are truncated to top-5 per type. A 939-page wiki returns ~21 pages from the catalog. Don't pick exclusively from those — most of the wiki is invisible.
- **`browse_wiki` with combined filters is the workhorse.** `browse_wiki(page_type="entity", search_text="investor")` is far more precise than either filter alone, and far higher recall than the catalog's top-5 entities. Fire 2–4 parallel calls with different filter combinations.
- **`search` is the narrow-target backstop, not the primary tool.** The MCP authors explicitly warn that blind search misses connective data the structured browse path surfaces. Use search only when a specific named page or one-off phrase didn't appear via `browse_wiki(search_text=…)`.

## Worked decomposition examples

Each example shows the internal answer to questions 1–5 above for a specific task shape.

### "Plan our anniversary dinner"

- **Action:** plan + decide (restaurant + reservation logistics)
- **Domains:** `food_and_dining`, `entertainment`, partner relationship (`identity`), local geography (`home_and_auto`)
- **Already in context:** none
- **What RaLHF likely has** (combined-filter browse):
  - `browse_wiki(page_type="profile", search_text="food")` — Identity Profile, Food and Dining Profile, partner profile
  - `browse_wiki(tag="food_and_dining", search_text="anniversary")` — Dining Preferences, Celebration History
  - `browse_wiki(tag="food_and_dining", search_text="restaurant")` — Household Food Rules, prior restaurant choices
- **Batch plan:**
  - First batch (wiki ×4): Dining Preferences, Household Food Rules, Celebration History, partner entity page
  - Second batch (documents from `sources[]`): prior reservation confirmations, booking receipts — auto-fetch the most-cited and recent
- **Conflicts to watch:** dietary restrictions vs partner preferences (typically both in `personalized` — apply silently if reinforced)
- **Connectors plausibly helpful:** Gmail (prior reservation confirmations, recent threads with the partner about dining) — propose in Turn 2b if Gmail is verified-present

### "Q1 board deck for <Company>"

- **Action:** build (deliverable: standalone deck following established cadence)
- **Domains:** `work_and_learning`, `money`
- **Already in context:** task name, company name
- **What RaLHF likely has** (combined-filter browse):
  - `browse_wiki(page_type="entity", search_text="<Company>")` — Company entity, founder entities
  - `browse_wiki(page_type="profile", search_text="money")` — Money profile
  - `browse_wiki(page_type="summary", search_text="quarterly")` — prior quarterly updates
  - `browse_wiki(page_type="summary", search_text="board")` — prior board materials
  - `browse_wiki(page_type="concept", search_text="brand")` — Brand Guidelines
  - `browse_wiki(page_type="concept", search_text="board")` — Quarterly Board Procedures
- **Batch plan:**
  - First batch (wiki ×5–7): Company entity, Quarterly Board Meeting page, Money profile, Brand Guidelines, recent quarterly summary
  - Second batch (documents from `sources[]`): prior board decks, prior quarterly update doc, brand guide pptx, financial source — auto-fetch the multi-page-backed and recent
- **Conflicts to watch:** brand stack (legacy wiki vs current pptx) — Band-1 silent if `personalized` reinforces "prefer pptx for brand"
- **Connectors plausibly helpful:** QuickBooks (live Q1 financials), GDrive (running deck file) — propose in Turn 2b

### "Quarterly customer newsletter"

- **Action:** draft (continuing series)
- **Domains:** `work_and_learning`, `social_and_digital_life`
- **Already in context:** "newsletter"
- **What RaLHF likely has** (combined-filter browse):
  - `browse_wiki(page_type="entity", search_text="newsletter")` — Newsletter entity
  - `browse_wiki(page_type="summary", search_text="newsletter")` — prior issue summaries
  - `browse_wiki(page_type="summary", search_text="<product>")` — recent product updates worth surfacing
  - `browse_wiki(page_type="concept", search_text="voice")` / `search_text="brand"` — Brand Voice & Tone, Style Guidelines
- **Batch plan:**
  - First batch (wiki ×4): Newsletter entity, last 2 issue summaries, Brand Voice
  - Second batch (documents): prior sent newsletters, the template, brand voice guidelines doc
- **Conflicts to watch:** voice/tone evolution (newer issues vs older brand voice doc) — flag in Step 3a if relevant
- **Connectors plausibly helpful:** Gmail (prior send threads to match cadence), GDrive (the running newsletter folder)

### "Letter to my child's teacher"

- **Action:** write (relational, audience-specific tone)
- **Domains:** `identity` (child, family), `work_and_learning` (school)
- **Already in context:** none
- **What RaLHF likely has** (combined-filter browse):
  - `browse_wiki(page_type="profile", search_text="identity")` — Identity Profile (children section)
  - `browse_wiki(page_type="profile", search_text="education")` — Education Profile
  - `browse_wiki(page_type="entity", search_text="<child name>")` — Child entity
  - `browse_wiki(page_type="entity", search_text="school")` — School entity
  - `search(query="<teacher name>")` — narrow-target lookup if the teacher has a wiki entity, since teacher names rarely fit a category keyword
- **Batch plan:**
  - First batch (wiki ×4): Child entity, Teacher entity, School entity, Education Profile
  - Document bucket: usually thin for personal-relational tasks — auto-fetch may be empty, in which case Turn 2b is skipped
- **Conflicts to watch:** rare for personal-relational
- **Connectors plausibly helpful:** Gmail (prior teacher correspondence to match tone) — propose in Turn 2b

### "Refactor the auth module"

- **Action:** code change (architectural decision)
- **Domains:** `work_and_learning` (technical)
- **Already in context (co-work mode):** repo structure, files in working tree
- **What RaLHF likely has** (combined-filter browse — usually thin for code work, focus on design rationale and prior decisions):
  - `browse_wiki(page_type="concept", search_text="auth")` — auth-related architecture concepts
  - `browse_wiki(page_type="summary", search_text="auth")` — prior decisions about this work
  - `browse_wiki(page_type="comparison", search_text="auth")` — pattern comparisons (session vs. token approaches)
  - `browse_wiki(tag="work_and_learning", search_text="auth")` — anything tagged work-and-learning mentioning auth, regardless of page type
- **Local-file scan in parallel:** `Glob("**/CLAUDE.md")`, `Glob("**/README*")`, repo-level config and design docs
- **Batch plan:**
  - First batch (wiki ×3): auth concept page, recent architecture summary, relevant comparison
  - Document bucket: prior design docs from `sources[]`
- **Conflicts to watch:** repo `CLAUDE.md` (authoritative for project conventions per §4.6) vs older wiki pages
- **Connectors plausibly helpful:** Jira/Linear (related tickets), GitHub (PR history), Confluence/Notion (design docs)

## Heuristics to internalize

- **Cost asymmetry:** loading context that turns out irrelevant costs seconds. Missing context that turns out critical costs 2–3 revision cycles. When uncertain, fetch the wiki side; propose the connector side for user approval.
- **Catalog is orientation, browse_wiki is discovery.** The catalog gives you counts, top tags, and the top-5 pages per type — orientation, not enumeration. Use `browse_wiki(page_type=…, search_text=…)` with combined filters to find task-relevant pages in the long tail (the 90%+ of the wiki that's invisible to the catalog). Fire 2–4 parallel browse calls per task.
- **Do not `batch_fetch` random pages by guessing IDs.** Always derive IDs from `browse_wiki` / `search` / `related_pages[]` / `sources[]` first.
- **Sources are the discovery, not the wiki page.** A wiki page with `source_count: 140` has 140 documents that back it. The page is a pointer; the `sources[]` are where the substance lives. Document triage (§2.9) is non-negotiable.
- **Empty shortlists are a real result.** If the catalog scan returns nothing for a tag/type, record it as `Wiki [Y]` with zero hits — not as `N`. Tells you to lean harder on connectors (Turn 2b) or `/ralhf-learn` invitations (Step 3a).
- **Co-work mode means dual-source.** Both Wiki AND Local must be scanned in parallel. The repo's own `CLAUDE.md` has authoritative weight equal to `personalized` rules for project conventions.
