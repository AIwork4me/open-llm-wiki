# Showcase

This repository includes a minimal vault that demonstrates the expected wiki
shape without requiring private papers or API keys.

## Minimal Vault

Path: `examples/minimal-vault/`

It contains:

- one stable source page
- one concept page
- one QA report
- one contradiction report
- one normalized claim graph
- one vault-local schema
- an index
- an operation log

The sample uses "Attention Is All You Need" because it is a familiar public
paper and the example can be reviewed without special context.

## Expected Graph

```text
LLM-0001
  -> attention-mechanisms
attention-mechanisms
  -> LLM-0001
```

## What Good Output Looks Like

A good source page:

- has complete frontmatter
- names exact metrics and baselines
- separates evidence from interpretation
- links to relevant concepts
- remains in `drafts/` until QA passes

A good concept page:

- synthesizes across sources
- cites claims
- marks inference
- keeps open questions visible
- records contradictions rather than overwriting them

## How To Try It

```text
Run wiki lint on examples/minimal-vault.
```

The expected result is a report-only health check with no required fixes.

The runtime smoke test also verifies search, writeback proposal generation, and
fresh vault initialization. Semantic-growth scripts can extract claims, run
semantic QA, scan contradictions, and refresh concept pages:

```bash
uv run python scripts/wiki_eval.py
uv run python scripts/wiki_grow.py examples/minimal-vault --apply-concept-revision
```

PDF-to-Markdown conversion, corpus ingestion, claim extraction, semantic QA,
contradiction scanning, concept revision, and the corpus report are smoke-tested
in CI. Real cloud parsing still requires a private token and sends document
bytes to the configured layout-parsing endpoint.
