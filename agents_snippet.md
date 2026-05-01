# AGENTS_SNIPPET.md — Copy This Into Your AGENTS.md

Paste these rules into your OpenClaw `AGENTS.md` to enable wiki operations. Adjust paths for your setup.

```markdown
## Wiki 页面格式（硬约束）

- Source 页 frontmatter 必须包含：id, title, status, created, updated, source, tags
- ID 格式：LLM-NNNN（4 位零填充），从 _state/id-counter.md 分配
- 生命周期：drafts/ → QA(≥7.0) → sources/（status: draft → stable）
- created = 论文发布日期（事实），updated = 最后修改 source 页日期（操作记录）

## Wiki 查询规则

- 查询前先读 index.md 了解现有内容
- 回答引用 wiki 内容时标注来源：[[LLM-XXXX]] 或 [[concept-name]]
- 引用 3+ source 的合成回答 → 触发 query-writeback

## Wiki QA 红线（零容忍）

- QA 必须由独立子代理执行（sessions_spawn，model=glm-5.1）
- 综合评分 ≥ 7.0 才能 publish
- QA 报告写入 qa-reports/（append-only）
- 没有通过 QA 的条目不能 sync 到任何外部平台

## Wiki 矛盾检测规则

- 每次 publish 后 spawn 独立子代理检查新 source 与已有 concept 页的冲突
- 矛盾用 ⚠️ [CONTRADICTION YYYY-MM-DD] 标注，不静默覆盖
- 每 10 次 ingest 触发 concept 修订（独立子代理 review）
```

## Sub-Agent Spawn Configuration

For QA, contradiction check, and concept revision sub-agents:

```
model: glm-5.1
mode: run
runTimeoutSeconds: 180
```

**Why glm-5.1**: Tested with 4/4 reliability. claude-sonnet-4 returned `status=completed` with 0 tokens generated (silent failure, 0/3 reliability).

## Skill Loading

These three skills must be installed in `~/.openclaw-autoclaw/skills/`:

| Skill | When It Triggers |
|-------|-----------------|
| `wiki-ingest` | User provides a paper to add |
| `query-writeback` | User asks about wiki content |
| `wiki-lint` | Periodic (heartbeat or cron) |

