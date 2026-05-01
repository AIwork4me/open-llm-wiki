# open-llm-wiki

**自己会生长的 AI 知识库。扔论文进去，活的知识出来。**

灵感来自 [Karpathy 的 LLM Wiki 概念](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)。23 篇论文实战验证。零手写。每条事实独立审查。

---

## 你有没有这种感觉？

读了一堆论文，记了一堆笔记，一周后全忘光。笔记不会生长，每篇论文都从零开始。

**open-llm-wiki 的做法**：

- 📥 扔一篇 PDF → 自动解析、写理解页、**独立 AI 质检** → 晋升到 wiki
- ❓ 问一个问题 → 搜索 wiki、综合回答 → **答案自动写回 wiki**
- ⚡ 矛盾自动检测 → 新论文和旧结论冲突时**标记而不是覆盖**
- 📈 概念页持续积累 → 读 10 篇论文后，一个概念页有 5 个来源的交叉理解

**核心洞察：大模型不能自评。** 自检能发现错别字，发现不了错误数字和微妙矛盾。每篇论文都经过**独立子代理 QA**（独立上下文、独立会话）。

---

## 快速开始

```bash
# 一行命令搞定
curl -sSL https://raw.githubusercontent.com/AIwork4me/open-llm-wiki/main/setup.sh | bash

# 然后扔论文进去
cp ~/papers/attention.pdf my-llm-wiki/raw/
# 告诉你的 agent: "Ingest this paper: my-llm-wiki/raw/attention.pdf"

# 用 Obsidian 打开看效果
open my-llm-wiki/
```

---

## 实战数据

23 篇 DeepSeek 论文（2024.01 – 2026.01），覆盖架构演化、推理突破、多模态、专业化方向：

| 指标 | 数值 |
|------|------|
| 入库论文 | 23 |
| Source 页（stable） | 23 |
| Concept 页 | 11 |
| 首次 QA 通过率 | 31% → 70%（"硬数字优先"规则后） |
| 抓住的关键错误 | 1 次（V3.2 Figure vs Table 张冠李戴） |
| 子代理可靠性（glm-5.1） | 4/4 = 100% |

---

## 三条流水线

| 流水线 | 触发 | 做什么 |
|--------|------|--------|
| **Ingest** | 扔 PDF | 解析 → 起草 → 独立 QA → 晋升 → 更新概念 → 矛盾检测 |
| **Ask** | 问问题 | 搜索 wiki → 综合 → 答案写回 wiki |
| **Check** | 每日定时 | 格式检查、QA 覆盖、交叉引用、日志归档 |

---

## 设计原则

1. **论文是原料，概念才是 wiki** — 一篇论文入库应该更新 3-5 个概念页
2. **大模型不能自评** — QA 和矛盾检测必须用独立子代理
3. **查询让 wiki 生长** — 好的综合分析写回 wiki，不消失在聊天里
4. **矛盾标记，永不覆盖** — `⚠️ [CONTRADICTION]` 保留双方
5. **硬数字是脊梁** — "有竞争力的结果"是废话，精确的 benchmark 才是知识

---

## 项目结构

```
open-llm-wiki/
├── setup.sh                  ← 一键安装
├── SCHEMA.md                 ← Wiki 数据结构
├── skills/
│   ├── wiki-ingest/          ← 论文入库流水线（10 步）
│   ├── query-writeback/      ← 查询写回流水线（6 步）
│   └── wiki-lint/            ← 健康检查（5 维度）
├── templates/                ← 页面模板
├── examples/
│   ├── deepseek-v4-sample.md ← 真实 source 页示例
│   └── minimal-vault/        ← 可运行的最小 wiki
└── assets/                   ← 图表和截图
```

---

## 致谢

- **[Andrej Karpathy](https://twitter.com/karpathy)** — [LLM Wiki 概念](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)的原创者
- **[OpenClaw](https://github.com/openclaw/openclaw)** — 让独立 QA 成为可能的 agent 平台
- **DeepSeek** — 23 篇论文作为测试套件

## 许可

MIT
