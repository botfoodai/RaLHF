#!/usr/bin/env bash
#
# build-plugin.sh — package the RaLHF plugin into a distributable zip.
#
# Reads name + version from .claude-plugin/plugin.json, stages a clean copy
# of the plugin (excluding repo cruft like .git, .claude/, dist/, etc.),
# and produces dist/<name>-<version>.zip.
#
# Usage:
#   ./build-plugin.sh
#
# The resulting zip extracts to a single top-level directory named after
# the plugin, so recipients get a clean folder no matter where they unzip.

set -euo pipefail

# --- locate ourselves ---------------------------------------------------------
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$ROOT/.claude-plugin/plugin.json"
DIST="$ROOT/dist"

# --- sanity checks ------------------------------------------------------------
if [[ ! -f "$MANIFEST" ]]; then
  echo "error: $MANIFEST not found — are you running this from the plugin root?" >&2
  exit 1
fi

for tool in zip rsync python3; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "error: '$tool' is required but not on PATH" >&2
    exit 1
  fi
done

# --- read name + version from manifest ---------------------------------------
read -r PLUGIN_NAME VERSION < <(python3 -c "
import json, sys
with open('$MANIFEST') as f:
    m = json.load(f)
n = m.get('name')
v = m.get('version')
if not n or not v:
    print('error: plugin.json missing name or version field', file=sys.stderr)
    sys.exit(1)
print(n, v)
")

ZIP_NAME="${PLUGIN_NAME}-${VERSION}.zip"
ZIP_PATH="$DIST/$ZIP_NAME"

# --- verify required files are present ---------------------------------------
REQUIRED=(
  ".claude-plugin/plugin.json"
  ".codex-plugin/plugin.json"
  ".mcp.json"
  "hooks/codex-hooks.json"
  "skills/ralhf-start/SKILL.md"
  "hooks/hooks.json"
  "LICENSE"
  "NOTICE"
  "README.md"
)
missing=0
for f in "${REQUIRED[@]}"; do
  if [[ ! -f "$ROOT/$f" ]]; then
    echo "error: required file missing: $f" >&2
    missing=1
  fi
done
if [[ $missing -ne 0 ]]; then
  exit 1
fi

# --- validate skill metadata --------------------------------------------------
python3 "$ROOT/scripts/validate_skill_frontmatter.py"

# --- prepare output dir -------------------------------------------------------
mkdir -p "$DIST"
rm -f "$ZIP_PATH"

# --- stage a clean copy in a temp dir ----------------------------------------
STAGING=$(mktemp -d -t ralhf-build.XXXXXX)
trap 'rm -rf "$STAGING"' EXIT
TARGET="$STAGING/$PLUGIN_NAME"

# rsync respects trailing slashes: copy contents of $ROOT into $TARGET
rsync -a \
  --exclude='.git/' \
  --exclude='.gitignore' \
  --exclude='.DS_Store' \
  --exclude='.claude/' \
  --exclude='.codex/' \
  --exclude='dist/' \
  --exclude='build/' \
  --exclude='*.zip' \
  --exclude='build-plugin.sh' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='*.swp' \
  --exclude='.idea/' \
  --exclude='.vscode/' \
  --exclude='node_modules/' \
  "$ROOT/" "$TARGET/"

# --- build the zip ------------------------------------------------------------
# Run zip from the staging dir so paths inside the archive are relative
# to the plugin folder (i.e. "ralhf/.claude-plugin/plugin.json" not
# "/private/tmp/.../ralhf/.claude-plugin/plugin.json").
( cd "$STAGING" && zip -rqy "$ZIP_PATH" "$PLUGIN_NAME" )

# --- report -------------------------------------------------------------------
SIZE=$(du -h "$ZIP_PATH" | awk '{print $1}')
FILE_COUNT=$(unzip -l "$ZIP_PATH" | tail -1 | awk '{print $2}')

echo ""
echo "Built: $ZIP_PATH"
echo "  version: $VERSION"
echo "  size:    $SIZE"
echo "  files:   $FILE_COUNT"
echo ""
echo "To install:"
echo "  1.  unzip $ZIP_NAME"
echo "  2.  In Claude Code: /plugin install ./$PLUGIN_NAME"
echo "  3.  In Codex: install through botfoodai/ralhf-codex-marketplace"
echo ""
