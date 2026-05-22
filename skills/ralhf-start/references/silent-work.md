# Phase 0 silent work

After the greeting (and never narrated to the customer), run these calls in sequence.

**Phase 0a already fired `get_my_mcp_usage`** before the greeting (it gates the Small-task opt-in and informs greeting length). Its `usage_count` is in hand. Phase 0 silent work covers the remaining calls.

**Light-flow exception:** if Phase 0a routed to the opt-in AND the customer said "yes" (Small + veteran branch), skip Step 2 (`get_wiki_catalog`). Only Step 1 (`get_instructions`) runs. See `references/task-triage.md`.

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

Some personalized rules apply to RaLHF's context selection (what to fetch, which sources to trust). Some apply to Claude's drafting (tone, structure, briefing requirements).

Rules that demand task-input clarifications ("never propose structure until a briefing is shared", "always ask the audience first") apply to Claude's drafting in Phase 4. They do not apply to RaLHF's context selection in Phase 2. RaLHF presents the inventory and runs the amendment ask. RaLHF does not pause to ask the customer task questions, even when a personalized rule sounds like it wants RaLHF to.

## Step 2: Call `get_wiki_catalog`

Returns the grouped table of contents of the customer's wiki.

## Apply the playbook silently throughout the session

- Phase 1: when picking pages from the catalog, follow the operational rules, retrieval strategies, and trigger signals in the block. Skip pages it says to skip, include pages it says to include, use the retrieval strategy it specifies for this task type.
- Phase 2: apply source preferences and tie-breakers before asking the customer to resolve conflicts.
- Step 3a: honor connector preferences from the block.
- Phase 5: when the customer corrects something or expresses a preference, save it via `remember` so the playbook grows.

The customer doesn't see the rules being applied. They just see RaLHF behaving consistently with what they've taught it.

If the block is empty, fall back to generic behavior and move on.

## When both calls return, proceed to Phase 1

No second greeting.
