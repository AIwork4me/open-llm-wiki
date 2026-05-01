---
id: LLM-0040
title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
status: stable
created: 2026-04-27
updated: 2026-04-27
source: "DeepSeek-AI, DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence, 2026"
tags: [deepseek, moe, long-context, hybrid-attention, muon, million-token]
---

# DeepSeek-V4

> DeepSeek 再次升级：1.6T 参数 MoE（49B 激活），百万 token 原生上下文，推理 FLOPs 只有 V3 的 27%。核心创新是混合注意力（CSA + HCA）——把 KV cache 压到极致，让百万 token 成为工程现实而非理论极限。后训练用 On-Policy Distillation 替代了 RL。

## 核心贡献

### 架构升级

**两个模型**：
- **DeepSeek-V4-Pro**：1.6T 总参数，49B 激活（MoE），对标 GPT-5 级别
- **DeepSeek-V4-Flash**：284B 总参数，13B 激活，推理极快
- 两个都支持 **100 万 token 上下文**

**三大架构创新**：

1. **混合注意力（CSA + HCA）**：这是最核心的贡献
   - **CSA（Compressed Sparse Attention）**：先把 KV cache 按 m 个 token 压缩成一个 entry，再用 sparse attention 只选 top-k 个 compressed entry。压缩 + 稀疏双管齐下
   - **HCA（Heavily Compressed Attention）**：更激进的压缩（m' >> m），把 KV cache 压得更狠，但不做 sparse selection
   - 两种注意力交替使用（hybrid），在不同层用不同策略
   - **效果**：1M 上下文时，KV cache 只有 V3 的 **10%**，单 token 推理 FLOPs 只有 **27%**

2. **mHC（Manifold-Constrained Hyper-Connections）**：改进残差连接。传统残差是 y = x + f(x)，mHC 在流形空间做约束，让信息流更稳定。Wall-time 开销只有 6.7%

3. **Muon 优化器**：替代 AdamW，用矩阵正交化（Newton-Schulz 迭代）更新参数。收敛更快、训练更稳定

### 混合注意力的细节

CSA 的核心流程：
1. **KV 压缩**：每 m 个 token 的 KV 压成一个 compressed entry（可学习权重 + 位置偏置）
2. **Lightning Indexer**：用低秩方式为每个 query 生成 indexer query，计算与 compressed block 的相关度
3. **Top-k 选择**：只保留最相关的 k 个 compressed block
4. **Shared-KV MQA**：选中的 compressed entry 同时当 key 和 value
5. **Grouped Output Projection**：多头输出分组投影，减少计算量

HCA 的区别：
- 更大的压缩率（m' >> m）
- 不做 sparse selection，全量 attention 但在极压缩的 KV 上
- 加 sliding window attention 保持局部依赖

附加技术：
- **Partial RoPE**：只对最后 64 维用旋转位置编码
- **Attention Sink**：可学习的 sink logits，防止 attention score 必须等于 1
- **FP8/BF16 混合 KV 存储**：RoPE 维度用 BF16，其余用 FP8

### 后训练：On-Policy Distillation (OPD)

V4 用 OPD 替代了 V3 的混合 RL 阶段：
- 先训练领域专家（数学、代码等），用 GRPO 做 RL
- 然后用 OPD 把多个专家的知识蒸馏回主模型
- 好处：避免了 RL 的不稳定性，蒸馏过程更可控

### 基础设施

- **MegaMoE²**：细粒度 EP（Expert Parallelism），通信和计算重叠，1.50-1.96x 加速
- **TileLang**：DSL 开发自定义 kernel，替代数百个 Torch ATen 算子
- **FP4 QAT**：MoE expert 权重量化到 FP4，推理加速 + 省内存
- **Batch-invariant + Deterministic**：确保训练中每个 token 的输出一致，便于调试

## 关键数据

### 预训练
- 32T+ tokens 训练数据（比 V3 更大更多样）
- 多语言数据扩展，覆盖长尾知识

### 效率

| 指标（1M 上下文） | vs DeepSeek-V3.2 |
|-------------------|-------------------|
| 单 token 推理 FLOPs | **27%** |
| KV cache 大小 | **10%** |

KV cache 相比标准 BF16 GQA8 基线压到 **~2%**。

### 基准性能

DeepSeek-V4-Pro-Max（最大推理努力模式）：
- **知识**：MMLU-Pro / GPQA / HLE 上领先开源模型，接近 Gemini-3.1-Pro
- **推理**：超过 GPT-5.2 和 Gemini-3.0-Pro，略低于 GPT-5.4 和 Gemini-3.1-Pro（约落后 3-6 个月）
- **长上下文**：原生 1M token 支持，效率碾压所有竞品
- **实际任务**：中文写作、搜索、代码 Agent 等真实场景表现出色

## 概念关联

- 基座：[[LLM-0018|LLaMA]] 的架构思想（RoPE、SwiGLU、RMSNorm）→ DeepSeek V3 → V4
- MoE 路线：[[LLM-0019|GLaM]] → [[LLM-0032|Mixtral]] → DeepSeek V3/V4
- 长上下文：[[LLM-0010|Transformer-XL]] 开创 → V4 用 CSA/HCA 做到 1M
- Scaling：[[LLM-0025|Scaling Laws]] 的延续——1.6T 参数仍在 scaling
- 概念页：[[decoder-only]]、[[transformer-architecture]]

## 洞察

DeepSeek V4 的核心洞察：**长上下文的瓶颈不是"能不能做"，而是"能不能做得起"**。

之前的长上下文方案（如 Mamba、Ring Attention）要么牺牲效果，要么牺牲速度。V4 的混合注意力方案第一次让百万 token 变成了"工程可行"——KV cache 压到 2%，推理 FLOPs 压到 27%。这意味着百万 token 不是 demo 级别的噱头，而是可以日常使用的生产级能力。

OPD 替代 RL 也很有意思：DeepSeek 的经验是 RL 虽然效果好但不稳定，用 OPD 把多个专家模型的知识蒸馏回来更可控。这可能是"对齐方法"的一个新方向——不是直接 RL，而是先 RL 训专家再蒸馏。

V4 也代表了 MoE 架构的成熟：1.6T 总参数但只激活 49B——MoE 从"实验性架构"变成了"生产级架构"。DeepSeek 在这条路上持续投入，V3 → V3.2 → V4，每次都在 MoE 的效率和基础设施上做深度优化。

---

> 原始论文：`raw/DeepSeek-V4.pdf`

## Changelog
- 2026-04-27: 初始 ingest

