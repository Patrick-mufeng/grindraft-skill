# 磨稿 / Grindraft

> Claude Code 插件 · 18 个子 skill · 把公众号写作变成可进化的校准系统

[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blue)](https://claude.ai)

---

## 一句话

**不是帮你写文章，是帮你建立一套"每写一篇，下一篇就更准"的写作系统。**

---

## 它和普通 AI 写作工具有什么区别？

普通 AI 写作：你让它写 → 它写 → 写完了。下次再写，它不记得你上一篇阅读量 3000 还是 300。

磨稿：**每一篇文章都变成数据，数据反过来校准你的写作判断。**

```
写 → 预测 → 发布 → 复盘 → 进化
  ↓                        ↑
  └──── 更准的评分系统 ────┘
```

---

## 系统全貌

```
┌─────────────────────────────────────────────────────────────────┐
│ 第一阶段：发现 + 选题                                              │
│   "抓热点" → ①trends → "找选题" → ②seed                          │
│                       ↓                                            │
│                   candidates.md（选题池）                           │
├─────────────────────────────────────────────────────────────────┤
│ 第二阶段：写作 + 打磨                                              │
│   "写文章" → ③write → "去AI味" → ④humanize → "配图" → ⑤illustrate  │
│                       ↓                     ↓                        │
│                  draft.md              final.md                      │
│                       ↓                                              │
│   "设计封面" → ⑥cover → "打磨标题" → ⑥polish（可选）                 │
│                       ↓                                              │
│              cover/ + 标题候选                                        │
├─────────────────────────────────────────────────────────────────┤
│ 第三阶段：排版                                                      │
│   "排版" → ⑦format                                                  │
│                       ↓                                              │
│          output.html + output-preview.html                           │
├─────────────────────────────────────────────────────────────────┤
│ 第四阶段：校准闭环                                                  │
│   "启动预测" → ⑧predict（不可修改）                                   │
│   "已发布"   → ⑨publish（登记URL）                                    │
│   T+3 "复盘"  → ⑩retro                                              │
│   "升级rubric" → ⑪bump（全量重打+跨模型审核）                          │
└─────────────────────────────────────────────────────────────────┘
```


## 路由表（触发词 → 子 skill）

| 用户说 | 调用 skill | 功能一句话 | 前置条件 |
|--------|-----------|-----------|---------|
| "初始化" / "磨稿初始化" | `grindraft-init` | 首次搭项目骨架，判定 cold-start/calibration 模式 | 无（入口） |
| "抓热点" / "今天有什么可写的" | `grindraft-trends` | 从 aihot API 抓 AI 圈精选资讯，写入选题池 | 已 init |
| "找选题" / "聊选题" | `grindraft-seed` | 深度对话收敛到一个具体写作角度 | 已 init |
| "写文章" / "帮我写一篇" | `grindraft-write` | AI 出初稿（3 种参与度 low/medium/high） | 有选题 |
| "去 AI 味" / "修一下" | `grindraft-humanize` | 四层去 AI 味（L1 硬规则→L2 逻辑→L3 节奏→L4 活人感） | 有初稿 |
| "配图" / "生成配图" | `grindraft-illustrate` | 小霓赛博风格正文插图，API 生图 + shot-list | final.md 存在 |
| "设计封面" / "封面" | `grindraft-cover` | 读文章自动匹配 40 套模板，生成预览 HTML + PNG | 已改完稿 |
| "打磨标题" / "起标题" | `grindraft-polish` | 生成标题候选 + 简介 + 封面提示词 | 已改完稿 |
| "排版" / "转 HTML" | `grindraft-format` | AI 设计主题色板，Markdown → 公众号兼容 HTML | 有终稿 |
| "启动预测" / "predict" | `grindraft-predict` | 7 维盲打分 + bucket 押注，写完即锁定（不可修改） | 已排版 |
| "已发布" / "发布链接是..." | `grindraft-publish` | 登记 URL，更新状态 | 已预测 |
| "复盘" | `grindraft-retro` | T+3 数据回收 → 逐条验证预测假设 → 提炼观察 | 已发布 ≥3 天 |
| "状态" / "看板" | `grindraft-status` | 渲染看板 → STATUS.md + kanban.html + kanban-data.js | 已 init |
| "推荐选题" | `grindraft-recommend` | 按 rubric 排序推荐选题池 | 有选题池 |
| "我的读者是谁" | `grindraft-persona` | 从复盘评论数据派生读者画像 | 有复盘数据 |
| "升级 rubric" | `grindraft-bump` | 全量重打分 + 跨模型独立审核 → 更新权重 | 校准样本 ≥5 篇 |


## 18 个子 skill 清单

| 类型 | Skill | 文件位置 |
|------|-------|---------|
| 🧭 路由器 | `grindraft` | `skills/grindraft/SKILL.md` |
| 🚀 入口 | `grindraft-init` | `skills/grindraft-init/SKILL.md` |
| 🔥 发现 | `grindraft-trends` | `skills/grindraft-trends/SKILL.md` |
| 💡 选题 | `grindraft-seed` | `skills/grindraft-seed/SKILL.md` |
| ✍️ 写作 | `grindraft-write` | `skills/grindraft-write/SKILL.md` |
| 🧹 去味 | `grindraft-humanize` | `skills/grindraft-humanize/SKILL.md` |
| 🎨 配图 | `grindraft-illustrate` | `skills/grindraft-illustrate/SKILL.md` |
| 🎴 封面 | `grindraft-cover` | `skills/grindraft-cover/SKILL.md` |
| ✨ 打磨标题 | `grindraft-polish` | `skills/grindraft-polish/SKILL.md` |
| 📻 排版 | `grindraft-format` | `skills/grindraft-format/SKILL.md` |
| 🎯 预测 | `grindraft-predict` | `skills/grindraft-predict/SKILL.md` |
| 📮 发布 | `grindraft-publish` | `skills/grindraft-publish/SKILL.md` |
| 📊 复盘 | `grindraft-retro` | `skills/grindraft-retro/SKILL.md` |
| 👤 受众画像 | `grindraft-persona` | `skills/grindraft-persona/SKILL.md` |
| ⬆️ 升级 rubric | `grindraft-bump` | `skills/grindraft-bump/SKILL.md` |
| 💡 推荐选题 | `grindraft-recommend` | `skills/grindraft-recommend/SKILL.md` |
| 📋 状态看板 | `grindraft-status` | `skills/grindraft-status/SKILL.md` |
| 🔒 盲打分 | `grindraft-score-blind` | `skills/grindraft-score-blind/SKILL.md` |


## 7 维评分体系

| 维度 | 测什么 | 公众号数据验证 |
|------|--------|---------------|
| **HK** 标题钩力 | 标题+封面能不能让人点进来 | 阅读量 |
| **NR** 叙事牵引力 | 有没有一路看到底的欲望 | 阅读完成率 |
| **QA** 金句锚点 | 有没有值得划线分享的句子 | 划线数 / 在看数 |
| **UT** 实用密度 | 看完有没有"以后用得上" | 收藏率 |
| **DT** 思辨激发度 | 有没有让人想讨论的问题 | 留言率 |
| **EP** 情绪峰值 | 有没有"卧槽"或鼻子一酸的瞬间 | 分享率 |
| **SC** 结构闭环 | 开头埋的线结尾有没有收 | 读完后的完整感 |

每维 1-5 分，加权算 composite 对应阅读量 bucket（S/A/B/C/D/E）。

---

## 用户使用流程（完整版）

### 首次使用
```
说"磨稿初始化" → 系统创建项目骨架（STATUS.md / candidates.md / style_guide.md 等）
```

### 写一篇文章的完整流程
```
① "抓热点"          → 获取今日 AI 圈资讯到选题池
② "找选题"          → 对话确定一个写作角度
③ "写文章"          → AI 出初稿
④ "去 AI 味"        → 四层质检，改出终稿
⑤ "配图"            → 生成正文插图（可选）
⑥ "设计封面"        → 自动匹配模板出封面
⑦ "排版"            → Markdown 转公众号 HTML
⑧ "启动预测"        → 7 维盲打分（锁死不可改）
⑨ 发布文章到公众号
⑩ "已发布，链接是..." → 登记 URL
⑪ 3 天后"复盘"       → 贴数据 → 验证预测 → 提炼观察
⑫ 数据积累后"升级 rubric" → 全量重打分（可选）
```

### 日常查看
```
"状态" / "看板" → 查看全盘进度、待办、维护提醒
"推荐选题"     → 获取下一篇文章推荐
"我的读者是谁" → 查看读者画像
```


## 安装

### 方式一：Claude Code 插件市场
```bash
claude plugin install github.com/Patrick-mufeng/grindraft-skill
```

### 方式二：手动复制
将需要的 skill 文件夹复制到你的项目目录：
```bash
cp -r skills/grindraft-* <your-project>/.claude/skills/
```

安装后在 Claude Code 中说 **"磨稿初始化"** 即可开始。

---

## 看板（Kanban Dashboard）

### 看板是什么
每次说"状态"时，系统会：
1. 读取当前所有文章的状态数据
2. 生成一个 HTML 看板页面
3. 用浏览器双击就能查看

### 看板里有啥
- **基本状态**：模式（cold-start / calibration）、rubric 版本、置信度
- **选题池**：tier1/2/3 各有多少候选
- **草稿流水线**：每篇文章当前在哪个阶段（待改/配图中/已排版/已预测...）
- **预测池**：已预测未发布、待复盘、已复盘的数量
- **待复盘表格**：哪些文章可以复盘了、还差几天
- **校准状况**：连续同向偏差次数、是否建议升级 rubric
- **基准指标**：平均阅读量/分享率/收藏率/留言率
- **维护提醒**：style_guide 过期、选题过时、热点池过期

### 数据准确性能保证吗？
**能。三层保障：**

1. **自动刷新**：每次修改状态的操作（写稿/预测/发布/复盘/升级/抓热点）完成后，自动刷新 STATUS.md
2. **硬校验**：每次新会话读 STATUS.md 时，用系统日期与 QUICK_STATUS 锚点中的日期做机械比较，过期则提醒刷新
3. **系统日期**：所有时间计算都从系统命令获取当天日期，禁止使用模型记忆


## 三条不可妥协原则

1. **盲预测**：预测必须在看到任何实际数据之前写完，写完即锁定，不可修改
2. **升级 = 全量重打**：rubric 升级时所有历史文章用新公式重打分，新排序与实际表现 ≥4/5 一致才通过
3. **Rubric 是工作台，不是博物馆**：被数据推翻的观察删掉，git history 才是档案

---

## 依赖

- **Node.js 18+**（可选）：grindraft-cover 的 PNG 导出需要（puppeteer + canvas），HTML 预览无需依赖
- **Python 3.9+**（可选）：grindraft-illustrate 的 API 生图脚本需要（requests）
- **aihot API**：公开免费，grindraft-trends 使用，无需 token

---

## 项目结构

```
grindraft-skill/
├── skills/                          # 18 个子 skill
│   ├── grindraft/SKILL.md           # 总协议 + 路由器
│   ├── grindraft-init/SKILL.md      # 入口：初始化
│   ├── grindraft-trends/SKILL.md    # 热点抓取
│   ├── grindraft-seed/SKILL.md      # 选题对话
│   ├── grindraft-write/SKILL.md     # AI 写初稿
│   ├── grindraft-humanize/SKILL.md  # 去 AI 味
│   ├── grindraft-illustrate/SKILL.md# 正文配图
│   ├── grindraft-cover/SKILL.md     # 封面设计
│   ├── grindraft-polish/SKILL.md    # 打磨标题
│   ├── grindraft-format/SKILL.md    # 排版
│   ├── grindraft-predict/SKILL.md   # 盲预测
│   ├── grindraft-publish/SKILL.md   # 发布登记
│   ├── grindraft-retro/SKILL.md     # 复盘
│   ├── grindraft-persona/SKILL.md   # 受众画像
│   ├── grindraft-bump/SKILL.md      # 升级 rubric
│   ├── grindraft-recommend/SKILL.md # 推荐选题
│   ├── grindraft-status/SKILL.md    # 状态看板
│   └── grindraft-score-blind/SKILL.md # 盲打分 sub-agent
├── shared-references/               # 9 份跨 skill 协议
├── templates/                       # 写入用户项目的模板
├── cover-templates/                 # 40 套封面设计模板
├── starter-rubrics/                 # 评分体系初始权重
├── adapters/                        # 外部数据源适配
├── docs/                            # 文档
├── package.json                     # Node.js 依赖
├── CLAUDE.md                        # 项目级引导
└── README.md                        # 本文件
```

---

## 许可

MIT

