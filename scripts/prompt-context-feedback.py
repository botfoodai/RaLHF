#!/usr/bin/env python3
"""Stop hook: blocks session exit once to collect context feedback.

Guard logic:
  1. stop_hook_active=True  -> allow (re-entry guard, prevents infinite loop)
  2. No context tools used  -> allow (nothing to report)
  3. Feedback already saved  -> allow (Phase 5 did its job)
  4. Otherwise              -> block once, ask Claude to call save_context_feedback
"""
import json
import os
import sys
import tempfile

try:
    hook_input = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    sys.exit(0)

session_id = hook_input.get("session_id", "")
stop_hook_active = hook_input.get("stop_hook_active", False)

# Re-entry guard
if stop_hook_active:
    sys.exit(0)

# Cross-platform temp dir matches what track-context-tool.py and
# track-feedback-saved.py write to.
hook_dir = os.path.join(tempfile.gettempdir(), "ralhf-hooks")

# No context tools used this session
if not os.path.exists(os.path.join(hook_dir, f"{session_id}.context_used")):
    sys.exit(0)

# Feedback already saved (by Phase 5 or a prior block)
if os.path.exists(os.path.join(hook_dir, f"{session_id}.feedback_saved")):
    sys.exit(0)

# Block and ask Claude to save feedback
output = {
    "decision": "block",
    "reason": (
        "You used RaLHF context tools in this session but haven't saved "
        "context feedback yet. Call save_context_feedback now with:\n"
        "- successful_strategies: which browse/search approaches found useful results\n"
        "- unsuccessful_strategies: which returned irrelevant or empty results\n"
        "- missing_context: what you needed but couldn't find\n"
        "- irrelevant_context: what was returned but not useful\n"
        "- overall_usefulness: 'high', 'medium', or 'low'\n"
        "- notes: any observations about this user's library topology\n"
        "- phase_grades (optional): {phase_0..phase_4: A|B|C|D|F|N/A}\n"
        "- source_counters (optional): {wiki, cowork_local, claude_memory, "
        "user_provided, external, prior_session: int}\n"
        "- trigger_signals (optional): [{signal: ..., implies: ...}, ...]"
    ),
}
print(json.dumps(output))
sys.exit(0)
