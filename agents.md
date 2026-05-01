# AGENTS.md â€?Contributor Guide for AI Agents and Humans

> Read this file before contributing. It defines the rules, structure, and workflow for this project.

---

## Before making any changes

1. **Search existing issues** at https://github.com/AIwork4me/open-llm-wiki/issues
2. **If no issue exists, create one** â€?describe what you want to add/fix and why
3. **Comment on the issue** stating your approach
4. **Branch from `main`**: `git checkout -b feat/short-description main`

---

## Repo Map

```
open-llm-wiki/
â”œâ”€â”€ README.md              â†?Start here. What this project is.
â”œâ”€â”€ README.zh.md           â†?Chinese version
â”œâ”€â”€ AGENTS.md              â†?This file. Rules and structure.
â”œâ”€â”€ SHOWCASE.md            â†?Real output from 23 papers. Proof it works.
â”œâ”€â”€ PHILOSOPHY.md          â†?Design philosophy. Why these decisions.
â”œâ”€â”€ EXAMPLES.md            â†?Anti-patterns. What we learned the hard way.
â”œâ”€â”€ QUICKSTART.md          â†?5-minute setup guide.
â”œâ”€â”€ AGENTS_SNIPPET.md      â†?Copy-paste config for your AGENTS.md.
â”œâ”€â”€ SCHEMA.md              â†?Wiki data structure and conventions.
â”œâ”€â”€ LICENSE                â†?MIT
â”?
â”œâ”€â”€ skills/                â†?OpenClaw Skills (the core product)
â”?  â”œâ”€â”€ wiki-ingest/       â†?  Paper â†?source page pipeline (10 steps)
â”?  â”œâ”€â”€ query-writeback/   â†?  Query â†?wiki growth pipeline (6 steps)
â”?  â””â”€â”€ wiki-lint/         â†?  Periodic health check (5 dimensions)
â”?
â”œâ”€â”€ templates/             â†?Page templates for wiki content
â”?  â”œâ”€â”€ source-template.md â†?  One paper's understanding page
â”?  â””â”€â”€ concept-template.mdâ†?  One concept's accumulation page
â”?
â””â”€â”€ examples/
    â”œâ”€â”€ deepseek-v3-sample.md  â†?Real source page example
    â””â”€â”€ minimal-vault/         â†?Complete minimal wiki you can run
        â”œâ”€â”€ index.md           â†?  Navigation hub
        â”œâ”€â”€ log.md             â†?  Operation audit trail
        â”œâ”€â”€ _state/            â†?  ID counter
        â”œâ”€â”€ sources/           â†?  Stable paper pages
        â”œâ”€â”€ concepts/          â†?  Evolving concept pages
        â”œâ”€â”€ drafts/            â†?  Pre-QA drafts
        â”œâ”€â”€ raw/               â†?  Original files (empty in example)
        â”œâ”€â”€ qa-reports/        â†?  QA audit records (empty in example)
        â””â”€â”€ log-archive/       â†?  Archived logs (empty in example)
```

### What goes where

| Want to... | Edit this | Don't touch |
|-----------|-----------|-------------|
| Fix a Skill pipeline | `skills/*/SKILL.md` | Other skills |
| Add a new anti-pattern | `EXAMPLES.md` | SCHEMA.md |
| Update setup instructions | `QUICKSTART.md` | PHILOSOPHY.md |
| Change data conventions | `SCHEMA.md` | Individual skills |
| Add a page template | `templates/` | examples/ |
| Update the example vault | `examples/minimal-vault/` | templates/ |

---

## Architecture

### Three pipelines, one system

```
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”?
                    â”?        open-llm-wiki            â”?
                    â”?                                â”?
  Paper (PDF) â”€â”€â”€â”€â”€â–¶â”‚  wiki-ingest                    â”?
                    â”?   parse â†?draft â†?QA â†?publish â”?
                    â”?        â†?                      â”?
  User query â”€â”€â”€â”€â”€â”€â–¶â”‚  query-writeback                â”?
                    â”?   search â†?answer â†?writeback   â”?
                    â”?        â†?                      â”?
  Cron / manual â”€â”€â–¶â”‚  wiki-lint                      â”?
                    â”?   format + QA + cross-refs      â”?
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”?
```

### Data flow

