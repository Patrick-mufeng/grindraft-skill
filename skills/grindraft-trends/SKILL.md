---
name: grindraft-trends
description: |
  从 aihot 抓取 AI 圈精选资讯，去重 + 粗打分 + 写入选题池。默认源 aihot，可扩展。触发词："抓热点"/"fetch trends"/"今天有什么可写的"/"AI 圈有什么"/"最近 AI 动态"。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - WebFetch
---

# grindraft-trends — 热点抓取

从 aihot API 拉 AI 圈精选资讯 → normalize → 去重 → 粗打分 → 写入 candidates.md。

## Overview

```
[用户：抓热点]
  ↓
[Phase 0: 读 state 拿 enabled sources]
  ↓
[Phase 1: 调 aihot API]
  ↓
[Phase 2: normalize 到 candidate 格式]
  ↓
[Phase 3: 去重（vs candidates / predictions / trends-history）]
  ↓
[Phase 4: 粗打分（用当前 rubric inline 打分）]
  ↓
[Phase 5: 展示 + 询问用户选哪些加入]
  ↓
[Phase 6: 写入 candidates.md + 更新缓存]
  ↓
[Phase 7: 自检 — 逐项重读验证全部写入]
```

## Constants

- **DEFAULT_SOURCES = ["aihot"]**
- **MAX_PER_SOURCE = 20**
- **MIN_COMPOSITE_TO_SUGGEST = 5.0** — 低于此分不推荐（但可手动选）

## Workflow

### Phase 0: 读启用的 sources

读 `.grindraft-state.json` 的 `enabled_trend_sources`。默认 `["aihot"]`。

### Phase 1: 调 aihot API

按 `adapters/trend-sources/aihot.md` 的 fetch 接口：

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
since=$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-24H +%Y-%m-%dT%H:%M:%SZ)
curl -sH "User-Agent: $UA" "https://aihot.virxact.com/api/public/items?mode=selected&since=$since&take=50"
```

优雅降级：API 不可用 → "aihot 暂时不可用，你可以手动粘贴今天看到的选题（URL/标题，每行一条）。"

### Phase 2: Normalize

每条 aihot item → grindraft candidate：

```json
{
  "id": "sha256(aihot_title + aihot_url)[:12]",
  "title": "aihot.title",
  "source": "aihot",
  "source_url": "aihot.url",
  "snippet": "aihot.summary",
  "category": "aihot.category → 选题方向",
  "snapshot_at": "ISO now"
}
```

### Phase 3: 去重

1. 对每个 item 检查 `candidates.md` 是否已有同 id → 跳过
2. 检查 `articles/*/prediction.md` 是否已有同 id → 跳过（已写过的选题）
3. 检查 `.grindraft-cache/trends-history.jsonl` 是否有同 id 且 `rejected_at` 在 6 个月内 → 跳过

### Phase 4: 粗打分

对每条新 item，用当前 rubric inline 打分（7 维，不调 sub-agent）：
- 标题钩力（HK）：按标题文本判断
- 叙事牵引力 / 金句锚点 / 情绪峰值 / 结构闭环：信息不足，默认 2（"无法判断"）
- 实用密度 / 思辨激发度：按摘要判断

标注 `composite (rough, snapshot-based)` 区别于正式预测的精打分。

### Phase 5: 展示

```
🔥 抓热点完成。aihot 拉到 {N} 条精选。

去重后剩 {M} 条新选题。粗打分后 {K} 条 composite ≥ 5.0：

| # | 标题 | 方向 | composite | 理由 |
|---|---|---|---|---|
| 1 | ... | 行业趋势 | 6.8 | HK=4 悬念强，DT=3 有讨论空间 |
| 2 | ... | AI 模型 | 5.5 | HK=3 信息明确，UT=3 实用 |
| ... |

哪些加入选题池？
- 全部 → "all"
- 选几个 → "1, 3, 5"
- 都不要 → "none"
```

### Phase 6: 落盘

- 选中的 items → 追加到 `candidates.md`
- 所有抓回的 items → append 到 `.grindraft-cache/trends-history.jsonl`
- 更新 `.grindraft-state.json` 的 `last_trends_run_at`

### Phase 7: 自检 — 逐项重读验证写入完整性

写完所有数据后，**重新读取每个目标文件**，逐项确认写入生效。不依赖记忆——必须 re-read。

#### 验证清单

| # | 目标 | 读什么 | 通过条件 |
|---|---|---|---|
| 1 | candidates.md | `candidates.md` | 本次选中的 item id 在文件中可找到 |
| 2 | trends-history.jsonl | `.grindraft-cache/trends-history.jsonl` | 本次抓回的 item id 在文件中可找到 |
| 3 | state.json | `.grindraft-state.json` | `last_trends_run_at` 已更新为当天日期 |

#### 自检输出格式

```
📋 自检 Phase 7:
  □ candidates.md → 新增 N 条，id 均存在 ✅
  □ trends-history.jsonl → 写入 N 条记录 ✅
  □ state.json → last_trends_run_at 已更新 ✅

✅ 抓热点自检全部通过
```

#### 失败处理

- ❌ 任何一项不通过 → **立即重写对应字段**，不中断流程
- 重写后再次 re-read 确认 → 仍不通过 → 输出 `❌ 自检失败，请手动检查` 并列出具体失败项
- 所有项通过 → 输出 `✅ 抓热点自检全面通过`

**自检通过后，按全局规则刷新 `STATUS.md`。**

## Refusals

- 「跳过粗打分，直接全写进去」 → 允许但提示"没粗打分的话，grindraft-recommend 没法排序，你只能手动挑"
- 「去重新设置的时间窗」→ 支持 `— since: 7d` 等覆盖

## Integration

- 上游：grindraft-init 创建 candidates.md
- 下游：grindraft-recommend 读 candidates.md 排序
- 下游：grindraft-seed Mode C 以此作为外部素材源
