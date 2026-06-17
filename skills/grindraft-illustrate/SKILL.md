---
name: grindraft-illustrate
description: |
  正文配图生成。读文章自动分析出配图策略（shot list），用小黑怪诞手绘风格逐张生成 16:9 横版插图。
  触发词："配图"/"生成配图"/"文章插图"/"illustrate"/"做插图"。
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
---

# grindraft-illustrate — 正文配图生成

在文章定稿后，为正文生成小黑风格的怪诞手绘配图。通过 image-2 服务调用生图 API 逐张生成 16:9 横版插图。

## 前置依赖

**Python 3.9+** + `requests`。

检查依赖：
```bash
python --version           # 需 >= 3.9
pip install requests       # 安装 HTTP 请求库
```

**首次使用引导**：配图功能默认使用 **云雾 API 中转站** 调用 ChatGPT image-2 模型生图。首次使用需要：

1. **注册账号**：打开 https://yunwu.ai/register?aff=zM1f 注册
2. **获取 API Key**：注册后进入控制台，复制你的 API Key
3. **配置 API Key**：在项目根目录 `.env` 或 `.grindraft/config.env` 中填入：

```env
# 云雾API 配置（用于正文配图生图）
YUNWU_API_KEY=sk-你复制的API Key
YUNWU_BASE_URL=https://yunwu.ai/

# IMAGE2_BASE_URL：默认为 YUNWU_BASE_URL，指向同一代理服务
# 仅当使用独立的 image-2 兼容服务时才需覆盖此值
# IMAGE2_BASE_URL=https://自建服务地址/
```

> 配置优先级：`.env` → `.grindraft/config.env`，后者覆盖前者。
> 首次使用会自动创建 `.grindraft/config.env` 模板。
> `IMAGE2_BASE_URL` 未显式设置时自动回退到 `YUNWU_BASE_URL`，无需单独配置。

> 📌 **为什么默认用云雾 API**：`gpt-image-2` 模型目前仅通过 API 中转站可用。云雾提供标准 OpenAI 兼容接口，注册即用，无需自建 image-2 服务。

**API 配置说明**（二选一）：

| 方式 | 配置 | 适用场景 |
|------|------|---------|
| ☁️ **云雾 API**（推荐） | `.env` 或 `.grindraft/config.env` 中填 `YUNWU_API_KEY` 即可 | 大多数用户，开箱即用 |
| 🖥️ **自建 image-2 服务** | `.env` 或 `.grindraft/config.env` 中设 `IMAGE2_BASE_URL` 覆盖 | 有自建服务的高级用户 |

---

## Workflow

```
用户: "配图"
  ↓
Phase -1: API Key 检查
  ├─ .grindraft/config.env 存在 + YUNWU_API_KEY 已填 → 通过
  └─ 未配置 → 自动创建 .grindraft/config.env 模板
               → 显示注册引导 → 用户填好 key 后重新说"配图"
  ↓
Phase 0: 读取 final.md → 消化正文
  ↓
Phase 1: 出配图策略（shot list，4-8 张）
  ↓
Phase 2: 用户确认策略
  ↓
Phase 3: 逐张生成（构建英文 prompt → Node.js 脚本调 API → 保存 PNG）
  ↓
Phase 4: QA 检查（对照 checklist，失败的重生成）
  ↓
Phase 5: 交付汇总
  ↓
回到主流程: "设计封面"
```

---

## 先读这些参考

开始工作前，按需要读取以下参考文件，不要一次塞满上下文：

- `references/style-dna.md`：风格 DNA、颜色、文字、禁忌。
- `references/xiaohei-ip.md`：小黑 IP 的形象、性格、动作库和禁忌。
- `references/composition-patterns.md`：结构类型、原创隐喻方法和反复刻规则。
- `references/prompt-template.md`：单张生图提示词模板。
- `references/qa-checklist.md`：生成后检查和迭代规则。
- `assets/examples/`（如存在）：只作低频视觉校准，不进入默认生成路径。**不要照抄**这些案例的构图、物件或标注。

---

## Phase -1 · API Key 检查与自动配置

首次使用配图时，自动检测 API Key 是否已配置。如果未配置，自动创建配置文件夹和模板文件。

### 检查流程

1. 检查 `.grindraft/config.env` 是否存在且包含 `YUNWU_API_KEY=sk-` 开头的有效 key
2. 如已配置 → 通过，进入 Phase 0
3. 如未配置 → 执行自动配置：

```
📁 检测到 API Key 未配置，正在自动创建配置...
  □ 创建 .grindraft/ 目录 ✅
  □ 创建 .grindraft/config.env 模板 ✅
  □ 写入注册引导信息 ✅

请在 .grindraft/config.env 中填入你的 API Key：

  1. 🔑 注册获取 Key：https://yunwu.ai/register?aff=zM1f
  2. 📝 复制你的 API Key（以 sk- 开头）
  3. ✏️ 打开 .grindraft/config.env，替换 YUNWU_API_KEY= 后面的值

配置好后重新说"配图"即可继续。
```

