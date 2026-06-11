#!/usr/bin/env python3
"""Validate YAML frontmatter in skill markdown files."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def skill_files_from_args(argv: list[str]) -> list[Path]:
    if argv:
        return [Path(arg) for arg in argv if Path(arg).name == "SKILL.md"]
    return sorted(ROOT.glob("skills/*/SKILL.md"))


def extract_frontmatter(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening frontmatter delimiter")

    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            return "\n".join(lines[1:index]) + "\n"

    raise ValueError("missing closing frontmatter delimiter")


def validate_yaml(frontmatter: str) -> tuple[bool, str]:
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        yaml = None

    if yaml is not None:
        try:
            yaml.safe_load(frontmatter)
            return True, ""
        except Exception as exc:  # pragma: no cover - depends on optional PyYAML
            return False, str(exc)

    ruby = shutil.which("ruby")
    if ruby is None:
        return False, "install PyYAML or Ruby to validate YAML frontmatter"

    proc = subprocess.run(
        [
            ruby,
            "-ryaml",
            "-e",
            "YAML.safe_load(STDIN.read, permitted_classes: [], aliases: false)",
        ],
        input=frontmatter,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode == 0:
        return True, ""
    return False, (proc.stderr or proc.stdout).strip()


def main(argv: list[str]) -> int:
    failures: list[str] = []

    for path in skill_files_from_args(argv):
        try:
            frontmatter = extract_frontmatter(path)
            ok, error = validate_yaml(frontmatter)
            if not ok:
                failures.append(f"{path}: invalid YAML frontmatter\n{error}")
        except Exception as exc:
            failures.append(f"{path}: {exc}")

    if failures:
        print("\n\n".join(failures), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
