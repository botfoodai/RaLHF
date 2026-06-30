# Platform Bindings — Claude Code / Cowork

Tool name mappings for the Claude Code CLI and Cowork environments.
SKILL.md files use capability descriptions; this file maps them to
concrete Claude tools.

## Tool Mappings

| Capability | Claude Tool |
|---|---|
| Read file | `Read` tool (absolute paths) |
| Search files by pattern | `Glob` tool |
| Search file contents | `Grep` tool |
| HTTP fallback (no browser) | `WebFetch` tool |
| Run shell commands | `Bash` tool |
| Browser automation | Cowork Chrome extension (see below) |
| Background agent | `Task` subagent (`run_in_background: true`) |
| User prompt / choice | `AskUserQuestion` with `multiSelect` option |
| Scheduled tasks | Cowork scheduled task system |
| Skill invocation syntax | `/skill-name <args>` |

## Browser Tools (Cowork Chrome Extension)

When running in Cowork with the Chrome extension available:

| Action | Tool |
|---|---|
| Open a URL | `navigate` |
| Read accessibility tree | `read_page` |
| Run DOM queries / JS | `javascript_tool` |
| Get raw page text | `get_page_text` |
| Text search on page | `find_in_page` |
| Click elements | `click` |

## Credential Persistence

- Primary: `~/.config/ralhf/.env`
- Secondary: the ralhf-extract **skill install directory**'s `.env` —
  under the plugin install root, NOT the project working directory. May be
  read-only in plugin installs; prefer the primary path. The skill scripts
  (`skills/ralhf-extract/scripts/`) check both automatically.

Both paths are accessible in Claude Code and Cowork.

## MCP Tool Naming

RaLHF MCP tool names are platform-prefixed. The same `get_api_key` tool
appears as `mcp__ralhf_mcp__get_api_key` in Claude Code CLI and
`mcp__claude_ai_ralhf-mcp__get_api_key` in Cowork. When a skill names
an MCP tool, match by the trailing tool name, not the full prefix.

## Scheduling

Cowork scheduled tasks are fully supported. The `ralhf-extractions` task
fires at `tick_interval_hours` and invokes `/ralhf-schedule-run`.
