---
name: grindraft-cover
description: |
  公众号封面设计。读文章自动分析情绪+领域，从40套模板推荐3个，生成预览HTML和PNG。触发词："设计封面"/"帮我做封面"/"生成封面"/"公众号封面"/"封面"。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
---

# grindraft-cover — 公众号封面设计

文章改完后，制作封面。40 套模板覆盖 5 种情绪 × 6 个领域。

## 前置依赖

**HTML 预览**：无依赖，双击即开。

**PNG 渲染**：需要 Node.js + `puppeteer` + `canvas`（npm 包名小写）。执行前必须先检查依赖：

```
node -e "require('puppeteer');require('canvas');console.log('ok')"
```

如果报错 → 提示用户 `npm install puppeteer canvas`，然后只用 HTML 预览。首次使用时主动提示"封面功能需要 Node.js + puppeteer + canvas，安装后可自动生成 PNG。也可以只用 preview.html 手动截图。"

## Workflow

```
用户: "设计封面"（或文章改完后自动提示）
  ↓
Phase 0: 从 articles/{标题}_{日期}/final.md 读取文章
  ↓
Phase 1: 三维分析（情绪/领域/IP）
  ↓
Phase 2: 推荐 3 个模板（按情绪+领域匹配）
  ↓
Phase 3: 提取封面文案（标题/描述/标签）
  ↓
Phase 4: 生成预览 HTML + 可选 PNG
  ↓
Phase 5: 改稿循环（最多 5 轮）
  ↓
回到主流程: "排版"
```

---

## Phase 0 · 读取文章

从 `articles/{标题}_{日期}/final.md` 读取文章内容。**只读正文**（跳过 frontmatter、标题候选、简介、封面提示词段）。正文起始位置为最后一个 `---` 分隔线之后。

如果 `articles/` 下有多个文件夹，让用户选。

---

## Phase 1 · 三维分析

阅读文章后必须从以下三个维度分析：

### 情绪调性（5 选 1）

| 调性 | 判断信号 |
|------|---------|
| 冷峻 | 数据多、逻辑链、技术术语、冷静陈述 |
| 温暖 | 个人故事、情感表达、生活场景、治愈 |
| 激昂 | 观点鲜明、号召行动、对比冲突、力量感 |
| 轻松 | 幽默、自嘲、流行梗、年轻化语言 |
| 严肃 | 权威引用、深度分析、正式语气、长段落 |

### 内容领域（6 选 1）

科技 / 商业 / 生活 / 教育 / 娱乐 / 人文

### 个人 IP

如果文章来自个人创作者，提取：IP 名称、人设标签、品牌色（如有）。如无则不填。

---

## Phase 2 · 风格推荐

从 `cover-templates/index.md` 按情绪+领域交叉匹配，推荐 3 个模板。每个带：名称、色板、一句话理由。

```
根据文章分析：
· 情绪：冷峻
· 领域：科技

| # | 模板 | 色板 | 理由 |
|---|------|------|------|
| A | 赛博霓虹 | 暗底+青品红辉光 | 科技感最强，匹配 AI 话题 |
| B | 工程蓝图 | 蓝图青蓝调 | 技术教程感，网格背景 |
| C | 瑞士极简 | 黑白几何 | 冷峻克制，适合技术深度 |

选 A/B/C，或描述想要的感觉（如"暖一点""暗黑一点"）。
```

用户指定模板名则跳过推荐，直接进 Phase 3。

---

## Phase 3 · 封面文案

从文章提取：

1. **主标题**（≤15 字）
2. **描述**（≤30 字）
3. **标签**（3-5 个，如 AI排版 · 开源 · 效率）

展示给用户确认。

---

## Phase 4 · 生成

### 4.1 加载模板

从 `cover-templates/{序号}-{name_en}.md` 读取：`palette`、`fonts`、`layout`、`core_rules`、`negative_rules`、`css_snippets`。

### 4.2 生成预览 HTML

输出到 `articles/{标题}_{日期}/cover/`：

```
articles/{标题}_{日期}/
└── cover/
    ├── preview.html       ← 2.35:1 + 1:1 双版预览
    ├── cover-2x35.png     ← （需 Node.js）
    ├── cover-1x1.png      
    └── cover-combined.png  
```

预览 HTML 规范：
- Grid 布局 2.35fr 1fr，两张封面自动等高，左右并排
- 所有 CSS 内联，无外部依赖
- 禁止 vw 单位（Grid 列宽已限定）
- ⚠️ **两个 .cover-card 必须是 .preview-grid 的直接子元素**——如果嵌套（前一个 cover-card 未闭合），grid 退化为单列堆叠，1:1 跑到 2.35:1 下方
- ⚠️ **截图回退**：使用 `filter: blur()`、`background-clip: text`、`backdrop-filter` 的元素必须加 `data-capture-fallback` 属性 + CSS `@media print` 回退规则，否则 Puppeteer 截图会丢失这些效果（详见 `cover-templates/design-principles.md` 的"捕获安全规范"）
- ⚠️ **底部品牌栏（强制）**：`.preview-grid` 之后必须有一个 `<footer class="brand-footer">磨稿 • grindraft - Design</footer>`，样式内联在 `<style>` 中：居中、字号 12px、letter-spacing 1px、颜色与页面主色协调、上边距与 grid 有 `gap` 相同的间距——与封面卡片视觉隔离，不进入截图区域

