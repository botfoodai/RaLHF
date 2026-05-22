# Connector Pattern Table — Tool-Name Identification Lookup

Companion reference to SKILL.md Phase 1 step 4 ("Inventory the actual MCP tool surface"). When you enumerate MCP tools in this session and need to identify which server is which, use this lookup. **It's a lookup aid, not a default list to mention.** The authoritative source for what to mention in Turn 2a / Turn 2b is the session's actual tool surface — NOT this table.

MCP tool names have the form `mcp__<server-id>__<tool>` (the server-id is often a UUID, so rely on the tool-name half plus the cluster of related tools to identify the server).

## The table

| Category | Tool-name patterns that identify the server |
|---|---|
| Email — Gmail | `search_threads`, `get_thread`, `create_draft`, `list_labels`, `create_label` |
| Email — Outlook/other | `list_messages`, `send_mail`, `get_message` |
| Calendar — Google Cal | `list_events`, `create_event`, `suggest_time`, `respond_to_event` |
| Drive — Google Drive | `search_files`, `read_file_content`, `list_recent_files`, `get_file_metadata`, `download_file_content` |
| Docs — Notion | `search_pages`, `create_page`, `get_page`, `update_block` |
| PM — Jira/Atlassian | `searchJiraIssuesUsingJql`, `getJiraIssue`, `createJiraIssue`, `getVisibleJiraProjects` |
| PM — Linear | `list_issues`, `create_issue`, `list_teams` |
| Confluence | `searchConfluenceUsingCql`, `createConfluencePage`, `getConfluencePage` |
| Accounting — QuickBooks | `profit-loss-generator`, `cash-flow-generator`, `company-info`, `benchmarking-*` |
| Payments — Stripe | `explain-error`, `test-cards`, `stripe-best-practices` |
| CRM — Common Room | `account-research`, `prospect`, `compose-outreach`, `call-prep` |
| Chat — Slack | `list_channels`, `post_message`, `search_messages` |
| Code — GitHub | `get_repo`, `list_prs`, `get_issue` |
| Scheduling — Calendly-like | `suggest_time`, `create_booking` |
| Browser | `navigate`, `get_page_text`, `preview_click`, `preview_screenshot` |
| Files/Sheets — Office | `xlsx`, `docx`, `pptx` (skills that manipulate these) |
| RaLHF itself | `get_wiki_catalog`, `browse_wiki`, `batch_fetch`, `remember`, `save_context_feedback` — **NOT a connector to mention**, these are your own tools |

If you see tool patterns not in this table, categorize them by function (e.g. *"a CRM-like server"* / *"a time-tracking server"*) and include them in your inventory under a generic category.

## Rules for using this table

- **Only connectors you VERIFY are present** can be mentioned in Turn 2a or Turn 2b. Never guess. Never say *"I could check Gmail if you have it connected"* — that's a probe. Either it's in the tool surface or you don't mention it.
- If an obviously relevant connector is NOT present, you may note it in Turn 2b as a one-line *"if you connect Notion next time, I could…"* soft suggestion — but this is one-shot, never a probe to be repeated.
- Ignore RaLHF's own tools (`get_wiki_catalog`, `browse_wiki`, etc.) when building the inventory. Those are core tools, not connectors to propose.
- The table is a lookup aid for **identifying** unknown server-ids. The authoritative list is **this session's actual tool surface**.

## Connector category → task shape mapping

When deciding whether to mention a connector in Turn 2b, map task shape to category first, THEN match category to a verified-present server in the inventory:

| Task shape | Helpful category | Why |
|---|---|---|
| Writing *to* a named person (letter, email, DM) | Email-or-messaging | Prior threads with that person |
| Writing *about* a past event (recap, follow-up, thank-you) | Email + Calendar | Confirm what happened and when |
| Continuing a series (newsletter, weekly update, sprint recap) | Docs/Drive + Email | Prior drafts + prior sends |
| Anything referencing a date, booking, confirmation | Email + Calendar | Source of truth for bookings |
| Coding / PR / spec / ticket work | PM/issue tracker + Docs/Drive + Code-host | Task detail + prior discussion + code state |
| **Investor / fundraising / pitch deck / one-pager** | **Accounting + Email + Drive + Calendar** | Live financials (cash, burn, runway) + recent investor threads + prior pitch materials + recent investor meetings. ALL FOUR are usually relevant — narrow to top 2 by what's freshest, but enumerate all four when planning the ask. |
| Financial / accounting / budgeting (internal use) | Accounting + Email | Invoices, reports, correspondence |
| CRM / sales / customer-facing | CRM + Email + Calendar | Account history + correspondence + meetings |
| Research / web-based lookup | Browser | Live web access |
| Personal task with no external artifact (meal, workout, home errand) | Usually none | Mode C minimum 2c — *"anything else?"* |

Walk the two steps:
1. **Match the task shape** to a category from the right column.
2. **Match the category to a verified-present server** in this session's MCP inventory. If the category has a match, mention that specific server in Turn 2b. If it doesn't, drop the connector mention or use the "if you connect X next time" soft suggestion (one-shot only).

**Enumerate before narrowing.** For task shapes that map to multiple connector categories (investor / fundraising, CRM / sales, coding work), **first list ALL plausibly-relevant connector categories** that are verified-present in this session. Then narrow to the top 2 for the mode A ask. Skipping the enumeration step is how the model misses obvious connectors — e.g., picking QuickBooks + Gmail for an investor one-pager but forgetting Drive (which holds the actual prior pitch decks). The enumeration step is the safety net against partial pattern-matching.

**Cap connector mentions at 2 across all of Turn 2b** even if more are present. Top two that most directly fill gaps or add depth. **But:** if 3+ are clearly relevant (named failure mode: investor one-pager with QB + Gmail + Drive all relevant), prefer mode B (open-ended check listing all relevant connectors) over mode A (pick 2, miss 1). Mode B's open-ended ask is the right shape when 3+ are plausibly important.
