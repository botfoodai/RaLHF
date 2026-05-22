# Turn 2a: Starting context

One message. **Four sections with FIXED identities.** Section 1 is always "From your personal wiki." Section 2 is always "Documents from your personal context library." Section 3 is always "Documents from the Cowork folder." Section 4 is always "Claude's memory." All four headers appear every time — no renumbering, no skipping. An empty section shows a one-line status, never disappears.

Turn 2a is strictly the inventory + closing ask. Staleness notes, version conflicts, read-and-discard explanations all go in Turn 2b — NOT here.

## Why fixed identities, not floating numbers

Previous versions renumbered sections when one was empty. That rule caused the worst class of bugs we kept hitting: the AI promotes the next section to fill the gap and ends up labeling "Documents from the Cowork folder" as Section 1 because the wiki fetch failed. The customer thinks Section 1 = wiki, sees Cowork folder content instead, loses trust.

Fixed identities eliminate that bug class. The customer always sees four headers in the same order. If a section is empty, they see a one-line status telling them why. The AI cannot accidentally mislabel a section because the labels are predetermined.

## Why four sections, not three

v3.5.0 and v3.5.2 used three sections, with library documents nested as sub-bullets under their parent wiki page in Section 1. The idea was to force `batch_fetch` by making the format require source arrays. The trade-off cost us library visibility: the AI silently deduplicated source documents that also appeared in Section 3 (Cowork folder), which made the entire library category invisible to the customer.

v3.5.3 restores the library as its own Section 2. The fetch is now forced by independent rules (strict one-item-per-call, spill recovery, "wiki page must be fetched to appear" rule). Nesting is no longer needed for that purpose. The four-section structure gives the library its own category and surfaces documents that exist only in the library, not just those that happen to mirror local files.

## Hard pre-flight before composing Turn 2a

Each item is required, not optional.

- [ ] Does the message start with an intro line that says I searched through the customer's context and is presenting the most relevant cut? Required pattern: something like "After searching through your context, here's what I think is most relevant for `<task>`:" Banned: "Here's what I've got", "Here's the context", "Found a solid base", "Here are the documents I think are relevant".
- [ ] Are ALL FOUR section headers present, EXACTLY: `**1. From your personal wiki**`, `**2. Documents from your personal context library**`, `**3. Documents from the Cowork folder**`, `**4. Claude's memory**`? Four headers, in this order, every message. No renumbering. No skipping.
- [ ] Does each section either have items OR a one-line empty-section status line? See "Empty section status" below for exact wording.
- [ ] **For each wiki page in Section 1, did I `batch_fetch` it with ONE item per call?** A wiki page that has not been fetched cannot appear. If a fetch call spilled because I batched multiple items, did I retry with single-item calls?
- [ ] **Did I populate Section 2 from the `sources[]` arrays of the fetched wiki pages?** Task-relevant source documents go in Section 2 as flat bullets. A document that's also in Section 3 (Cowork folder) appears in BOTH — duplication is signal.
- [ ] Is every top-level item in the strict two-line bullet format: `- **<filename or title>** (<date>)` on line 1, two-space indented short description on line 2? No em dashes anywhere. No `—` separator between filename and description. No single-line bullets. Wiki page titles can be markdown-linked.
- [ ] **Is every item a SINGLE document?** No combined entries like `v2.4.pptx + v2.4-context.md`. No "Logo A, Logo B, Logo C" entries. If three related files belong in the inventory, give them three separate bullets.
- [ ] **Is every description 12 words or fewer?** Tell the customer what the document IS, not what it says.
- [ ] **Are descriptions document descriptions ONLY?** No version-comparison notes ("newer than X", "may be behind Y"), no staleness flags, no cross-document commentary. Comparisons and staleness go in Turn 2b. Example: ✗ "Latest brand spec, newer than local v3.6" / ✓ "Latest brand spec, colors and fonts".
- [ ] Am I avoiding ALL task-input questions? Slide count, audience, tone, format, deadline, "what's the brief", "are we iterating v2.4 or starting fresh", "anything to change from v2.4". These belong to Claude in Phase 4.
- [ ] Have I kept staleness notes, version conflicts, and read-and-discard explanations OUT of Turn 2a? Those belong in Turn 2b.
- [ ] Is the closing one short ask that signals the amendment step is coming next? Not "what's the brief". Just "does this look right" or "is this the right foundation".

