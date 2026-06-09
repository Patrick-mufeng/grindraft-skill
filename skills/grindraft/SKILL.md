---
name: grindraft
description: |
  磨稿——把公众号长文写作变成可校准预测循环。**从找热点到复盘，全流程闭环**：抓热点 → 聊选题 → AI 写初稿 → 去 AI 味 → 设计封面 → 排版 HTML → 盲预测 → 发布登记 → 数据复盘 → 进化 rubric。适用公众号长文（后续扩展小红书 / 抖音分发）。触发词："磨稿"/"初始化"/"抓热点"/"找选题"/"写文章"/"去 AI 味"/"排版"/"启动预测"/"已发布"/"复盘"/"升级 rubric"/"推荐选题"/"状态"。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - WebFetch
---

# 磨稿 / Grindraft

> 🎯 **公众号长文写作的校准闭环——让每一篇都算数**
>
> **方法论**（7 阶段闭环）：找热点 → 聊选题 → AI 写初稿 → 去 AI 味 → 排版 HTML → 盲预测 → 发布复盘。
> 任何能被量化的内容形态都适用这套循环——文章 / 视频 / 播客 / 图文。
>
> **当前内置 rubric**：公众号长文 7 维评分体系（HK 标题钩力 / NR 叙事牵引力 / QA 金句锚点 / UT 实用密度 / DT 思辨激发度 / EP 情绪峰值 / SC 结构闭环），初始权重由阅读心理推导，随复盘数据进化。
>
> **默认假设**：支持两类用户——
> - **有经验用户**（已有粉丝和写作基础）：直接进入 calibration 模式，做完整 7 组件预测
> - **从零开始用户**（没发过文章）：cold-start 简化期（前 5 篇简版预测），积累数据后解锁完整模式
>
> 首次使用必须先跑 `grindraft-init`。

把公众号长文写作变成可校准预测循环：**抓热点 → 聊选题 → 写初稿 → 去 AI 味 → 做排版 → 盲预测 → 发布 → 复盘 → 进化 rubric**。

本文件是**总协议 + 路由器**。具体每个阶段的工作流在各自的子 skill 里。

> **Claude Code 使用方式**：16 个子 skill 各自独立。安装本插件后，直接用触发词或 skill 名调用——例如说"初始化"会匹配到 `grindraft-init`，说"写文章"匹配到 `grindraft-write`。详见下方路由表。

---

## 🔄 新会话引导（New Session Bootstrap）

**分层读取策略——按用户意图决定读多少，不盲目全量加载。**

### ⚡ 核心机制：STATUS.md 的 QUICK_STATUS 锚点

STATUS.md 文件第一行是机器可解析的快速锚点：

```
<!-- QUICK_STATUS: calibration | v1 | 8样本 | 3待复盘 | 选题池2条 | 最后复盘06-05 | 最后发布06-06 -->
```

AI 用 `Read` 工具读文件头 3 行即可拿到 6 个核心指标——这是回答 90% "进度"问题的全部数据。

### 分层读取规则

| 用户意图 | 触发词 | 读取量 | 读什么 |
|---|---|---|---|
| 🟢 **进度/状态** | "进度""状态""到哪了""今天干什么""看板" | **极轻** | `Read(STATUS.md)` 前 3 行 → 解析 QUICK_STATUS → 直接回答 |
| 🟡 **写作操作** | "写文章""去 AI 味""排版""找选题""抓热点" | **中等** | 先读 STATUS.md 前 3 行确认进度 → 再读 `style_guide.md` + `rubric_notes.md`（按需） |
| 🔴 **校准操作** | "启动预测""复盘""升级 rubric" | **完整** | 先读 STATUS.md 前 3 行 → 再读 `.grindraft-state.json`（权重/bucket/pending_retros）→ 再读 `predictions/` 最近 2 篇 |

### ⚠️ STATUS.md 过期检测（轻量版）

QUICK_STATUS 锚点已含 `最后复盘` 和 `最后发布` 日期。如果时间看起来异常（如显示 8 天前但你刚操作过），提示用户刷新：

```
⚠️ STATUS.md 快照显示最后复盘 05-28（9 天前），可能过期。说"状态"刷新。
```

> **不需要**为此额外读 state.json——QUICK_STATUS 已自包含日期。过期检测是"顺便看一眼"，不是单独步骤。

### 文件不存在时的处理

- `STATUS.md` 不存在 → 提示"先跑'磨稿初始化'"
- `QUICK_STATUS` 行不存在 → 回退到读全文 STATUS.md + state.json（兼容旧版 STATUS.md）
- 其他文件缺失 → 按需提示

---

