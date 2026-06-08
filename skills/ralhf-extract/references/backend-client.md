# Backend Client Contract

Single-source-of-truth for the 8 endpoints on the ralhf backend (6
app-extract endpoints + 2 source-connection endpoints).

## Base URL & Auth

Read two files once at start (absolute paths):

- `skills/ralhf-extract/config.json` — backend URL (committed)
- `skills/ralhf-extract/.env` — credentials (gitignored)

```json
// config.json
{ "backend_url": "https://backend.ralhf.ai" }
```

```bash
# .env — two auth modes (bearer preferred, legacy fallback)
RALHF_MCP_TOKEN=sk-mcp-...          # preferred: self-serve bearer token
RALHF_EXTRACT_KEY=<key>             # legacy: static API key
RALHF_USER_EMAIL=<email>            # legacy: required with RALHF_EXTRACT_KEY
```

```
Base: {backend_url}
Prefix: /v1/domain/app_extract
```

### Auth selection (checked in order)

1. **Bearer token** (preferred): if `RALHF_MCP_TOKEN` is set, use:
   ```
   Authorization: Bearer {RALHF_MCP_TOKEN}
   ```
   No `X-User-Email` needed — user identity is resolved from the token.

2. **Legacy static key**: if `RALHF_EXTRACT_KEY` + `RALHF_USER_EMAIL` are set:
   ```
   X-API-Key: {RALHF_EXTRACT_KEY}
   X-User-Email: {RALHF_USER_EMAIL}
   ```

**Error handling**: Either file missing or incomplete → local-only (silent).
First 401/403 → warn user once, switch to local-only for the rest of the
session. All other errors → silent, continue without backend.

## Endpoint: `POST /recipe/lookup`

Look up the current recipe for a domain + view.

**Request**:

```json
{
  "domain": "netflix.com",
  "view_id": "viewingactivity"
}
```

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `domain` | string | yes | — | Bare domain (no `www.`, max 255 chars) |
| `view_id` | string | no | `null` | View identifier (max 128 chars). Omit for domain-wide best match. Response `view_id` reflects the actual view of the matched recipe. |

**Response** (200):

```json
{
  "found": true,
  "recipe_id": "uuid",
  "domain": "netflix.com",
  "view_id": "viewingactivity",
  "version": 3,
  "recipe_json": { "...recipe object..." },
  "schema_hash": "a1b2c3...",
  "score": 0.92,
  "feedback_count": 5
}
```

On miss: `{"found": false}` (still 200).

## Endpoint: `POST /recipe`

Save (upsert) a recipe. If `schema_hash` changed, all cache entries for
the domain are evicted automatically.

**Request**:

```json
{
  "domain": "netflix.com",
  "view_id": "viewingactivity",
  "recipe_json": {
    "strategy": "dom_css",
    "content_type": "listing",
    "fields": [...]
  },
  "schema_hash": "a1b2c3..."
}
```

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `domain` | string | yes | — | Bare domain (max 255 chars) |
| `view_id` | string | no | `"index"` | View identifier (max 128 chars) |
| `recipe_json` | object | yes | — | Full recipe object (max 512 KB) |
| `schema_hash` | string | yes | — | Hex SHA-256 of sorted field names (max 64 chars) |

**Response** (200):

```json
{
  "recipe_id": "uuid",
  "domain": "netflix.com",
  "view_id": "viewingactivity",
  "version": 1,
  "schema_hash": "a1b2c3..."
}
```

`version` starts at 1 and increments on each upsert.

## Endpoint: `POST /cache/lookup`

Get fresh cached extraction data for a URL.

**Request**:

```json
{
  "url": "https://netflix.com/viewingactivity",
  "schema_hash": "a1b2c3..."
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `url` | string | yes | Full URL (max 8192 chars) |
| `schema_hash` | string | yes | Must match the recipe's current schema_hash |

**Response** (200):

```json
{
  "found": true,
  "url": "https://netflix.com/viewingactivity",
  "recipe_id": "uuid",
  "data": { "...extracted data..." },
  "schema_hash": "a1b2c3...",
  "cached_at": "2026-05-15T10:30:00Z"
}
```

On miss (expired, schema mismatch, or not cached): `{"found": false}`.

## Endpoint: `POST /cache`

Cache extracted data for a URL.

**Request**:

```json
{
  "url": "https://netflix.com/viewingactivity",
  "recipe_id": "uuid-from-recipe-save",
  "data": { "items": [...] },
  "schema_hash": "a1b2c3...",
  "ttl_seconds": 86400
}
```

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `url` | string | yes | — | Full URL (max 8192 chars) |
| `recipe_id` | UUID | yes | — | Must reference an existing recipe |
| `data` | object | yes | — | Extracted data payload (max 512 KB) |
| `schema_hash` | string | yes | — | Hex SHA-256 (max 64 chars) |
| `ttl_seconds` | int | no | `86400` | Cache lifetime (min 60, max 2592000) |

**Response** (200):

```json
{
  "cache_id": "uuid",
  "url": "https://netflix.com/viewingactivity",
  "cached_at": "2026-05-15T10:30:00Z"
}
```

Returns 404 if `recipe_id` does not exist.

## Endpoint: `POST /feedback`

Record quality feedback for a recipe extraction. Should not block user
output, but errors must be logged and retried once (see
`references/completion-rubric.md`).

**Request**:

```json
{
  "recipe_id": "uuid",
  "recipe_version": 3,
  "url": "https://netflix.com/viewingactivity",
  "score": 0.85,
  "missing_fields": ["duration", "genre"],
  "extra_fields": ["unexpected_col"],
  "notes": "Date format changed from ISO to US locale"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `recipe_id` | UUID | yes | Recipe this feedback applies to |
| `recipe_version` | int | yes | Version of the recipe at extraction time |
| `url` | string | yes | URL that was extracted |
| `score` | float | yes | Quality score 0.0–1.0 |
| `missing_fields` | string[] | no | Fields that returned empty (max 50, each max 256 chars) |
| `extra_fields` | string[] | no | Unexpected fields found (max 50, each max 256 chars) |
| `notes` | string | no | Free-text notes (max 4096 chars) |

**Response** (200):

```json
{
  "feedback_id": "uuid"
}
```

Returns 404 if `recipe_id` does not exist.

## Endpoint: `POST /ingest`

Route extracted data to the appropriate domain table (media, commerce,
or travel). Should not block user output, but errors must be logged and
retried (see `references/completion-rubric.md`).

> **WARNING — `fields` format**: `fields` MUST be an array of **objects**
> `[{"name":"...","type":"..."}, ...]`, NOT an array of strings. Sending
> bare strings (e.g. `["date","title"]`) causes a **silent 400** — the
> backend rejects the request without a descriptive error. Build from the
> recipe: `recipe_json.fields.map(f => ({name: f.name, type: f.type}))`.

The backend maps the bare domain to a domain type and provider, transforms
extractor field names to the handler schema, and upserts. **The backend
also dispatches a wiki delta task automatically** — the user's wiki is
updated server-side. Do NOT call wiki MCP tools (browse_wiki, remember,
etc.) to store extraction results. Unclassified domains return
`ingested: false` (not an error).

See `references/domain-classification.md` for the full domain → type mapping.

**Request**:

```json
{
  "domain": "netflix.com",
  "view_id": "viewingactivity",
  "url": "https://www.netflix.com/viewingactivity",
  "recipe_id": "uuid-or-null",
  "content_type": "listing",
  "fields": [
    {"name": "date", "type": "date"},
    {"name": "title", "type": "text"}
  ],
  "data": [
    {"date": "2026-05-18", "title": "Stranger Things"},
    {"date": "2026-05-17", "title": "Wednesday"}
  ]
}
```

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `domain` | string | yes | — | Bare domain (max 255 chars) |
| `view_id` | string | no | `"index"` | View identifier (max 128 chars) |
| `url` | string | yes | — | Full source URL (max 8192 chars) |
| `recipe_id` | UUID | no | `null` | Recipe that produced this data |
| `content_type` | string | no | `"listing"` | Content type from recipe |
| `fields` | object[] | no | `[]` | Recipe field descriptors |
| `data` | object[] | yes | — | Extracted rows (max 500, total max 2 MB) |

**Response** (200):

```json
{
  "ingested": true,
  "domain_type": "media",
  "provider": "NETFLIX",
  "total_records": 2,
  "successful_records": 2,
  "failed_records": 0,
  "errors": []
}
```

Unclassified domain: `{"ingested": false, "total_records": 2, ...}`.

## Endpoint: `GET /source-connection`

> **Note:** This endpoint lives at `{backend_url}/source-connection`, NOT
> under the `/v1/domain/app_extract/` prefix.

List all connected data sources for the authenticated user. Used by
`ralhf-schedule-run` for reconciliation (Step 1a).

**Request**:

```bash
curl -s -X GET "{backend_url}/source-connection" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {RALHF_MCP_TOKEN}"
```

No request body. Auth headers follow the same selection logic as other
endpoints (bearer preferred, legacy fallback).

**Response** (200):

```json
{
  "datasources": [
    {
      "source_name": "NETFLIX",
      "domain": "netflix.com",
      "connected_at": "2026-05-15T10:30:00Z",
      "status": "active"
    },
    {
      "source_name": "AMAZON_USA",
      "domain": "amazon.com",
      "connected_at": "2026-05-10T08:00:00Z",
      "status": "active"
    }
  ]
}
```

| Field | Type | Description |
|---|---|---|
| `datasources` | array | List of connected data sources |
| `datasources[].source_name` | string | Provider identifier (e.g., `NETFLIX`) |
| `datasources[].domain` | string | Bare domain associated with this provider |
| `datasources[].connected_at` | string | ISO timestamp of connection creation |
| `datasources[].status` | string | Connection status (`active`, `paused`) |

Empty response (no connections): `{"datasources": []}`.

## Endpoint: `DELETE /source-connection`

> **Note:** This endpoint lives at `{backend_url}/source-connection`, NOT
> under the `/v1/domain/app_extract/` prefix.

Disconnect a data source for the authenticated user. Used by
`ralhf-schedule` remove command (step 4b) and sync-stack replay.

**Request**:

```bash
curl -s -X DELETE "{backend_url}/source-connection" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {RALHF_MCP_TOKEN}" \
  -d '{"source_name": "NETFLIX"}'
```

| Field | Type | Required | Description |
|---|---|---|---|
| `source_name` | string | yes | Provider identifier (e.g., `NETFLIX`, `AMAZON_USA`) |

**Response** (200):

```json
{
  "disconnected": true,
  "source_name": "NETFLIX"
}
```

**404** — source was not connected (already disconnected or never existed):

```json
{
  "disconnected": false,
  "source_name": "NETFLIX",
  "error": "source_connection_not_found"
}
```

Treat 404 as success — the desired end state (disconnected) is achieved.

## schema_hash Computation

The `schema_hash` is a SHA-256 hex digest of the JSON-serialized sorted
field names from the recipe:

```bash
echo -n '["date","title"]' | shasum -a 256 | cut -d' ' -f1
```

Or in JS:

```js
const hash = await crypto.subtle.digest(
  "SHA-256",
  new TextEncoder().encode(JSON.stringify(fields.map(f => f.name).sort()))
);
```

## view_id Semantics

- Defaults to `"index"` for single-view domains.
- For multi-view domains (e.g., Netflix has `viewingactivity` + `profiles`),
  use the view ID from the domain manifest / URL path.
- Max 128 characters, matches the view file name in
  `skills/extract-{domain}/views/{view-id}.md`.
- Recipes are uniquely keyed by `(user_id, domain, view_id)`.

## Curl Template

**Bearer token (preferred):**
```bash
curl -s -X POST "{backend_url}/v1/domain/app_extract/<endpoint>" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {RALHF_MCP_TOKEN}" \
  -d '<json>'
```

**Legacy static key (fallback):**
```bash
curl -s -X POST "{backend_url}/v1/domain/app_extract/<endpoint>" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: {RALHF_EXTRACT_KEY}" \
  -H "X-User-Email: {RALHF_USER_EMAIL}" \
  -d '<json>'
```

### Request Body Guardrails

> **NEVER include user identity fields in request bodies.** Do not add
> `user`, `user_email`, `email`, `RALHF_USER_EMAIL`, or any
> user-identifying field to the JSON body. User identity is derived from
> the `Authorization` header only. Use ONLY the fields documented for
> each endpoint above. The backend rejects undocumented fields.
