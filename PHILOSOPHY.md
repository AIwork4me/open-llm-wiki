# Philosophy

open-llm-wiki is built around one idea: a research wiki should compound.

Papers are not the final interface. They are evidence. The useful interface is
the evolving set of concept pages that connect evidence across time.

## Principles

### Sources Feed Concepts

Each paper gets a source page, but the wiki's real value lives in concept pages.
Concepts collect claims, numbers, tensions, and open questions across sources.

### QA Must Be Independent

The same context that drafted a page should not be the only reviewer. Source
pages become stable only after a separate QA pass records a passing audit.

### File Writes Need Boundaries

Agentic workflows are useful because they can update the wiki. They are risky
for the same reason. Every skill states where it may write, when it is read-only,
and what must be logged.

### Contradictions Are Preserved

New evidence should not silently erase old understanding. Mark contradictions,
cite both sides, and let the concept page show how understanding changed.

### Automation Should Be Verifiable

The repository should be easy to validate with official skill checks, a local
quality script, and CI. A workflow that cannot be checked will drift.

### Runtime Beats Prompting Alone

Long-lived knowledge systems need deterministic tools for repetitive work:
initialization, lint, search, and diff generation. The LLM should spend its
attention on judgment and synthesis, while scripts enforce the boring invariants
that keep the wiki healthy after hundreds of edits.
