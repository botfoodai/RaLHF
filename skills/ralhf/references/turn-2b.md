# Turn 2b: Conditional proactive flag

> **Turn 2b is the proactive gap-flag** for a suspected-missing document — it fires (when warranted) before the Step 3b inventory. Its job: flag a document type the customer clearly has but RaLHF couldn't surface. It is not package-approval; the include/exclude and green light happen at the Step 3b inventory.

The Turn 2b firing condition, the probe-intercept rule, the one-sentence format, the light-flow exception, and the banned list are stated in `SKILL.md` → Phase 2 → Turn 2b. This file holds the example flags, the compression before/after, and the customer-reply table.

## Examples (do not use verbatim)

> "One thing I noticed - no current investor deck surfaced. Got a recent version handy?"

> "Heads up, no fresh GTM doc in the package. If there's one elsewhere, point me at it."

> "Flag: missing a post-NACO source pptx for the v2.4 deck. Got a newer working file?"

> "Quick flag - couldn't find the v3.9 brand guide locally, only an older version. Latest one in Drive?"

## Compression before/after

The banned list (in SKILL.md) forbids long setup of the proactive flag. Concrete example — too long, then compressed:

> ✗ "I notice the May 13 RaLHF.pdf in the NACO folder is your most recent shared version, but I don't see a matching source pptx after v2.4. If there's a newer working file (post-NACO edits) on Google Slides or another drive, point me at it." → 50+ words for one question.
>
> ✓ Compress to: "Flag: missing a post-NACO source pptx after v2.4. Got a newer one?"

## Customer replies

| Reply | Action |
|---|---|
| Names a document | Fetch it (run the appropriate fetch or connector search), confirm what was found, advance to Step 3a. |
| "I don't have one / use what you've got / skip" | Acknowledge briefly, advance to Step 3a. |
| Names a connector ("oh, also check Slack") | Run that connector check now as part of Step 3a, present results briefly. |
| Volunteers a non-document detail | Acknowledge and pass through to the AI as Phase 4 context, do not save as a `remember` entry unless the customer clearly intends it as durable. |
