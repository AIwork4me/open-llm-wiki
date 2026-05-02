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

copy_new_file() {
  local src="$1"
  local dst="$2"
  if [ -e "$dst" ] && [ "$FORCE" != "1" ]; then
    echo "Keeping existing file: $dst"
    return 0
  fi
  cp "$src" "$dst"
}

write_new_file() {
  local dst="$1"
  if [ -e "$dst" ] && [ "$FORCE" != "1" ]; then
    echo "Keeping existing file: $dst"
    return 0
  fi
  cat > "$dst"
}

need_command git
need_command cp
need_command mkdir
need_command mktemp

TMPDIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

echo "Setting up open-llm-wiki"
echo "Wiki directory: $WIKI_DIR"
echo "Skill directory: $SKILL_DIR"

git clone --depth 1 "$REPO_URL" "$TMPDIR/open-llm-wiki" >/dev/null

mkdir -p "$WIKI_DIR"/{raw,sources,concepts,drafts,qa-reports,templates,_state,log-archive}
mkdir -p "$SKILL_DIR"

copy_new_file "$TMPDIR/open-llm-wiki/SCHEMA.md" "$WIKI_DIR/SCHEMA.md"
cp "$TMPDIR/open-llm-wiki/templates/"* "$WIKI_DIR/templates/"

write_new_file "$WIKI_DIR/_state/id-counter.md" <<'EOF'
# ID Counter
next: 1
EOF

write_new_file "$WIKI_DIR/index.md" <<'EOF'
# LLM Wiki Index

## Sources
| ID | Title | Tags |
| --- | --- | --- |

## Concepts
| Concept | Key Question | Sources |
| --- | --- | --- |
EOF

write_new_file "$WIKI_DIR/log.md" <<'EOF'
# Wiki Log
EOF

write_new_file "$WIKI_DIR/README.md" <<'EOF'
# My LLM Wiki

Personal research wiki powered by open-llm-wiki.

## Structure

- `raw/`: original source files
- `drafts/`: pre-QA source drafts
- `sources/`: stable source pages
- `concepts/`: evolving concept pages
- `qa-reports/`: append-only QA and contradiction reports
- `templates/`: page templates

## First Use

Drop a paper into `raw/`, then ask your agent:

`Ingest this paper: raw/<paper>.pdf`
EOF

cp -R "$TMPDIR/open-llm-wiki/skills/"* "$SKILL_DIR/"

echo ""
echo "Done."
echo "- Wiki created at: $WIKI_DIR"
echo "- Skills installed to: $SKILL_DIR"
echo ""
echo "Next:"
echo "1. Inspect the installed skills if this is your first run."
echo "2. Drop a PDF into $WIKI_DIR/raw/"
echo "3. Ask Claude Code: Ingest this paper: $WIKI_DIR/raw/<paper>.pdf"