### 4.3 可选 PNG 渲染（需 Node.js）

先跑依赖检查（见"前置依赖"），通过后分两步。

> **{标题}_{日期}** 为文章文件夹名，格式如 `DeepSeek价格战_2026-05-27`。

**Step 1 — 截图单张**：生成 `screenshot.js` 并执行。

```javascript
// screenshot.js — clip 两个 cover 并保存
const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  const htmlPath = 'file:///' + path.resolve('articles/{标题}_{日期}/cover/preview.html').replace(/\\/g, '/');
  const outDir = path.resolve('articles/{标题}_{日期}/cover');

  await page.setViewport({ width: 1600, height: 900 });
  await page.goto(htmlPath, { waitUntil: 'networkidle0' });

  // ⚠️ 先取 rect（同一个 viewport），不要中途改 viewport
  const rects = await page.evaluate(() => {
    const el235 = document.querySelector('.cover-2x35');
    const el11 = document.querySelector('.cover-1x1');
    return el235 && el11 ? {
      r235: { x: el235.getBoundingClientRect().x, y: el235.getBoundingClientRect().y, w: el235.getBoundingClientRect().width, h: el235.getBoundingClientRect().height },
      r11:  { x: el11.getBoundingClientRect().x,  y: el11.getBoundingClientRect().y,  w: el11.getBoundingClientRect().width,  h: el11.getBoundingClientRect().height }
    } : null;
  });
  if (!rects) { console.error('cover elements not found'); process.exit(1); }

  await page.screenshot({ path: path.join(outDir, 'cover-2x35.png'), clip: rects.r235 });
  await page.screenshot({ path: path.join(outDir, 'cover-1x1.png'),  clip: rects.r11 });
  await browser.close();
  console.log('screenshots done');
})();
```

**Step 2 — 拼接合并**：生成 `merge.js` 并执行。⚠️ 合并的是两张单图文件本身，不是网页截图。

```javascript
// merge.js — 以 1:1 高度为基准，左右拼接
const { createCanvas, loadImage } = require('canvas');
const fs = require('fs');
const path = require('path');
const outDir = path.resolve('articles/{标题}_{日期}/cover');

(async () => {
  const img235 = await loadImage(path.join(outDir, 'cover-2x35.png'));
  const img11  = await loadImage(path.join(outDir, 'cover-1x1.png'));

  const h = img11.height;                                    // 以 1:1 高度为基准
  const w235 = Math.round(img235.width * (h / img235.height)); // 2.35:1 等比例缩放

  const canvas = createCanvas(w235 + img11.width, h);
  const ctx = canvas.getContext('2d');
  ctx.drawImage(img235, 0, 0, w235, h);       // 左
  ctx.drawImage(img11, w235, 0, img11.width, h); // 右

  fs.writeFileSync(path.join(outDir, 'cover-combined.png'), canvas.toBuffer('image/png'));
  console.log('merged:', w235 + img11.width, 'x', h);
})();
```

执行：

```bash
node articles/{标题}_{日期}/cover/screenshot.js   # Step 1
node articles/{标题}_{日期}/cover/merge.js         # Step 2
```

执行完后删除两个临时脚本。

无 Node.js → 跳过，提示"已生成预览 HTML，你可以手动截图。安装 Node.js + puppeteer + canvas 后可自动生成 PNG。"

---

## Phase 5 · 改稿循环

- 改文案 → 更新标题/描述/标签 → 刷新 HTML
- 改配色/布局 → 微调，改动超 2 个核心规则建议换模板
- "换一个风格" → 回到 Phase 2
- 最多 5 轮，超限建议换模板

改完后用户说"可以了" → 回到主流程，自动提示"排版？"

**自检通过后，按全局规则刷新 `STATUS.md`**（见主 SKILL.md "STATUS.md 自动刷新"段）。获取当天日期 → 读 state.json → 扫 articles/ 下所有文章文件夹 → 渲染看板 → 写入 STATUS.md。

---

## Key Rules

1. **只读 articles/{标题}_{日期}/final.md 正文段**——不读 frontmatter 和候选段
2. **模板只读**——不修改 cover-templates/ 下的文件
3. **一次一个模板**——不混搭
4. **输出到 articles/{标题}_{日期}/cover/**——与文章其他产出同目录

## Integration

- 上游：grindraft-humanize（用户改完稿子后）
- 下游：grindraft-format（排版）
- 主路由已注册触发词