### 自动创建的文件结构

```
{项目根目录}/
└── .grindraft/              ← API 配置目录（不入版本控制）
    └── config.env           ← API Key 配置
        ├── YUNWU_API_KEY=sk-你的Key     ← 配图（gpt-image-2）
        └── YUNWU_BASE_URL=https://yunwu.ai/  ← 云雾 API 地址
```

### 实现方式

```bash
# 检查 .grindraft/config.env 是否存在
if [ ! -f .grindraft/config.env ]; then
  mkdir -p .grindraft
  cat > .grindraft/config.env << 'EOF'
# 云雾API 配置 — 正文配图使用 gpt-image-2 生成
# 注册地址：https://yunwu.ai/register?aff=zM1f
# 将下方 YOUR_API_KEY 替换为你的真实 Key
YUNWU_API_KEY=sk-YOUR_API_KEY
YUNWU_BASE_URL=https://yunwu.ai/
EOF
  echo "✅ 已创建 .grindraft/config.env，请配置 API Key 后重试"
fi
```

> ⚠️ `.grindraft/` 目录已包含在 `.gitignore` 模式中，不会提交到版本控制。

## Phase 0 · 读取文章

从 `articles/{标题}_{日期}/final.md` 读取文章内容。**只读正文**（跳过 frontmatter）。

提炼：
- 核心观点是什么
- 哪些段落承担认知转折
- 哪些内容适合用图解释
- 哪些地方只适合文字，不需要图

不要平均配图。优先选择"认知锚点"：核心判断、两个断点、输入输出闭环、分流、前后对比、一鱼多吃、承接路径、常见坑、角色状态变化。

---

## Phase 1 · 配图策略

输出 shot list。每张图写清楚：

| 字段 | 说明 |
|---|---|
| 位置 | 放在哪个段落后 |
| 主题 | 图的主题 |
| 核心意思 | 这张图要表达什么 |
| 结构类型 | Workflow / 系统局部 / 前后对比 / 角色状态 / 概念隐喻 / 方法分层 / 地图路线 / 小漫画分镜 |
| 小黑动作 | 小黑在图里做什么 |
| 建议元素 | 1-4 个核心物件 |
| 中文标注词 | 3-8 个短标注词 |

默认 4-8 张。文章很短时 1-3 张；长文也不要超过 9 张。够用就好。

输出格式：

```
## 配图策略

| # | 位置 | 主题 | 结构类型 | 小黑动作 |
|---|------|------|----------|----------|
| 1 | 第X段后 | xxx | 概念隐喻 | xxx |
| 2 | ... | ... | ... | ... |

### 图 1：{主题}
- **核心意思**：...
- **结构类型**：概念隐喻
- **小黑动作**：...
- **建议元素**：纸箱 / 漏斗 / 箭头
- **中文标注词**：输入 / 卡住了 / 输出 / ？
...
```

---

## Phase 2 · 用户确认策略

将上一阶段的 shot list 展示给用户确认。用户确认前不要进入 Phase 3 生图。

用户可以对 shot list 做增删改：
- **"去掉第3张"** — 删除指定图片
- **"加一张关于XX的"** — 新增一张图
- **"改一下图4的核心意思"** — 修改现有策略
- **"直接生成"** — 确认所有策略，进入 Phase 3

用户确认后生成的 shot list 保存在 `illustrations/shot-list.md`。

---

## Phase 3 · 逐张生成

### 3.1 构建 Prompt

每张图根据 `references/prompt-template.md` 模板构建英文 prompt。必须包含：

- 16:9 horizontal Chinese article illustration
- Pure white background, black hand-drawn line art
- 小黑 IP（solid-black creature, white dot eyes, thin legs, blank serious expression）
- 小黑 must perform the core conceptual action
- Sparse red/orange/blue handwritten Chinese annotations
- 大量留白（≥35%）
- 禁止 PPT、商业插画、可爱卡通、复杂背景、左上角标题

**不要复刻旧案例构图**。每次从当前文章重新发明隐喻。参考 `references/composition-patterns.md` 的原创隐喻生成法和反复刻规则。

### 3.2 调用 image-2 服务

使用 `scripts/illustrate.py` 脚本（Python 3.9+，依赖 requests）：

```bash
python scripts/illustrate.py \
  --prompt "<英文prompt>" \
  --output "articles/{标题}_{日期}/illustrations/{序号}-{主题}.png" \
  --size "1024x576"
```

