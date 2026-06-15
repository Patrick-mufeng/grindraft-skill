# 磨稿工作流 / Grindraft Workflow

> 11 阶段闭环：找热点 → 聊选题 → 写初稿 → 去 AI 味（可选）→ 配图 → 设计封面 → 排版 → 盲预测 → 发布 → 复盘 → 进化。

---

## 阶段 1：找热点

**触发**："抓热点" / "今天有什么可写的"

运行 `grindraft-trends`。从 aihot 拉 AI 圈精选资讯，去重 + 粗打分 + 写入选题池。

**输出**：`candidates.md` 新增候选选题。

---

## 阶段 2：找选题 / 确定选题

**触发**："找选题" / "聊选题"

运行 `grindraft-seed`。围绕你的真实经历、观察、兴趣深挖，收敛到一个具体角度。

**输出**：`candidates.md` 新增 tier1 选题 + 可选初稿。

---

## 阶段 3：AI 写初稿

**触发**："写文章" / "出稿"

运行 `grindraft-write`。按 autonomy 设置（low/medium/high）出初稿，自动附带标题候选 + 简介。

**输出**：`articles/{标题}_{日期}/draft.md`

---

## 阶段 4：去 AI 味（可选）

**触发**："去 AI 味" / "humanize"（由用户主动调用）

运行 `grindraft-humanize`。四层自检（L1 硬规则 → L2 风格一致 → L3 内容质量 → L4 活人感）。跳过则用户手动改稿后直接保存为 final.md。

**输出**：`articles/{标题}_{日期}/final.md` + `plates/style-diffs/` 备份

---

## 阶段 5：配图（可选）

**触发**："配图" / "生成配图"

运行 `grindraft-illustrate`。读文章 → 出 shot list → 用户确认 → 逐张生成小黑怪诞手绘风格 16:9 插图。

**输出**：`articles/{标题}_{日期}/illustrations/{序号}-{主题}.png`

---

## 阶段 6：设计封面

**触发**："设计封面" / "封面"

运行 `grindraft-cover`。三维分析（情绪 × 领域 × IP）→ 从 40 套模板推荐 → 生成预览 HTML + 可选 PNG。

**输出**：`articles/{标题}_{日期}/cover/preview.html` + `cover-2x35.png` + `cover-1x1.png`

---

## 阶段 7：排版

**触发**："排版" / "转 HTML"

运行 `grindraft-format`。将 Markdown 终稿转为公众号兼容 HTML，自动设计主题色板，输出清洁版 + 预览版。

**输出**：`articles/{标题}_{日期}/output.html` + `output-preview.html`

---

## 阶段 8：盲预测

**触发**："启动预测"

运行 `grindraft-predict`。对终稿打 7 维分 + bucket 押注 + 概率分布。**预测一旦写入即不可改。**

**输出**：`articles/{标题}_{日期}/prediction.md`

---

## 阶段 9：发布登记

**触发**："已发布" + URL

运行 `grindraft-publish`。在 prediction.md header 追加发布时间和 URL，更新待复盘列表。

**输出**：`articles/{标题}_{日期}/prediction.md` header 更新

---

## 阶段 10：复盘

**触发**："复盘"（发布 T+3 天后）

运行 `grindraft-retro`。粘贴 3 个核心数据 → 派生比率 → 逐假设验证 ✅/❌ → 跨样本检测 → 提炼观察。

**输出**：`articles/{标题}_{日期}/retro/report.md` + `prediction.md` ## 复盘 段追加

---

## 阶段 11：进化

**触发**："升级 rubric"

运行 `grindraft-bump`。全量重打 + 跨模型审核 + 清理旧观察。满足触发条件时由复盘自动提示。

**输出**：`rubric_notes.md` 公式更新

---

## 辅助动作

- **风格沉淀**：每次排版/预测/去 AI 味时自动 diff 用户改写 → 去重写入 `style_guide.md`
- **状态看板**："状态" → `grindraft-status` 显示 buffer / 待复盘 / calibration 进度
- **推荐选题**："推荐选题" → `grindraft-recommend` 按 composite 排序推荐
- **受众画像**："我的读者是谁" → `grindraft-persona` 从评论数据派生
