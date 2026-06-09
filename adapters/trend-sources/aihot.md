# aihot Adapter

> 热点源适配：aihot.virxact.com — 中文 AI 资讯精选。
> 默认启用的唯一热点源。用户可在 `.grindraft-state.json` 中添加其他源。

## 依赖

- 无 API key
- 公开 REST API，匿名可访
- 需要 User-Agent header（非默认 curl UA）

## Fetch 接口

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

# 默认：拉精选 + 最近 24 小时
since=$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-24H +%Y-%m-%dT%H:%M:%SZ)
curl -sH "User-Agent: $UA" "https://aihot.virxact.com/api/public/items?mode=selected&since=$since&take=50"
```

## 输出 Normalize

aihot API 返回的每个 item 映射到 grindraft candidate：

```json
{
  "id": "<aihot item id 的 sha256 前 12 位>",
  "title": "<aihot.title>",
  "source": "aihot",
  "source_url": "<aihot.url>",
  "snippet": "<aihot.summary>",
  "category": "<aihot.category → grindraft category>",
  "published_at": "<aihot.publishedAt>",
  "fetched_at": "<ISO now>"
}
```

## Category 映射

| aihot category | grindraft 选题方向 |
|---|---|
| ai-models | AI 模型/技术 |
| ai-products | AI 产品/工具 |
| industry | 行业趋势/解读 |
| paper | 论文/研究 |
| tip | 技巧/观点 |

## 失败模式

| 错误 | 处理 |
|---|---|
| HTTP 403 | UA header 缺失 → 重试带 UA |
| HTTP 429 | 限流 → 等待 1s 重试 |
| 空响应 | 标记 "aihot 今日无数据" |
| 网络超时 | 优雅降级 → 提示用户手动粘贴 |

## 稳定性等级

★★★★☆（公开 API，偶有维护窗口）
