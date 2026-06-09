---
name: grindraft-format
description: |
  将 Markdown 终稿转为微信公众号兼容 HTML。默认 AI 自动选择最适配主题排版，无需用户操心。触发词："排版"/"format"/"转 HTML"/"公众号排版"/"生成 HTML"。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
---

# grindraft-format — Markdown → 公众号 HTML

## 设计规范引用

排版生成前必须读取 `adapters/format/公众号HTML排版设计规范.md`——这是 HTML 生成的真实来源。按规范中的标签规则、CSS 白名单、组件配方严格执行，不凭记忆。

## 默认行为：AI 自动排版

**除非用户明确说要某个主题，否则 AI 自行发挥，设计最好看的排版。不预设主题，每次都重新设计。**

如果用户说"排版"两个字——直接出 HTML，不问主题、不确认。做到"一键排版"。

## 用户可选主题（仅在用户主动要求时提供）

当用户说"用上次的主题""用XX主题"或"有哪些主题可选"时，展示已有风格名称供参考：

| 用过的主題 | 特征 |
|---|---|
| 脉冲 | 深空黑 + 电光青 + 数据橙，科技硬核 |
| 刃 | 黑白 + 玫瑰红左边框，锋利 |
| 纸墨 | 暖纸底 + 朱砂红 + 细线，杂志阅读感 |
| 构 | 黑底金字标题带 + 3px粗线 + 金色数字 |
| 编 | 暖灰底 + 赤陶点缀 + 细横线，编辑感 |
| 壳 | 终端美学 + 珊瑚红 + monospace，明亮 |

用户不选 → AI 自行设计新主题。

## 格式解析

读 `drafts/<id>.md`，识别结构：

- `---` 包裹的 frontmatter → 提取 `title` 和 `summary`，不排版
- `## 📝 标题候选` → 跳过
- `## 📋 简介` → 跳过
- `## 🎨 封面提示词` → 跳过
- 最后一个 `---` 之后 → **正文，排版内容**
- 正文中的 `![alt](path)` → 图片，圆角处理 + 阴影

## Workflow

### Phase 0: 读文件 + 去 AI 味提醒

1. **优先读 `scripts/<id>.md`**（用户改完的终稿）。如果 scripts/ 下没有同款文件，fallback 到 `drafts/<id>.md`
2. 提取 frontmatter 的 `title`（作为 HTML 标题）
3. 跳过候选段，取正文
4. 如果读的是 drafts/ 而非 scripts/ → 提醒用户"终稿在 scripts/ 下吗？排版用的是 drafts/ 初稿"
5. **去 AI 味提醒**：如果文章还没有跑过 humanize，排版前自动问一句

```
排版前要先"去 AI 味"吗？
A) 去 AI 味 → 四层自检，修完再排版
B) 直接排版 → 跳过
```

6. **封面提醒**：如果文章还没有做封面，排版前自动问一句

```
封面做了吗？要先设计吗？
A) 设计封面 → 选模板 → 生成预览
B) 直接排版 → 跳过
```

用户选 A → 调 grindraft-cover 逻辑，出完封面自动接着排版。选 B → 直接排版。

### Phase 1: AI 设计主题

自动设计一套全新主题色板 + 设计语言。不重复使用已有主题名。

如果用户指定了主题 → 用那个。如果用户说"排版"没提主题 → AI 发挥。

### Phase 2: 生成 HTML

#### 路径规则（强制！）

| 规则 | 说明 |
|---|---|
| HTML 平铺 | `output/<date>_<id>_<short>.html`（禁止在 output/ 下创建子目录） |
| 与源文件同名 | `<date>` `<id>` `<short>` 必须与 drafts/ 或 scripts/ 中的源文件完全一致 |
| 封面图片 | 如有封面，放在 `output/cover/<date>_<id>_<short>/` 子目录下，不影响 HTML 路径 |

> ⚠️ **禁止** `output/hermes-desktop/index.html`、`output/mirofish/2026-06-06_mirofish.html` 等子目录结构。所有 HTML 必须平铺在 output/ 根目录下——这是 status 看板和 retro 跨文件校验能找到它们的前提。

#### 落盘（两个文件）

**文件 A — 清洁版**：`output/<date>_<id>_<short>.html`
纯净排版 HTML，可直接粘贴公众号后台。与之前相同。

**文件 B — 预览版**：`output/<date>_<id>_<short>-preview.html`
手机预览 + 一键复制。双击打开即可在手机模拟器中预览，顶部"复制到公众号"按钮一键复制。

生成方式：
1. 读取 `adapters/format/preview.html`（skill 内置预览模板，无外部依赖）
2. 将排版生成的 HTML 原文嵌入 `<script type="text/plain" id="preload-content">` 标签内（替换 `<!-- CONTENT_PLACEHOLDER -->`）
3. 写入 `output/<date>_<id>_<short>-preview.html`

### Phase 3: 完成

```
✅ 排版完成：output/YYYY-MM-DD_<id>_<short>.html
主题：<自研名称>

预览版：output/YYYY-MM-DD_<id>_<short>-preview.html
（双击打开 → 手机预览 + 一键复制到公众号）

下一步：打开 -preview.html 预览效果 → 复制 HTML → 粘贴公众号后台 → "启动预测"
```

### Phase 4: 自检 — 逐项重读验证写入完整性

生成 HTML 后，**重新读取输出文件**，确认写入生效。

#### 验证清单

| # | 目标 | 读什么 | 通过条件 |
|---|---|---|---|
| 1 | 清洁版 HTML | `output/<date>_<id>_<short>.html` | 文件存在，字节数 > 1000（有效 HTML），含 `<section` 标签 |
| 2 | 预览版 HTML | `output/<date>_<id>_<short>-preview.html` | 文件存在，字节数 > 5000（含完整预览模板），含 `preload-content` 且不含 `CONTENT_PLACEHOLDER` |
| 3 | 路径正确 | 两个文件 | 文件名与 draft/script 同名（仅后缀不同） |
| 4 | 路径平铺 | `output/` 目录 | 两个文件均在 output/ 根目录下，**不在子目录内** |

#### 自检输出格式

```
📋 自检 Phase 4:
  □ output/<file>.html → 文件存在，{N} 字节，含 section 标签 ✅
  □ output/<file>-preview.html → 文件存在，{N} 字节，内容已嵌入 ✅
  □ 路径一致 → 两个文件与源文件同名 ✅
  □ 路径平铺 → 两个文件均在 output/ 根目录下 ✅

✅ 排版自检全部通过
```

#### 失败处理

- ❌ HTML 不存在或过小 → **立即重新生成**
- ❌ 文件名不匹配 → **移动到正确路径**
- ❌ 在子目录内 → **移动到 output/ 根目录**
- 重试后再次 re-read 确认 → 仍不通过 → 输出 `❌ 自检失败，请手动检查`
