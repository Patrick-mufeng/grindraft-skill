# Download Fix Guide · html2canvas 兼容性修复

## 已知丢失的 CSS 特性

| CSS 特性 | html2canvas | 表现 |
|----------|------------|------|
| `background-clip: text` | ❌ 不支持 | 元素变成透明或满框背景色 |
| `filter: blur()` | ⚠️ 部分支持 | 大 blur 值可能丢失或偏差 |
| `filter: drop-shadow()` | ⚠️ 部分支持 | 可能消失 |
| `backdrop-filter` | ❌ 完全不支持 | 玻璃态效果全丢 |
| CSS `background-image` SVG data URI | ⚠️ 不稳定 | 纹理噪点可能丢失 |

## 修复方案

### 方案：data-capture-fallback 属性

给每个使用不支持 CSS 的元素添加 `data-capture-fallback="cssText"`。在 html2canvas 的 `onclone` 回调中，将这些元素的 style 替换为 fallback 值。

```html
<!-- 渐变文字 → 捕获时改为纯色 -->
<h1 class="holo-title"
    data-capture-fallback="color:#7b5ea7 !important;background:none !important;-webkit-text-fill-color:#7b5ea7 !important">
  排版告别拖拽
</h1>

<!-- 模糊光球 → 捕获时降低透明度模拟 -->
<div class="holo-orb"
     data-capture-fallback="filter:none !important;opacity:0.06 !important">
</div>

<!-- 毛玻璃卡片 → 捕获时改为半透明纯色 -->
<div class="glass-card"
     data-capture-fallback="backdrop-filter:none !important;background:rgba(255,255,255,0.08) !important">
</div>
```

### JS 处理（在 onclone 中）

```js
onclone: (clonedDoc) => {
  clonedDoc.querySelectorAll('[data-capture-fallback]').forEach(el => {
    el.style.cssText = el.dataset.captureFallback;
  });
}
```

## 各模板特效映射表

生成封面 HTML 时，以下特效需要用 `data-capture-fallback`：

| 特效类型 | 示例 CSS | fallback |
|---------|---------|----------|
| 渐变文字 (background-clip) | `background:linear-gradient(...);-webkit-background-clip:text;color:transparent` | `color:{渐变色中间值};background:none;-webkit-text-fill-color:{色值}` |
| 大模糊光球 (blur > 30px) | `filter:blur(60px)` | `filter:none;opacity:0.06` |
| drop-shadow 文字发光 | `filter:drop-shadow(0 0 15px rgba(...))` | `text-shadow:0 0 15px rgba(...)` |
| 毛玻璃 (backdrop-filter) | `backdrop-filter:blur(20px)` | `backdrop-filter:none;background:rgba(255,255,255,0.1)` |
| 模糊棱镜光束 | `filter:blur(3px)` | `opacity:0.5` (小 blur 影响可控) |

## SVG 导出方案

SVG `<foreignObject>` 对 CSS 支持比 html2canvas 还差。改为用 html2canvas 渲染为 Canvas → toDataURL → 嵌入 SVG 作为 `<image>`：

```js
function downloadSVG_viaCanvas(el, size) {
  const scale = size === '4K' ? 4 : size === '2K' ? 2.5 : 2;
  html2canvas(el, { scale, backgroundColor, onclone }).then(canvas => {
    const dataUrl = canvas.toDataURL('image/png');
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" 
      width="${canvas.width}" height="${canvas.height}">
      <image href="${dataUrl}" width="100%" height="100%"/>
    </svg>`;
    // download...
  });
}
```

注意：这样 SVG 内嵌的是位图，不是真矢量。但对于"排版封面"这类图形密集内容，矢量导出本身意义有限——真需要矢量应该用 Figma/Illustrator 而非浏览器截图。
