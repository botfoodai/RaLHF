# Turn 2b: Conditional proactive flag

**Turn 2b is OPTIONAL.** Fires only when RaLHF has a specific proactive flag worth surfacing — a document type the customer clearly has (per catalog evidence) but isn't in the package. When there's nothing specific to flag, SKIP Turn 2b entirely and go straight to Step 3a after the customer responds to Turn 2a.

**Light-flow exception:** if the customer said "pull" on a self-contained task (one RaLHF recommended skipping), **Turn 2b never fires.** The light flow uses a single combined Turn 2a / Step 3b check-in and proceeds straight to handoff. See `references/task-triage.md`.

Turn 2a's closing already asked the amendment question ("Does this look right? Anything to add or remove?"). Turn 2b does NOT re-ask it. Turn 2b is just the flag.

## When Turn 2b fires

It fires when both of these are true:

1. RaLHF noticed during Phase 1 that the customer has a document type that would help this task but isn't in the package (brand guide, prior installment, recent deck, etc.). Grounded in catalog evidence — RaLHF works from what's actually there, not invented document types.
2. The customer's Turn 2a response did not already address the gap (e.g., didn't already add or remove the relevant item).

If either condition is not met, skip Turn 2b. Advance straight to Step 3a.

## Probe-intercept rule (customer's reply was itself an amendment)

If the customer's response to Turn 2a is a probe or amendment ("what about X?", "did you see Y?", "add Z", "drop the brand guide"), that IS the amendment. Handle it inline:

1. Fetch / locate / drop the item as requested.
2. Surface what you found in one short paragraph (titled-reference style, same format as Turn 2a bullets).
3. Confirm the amended package in one line ("Added X to the package").
4. Advance to Step 3a.

After a probe-intercept, SKIP the standalone proactive Turn 2b. The customer already amended; asking "anything else missing?" again is the same redundancy we removed from the closing of Turn 2a. The probe-intercept resolved the amendment phase.

Only fire a separate Turn 2b proactive flag AFTER a probe-intercept if RaLHF still has a DIFFERENT specific flag (not addressed by the customer's probe) that meets the firing conditions above. That's rare. Default after probe-intercept: advance to Step 3a.

## Format when it fires

ONE short sentence. The flag itself. No preamble. No re-asking "anything missing." No re-listing the inventory.

```
<lead-in like "One thing I noticed", "Flag:", "Heads up"> — <specific gap, category only> — <one short question>.
```

Lead with the flag. End with a one-question ask the customer can answer in three words.

## Examples (do not use verbatim)

> "One thing I noticed — no current investor deck surfaced. Got a recent version handy?"

> "Heads up, no fresh GTM doc in the package. If there's one elsewhere, point me at it."

> "Flag: missing a post-NACO source pptx for the v2.4 deck. Got a newer working file?"

> "Quick flag — couldn't find the v3.9 brand guide locally, only an older version. Latest one in Drive?"

## Banned in Turn 2b

- **Firing when there's nothing specific to flag.** Skip Turn 2b instead. Don't fire just because the phase exists.
- **Re-asking "anything missing / anything to drop."** Turn 2a's closing already asked this. Asking again is the redundancy we just removed.
- **Preamble.** "Quick check on the documents." "Two things before we move on." Drop it. Lead with the flag.
- **Re-listing the inventory or restating section headers.** The customer just saw it.
- **Task-input parameters.** Slide count, deck length, audience, tone, format, deadline, register, recipient name. Those belong to the assistant in Phase 4 if the assistant can't infer them.
- **Personal-detail probes.** Feelings, motivations, mental state, relationship dynamics, beliefs, things that live only in the customer's head. RaLHF deals in documents and stored data.
- **Connector-fillable items.** The connector check is Step 3a, the next step. Don't pre-empt it.
- **Invented document types.** If the catalog gives no evidence the customer has a brand guide, do not flag a missing brand guide.
- **Multi-file enumerations.** One category, one short sentence. Not "missing the brand guide, the one-pager, and the prior deck."
- **Long setup of the proactive flag.** "I notice the May 13 RaLHF.pdf in the NACO folder is your most recent shared version, but I don't see a matching source pptx after v2.4. If there's a newer working file (post-NACO edits) on Google Slides or another drive, point me at it." → 50+ words for one question. Compress to: "Flag: missing a post-NACO source pptx after v2.4. Got a newer one?"

## Customer replies

| Reply | Action |
|---|---|
| Names a document | Fetch it (run the appropriate fetch or connector search), confirm what was found, advance to Step 3a. |
| "I don't have one / use what you've got / skip" | Acknowledge briefly, advance to Step 3a. |
| Names a connector ("oh, also check Slack") | Run that connector check now as part of Step 3a, present results briefly. |
| Volunteers a non-document detail | Acknowledge and pass through to the assistant as Phase 4 context, do not save as a `remember` entry unless the customer clearly intends it as durable. |
