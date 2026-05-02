#!/usr/bin/env bash
set -euo pipefail

# open-llm-wiki setup
#
# Safe defaults:
# - creates a new local wiki vault
# - installs skills into Claude Code's user skill directory by default
# - never edits an existing wiki file unless OPEN_LLM_WIKI_FORCE=1 is set
#
# Usage:
#   bash setup.sh [wiki-dir]
#   OPEN_LLM_WIKI_SKILL_DIR="$HOME/.claude/skills" bash setup.sh my-llm-wiki

REPO_URL="${OPEN_LLM_WIKI_REPO_URL:-https://github.com/AIwork4me/open-llm-wiki.git}"
WIKI_DIR="${1:-${OPEN_LLM_WIKI_DIR:-my-llm-wiki}}"
SKILL_DIR="${OPEN_LLM_WIKI_SKILL_DIR:-${HOME}/.claude/skills}"
FORCE="${OPEN_LLM_WIKI_FORCE:-0}"

need_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

need_command git
need_command mktemp

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Missing required command: python3 or python" >&2
  exit 1
fi

TMPDIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

echo "Setting up open-llm-wiki"
echo "Wiki directory: $WIKI_DIR"
echo "Skill directory: $SKILL_DIR"

git clone --depth 1 "$REPO_URL" "$TMPDIR/open-llm-wiki" >/dev/null

"$PYTHON_BIN" "$TMPDIR/open-llm-wiki/scripts/wiki_init.py" "$WIKI_DIR" \
  --repo-root "$TMPDIR/open-llm-wiki" \
  --skill-dir "$SKILL_DIR" \
  --install-skills \
  $(if [ "$FORCE" = "1" ]; then printf '%s' "--force"; fi)

echo ""
echo "Done."
echo "- Wiki created at: $WIKI_DIR"
echo "- Skills installed to: $SKILL_DIR"
echo "- Runtime scripts copied to: $WIKI_DIR/.open-llm-wiki/scripts"
echo ""
echo "Next:"
echo "1. Inspect the installed skills if this is your first run."
echo "2. Drop a PDF into $WIKI_DIR/raw/"
echo "3. Ask Claude Code: Ingest this paper: $WIKI_DIR/raw/<paper>.pdf"
