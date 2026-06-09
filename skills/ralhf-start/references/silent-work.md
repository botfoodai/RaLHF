# Phase 0 silent work

After the customer says "pull" on the ask-first gate (and never narrated to the customer), run these calls in sequence. There is no separate greeting turn — identity was carried by the gate message.

**Phase 0a already fired `get_my_mcp_usage`** before the gate (it scales the gate's identity tier and drives the new-user pull-lean). Its `usage_count` is in hand. Phase 0 silent work covers the remaining calls.

**Light-flow exception:** if the customer said "pull" on a self-contained task (one RaLHF recommended skipping), skip Step 2 (`get_wiki_catalog`). Only Step 1 (`get_instructions`) runs. See `references/task-triage.md`.

## Step 1: Call `get_instructions`

Returns two blocks:
- `general` — how RaLHF works for any customer.
- `personalized` — the learned playbook for this customer.

Reading both is mandatory every session.

### The `personalized` block

It is the highest-priority retrieval and behavior input. It distills prior sessions and post-mortems into patterns:
- Operational rules ("read local files first")
- Retrieval strategies ("use the wiki for positioning, local files for ground truth")
- Source preferences ("prefer the newer pptx over the v3.5 wiki for brand")
- Trigger signals ("when the task says 'competition refresh', do X")
- Phase-level weaknesses to watch for
- Lessons from what worked and what didn't

It is not a list of narrow filter rules. It is an evolving operating manual that shapes every retrieval and behavior decision.

**On day one for a new customer the block is empty.** That is normal. RaLHF runs on generic defaults. Each Phase 5 feedback save writes new patterns into it. Over time the block grows into a customer-specific playbook.

### Scoping personalized rules

Some personalized rules apply to RaLHF's context selection (what to fetch, which sources to trust). Some apply to the assistant's drafting (tone, structure, briefing requirements).

Rules that demand task-input clarifications ("never propose structure until a briefing is shared", "always ask the audience first") apply to the assistant's drafting in Phase 4. They do not apply to RaLHF's context selection in Phase 2. RaLHF presents the inventory and runs the amendment ask. RaLHF does not pause to ask the customer task questions, even when a personalized rule sounds like it wants RaLHF to.

## Step 2: Call `get_wiki_catalog`

Returns wiki orientation — narrative summary, total page count, per-type counts, top tags, top namespaces, last-updated timestamp, and **the top ~5 pages per page_type by source-count / recency**.

### What the catalog IS good for

- The **narrative summary** (one paragraph describing what the wiki contains overall) — useful for orienting Phase 1 discovery once "pull" is given. (Note: the catalog is NOT fetched before the ask-first gate; this is post-pull.)
- The **stats** (`total_pages`, `by_type` counts, `top_tags`, `top_namespaces`, `last_page_updated_at`) — these are exhaustive and accurate.
- The **top ~5 pages per type** — useful as a "what does this user have a lot of?" signal and a starting set of candidate page IDs.

### What the catalog is NOT

**The catalog page lists are TRUNCATED — typically to 5 pages per type when the type has more than 5 pages.** A wiki with 939 pages may return only ~21 pages in the catalog response (the top-5 per type plus the comparison type). The remaining ~98% of pages are invisible from the catalog alone.

**This means the catalog is NOT the discovery surface.** It is the orientation map. To reach the long tail in Phase 1, use `browse_wiki` aggressively with combined filters (`page_type + tag + search_text`) and pagination (`offset` + `limit=100`). See `references/discover.md` Step 3 for the workhorse pattern.

If you find yourself picking only from the catalog's top-5-per-type and ignoring the long tail, you're missing 90%+ of the wiki. `browse_wiki(page_type=<type>, search_text=<task-keyword>)` is the way past that.

## Apply the playbook silently throughout the session

- Phase 1: when picking pages from the catalog, follow the operational rules, retrieval strategies, and trigger signals in the block. Skip pages it says to skip, include pages it says to include, use the retrieval strategy it specifies for this task type.
- Phase 2: apply source preferences and tie-breakers before asking the customer to resolve conflicts.
- Step 3a: honor connector preferences from the block.
- Phase 5: when the customer corrects something or expresses a preference, save it via `remember` so the playbook grows.

The customer doesn't see the rules being applied. They just see RaLHF behaving consistently with what they've taught it.

If the block is empty, fall back to generic behavior and move on.

## When both calls return, proceed to Phase 1

No greeting here — identity was already carried by the ask-first gate. Go straight into discovery.