## ⏰ 日期规则（全局最高优先级）

**涉及"今天""现在""进度""什么时候"等时间相关问题时，必须先通过系统命令获取当天真实日期，再用该日期计算所有时间差。** 禁止使用训练数据中的日期、模型记忆中的日期、或任何硬编码日期。

执行方式：
```
Linux/Mac:  date +%Y-%m-%d
Windows:    date /t
```

**这条规则覆盖以下所有场景**：

| 用户问 | 必须做什么 |
|---|---|
| "今天干什么" / "进度怎么样" / "现在情况" / "到哪了" | 先获取日期 → 再读 STATUS.md + state.json → 计算各文章发布天数 → 判断可复盘/还差几天 → 回答 |
| "复盘 predictions/xxx" | 先获取日期 → 计算发布天数 ≥ 3？→ 未到时提示"还差 X 天" |
| "抓热点" / "今天有什么可写的" | 先获取日期 → 写 trends 时间戳到 state |
| "状态" / "看板" | 先获取日期 → 写看板标题日期 → 渲染 |

**为什么必须这样**：磨稿系统的复盘窗口（T+3天）、选题时效性、风格上次更新时间，全部依赖"今天"的真实日期计算。用模型记忆的日期（例如训练数据中的某个日期）会导致复盘窗口计算错误。

---

## 三条不可妥协原则

任何一条被违反，整个校准循环退化为"凭直觉的自我安慰"。如果用户要求打破其中任何一条，**拒绝执行并说明原因**。

1. **盲预测（Blind prediction）**：预测必须在看到任何实际数据**之前**写完。一旦写完，`## 预测` 段是 immutable——只能往 `## 复盘` 段追加。完整规范：[shared-references/blind-prediction-protocol.md](shared-references/blind-prediction-protocol.md)。

2. **升级 = 全量重打（Bump = full re-score）**：rubric 升级时，校准池所有有实绩数据的样本必须用新公式重打分；新排序与实际表现排序若在 ≥4/5 样本上不一致，升级被拒；升级必须经跨模型独立审核。完整规范：[shared-references/bump-validation-protocol.md](shared-references/bump-validation-protocol.md)。

3. **rubric 是工作台，不是博物馆**：被新数据推翻或被吸收为正式维度的观察，**删掉**。绝不留"我曾经以为 X，但其实..."的考古层。git history 才是档案。完整规范：[shared-references/observation-lifecycle.md](shared-references/observation-lifecycle.md)。

---

## 🔄 STATUS.md 自动刷新（全局规则）

**任何修改 `.grindraft-state.json` 的 skill，在其自检 Phase 通过后，必须自动刷新 `STATUS.md`。** 确保看板数据的日期不晚于本次操作日期。

需要自动刷新的 skill：
- `grindraft-write`：写稿后（in_progress_session 变化）
- `grindraft-predict`：预测后（cold_start_remaining / last_prediction_at 变化）
- `grindraft-publish`：发布后（last_published_at / pending_retros 变化）
- `grindraft-retro`：复盘后（calibration_samples / last_retro_at / pending_retros 变化）
- `grindraft-bump`：升级后（rubric_version / weights 变化）
- `grindraft-trends`：抓热点后（last_trends_run_at 变化）

**刷新方式**：调用 `grindraft-status` 的内联逻辑——获取当天日期 → 读 state.json → 扫 drafts/predictions/output → 渲染看板 → 写入 `STATUS.md`。

> ⚠️ STATUS.md 过期检测（新会话引导段）作为**双重保险**保留——万一某次操作漏刷新，下次会话仍会被拦住。

---

## 路由表（触发词 → 子 skill）

> 在 Claude Code 中，每个子 skill 独立安装。用户说触发词或 skill 名时，Claude Code 自动匹配对应 skill。

