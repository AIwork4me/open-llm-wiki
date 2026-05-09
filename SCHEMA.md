# open-llm-wiki Schema

This file defines the vault structure and safety rules used by the skills.
Agents should read it before editing a wiki vault.

## Directory Structure

```text
my-llm-wiki/
|-- .open-llm-wiki/ # runtime scripts copied by setup/init
|-- .graph/          # optional derived graph JSON/report/schema
|-- .obsidian/       # optional Obsidian settings when enabled
|-- raw/             # original source files and parsed text
|   `-- inbox/       # optional unprocessed material drop zone
|-- drafts/          # source pages before QA approval
|-- sources/         # stable source pages
|-- concepts/        # evolving concept pages
|-- qa-reports/      # append-only QA and contradiction reports
|-- claims/          # normalized claim graph for semantic QA and growth
|-- canvas/          # optional explanatory diagrams, not evidence
|-- assets/          # optional Obsidian/diagram assets
|-- log-archive/     # archived log entries by month
|-- templates/       # source and concept templates
|   `-- agent-prompts/
|-- _state/          # counters and internal state
|   |-- source-registry.jsonl
|   |-- growth-queue.jsonl
|   `-- science-review-queue.jsonl
|-- _dashboard.md    # optional generated Obsidian status homepage
|-- AGENTS.md        # optional generated agent context for the vault
|-- CLAUDE.md        # optional generated Claude context for the vault
|-- SCHEMA.md
|-- README.md
|-- index.md
`-- log.md
```

## Page Types

| Type | Directory | Purpose |
| --- | --- | --- |
| source | `sources/` | stable understanding page for one source document |
| draft | `drafts/` | source page before QA approval |
| concept | `concepts/` | evolving synthesis across multiple sources |
| claim graph | `claims/` | normalized durable claims extracted from stable source pages |
| raw | `raw/` | immutable evidence and parsed text |

## Parse Artifact Contract

Each `raw/<source>_markdown/` directory is a **parse artifact** — a verifiable,
traceable, reusable output of a parser. The contract defines required files and
fields so downstream tools (ingest, claims, QA, lint) can trust artifact state.

### Required Files

| File | Status | Purpose |
| --- | --- | --- |
| `combined.md` | required | full parsed text, page-separated by `---` |
| `manifest.json` | required | artifact metadata and provenance |
| `chunks.jsonl` | required | structured evidence anchors (line, page, heading) |
| `tables.jsonl` | optional | extracted table structures |
| `figures.jsonl` | optional | figure/metadata entries |
| `assets/` | optional | images, table screenshots, attachments |
| `parse.log` | optional | parser stdout/stderr summary |

### `manifest.json` Fields

Required fields:

| Field | Type | Description |
| --- | --- | --- |
| `source_path` | string | vault-relative path to the original source file |
| `source_sha256` | string | SHA-256 of the source file at parse time |
| `artifact_sha256` | string | SHA-256 of `combined.md` |
| `combined` | string | filename of combined markdown (usually `combined.md`) |
| `parser` | string | parser identifier (`pdf_to_markdown`, `desktop-text-stager`, `manual`) |
| `parser_version` | string | parser version string |
| `created_at` | ISO 8601 | timestamp when the artifact was created |
| `source_mtime` | ISO 8601 | source file modification time at parse time |
| `mime` | string | MIME type of the source (e.g. `application/pdf`) |
| `page_count` | integer | number of pages or top-level sections parsed |
| `anchors` | object | which anchor types are preserved (see below) |
| `limitations` | array of strings | known parse limitations |

`anchors` sub-object fields (all boolean):

| Field | Meaning |
| --- | --- |
| `pages` | page boundaries are preserved |
| `lines` | line numbers are accurate |
| `tables` | tables were extracted (may be flattened) |
| `figures` | figures/images were extracted |
| `equations` | equations were preserved |

Additional fields from previous versions (e.g. `input`, `api_url`, `attempts`,
`documents`, `download_images`, `warnings`) are preserved for backward
compatibility but are not part of the contract.

### `chunks.jsonl` Fields

Each line is a JSON object. Required fields:

