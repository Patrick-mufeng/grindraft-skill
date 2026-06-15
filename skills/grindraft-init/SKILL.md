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
[Phase 3: 配置 rubric + 历史文章导入]
  │  ├─ 3.0 复制初始 rubric
  │  ├─ 3.1 询问历史文章
  │  └─ 3.2 完整导入（3a-3h）或跳过
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
articles/
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
| .env | 新建（API 配置模板） |
| STATUS.md | grindraft-status 首次运行时创建 |
| preview.html | templates/preview.html |

**.env 模板内容**：
```
# 云雾API 配置（用于正文配图生图 — 注册：https://yunwu.ai/register?aff=zM1f）
# 将 sk-your-api-key-here 替换为你的真实 API Key
YUNWU_API_KEY=sk-your-api-key-here
YUNWU_BASE_URL=https://yunwu.ai

# IMAGE2_BASE_URL 默认同 YUNWU_BASE_URL，通常无需修改
# IMAGE2_BASE_URL=https://yunwu.ai
```

### Phase 3: 配置 rubric + 历史文章导入

#### 3.0 复制初始 rubric

复制 `starter-rubrics/wechat-long-form-zero.md` 内容到 `rubric_notes.md` 的"当前公式"段。

#### 3.1 询问历史文章

```
你有之前写过的公众号文章吗？有的话我可以：
- 分析你的写作风格（自动沉淀到 style_guide.md）
- 用历史数据设定基准指标（复盘时"vs 基准"就有参照了）
- 如果 ≥5 篇，还能拟合初始评分权重

有历史文章吗？
A) 有，我提供 → 进入 Phase 3.2 完整导入
B) 没有，从零开始 → 跳到 Phase 4
```

> 如果用户选了 A 但只有 1-2 篇 → 主动提示：
> "只有 1-2 篇的话，风格分析可能不太准（样本太少），基准值也算不出来。要不要试试找更多？如果暂时没有更多也没关系——等你写完前 5 篇新文章后，沉淀机制会自动积累你的风格偏好。"

#### 3.2 完整导入流程

按 [shared-references/historical-import-protocol.md](../../shared-references/historical-import-protocol.md) 执行 8 个子 Phase：

```
Phase 3a: 收集文章数据
  - 逐篇询问：标题、正文、发布日期、阅读量、分享数、收藏数
  - 支持三种方式：逐篇给 / 一次性全给 / 指定文件夹
  - 最少需要：标题 + 正文 + 发布日期 + 阅读量

Phase 3b: 落盘到 articles/ 目录
  - 每篇创建 articles/{标题}_{发布日期}/
  - 写入 final.md（标"历史文章 — 非 AI 生成"）
  - 写入 retro/report.md（原始数据）

Phase 3c: 风格分析（逆向沉淀）
  - 通读所有历史文章
  - 提取：禁用词、口语化特征、结构偏好、文章原型、语气特征
  - ≥2 篇出现的 pattern → 写入 style_guide.md 正式规则
  - 仅 1 篇出现的 → 标"待验证"
  - 在 style_guide.md 追加"历史文章分析（初始化导入）"段

Phase 3d: 逆向打分
  - 对每篇做 7 维 retrospective 打分
  - 写入 prediction.md（标 ⚠️ RETROSPECTIVE — NOT A BLIND PREDICTION）
  - 标注"已知数据下的观察"（哪些维度可能被高估/低估）

Phase 3e: 拟合初始权重（仅 historical_samples ≥ 5）
  - 计算每维分数与阅读量的 Spearman 相关系数
  - 强正相关（r > 0.5）→ 权重 ×2.0
  - 中等正相关（r > 0.3）→ 权重 ×1.5
  - 负相关（r < -0.1）→ 权重 ×0.5
  - 调整后 rank correlation ≥ 4/5 → rubric_version = "v1"
  - 否则保持 v0，记录偏差方向

Phase 3f: 设定基准值
  - 计算中位数：分享率、收藏率、留言率、在看率、平均阅读量
  - 写入 benchmark.md（含基准指标表 + 历史文章列表）

Phase 3g: 更新 state
  - historical_samples = N
  - calibration_samples = 0（历史文章不计入）
  - baseline_metrics 写入
  - rubric_fitted_from_history = true/false

Phase 3h: 自检
  - 逐项重读：articles/、style_guide.md、benchmark.md、rubric_notes.md、state.json
```

#### 3.3 按粉丝数调整 bucket 边界

