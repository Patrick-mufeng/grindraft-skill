---
name: grindraft-predict
description: |
  给终稿写一份 immutable 盲预测日志。AI 打 7 维分 + bucket 押注 + 概率分布 + 反事实场景 + 关键校准假设。cold-start 期简化版（只做 7 维分 + 方向押注）。触发词："启动预测"/"predict"/"写预测日志"/"打分并预测"。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
---

# grindraft-predict — 盲预测

**严格遵守 [blind-prediction-protocol.md](../../shared-references/blind-prediction-protocol.md)**。

## Overview

```
[用户：启动预测 articles/{标题}_{日期}/final.md]
  ↓
[Phase 0: Blind check 自检]
  ↓
[Phase 0.5: Mode 判定 — cold-start 简版 vs calibration 完整版]
  ↓
[Phase 1: 读终稿 + rubric + state + 派生 confidence]
  ↓
[Phase 2: 7 维打分]  ← cold-start: Claude 自评 / calibration: 委派 score-blind sub-agent
  ↓
[Phase 3: 锚点对比（如有历史）]
  ↓
[Phase 4: Bucket + 概率分布 + 中枢]  ← cold-start 跳过
  ↓
[Phase 5: 反事实场景 + 关键校准假设]  ← cold-start 跳过
  ↓
[Phase 6: 用户 review]
  ↓
[Phase 7: 落盘 + 更新 state]
  ↓
[Phase 8: 衔接发布]
  ↓
[Phase 9: 自检 — 逐项重读验证全部写入]
```

## Workflow

### Phase 0: Blind check 自检

1. 询问当前发布状态：未发 → 通过
2. 已发且未到复盘窗口 → 问"你看过后续数据吗？"
3. 已发且已过复盘窗口 → 拒绝

### Phase 0.5: Mode 判定

读 `.grindraft-state.json`：
- `mode = "cold-start"` → 简化版（组件 1-3 仅）
- `mode = "calibration"` → 完整版（全部 7 组件）

### Phase 0.7: 风格沉淀

按 [shared-references/style-precipitation.md](../../shared-references/style-precipitation.md) 检查用户是否在预测前做了最后一次修改：

1. 读 `.grindraft-cache/precipitation-log.jsonl`，取本文最近的 file_hash
2. 算当前 `articles/{标题}_{日期}/final.md`（或 draft.md）的正文 hash
   ```bash
   sed -n '/^---$/,/^---$/!p' articles/{标题}_{日期}/final.md | tail -n +2 | sha256sum | cut -c1-12
   ```
3. hash 不同 → 做一轮新沉淀（diff → 识别 pattern → 去重写入 style_guide.md）
4. hash 一致 → 跳过（无新改动）

> 预测前沉淀确保：用户写稿到预测之间所有手动修改的 pattern 都被捕捉，不影响预测的 blind 属性。沉淀只读写 style_guide.md，不碰 prediction.md。

### Phase 1: 读文件

1. **读 `articles/{标题}_{日期}/final.md`**（用户改完的终稿）。
2. 算 script_hash = sha256[:12]（对实际读取的文件内容做 hash）
3. 读 `rubric_notes.md` 当前公式
4. 读 `.grindraft-state.json` → rubric_version, calibration_samples, mode
5. 派生 confidence 等级
6. 问"这是你打算发布的最终稿吗？"

### Phase 2: 7 维打分

#### Cold-start 模式

Claude 自评 7 维等权（按 wechat-long-form-zero.md 锚点）。每维 1-5 分，一行理由引用原文。

#### Calibration 模式（强制隔离流程）

**⚠️ 遵守严格的先后顺序——打乱则隔离失效：**

```
Step 1: 主 Claude 先读 rubric_notes.md（公式），但暂不读终稿正文
   ↓
Step 2: spawn grindraft-score-blind sub-agent，传入 script_path + rubric_notes_path
        → sub-agent 返回 JSON（7维分数 + composite + self_check）
   ↓
Step 3: 主 Claude 现在读终稿正文，独立打分（不受 sub-agent 结果影响）
   ↓
Step 4: 逐维度对比 delta = |self_score - blind_score|
   ↓
Step 5: 异常检测（强制！）
```

**Step 5 异常检测规则**：

| 情况 | 判定 | 处理 |
|---|---|---|
| 7 维 delta 全部 = 0 | ⚠️ 统计异常（概率 ~0） | 输出警告："全部 7 维 delta=0（概率极低）。请确认 sub-agent 是否真正独立运行。如果 sub-agent 未运行，以 self 为准并标注 BlindScored By: main-claude-self" |
| delta ≥ 2 的维度 ≥ 3 个 | 🔴 严重分歧 | 暂停，展示双方打分 + 理由，让用户逐维仲裁 |
| delta ≥ 2 的维度 1-2 个 | 🟡 轻微分岐 | 标注 `decided_as: <self/blind/avg>`，取用户判断或默认取 self |
| 其余 | ✅ 一致 | 取 self 或盲评均可，标注 `decided_as: blind` |

