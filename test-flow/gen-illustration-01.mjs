/**
 * grindraft-illustrate 生图测试脚本
 *
 * 用法:
 *   node test-flow/gen-illustration-01.mjs
 *
 * 依赖: Node.js 18+（fetch 内置，零 npm 依赖）
 *
 * 从项目 .env / .grindraft/config.env 读取 API Key 和 Base URL，
 * 调用 gpt-image-2 服务生成测试图片。
 */

import { writeFileSync, mkdirSync, readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(__dirname, "..");

// ── 加载配置 ──────────────────────────────────────────────

function loadEnv(projectRoot) {
  const defaults = {
    IMAGE2_BASE_URL: "",
    YUNWU_API_KEY: "",
    YUNWU_BASE_URL: "https://yunwu.ai/",
  };

  const candidates = [
    resolve(projectRoot, ".env"),
    resolve(projectRoot, ".grindraft", "config.env"),
  ];

  for (const envPath of candidates) {
    try {
      const text = readFileSync(envPath, "utf-8");
      for (const line of text.split("\n")) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith("#") || !trimmed.includes("=")) continue;
        const [key, ...rest] = trimmed.split("=");
        const val = rest.join("=").trim();
        if (key.trim() in defaults) defaults[key.trim()] = val;
      }
    } catch {
      // 文件不存在则跳过
    }
  }

  return defaults;
}

const config = loadEnv(projectRoot);
const apiKey = config.YUNWU_API_KEY;
const baseUrl = config.IMAGE2_BASE_URL || config.YUNWU_BASE_URL;

if (!apiKey) {
  console.error("错误：未配置 YUNWU_API_KEY");
  console.error("请在 .env 或 .grindraft/config.env 中设置：");
  console.error("  YUNWU_API_KEY=sk-你的API Key");
  process.exit(1);
}

const endpoints = [
  { name: "中转站", url: `${baseUrl.replace(/\/+$/, "")}/v1/images/generations` },
];

const prompt = `Generate one standalone 16:9 horizontal Chinese article illustration.

Visual DNA:
Pure white background. Minimalist black hand-drawn line art. Slightly wobbly pen lines. Lots of empty white space. Sparse red/orange/blue handwritten Chinese annotations. Clean absurd product-sketch feeling. No gradients, no shadows, no paper texture, no complex background, no commercial vector style, no PPT infographic look, no cute mascot poster, no children illustration, no realistic UI.

Recurring IP character required:
Xiao Hei, a small solid-black absurd creature with white dot eyes, tiny thin legs, blank serious expression, slightly uneven hand-drawn body shape. Xiao Hei must perform the core conceptual action, not decorate the scene. Xiao Hei is serious, deadpan, and slightly bizarre, not cute.

Theme: Comparing shallow chat wrapper clients vs real agent that works on your project.

Structure type: Before-after comparison.

Core idea: Left side shows a shallow plate with a chat bubble (representing 90% wrapper clients that are just web chat in a local window). Right side shows deep ocean with a project door opening to code files (representing DeepSeek-GUI that really works on projects). Xiao Hei in middle pulls a lever to switch from left to right.

Composition: Left-right split. Left: A shallow plate/dish with an empty chat bubble floating above it, light thin sketch lines. Right: Dark ocean water indicated by light blue thin hatch lines, with a heavy door slightly open revealing code files behind it. Center: A large mechanical lever/switch on a base, Xiao Hei standing beside it with tiny arms pulling the lever toward the right.

Chinese handwritten labels: tao ke in red on left side, zhen gan huo in red on right side, Kun in blue on the lever base, Deep to Deeper in orange along the lever direction.

Color use: Black for main line art and Xiao Hei. Orange for the lever and direction arrow. Red only for the two key labels. Blue only for Kun label. Light blue thin hatching lines to suggest ocean depth, no gradients.

Constraints: One image explains only one core comparison. Main subject 40-60 percent of canvas. At least 35 percent blank white space. At most 5 short handwritten Chinese labels. No title in top-left corner. No structure type text. No formal diagram, course slide, or dense explainer. Do not copy prior examples. It should be clear but not instructional, interesting but not childish, strange but clean.`;

const outDir = resolve(projectRoot, "test-flow/articles/又一款 DeepSeek 桌面客户端_2026-06-16/illustrations");
const outPath = resolve(outDir, "01-套壳-vs-真干活.png");
mkdirSync(outDir, { recursive: true });

for (const ep of endpoints) {
  console.log(`尝试 ${ep.name}...`);
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 60000);
    const resp = await fetch(ep.url, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({ model: "gpt-image-2", prompt, n: 1, aspect_ratio: "16:9", response_format: "b64_json" }),
      signal: controller.signal,
    });
    clearTimeout(timer);

    if (!resp.ok) {
      const err = await resp.text();
      console.log(`  ${ep.name} 返回 ${resp.status}: ${err.slice(0, 200)}`);
      continue;
    }

    const data = await resp.json();
    const img = data.data?.[0];
    if (!img?.b64_json) {
      console.log(`  ${ep.name} 无图片数据`);
      continue;
    }

    writeFileSync(outPath, Buffer.from(img.b64_json, "base64"));
    console.log(`测试成功: ${outPath}`);
    process.exit(0);
  } catch (e) {
    console.log(`  ${ep.name} 错误: ${e.message}`);
  }
}

console.error("所有服务均失败");
process.exit(1);
