---
name: grindraft-bump
description: |
  Rubric 升级——调整维度权重/bucket 边界/新增维度。必须经全量重打 + 跨模型审核。触发词："升级 rubric"/"bump rubric"/"更新公式"/"调整权重"。
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
---

# grindraft-bump — Rubric 升级

**严格遵守 [bump-validation-protocol.md](../../shared-references/bump-validation-protocol.md)。**

## Overview

```
[用户：升级 rubric]
  ↓
[Phase 0: 前置检查 — 校准池是否够大]
  ↓
[Phase 1: 识别升级方向]
  ↓
[Phase 2: 全量重打 + 排序一致性检验]
  ↓
[Phase 3: 跨模型审核]
  ↓
[Phase 4: Cleanup pass — 清理 rubric_notes.md]
  ↓
[Phase 5: 写入新公式 + 版本号]
```

## Constants

- **MIN_SAMPLES_FOR_BUMP = 5** — 首次 bump 至少 5 个样本。后续 ≥8
- **RANK_CONSISTENCY_THRESHOLD = 4/5** — 新排序 vs 实绩排序 ≥4/5 一致
- **CROSS_MODEL_AUDIT = true** — 默认需要跨模型审

## Workflow

### Phase 0: 前置检查

1. 读 `calibration_samples` ≥ MIN_SAMPLES_FOR_BUMP → 不够则拒绝
2. 读 `consecutive_directional_errors` → 看是否有系统性偏差方向
3. 展示当前公式 + 偏差方向摘要

### Phase 1: 识别升级方向

根据复盘观察，确定升级类型：

| 类型 | 触发信号 | 操作 |
|---|---|---|
| **权重调整** | 某维度持续被验证/推翻 | 调权重 ×0.5 ~ ×3.0 |
| **Bucket 重校** | 预测 vs 实绩系统偏移 | 调 bucket 边界 |
| **新维度** | 复盘反复提到 rubric 未捕获的因素 | 新增维度（需 ≥3 样本支持） |
| **维度合并/删除** | 某维度在 ≥5 样本中贡献约等于噪声 | 合并或删除 |

**询问用户**："你感觉 rubric 哪里最不准？"——作为方向参考，但最终升级由数据说话。

### Phase 2: 全量重打

1. 用新公式对校准池所有样本重新计算 composite
2. 新 composite 排序 vs 实际阅读量排序
3. 计算 rank correlation：≥4/5 一致 → 通过

不通过 → 拒绝升级，输出具体哪几篇排序颠倒。

### Phase 3: 跨模型审核

1. 将新公式 + 5 个代表性样本发给外部模型
2. 对方独立打分 → 对比一致性
3. 差异 ≥2 的维度超过 2 个 → 升级被拒

`CROSS_MODEL_AUDIT=false` 时跳过，但标 `self_audited: true`。

### Phase 4: Cleanup pass

按 [observation-lifecycle.md](../../shared-references/observation-lifecycle.md)：
1. 删除已被吸收到公式的观察
2. 删除已被新数据推翻的观察
3. 用新公式重写 rubric_notes.md 的"当前公式"段
4. 更新"历史公式"段（追加新版本号 + 变更摘要）

**绝不留考古层。**

### Phase 5: 写入

```markdown
## 当前公式

**版本**：v{N}
**公式**：raw = (HK×{w} + NR×{w} + ...) / {total}，composite = raw × 5
**升级日期**：YYYY-MM-DD
**升级类型**：权重调整 / bucket 重校 / 新增维度 / 合并删除
**变更摘要**：一句话
**跨模型审核**：通过 / 自审
```

更新 `.grindraft-state.json` → `rubric_version` + `rubric.weights`。

### Phase 5.5: Bucket 边界校验（强制！）

写入新公式前，**必须校验 bucket 边界**：

#### 校验规则

| # | 规则 | 说明 |
|---|---|---|
| 1 | composite 范围不超 [0, 10] | 任何 bucket 的 composite 区间不能超出 0-10 |
| 2 | bucket 区间不重叠 | 相邻 bucket 的 composite 区间不能有交集 |
| 3 | bucket 区间不留间隙 | 相邻 bucket 的 composite 区间必须连续（不含断崖） |
| 4 | 权重总和合理 | 所有权重之和 > 0 |
| 5 | composite 公式输出范围校验 | 用 7 维全 1 分和全 5 分代入公式，输出值必须在 [0, 10] 内 |

#### 校验输出格式

```
📋 Bucket 校验 Phase 5.5:
  □ composite 范围检查 → [0.0, 10.0] 内 ✅
  □ bucket 不重叠检查 → S/A/B/C/D/E 无重叠 ✅
  □ bucket 连续检查 → 无间隙 ✅
  □ 权重总和 → 8.0 > 0 ✅
  □ 极值代入 → min=1.25, max=6.25 ✅

✅ Bucket 校验全部通过
```

#### 失败处理

- ❌ 任何一项不通过 → **拒绝写入**，输出具体错误
- 常见错误示例：
  - `C bucket: 8-11.9 —— composite 最大 10，区间超出` → 拒绝
  - `B(4.8-6.7) 与 C(8-11.9) 间隙 6.7-8.0 —— 缺失区间` → 拒绝
  - `B(4.8-6.7) 与 D(4-7.9) 重叠 [4.8-6.7]` → 拒绝

**校验不通过则不允许写入新公式。**

**校验通过并写入新公式后，按全局规则刷新 `STATUS.md`。**

## Refusals

- 「校准池只有 3 篇，但我感觉公式不准了」 → 拒绝。MIN_SAMPLES_FOR_BUMP 是硬门槛。建议多跑几次复盘再 bump。
- 「跳过跨模型审」 → 仅 `CROSS_MODEL_AUDIT=false` 时允许，标自审。
- 「只调 HK 权重，别的别动」 → 允许（局部 bump），但仍需全量重打验证。
