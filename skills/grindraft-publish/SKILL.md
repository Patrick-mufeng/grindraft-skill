---
name: grindraft-publish
description: |
  登记一篇公众号文章已发布，更新预测文件 header 元数据和 state file。**不动预测段任何字符**。触发词："已发布"/"publish"/"发布链接是 X"/"发出去了"。
allowed-tools:
  - Bash
  - Read
  - Edit
  - Glob
---

# grindraft-publish — 发布登记

## Overview

```
[用户：已发布 + URL]
  ↓
[Phase 0: 找到对应预测文件]
  ↓
[Phase 1: 更新 prediction header（仅 metadata 段）]
  ↓
[Phase 2: 更新 .grindraft-state.json]
  ↓
[Phase 2.5: 自检 — 重读验证 header + state]
  ↓
[Phase 3: 提醒盲度 + 复盘时间]
```

## Workflow

### Phase 0: 找到对应预测文件

1. 用户给了 prediction 文件路径 → 直接用
2. 只有 URL → 读 `.grindraft-state.json` 的 `in_progress_session.file`
3. 都没有 → 列出 `articles/*/prediction.md` 中 header 没 `published_at` 的让用户选

### Phase 1: 更新 prediction header

**绝不**触碰 `## 预测` 段及之后。只在 header metadata 块追加：

```markdown
**Published at**: <ISO>
**Platform**: wechat
**URL**: <公众号链接>
```

### Phase 2: 更新 state file

```json
{
  "in_progress_session": null,
  "last_published_at": "<ISO>",
  "last_published_file": "articles/{标题}_{日期}/prediction.md",
  "pending_retros": <追加 "articles/{标题}_{日期}"——不是覆盖，是 append 到已有列表>
}
```

> ⚠️ `pending_retros` 是数组追加，不是覆盖。如果已有其他待复盘文章，保留它们，把本文 append 进去。

### Phase 2.2: 同步 candidates.md（如有联动）

如果文章选题来自 `candidates.md`：
1. 找到对应候选条目
2. 将 `status` 改为 `published`
3. 追加一行 `published_at: YYYY-MM-DD`

### Phase 2.5: 自检 — 重读验证发布登记完整性

写完所有数据后，**重新读取**每个目标文件，逐项确认写入生效。不依赖记忆——必须 re-read。

#### 验证清单

| # | 目标 | 读什么 | 通过条件 |
|---|---|---|---|
| 1 | 预测文件 | articles/{标题}_{日期}/prediction.md | header 含 `Published at:` + `URL:` |
| 2 | state.json | .grindraft-state.json | `last_published_at` 已更新；`last_published_file` 正确；`pending_retros` 已**追加**此文（保留旧条目） |
| 3 | candidates.md（如有） | `candidates.md` | 对应条目 `status` 已改为 `published` |

#### 自检输出格式

```
📋 自检 Phase 2.5:
  □ articles/{标题}_{日期}/prediction.md → header 含 Published at ✅
  □ articles/{标题}_{日期}/prediction.md → header 含 URL ✅
  □ state.json → last_published_at ✅
  □ state.json → last_published_file ✅
  □ state.json → pending_retros 已追加（含 N 篇） ✅
  □ candidates.md → status: published ✅（或 "无联动，跳过"）

✅ 发布登记自检通过
```

#### 失败处理

- ❌ 任何一项不通过 → **立即重写对应字段**，不中断流程
- 重写后再次 re-read 确认 → 仍不通过 → 输出 `❌ 自检失败，请手动检查`
- 所有项通过 → 输出 `✅ 发布登记自检全面通过`

**自检通过后，按全局规则刷新 `STATUS.md`。**

### Phase 3: 提醒

```
✅ 发布登记完成

⚠️  从此刻起，你看到任何阅读/分享/留言数据都会破坏盲度声明。
   如果不小心看到，告诉我——我会在文件里追加 integrity warning。

📅 计划复盘：T+3 天，约 YYYY-MM-DD
   到时间说："复盘 articles/{标题}_{日期}"

📄 排版好的 HTML 在 articles/{标题}_{日期}/output.html
   别忘了去公众号后台粘贴发布～
```

## Key Rules

1. **不动预测段**——连笔误都不修
2. **不抓数据**——publish 是登记，不是数据回收
3. **发布后提醒盲度**——用户在后台看数据的瞬间，下次预测的盲度窗口就关了
4. **自检必过才结束**——Phase 2.5 逐项重读验证，任意一项 ❌ 即重写，重写仍失败则报错

## Refusals

- 「顺便改一下预测段的 HK，我现在觉得是 4 不是 3」 → 拒绝。预测段 immutable。真要改走 `_redo.md`。
- 「URL 等会儿补」 → 允许。published_at 必填，URL 可后续追加。
