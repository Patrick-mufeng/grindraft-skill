# 磨稿工作流 / Grindraft Workflow

> 7 阶段闭环：抓热点 → 聊选题 → 写初稿 → 去 AI 味 → 做排版 → 盲预测 → 发布复盘。

---

## 阶段 1：找热点

**触发**："抓热点" / "今天有什么可写的"

运行 `grindraft-trends`。从 aihot 拉 AI 圈精选资讯，去重 + 粗打分 + 写入选题池。

**输出**：candidates.md 新增候选选题。

---

## 阶段 2：找选题 / 确定选题

**触发**："找选题" / "聊选题"

运行 `grindraft-seed`。围绕你的真实经历、观察、兴趣深挖，收敛到一个具体角度。

**输出**：candidates.md 新增 tier1 选题 + 可选 draft 到 drafts/。

---

## 阶段 3：AI 写初稿

**触发**："写文章" / "出稿"

运行 `grindraft-write`。按 autonomy 设置（low/medium/high）出初稿。

**输出**：drafts/<date>_<id>_<short>.md。

---

## 阶段 4：去 AI 味

**触发**："去 AI 味" / "humanize"

运行 `grindraft-humanize`。四层自检（L1 硬规则 → L2 风格一致 → L3 内容质量 → L4 活人感）。

**输出**：覆盖 drafts/<id>.md（或另存到 scripts/<id>.md 表示用户已审）。

---

## 阶段 5：排版

**触发**："排版" / "转 HTML"

运行 `grindraft-format`。将 Markdown 终稿转为公众号兼容 HTML。

**输出**：output/<date>_<id>_<short>.html。

---

## 阶段 6：盲预测

**触发**："启动预测"

运行 `grindraft-predict`。对终稿打 7 维分 + bucket 押注 + 概率分布。**预测一旦写入即不可改。**

**输出**：predictions/<date>_<id>_<short>.md。

---

## 阶段 7：发布 + 复盘

**发布登记**："已发布" → `grindraft-publish` 更新元数据。

**复盘**："复盘"（发布 T+3 天后）→ `grindraft-retro` 收数据 + 对比预测 + 提炼观察 + 进化 rubric。

**输出**：predictions/<id>.md 的 ## 复盘 段 + rubric_notes.md 新观察。

---

## 辅助动作

- **状态看板**："状态" → `grindraft-status` 显示 buffer / 待复盘 / calibration 进度
- **推荐选题**："推荐选题" → `grindraft-recommend` 按 composite 排序推荐
- **受众画像**："我的读者是谁" → `grindraft-persona` 从评论数据派生
- **升级 rubric**："升级 rubric" → `grindraft-bump` 公式升级（需满足触发条件）
