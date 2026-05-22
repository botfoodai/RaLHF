#!/usr/bin/env python3
"""PostToolUse hook: marks that save_context_feedback succeeded in this session.

Cross-platform replacement for the previous bash version. Marker is read by
the Stop hook (prompt-context-feedback.py) to allow session exit without
re-prompting for feedback.
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

hook_dir = os.path.join(tempfile.gettempdir(), "memoire-hooks")
os.makedirs(hook_dir, exist_ok=True)
marker = os.path.join(hook_dir, f"{session_id}.feedback_saved")
open(marker, "a", encoding="utf-8").close()
sys.exit(0)
