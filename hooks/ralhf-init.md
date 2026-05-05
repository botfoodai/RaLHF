RaLHF (prep-context skill) is active for this session.

On EVERY user task — not just the first — you MUST invoke the `ralhf:prep-context` skill before any other action.

The skill (RaLHF) introduces itself, searches the user's RaLHF wiki, inventories connected sources from the session's MCP tool surface, and guides the user through a five-phase flow: Load → Discover → Propose → Confirm → Execute → Remember.

Do NOT ask clarifying questions before invoking the skill.
Do NOT call other tools first.
Do NOT try to gather requirements yourself — that is the skill's job.

Note: AskUserQuestion is BANNED while this plugin is active. The structured-popup UX encouraged Claude to ask clarifying questions before the skill fired, defeating the whole point. RaLHF handles all clarification inside its Phase 2 staged check-ins (plain text). On Mac and Linux this is enforced by a PreToolUse hook; on Windows without bash/cat the ban is enforced by skill-level rules in CLAUDE.md and SKILL.md.

Your ONLY first action on any task is: invoke the `ralhf:prep-context` skill.
