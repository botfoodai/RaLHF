#!/usr/bin/env python3
"""Cross-platform replacement for `cat <file>` in hooks.json command invocations.

Why this exists:
  Previous hooks.json used shell `cat ${CLAUDE_PLUGIN_ROOT}/hooks/<name>.md` to
  emit hook content into Claude's context. `cat` works in Unix shells (bash,
  zsh, sh) and in Git Bash / WSL on Windows, but is NOT present in the default
  Windows command runner that Claude Desktop uses. Hooks would silently fail
  to emit content there. This Python replacement works identically across
  platforms as long as Python 3 is on PATH.

Diagnostic logging:
  Every hook invocation writes a timestamped line to
  <tempdir>/ralhf-hook-log.txt so the user can verify hooks are actually
  firing. After a test session, run:
      cat $TMPDIR/ralhf-hook-log.txt    (Unix)
      type %TEMP%\\ralhf-hook-log.txt   (Windows)
  An empty/missing log file means hooks didn't fire at all (Desktop runtime
  doesn't honor command-type hooks). A populated log means hooks fire — any
  remaining issues are about output format or matchers, not whether hooks
  run.

Usage in hooks.json:
  "command": "python ${CLAUDE_PLUGIN_ROOT}/scripts/print-hook.py ${CLAUDE_PLUGIN_ROOT}/hooks/<name>.md"
"""
import datetime
import os
import sys
import tempfile

LOG_PATH = os.path.join(tempfile.gettempdir(), "ralhf-hook-log.txt")


def _log(msg: str) -> None:
    """Append a diagnostic line to the hook log. Best-effort; never raises."""
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            ts = datetime.datetime.now().isoformat(timespec="seconds")
            f.write(f"{ts}  print-hook.py  {msg}\n")
    except OSError:
        pass


def main() -> int:
    if len(sys.argv) != 2:
        _log(f"ERROR usage: argv={sys.argv}")
        sys.exit("Usage: print-hook.py <path-to-file>")
    target = sys.argv[1]
    _log(f"fire  file={os.path.basename(target)}")
    try:
        with open(target, encoding="utf-8") as f:
            sys.stdout.write(f.read())
    except OSError as exc:
        _log(f"ERROR open: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
