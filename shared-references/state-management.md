# 状态管理 / State Management

> `.grindraft-state.json` 的 schema、读写约定、各子 skill 的读写权限。

## 文件位置

```
<user-project>/.grindraft-state.json
```

## Schema

```json
{
  "schema_version": 1,
  "project_name": "string",
  "created_at": "ISO-8601",
  "mode": "cold-start | calibration",
  "content_form": "wechat-long-form",
  "rubric_version": "v0",

  "user_profile": {
    "follower_count": 4000,
    "target_frequency": "weekly-2",
    "style_migration": false,
    "old_style_desc": "",
    "new_style_desc": ""
  },

  "calibration_samples": 0,
  "cold_start_remaining": 5,

  "rubric": {
    "dimensions": ["HK", "NR", "QA", "UT", "DT", "EP", "SC"],
    "weights": { "HK": 2.0, "NR": 2.0, "QA": 1.5, "UT": 1.5, "DT": 1.0, "EP": 1.0, "SC": 0.5 },
    "bucket_boundaries": { "S": 50000, "A": 10000, "B": 3000, "C": 1000, "D": 300 }
  },

  "in_progress_session": {
    "type": "prediction | write | null",
    "file": "scripts/<id>.md",
    "started_at": "ISO"
  },

  "last_trends_run_at": "ISO",
  "last_prediction_at": "ISO",
  "last_published_at": "ISO",
  "last_retro_at": "ISO",
  "last_prediction_self_scored": false,
  "last_self_scored_at": null,

  "pending_retros": ["predictions/<id>.md"],
  "consecutive_directional_errors": [],
  "enabled_trend_sources": ["aihot"],

  "style_guide": {
    "version": 1,
    "last_updated": "ISO",
    "patterns_learned": 0
  }
}
```

## 各子 skill 读写权限

| 子 skill | 读哪些字段 | 写哪些字段 |
|---|---|---|
| grindraft-init | 全部 | 全部（初始化） |
| grindraft-trends | enabled_trend_sources | last_trends_run_at |
| grindraft-seed | mode, rubric_version, calibration_samples | —（写 candidates.md 和 drafts/） |
| grindraft-write | mode, user_profile | in_progress_session |
| grindraft-humanize | style_guide | style_guide（如有新 pattern） |
| grindraft-format | — | —（只读稿子，不碰 state） |
| grindraft-predict | rubric, calibration_samples, mode | in_progress_session, last_prediction_at |
| grindraft-publish | in_progress_session | last_published_at, pending_retros |
| grindraft-retro | rubric, consecutive_directional_errors | calibration_samples, last_retro_at, consecutive_directional_errors, pending_retros |
| grindraft-persona | calibration_samples | —（写 audience.md） |
| grindraft-bump | rubric, calibration_samples | rubric, rubric_version |
| grindraft-recommend | rubric | —（读 candidates.md） |
| grindraft-status | 全部（只读） | —（写 STATUS.md） |
| grindraft-score-blind | rubric | —（只读 rubric_notes.md + script） |

## Confidence 派生表

从 `calibration_samples` 派生 confidence 等级（见 prediction-anatomy.md）：

```
0     → 🔴 极低
1-4   → 🔴 极低
5-9   → 🟡 低
10-19 → 🟢 中
20-29 → 🟢 中
30+   → 🟣 较高
```

## Mode 切换

```
calibration_samples < 5 → mode = "cold-start"
calibration_samples >= 5 → mode = "calibration"
```

切换时 grindraft-status 主动提示用户"完整预测模式已解锁"。
