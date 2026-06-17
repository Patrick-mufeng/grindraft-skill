# CLAUDE.md

Grindraft (磨稿) — Claude Code plugin for WeChat long-form article writing with a calibrated prediction loop. Version: **1.0.0**.

## Architecture

17 independent skills covering the full content creation lifecycle:

| Phase | Skill | Description |
|-------|-------|-------------|
| Entry | `grindraft-init` | Onboarding & project scaffolding |
| Discovery | `grindraft-trends` | Fetch AI trends from aihot API |
| Ideation | `grindraft-seed` | Topic exploration through dialogue |
| Writing | `grindraft-write` | AI draft generation (3 autonomy levels) |
| Polish | `grindraft-humanize` | 4-layer AI-tells removal |
| Polish | `grindraft-illustrate` | Inline illustration generation (Xiaohei style) |
| Polish | `grindraft-cover` | Cover design from 40 templates |
| Polish | `grindraft-polish` | Title candidates + cover prompts |
| Format | `grindraft-format` | Markdown → WeChat-compatible HTML |
| Calibrate | `grindraft-predict` | Blind prediction (7-dim rubric) |
| Calibrate | `grindraft-publish` | Publish registration |
| Calibrate | `grindraft-retro` | Data recall & retrospective |
| Calibrate | `grindraft-persona` | Audience persona derivation |
| Calibrate | `grindraft-bump` | Rubric upgrade with cross-model audit |
| Utility | `grindraft-recommend` | Topic pool ranking |
| Utility | `grindraft-status` | Status dashboard |
| Internal | `grindraft-score-blind` | Isolated blind scoring sub-agent |
| Meta | `grindraft` | Router & global protocol |

Each skill contains `SKILL.md` (YAML front matter + docs). Shared resources live in `shared-references/`, `templates/`, `starter-rubrics/`, `adapters/`, `cover-templates/`.

## Skill Loading

Priority: project `.claude/skills/` → `$HOME/.claude/skills/` → system-level.

Install via Claude Code plugin marketplace or copy individual skill folders to your project's `.claude/skills/` directory.

## Three Inviolable Principles

1. **Blind prediction**: Predictions are written before seeing any actual data and are immutable once written
2. **Bump = full re-score**: Rubric upgrades require re-scoring all calibration samples; ≥4/5 rank consistency required
3. **Rubric is a workbench, not a museum**: Observations disproven by data get deleted — git history is the archive

Full protocols in `shared-references/`.

## User Project Layout

After `grindraft-init`, the user's project will have:

```
<user-project>/
├── rubric_notes.md              # Scoring rules (source of truth)
├── style_guide.md               # Personal style guide
├── WORKFLOW.md                  # Workflow documentation
├── STATUS.md                    # Dashboard
├── .grindraft-state.json        # Shared state
├── articles/                    # Per-article directories
│   └── {title}_{YYYY-MM-DD}/
│       ├── draft.md             # AI draft
│       ├── final.md             # User-polished final
│       ├── prediction.md        # Immutable prediction log
│       ├── output.html          # Formatted HTML
│       ├── output-preview.html  # Mobile preview HTML
│       ├── cover/               # Cover images
│       │   ├── preview.html
│       │   ├── cover-2x35.png
│       │   └── cover-1x1.png
│       ├── illustrations/       # Inline illustrations
│       │   ├── shot-list.md
│       │   └── 01-{theme}.png
│       └── retro/               # Retrospective raw data
│           └── report.md
├── plates/style-diffs/          # Edit history diffs
└── candidates.md                # Topic pool
```

## Date Rule (Highest Priority)

Always fetch the real current date via system command before any time-sensitive operation. Never use training data dates.

## Key Dependencies

- **Node.js 18+** (optional): Required for `grindraft-cover` PNG export (`puppeteer` + `canvas`). Cover HTML preview works without Node.js.
- **Python 3.9+** (optional): Required for `grindraft-illustrate` inline image generation (`requests`).
- **aihot API**: Public, no auth required. Used by `grindraft-trends` for trend fetching.

## Adding New Content Formats

- New format (Xiaohongshu, Douyin, etc.) → add `starter-rubrics/<format>.md`
- New trend source → add `adapters/trend-sources/<name>.md`
- Modify principles → edit `shared-references/<protocol>.md`
- Modify routing → edit `skills/grindraft/SKILL.md` routing table