```
raw/paper.pdf
    â†?parse (PyMuPDF or PaddleOCR)
raw/paper_fulltext.txt
    â†?draft (AI writes understanding)
drafts/LLM-NNNN.md (status: draft)
    â†?independent QA sub-agent (â‰?.0)
sources/LLM-NNNN.md (status: stable)
    â†?update 3-5 concept pages
concepts/*.md
    â†?contradiction check (independent sub-agent)
qa-reports/LLM-NNNN-contradiction.md
    â†?query triggers synthesis
concepts/*.md (updated via writeback)
```

### Key constraint: independent QA

**LLMs cannot self-evaluate.** This is the project's core insight.

- `wiki-ingest` Step 5: **Independent sub-agent** runs QA (separate context, separate session)
- `wiki-ingest` Step 9: **Independent sub-agent** runs contradiction check
- The writing agent can self-check (Step 4), but self-check â‰?QA

Any change that weakens the independence of QA or contradiction detection is a regression.

---

## Hard Rules

Violating any of these will cause a PR to be rejected:

- **QA is always independent** â€?never self-evaluate, never use the same session that wrote the content
- **QA score â‰?7.0 required** â€?no exceptions, no "it looks fine to me"
- **Contradictions are marked, never silently overwritten** â€?use `âš ï¸ [CONTRADICTION YYYY-MM-DD]`
- **One paper at a time** â€?serial ingestion for stability and error isolation
- **Hard numbers in every source page** â€?"competitive results" is not acceptable
- **Tables over Figures** â€?when extracting data, always verify against Table text
- **QA reports are append-only** â€?never modify an existing QA report
- **No new dependencies without an issue** â€?keep the framework lightweight
- **No API keys required for basic use** â€?PyMuPDF (local) works out of the box; PaddleOCR is optional

---

## Adding a new Skill

Skills live in `skills/<name>/SKILL.md`. To add a new one:

### Minimal structure

```
skills/my-skill/
â””â”€â”€ SKILL.md    â†?Required. Frontmatter + pipeline definition.
```

### SKILL.md frontmatter

```yaml
---
name: my-skill
description: One-line description of what this skill does.
version: 0.1.0
---
```

### Skill design rules

1. **Pipeline-based** â€?define clear steps with inputs and outputs
2. **State success criteria** â€?each step must have a verifiable check
3. **Reference SCHEMA.md** â€?don't duplicate data conventions in the skill
4. **Independent evaluation where needed** â€?any quality gate must use a separate sub-agent
5. **Document lessons learned** â€?add anti-patterns to EXAMPLES.md, not inline

### Testing a Skill

Before submitting a PR:

1. Install the skill: `cp -r skills/my-skill ~/.openclaw-autoclaw/skills/`
2. Run it against a real paper in a test wiki
3. Verify the output matches SCHEMA.md conventions
4. Check that QA sub-agent produces a valid report

---

## Fixing a bug in a Skill

1. **Identify the specific step** that fails (reference the pipeline step number)
2. **Reproduce with a real paper** â€?not a hypothetical example
3. **Fix the step** â€?don't refactor the whole pipeline
4. **Add the anti-pattern to EXAMPLES.md** if it's a new failure mode
5. **Test with the same paper** that triggered the bug

---

## Writing Style

### Skills (SKILL.md)
- Technical, precise, pipeline-oriented
- Each step has: input â†?action â†?output â†?verify
- Include task templates for sub-agents

### Documentation (README, QUICKSTART, PHILOSOPHY)
- Conversational but not chatty
- Lead with the insight, not the history
- English as primary, Chinese translation in README.zh.md

### Wiki content (templates, examples)
- Karpathy style: conversational, opinionated, grounded in hard numbers
- 1-2 KB per source page â€?not a paper summary, an understanding note
- Concept pages are alive â€?they grow with every new source

---

## Submitting a PR

```bash
git push -u origin feat/my-feature
gh pr create --base main --fill
```

**Checklist before marking ready for review:**

- [ ] Changes are limited to the files you intended to modify (surgical changes)
- [ ] No new dependencies added without an issue
- [ ] If you changed a Skill, tested it against a real paper
- [ ] If you changed SCHEMA.md, updated all affected Skills
- [ ] Documentation is consistent (English + Chinese README if applicable)
- [ ] No private data, API keys, or personal information in commits

---

## Branch conventions

| Prefix | Use for |
|--------|---------|
| `feat/` | New skill, new feature, new template |
| `fix/` | Bug fix in a skill or documentation |
| `docs/` | Documentation-only changes |
| `refactor/` | Restructure without behavior change |
| `test/` | Add or update test examples |

All PRs target `main`. Squash-merge on approval.

