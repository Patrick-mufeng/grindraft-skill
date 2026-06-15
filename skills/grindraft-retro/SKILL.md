---
name: grindraft-retro
description: |
  T+N 天数据回收 + 复盘。逐假设验证预测、提炼派生比率、跨样本检测升级。触发词："复盘"/"retro"/"T+N 天数据来了"/"看数据"/"复盘这篇"。
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
---

# grindraft-retro — 数据回收与复盘

抓 T+N 天的实际数据 → 逐假设验证预测 → 派生比率 → 提炼观察 → 跨样本检测 → 写入文件。

**只追加 `## 复盘` 段，绝不改预测段。**

## Overview

```
[用户：复盘 articles/{标题}_{日期}]
  ↓
[Phase 0: 校验 immutability + 时间窗口]
  ↓
[Phase 1: 抓数据（manual paste — 只需 3 个核心数字 + 可选 4 个）]
  ↓
[Phase 2: 写实绩段 + 派生比率]
  ↓
[Phase 3: 逐假设验证 ✅/❌]
  ↓
[Phase 4: 提炼新观察 → rubric_notes.md 或 style_guide.md]
  ↓
[Phase 5: 跨样本检测 → 自动升级 pattern]
  ↓
[Phase 6: 追加到 ## 复盘 段]
  ↓
[Phase 7: 更新 state + 检测 bump 触发]
  ↓
[Phase 8: 自检 — 逐项重读验证全部写入]
  ↓
[Phase 9: 跨文件一致性校验 — 闭环终点检查]
```

## Constants

- **RETRO_WINDOW_DAYS = 3** — 公众号文章默认 T+3d
- **CORE_METRICS = ["阅读量", "分享数", "收藏数"]** — 最少需要这 3 个
- **OPTIONAL_METRICS = ["在看数", "留言数", "阅读完成率", "留言文本"]** — 可选，有就更好

## Workflow

### Phase 0: 校验

1. 读 `<prediction-file>`，确认存在
2. 取最后一个 `## 预测 vN` 作为校准依据
3. 校验 header 有 `Published at`——没登记不能复盘
4. 校验时间窗口：今天 - published_at >= 3 天。不够 → 提示"还差 X 天"，询问是否仍复盘（标 `early_retro: true`）
5. 已有复盘段 → 询问"补充还是修正？"——修正预测段 = 拒绝

### Phase 1: 抓数据

**只需 3 个核心数字，4 个可选。不用全粘。**

询问用户：

```
打开公众号后台 → 内容管理 → 找到这篇文章。

粘贴以下数据（有就粘，没有跳过）：
  阅读量：_______
  分享数：_______
  收藏数：_______

可选（有助于更准）：
  在看数：_______
  留言数：_______
  阅读完成率：______%

如果有印象深刻的留言，简单描述几句就行。
```

解析数字 → **立即写入 `articles/{标题}_{日期}/retro/report.md`**（强制！）。

> ⚠️ `articles/{标题}_{日期}/retro/report.md` 是原始数据的唯一权威存储。用户粘贴的原始数字必须一字不改地写入这里。predictions 的 `## 复盘` 段只放分析结果（派生比率 + 验证 + 观察），不重复放原始数据。

**report.md 格式**（原始数据，不做任何加工）：

```markdown
# 复盘原始数据：<文章标题>

**复盘时间**：YYYY-MM-DD
**数据来源**：manual paste（公众号后台）

## 原始数据

| 指标 | 数值 |
|---|---|
| 阅读量 | |
| 分享数 | |
| 收藏数 | |
| 在看数 | |
| 留言数 | |
| 阅读完成率 | |

## 留言摘要

（如有）
```

> ⚠️ report.md 写入后立即自检（Phase 1.5）：re-read 确认文件存在且非空。

### Phase 2: 实绩段 + 派生比率

**读 `articles/{标题}_{日期}/retro/report.md` 原始数据**，计算派生比率。派生结果写入 predictions 的 `## 复盘` 段。

**不能只列数字。必须算比率，有比率才有对比。**

```markdown
### 实绩数据

| 指标 | 数值 | 派生比率 | vs 基准 |
|---|---|---|---|
| 阅读量 | 3,200 | — | 高于同粉丝量均值 1.3 倍 |
| 分享数 | 45 | 分享率 1.4% | 低于基准（均值 2.1%） |
| 收藏数 | 128 | 收藏率 4.0% | 高于基准 2.1 倍 ⬆ |
| 在看数 | 18 | 在看率 0.56% | — |
| 留言数 | 23 | 留言率 0.72% | — |
| 阅读完成率 | 68% | — | — |
```

派生比率公式：
- 分享率 = 分享数 / 阅读量 × 100%
- 收藏率 = 收藏数 / 阅读量 × 100%
- 留言率 = 留言数 / 阅读量 × 100%
- 在看率 = 在看数 / 阅读量 × 100%