follower_count 每 +1000，bucket 下界 +10%。

### Phase 4: 判定 mode

```
if calibration_samples >= 5:
    mode = "calibration"
    cold_start_remaining = 0
elif historical_samples >= 5 AND rubric_fitted_from_history:
    mode = "cold-start"
    // rubric 可以是 v1，但预测格式仍是简化版（不打 bucket 数字）
    // 因为 calibration_samples = 0，没有 blind prediction 经验
else:
    mode = "cold-start"
    cold_start_remaining = 5
```

> **关键区分**：`calibration_samples`（盲预测+复盘完成的文章）和 `historical_samples`（初始化导入的历史文章）是两个独立字段。即使有 100 篇历史文章，只要没有 blind prediction 经验，mode 就是 cold-start。

### Phase 5: 写入 .grindraft-state.json

按 [shared-references/state-management.md](../../shared-references/state-management.md) 的 schema 写入。

### Phase 6: 输出入口引导

```
✅ 磨稿初始化完成！

模式：{cold-start / calibration}
Rubric：公众号长文 7 维 {v0 等权 / v1 加权（从 {N} 篇历史文章拟合）}
默认 AI 参与度：{low / medium / high}
发布频率：{周 N 篇}
{如有历史文章导入：}
📊 已导入 {N} 篇历史文章：
  - 风格特征已沉淀到 style_guide.md（{M} 条 pattern）
  - 基准指标已写入 benchmark.md
  - {rubric 拟合结果}

⚠️ 关于模式：
  你的模式是「cold-start」——虽然有了历史数据，
  但前 5 篇新文章的预测仍是简化版（不打阅读量数字）。
  这是因为历史数据的打分是 retrospective 的（你已经看过数据），
  只有 blind prediction（完全不看数据写预测）才算真正的校准样本。
  写完 5 篇新文章并复盘后，自动解锁完整预测模式。

📂 已创建项目骨架：
  articles/{标题}_{日期}/     — 每篇文章一个文件夹（含 draft/final/封面/配图/排版/预测/复盘）

📋 核心工作流：
  1. "抓热点" → 拉 AI 圈精选资讯
  2. "找选题" → 聊出一个想写的角度
  3. "写文章" → AI 出初稿
  4. "去 AI 味" → 四层自检
  5. "配图" → 生成小黑风格正文插图
  6. "设计封面" → 选模板生成公众号封面
  7. "排版" → 转公众号 HTML
  8. "启动预测" → 写预测日志（⚠️ 写完不可改）
  9. "已发布" → 登记 + 提醒复盘时间
  10. "复盘" → T+3 天后看数据

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
| 2 | 目录 | 检查各目录存在 | `articles/` `plates/style-diffs/` `.grindraft-cache/` 全部存在 |
| 3 | rubric_notes.md | `rubric_notes.md` | 文件非空，含"当前公式"段 |
| 4 | style_guide.md | `style_guide.md` | 文件存在且非空 |
| 5 | WORKFLOW.md | `WORKFLOW.md` | 文件存在且非空 |
| 6 | candidates.md | `candidates.md` | 文件存在且非空 |
| 7 | benchmark.md | `benchmark.md` | 文件存在且非空；如有历史文章导入，含基准指标表 |
| 8 | 历史文章（如有导入） | `articles/` 下各历史文章目录 | 每篇含 `final.md` + `prediction.md` + `retro/report.md` |

#### 自检输出格式

```
📋 自检 Phase 7:
  □ state.json → schema_version=1, mode=calibration ✅
  □ 目录 → 7/7 全部存在 ✅
  □ rubric_notes.md → 含"当前公式"段 ✅
  □ style_guide.md → 文件存在 ✅
  □ WORKFLOW.md → 文件存在 ✅
  □ candidates.md → 文件存在 ✅
  □ benchmark.md → 文件存在，{'含基准指标'/'空骨架'} ✅
  □ 历史文章 → {N} 篇已落盘，每篇含 final + prediction + retro ✅（或"无历史文章导入，跳过"）

✅ 初始化自检全部通过
```

#### 失败处理

- ❌ 任何一项不通过 → **立即重建对应文件/目录**，不中断流程
- 重建后再次 re-read 确认 → 仍不通过 → 输出 `❌ 自检失败，请手动检查` 并列出具体失败项
- 所有项通过 → 输出 `✅ 初始化自检全面通过`

**自检通过后才算初始化完成。** 自检不通过不允许进入后续流程。
