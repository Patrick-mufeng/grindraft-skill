// cover-designer-skill/screenshot.js
// 用法: node screenshot.js {工作目录路径} {文件夹名}
// 示例: node screenshot.js "C:/my-blog" "AI排版10分钟搞定"

const puppeteer = require('puppeteer');
const { createCanvas, Image: CanvasImage } = require('canvas');
const path = require('path');
const fs = require('fs');

(async () => {
  const workDir = process.argv[2];
  const folderName = process.argv[3];
  
  if (!workDir || !folderName) {
    console.error('用法: node screenshot.js <工作目录> <文件夹名>');
    process.exit(1);
  }
  
  const outDir = path.resolve(workDir, 'articles', folderName);
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  
  const htmlPath = path.join(outDir, 'preview.html');
  if (!fs.existsSync(htmlPath)) {
    console.error('preview.html not found:', htmlPath);
    process.exit(1);
  }
  
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  // 2.35:1 — 宽视口
  await page.setViewport({ width: 1440, height: 800, deviceScaleFactor: 2 });
  await page.goto('file:///' + htmlPath.replace(/\\/g,'/'), { waitUntil: 'networkidle0' });
  const el2x35 = await page.$('#cover-2x35');
  if (el2x35) {
    await el2x35.screenshot({ path: path.join(outDir, 'cover-2x35.png') });
    console.log('cover-2x35.png');
  }
  
  // 1:1 — 方视口
  await page.setViewport({ width: 800, height: 800, deviceScaleFactor: 2 });
  await page.goto('file:///' + htmlPath.replace(/\\/g,'/'), { waitUntil: 'networkidle0' });
  const el1x1 = await page.$('#cover-1x1');
  if (el1x1) {
    await el1x1.screenshot({ path: path.join(outDir, 'cover-1x1.png') });
    console.log('cover-1x1.png');
  }
  
  await browser.close();
  
  // Canvas 拼接 — 以 1:1 高度为基准，2.35:1 等比缩放，并排无变形
  function loadImg(filePath) {
    return new Promise((resolve, reject) => {
      const img = new CanvasImage();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = fs.readFileSync(filePath);
    });
  }
  
  const img1 = await loadImg(path.join(outDir, 'cover-2x35.png'));
  const img2 = await loadImg(path.join(outDir, 'cover-1x1.png'));
  
  const targetH = img2.naturalHeight;
  const scale = targetH / img1.naturalHeight;
  const w1 = Math.round(img1.naturalWidth * scale);
  const w2 = img2.naturalWidth;
  
  const canvas = createCanvas(w1 + w2, targetH);
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#0a0a0a';
  ctx.fillRect(0, 0, w1 + w2, targetH);
  ctx.drawImage(img1, 0, 0, w1, targetH);
  ctx.drawImage(img2, w1, 0, w2, targetH);
  
  fs.writeFileSync(path.join(outDir, 'cover-combined.png'), canvas.toBuffer('image/png'));
  console.log('cover-combined.png (' + (w1+w2) + 'x' + targetH + ', both same height)');
  console.log('Output → ' + outDir);
})();
