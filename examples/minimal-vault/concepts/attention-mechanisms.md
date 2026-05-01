---
id: concept-attention-mechanisms
title: "Attention Mechanisms"
created: 2026-05-01
updated: 2026-05-01
---

# Attention Mechanisms

> 从 RNN 的辅助机制到整个架构的核心——注意力机制的演化是理解现代 LLM 的关键线索。

## Why It Matters

Attention 让模型"看向"输入中相关的部分，而不是被序列顺序束缚。从 Bahdanau 的 additive attention 到 Transformer 的 multi-head self-attention，这个演化路径解释了为什么现代 LLM 能处理长文本、并行训练、并且理解复杂关系。

## Key Insights

- **Attention 不是 Transformer 发明的**，但 Transformer 证明了 attention alone 就够了。[[LLM-0001]]
- **Multi-head 是关键创新**：不同头关注不同模式（语法、语义、共指），比单一注意力表达力强得多。
- **位置编码是补丁**：attention 不感知顺序，所以需要外部注入。后来 RoPE 用旋转矩阵优雅解决了这个问题。

## Innovation Timeline

| When | What | Source | Key Idea |
|------|------|--------|----------|
| 2015 | Additive Attention | Bahdanau | Alignment between seq2seq states |
| 2017 | Multi-Head Self-Attention | [[LLM-0001]] | Pure attention, no recurrence |

## Open Questions

- 线性注意力（Linformer、Flash Attention）能否在保持表达能力的同时突破 O(n²) 复杂度？
- 多模态注意力（文本+图像）需要怎样的架构变化？

## Sources
- [[LLM-0001|Attention Is All You Need]] — 纯 attention 架构的开创性工作
