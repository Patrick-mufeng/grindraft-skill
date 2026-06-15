# 风格沉淀协议 / Style Precipitation Protocol

> 用户每次改完稿子后，自动 diff 改动 → 识别 pattern → 去重写入 style_guide.md。
> 不再是"等去 AI 味时才做"，而是写在 format/predict 等入口，**用户一回来就沉淀**。

## 核心规则

1. **每次用户改完回来触发**：在 format / predict / humanize 等入口自动运行
2. **对比的基准**：当前文件 vs 最近一次沉淀时的快照。首轮沉淀以 AI 初稿（`draft.md`）为基准
3. **去重**：写入 style_guide.md 前检查是否已存在同内容 pattern
4. **跨轮追踪**：每篇文章每轮沉淀都记录到 `.grindraft-cache/precipitation-log.jsonl`，避免同一 diff 重复处理
5. **跳过历史文章分析段**：`## 历史文章分析（初始化导入）` 段是 grindraft-init 一次性写入的，沉淀机制不碰此段——历史分析段的 pattern 由用户的正常改稿来验证和升级，沉淀机制通过后续改稿逐步覆盖和细化

## Workflow

```
[入口：humanize/format/predict 任一]
  ↓
Phase 0: 检查是否需要沉淀
  │  ├─ 读 precipitation-log，看本文上次沉淀的 file_hash
  │  └─ 算当前 final.md（或 draft.md）的 file_hash
  │     └─ hash 一致 → 跳过（无改动，不用沉淀）
  │
Phase 1: Diff
  │  对比当前文件 vs 上一轮沉淀时的快照（首轮 vs draft.md）
  │  输出改动清单：
  │  - 删了哪些词/句
  │  - 改了哪些表达
  │  - 加了什么风格元素
  │
Phase 2: 识别 Pattern
  │  从改动清单中提取可沉淀的模式：
  │  - 砍掉的 AI 常用词 → 追加到"绝对禁区"
  │  - 新增的口语化表达 → 追加到"推荐口语化词组"
  │  - 结构偏好（短段落/长段落/排比等）→ 追加到"写作人格"
  │
Phase 3: 去重写入
  │  逐条检查 style_guide.md 是否已有：
  │  - 已有 → 跳过
  │  - 已有但措辞不同 → 追加（标注"同义变体"）
  │  - 没有 → 追加
  │  ⚠️ 不扫描 `## 历史文章分析（初始化导入）` 段——此段由 init 管理
  │  ⚠️ Pattern 写入目标段（如"绝对禁区""推荐口语化词组"等），不写历史分析段
  │
Phase 4: 记录日志
  │  写入 .grindraft-cache/precipitation-log.jsonl：
  │  {"article": "{标题}_{日期}", "round": N, "file_hash": "...",
  │   "patterns_found": [...], "patterns_written": [...],
  │   "precipitated_at": "ISO"}
  │
Phase 5: 更新快照
  └── 将当前文件复制为 plates/style-diffs/{标题}_{日期}_precipitated.md
      （记录"已沉淀的版本"，下次 diff 以它为准）
```

## File Hash 计算

用文件正文的 sha256[:12] 判断是否有改动：

```bash
# 提取正文（跳过 frontmatter/title/简介等候选段）
sed -n '/^---$/,/^---$/!p' articles/{标题}_{日期}/final.md | tail -n +2 | sha256sum | cut -c1-12
# 如果 final.md 不存在，用 draft.md
```

## 去重检查逻辑

向 `style_guide.md` 写入前，逐条比对：

```python
def is_duplicate(pattern, section_content):
    """检查一条 pattern 是否已在 style_guide.md 的对应段中出现过"""
    # 1. 完全匹配 → 重复
    if pattern in section_content:
        return True
    # 2. 关键词匹配（"把"字句、"不要用XXX"等句式）
    #    如果 pattern 是"不要用 X"，而已有"X 看起来像 AI 套话"→ 语义重复
    # 3. 模式尾部匹配（"避免使用 X" vs "不用 X"）
    # 简单实现：pattern 的核心名词/动词在已有条目中出现 → 标记"同义变体"
    return False
```

实现时至少做**精确匹配**去重，建议做**关键词去重**。

## 沉淀纪律

- 只沉淀 **≥2 次出现**的 pattern，单次改动标 "待验证" 不写入正式规则
- 不沉淀**格式性改动**（中英文空格、标点符号统一等——这些由 humanize L1 自动处理）
- 不沉淀**一次性内容**（某篇文章特有的术语、案例名等）
