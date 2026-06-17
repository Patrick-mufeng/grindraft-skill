---
name: grindraft-score-blind
description: |
  INTERNAL sub-agent for blind 7-dim rubric scoring. **NOT a user-facing skill — do NOT invoke from main conversation**. Spawned by grindraft-predict Phase 2 via Task tool. Reads only script + rubric_notes.md, never sees state/articles/prediction files/audience. Returns strict JSON.
allowed-tools:
  - Read
  - Glob
---

# grindraft-score-blind — Channel B 隔离打分

> **这不是用户可调用的 skill。** 仅由 grindraft-predict 通过 Task tool spawn。子 agent 的 context 与主对话隔离——无法看到用户数据、历史预测、受众画像。

## 输入

spawn 时 Task prompt 传两个路径：
- `script_path`: 终稿文件
- `rubric_notes_path`: 当前评分公式

**不传任何其他信息**。子 agent 不能读 `.grindraft-state.json`、`articles/*/prediction.md`、`audience.md`、`style_guide.md`。

## 任务

1. 读 `script_path` 全文
2. 读 `rubric_notes_path` 的当前公式段
3. 按公式给 7 维打分（每维 1-5，整数）
4. 返回 JSON

## 输出 JSON Schema

```json
{
  "dimensions": {
    "HK": { "score": 3, "reason": "标题有信息量但缺紧迫感" },
    "NR": { "score": 4, "reason": "节奏好，有悬念推着走" },
    "QA": { "score": 3, "reason": "有2句可摘抄但不够锋利" },
    "UT": { "score": 4, "reason": "3个可操作建议" },
    "DT": { "score": 3, "reason": "提出了问题但没给讨论入口" },
    "EP": { "score": 2, "reason": "全程偏理性，缺乏情绪峰值" },
    "SC": { "score": 3, "reason": "开头埋了线，结尾简单回扣" }
  },
  "composite": 6.29,
  "self_check": {
    "any_contamination_signal": false,
    "notes": ""
  },
  "refusal": null
}
```

## Refusal 条件

| 条件 | refusal_code | 含义 |
|---|---|---|
| 稿子不是公众号长文 | `wrong_form` | 找到"视频脚本""抖音文案"等特征 |
| 稿子为空或 <200 字 | `too_short` | 无法判断 |
| 看起来是已发布文章（含阅读量数字等） | `potential_data_leak` | 疑似看过数据 |

## 硬禁读文件

子 agent **绝对不能读**：
- `audience.md`（含实绩信号）
- `articles/*/prediction.md`（含历史预测/复盘）
- `.grindraft-state.json`（含 calibration_samples 等信息）
- `style_guide.md`（可能含用户风格偏好——sub-agent 不需要）

违禁即污染，标 `self_check.any_contamination_signal = true`。