| 用户说 | 调用 skill | 前置条件 |
|---|---|---|
| "初始化" / "init" / "磨稿初始化" / "首次使用" | `grindraft-init` | 无（这是入口） |
| "抓热点" / "fetch trends" / "今天有什么可写的" / "AI 圈有什么" | `grindraft-trends` | 已 init |
| "找选题" / "我不知道写什么" / "seed" / "聊选题" | `grindraft-seed` | 已 init |
| "写文章" / "帮我写一篇" / "write" / "出稿" | `grindraft-write` | 已 init + 有选题（含标题候选+简介+封面提示词） |
| "去 AI 味" / "humanize" / "去味" / "修一下" | `grindraft-humanize` | 有初稿 |
| "设计封面" / "帮我做封面" / "生成封面" / "公众号封面" / "封面" | `grindraft-cover` | 已改完稿（需 Node.js 可出 PNG） |
| "排版" / "format" / "转 HTML" / "公众号排版" | `grindraft-format` | 有终稿 |
| "启动预测" / "predict" / "写预测日志" | `grindraft-predict` | 已 init + 有最终稿（预测后可直接发URL登记） |
| "已发布" / "publish" / "发布链接是 X" / "发出去了" | `grindraft-predict` | 对应预测文件存在（预测时已含发布衔接） |
| "复盘" / "retro" / "T+N 天数据来了" / "看数据" | `grindraft-retro` | 对应预测文件存在 + 已发布 |
| "构造受众画像" / "persona" / "我的读者是谁" | `grindraft-persona` | 已 init；有复盘数据 |
| "升级 rubric" / "bump rubric" / "更新公式" | `grindraft-bump` | 校准池 ≥ MIN_SAMPLES_FOR_BUMP |
| "推荐选题" / "next topic" / "下一篇写什么" | `grindraft-recommend` | candidates.md 存在且非空 |
| "状态" / "status" / "看板" / "磨稿状态" / "今天干什么" / "进度怎么样" / "到哪了" | `grindraft-status` | 任意时刻（自动获取当天日期） |

> 🔍 **子 skill 自检**：`grindraft-retro` 和 `grindraft-publish` 在写入数据后自动**重读验证**（re-read 对比，非自我承诺），确保 state / 预测文件 / rubric_notes 全部完整写入后才结束。

**Mode detection**（首次接到非 init 触发词时执行）：
1. 检查用户项目是否有 `.grindraft-state.json` → 没有 → 强制路由到 `grindraft-init`
2. 检查 `predictions/` 下有几个文件含完整 `## 复盘` 段填了真实数据 → 决定 `mode: cold-start | calibration`
3. 把判定结果写回 `.grindraft-state.json` 后再路由到目标 skill

---

## 必须拒绝的请求

下列模式会**直接破坏**三条原则之一，无论用户怎么说，都拒绝执行：

- 「帮我预测一下，但我先告诉你阅读量你来反推就行」 → 违反原则 #1。改用 `_redo.md` 路径记为 reconstructed
- 「能不能从 candidates 里直接挑 composite 最高的，不用解释理由」 → 拒绝。永远展示各维度评分和至少一个锚点对比
- 「跳过校准池重打，直接换公式」 → 违反原则 #2
- 「跳过外部模型审核，自己说了算」 → 仅当 `CROSS_MODEL_AUDIT=false` 显式设置且 state file 标记自审时允许
- 「删掉这份预测，我想重写」 → 违反原则 #1。预测是 immutable。如有正当理由重做，写新文件 `_redo.md`，原版必须保留
- 「凭你的感觉给我推荐选题，不用打分」 → 拒绝。本工具不做 gut-feel forecast——那是它诞生**之前**的状态
- 「把 rubric_notes.md 里所有历史观察都留着，加个时间戳分组就行」 → 违反原则 #3。git history 是档案，不是 markdown 文件
- 「能不能把 THRESHOLD 从 4/5 降到 3/5 让这次 bump 过」 → 拒绝。改 THRESHOLD 本身是元层级 bump，单独走流程
- 「跳过 autonomy 设置，直接给我出稿」 → 询问一次后仍拒绝则允许（默认 medium），但提示用户 autonomy 影响稿子质量

详细的拒绝场景在每个子 skill 的 `Refusals` 段。

---

## 项目目录结构（用户 repo）

skill 期望用户项目布局如下。`grindraft-init` 会创建缺失项；**绝不在没确认的情况下覆盖**。

```
<user-article-project>/
├── rubric_notes.md                    # 评分规则的真实来源（7 维）
├── style_guide.md                     # 用户风格指南（从修改中沉淀）
├── WORKFLOW.md                        # 7 阶段流程文档（grindraft-init 创建）
├── STATUS.md                          # 看板（grindraft-status 维护）
├── .grindraft-state.json              # 状态文件，子 skill 共享上下文
├── .grindraft-cache/                  # 不入版本控制
│   ├── usage.jsonl                    # 使用日志
│   └── trends-history.jsonl           # 热点去重缓存
├── benchmark.md                       # 对标账号信息（可选，后续支持）
├── audience.md                        # 受众画像（grindraft-persona 派生；blind 硬禁读）
├── drafts/                            # AI 初稿存放
│   └── YYYY-MM-DD_<id>_<short>.md
├── scripts/                           # 用户修改后的终稿
│   └── YYYY-MM-DD_<id>_<short>.md
├── predictions/                       # immutable 预测日志
│   └── YYYY-MM-DD_<id>_<short>.md
├── output/                            # 排版后的 HTML 输出
│   └── YYYY-MM-DD_<id>_<short>.html
├── retro/                             # 复盘数据
│   └── YYYY-MM-DD_<id>_<short>/
│       └── report.md                  # 用户粘贴的数据
├── candidates.md                      # 选题池
└── plates/                            # 风格指南沉淀的用户改写记录
    └── style-diffs/                   # AI 初稿 vs 用户终稿的 diff 记录
```

