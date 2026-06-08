# Recipe Schema

A recipe is a JSON object that describes how to extract structured data from
a specific domain. Recipes are stored in `extraction_recipe.recipe_json` on
the backend.

## Top-Level Schema

```json
{
  "view_id": "optional — identifies which view file this recipe corresponds to",
  "strategy": "api_direct | api_intercept | embedded_json | export_download | dom_css | dom_xpath",
  "content_type": "article | listing | product | profile | table | feed",
  "fields": [
    {
      "name": "title",
      "type": "text | link | image | number | date | list | html",
      "selector": "h1.article-title",
      "selector_type": "css",
      "json_path": "$.data.items[*].title",
      "required": true,
      "description": "The main title of the article"
    }
  ],
  "pagination": {
    "type": "next_link | url_pattern | infinite_scroll | offset_limit | cursor | token | scroll_trigger | none",
    "selector": "a.next-page",
    "url_pattern": "/page/{n}",
    "max_pages": 10
  },
  "list_container": {
    "selector": "div.results-list",
    "item_selector": "div.result-item",
    "description": "Container and item selectors for list/feed content types"
  },
  "api": { "...": "see API Object below" },
  "intercept": { "...": "see Intercept Object below" },
  "embedded_json": { "...": "see Embedded JSON Object below" },
  "export": { "...": "see Export Object below" },
  "incremental": {
    "time_field": "<name of a field from fields[]>",
    "sort_order": "desc",
    "id_field": "<name of a field from fields[], optional>",
    "date_format": "auto"
  },
  "ttl_seconds": 86400,
  "notes": "Optional free-text notes about quirks of this domain"
}
```

## Strategy

| Property | Type | Required | Description |
|---|---|---|---|
| `strategy` | enum | no | One of: `api_direct`, `api_intercept`, `embedded_json`, `export_download`, `dom_css`, `dom_xpath`. Default: `dom_css`. |

The strategy field declares which extraction method this recipe uses.
Existing recipes without a `strategy` field default to `dom_css` for
backward compatibility. The strategy determines which recipe sub-object
is required and how fields are sourced.

| Strategy | Required sub-object | Field source |
|---|---|---|
| `api_direct` | `api` | `json_path` on each field |
| `api_intercept` | `intercept` | `json_path` on each field |
| `embedded_json` | `embedded_json` | `json_path` on each field |
| `export_download` | `export` | `source_key` on each field |
| `dom_css` | none (uses `selector`) | `selector` on each field |
| `dom_xpath` | none (uses `selector`) | `selector` on each field |

## View ID

| Property | Type | Required | Description |
|---|---|---|---|
| `view_id` | string | no | Identifies which view file this recipe corresponds to. Matches the view's `id` in the domain manifest. |

When present, `view_id` ties the recipe to a specific `views/{view_id}.md`
file in the domain's skill directory. Non-breaking — recipes without this
field remain valid.

## Context Fingerprint

| Property | Type | Stored in | Description |
|---|---|---|---|
| `context` | string | View file YAML front matter | A 2–4 sentence natural-language description of the page's structural characteristics. |

The `context` field is **not** part of the recipe JSON. It lives in the view
file's YAML front matter alongside `name`, `description`, and `view_id`.

Purpose: variant disambiguation. When multiple view files exist for the same
URL pattern (premium vs. free, A/B test variants, geo-specific layouts), the
context fingerprint lets the warm path determine which view file matches the
page the user is currently seeing.

See `references/context-fingerprint.md` for generation rules, comparison
semantics, and the decision flow.

## Field Object

| Property | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Machine-friendly field name (snake_case). |
| `type` | enum | yes | One of: `text`, `link`, `image`, `number`, `date`, `list`, `html`. |
| `selector` | string | conditional | CSS selector or XPath expression. Required for `dom_css`/`dom_xpath` strategies. |
| `selector_type` | enum | no | `css` (default) or `xpath`. |
| `json_path` | string | conditional | JSONPath expression to extract the field from API/JSON data. Required for `api_direct`, `api_intercept`, `embedded_json` strategies. |
| `source_key` | string | conditional | Column name or index for export strategies (e.g., CSV column name, Excel column header). Required for `export_download` strategy. |
| `required` | bool | no | If true, a null/empty result triggers feedback. Default: false. |
| `description` | string | no | Human-readable description of what this field captures. |
| `attribute` | string | no | Which attribute to extract (DOM strategies only). Defaults: `textContent` for text, `href` for link, `src` for image. |
| `transform` | string | no | Post-extraction transform: `trim`, `strip_html`, `parse_number`, `parse_date`. |

