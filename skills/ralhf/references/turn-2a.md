# Turn 2a: Starting context

> **This is the Turn 2a inventory format.** RaLHF assembles the four-source inventory in Phase 2 and posts it as a customer-facing text message with a short "anything to add or remove?" ask. The final green light comes later, at the Step 3b pre-handoff check-in. See `SKILL.md` → Phase 2 / Phase 3.

The four-source canonical order, drop-empties/keep-names/renumber, the bullet formats (Section 1 wiki pages are a single linked title; Sections 2–3 documents are two-line with date + description), per-section identifier/link rules, and the closing-ask rules are all stated in `SKILL.md` → Phase 2 → Turn 2a → Format. This file holds the examples, the mechanical link-check, the WRONG/RIGHT side-by-sides, the design history, and the banned-moves list.

## Why drop empties but keep descriptive names

Two failure modes to avoid, and how this design avoids both:

**1. Clutter from empty sections.** Earlier versions printed all four headers every time, each empty one carrying a "we checked and found nothing" status line. On a task where only the wiki and memory had content, the customer read four headers and two apologies. The package looked padded. **Fix:** a source with no task-relevant content is dropped entirely — no header, no status line. The message shows only what's actually there.

**2. Mislabeling when numbers float.** An even older version renumbered by position and the AI would promote the next source to fill a gap — labeling "Documents from the Cowork folder" as Section 1 when the wiki was empty, so the customer expecting wiki content saw local files and lost trust. **Fix:** every header keeps its full descriptive name ("From your personal wiki", never just "Section 1"). The leading number is purely sequential over the sources that survived; because the customer reads the name, a renumber can't mislabel what they're looking at.

So: drop empties (no clutter), keep names (no mislabeling), number the survivors `1..N` in canonical order.

## Why four sections, not three

v3.5.0 and v3.5.2 used three sections, with library documents nested as sub-bullets under their parent wiki page in Section 1. The idea was to force `batch_fetch` by making the format require source arrays. The trade-off cost us library visibility: the AI silently deduplicated source documents that also appeared in Section 3 (Cowork folder), which made the entire library category invisible to the customer.

v3.5.3 restores the library as its own Section 2. The fetch is now forced by independent rules (strict one-item-per-call, spill recovery, "wiki page must be fetched to appear" rule). Nesting is no longer needed for that purpose. The four-section structure gives the library its own category and surfaces documents that exist only in the library, not just those that happen to mirror local files.

## Pre-flight

The hard pre-flight before composing Turn 2a is `SKILL.md` Phase 1 (discovery/fetch checklist) + Phase 2 (Turn 2a format rules). Run those. The one Turn-2a-specific mechanical gate not stated there:

**Mechanical link check — does EVERY Section 2 bullet contain the substring `](`?** Each `sources[]` item returns a `url` (typically `https://app.ralhf.ai/my-content?fileId=...`); Section 2 filenames MUST be wrapped as `[<filename>](<url>)`. Scan your drafted Section 2: if any bullet's filename is bare bold text with no `](` in it, you dropped the link — fix it before sending. This is the single most common Turn 2a regression: the model links Section 1 (wiki pages) but renders Section 2 (library docs) unlinked. They are NOT optional — `sources[].url` is always present. (Live-session evidence: every library `sources[]` item carries a populated `url`; an unlinked Section 2 is always a rendering miss, never missing data.)

## Full format example

```
After searching through your context, here's what I think is most relevant for the Q1 board deck:

**1. From your personal wiki**
- **[Q1 2026 Board Meeting](https://app.ralhf.ai/wiki/...)**
- **[Bot Food Corporation](https://app.ralhf.ai/wiki/...)**
- **[Board Reporting Standards](https://app.ralhf.ai/wiki/...)** · shared · Bot Food Finance

**2. Documents from your personal context library**
- **[Q1_2026_Quarterly_Update.docx](https://app.ralhf.ai/my-content?fileId=...)** (Apr 3, 2026)
  Canonical Q1 narrative, financials, customer growth
- **[Bot Food - Brand Guidelines v3.9.pdf](https://app.ralhf.ai/my-content?fileId=...)** (May 3, 2026)
  Current brand spec, colors, fonts
- **[2026_OKRs.docx](https://app.ralhf.ai/my-content?fileId=...)** (Jan 6, 2026)
  Company OKRs feeding the board narrative

**3. Documents from the Cowork folder**
- **2025-q4-board-deck.pptx** (Jan 14, 2026)
  Last quarter's deck, structural template
- **botfood-board-narrative-notes.md** (Apr 20, 2026)
  Working notes on the Q1 narrative arc

**4. The AI's memory**
- **Board deck format preference**: tight executive summary; detailed data in appendix
- **Last board deck timing**: 18 slides came in 12 minutes under the meeting block

Does this look right? Anything to add or remove?
```