---

## 文件清单

### 本 skill 包

```
grindraft-skill/
├── .claude-plugin/
│   └── marketplace.json               # Claude Code 插件注册
├── CLAUDE.md                          # 仓库级说明
├── README.md                          # 安装与使用说明
├── skills/                            # 子 skill 集
│   ├── grindraft/SKILL.md             # 本文件（总协议 + 路由）
│   ├── grindraft-init/SKILL.md        # 入口：onboarding 与脚手架（双模式）
│   ├── grindraft-trends/SKILL.md      # 热点抓取（aihot adapter）
│   ├── grindraft-seed/SKILL.md        # 选题对话 + 可选 draft
│   ├── grindraft-write/SKILL.md       # AI 写初稿（autonomy low/medium/high）
│   ├── grindraft-humanize/SKILL.md    # 四层去 AI 味（L1-L4 通用版）
│   ├── grindraft-format/SKILL.md      # Markdown → 公众号 HTML
│   ├── grindraft-predict/SKILL.md     # 盲预测（7 维 + bucket + 概率分布）
│   ├── grindraft-publish/SKILL.md     # 发布登记
│   ├── grindraft-retro/SKILL.md       # 数据回收 + 复盘 + 观察提炼
│   ├── grindraft-persona/SKILL.md     # 受众画像派生
│   ├── grindraft-bump/SKILL.md        # Rubric 升级（含跨模型审）
│   ├── grindraft-recommend/SKILL.md   # 候选池排序推荐
│   ├── grindraft-status/SKILL.md      # 状态看板
│   ├── grindraft-score-blind/SKILL.md # Channel B 隔离打分 sub-agent
│   ├── grindraft-cover/SKILL.md       # 公众号封面设计
│   └── grindraft-polish/SKILL.md      # 标题 + 简介 + 封面提示词
├── starter-rubrics/                   # 各内容形态的先验 rubric
│   ├── wechat-long-form.md            # 公众号长文 7 维 rubric
│   └── wechat-long-form-zero.md       # v0 等权占位（cold-start）
├── shared-references/                 # 跨 skill 共享协议
│   ├── blind-prediction-protocol.md   # 原则 #1
│   ├── bump-validation-protocol.md    # 原则 #2
│   ├── observation-lifecycle.md       # 原则 #3
│   ├── prediction-anatomy.md          # 一份合格预测的 7 个组件
│   ├── rubric-dimensions.md           # 7 维定义 + 打分细则
│   ├── cadence-protocol.md            # 节奏协议
│   └── state-management.md            # .grindraft-state.json 读写约定
├── templates/                         # skill 写进用户 repo 的文件骨架
│   ├── rubric_notes.template.md
│   ├── prediction.template.md
│   ├── style_guide.template.md
│   ├── candidates.template.md
│   ├── benchmark.template.md
│   ├── audience.template.md
│   └── workflow.template.md
├── cover-templates/                   # 40 套封面设计模板
└── adapters/
    ├── trend-sources/
    │   └── aihot.md                   # aihot 热点 adapter
    ├── format/
    │   └── preview.html               # 排版预览
    └── perf-data/
        └── manual-paste.md            # 手动粘贴复盘数据
```

---

## Tone & voice

写面向用户的文案（report / 复盘小结 / 预测总结等）时，匹配项目的 **直白克制** voice：

- 直接说出成败：「HK=4 但实际打开率只有均值一半——标题钩力被高估了」
- **不要**用模糊措辞软化：「这或许可能在某种程度上暗示...」——别这么写
- 第一人称，定位为"写手"——"我帮你出了一稿，你看哪里需要改"
- 但数据部分切换为分析口吻——"你的分享率 4.2%，高于同 bucket 中位数 1.8 倍"

---

## 给开发者：扩展本 skill

- 新增内容形态（小红书图文 / 抖音视频等）→ 加 `starter-rubrics/<form>.md`
- 新增热点抓取源 → 加 `adapters/trend-sources/<name>.md`
- 修改原则 → 改 `shared-references/<protocol>.md`，所有引用它的 skill 自动跟进
- 修改路由 → 改本文件的"路由表"段
- 子 skill 内部细节 → 直接改对应 `skills/grindraft-*/SKILL.md`