### Field Types

- **text** — `element.textContent.trim()`. Plain text.
- **link** — `element.href` or `element.querySelector('a')?.href`.
- **image** — `element.src` or `element.querySelector('img')?.src`.
- **number** — `parseFloat(element.textContent.replace(/[^0-9.-]/g, ''))`.
- **date** — `element.getAttribute('datetime')` or `element.textContent` parsed via `Date.parse`.
- **list** — `Array.from(elements).map(el => el.textContent.trim())`. Returns array of strings.
- **html** — `element.innerHTML`. Raw HTML content (use sparingly, for rich text fields).

## API Object

Present when `strategy` is `api_direct`. Describes a direct API endpoint
that returns the target data as structured JSON.

| Property | Type | Required | Description |
|---|---|---|---|
| `endpoint` | string | yes | Full URL or path of the API endpoint. |
| `method` | string | yes | HTTP method: `GET` or `POST`. |
| `headers` | object | no | Additional headers required (e.g., auth tokens, content-type). |
| `body_template` | string | no | JSON body template for POST requests. Use `{variable}` placeholders. |
| `response_path` | string | yes | JSONPath to the data array or object in the response (e.g., `$.data.items`). |
| `pagination` | enum | no | Pagination style: `offset_limit`, `cursor`, `token`, `none`. Default: `none`. |

```json
{
  "endpoint": "https://api.example.com/v1/items",
  "method": "GET",
  "headers": { "Accept": "application/json" },
  "response_path": "$.data.items",
  "pagination": "offset_limit"
}
```

## Intercept Object

Present when `strategy` is `api_intercept`. Describes an API call that must
be triggered by a page interaction (scroll, click, page load).

| Property | Type | Required | Description |
|---|---|---|---|
| `url_pattern` | string | yes | URL pattern to match intercepted requests (glob or regex). |
| `trigger` | enum | yes | What triggers the API call: `scroll`, `click`, `page_load`. |
| `trigger_selector` | string | conditional | CSS selector for the element to click/scroll to. Required if trigger is `scroll` or `click`. |
| `response_path` | string | yes | JSONPath to the data in the intercepted response. |
| `dedup_key` | string | no | Field name to deduplicate across multiple intercepted responses (e.g., `id`). |
| `stop_condition` | string | no | When to stop triggering: `empty_response`, `max_items:{n}`, `no_new_items`. |

```json
{
  "url_pattern": "**/api/v1/feed*",
  "trigger": "scroll",
  "trigger_selector": "[data-testid='feed-container']",
  "response_path": "$.data.items",
  "dedup_key": "id",
  "stop_condition": "empty_response"
}
```

## Embedded JSON Object

Present when `strategy` is `embedded_json`. Describes a server-rendered
data blob embedded in the page's HTML.

| Property | Type | Required | Description |
|---|---|---|---|
| `source` | string | yes | The data source identifier: `__NEXT_DATA__`, `__NUXT__`, `__INITIAL_STATE__`, `__REDUX_STATE__`, `__APOLLO_STATE__`, `data-injector-instances`, `ld+json`, or a custom `script#id`. |
| `selector` | string | no | CSS selector for the script/element containing the blob (e.g., `script#__NEXT_DATA__`). Used when `source` alone is ambiguous. |
| `json_path` | string | yes | JSONPath from the blob root to the target data (e.g., `$.props.pageProps.listings`). |
| `recursive_search` | bool | no | If true, search nested objects for matching keys when `json_path` doesn't resolve. Default: false. |

```json
{
  "source": "__NEXT_DATA__",
  "selector": "script#__NEXT_DATA__",
  "json_path": "$.props.pageProps.searchResults.items",
  "recursive_search": false
}
```

## Export Object

Present when `strategy` is `export_download`. Describes a site-provided
export feature (CSV, JSON, XLSX download).

| Property | Type | Required | Description |
|---|---|---|---|
| `trigger_selector` | string | yes | CSS selector for the download/export button or link. |
| `trigger_action` | enum | yes | How to activate: `click`, `submit`, `navigate`. |
| `format` | enum | yes | Expected file format: `csv`, `json`, `xlsx`. |
| `interception_method` | string | no | How to capture the download: `blob_url`, `download_event`, `network_response`. |
| `parse_config` | object | no | Format-specific parsing options. |

