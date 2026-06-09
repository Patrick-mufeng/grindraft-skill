# 盲预测协议 / Blind Prediction Protocol

> 原则 #1 的完整规范。任何预测一旦写入 `## 预测` 段即不可修改。

## 核心规则

1. **预测必须在看到数据前写完**。一旦写完，`## 预测` 段是 immutable。
2. 只能往 `## 复盘` 段追加内容。
3. **不允许**在数据出来后"调整"预测——那叫 reconstructed retrospective，要走 `_redo.md` 路径。
4. 如果用户承认已看过数据 → 拒绝写"预测"，改用 `_redo.md` 标注 `**Reconstructed retrospective — NOT a blind prediction**`。

## 预测文件的不可变边界

```
[文件顶部 — metadata header]
  - 可编辑：published_at / URL / platform 等发布登记字段
---
## 预测 v1（或 ## 预测 v2）
  ↓
  **整个段 IMMUTABLE —— 写完即锁定**
  ↓
---
## 复盘
  ↓
  可追加：实绩数据 / 验证推翻 / 新观察
```

## 子 skill 必须做的检查清单

所有涉及"盲度"的子 skill（grindraft-predict / grindraft-retro / grindraft-publish）必须执行：

1. 询问用户该文章当前发布状态
   - 未发 → 通过
   - 已发但未到复盘窗口 → 询问"你看过任何后续数据吗（阅读量/分享/在看/留言）？"
     - 用户回答"没看过" → 通过，标记 `blind_status: confirmed_no_data_seen`
     - 用户回答含糊 → 视为"已看"，按下一项处理
   - 已发且已过复盘窗口 → **立即拒绝写"预测"**，建议用 `_redo.md` 路径

2. 自检对话历史里是否含阅读量/分享/在看/留言等字眼的实际数字 → 命中则视为已见数据

## 公众号长文的"见数据"定义

与短视频不同，公众号文章发布后，创作者通常在后台**立即看到**：
- 阅读量（实时更新）
- 分享数
- 在看数
- 留言（公开可见）

因此盲度窗口更短——**发布前必须写好预测**。一旦发布并打开后台看数据，即视为"已见数据"，不能再补预测。

## 文件名约定

```
predictions/YYYY-MM-DD_<id>_<short-title>.md
```
- `YYYY-MM-DD`：预测写下的日期
- `<id>`：12 位 hash，对终稿全文做 sha256 取前 12 位
- `<short-title>`：3-8 字，去标点

## 重做路径 `_redo.md`

如有正当理由重做预测（如发现预测时稿子版本搞错了），写 `predictions/YYYY-MM-DD_<id>_<short>_redo.md`，原文件保留不动。`_redo.md` 的 header 必须标注：
```markdown
**⚠️ Reconstructed retrospective — NOT a blind prediction**
**Original prediction**: predictions/<原文件>
**Reason for redo**: <原因>
```
