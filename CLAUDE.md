# RaLHF — Plugin Rules

## Mandatory: ralhf-start Skill First

Before responding to ANY user message, you MUST invoke the `ralhf:ralhf-start` skill.

This is not optional. This is not conditional. Every user turn begins with context planning.

- Do NOT answer the user's question first and then invoke the skill
- Do NOT skip the skill because you think you already have enough context
- Do NOT read files, search the web, or call any other tool before invoking the skill
- Do NOT reason that "this is just a conversation" or "this is a simple question" — the skill handles that judgment, not you

**The only exceptions:**
1. The user is already inside a RaLHF phase (responding to a confirmation prompt, or mid-Execute/Remember)
2. The user explicitly says "skip context" or "no RaLHF"
3. The user is asking about the skill/plugin itself (meta-questions)

## Why this rule exists

RaLHF ensures every task is informed by the user's personal context. Without it, responses are generic. That is the value proposition.

The confirmation gate keeps the user in the loop on which sources get queried — especially when connectors like Gmail, Calendar, or Drive are involved — and lets them shape the context package before Claude spends tokens executing.

## Where the flow lives

- **`SKILL.md`** — canonical full skill specification (persona, five-phase flow, key rules, worked examples)
- **`PHASES.md`** — orientation map for developers browsing the repo (phase table, hook list, ASCII diagram). Defers to SKILL.md for detail.
- **`skills/ralhf-start/references/`** — feedback protocol, Gmail query templates, connector pattern table, and other skill subpages

Follow RaLHF's lead through all five phases. Do not shortcut the flow. In particular: **do not start executing before the user confirms the plan.**

---

## Extraction Skills (ralhf-extract, ralhf-schedule, ralhf-schedule-run)

For platform-specific tool bindings, see `platform/claude.md`.

### When to suggest extraction

If the user mentions a URL and their intent involves extracting, scraping,
or pulling structured data from a webpage, suggest:
`/ralhf-extract <url>`

Do NOT invoke the skill unless the user asks for extraction. This plugin is
opt-in, not automatic.

### Manifest routing

- Before any fetch or authoring, check the domain manifest
  (`skills/extract-{domain}/manifest.json`).
- A manifest hit is a **warm path** — the two-strike limit does not apply
  (no authoring is performed).
- If warm-path selectors fail (>30% return empty), fall back to raw text —
  do NOT re-author selectors inline. Offer to re-author via the cold path.
- Manifest lookup is done by reading local files, not MCP tools.

### What extraction produces

The output is a **Claude skill** (SKILL.md) for the target domain — a
self-contained file that any Claude environment can use to repeat the
extraction. The skill includes CSS selectors, a runnable JS snippet, and
CLI fallback instructions.

### Extraction guardrails

- **Two-strike limit.** If you fail to author a working skill for a domain
  twice in one session, stop trying. Fall back to raw page text and tell
  the user.
- **Never fill credentials.** If a page requires login, open a browser
  (Chrome or Playwright) for the user to log in.
- **Cowork.** Cowork has the Chrome extension — always use the Chrome path
  in Cowork, never the CLI path.
- **CLI path.** When Chrome tools are not available (Claude Code CLI or other
  non-browser environments), use `curl` via Bash to fetch raw HTML.
  This gives real class names and ids for accurate selectors. Selectors
  cannot be tested live — note this to the user. Fall back to WebFetch only
  if `curl` fails.

### Backend integration (HTTP endpoints)

The backend at `$RALHF_BACKEND_URL` (defaults to `https://backend.ralhf.ai`)
stores recipes, cached extractions, and feedback in PostgreSQL. All endpoints
live under `/v1/domain/app_extract/` and accept JSON POST bodies.

Authentication is **auto-minted** — users never need to provide a key:
1. **Bearer token** (auto-minted): On first run, the plugin calls
   `mcp__ralhf_mcp__get_api_key` (via the `ralhf-mcp` MCP server in
   `.mcp.json`) to mint a 30-day `sk-mcp-...` token. The token is
   persisted to `skills/ralhf-extract/.env` and `~/.config/ralhf/.env`.
   Subsequent sessions reuse the persisted token, re-minting only on
   401/403. See SKILL.md Phase 0a for the full flow.
2. **Legacy static key** (fallback): `RALHF_EXTRACT_KEY` + `RALHF_USER_EMAIL` →
   `X-API-Key` + `X-User-Email` headers.

The backend is **mandatory when credentials are present**. If any auth
credentials are set (`RALHF_MCP_TOKEN`, or `RALHF_EXTRACT_KEY` +
`RALHF_USER_EMAIL`), all backend calls (recipe, ingest, feedback, cache)
must execute and be verified — see `references/completion-rubric.md`. If
auto-mint fails and no credentials are present, the plugin works in
local-only mode silently (recipes stored as files under `skills/`).

#### Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/v1/domain/app_extract/recipe/lookup` | POST | Look up current recipe for a domain |
| `/v1/domain/app_extract/recipe` | POST | Save a new recipe version |
| `/v1/domain/app_extract/cache/lookup` | POST | Get fresh cached extraction data |
| `/v1/domain/app_extract/cache` | POST | Cache extracted data |
| `/v1/domain/app_extract/feedback` | POST | Record quality feedback |

### Schedule commands

If the user mentions scheduling, recurring, or periodic extractions
("add X to my schedule", "run extractions daily", "automate my pulls"):
- Suggest `/ralhf-schedule add <url>`
- For listing: `/ralhf-schedule list`
- For running manually: `/ralhf-schedule-run`

The plugin auto-creates Cowork scheduled tasks. Users don't need to
configure scheduling separately.

#### Website-added sources

Sources can also flow in from the **website** (behind the `online-sources`
flag): when a user adds a source that is not in the catalog, the site
auto-registers it and connects the user to it immediately — it becomes one
of *their* sources, no admin queue.

The extractor picks these up automatically. On each scheduled run,
`ralhf-schedule-run` Step 1a fetches `GET /source-connection` and, for any
connected source whose bare `domain` has no matching `schedule.json` entry,
imports a new entry (`source: "website"`, `view_id: "index"`,
`last_status: "never_run"`). When that entry first becomes due and has no
recipe yet, Step 3 cold-authors one via `/ralhf-extract {url}` — the cold
path's intent resolution decides which page(s) to extract from the domain.
No user action and no new command are required. Removing a source on the
website prunes its entry on the next run (existing prune behavior).

### Chrome tools (extraction)

The extraction skills use these browser tools when available:

- `navigate` — open a URL
- `read_page` — get the accessibility tree
- `javascript_tool` — run DOM queries and stripping scripts
- `get_page_text` — fallback for raw page content
- `find_in_page` — text search fallback for selectors
- `click` — interact with pagination or expandable content