脚本行为：
- 从 `.env` 和 `.grindraft/config.env` 读取配置（后者覆盖前者）
- 配置项：`YUNWU_API_KEY`（必填）、`YUNWU_BASE_URL`（默认 `https://yunwu.ai/`）、`IMAGE2_BASE_URL`（未设置时回退到 `YUNWU_BASE_URL`）
- 调用 `POST {IMAGE2_BASE_URL}/v1/images/generations`（OpenAI 兼容格式）
- 从返回的 `b64_json` 解码保存为本地 PNG 文件
- 输出 JSON：`{"success": true, "path": "...", "url": "", "attempts": 1}`
- 模型固定使用 `gpt-image-2`，不可切换
- 超时时间：300 秒（可传 `--timeout` 自定义）

### 3.3 错误处理

- API 调用失败 → 指数退避重试（3s → 9s → 27s），最多 2 次
- 网络连通性检测：发请求前先快速 ping API 地址（5s 超时），网络不通立即报错不等待
- 备选 API 切换：传 `--fallback-url <地址>`，连续失败 2 次后自动切换到备选地址
- 仍失败 → 跳过该张，在汇总中标注
- 连续 3 张失败 → 停止，提示用户检查 API 配置

### 3.4 超时和上游负载的排查

如果配图生成经常超时，按以下顺序排查：

**1. 网络连通性**
```bash
# 测试 API 是否可达
curl -s -o /dev/null -w "%{http_code}" https://yunwu.ai/v1/models
# 正常应返回 200
```

**2. 延长超时时间**
```bash
# 默认 300s，可延长到 600s
python ... --timeout 600
```

**3. 切换备选 API 地址**
```bash
# 如果主地址负载高，指定备选
python ... --fallback-url https://备选地址/
```

**4. 常见原因**

| 现象 | 原因 | 解决 |
|------|------|------|
| `无法连接 API 服务` | 本地网络不通 / API 地址错误 | 检查 `.env` 中的 `YUNWU_BASE_URL` |
| `API 请求超时（>300s）` | 上游 gpt-image-2 负载高 | `--timeout 600` 或错峰使用 |
| `API 返回 429/503` | 请求频率过高 / 服务限流 | 降低并发，增加 `--retries` |
| `API 返回 4xx` | API Key 无效或余额不足 | 检查 `YUNWU_API_KEY` 是否有效 |

---

## Phase 4 · QA 检查

对照 `references/qa-checklist.md` 检查每张图：

**必过项**：
- 16:9 横版
- 干净白底
- 有小黑且承担核心动作
- 没有复刻旧案例构图
- 画面怪诞有创意
- 中文标注少、短、能读
- 颜色克制（橙=路径、红=重点、蓝=补充）

**失败信号** → 重生成：
- 左上角有类型标题
- 小黑像吉祥物/可爱卡通
- 画面像 PPT/流程图/课件
- 背景有纸纹/阴影/渐变
- 元素太多太满

由于 API 生图无法像 Codex 工具那样精确控制，QA 以人工目测为主。AI 根据返回的图片内容做初步判断，标注可疑项供用户确认。

---

## Phase 5 · 交付汇总

```
✅ 配图完成

| # | 文件 | 用途 | 状态 |
|---|------|------|------|
| 1 | 01-xxx.png | 第X段后 | ✅ |
| 2 | 02-xxx.png | 第X段后 | ✅ |
| 3 | 03-xxx.png | 第X段后 | ⚠️ 重试1次 |

保存路径：articles/{标题}_{日期}/illustrations/
配图策略：articles/{标题}_{日期}/illustrations/shot-list.md
```

---

## 文件结构

```
articles/{标题}_{日期}/
├── draft.md
├── final.md
├── prediction.md
├── output.html
├── cover/
│   ├── preview.html
│   ├── cover-2x35.png
│   └── cover-1x1.png
├── illustrations/          ← 本 skill 产出
│   ├── shot-list.md
│   ├── 01-{主题}.png
│   ├── 02-{主题}.png
│   └── ...
└── retro/
    └── report.md
```

---

## 输出口径

生成前的策略输出要短而准。生成后的交付要包含：

- 生成了几张
- 每张图的用途
- 保存路径
- 哪些图最稳，哪些图是可选

**不要长篇解释风格理论**；让图自己说话。

---

## Key Rules

1. **只读 final.md 正文段**——不读 frontmatter
2. **一张图一个核心结构**——不堆砌
3. **每次重新发明隐喻**——不复刻旧案例，参考 `references/composition-patterns.md`
4. **小黑必须是动作主体**——不只是装饰
5. **API 生图不可控时降低期望**——gpt-image-2 等 API 模型的风格还原度有限，接受合理偏差
6. **先出策略再生成**——未经用户确认的 shot list 不要直接生图（除非用户说"直接生成"）

## Integration

- 上游：grindraft-humanize（用户改完稿子后）
- 下游：grindraft-cover（设计封面）
- 主路由注册触发词："配图"/"生成配图"/"文章插图"/"illustrate"/"做插图"