基准值从 `.grindraft-state.json` 的 `baseline_metrics` 读取（初始化时从历史文章计算，后续每次复盘后自动更新）。如果 `baseline_metrics` 为空（无历史文章导入），使用粉丝量相近账号的默认均值。

**留言关键词**：如果有留言，简单归纳 2-3 个高频主题（如"实用""太贵了""试了确实好用"）。

### Phase 3: 逐假设验证

对预测文件里每一项，用真实数据逐条判定。**每条必须引用具体数据，不许写"基本符合"。**

```markdown
### 验证 ✅ / 推翻 ❌

**验证 ✅**：
- HK=4 被验证：阅读量 3200，高于同粉丝量均值 1.3 倍，标题钩力成立
- UT=5 被验证：收藏率 4.0%，高于基准 2.1 倍——这篇文章确实"有用"
- SC=4 被验证：留言中有"写得真完整""结构好"等反馈

**推翻 ❌**：
- EP=3 被推翻：分享率 1.4% 低于基准，说明虽然文章有共鸣但缺乏"让人想转发"的峰值
- DT=2 可能低估：留言率 0.72% 不算低，且留言质量高（"我也遇到了这个问题..."），思辨激发度应该 ≥3

**不确定**：
- NR=4 无法判断：缺阅读完成率数据
```

判定逻辑：
- 维度分 ≥4 且对应数据高于基准 → ✅ 验证
- 维度分 ≥4 但对应数据低于基准 → ❌ 推翻
- 维度分 ≤2 但对应数据高于基准 → ❌ 低估
- 数据缺失 → 无法判断

### Phase 4: 提炼新观察

分两类输出：

#### 4a. Rubric 观察（→ rubric_notes.md）

打分维度/公式相关。**每条必须可追溯到具体数据。**

```markdown
### 写入 rubric_notes.md

1. **UT 在工具分享型文章中的真实权重应 ≥ ×2.5**：收藏率 4.0% 是基准的 2.1 倍，UT=5 的信号强度被验证
2. **EP 和分享率的相关性需要再观察**：EP=3 但分享率倒挂，下次同类型文章压低 EP 预测
```

#### 4b. 写作观察（→ style_guide.md）

如果用户做了明显改动（diff draft 初稿 vs 终稿），且改动方向与数据表现有因果关系：

```markdown
### 写入 style_guide.md

1. **你把 AI 写的"高效""强大"等词全砍了** → 文章更口语 → 完读率 68% 高于预期
   → 建议加到禁区："高效""强大""赋能"等 inflated 词
```

用户确认后写入。

### Phase 5: 跨样本检测

扫 `rubric_notes.md` 已有观察，看本次新观察是否与某条已有观察形成 ≥2 样本支持。

```markdown
### 跨样本检测

🔗 **UT 的权重应上调**：本次 UT=5→收藏率 4.0%（2.1 倍基准）+ 上次 UT=4→收藏率 3.5%（1.8 倍基准）
   → 2 个独立样本支持，建议下次 bump 时将 UT 权重从 ×1.5 调到 ×2.5
```

如果 ≥2 样本支持同一结论 → 在 rubric_notes.md 中升级到"重大跨样本观察"段。

### Phase 6: 追加到 ## 复盘 段（仅分析结果）

用 Edit 追加到 `## 复盘` 段（删除占位 "（待填）"）。

**写入内容**：派生比率 + 逐假设验证 + 提炼观察 + 跨样本检测（Phase 2-5 的输出）。**不写入原始数据**——原始数据在 `articles/{标题}_{日期}/retro/report.md` 中。

追加后校验：所有 `## 预测...` 段的 hash 与 Phase 0 cache 一致。**任一段被改 → 报错回滚。**

### Phase 7: 更新 state + 检测 bump

```json
{
  "calibration_samples": <+1>,
  "pending_retros": [<剔除本次>],
  "last_retro_at": "<ISO>",
  "baseline_metrics": <重新计算中位数>
}
```

> **baseline_metrics 更新**：每次复盘后，将本次文章的分享率/收藏率等纳入历史数据，重新计算中位数。这样基准值会随着数据积累越来越准确。

> **benchmark.md 同步更新**（强制！）：更新 baseline_metrics 后，**必须同时**将新基准值写入 `benchmark.md` 的"我的基准指标"表，并在"基准更新日志"追加一条记录。state.json 和 benchmark.md 必须保持一致。

**bump 触发判断**（不是固定阈值，AI 判断）：

| 信号 | 说明 |
|---|---|
| 连续 ≥3 次同向偏差 | 同一个方向连续错 → 系统性偏差 |
| 1 次极端偏差 ≥5x | 单次超大幅度 → 强烈信号 |
| 跨样本检测命中 ≥2 样本 | 多个独立样本支持同一结论 → 可靠信号 |
| 评论中出现反向证据 | 数据 + 评论双信号 → 置信度更高 |

任一触发 → 提示"建议升级 rubric"。不触发 → 继续积累。

### Phase 8: 自检 — 逐项重读验证写入完整性

写完所有数据后，**重新读取每个目标文件**，逐项确认写入生效。不依赖"刚才写过了"的记忆——必须 re-read。

