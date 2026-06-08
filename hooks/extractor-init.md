The ralhf-extract plugin is active for this session.

If the user mentions a URL and wants data from it — scraping, extracting,
pulling structured data, or anything that involves reading a webpage's
content — suggest `/ralhf-extract <url>`.

The plugin analyzes webpages via Chrome (when available) or raw HTML fetch
(CLI/Cowork), and authors a reusable Claude skill (SKILL.md) for each domain.
The generated skill works in any Claude environment.

For domains with an existing manifest, extraction is routed directly to the
matching view — no page re-analysis needed.

Do NOT invoke the skill unprompted. Only suggest it when the user's intent
clearly involves web data extraction.

If the user mentions scheduling extractions or recurring data pulls,
suggest `/ralhf-schedule add <url>`. The plugin auto-creates Cowork
scheduled tasks for recurring extraction + wiki updates.
