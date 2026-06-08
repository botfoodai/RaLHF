# Sync Queue

Persists incomplete backend operations to disk so the next session can
replay them without re-extracting.

## Files

- `skills/ralhf-extract/.sync-stack.json` — array of pending operations
- `skills/ralhf-extract/.sync-payloads/{timestamp}-{op}.json` — curl bodies

Both are gitignored. Empty array = all syncs complete.

## Entry format

```json
{
  "id": "1716400000-ingest",
  "op": "ingest",
  "domain": "netflix.com",
  "view_id": "viewingactivity",
  "url": "https://www.netflix.com/viewingactivity",
  "payload_file": "skills/ralhf-extract/.sync-payloads/1716400000-ingest.json",
  "pushed_at": "2026-05-22T14:05:00Z",
  "recipe_id": "uuid-or-null"
}
```

`id` = `{epoch}-{op}`. Unique per entry. All lookups use `id`, not position.

## Push/remove protocol

Before each backend call in Phase 3b:

1. `mkdir -p skills/ralhf-extract/.sync-payloads`
2. Generate `id` = `{epoch}-{op}` (e.g. `1716400000-ingest`)
3. Write the full curl JSON body to `.sync-payloads/{id}.json`
4. Read `.sync-stack.json` (or `[]` if missing)
5. Append the new entry, write back
6. Execute the curl call
7. **On success (200)**: find entry by `id`, splice it out, write back, delete payload file
8. **On failure**: classify error (see below), act accordingly

Multiple tasks can run concurrently. Each removes its own entry by `id` —
order of completion doesn't matter.

## Error classification

| Status | Class | Action |
|--------|-------|--------|
| 200 | success | Remove entry by `id`, delete payload file |
| 400 + `fields` in body | bad_payload | Fix fields format, retry once. Remove on success. |
| 400 (other) | permanent | Remove entry (unfixable). Log warning. |
| 401 / 403 | auth_expired | Remove ALL entries. Warn user once. Switch to local-only. |
| 429 | rate_limited | Leave in queue. Next session retries. |
| 500 / 502 / 503 | transient | Leave in queue. Next session retries. |
| Timeout / connection error | transient | Leave in queue. Next session retries. |

## Replay (Phase 0)

At the start of every extraction, before manifest lookup:

1. Read `.sync-stack.json`. Missing or empty → skip.
2. Sort entries by `pushed_at` (oldest first).
3. **Dedup check** — before replaying any entry, probe existing endpoints to
   detect work that completed in a previous session (crash after success,
   before queue pop):
   a. Group entries by URL.
   b. For each URL group, call `cache/lookup` with `{url, schema_hash}`
      (schema_hash from the entry's payload). Cache is the last operation in
      the dependency chain — if it exists, everything before it succeeded.
      **Found → discard all entries for this URL** (remove + delete payloads).
   c. For remaining entries where `op == "recipe"`, call `recipe/lookup` with
      `{domain, view_id}`. If found AND response `schema_hash` matches the
      entry's schema_hash → **skip the recipe entry only** (remove + delete
      payload). Leave ingest/feedback/cache entries for replay.
   d. Entries that survive both checks → replay normally (step 4).
4. For each surviving entry:
   a. Check `pushed_at`. Older than 24 hours → discard (remove entry + delete payload).
   b. Read payload from `payload_file`.
   c. Execute the curl call with auth headers from `.env` / `config.json`.
   d. On success → remove entry by `id`, delete payload.
   e. On failure → classify. Auth expired → clear all entries, warn, stop replay.
      Transient → leave for next session. Permanent → discard.
5. Proceed to normal Phase 0 logic.

**Dedup limitations**: No ingest lookup endpoint exists. If a crash happened
after ingest but before cache, replay will re-ingest (wiki regenerates without
corruption). Duplicate feedback may slightly skew quality scores. Both are
acceptable tradeoffs — backend-side idempotency keys would fix these but
require schema changes.

## Dependency order

Phase 3b pushes in order: recipe → ingest → feedback → cache.
Replay sorts by `pushed_at` (oldest first), which preserves the dependency
chain: recipe completes before ingest, ingest before feedback/cache.

If a `recipe` entry succeeds during replay and returns a new `recipe_id`,
update the `recipe_id` field in any remaining entries with the same
`domain` + `view_id` before replaying them.

## Disconnect operation

Handles failed backend disconnects from `/ralhf-schedule remove`. When
a `DELETE /source-connection` call fails with a transient error, the
operation is queued here for retry.

### Entry format

```json
{
  "id": "1716400000-disconnect",
  "op": "disconnect",
  "domain": "netflix.com",
  "view_id": null,
  "url": null,
  "payload_file": "skills/ralhf-extract/.sync-payloads/1716400000-disconnect.json",
  "pushed_at": "2026-05-22T14:05:00Z",
  "recipe_id": null
}
```

Payload file contents:
```json
{
  "source_name": "NETFLIX"
}
```

### Replay routing

Disconnect ops use a different HTTP method and endpoint than the standard
`/v1/domain/app_extract/` POST calls:

```bash
curl -s -X DELETE "{backend_url}/source-connection" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {RALHF_MCP_TOKEN}" \
  -d '{"source_name": "{PROVIDER}"}'
```

- **404** is treated as success (source already disconnected).
- **No dedup check needed** — `DELETE` is idempotent. Re-deleting an
  already-disconnected source is harmless.
- **No dependency on other operations** — disconnect ops are independent
  of the recipe → ingest → feedback → cache chain. They can replay in
  any order relative to other ops.

### Error classification

Same as the main error classification table, with one addition:
- **404** → success (remove entry, delete payload). The source-connection
  was already removed.

## Valid `op` values

| `op` | Endpoint | Method | Notes |
|------|----------|--------|-------|
| `recipe` | `/v1/domain/app_extract/recipe` | POST | — |
| `ingest` | `/v1/domain/app_extract/ingest` | POST | — |
| `feedback` | `/v1/domain/app_extract/feedback` | POST | — |
| `cache` | `/v1/domain/app_extract/cache` | POST | — |
| `disconnect` | `/source-connection` | DELETE | 404 = success |

## Replay step 4c routing

When replaying entries in step 4c, check the `op` field to determine
the HTTP method and endpoint:

- If `op` is `"disconnect"`: use `DELETE {backend_url}/source-connection`
  with the payload as the request body. Treat 404 as success.
- All other ops: use `POST {backend_url}/v1/domain/app_extract/{op}`
  with the payload as the request body.