`parse_config` for CSV:

| Property | Type | Description |
|---|---|---|
| `delimiter` | string | Column delimiter. Default: `,`. |
| `has_header` | bool | Whether the first row is a header. Default: true. |
| `encoding` | string | File encoding. Default: `utf-8`. |

```json
{
  "trigger_selector": "a:has-text('Download all')",
  "trigger_action": "click",
  "format": "csv",
  "interception_method": "blob_url",
  "parse_config": { "delimiter": ",", "has_header": true }
}
```

## Incremental Object

Optional. For chronologically-ordered lists (history, feed, transactions).
Enables watermark-based delta extraction on scheduled runs.

| Property | Type | Required | Description |
|---|---|---|---|
| `time_field` | string | yes | Field from `fields[]` with chronological values. |
| `sort_order` | enum | no | `desc` (default) or `asc`. |
| `id_field` | string | no | Field from `fields[]` for dedup at watermark boundary. Absent → hash-based dedup. |
| `date_format` | string | no | `auto` (default), `iso8601`, `us`, `epoch_s`, `epoch_ms`, or strftime string. |

Set during Phase 2 if data is a chronological list. Omit for unordered or single-record data.

## Pagination Object

| Property | Type | Required | Description |
|---|---|---|---|
| `type` | enum | yes | `next_link`, `url_pattern`, `infinite_scroll`, or `none`. |
| `selector` | string | conditional | CSS selector for the next-page link. Required if type = `next_link`. |
| `url_pattern` | string | conditional | URL template with `{n}` placeholder. Required if type = `url_pattern`. |
| `scroll_trigger` | string | no | Selector for the element to scroll into view (infinite scroll). |
| `max_pages` | int | no | Safety cap. Default: 10. |

## List Container Object

Only present when `content_type` is `listing`, `feed`, or `table`.

| Property | Type | Required | Description |
|---|---|---|---|
| `selector` | string | yes | Selector for the container element holding all items. |
| `item_selector` | string | yes | Selector for each individual item within the container. |
| `description` | string | no | What each item represents. |

When `list_container` is present, the `fields` array describes fields
**within each item**, not on the page as a whole. The extraction engine runs
the field selectors relative to each matched item element.

## Schema Hash

The `schema_hash` is a SHA-256 hex digest of the sorted field names:

```
sha256(JSON.stringify(fields.map(f => f.name).sort()))
```

This is used to detect when a recipe's field structure changes (triggering
cache invalidation for URLs extracted under the old schema).

## TTL Guidelines

| Content type | Suggested TTL | Reason |
|---|---|---|
| News feed, dashboard | 300s (5 min) | Content changes frequently |
| Search results | 3600s (1 hour) | Moderately dynamic |
| Product page, profile | 86400s (1 day) | Changes infrequently |
| Documentation, reference | 604800s (1 week) | Rarely changes |
| Static/archival page | 2592000s (30 days) | Essentially permanent |

## Validation Rules

Before saving a recipe, validate:

1. `content_type` is a valid enum value.
2. `fields` is non-empty (at least one field).
3. Every field has `name` and `type`.
4. Field names are unique.
5. If `content_type` is `listing`/`feed`/`table`, `list_container` must be present (DOM strategies) or `response_path` must return an array (API strategies).
6. If `pagination.type` is not `none`, the corresponding required fields are set.
7. `ttl_seconds` is a positive integer.
8. If `strategy` is `api_direct`, the `api` object must be present with `endpoint`, `method`, and `response_path`.
9. If `strategy` is `api_intercept`, the `intercept` object must be present with `url_pattern`, `trigger`, and `response_path`.
10. If `strategy` is `embedded_json`, the `embedded_json` object must be present with `source` and `json_path`.
11. If `strategy` is `export_download`, the `export` object must be present with `trigger_selector`, `trigger_action`, and `format`.
12. For `dom_css`/`dom_xpath` strategies (or absent `strategy`), every field must have `selector`.
13. For `api_direct`/`api_intercept`/`embedded_json` strategies, every field must have `json_path`.
14. For `export_download` strategy, every field must have `source_key`.
15. If `incremental` is present, `incremental.time_field` must reference an existing field name in `fields[]`. If `id_field` is present, it must also reference an existing field name.
