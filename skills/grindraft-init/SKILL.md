---
name: grindraft-init
description: |
  磨稿首次 onboarding 与脚手架创建器。检测用户状态 → 创建项目骨架 → 配置参数。支持双模式：有历史数据的用户直入 calibration，从零开始的用户走 cold-start。触发词："初始化"/"init"/"磨稿初始化"/"首次使用"。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
---

# grindraft-init — 磨稿初始化

## Overview

```
[用户：磨稿初始化]
  ↓
[Phase 0: 检测已有状态]
  ↓
[Phase 1: 收集用户参数]
  ↓
[Phase 2: 创建目录和骨架文件]
  ↓
[Phase 3: 配置 rubric]
  ↓
[Phase 4: 判定 mode（cold-start vs calibration）]
  ↓
[Phase 5: 写入 .grindraft-state.json]
  ↓
[Phase 6: 输出入口引导]
  ↓
[Phase 7: 自检 — 逐项重读验证全部写入]
```

## Constants

- **DEFAULT_FREQUENCY = "weekly-2"** — 默认周 2 篇
- **COLD_START_THRESHOLD = 5** — 前 5 篇走 cold-start 简化预测
- **MODES = ["cold-start", "calibration"]**

## Workflow

### Phase 0: 检测已有状态

检查用户项目是否已有 `.grindraft-state.json`：
- 存在 → 询问"已经初始化过，要重新配置还是继续？"
  - 重新配置 → 读旧 state 作参考，进入 Phase 1
  - 继续 → 退出，提示"用 grindraft-status 查看状态"
- 不存在 → 进入 Phase 1

### Phase 1: 收集用户参数

按优先级询问（可一次性用 AskUserQuestion 批处理）：

**Q1: 公众号粉丝数**
- "你公众号有多少关注？（大致数字即可）"
- 默认 0（不输入时）
- 用于调整初始 bucket 边界

**Q2: 当前写作状态**
- A) "我有粉丝但文章不是我写的，现在想自己沉淀风格" → `style_migration = true`
- B) "我从零开始，还没发过文章" → `style_migration = false, cold-start`
- C) "我已经在写文章了，想用磨稿来校准提升" → `style_migration = false, calibration`

**Q3: 发布频率**
- A) 周 2-3 篇（起步期，频率换曝光）
- B) 周 1-2 篇（成长期，品质优先）
- C) 周 1 篇或更慢（成熟期，深度长文）

**Q4: AI 默认参与程度**
- A) low — "我写核心内容，AI 只润色"
- B) medium — "我给大纲和要点，AI 扩写"
- C) high — "我给选题，AI 出初稿，我修改"

### Phase 2: 创建目录和骨架文件

在用户项目根目录下创建：

```
drafts/
scripts/
predictions/
output/
retro/
plates/style-diffs/
.grindraft-cache/
```

写入模板文件（**绝不覆盖已有文件**——用户如果已有同名的，先警告再询问）：

| 文件 | 来源模板 |
|---|---|
| rubric_notes.md | templates/rubric_notes.template.md |
| style_guide.md | templates/style_guide.template.md |
| WORKFLOW.md | templates/workflow.template.md |
| candidates.md | templates/candidates.template.md |
| benchmark.md | templates/benchmark.template.md |
| audience.md | templates/audience.template.md |
| STATUS.md | grindraft-status 首次运行时创建 |

### Phase 3: 配置 rubric

1. 复制 `starter-rubrics/wechat-long-form-zero.md` 内容到 `rubric_notes.md` 的"当前公式"段
2. 如果用户有历史文章数据 → 询问是否导入做 benchmark
   - 是 → 进入 calibration 模式（跳过 cold-start）
   - 否 → 走 Phase 4 的 mode 判定
3. 按 Q1 粉丝数调整 bucket 边界：follower_count 每 +1000，bucket 下界 +10%

### Phase 4: 判定 mode

```
if calibration_samples >= 5 OR 用户明确选了 "已经在写文章":
    mode = "calibration"
    cold_start_remaining = 0
else:
    mode = "cold-start"
    cold_start_remaining = 5
```

### Phase 5: 写入 .grindraft-state.json

按 [shared-references/state-management.md](../../shared-references/state-management.md) 的 schema 写入。

### Phase 6: 输出入口引导

```
✅ 磨稿初始化完成！

模式：{cold-start / calibration}
Rubric：公众号长文 7 维 {v0 等权 / v1 加权}
默认 AI 参与度：{low / medium / high}
发布频率：{周 N 篇}

📂 已创建项目骨架：
  drafts/      — AI 初稿存这里
  scripts/     — 你改完的终稿
  predictions/ — 预测日志（不可改！）
  output/      — 排版好的 HTML
  retro/       — 复盘数据

📋 核心工作流：
  1. "抓热点" → 拉 AI 圈精选资讯
  2. "找选题" → 聊出一个想写的角度
  3. "写文章" → AI 出初稿
  4. "去 AI 味" → 四层自检
  5. "排版" → 转公众号 HTML
  6. "启动预测" → 写预测日志（⚠️ 写完不可改）
  7. "已发布" → 登记 + 提醒复盘时间
  8. "复盘" → T+3 天后看数据

现在想做什么？
- 抓热点找灵感 → "抓热点"
- 直接聊选题 → "找选题"
- 看看我能干嘛 → "状态"
```

### Phase 7: 自检 — 逐项重读验证写入完整性

写完所有数据后，**重新读取每个目标文件**，逐项确认写入生效。不依赖记忆——必须 re-read。

#### 验证清单

| # | 目标 | 读什么 | 通过条件 |
|---|---|---|---|
| 1 | state.json | `.grindraft-state.json` | `schema_version` 存在，`mode` 为 cold-start 或 calibration，`rubric_version` 非空，`created_at` 非空 |
| 2 | 目录 | 检查各目录存在 | `drafts/` `scripts/` `predictions/` `output/` `retro/` `plates/style-diffs/` `.grindraft-cache/` 全部存在 |
| 3 | rubric_notes.md | `rubric_notes.md` | 文件非空，含"当前公式"段 |
| 4 | style_guide.md | `style_guide.md` | 文件存在且非空 |
| 5 | WORKFLOW.md | `WORKFLOW.md` | 文件存在且非空 |
| 6 | candidates.md | `candidates.md` | 文件存在且非空 |

#### 自检输出格式

```
📋 自检 Phase 7:
  □ state.json → schema_version=1, mode=calibration ✅
  □ 目录 → 7/7 全部存在 ✅
  □ rubric_notes.md → 含"当前公式"段 ✅
  □ style_guide.md → 文件存在 ✅
  □ WORKFLOW.md → 文件存在 ✅
  □ candidates.md → 文件存在 ✅

✅ 初始化自检全部通过
```

#### 失败处理

- ❌ 任何一项不通过 → **立即重建对应文件/目录**，不中断流程
- 重建后再次 re-read 确认 → 仍不通过 → 输出 `❌ 自检失败，请手动检查` 并列出具体失败项
- 所有项通过 → 输出 `✅ 初始化自检全面通过`

**自检通过后才算初始化完成。** 自检不通过不允许进入后续流程。
