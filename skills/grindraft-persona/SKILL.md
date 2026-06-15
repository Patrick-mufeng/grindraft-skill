---
name: grindraft-persona
description: |
  从复盘评论数据派生/刷新公众号读者画像，写入 audience.md。和 rubric 平行的第二个派生物——rubric 答"怎么打分"，persona 答"谁在看"。触发词："构造受众画像"/"persona"/"我的读者是谁"/"看看我的受众画像"。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# grindraft-persona — 受众画像

从 `articles/*/prediction.md` 复盘段的留言数据，聚类出公众号真实读者画像，写入 `audience.md`。

## ⚠️ 污染隔离

`audience.md` 从复盘留言派生 = **含已发布作品的实绩信号**。因此：
- `audience.md` 在 grindraft-score-blind 的 hard refusal list 里
- persona 影响 grindraft-seed 和 grindraft-write 的**选题和写作方向**（creative direction），不影响 grindraft-predict 的**评分**（blind sub-agent 永远不读 audience.md）

## Workflow

### Phase 0: 收集数据

1. Glob `articles/*/prediction.md`，读每个文件的 `## 复盘` 段
2. 抽取每篇的 top 留言（带赞数）+ 实绩数据
3. 至少有 3 篇有留言数据的复盘 → 可以首次派生画像

### Phase 1: 数据量判定 → Confidence

| 复盘数（有留言） | Confidence | 行为 |
|---|---|---|
| 0-2 | 🔴 极低 | 提示"至少 3 篇有留言数据才能派生画像" |
| 3-6 | 🟡 低 | 可首次派生，标注低置信度 |
| 7-14 | 🟢 中 | 画像较可靠 |
| 15+ | 🟣 较高 | 画像可进选题决策 |

### Phase 2: 留言聚类

将留言分为以下几类：

| 类型 | 含义 | 信号价值 |
|---|---|---|
| **自我认同** | "我也是""对对对" | 这个读者群有共性痛点/经历 |
| **情绪寄存** | "看哭了""气得我" | 情绪峰值 EP 被验证 |
| **反驳/质疑** | "但我觉得...""有一点不同意" | 思辨激发度 DT 被验证 |
| **补充讨论** | "还有一点...""其实..." | 读者有专业知识，是高价值信号 |
| **行动转化** | "已经转发了""马上去试" | 分享/收藏的动因 |
| **离题/噪声** | "好文""赞" | 低信号 |

### Phase 3: Persona 输出

写入 `audience.md`：

```markdown
## 当前 Confidence：🟡 低（基于 N 篇复盘数据）

## 读者群像

- **核心年龄/职业推断**：...
- **共同痛点**：...
- **阅读动机**："为什么关注这个号？"
- **转发动机**："什么让他们转发？"
- **留言风格**：...

## 评论关键词聚类
（Phase 2 的比例分布 + 代表性留言）

## Persona × Rubric 交叉检验
- rubric HK 高估？读者自我认同留言多→可能是标题过度承诺
- rubric NR 低估？留言里"一口气读完"高频出现
```

## Key Rules

1. **只读复盘段**——不碰预测段
2. **每条特征至少 3 条留言证据**——否则标"假设特征（待验证）"
3. **不因为 persona 改 rubric**——那是 grindraft-bump 的事
