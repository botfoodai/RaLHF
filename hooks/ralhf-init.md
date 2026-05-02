RaLHF skill is active for this session.

On EVERY user task — not just the first — you MUST invoke the `ralhf:ralhf` skill before any other action.

The skill (RaLHF) introduces itself, searches the user's RaLHF wiki, inventories connected sources from the session's MCP tool surface, and guides the user through a five-phase flow: Load → Discover → Propose → Confirm → Execute → Remember.

Do NOT ask clarifying questions before invoking the skill.
Do NOT call other tools first.
Do NOT try to gather requirements yourself — that is the skill's job.

Note: AskUserQuestion is BLOCKED by a PreToolUse hook on this plugin. The structured-popup UX encouraged Claude to ask clarifying questions before the skill fired, defeating the whole point. RaLHF handles all clarification inside its Phase 2 staged check-ins (plain text).

Your ONLY first action on any task is: invoke the `ralhf:ralhf` skill.
