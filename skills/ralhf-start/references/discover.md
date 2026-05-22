# Phase 1: Discover

Phase 1 has two jobs:
1. Read the RaLHF wiki pages and source documents the task calls for.
2. Inventory what external connectors are available in this session so Phase 3 can offer them.

Do NOT query non-RaLHF connectors (Gmail, Calendar, Drive, Jira, QuickBooks, etc.) in Phase 1. Those happen only after the customer approves them in Phase 3 Step 3a.

## Steps (all run in parallel where possible)

1. **Apply the `personalized` playbook silently when picking what to read.** Follow the operational rules, retrieval strategies, and trigger signals in the block. Skip pages it says to skip, include pages it says to include, use the retrieval strategy it specifies for this task type. Empty `personalized` is normal, fall back to generic.

2. **Check the Trigger Signal Matching table** below. Does the task match a pattern that calls for targeted browsing?

3. **In parallel, drill and scan ALL sources:**
   - **Personal wiki (Section 1):** **the catalog's page lists are TRUNCATED to the top ~5 per type by source-count/recency — they are NOT the discovery surface.** Use `browse_wiki` aggressively with **combined filters** (`page_type` + `tag` + `search_text` together) to reach the long tail. The catalog earns its keep on counts / top tags / namespaces / narrative summary, not on its truncated page lists. Examples:
     - `browse_wiki(page_type="entity", search_text="<task-keyword>")` — type-scoped keyword filter, much higher precision than a global search.
     - `browse_wiki(tag="<dimension>", search_text="<task-keyword>")` — tag-scoped keyword filter, narrows by life area + topic.
     - `browse_wiki(page_type="<type>", tag="<dimension>", search_text="<keyword>")` — all three combined for max precision.
     - `browse_wiki(page_type="<type>", offset=0, limit=100)` then `offset=100, limit=100` — pagination when you need to scan a full category (318 concepts, 404 summaries, etc.).
     - **Fire 2–4 parallel `browse_wiki` calls** with different filter combinations per task — one per relevant page_type, one per relevant tag, plus combined-filter variants. The cost is one round-trip; the recall improvement is large.
     - **`search(...)` is the narrow-target backstop**: use when you know a specific named page or one-off phrase that doesn't fit a page_type/tag (e.g. a person's name, a unique product term) AND your `browse_wiki(search_text=...)` filters didn't surface it. Never use as the primary discovery tool — the MCP authors explicitly warn that blind searching misses connective data.
     - Then single-item `batch_fetch` calls for each page identified. Fire fetches in parallel. **The fetch is required because Section 2 of Turn 2a is populated from the `sources[]` arrays returned by these fetches.**
   - **Personal context library (Section 2):** after wiki pages are fetched, consolidate their `sources[]` arrays. Triage each source for task relevance. The task-relevant ones appear as flat bullets in Section 2 of Turn 2a. A document that's also in the Cowork folder (Section 3) appears in BOTH sections — duplication is signal, not noise.
   - **Claude memory** (every session): read any memory files the runtime loaded (`CLAUDE.md`, user memory). Look for customer preferences, project conventions, recurring constraints.
   - **Local project files** (co-work mode only): see the "Local folder enumeration" subsection below for the exact procedure. The brand voice file, current one-pager, and other root-level artifacts are easy to miss when starting from subdirectories.
   - **Session state:** don't re-read files already in context from earlier in the turn or session.

### Local folder enumeration

When a Cowork folder is mounted, follow this exact sequence:

1. **Enumerate the folder ROOT first.** Run `Glob("*.md")`, `Glob("*.docx")`, `Glob("*.pdf")`, `Glob("*.pptx")`, `Glob("*.csv")` against the mounted folder's top level. Root-level files (brand guide, current one-pager, top-level briefs) are commonly the most active artifacts.
2. **Then enumerate one level deep.** Run `Glob("*/*.md")` and similar to pull files from immediate subdirectories.
3. **Don't pre-filter by filename match against the task title for content tasks.** A marketing folder's brand voice doc isn't named after the deliverable but always applies. Past issues inform tone. Style guidelines apply across deliverables.
4. **Triage with the §2.9 rubric** (multi-purpose use, recency, direct task relevance, type fit).
5. **When multiple versions of the same file exist** (e.g., `Brand Guidelines v3.5`, `v3.6`, `v3.8`, `v3.9`), use the HIGHEST version as active and flag earlier versions as archived. Do not pick the first one Glob returns. Compare versions explicitly.
6. **Read every file judged relevant.** These go in Section 3 of Turn 2a (Documents from the Cowork folder).

4. **Inventory the actual MCP tool surface of THIS session.** Enumerate the tools available in your runtime. MCP tool names have the form `mcp__<server-id>__<tool>`. Group tools by server and categorize each server using `references/connector-patterns.md`.