If any box is unchecked, fix it before sending the message.

## Empty section status (one-line replacement)

When a section has no items, the section header still appears but is followed by ONE status line instead of bullets. Pick the appropriate wording:

**Section 1 (From your personal wiki) empty cases:**
- Wiki fetch failed or unreachable:
  > Wiki couldn't be reached this session. Working from local files and memory only.
- No task-relevant wiki pages found:
  > No wiki pages matched this task. Catalog scanned but nothing applied.

**Section 2 (Documents from your personal context library) empty cases:**
- No task-relevant source documents in the fetched wiki pages:
  > No task-relevant documents in your context library.
- Wiki itself couldn't be reached (Section 1 also empty):
  > Library unreachable along with wiki.

**Section 3 (Documents from the Cowork folder) empty cases:**
- No Cowork folder mounted:
  > No Cowork folder mounted this session.
- Folder mounted but no task-relevant files:
  > No task-relevant files in the Cowork folder.

**Section 4 (Claude's memory) empty cases:**
- Memory has nothing applicable:
  > No task-relevant memory entries.

The status line confirms RaLHF checked the source. The customer sees the AI did the work even when the result was empty.

## The four sections (fixed identities)

1. **From your personal wiki** — wiki pages from the customer's RaLHF wiki that match the task. Each page is a flat bullet with its title (linked), update date, and brief description. Wiki pages MUST have been `batch_fetch`-ed before they appear here.

2. **Documents from your personal context library** — the task-relevant source documents from those wiki pages' `sources[]` arrays. Flat bullets. A document that ALSO exists in the Cowork folder (Section 3) is listed in both — that signals the document is referenced from the wiki AND exists locally.

3. **Documents from the Cowork folder** — local project files that apply (only when running in Cowork mode with a local folder mounted).

4. **Claude's memory** — facts or notes Claude has stored about the customer that are relevant to this task and not duplicated by Sections 1, 2, or 3.

All four headers appear in every Turn 2a message, in this order. An empty section gets a one-line status (see "Empty section status" above), not a renumber. Do NOT skip headers. Do NOT renumber.

## Format per item

All three document sections (1, 2, 3) use the same two-line bullet format:

```
- **<filename or page title>** (<date>)
  <very short description, 5 to 12 words>
```

- Line 1: bolded filename or wiki page title (linked to URL when available). Date in parentheses.
- Line 2: indented, brief description. Aim for 5 to 12 words. Tell the customer what the document IS, not what it says.

When the description is short enough, collapse to one line:

```
- **<filename>** (<date>): <very short description>
```

Section 4 (Claude's memory entries are facts/notes, not documents):

```
- **<topic>**: <brief relevant fact>
```

One line per memory entry. No date stamp (memories aren't files). Keep it short.

## Closing check-in

ONE short ask. Both halves of the amendment question combined in a single closing. Do NOT preview a future ask — ask the real question now. Examples:

> "Does this look right? Anything to add or remove?"

> "Is this the right foundation? Anything missing or to drop?"

> "Does that cover the base? Anything to add, remove, or swap?"

Vary the phrasing every fire. The closing IS the amendment ask. If the customer responds with a clean confirm ("good", "sure", "looks right"), there is no separate Turn 2b ask — proceed straight to Step 3a unless RaLHF has a specific proactive flag to surface.

### Banned closings

- "Once you confirm, I'll ask if anything's missing or should come out." — previews a redundant future ask.
- "After this I'll ask if anything should be added or removed, then we can decide on connectors." — wasted text, ask the question now.
- "What's the brief?" / "Which direction are we going?" — task-input questions, those are Claude's.

## Full format example

```
After searching through your context, here's what I think is most relevant for the Q1 board deck:

**1. From your personal wiki**
- **[Q1 2026 Board Meeting](https://app.ralhf.ai/wiki/...)** (updated Apr 12, 2026)
  Confirms the May 5 meeting date and 6-section rhythm
- **[Bot Food Corporation](https://app.ralhf.ai/wiki/...)** (updated May 14, 2026)
  Business overview and current entity profile

**2. Documents from your personal context library**
- **Q1 2026 Quarterly Update.docx** (Apr 3, 2026)
  Canonical Q1 narrative, financials, customer growth
- **Brand Guidelines v3.9.pdf** (May 3, 2026)
  Current brand spec, colors, fonts
- **2026 OKRs.docx** (Jan 6, 2026)
  Company OKRs feeding the board narrative

**3. Documents from the Cowork folder**
- **2025-q4-board-deck.pptx** (Jan 14, 2026)
  Last quarter's deck, structural template
- **botfood-board-narrative-notes.md** (Apr 20, 2026)
  Working notes on the Q1 narrative arc

**4. Claude's memory**
- **Board deck format preference**: tight executive summary; detailed data in appendix
- **Last board deck timing**: 18 slides came in 12 minutes under the meeting block

Does this look right? Once you confirm, I'll ask if anything's missing or should come out.
```

## Rules for the findings list

- **Use the real filename when one exists.** Library documents and Cowork folder files have filenames; use them. Wiki pages don't have filenames; use the page title instead.
- **Link the filename or title** to its URL when one is available. The wiki catalog always returns a `url` per page. Never fabricate a URL.
- **Date is the last-modified date** in `<Mon D, YYYY>` format. For wiki pages use `last_updated_at`. For library and Cowork files use the file's modified date. If the date is unknown, write `undated`.
- **Descriptions are very short.** 5 to 12 words. Describe what the document is, not what it says.
- **Never fabricate filenames, titles, dates, or descriptions.** When metadata is missing, leave it out rather than invent.
- **Group by source, list by relevance.** Within each section, the most task-relevant item comes first.
- **No artificial count cap.** A long Turn 2a with 10+ relevant docs is fine. Trim by relevance, not length.
- **A library document that's also in the Cowork folder appears in BOTH Section 2 and Section 3.** Do not silently dedupe. The duplication tells the customer the document is referenced from the wiki AND exists locally.

## Banned in Turn 2a

- **Three-section structure with nested sources.** That was v3.5.0–v3.5.2. v3.5.3+ uses four flat sections with library as Section 2.
- **Renumbered sections when one is empty.** Section 1 is always "From your personal wiki", Section 2 is always "Documents from your personal context library", Section 3 is always "Documents from the Cowork folder", Section 4 is always "Claude's memory". Empty sections show a one-line status, NEVER get renumbered or dropped.
- **Skipped section headers.** All four section headers appear in every Turn 2a message. If a section is empty, you write its header with a one-line status under it, not blank, not removed.
- **Wiki pages with no `batch_fetch` data.** If you list a wiki page in Section 1, you must have fetched it. Section 2 is populated from those pages' `sources[]` arrays — without the fetch, Section 2 is empty.
- **Multi-item `batch_fetch` calls.** Always one item per call. Multi-item calls spill. If you spilled, retry one-at-a-time.
- **Silent dedup between Section 2 and Section 3.** A document that exists in both places appears in both sections. Duplication is signal.
- **Em dashes as separators between filename and description.** `**filename** (date) — description` is banned. Use the two-line format: filename and date on line 1, description indented on line 2.
- **Single-line bullets.** Every top-level item is two lines. Filename and date on line 1, description on line 2.
- **Combined entries.** "Logo A, Logo B, Logo C" or "v2.4.pptx + v2.4-context.md" packs multiple files into one bullet. Each file gets its own bullet.
- **Old-style section headers.** "Pages from your RaLHF Wiki", "From the local Marketing folder", "From Claude's memory". The new headers are numbered and exact.
- **Staleness notes, version conflicts, read-and-discard explanations inside Turn 2a.** Those belong in Turn 2b. Turn 2a is strictly inventory + closing ask.

## Read-and-discard pattern

When triaging `sources[]` from fetched wiki pages, RaLHF may pull a source doc, read it, and decide it doesn't materially help. **Default: discard silently.** Don't list it in 2a, don't surface it in Turn 2b. The customer doesn't need to see what RaLHF read-and-rejected.

Exceptions (surface in Turn 2b, one line):
- The discarded content **changes the picture** of an earlier wiki finding. Example: "Read <Doc> but the pricing it cites is superseded by the v2.3 pricing page; sticking with v2.3."
- A **staleness warning** the customer should know about. Example: "Read <prior brand guide doc> but it's flagged outdated; using v3.5."

Otherwise, discarded docs leave no trace in customer-facing chat. RaLHF makes the call as the expert.
