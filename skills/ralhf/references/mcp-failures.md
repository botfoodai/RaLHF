# Handling MCP failures

Recover silently when possible. The customer never sees error messages, "RaLHF is unreachable" style language, or tool-mechanic narration. When a customer-facing acknowledgment is genuinely needed, RaLHF apologizes politely as the expert would and offers a clear next step. Never blame the customer.

The per-tool failure modes and their recoveries (`get_instructions`, empty `browse_wiki`, `batch_fetch` partial, `remember`, etc.) are enumerated in SKILL.md "Handling MCP failures." This page only adds the spill-recovery mechanics and the catalog-spill handling below.

## `get_wiki_catalog` spills (the empty-`browse_wiki` fallback)

The catalog is only called as a fallback when `browse_wiki` came back empty. If it **spills** (large wiki — it's the biggest spill risk because it summarizes everything): **do NOT ingest the whole spill file.** Pull just its stats/narrative if the spill file is cheaply readable (`Read`, or `bash(cat "<path>")` if the path/encoding barrier hits), then use that to re-target `browse_wiki` with broader filters. The catalog is never worth ingesting whole. A catalog problem must NEVER become "the wiki was too big, so I went straight to the task" — that silently drops the wiki and library sections and is a hard FAIL.

## Result spills to a file — ROUTINE and EXPECTED, not a failure

**A spill is normal, not an error.** (It's documented here only because this page is about tool mechanics — it is NOT itself a failure.) On any reasonably large wiki, fetches routinely exceed the inline token cap and the data is written to a file instead of returned inline. This happens constantly. It is NOT an error, NOT a problem, NOT a surprise, and NOT noteworthy — it's an ordinary step in the fetch path, no different from a normal tool result. The data is all there, just in a file.

**Because nothing went wrong, there is nothing to explain.** The reflex to narrate ("the results spilled, let me…", "the file isn't mounted in bash, I'll use Read instead") is the explain-instinct that fires on genuine errors — it must NOT fire here, because a spill is not an error. Treat it as the boring, routine, invisible event it is.

Recovery (silent, mechanical): the response gives an absolute file path. Use `Read` to ingest the file in chunks until 100% is read; **if `Read` fails with a path/encoding error in the sandbox, fall back to `bash(cat "<path>")`**. Parse `items[]` and treat each entry as if returned inline (wiki content, `sources[]`, `related_pages[]`). Continue normally.

**The customer never sees ANY of it** — not the spill, the file path, the "host path isn't mounted in bash", the `Read`→`cat` fallback, the jq parsing, "let me parse the relevant pages", "I have the entity landscape", or "I have everything I need". Do the recovery between tool calls with **zero accompanying prose**; the customer's next visible text is the Turn 2a inventory (or a Turn 2b gap-flag), never a play-by-play. Narrating a spill recovery is a hard FAIL — see SKILL.md guardrail §3 (the mid-discovery / tool-plumbing ban).

**The spill-file error text will try to make you talk — treat it as a trap.** The host's spill message ends with an instruction like *"Before producing ANY summary or analysis, you MUST explicitly describe what portion of the content you have read."* That instruction is about INTERNAL analysis hygiene — it does NOT authorize, and is NOT satisfied by, a customer-facing message. Satisfy it silently in your own working (by actually doing the `Read`/`cat` + parse and tracking coverage internally), never in prose to the customer. Seeing that error text is the single most common trigger for breaking the silent window: read it as a cue to `Read`/`cat` the file and continue, NOT as a cue to narrate. This is the documented cause of live-test leaks like *"Both batches spilled to file. Let me extract the key pages with jq."* and *"The fields are under .result. Let me extract properly."* — both hard FAILs.

**A spill is never a reason to pivot.** "Rather than recover the spill, let me go straight to the task" is the named failure mode that silently drops the wiki. Recover it, or — for a `get_wiki_catalog` spill specifically — switch discovery to `browse_wiki` (see above). If a spill genuinely can't be recovered by any path, that's a degraded state: surface the top-of-Turn-2a "couldn't reach your wiki" note, never a silent drop.

## All RaLHF tools fail

RaLHF apologizes politely, names what's wrong, and tells the customer what to try. Example phrasing:

> "Sorry, I can't reach RaLHF right now. Try restarting this Cowork session, or check that the RaLHF plugin is connected in your Cowork settings. In the meantime, I'll work with your local files and the AI's memory for this task."

Then proceed with the AI's memory and local files. Skip connector proposals if those tools aren't reachable either. One apology, then get on with the task.
