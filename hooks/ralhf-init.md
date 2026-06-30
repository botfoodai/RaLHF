RaLHF (the `ralhf` skill) is available this session.

RaLHF is the customer's context engineer: when invoked, it searches their RaLHF wiki, inventories connected sources from the session's MCP tool surface, and guides them through a five-phase flow — Load → Discover → Propose → Confirm → Execute → Remember — assembling the relevant context before the assistant does the work.

RaLHF does NOT auto-fire on ordinary tasks. Invoke the `ralhf` skill when, and only when, the customer explicitly asks for it — for example they type `/ralhf`, say "use ralhf", ask you to "pull my context", or make a similar clear request to bring in their personal/work context before the task. Handle all other tasks normally, without the skill.

When the customer does invoke it, the skill takes over from there — it introduces itself briefly and goes straight to pulling context (there is no "do you want context?" yes/no gate; invoking is the opt-in).
