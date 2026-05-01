#!/usr/bin/env bash
set -euo pipefail

# open-llm-wiki: One-line setup
# Usage: curl -sSL https://raw.githubusercontent.com/AIwork4me/open-llm-wiki/main/setup.sh | bash

REPO_URL="https://github.com/AIwork4me/open-llm-wiki.git"
WIKI_DIR="${1:-my-llm-wiki}"
SKILL_DIR="${HOME}/.openclaw-autoclaw/skills"

echo "🧠 Setting up open-llm-wiki..."
echo ""

# 1. Clone repo to temp
TMPDIR=$(mktemp -d)
git clone --depth 1 "$REPO_URL" "$TMPDIR/open-llm-wiki" 2>/dev/null

# 2. Create wiki structure
mkdir -p "$WIKI_DIR"/{raw,sources,concepts,drafts,qa-reports,templates,_state,log-archive}

# 3. Copy schema and templates
cp "$TMPDIR/open-llm-wiki/SCHEMA.md" "$WIKI_DIR/"
cp "$TMPDIR/open-llm-wiki/templates/"* "$WIKI_DIR/templates/"

# 4. Initialize state files
cat > "$WIKI_DIR/_state/id-counter.md" << 'EOF'
# ID Counter
next: 1
EOF

cat > "$WIKI_DIR/index.md" << 'EOF'
# LLM Wiki Index

## Sources
| ID | Title | Tags |
|----|-------|------|

## Concepts
| Concept | Key Question | Sources |
|---------|-------------|---------|
EOF

cat > "$WIKI_DIR/log.md" << 'EOF'
# Wiki Log
EOF

cat > "$WIKI_DIR/README.md" << EOF
# My LLM Wiki

Personal knowledge base powered by [open-llm-wiki](https://github.com/AIwork4me/open-llm-wiki).

## Structure
- \`raw/\` — Original papers (PDFs)
- \`sources/\` — Paper understanding pages (stable)
- \`concepts/\` — Evolving concept pages
- \`drafts/\` — Pre-QA drafts
- \`qa-reports/\` — QA audit records
- \`templates/\` — Page templates

## Usage
Drop a PDF into \`raw/\` and tell your agent: "Ingest this paper"
EOF

# 5. Install skills (if OpenClaw skills dir exists)
if [ -d "$SKILL_DIR" ]; then
    cp -r "$TMPDIR/open-llm-wiki/skills/"* "$SKILL_DIR/"
    echo "✅ Skills installed to $SKILL_DIR"
else
    echo "⚠️  OpenClaw skills dir not found at $SKILL_DIR"
    echo "   Skills are in: $TMPDIR/open-llm-wiki/skills/"
    echo "   Copy manually to your agent's skills directory"
fi

# 6. Cleanup
rm -rf "$TMPDIR"

echo ""
echo "✅ Done! Your wiki is ready at: $WIKI_DIR/"
echo ""
echo "Next steps:"
echo "  1. Drop a PDF into $WIKI_DIR/raw/"
echo "  2. Tell your agent: 'Ingest this paper: $WIKI_DIR/raw/your-paper.pdf'"
echo "  3. Open $WIKI_DIR/ in Obsidian to browse your wiki"
echo ""
echo "📖 Read the full guide: https://github.com/AIwork4me/open-llm-wiki/blob/main/QUICKSTART.md"
