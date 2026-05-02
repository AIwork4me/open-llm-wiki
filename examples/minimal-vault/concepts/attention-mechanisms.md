---
id: concept-attention-mechanisms
title: "Attention Mechanisms"
created: 2026-05-01
updated: 2026-05-01
---

# Attention Mechanisms

> Attention lets a model weight relevant tokens directly instead of relying only
> on sequential recurrence.

## Why It Matters

Attention is central to modern language models because it gives each token a
direct path to other relevant tokens. In the Transformer, self-attention replaced
recurrent sequence processing as the main computation path. [[LLM-0001]]

## Current Understanding

- Transformer did not invent attention, but it showed that a network built
  primarily from multi-head self-attention could outperform strong recurrent
  and convolutional sequence models on machine translation. [[LLM-0001]]
- Multi-head attention is useful because different heads can attend to different
  relationship patterns in parallel. [[LLM-0001]]
- Positional encoding is required because pure self-attention does not encode
  token order by itself. [[LLM-0001]]

## Timeline

| Date | Change | Source | Evidence |
| --- | --- | --- | --- |
| 2017-06 | Transformer uses multi-head self-attention as the core sequence model | [[LLM-0001]] | 6-layer encoder-decoder, 8 attention heads in base model |

## Open Questions

- Which later positional encoding variants preserve the most long-context
  performance?
- When does sparse or linear attention preserve enough quality to replace full
  attention?

## Sources

- [[LLM-0001|Attention Is All You Need]] - Transformer paper introducing the
  attention-only sequence modeling architecture.