That example has all four sources. When some are empty, they're dropped and the rest renumber. Same task, but this session has no library docs and no Cowork folder mounted — so only the wiki and memory sources appear, numbered 1 and 2:

```
After searching through your context, here's what I think is most relevant for the Q1 board deck:

**1. From your personal wiki**
- **[Q1 2026 Board Meeting](https://app.ralhf.ai/wiki/...)**
- **[Bot Food Corporation](https://app.ralhf.ai/wiki/...)**

**2. The AI's memory**
- **Board deck format preference**: tight executive summary; detailed data in appendix

Does this look right? Anything to add or remove?
```

No "2. Documents from your personal context library — none found" stub, no "3. Documents from the Cowork folder — no folder mounted" stub. The two empty sources are simply gone, and memory takes the `2` slot.

## Rules for the findings list

Per-section identifier/link rules, the verbatim-filename rule, the bullet formats (Section 1 single linked title; Sections 2–3 two-line with date + description), and "never fabricate a URL" are in SKILL.md Phase 2 → Turn 2a → Format. The Turn-2a-specific operational details not stated there:

- **Section 1 wiki pages carry NO date and NO description** — just the linked title (plus the shared tag on shared pages). The date + description belong to documents only.
- **Date is the last-modified date** in `<Mon D, YYYY>` format, for **Sections 2–3 documents only**. For library and Cowork files use the file's modified date. If the date is unknown, write `undated`. (Section 1 wiki pages show no date at all — do not print `last_updated_at`.)
- **Personal vs. shared origin (Section 1 only).** The wiki mixes the customer's **personal** pages and **shared** pages (from shared groups; internally *potlucks*). Personal pages are unmarked. A page that came from a shared group gets ` · shared · <group name>` appended to its single-line bullet: `- **[<title>](<url>)** · shared · <group name>`. The group name is the `team_name` value from the catalog's `teams[]` (e.g. `Bot Food Finance`), never a bare "shared" or an invented label. Origin is determined by the scoped discovery (`references/discover.md` → personal vs. shared origin), not by guessing from the title. Do NOT tag personal pages, and do NOT split shared pages into their own section — they stay in Section 1, tagged, sorted by relevance alongside personal pages.
- **Group by source, list by relevance.** Within each section, the most task-relevant item comes first.
- **No artificial count cap.** A long Turn 2a with 10+ relevant docs is fine. Trim by relevance, not length.
- **A library document that's also in the Cowork folder appears in BOTH Section 2 and Section 3.** Do not silently dedupe — the duplication tells the customer the document is referenced from the wiki AND exists locally. (Same rule restated in the banned-moves list for visibility.)

## Banned in Turn 2a

