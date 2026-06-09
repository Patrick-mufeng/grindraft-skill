# 磨稿 / Grindraft

> 把公众号长文写作变成可校准预测循环——让每一篇都算数。

[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blue)](https://claude.ai)

---

## 这是什么？

**磨稿** 是一个 Claude Code 插件，包含 16 个独立 skill，覆盖公众号长文写作全流程：

```
抓热点 → 聊选题 → AI 写初稿 → 去 AI 味 → 设计封面 → 排版 → 盲预测 → 发布 → 复盘 → 进化
```

常规 AI 写作是一次性的。磨稿不一样——**每一篇文章都变成数据，数据反过来让下一篇更好**。

---

## 安装

### 方式一：Claude Code 插件市场

```bash
claue plugin install github.com/grindraft/grindraft-skill
```

### 方式二：手动复制

将 `skills/` 目录下的任意 skill 文件夹复制到项目的 `.claude/skills/` 目录：

```bash
# 安装全部 16 个 skill
cp -r skills/* ~/your-project/.claude/skills/

# 或只安装需要的
cp -r skills/grindraft-init ~/your-project/.claude/skills/
```

---

## 快速开始

安装后在 Claude Code 中说：

```
磨稿初始化
```

跟着引导回答几个问题（粉丝数、发布频率、AI 参与度），脚手架就建好了。

之后用自然语言触发每个环节：

```
抓热点          → 拉今日 AI 圈精选资讯，写入选题池
找选题          → 围绕你的真实经历深挖，收敛到一个角度
写文章          → AI 按你的大纲出初稿
去 AI 味        → 四层自检，修复 AI 写作痕迹
设计封面        → 40 套模板选一个，生成预览 HTML
排版            → Markdown 一键转公众号 HTML
启动预测        → 7 维盲打分 + bucket 押注（写完不可改！）
已发布          → 登记 URL，提醒复盘时间
复盘            → T+3 天后看数据，对比预测验证/推翻
状态            → 看板：进度、选题池、待复盘
```

---

## 16 个 Skill

| Skill | 触发词 | 做什么 |
|-------|--------|--------|
| `grindraft` | 磨稿 | 总路由 + 全局协议 |
| `grindraft-init` | 初始化 | Onboarding + 创建项目骨架 |
| `grindraft-trends` | 抓热点 | 从 aihot 拉 AI 圈精选资讯 |
| `grindraft-seed` | 找选题 | 深度对话，收敛到一个角度 |
| `grindraft-write` | 写文章 | AI 出初稿（low/medium/high 三种自由度） |
| `grindraft-humanize` | 去 AI 味 | L1-L4 四层质检体系 |
| `grindraft-cover` | 设计封面 | 40 套模板自动匹配 + HTML 预览 |
| `grindraft-polish` | 打磨标题 | 标题候选 + 简介 + 封面提示词 |
| `grindraft-format` | 排版 | Markdown → 公众号兼容 HTML |
| `grindraft-predict` | 启动预测 | 7 维盲打分 + bucket 押注（⚠️ immutable） |
| `grindraft-publish` | 已发布 | 登记 URL，更新状态 |
| `grindraft-retro` | 复盘 | T+3 数据回收 + 验证预测 |
| `grindraft-persona` | 受众画像 | 从留言聚类读者画像 |
| `grindraft-bump` | 升级 rubric | 公式升级（全量重打 + 跨模型审） |
| `grindraft-recommend` | 推荐选题 | 选题池按 rubric 排序推荐 |
| `grindraft-status` | 状态 | 看板：模式、进度、维护提醒 |

---

## 三条铁律

1. **盲预测**：预测写完即锁定，不可修改。真实数据只能追加到复盘段。
2. **升级必须全量重打**：rubric 升级时要对所有历史文章用新公式重排序，≥4/5 一致才通过。
3. **rubric 是工作台，不是博物馆**：被数据推翻的观察删掉——git history 才是档案。

---

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

每维 1-5 分，加权算出 composite，对应阅读量 bucket（S/A/B/C/D/E）。

---

## 项目结构

初始化后，你的文章项目会变成：

```
<你的项目>/
├── rubric_notes.md          # 评分规则（7 维公式）
├── style_guide.md           # 你的写作风格（从修改中沉淀）
├── STATUS.md                # 状态看板
├── .grindraft-state.json    # 系统状态
├── drafts/                  # AI 初稿
├── scripts/                 # 你改完的终稿
├── predictions/             # ⚠️ 预测日志（不可修改）
├── output/                  # 排版 HTML
├── retro/                   # 复盘数据
└── candidates.md            # 选题池
```

---

## 依赖

- **Node.js + puppeteer + canvas**（可选）：封面 PNG 导出需要。HTML 预览无需依赖。
- **aihot API**：热点抓取数据源，公开免费，无需 token。

---

## 许可

MIT
