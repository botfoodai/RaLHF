# Context Fingerprint

A context fingerprint is a short natural-language description of a page's
structural characteristics. It is stored in the view file's YAML front matter
as the `context` field and used to distinguish page variants that share the
same URL pattern (premium vs. free tiers, A/B tests, geo variants).

## What a context describes (4 dimensions)

Every context covers exactly four dimensions:

1. **Layout pattern** — The overall page arrangement. Examples: "single-column
   article with hero image", "two-panel dashboard with sidebar navigation",
   "card grid with filters above".

2. **Key structural elements** — The major sections visible on the page.
   Examples: "header, search bar, results list, pagination footer",
   "profile banner, tab bar, activity feed". List 3–6 elements.

3. **Content volume** — Approximate density and count. Examples: "~25 items
   per page", "single long-form article with 5–10 paragraphs", "3-column
   pricing table with 4 tiers".

4. **Notable interactive elements** — Buttons, forms, expandable sections,
   or other interactive components that characterize the variant. Examples:
   "load more button at bottom", "accordion FAQ sections", "no interactive
   elements beyond navigation links".

## What it must NOT include

A context fingerprint must never reference implementation details that break
on a redesign:

- CSS selectors (e.g., `.card-grid > .item`)
- Class names (e.g., `result-item`, `premium-badge`)
- HTML element IDs (e.g., `#main-content`)
- Tag names used as identifiers (e.g., "uses `<article>` tags")
- Data attributes (e.g., `data-testid="product-card"`)
- Specific pixel dimensions or breakpoints

The context describes what the user *sees*, not how the developer *built it*.

## How to generate

### From stripped DOM (Chrome path)

After stripping the DOM (Phase 1), analyze the remaining structure:
1. Identify the overall layout pattern from the tag hierarchy.
2. List the major visible sections (headers, content areas, sidebars, footers).
3. Estimate content volume from the number of repeated elements.
4. Note interactive elements from buttons, forms, and expandable widgets.

### From raw HTML (CLI path)

After fetching via `curl`, scan the HTML:
1. Identify layout from semantic tags (`<main>`, `<aside>`, `<nav>`) and
   major container patterns.
2. List sections from heading hierarchy (`<h1>`–`<h3>`) and landmark roles.
3. Count repeated elements (list items, table rows, card containers).
4. Note forms, buttons, and other interactive elements.

### For API-based pages

When the strategy is `api_direct` or `api_intercept`, the page typically
loads data via JavaScript after initial render. The context should note:

1. **Layout pattern** — describe what the user sees (same as DOM), but note
   that content is dynamically loaded.
2. **Key structural elements** — include the loading state (spinners,
   skeleton screens) if visible, and the populated state.
3. **Content volume** — describe the volume from the API response, not just
   what's rendered in the initial viewport.
4. **Data loading pattern** — note that content arrives via API calls.
   Example: "Data loads via paginated API calls triggered by scrolling"
   or "All data fetched in a single GraphQL query on page load."

This helps distinguish between a page that loads data via API (where DOM
selectors would target dynamically-rendered elements) and a server-rendered
page with the same visual layout.

### For export-based pages

When the strategy is `export_download`, note the export mechanism in the
context:

- "A 'Download all' link provides CSV export of the full dataset."
- "An export button generates an XLSX file on demand."

This distinguishes the variant from a DOM-scraping variant of the same page.

### Output format

Write 2–4 sentences covering all four dimensions. Keep it concise — the
context is for machine comparison, not human documentation.

**Example**:
> Single-column article layout with a hero image, author byline, and
> publication date above the body text. The body contains 8–12 paragraphs
> with inline images and pull quotes. A comment section with ~20 threaded
> comments follows the article. Share buttons and a "related articles"
> carousel appear at the bottom.

## How to compare

Context comparison uses semantic LLM judgment — not string matching,
not hashing. The comparing agent reads the stored context and the live
context, then classifies the relationship.

### Classification outcomes

| Outcome | Criteria | Action |
|---|---|---|
| **Match** | Same layout pattern + same major sections + similar volume. Minor differences in styling, updated content, or small section additions/removals are acceptable. | Use this view file. |
| **Mismatch** | Different layout pattern OR missing/added major sections OR fundamentally different content volume (e.g., list vs. single item). | This is a different variant. |
| **Ambiguous** | Unclear whether structural differences are cosmetic or fundamental. | Default to repair — treat as match. |

### Comparison guidance

- "Same layout with updated styling" → **match**. A CSS redesign that keeps
  the same sections and structure is not a new variant.
- "Same content, different layout" → **mismatch**. A mobile-optimized layout
  that collapses a sidebar into a hamburger menu is structurally different.
- "Same layout, different tier content" → **mismatch**. A premium page with
  additional sections (downloads, reviews, extended data) that a free page
  lacks is a different variant.
- "Same layout, slightly different item count" → **match**. Pagination
  differences or content updates do not create new variants.

## Decision flow

When the warm path detects >30% required field failures:

```
Generate live context from current page
        │
        ▼
Load stored contexts from all files in the view's `files` array
        │
        ▼
Compare live context against each stored context
        │
        ├── Matches active view → repair selectors (Step 5)
        │
        ├── Matches a different view file → switch active view,
        │   re-execute from Step 2 (one retry — do not re-enter
        │   context comparison on the retry)
        │
        ├── No match → author new variant via cold path,
        │   append to `files` array, extract + present
        │
        └── Legacy file (no stored context) → backfill context
            into the view file + repair selectors (Step 5)
```

## Example contexts

**Listing page (search results)**:
> Grid layout with a search bar at top and filter sidebar on the left.
> The main area displays ~20 result cards in a 4-column grid, each with
> a thumbnail, title, price, and rating. Pagination controls appear at the
> bottom with numbered page links.

**Article page**:
> Single-column article with a hero image, title, author byline, and
> publish date. The body contains 6–10 paragraphs with occasional inline
> images. A related-articles section with 3 horizontal cards follows the
> body.

**Premium product page**:
> Two-column product layout with an image gallery on the left and details
> panel on the right. The details panel includes price, availability,
> specifications table, and customer reviews section (~15 reviews with
> ratings). A "Buy Now" button and quantity selector are prominent.

**Free product page (same URL pattern, different variant)**:
> Two-column product layout with a single product image on the left and
> a details panel on the right. The details panel includes price and a
> brief description only — no specifications table, no reviews section.
> A "Sign up for full details" banner replaces the buy button.