- **Three-section structure with nested sources.** That was v3.5.0–v3.5.2. v3.5.3+ uses four flat sections with library as Section 2.
- **Empty-section status lines.** A source with no content gets dropped, NOT a "No task-relevant files in the Cowork folder" / "No task-relevant memory entries" stub. The only allowed top-of-message note is the wiki-unreachable degraded-state warning.
- **Headers without their descriptive name.** Every header is the full string ("From your personal wiki", etc.) prefixed by its sequential number. A bare "Section 1" with no name is banned — the name is what prevents renumbering from mislabeling.
- **Presenting a shared page as personal.** Section 1 mixes personal and shared (*potluck*) pages. A page from a shared group MUST carry its ` · shared · <group name>` tag — leaving it untagged passes a shared page off as the customer's own, the exact mislabeling this format guards against. Conversely, do NOT tag personal pages `· personal` — personal is the unmarked default, and tagging every bullet is noise. And do NOT invent a group name or write a bare `· shared`: the group name is the `team_name` from the catalog's `teams[]`. If origin wasn't established by scoped discovery, go get it — don't guess.
- **Mislabeling a source under the wrong name.** Renumbering is sequential over surviving sources, but the NAME never moves: don't ever print local files under "From your personal wiki" or memory under "Documents from the Cowork folder". The number floats; the name+content pairing does not.
- **Wiki pages with no `batch_fetch` data.** If you list a wiki page in Section 1, you must have fetched it. Section 2 is populated from those pages' `sources[]` arrays — without the fetch, Section 2 is empty.
- **Multi-item `batch_fetch` calls.** Always one item per call. Multi-item calls spill. If you spilled, retry one-at-a-time.
- **Silent dedup between Section 2 and Section 3.** A document that exists in both places appears in both sections. Duplication is signal.
- **Em dashes as separators between filename and description.** `**filename** (date) — description` is banned. Use the two-line format: filename and date on line 1, description indented on line 2.
- **Using the human-readable `title` field for Section 2 items when a `filename` is available.** Library source documents must render with their `filename` field (extension included). Falling back to the title because it "reads nicer" is the named failure mode — the customer needs to know which actual file is being pulled, not a rephrased label. The `sources[]` data has BOTH fields; pick `filename`.
- **Humanizing the filename when rendering Section 2.** The model's instinct to strip underscores, strip extensions, or title-case the filename is wrong here. If the `filename` field is `Q1_2026_Quarterly_Update.docx`, the rendered text is `Q1_2026_Quarterly_Update.docx` — not `Q1 2026 Quarterly Update`, not `Q1 2026 Quarterly Update.docx`, not `q1_2026_quarterly_update.docx`. Verbatim means verbatim. (The customer's live test in v3.7.1 caught this — Section 2 items were rendering as `RaLHF Product Overview and Investment Pitch` when the actual `filename` was `Bot Food - One Pager v2.8.pdf`.)
- **Rendering Section 2 items WITHOUT a markdown link.** `sources[]` returns a `url` for every library document. Unlinked Section 2 items are a regression — the customer cannot click through to open the doc. **Side-by-side:**
  - ❌ WRONG (this is Section 3 format applied to Section 2): `- **Bot Food - One Pager v2.8.pdf** (Apr 21, 2026)`
  - ❌ WRONG (bare verbatim filename, no wrapper): `- Bot Food - One Pager v2.8.pdf (Apr 21, 2026)`
  - ✅ RIGHT (Section 2 format — verbatim filename WRAPPED in markdown link): `- **[Bot Food - One Pager v2.8.pdf](https://app.ralhf.ai/my-content?fileId=caf96653-...)** (Apr 21, 2026)`

  The "verbatim" rule applies to the filename STRING inside the link text — NOT to the markdown formatting around it. Verbatim ≠ unlinked. Section 3 (local Cowork files) stays unlinked because local paths have no URL; Section 2 always has a URL and must use the linked form.
- **Single-line bullets in Sections 2–3.** Every document item there is two lines: filename and date on line 1, description on line 2. (Section 1 wiki pages are the opposite — a deliberate single line, linked title only, no date, no description. Don't "fix" a Section 1 bullet by adding a date or description line.)
- **Adding a date or description to a Section 1 wiki bullet.** Section 1 is the linked title only. Do not append `(updated <date>)` and do not add an indented summary line — that two-line treatment is for documents (Sections 2–3), not wiki pages.
- **Combined entries.** "Logo A, Logo B, Logo C" or "v2.4.pptx + v2.4-context.md" packs multiple files into one bullet. Each file gets its own bullet.
- **Old-style section headers.** "Pages from your RaLHF Wiki", "From the local Marketing folder", "From the AI's memory". The new headers are numbered and exact.
- **Staleness notes, version conflicts, read-and-discard explanations inside Turn 2a.** Those belong in Turn 2b. Turn 2a is strictly inventory + closing ask.

## Read-and-discard pattern

When triaging `sources[]` from fetched wiki pages, RaLHF may pull a source doc, read it, and decide it doesn't materially help. **Default: discard silently.** Don't list it in 2a, don't surface it in Turn 2b. The customer doesn't need to see what RaLHF read-and-rejected.

Exceptions (surface in Turn 2b, one line):
- The discarded content **changes the picture** of an earlier wiki finding. Example: "Read <Doc> but the pricing it cites is superseded by the v2.3 pricing page; sticking with v2.3."
- A **staleness warning** the customer should know about. Example: "Read <prior brand guide doc> but it's flagged outdated; using v3.5."

Otherwise, discarded docs leave no trace in customer-facing chat. RaLHF makes the call as the expert.