| Field | Type | Description |
| --- | --- | --- |
| `chunk_id` | string | unique identifier, typically `<source_uuid>:<index>` |
| `source_uuid` | string | hash-derived UUID for the source file |
| `source_id` | string | wiki source ID (`LLM-NNNN`) or empty string if unassigned |
| `artifact_path` | string | relative path to `combined.md` within the artifact dir |
| `heading_path` | array of strings | heading hierarchy leading to this chunk |
| `page` | integer | page number (0 if unknown) |
| `line_start` | integer | 1-based start line in `combined.md` |
| `line_end` | integer | 1-based end line in `combined.md` |
| `char_start` | integer | 0-based start character offset |
| `char_end` | integer | 0-based end character offset |
| `kind` | string | chunk type: `paragraph`, `table`, `figure_caption`, `equation`, `code` |
| `text_hash` | string | SHA-256 hash of chunk text (truncated) |
| `token_count` | integer | estimated token count |

### Artifact Status

Downstream tools classify each artifact as:

| Status | Meaning |
| --- | --- |
| `complete` | manifest has all required fields, hashes are valid |
| `stale` | manifest is complete but `source_sha256` no longer matches the source file |
| `legacy` | manifest is missing or incomplete; treated as degraded |

### Legacy Compatibility

Artifacts created before this contract may have a partial `manifest.json` or none
at all. Downstream tools handle these cases:

- `wiki_lint.py` reports legacy artifacts as **P2** (advisory, not blocking).
- `wiki_ingest_corpus.py` marks legacy items with `artifact_status: legacy` and
  records limitations in the source page.
- `wiki_claims.py` annotates claims from legacy artifacts with
  `evidence_status: legacy`.
- `wiki_semantic_qa.py` emits a **P2** finding for evidence pointing to a legacy
  artifact.

Legacy artifacts are never treated as complete or trustworthy. They remain usable
for read-only evidence but should be re-parsed when possible.

### Desktop-Readable Fields

The following manifest fields are designed for desktop/UI consumption:

- `parser` and `parser_version`: show which parser produced this artifact.
- `anchors`: coverage indicator for pages, lines, tables, figures, equations.
- `limitations`: human-readable list of what was not extracted.
- `page_count`: quick quality indicator.
- `created_at` and `source_mtime`: freshness comparison.

## Source Frontmatter

```yaml
---
id: LLM-NNNN
title: "Paper Title"
status: draft|stable
created: YYYY-MM-DD
updated: YYYY-MM-DD
source: "Authors, title, venue or arXiv ID, year"
tags: [tag1, tag2]
---
```

Rules:

- `id` must match the filename.
- `status: stable` is allowed only after independent QA passes.
- `created` is the source publication date when known.
- `updated` is the last wiki edit date.
- every source page needs hard numbers or an explicit note that the source has
  no quantitative claims.
- important claims should include evidence anchors: page, section, table, line,
  or extraction offset.

## Concept Frontmatter

