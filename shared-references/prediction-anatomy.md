# 预测解剖 / Prediction Anatomy

> 一份合格的 grindraft 预测由 7 个组件构成。cold-start 期简化为 3 组件（7 维打分 + 方向押注 + 锚点 N/A），calibration 期解锁完整 7 组件。

## 完整结构总览

```markdown
# 预测：文章标题

**Article ID**: <12 位 hex hash — 对终稿正文做 sha256[:12]。**与 Script Hash 为同一值**
**Script Path**: scripts/<date>_<id>_<short>.md（优先）或 drafts/<date>_<id>_<short>.md
**Script Hash**: sha256[:12] — **与 Article ID 相同**，均为正文内容的 sha256 前 12 位

> ⚠️ Article ID 和 Script Hash 是**同一个值**，都是对正文内容做 sha256 取前 12 位。这不是两个独立字段——Script Hash 是技术名，Article ID 是业务名。手工构造的 ID（如 `mirafish0606`）无效。
**Calibration Samples**: N
**Confidence**: 🟢 中 / 🟡 低 / 🔴 极低 / ⚪ 无
**Prediction Basis**: pre_publish
**Scored By**: claude / claude+user_override
**BlindScored By**: subagent-v1 / main-claude-self / mixed
**BlindScore Disagreement**: [{dim, blind, self, delta, decided_as}]
**User Override**: [{field, original, final, reason}]

---

## 预测 v1

### 1. 7 维打分

| 维度 | 分 | 理由 |
|---|---|---|
| HK 标题钩力 | 1-5 | 一句话 |
| NR 叙事牵引力 | 1-5 | 一句话 |
| QA 金句锚点 | 1-5 | 一句话 |
| UT 实用密度 | 1-5 | 一句话 |
| DT 思辨激发度 | 1-5 | 一句话 |
| EP 情绪峰值 | 1-5 | 一句话 |
| SC 结构闭环 | 1-5 | 一句话 |
→ composite ≈ X.XX（加权）

### 2. Bucket 押注
**押注 bucket**：<S/A/B/C/D/E>
**中枢点估计**：<N> 阅读
**概率分布**：
| <E | D | C | B | A | S | >S |
|---|---|---|---|---|---|---|
| X% | X% | X% | X% | X% | X% | X% |

### 3. 加分因素
- [一句话：什么可能让数据超出中枢]

### 4. 减分因素
- [一句话：什么可能让数据低于中枢]

### 5. 锚点对比

| 对照 | composite | 实绩 bucket | 异同 |
|---|---|---|---|
| <历史文章 1> | X.XX | B | [一句话] |
| <历史文章 2> | X.XX | C | [一句话] |

如无锚点："锚点 N/A——这是第 N 篇预测，尚无同 bucket 锚点"

### 6. 反事实场景

- 如果 >A bucket → 意味着：[rubric 假设]
- 如果 B bucket → 基准线 ok
- 如果 <C bucket → 意味着：[rubric 假设被推翻]
- 如果 <D bucket → 意味着：[系统性问题]

### 7. 关键校准假设

- 本篇 vs [对照文章] 押 Nx
- 如果反过来 → [哪个 rubric 假设被推翻]
- 其他假设：[如有]

---

## 复盘

（待填——发布后 T+RETRO_WINDOW_DAYS 天跑 grindraft-retro）
```

## Cold-start 简化版（前 5 篇）

cold-start 期只要求前 3 个组件：
- 组件 1：7 维打分（完整）
- 组件 2：方向押注（"比上一篇明显好 / 差不多 / 可能不如"）
- 组件 3：锚点 N/A（显式说明为什么没有锚点）
- 组件 4-7：占位标 "cold-start 期跳过，第 5 篇复盘后解锁"

第 5 篇复盘后 → grindraft-status 主动提示解锁完整预测。

## Confidence 等级派生

| calibration_samples | Confidence | 预测精度预期 |
|---|---|---|
| 0 | 🔴 极低 | 纯先验猜测 |
| 1-4 | 🔴 极低 | 初具方向感 |
| 5-9 | 🟡 低 | 开始收敛 |
| 10-19 | 🟢 中 | ±50% 以内 |
| 20-29 | 🟢 中 | ±30% 以内 |
| 30+ | 🟣 较高 | ±20% 以内 |

> 这些数字是初始估计。实际精度由复盘跟踪。
