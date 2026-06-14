#!/usr/bin/env python3
"""Validate that a private mirror is safe to release publicly.

This script is intentionally conservative. It validates JSON files, blocks common
secret patterns, and enforces production MCP/public-source expectations where
applicable. It is used by both CI and the manual release-to-public workflow.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

TEXT_EXTS = {
    ".md", ".json", ".yml", ".yaml", ".toml", ".txt", ".py", ".sh",
    ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".mjs", ".cjs",
}

SKIP_DIRS = {".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"}

SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
]

FORBIDDEN_PUBLIC_STRINGS = [
    "backend.ralfh-dev.com",
    "ralfh-dev.com",
    "Dev canonical.",
    "dev variant points at",
]

EXPECTED_PROD_MCP = "https://backend.ralhf.ai/mcp"

# Infra files that legitimately contain the forbidden dev strings and are
# excluded from the public mirror, so they must not trip the forbidden scan.
FORBIDDEN_SCAN_SKIP = {
    "scripts/validate_public_release.py",
    "scripts/make_variant.py",
}

# Path prefixes excluded from the public mirror (see sync_to_public.sh /
# check_public_sync.sh). Content here never reaches public, so the forbidden
# dev-string scan must not flag it — e.g. internal docs that describe the
# dev/prod model and necessarily name the dev endpoint.
FORBIDDEN_SCAN_SKIP_PREFIXES = ("docs/internal/",)


def iter_files(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        yield path


def read_text(path: Path) -> str | None:
    if path.suffix not in TEXT_EXTS and path.name not in {"CLAUDE.md", "AGENTS.md", "README"}:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def validate_json(root: Path, errors: list[str]) -> None:
    for path in iter_files(root):
        if path.suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"Invalid JSON: {path.relative_to(root)}: {exc}")


def scan_public_safety(root: Path, errors: list[str]) -> None:
    for path in iter_files(root):
        text = read_text(path)
        if text is None:
            continue
        rel = path.relative_to(root)
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"Possible secret pattern in {rel}")
        # These infra files legitimately contain the forbidden literals (the
        # validator detects them; the dev-variant generator rewrites them). They
        # are excluded from the public mirror, so scanning them would only
        # produce false positives.
        rel_posix = rel.as_posix()
        skip_forbidden = rel_posix in FORBIDDEN_SCAN_SKIP or any(
            rel_posix.startswith(prefix) for prefix in FORBIDDEN_SCAN_SKIP_PREFIXES
        )
        if not skip_forbidden:
            for needle in FORBIDDEN_PUBLIC_STRINGS:
                if needle in text:
                    errors.append(f"Forbidden public string {needle!r} in {rel}")


def validate_ralhf_plugin(root: Path, errors: list[str]) -> None:
    claude_manifest = root / ".claude-plugin" / "plugin.json"
    codex_manifest = root / ".codex-plugin" / "plugin.json"
    mcp_config = root / ".mcp.json"
    if not claude_manifest.exists():
        return

    for required in [claude_manifest, codex_manifest, mcp_config, root / "skills", root / "hooks"]:
        if not required.exists():
            errors.append(f"Missing required plugin path: {required.relative_to(root)}")

    try:
        mcp_text = mcp_config.read_text(encoding="utf-8")
        if EXPECTED_PROD_MCP not in mcp_text:
            errors.append(f".mcp.json must point to production MCP {EXPECTED_PROD_MCP}")
    except Exception as exc:
        errors.append(f"Unable to read .mcp.json: {exc}")

    try:
        claude = json.loads(claude_manifest.read_text(encoding="utf-8"))
        version = claude.get("version")
        if not version:
            errors.append("Claude plugin manifest missing version")
        readme = root / "README.md"
        if readme.exists() and version and f"version-{version}" not in readme.read_text(encoding="utf-8"):
            errors.append(f"README version badge must match Claude manifest version {version}")
    except Exception as exc:
        errors.append(f"Unable to validate Claude plugin manifest: {exc}")


def validate_marketplace(root: Path, errors: list[str]) -> None:
    claude_market = root / ".claude-plugin" / "marketplace.json"
    codex_market = root / ".agents" / "plugins" / "marketplace.json"
    if claude_market.exists():
        data = json.loads(claude_market.read_text(encoding="utf-8"))
        text = json.dumps(data)
        if "botfoodai/RaLHF" not in text and "./plugins/ralhf" not in text:
            errors.append("Claude marketplace does not reference expected RaLHF plugin source")
    if codex_market.exists():
        data = json.loads(codex_market.read_text(encoding="utf-8"))
        text = json.dumps(data)
        if "botfoodai/RaLHF" not in text:
            errors.append("Codex marketplace does not reference expected public RaLHF plugin source")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors: list[str] = []

    validate_json(root, errors)
    scan_public_safety(root, errors)
    validate_ralhf_plugin(root, errors)
    validate_marketplace(root, errors)

    if errors:
        print("Public release validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Public release validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
