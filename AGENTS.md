# AGENTS.md

Contributor guide for humans and AI agents working on open-llm-wiki.

## Project Scope

open-llm-wiki is a Claude Code skill bundle plus a small wiki schema. The core
product is the behavior of the three skills in `skills/`:

- `wiki-ingest`: one-source ingest with independent QA
- `query-writeback`: read-first synthesis with approved writeback
- `wiki-lint`: report-first health checks with optional approved fixes

## Hard Rules

- Keep every `skills/<name>/SKILL.md` folder name aligned with its frontmatter
  `name`.
- Validate skills with `uvx --from skills-ref agentskills validate`.
- Do not add unsupported frontmatter fields. Use `metadata` for versioning.
- Basic use must not require API keys. Cloud OCR is optional and must be
  disclosed because document content may leave the local machine.
- `raw/` files are immutable evidence.
- QA reports and contradiction reports are append-only.
- Query writeback and lint are read-only by default.
- No secrets, private papers, personal notes, or API keys belong in the repo.

## Repo Map

```text
open-llm-wiki/
|-- README.md
|-- README.zh.md
|-- QUICKSTART.md
|-- SCHEMA.md
|-- AGENTS.md
|-- skills/
|   |-- wiki-ingest/
|   |-- query-writeback/
|   `-- wiki-lint/
|-- templates/
|-- examples/
|-- scripts/
|-- .github/workflows/
`-- assets/
```

## Before Submitting Changes

Run:

```bash
uvx --from skills-ref agentskills validate skills/wiki-ingest
uvx --from skills-ref agentskills validate skills/query-writeback
uvx --from skills-ref agentskills validate skills/wiki-lint
python scripts/check_quality.py
bash -n setup.sh
```

## Skill Design Guidance

- Put trigger conditions in the frontmatter `description`.
- Keep `SKILL.md` procedural and concise.
- State file side effects explicitly.
- Prefer report-only behavior before writes.
- List completion criteria so another agent can verify the workflow.

## Documentation Style

- Be specific and verifiable.
- Avoid absolute marketing claims.
- Distinguish tested examples from illustrative examples.
- Keep Claude Code as the default install path.
- Mention other agent runtimes only as optional adaptations.
