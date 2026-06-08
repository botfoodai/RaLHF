# Extraction File Templates

## View file template

```markdown
---
name: extract-{sanitized-domain}-{view-id}
description: >
  Extract structured data from {domain}{path}. Content type: {content_type}.
view_id: {view-id}
strategy: {api_direct|api_intercept|embedded_json|export_download|dom_css|dom_xpath}
context: >
  {2-4 sentence structural description per references/context-fingerprint.md.
   Layout, structure, volume, interactivity. No selectors/classes/IDs.}
---

# Extract from {domain} — {view label}

Authored by ralhf-extract on {date}.

## What this extracts

{One sentence: page contents and fields pulled.}

Content type: `{content_type}`
Strategy: `{strategy}`

## Fields

| Field | Type | Source | Required | Description | Example |
|---|---|---|---|---|---|
{One row per field with real example.}
{Source column: dom → CSS selector, api/json → JSONPath, export → column name}

## Data source

{dom_css: actual DOM hierarchy with field annotations}
{api_direct: endpoint, method, response_path, sample response}
{api_intercept: URL pattern, trigger, response_path, sample response}
{embedded_json: source type, selector, json_path, sample blob}
{export_download: trigger selector, action, format, sample content}

## Example output

\```json
[{"...":"first"},{"...":"second"}]
\```

## Container & pagination

{list/feed/table: container selector + item selector}
{paginated: type, selector/url_pattern, max_pages}

## Incremental extraction

{Chronological data:}
- Time field: `{field_name}` ({sort_order})
- ID field: `{field_name}` (or "none — hash dedup")
- Date format: `{format}`

{Not chronological or single-record: "Not applicable — full extraction each run."}

## Extraction JS

\```javascript
{Complete runnable JS. Varies by strategy.}
\```

## CLI fallback

{dom_css: curl + parse. embedded_json: grep + parse.
 api_direct: curl endpoint. export/intercept: suggest Playwright.}

## Notes

{Domain quirks, discovery findings, strategy rationale}
```

## Service-level SKILL.md template

```markdown
---
name: extract-{sanitized-domain}
description: >
  Service-level extraction skill for {domain}.
---

# {domain} — Extraction Service

## Authentication

{Requirements or "No authentication required."}

## SPA / rendering

{Server-rendered or SPA?}

## Base URL

`{base_url}`

## Navigation notes

{Cookie dismiss or "None."}
```

## Manifest template

```json
{
  "domain": "{bare-domain}",
  "aliases": ["{original hostname if different}"],
  "requires_auth": false,
  "base_url": "https://{hostname}",
  "views": [{
    "id": "{view-id}",
    "label": "{desc}",
    "url_patterns": ["{pattern}"],
    "files": ["views/{view-id}.md"],
    "strategy": "{strategy}",
    "authored_at": "{YYYY-MM-DD}",
    "cli_supported": true
  }]
}
```

Root path: `["/"]`. Parameterized: `:id`.
`cli_supported`: true if CLI worked, false if browser needed.
`strategy` optional — defaults to `dom_css` when absent.
`"file"` (string) → treat as `"files": [file]`.

## Variant naming

Variants: `{view-id}--v{N}.md` (N starts at 2). Original keeps name.