#### 验证清单

| # | 目标 | 读什么 | 通过条件 |
|---|---|---|---|
| 1 | 预测文件 | `articles/{标题}_{日期}/prediction.md` | `## 复盘` 段下有实绩数据（非占位"待填"），且 hash 校验通过（预测段未被改） |
| 2 | state.json | .grindraft-state.json | `calibration_samples` 已 +1；`pending_retros` 已剔除本次；`last_retro_at` 已更新；`baseline_metrics` 已更新 |
| 3 | rubric_notes.md | rubric_notes.md | 本次新写入的观察在文件末尾可找到（如有写入） |
| 4 | style_guide.md | style_guide.md | 本次新写入的 pattern 在文件末尾可找到（如有写入） |
| 5 | benchmark.md | benchmark.md | 如有 baseline_metrics 更新，`基准指标` 表已同步；`基准更新日志` 有新条目 |

#### 自检输出格式

按行逐项输出，**每一项必须标注 ✅ 或 ❌**：

```
📋 自检 Phase 8:
  □ articles/{标题}_{日期}/prediction.md → ## 复盘 段有实绩数据 ✅
  □ state.json → calibration_samples: 7 (+1) ✅
  □ state.json → pending_retros: 已剔除 ✅
  □ state.json → last_retro_at: 已更新 ✅
  □ state.json → baseline_metrics 已更新 ✅
  □ rubric_notes.md → 新观察已追加 ✅
  □ style_guide.md → 无写入，跳过
  □ benchmark.md → 基准指标表已同步，更新日志已追加 ✅（或"无 baseline_metrics，跳过"）

✅ 自检全部通过
```

#### 失败处理

- ❌ 任何一项不通过 → **立即重写对应字段**，不中断流程
- 重写后再次 re-read 确认 → 仍不通过 → 输出 `❌ 自检失败，请手动检查` 并列出具体失败项
- 所有项通过 → 输出 `✅ 自检全面通过`

### Phase 9: 跨文件一致性校验 — 闭环终点检查

Phase 8 自检通过后，**额外做一次跨文件交叉校验**，确保没有文件被遗漏。

#### 交叉校验清单

| # | 检查什么 | 怎么查 | 通过条件 |
|---|---|---|---|
| 1 | candidates.md vs 本次复盘 | 读 `candidates.md` | 对应条目的 `status` 应为 `published`（如选题来自 candidates） |
| 2 | retro/ 目录 | 检查 `articles/{标题}_{日期}/retro/report.md` | 如 Phase 1 写了 report.md，文件存在 |
| 3 | pending_retros 一致性 | 读 state.json 的 `pending_retros` | 本次复盘的文章已从中剔除 |
| 4 | 所有 predictions 完整性 | Glob `articles/*/prediction.md`，读 header | 所有含 `Published at` 的预测文件，要么有 `## 复盘` 实绩数据，要么在 `pending_retros` 中 |
| 5 | calibration_samples 一致性 | 读 state.json | `calibration_samples` = 有实绩复盘的 prediction 文件数量 |
| 6 | benchmark.md vs state.json 一致性 | 读 `benchmark.md` 的基准指标表 vs state.json 的 `baseline_metrics` | 两处数据一致（如有更新） |

#### 交叉校验输出格式

```
📋 跨文件一致性 Phase 9:
  □ candidates.md → 对应条目 status: published ✅（或 "无联动"）
  □ retro/ → report.md 已写入 ✅（或 "无 retro 报告"）
  □ pending_retros → 已剔除本次 ✅
  □ predictions 完整性 → 11/11 已发布文章均有 prediction 文件含复盘或待复盘 ✅
  □ calibration_samples → state=8，实际复盘=8 ✅
  □ benchmark.md ↔ state.json → 基准值一致 ✅（或 "无 baseline_metrics，跳过"）

✅ 跨文件一致性全部通过
```

#### 失败处理

- ❌ 任何一项不通过 → 输出 `⚠️ 发现不一致：<具体描述>`，询问用户是否立即修复
- 用户确认 → 修复后再次校验
- 用户拒绝 → 记录到 `rubric_notes.md` 的维护提醒

**Phase 9 是复盘的最后一步——通过后才算复盘真正完成。**

**Phase 9 通过后，按全局规则刷新 `STATUS.md`。**

## Key Rules

1. **预测段 immutable**——写完后 hash 校验
2. **派生比率必算**——不列裸数字
3. **逐假设验证**——每条 ✅/❌ 必须引用数据
4. **跨样本自动检测**——≥2 样本支持即升级
5. **不在复盘里 bump**——只提议
6. **自检必过才结束**——Phase 8 逐项重读验证，任意一项 ❌ 即重写，重写仍失败则报错

## Refusals

- 「把预测段调一下让复盘好看」 → 拒绝。原则 #1
- 「跳过数据直接写结论」 → 拒绝。没数据不叫复盘
- 「直接 bump 不走流程」 → 拒绝。bump 有跨模型审
