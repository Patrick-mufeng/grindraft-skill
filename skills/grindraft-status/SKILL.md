---
name: grindraft-status
description: |
  磨稿状态看板。显示当前模式 / rubric 版本 / 校准进度 / 待复盘 / 选题池状态。自动获取当天日期计算复盘窗口。触发词："状态"/"今天干什么"/"进度怎么样"/"到哪了"。
allowed-tools:
  - Bash
  - Read
  - Glob
---

# grindraft-status — 状态看板

## Overview

读 `.grindraft-state.json` + `candidates.md` + `articles/` → 渲染状态看板 → 写入 `STATUS.md` 并展示。

## 看板模板

**⚠️ STATUS.md 文件必须以 `<!-- QUICK_STATUS: ... -->` 行开头。** 此行是 AI 快速读取的机器可解析锚点——`Read` 工具读文件头 3 行即可拿到全部核心指标。

```markdown
<!-- QUICK_STATUS: {mode} | {rubric_version} | {calibration_samples}样本 | {historical_samples}历史 | {pending_retros_count}待复盘 | 选题池{candidates_count}条 | 最后复盘{last_retro_date} | 最后发布{last_published_date} -->
# 磨稿状态看板 — YYYY-MM-DD

## 📊 基本状态

| 项目 | 值 |
|---|---|
| 模式 | cold-start (剩余 N 篇简化预测) / calibration |
| Rubric | v{N} {等权/加权}{从 N 篇历史文章拟合} |
| 校准样本 | N 篇（盲预测+复盘完成） |
| 历史文章 | N 篇（初始化导入） |
| Confidence | 🔴/🟡/🟢/🟣 |

## 📝 选题池

| 状态 | 数量 |
|---|---|
| 🟢 待写 (tier1) | N |
| 🟡 备选 (tier2) | N |
| ⚪ 暂存 (tier3) | N |

🟢 充裕 / 🟡 警戒 / 🔴 断更风险

## 📝 草稿进度

扫 `articles/` 下所有文件夹，判断每篇当前阶段：

| 文章 | 阶段 | 下一步 |
|---|---|---|
| mimo降价战 | 已发 ✅ | — |
| nvidia-polar | 已发 ✅ | — |
| image2开源 | 已预测 ✅ | 发URL |
| fde架构师 | 已排版 ✅ | 启动预测 |
| agent之争 | 封面 ✅ | 排版 |
| R1推理 | 配图 ✅ | 设计封面 |
| 开源出海 | 终稿 ✓ | 配图 |
| AI面试 | 去味完成 ✅ | 设计封面 |
| 长上下文 | 待改 | 改完→去味→配图→封面→排版→预测 |

阶段判断逻辑：
- draft.md 存在、final.md 不存在 → "待改"
- final.md 存在、cover/preview.html 不存在 → "已定稿，待封面"
- cover/preview.html 存在、illustrations/ 为空（无 shot-list.md）→ "封面已完成，待配图"（或跳过）
- cover/preview.html 存在、output.html 不存在 → "封面 ✅ 待排版"
- output.html 存在、prediction.md 不存在 → "已排版，待预测"
- prediction.md 存在、未发布 → "已预测，待发布"
- 已发布 → "已发"

## 📈 预测池

- 已预测、未发布：N 篇
- 已发布、待复盘：N 篇
- 已复盘：N 篇

## 🔍 待复盘

| # | 文章 | 预测 bucket | 发布天数 | 可复盘 |
|---|---|---|---|---|
| 1 | ... | B | 5 | ✅ |
| 2 | ... | A | 1 | ⏳ 还差 2 天 |

## 🎯 校准状况

- 连续同向偏差：N 次（高估/低估）
- 极端偏差次数：N
- 是否建议 bump：是/否

## 📊 基准指标

（数据来源：`benchmark.md`，与 `.grindraft-state.json` 的 `baseline_metrics` 同步。无历史数据则为 —。）

| 指标 | 基准值 | 样本数 |
|------|--------|--------|
| 平均阅读量 | {N} | {N} |
| 分享率 | {X.X}% | {N} |
| 收藏率 | {X.X}% | {N} |
| 留言率 | {X.X}% | {N} |

> 标注"—"的指标因数据不足无法计算。基准值随每次复盘自动更新。

## 🧹 维护提醒

- [ ] style_guide.md 最后更新于 X 天前（你改了 N 篇稿子但没更新 style_guide）
- [ ] rubric_notes.md 有 N 条单样本观察待验证
- [ ] candidates.md 有 N 条 >30 天未处理的选题（可能过时了）
```

## 维护提醒阈值

| 条件 | 提醒 |
|---|---|
| candidates 中 >30 天未处理 | "有 N 条选题可能过时了——考虑清理或重打分" |
| style_guide 最后更新 >10 天 + ≥3 篇改稿 | "你改了 N 篇稿子但没更新 style_guide——积累的 pattern 要丢了" |
| 连续同向偏差 ≥3 次 | "建议'升级 rubric'" |
| cold_start_remaining = 0 但 mode 未切换 | 自动切换到 calibration |
| 上次抓热点 >7 天 | "热点池可能过期了——考虑'抓热点'刷新" |

## 日期规则（最高优先级）

**每次渲染看板时，必须通过系统获取当天真实日期。** 禁止使用记忆中的日期、训练数据中的日期、或任何硬编码日期。

执行方式：在渲染看板前跑 `date` 命令获取当天日期（Windows 用 `date /t`，否则用 `date +%Y-%m-%d`）。用这个日期：
1. 写入看板标题
2. 计算每篇"发布天数"（今天 - published_at）
3. 判断"可复盘/还差 X 天"（发布天数 >= 3 则可复盘）
4. 判断"上次抓热点 X 天前"

## Key Rules

1. **日期必须从系统获取**——最高优先级，违反即出错
2. **只读不写**——status 不修改任何文件（除了更新 STATUS.md）
3. **维护提醒带可行动建议**——不只说"有问题"，说"试试这个命令"
4. **任何时候可调**——无副作用