**写入 header**：
```markdown
**BlindScored By**: subagent-v1 / main-claude-self / mixed
**BlindScore Disagreement**: [{dim, blind, self, delta, decided_as}]
```

> ⚠️ 如果 BlindScored By = main-claude-self（sub-agent 未运行或失败），必须在 header 标注，且 confidence 降一档。

### Phase 3: 锚点对比

找历史预测中 composite 接近的样本（±0.5 内），列对照表。
如无锚点 → 写"N/A——第 N 篇预测"。

### Phase 4: Bucket + 概率分布（calibration only）

- 选最可能的 bucket（S/A/B/C/D/E）
- 给所有 bucket 概率分布（加起来 100%）
- 给中枢点估计（该 bucket 内的具体阅读量预测）

**诚实区间**：大概率 bucket 通常 40-65%，不是 95%。

### Phase 5: 反事实 + 校准假设（calibration only）

- 4 段反事实（每段对应一个 bucket）
- 关键校准假设：本篇 vs 对照押 Nx

### Phase 6: 用户 review

展示草稿 → 用户 ok → 落盘。用户挑刺 → 改对应字段 → 重新展示。

### Phase 7: 落盘

文件名：`articles/{标题}_{日期}/prediction.md`

Header 必填字段见 [prediction-anatomy.md](../../shared-references/prediction-anatomy.md)。
留空的 `## 复盘` 段。

**⚠️ `## 预测` 段一旦写入即 immutable。**

落盘后自动更新 state：

```json
{
  "cold_start_remaining": <减 1>,
  "calibration_samples": <不变，等复盘后才 +1>
}
```

如果 `cold_start_remaining` 减到 0 → 自动将 `mode` 切换为 `calibration`，并在输出中提示：

```
🎉 第 5 篇预测完成！完整预测模式已解锁。
   下一篇起可以用 bucket 数字、概率分布、反事实场景了。
```

### Phase 8: 衔接发布

预测落盘后，自动提示用户：

```
发完告诉我链接，我直接登记——不用再跑"已发布"。
```

当用户回复 URL 时，在同一轮对话中完成发布登记（更新 prediction header + state file），无需切换到 `grindraft-publish`。同时更新 `candidates.md` 中对应候选的 status 为 `published`。

> "已发布"仍可作为独立触发词使用（比如预测是很久之前写的，现在才发）。

### Phase 9: 自检 — 逐项重读验证写入完整性

写完预测后，**重新读取每个目标文件**，逐项确认写入生效。

#### 验证清单

| # | 目标 | 读什么 | 通过条件 |
|---|---|---|---|
| 1 | 预测文件 | `articles/{标题}_{日期}/prediction.md` | 文件存在，含 `## 预测 v1` 段且非空，`## 复盘` 段存在（可为占位） |
| 2 | state.json - cold_start | `.grindraft-state.json` | `cold_start_remaining` 已递减（cold-start 模式时） |
| 3 | state.json - prediction_at | `.grindraft-state.json` | `last_prediction_at` 已更新 |
| 4 | candidates.md | `candidates.md` | 如果选题来自 candidates，对应条目 status 已改为 `published`（仅在 Phase 8 衔接发布路径时） |

#### 自检输出格式

```
📋 自检 Phase 9:
  □ articles/{标题}_{日期}/prediction.md → ## 预测 v1 已写入，{N} 字节 ✅
  □ state.json → cold_start_remaining: N（已递减） ✅
  □ state.json → last_prediction_at 已更新 ✅
  □ candidates.md → 无联动或已更新（跳过/✅）

✅ 预测自检全部通过
```

#### 失败处理

- ❌ 预测文件不存在或预测段为空 → **立即重写**
- ❌ state.json 未更新 → **立即重写**
- ❌ candidates 状态未同步 → **立即补写**
- 重写后再次 re-read 确认 → 仍不通过 → 输出 `❌ 自检失败，请手动检查`

**自检通过后，按全局规则刷新 `STATUS.md`。**

## Refusals

- 「看过数据了，但你假装没看」 → 拒绝。走 `_redo.md`。
- 「覆盖之前的预测」 → 拒绝。v1 是档案。写 v2 append。
- 「cold-start 但我要完整版」 → 拒绝。前 5 篇 bucket 数字是 false precision。
- 「跳过反事实」 → calibration 模式下拒绝。反事实是复盘的诊断依据。