5. **Follow wikilinks for related pages.** Each fetched wiki page includes `related_pages[]`. Traverse into pages you haven't read yet when they look relevant.

6. **Stop and triage source documents.** Consolidate the `sources[]` arrays from fetched wiki pages and rank them. See the ranking signals section below. Two buckets only: fetch or skip.

## Trigger Signal Matching

**Use combined filters in every row** (`page_type` + `tag` + `search_text`). Single-filter `browse_wiki` calls hit too many pages and miss the long tail; combined filters are much more precise.

| Signal in the customer's request | Pattern | What to browse (use combined filters) |
|-----|---------|---------------|
| References a named product or company, output for an external audience | Brand & style identity | `browse_wiki(page_type="concept", search_text="brand")`, `browse_wiki(page_type="concept", search_text="style")`, `browse_wiki(tag="work_and_learning", search_text="identity")`; check `last_updated_at` for staleness |
| Writing about what a product does (marketing, pitch, one-pager) | Product knowledge | `browse_wiki(page_type="entity", search_text="<product name>")`, `browse_wiki(tag="work_and_learning", search_text="<product name>")` for PRDs / specs / terminology |
| References "the last one", prior installments, numbered editions | Prior work in a series | `browse_wiki(page_type="summary", search_text="<series keyword>")`; `browse_wiki(page_type="summary", offset=0, limit=50)` to scan recent summaries if no keyword fits |
| Says "picking up where we left off", "we decided" | Decisions from prior sessions | `browse_wiki(page_type="summary", search_text="<topic>")`, `browse_wiki(page_type="comparison", search_text="<topic>")` |
| States a budget, time limit, headcount, or automation constraint | Execution constraints | `browse_wiki(tag="money", search_text="pricing")` / `search_text="budget"`; `browse_wiki(tag="work_and_learning", search_text="team")` for team constraints |
| Deliverable names a specific audience (board, investors, judges) | Audience context | `browse_wiki(page_type="profile", search_text="<audience keyword>")`, `browse_wiki(page_type="entity", search_text="<audience name>")` |
| Specific named person, place, or one-off phrase that doesn't fit a category | Known-target lookup | `search(query="<exact name or phrase>")` — narrow-target backstop only. Use AFTER `browse_wiki(search_text=...)` filters have been tried. |

## Source document ranking signals (highest first)

- **Appears in multiple relevant wiki pages.** A source cited by 3 of 5 fetched pages is load-bearing. Auto-fetch.
- **Recency.** Newer sources win on topics that drift (brand, product, pricing, org structure).
- **Direct task relevance.** Filename matches the task shape.
- **`personalized` rule names it explicitly.** Auto-fetch regardless of other signals.
- **Type fits the task.** Customer-authored files for creative work, API sync snapshots for factual.

When triage signals are mixed and the title is ambiguous, prefer fetch over skip. Read-and-discard later is cheaper than missing relevant context.

## Conflict resolution (three bands)

When two sources contradict on the same fact, use the more recent one as the working answer. Whether to surface the tie-break depends on confidence:

- **Band 1, silent resolution:** winner is marked current AND `personalized` reinforces. Apply silently. Don't make the customer re-approve.
- **Band 2, one-line flag:** recency clearly wins but signals are weaker. Note it briefly in Turn 2a or Turn 2b. Example: "Using April pptx colors over v3.5 since they're newer, push back if wrong."
- **Band 3, surface as a Turn 2b amendment candidate:** genuinely ambiguous, choice meaningfully changes the output. Ask the customer.

Never surface a conflict just to display diligence. Display necessary diligence.

## End of Phase 1: Notice missing documents

Before Phase 2, take a beat and ask one question grounded in the catalog: are there document types the customer clearly has (visible in the catalog or referenced from other pages) that would help this task but aren't yet in the package?

Examples:
- Catalog shows a "Brand Voice Guidelines" page but it's not in the package, and the task is external-facing copy. Flag.
- Customer has a wiki page for a recurring deliverable (Q1 board deck) and the current task is the next instance. Flag any prior installment that isn't in the package.
- A relevant entity page exists but the related source documents weren't fetched. Flag.

This is NOT a list of personal-detail probes. RaLHF doesn't ask about feelings, motivations, relationship dynamics. The question is purely: what documents would help this task that aren't in the package yet, based on what the catalog shows the customer actually has.

If a missing-document candidate maps to a verified-present connector (a Gmail thread, a Drive file), use that to drive the connector check (Step 3a) rather than the amendment ask.

Phase 1 ends when you have: the catalog, the relevant wiki pages and source docs fetched, a mental inventory of MCP connectors present, and a short list of documents you noticed are missing. Phase 2 is the output phase.
