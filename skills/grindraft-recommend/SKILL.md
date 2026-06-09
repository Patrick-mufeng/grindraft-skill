---
name: grindraft-recommend
description: |
  从选题池按当前 rubric 排序推荐 top N 选题，每条带 composite + 一句话理由 + 锚点对比。触发词："推荐选题"/"next topic"/"下一篇写什么"/"挑个选题"。
allowed-tools:
  - Bash
  - Read
  - Glob
---

# grindraft-recommend — 选题推荐

## Overview

读 `candidates.md` → 按 composite 降序 → 展示 top N → 每条的 rubric 各维得分 + rationale + 锚点对比。

## Workflow

### Phase 0: 前置检查

1. `candidates.md` 存在且非空 → 进入 Phase 1
2. 不存在或为空 → "选题池是空的。试试'抓热点'或'找选题'。"

### Phase 1: 排序

按 composite 降序（已有粗打分的用已有分，没有的用当前 rubric inline 补打分）。

筛选：
- `status != rejected`（不推荐已放弃的）
- `status != published`（不推荐已发布的，但保留作锚点）

### Phase 2: 展示

```
📋 选题池推荐（top {N}）

| # | 标题 | composite | bucket | 亮点 | 风险 | 锚点 |
|---|---|---|---|---|---|---|
| 1 | ... | 7.8 | B | HK=4 NR=4 | UT=2 偏弱 | vs 上一篇 similar |
| ... |
```

每条附带：
- **亮点**：最高分的 2 个维度
- **风险**：最低分的 1 个维度
- **锚点**：与历史同类型文章的对比

### Phase 3: 选题策略建议

按 [cadence-protocol.md](../../shared-references/cadence-protocol.md) 的 "1 稳 + 1 实验"：

```
建议：
- 稳：选 #1（composite 最高，同类文章已验证）
- 实验：选 #4（新方向，测 UT 维度是否被低估）

或者你告诉我想写哪个方向，我帮你筛。
```

## Key Rules

1. **不全自动**——推荐但让用户选。AI 不替用户决定写什么
2. **每推荐必有理由**——不是"这篇 composite 高"，而是"HK=4 因为标题悬念强，上一篇文章 HK=4 实际打开率好"
3. **1 稳 + 1 实验**——保证产量同时持续探索
