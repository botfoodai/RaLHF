#!/usr/bin/env python3
"""PostToolUse hook: marks that RaLHF context tools were used in this session.

Cross-platform replacement for the previous bash version. Uses
tempfile.gettempdir() so it works on Windows (%TEMP%) as well as Unix (/tmp).

Hook input on stdin is JSON with at least `session_id`. On success creates
an empty marker file at <tempdir>/ralhf-hooks/<session_id>.context_used.
The Stop hook reads this marker to decide whether to gate session exit on
save_context_feedback being called.
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
os.makedirs(hook_dir, exist_ok=True)
marker = os.path.join(hook_dir, f"{session_id}.context_used")
# touch — create the file if it doesn't exist; do nothing if it does
open(marker, "a", encoding="utf-8").close()
sys.exit(0)
