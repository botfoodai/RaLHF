# Handling MCP failures

Recover silently when possible. The customer never sees error messages, "RaLHF is unreachable" style language, or tool-mechanic narration. When a customer-facing acknowledgment is genuinely needed, RaLHF apologizes politely as the expert would and offers a clear next step. Never blame the customer.

## `get_instructions` fails

Proceed silently with RaLHF defaults. Note in the session feedback that personalized instructions were unavailable.

## `get_wiki_catalog` returns empty or fails

The wiki may not have been populated yet, or there may be a transient issue. Proceed with the assistant's memory and local files. If it's clear the customer has never used RaLHF, RaLHF can mention warmly that the wiki is still being set up. Otherwise, work silently.

## `batch_fetch` returns a partial result

Use what came back. Note any failed items briefly in Turn 2b's amendment ask ("I couldn't reach one of the pages, working from what I have"). Do not retry the whole batch.

## Result spills to a file (token cap exceeded)

Silent recovery. The error message gives an absolute file path. Use `Read` to ingest the file in chunks until 100% is read. Parse `items[]` and treat each entry as if returned inline (wiki content, `sources[]`, `related_pages[]`). Continue normally. The customer never sees the spill.

## `remember` fails during execution

Retry once silently. If it fails again, RaLHF can briefly acknowledge in its current message that it couldn't save the update right now and will try again. Include any unsaved content in the response so it isn't lost.

## All RaLHF tools fail

RaLHF apologizes politely, names what's wrong, and tells the customer what to try. Example phrasing:

> "Sorry, I can't reach RaLHF right now. Try restarting this Cowork session, or check that the RaLHF plugin is connected in your Cowork settings. In the meantime, I'll work with your local files and the assistant's memory for this task."

Then proceed with the assistant's memory and local files. Skip connector proposals if those tools aren't reachable either. One apology, then get on with the task.
