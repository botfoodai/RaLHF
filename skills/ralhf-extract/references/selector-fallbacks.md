# Selector Fallbacks

> **Scope**: Applies to `dom_css` and `dom_xpath` strategies only. For
> API, embedded JSON, and export strategies, field resolution failures are
> handled by the strategy-specific repair logic in Phase 3 Step 5.

When a CSS selector from the recipe returns null or empty during warm
extraction (Phase 3), try these fallback strategies in order before marking
the field as missing.

## Fallback Chain

### 1. XPath Equivalent

Convert the CSS selector to an XPath expression and evaluate it:

```javascript
document.evaluate(
  xpathExpr,
  document,
  null,
  XPathResult.FIRST_ORDERED_NODE_TYPE,
  null
).singleNodeValue;
```

Common CSS → XPath conversions:
- `h1.title` → `//h1[contains(@class, "title")]`
- `#main-content` → `//*[@id="main-content"]`
- `div > p:first-child` → `//div/p[1]`
- `[data-testid="price"]` → `//*[@data-testid="price"]`

### 2. Text Content Search

If the field has a `description` in the recipe, use `find_in_page` to search
for text that matches the expected content pattern:

- For a "price" field → search for `$` or currency patterns.
- For a "date" field → search for date-like patterns (`\d{4}-\d{2}-\d{2}`).
- For a "title" field → search for the page's `<title>` tag content.

Then, find the DOM element containing that text:

```javascript
// Find element by text content
const walker = document.createTreeWalker(
  document.body,
  NodeFilter.SHOW_TEXT,
  { acceptNode: (node) =>
    node.textContent.trim().includes(searchText)
      ? NodeFilter.FILTER_ACCEPT
      : NodeFilter.FILTER_REJECT
  }
);
const textNode = walker.nextNode();
const element = textNode?.parentElement;
```

### 3. Accessibility Tree Reference

Use `read_page(filter="interactive")` to get the accessibility tree. Look for
elements matching the field's semantic role:

- Title → heading (level 1)
- Author → text near "by", "author", or byline landmarks
- Date → text with `time` role or near "published", "posted"
- Price → text with currency symbols near "price", "cost"
- Navigation/pagination → `nav` landmarks, links labeled "next", "previous"

### 4. Structural Position

As a last resort, try positional selectors based on common layout patterns:

- Main heading: `h1:first-of-type`, `:is(main, article, [role="main"]) h1`
- Body text: `:is(main, article) p`, `.content p`, `#content p`
- Author: `:is(main, article) .author`, `.byline`, `[rel="author"]`
- Date: `time[datetime]`, `.date`, `.published`, `.timestamp`
- Links in lists: `ul li a`, `ol li a`, `.list-item a`

## When All Fallbacks Fail

If all four strategies return null for a field:
1. Mark the field as missing in the extraction result (set to `null`).
2. Add the field name to `missing_fields` in the feedback payload.
3. If the field was `required: true`, include a note like:
   `"Required field '{name}' not found via CSS, XPath, text search, or a11y tree."`

If the warm-path evaluation loop is active, the model will attempt to
re-derive the selector from the live DOM before marking the field as null.
If re-derivation also fails, mark the field as null, add to
`missing_fields`, and note if it was `required: true`.

## Selector Stability Ranking

When authoring recipes (Phase 2), prefer selectors in this stability order:

1. **`data-testid` attributes** — Explicitly placed for testing; rarely change.
2. **`id` attributes** — Unique per page; stable unless redesigned.
3. **`aria-label` / `role` attributes** — Semantic; survive CSS refactors.
4. **Semantic tag + class** (e.g., `h1.article-title`) — Moderate stability.
5. **Positional selectors** (`:nth-child`, `> :first-child`) — Fragile; avoid.
