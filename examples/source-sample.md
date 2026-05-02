---
id: LLM-0001
title: "Attention Is All You Need"
status: stable
created: 2017-06-12
updated: 2026-05-01
source: "Vaswani et al., Attention Is All You Need, NeurIPS 2017"
tags: [transformer, attention, sequence-modeling]
---

# Attention Is All You Need

## One-Sentence Contribution

The Transformer replaces recurrent sequence processing with multi-head
self-attention and reports 27.3 BLEU on WMT 2014 English-German for the base
model and 28.4 BLEU for the big model.

## Core Idea

Self-attention lets every token directly attend to every other token in a
sequence. The architecture combines attention blocks, feed-forward layers,
residual connections, normalization, and positional encodings to preserve order
information without recurrence.

## Key Data

| Metric | Value | Baseline | Evidence |
| --- | --- | --- | --- |
| WMT 2014 EN-DE BLEU, base | 27.3 | prior sequence transduction systems listed by the paper | results table |
| WMT 2014 EN-DE BLEU, big | 28.4 | prior best systems listed by the paper | results table |
| Attention heads, base | 8 | not applicable | architecture section |
| Layers, base | 6 encoder + 6 decoder | not applicable | architecture section |

## Timeline Position

```text
RNN seq2seq
`-- attention-augmented seq2seq
    `-- Transformer
```

## Interpretation

The lasting contribution is architectural: attention becomes the main sequence
modeling operation instead of an auxiliary alignment mechanism.

## Links

- Related concepts: [[attention-mechanisms]]