```yaml
---
id: concept-name
title: "Concept Display Name"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Concept pages are living synthesis. They do not use `stable` status, but every
important claim should cite a source page.

## ID Allocation

- source IDs use `LLM-NNNN`
- read `_state/id-counter.md`
- allocate the next number only once a draft is created
- do not reuse IDs after deletion or failed ingest

## Lifecycle

```text
raw/source.pdf
  -> raw/source_fulltext.txt or raw/source_markdown/combined.md
  -> drafts/LLM-NNNN.md (status: draft)
  -> qa-reports/LLM-NNNN.md
  -> sources/LLM-NNNN.md (status: stable)
  -> concepts/*.md
  -> qa-reports/LLM-NNNN-contradiction.md
  -> log.md
```

## QA Gate

A stable source page requires:

- independent QA, not self-review
- `overall >= 7.0`
- `verdict: PASS`
- report saved under `qa-reports/`
- traceable fixes for any QA issues

QA report format:

```markdown
# QA Report: LLM-NNNN
- date: YYYY-MM-DD
- reviewer: independent-qa
- accuracy: X/10
- completeness: X/10
- compression: X/10
- traceability: X/10
- overall: X.X/10
- verdict: PASS|FAIL
- issues:
  - ...
```

QA reports are append-only. Do not rewrite historical reports.

## Evidence Anchors

Every durable factual claim should be traceable. Use the best available anchor:

- `page: 7`
- `section: 3.2`
- `table: 2`
- `raw extraction: raw/paper_fulltext.txt#L120-L145`
- `doi:` or `arxiv:` when the claim is source identity

If exact anchors are unavailable, write the nearest human-readable anchor and
mark what needs improvement.

## Contradictions

When new evidence conflicts with an existing concept claim:

- keep both pieces of evidence
- mark the tension with `[CONTRADICTION YYYY-MM-DD]`
- cite both sources
- do not silently overwrite older claims

## Claim Graph

Semantic self-growth uses `claims/claims.jsonl`. Each row is a JSON object with:

- `claim_id`: stable generated identifier
- `source_id`: `LLM-NNNN`
- `claim_type`: `contribution` or `metric`
- `subject`, `predicate`, `object`
- `value` and `unit` when numeric
- `baseline` when available
- `evidence`: source page, parsed Markdown, page, table, or line anchor
- `concepts`: related concept page ids
- `confidence`
- `needs_review`
- `metric_key`, `normalized_value`, `normalized_unit`, `unit_family`
- `baseline_key`, `protocol_key`, and `normalization_warnings` after metric
  normalization

The claim graph is generated from stable source pages. It can be regenerated,
but concept-page conclusions and QA reports remain reviewable Markdown records.

## Source Discovery And Deduplication

`_state/source-registry.jsonl` records discovered or ingested source candidates.
Rows may come from `raw/`, existing `sources/`, or optional arXiv API discovery.
Deduplication keys include:

- `arxiv`
- `doi`
- `sha256`
- `title_key`

Discovery is advisory. It must not delete raw files or source pages.

## Growth Queue

`_state/growth-queue.jsonl` records durable tasks with `task_id`, `action`,
`target`, `status`, `priority`, `due_at`, `attempts`, and `reason`.
Supported actions are `discover`, `grow`, `science-review`, `concept-revision`,
and `lint`. Queue runners may mark tasks done or failed, but should not edit
raw evidence.
Planning supports `now`, `daily`, `weekly`, and `monthly` cadence values and
stages dependent actions a few minutes apart.

## Second-Pass Scientific Review

`_state/science-review-queue.jsonl` contains claims that need human or second
LLM review. `qa-reports/science-review-YYYY-MM-DD.md` is the append-only review
packet. This layer checks scientific meaning, metric comparability, protocol
compatibility, and baseline fairness beyond deterministic anchor validation.
Queue rows include `review_id`, `review_status`, `review_decision`,
`reviewed_by`, `reviewed_at`, `review_reasons`, and `review_questions`.
Concept revision excludes review-required claims unless the claim is explicitly
marked `science_review: approved`.

## Query Writeback

Query writeback is for reusable synthesis, not every answer.

Writeback is appropriate when the answer:

- cites three or more sources
- creates a durable comparison table or timeline
- connects concepts not already linked
- identifies a recurring research question

Answering is read-only by default. Writeback requires approval unless the user
has pre-authorized automatic wiki growth.

Preferred writeback flow:

1. answer with citations
2. generate a proposed diff
3. get approval or use explicit pre-authorization
4. apply the diff
5. run lint
6. append `log.md`

## Log Format

Each operation appends one line:

```text
[YYYY-MM-DD HH:MM] action | target | agent | note
```

Allowed actions include:

- `parse`
- `draft`
- `qa`
- `publish`
- `concept-update`
- `query-writeback`
- `contradiction-check`
- `lint`
- `archive`

## File Safety Rules

- never edit original source files in `raw/`
- never modify files outside the wiki vault
- never publish without QA
- never delete pages during ingest or lint without explicit user approval
- prefer targeted edits over whole-page rewrites
- list changed files in the final response

## Optional Obsidian Layer

Obsidian settings, plugins, themes, and diagrams are an experience layer for
reading, search, navigation, backlinks, and light editing. They must not change
the evidence model.

Rules:

- enable Obsidian only through explicit setup, such as
  `wiki_obsidian_setup.py` or `wiki_init.py --obsidian`.
- merge `.obsidian/*.json` settings; do not overwrite unrelated user keys.
- prefer `[[wikilink]]` for internal wiki links.
- important concept-page conclusions must cite source pages such as
  `[[LLM-NNNN]]`.
- `raw/inbox/` may hold unprocessed material, but it is not stable evidence
  until ingest creates a draft/source page and registry entry.
- `raw/` remains immutable even when files are visible in Obsidian.
- `qa-reports/` remains append-only.
- diagrams under `canvas/` or `assets/excalidraw/` are explanatory aids, not
  evidence sources; link them from source or concept pages and keep evidence
  citations next to the claims they illustrate.
- Obsidian plugins must not bypass QA gates, science review, contradiction
  checks, or query writeback approval.
- `_dashboard.md` is generated status, not evidence. Regenerate it with
  `wiki_status.py --write-dashboard`; do not use it to approve review items.
- `templates/agent-prompts/` may contain reusable agent workflows, but those
  prompts must preserve the same raw immutability, review, QA, and writeback
  approval boundaries as the runtime.

## Optional Knowledge Graph Layer

The knowledge graph is a derived, read-only explanation layer. It may write
`graph.json`, `graph.schema.json`, and `graph-report.md` under `.graph/`, or an
Obsidian Canvas view under `canvas/`. It must not rewrite `sources/`,
`concepts/`, `claims/`, `qa-reports/`, `_state/`, or `raw/`.

Supported node types include `source`, `draft`, `concept`, `claim`, `metric`,
`qa-report`, `contradiction`, `science-review`, `raw`, and `queue-task`.
Supported edge types include `cites`, `derived-from`, `supports`,
`contradicts`, `needs-review`, `reviewed-by`, `updates`, and `related-to`.

Rules:

- graph nodes and Canvas nodes are not evidence sources.
- every durable concept conclusion still needs source or claim citations.
- useful evidence paths should resolve as
  `concept -> claim -> source -> evidence anchor`.
- focused graphs may hide unrelated context but must not change underlying
  Markdown or JSONL data.
- graph export must stay local and must not upload raw files or paper text.
- `wiki_lint.py --graph` reports broken evidence paths or isolated source and
  concept nodes; it does not apply fixes.

## Runtime Commands

The vault may contain runtime scripts at `.open-llm-wiki/scripts/`:

```bash
python .open-llm-wiki/scripts/pdf_corpus_report.py raw --fail-on-missing --fail-on-suspicious
python .open-llm-wiki/scripts/pdf_corpus_to_markdown.py raw --output-root raw --no-download-images
python .open-llm-wiki/scripts/pdf_to_markdown.py raw/source.pdf --output raw/source_markdown
python .open-llm-wiki/scripts/wiki_ingest_corpus.py . --resume
python .open-llm-wiki/scripts/wiki_claims.py .
python .open-llm-wiki/scripts/wiki_normalize_metrics.py . --in-place
python .open-llm-wiki/scripts/wiki_semantic_qa.py . --write-report --fail-on p1
python .open-llm-wiki/scripts/wiki_contradictions.py . --write-report
python .open-llm-wiki/scripts/wiki_science_review.py . --queue --write-report
python .open-llm-wiki/scripts/wiki_discover_sources.py .
python .open-llm-wiki/scripts/wiki_queue.py . plan
python .open-llm-wiki/scripts/wiki_concept_revision.py . --apply
python .open-llm-wiki/scripts/wiki_grow.py . --discover-sources --plan-queue --queue-cadence weekly --science-review --apply-concept-revision
python .open-llm-wiki/scripts/wiki_lint.py . --fail-on p1
python .open-llm-wiki/scripts/wiki_lint.py . --obsidian --fail-on p1
python .open-llm-wiki/scripts/wiki_lint.py . --graph --fail-on p1
python .open-llm-wiki/scripts/wiki_search.py . "query terms"
python .open-llm-wiki/scripts/wiki_obsidian_setup.py . --profile minimal --skip-downloads
python .open-llm-wiki/scripts/wiki_graph_export.py . --format json
python .open-llm-wiki/scripts/wiki_graph_export.py . --format obsidian-canvas --output canvas/wiki-graph.canvas
python .open-llm-wiki/scripts/wiki_status.py .
python .open-llm-wiki/scripts/wiki_status.py . --write-dashboard --force
python .open-llm-wiki/scripts/wiki_writeback.py . --target concepts/page.md --query "..." --body "..."
```
