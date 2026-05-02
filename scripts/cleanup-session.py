#!/usr/bin/env python3
"""SessionEnd hook: cleans up temp marker files for this session.

Cross-platform replacement for the previous bash version. Removes the
context_used and feedback_saved markers from <tempdir>/ralhf-hooks/ so
the session's tracking state doesn't persist beyond exit.
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
if not session_id:
    sys.exit(0)

hook_dir = os.path.join(tempfile.gettempdir(), "ralhf-hooks")
for suffix in ("context_used", "feedback_saved"):
    marker = os.path.join(hook_dir, f"{session_id}.{suffix}")
    try:
        os.remove(marker)
    except FileNotFoundError:
        pass
sys.exit(0)
