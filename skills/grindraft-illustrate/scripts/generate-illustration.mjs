/**
 * grindraft-illustrate 生图脚本（Node.js）
 *
 * 用法:
 *   node generate-illustration.mjs \
 *     --prompt "..." \
 *     --output "articles/{标题}_{日期}/illustrations/01-xxx.png" \
 *     [--size "1024x576"] \
 *     model: gpt-image-2（固定）
 *
 * 依赖: Node.js 18+（fetch 内置，零 npm 依赖）
 *
 * 流程:
 *   1. 从项目根目录 .env 读取 IMAGE2_BASE_URL
 *   2. 调用 image-2 服务的 POST /v1/images/generations 生成图片
 *   3. 从返回的 URL/base64 保存到本地
 */

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { env } from "node:process";

// ── 解析 args ──────────────────────────────────────────────

function parseArgs() {
  const args = {};
  const raw = process.argv.slice(2);
  for (let i = 0; i < raw.length; i++) {
    const key = raw[i].replace(/^--/, "");
    if (key === "prompt") args.prompt = raw[++i];
    if (key === "output") args.output = raw[++i];
    if (key === "size") args.size = raw[++i];
    if (key === "retries") args.retries = parseInt(raw[++i], 10);
    if (key === "project-root") args.projectRoot = raw[++i];
  }
  args.size ??= "1024x576";
  args.retries ??= 2;
  return args;
}

// ── .env 加载 ──────────────────────────────────────────────

function loadEnv(projectRoot) {
  const defaults = {
    IMAGE2_BASE_URL: "",
    YUNWU_API_KEY: "",
    YUNWU_BASE_URL: "https://yunwu.ai/",
  };

  // 读取优先级：.grindraft/config.env > 根目录 .env（后者先加载，前者覆盖）
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

// ── API 调用 ───────────────────────────────────────────────

async function generateViaImage2(prompt, baseUrl, model, size, config = {}, timeout = 500_000) {
  const aspectMap = { "1024x576": "16:9", "1024x1024": "1:1", "1792x1024": "16:9" };
  const aspectRatio = aspectMap[size] || "16:9";

  const url = `${baseUrl.replace(/\/+$/, "")}/v1/images/generations`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);

  try {
    const resp = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(config?.YUNWU_API_KEY ? { "Authorization": `Bearer ${config.YUNWU_API_KEY}` } : {}),
      },
      body: JSON.stringify({
        model,
        prompt,
        n: 1,
        aspect_ratio: aspectRatio,
        response_format: "b64_json",
      }),
      signal: controller.signal,
    });

    clearTimeout(timer);

    if (!resp.ok) {
      const errBody = await resp.text(); return { success: false, error: `image-2 返回 ${resp.status}: ${errBody.slice(0, 500)}` };
    }

    const data = await resp.json();
    if (!data || !data.data || !data.data.length) {
      return { success: false, error: `image-2 返回数据异常: ${JSON.stringify(data).slice(0, 300)}` };
    }

    return { success: true, data };
  } catch (err) {
    clearTimeout(timer);
    if (err.name === "AbortError") return { success: false, error: `image-2 请求超时（>${timeout / 1000}s）` };
    if (err.code === "ECONNREFUSED") return { success: false, error: `无法连接 image-2 服务 ${baseUrl}` };
    return { success: false, error: `网络异常: ${err.message}` };
  }
}

// ── 图片保存 ───────────────────────────────────────────────

function saveImage(data, outputPath) {
  mkdirSync(dirname(outputPath), { recursive: true });
  writeFileSync(outputPath, data);
}

// ── 主流程 ─────────────────────────────────────────────────

async function main() {
  const args = parseArgs();
  const cwd = process.cwd();

  // 确定项目根目录
  let projectRoot;
  if (args.projectRoot) {
    projectRoot = resolve(cwd, args.projectRoot);
  } else {
    // 从脚本位置向上找：scripts/ -> grindraft-illustrate/ -> skills/ -> 项目根
    const scriptDir = dirname(new URL(import.meta.url).pathname);
    projectRoot = resolve(scriptDir, "../../..");
  }

  const config = loadEnv(projectRoot);
  // IMAGE2_BASE_URL 未设置时从 YUNWU_BASE_URL 继承（文档：IMAGE2_BASE_URL 默认同 YUNWU_BASE_URL）
  if (!config.IMAGE2_BASE_URL) {
    config.IMAGE2_BASE_URL = config.YUNWU_BASE_URL;
  }
  const image2BaseUrl = config.IMAGE2_BASE_URL;
  const outputPath = resolve(cwd, args.output);
  const retries = args.retries;

  let lastError;
  for (let attempt = 0; attempt <= retries; attempt++) {
    if (attempt > 0) await new Promise((r) => setTimeout(r, 3000));

    const result = await generateViaImage2(args.prompt, image2BaseUrl, "gpt-image-2", args.size, config);
    if (!result.success) { lastError = result.error; continue; }

    const images = result.data.data || [];
    if (!images.length) { lastError = "image-2 返回空图片列表"; continue; }

    const img = images[0];
    let buf = null;

    if (img.b64_json) {
      buf = Buffer.from(img.b64_json, "base64");
    } else if (img.url) {
      const resp = await fetch(img.url);
      if (resp.ok) buf = Buffer.from(await resp.arrayBuffer());
    } else if (img.local_path) {
      const localPath = img.local_path.startsWith("/") ? img.local_path : `/${img.local_path}`;
      const resp = await fetch(`${image2BaseUrl.replace(/\/+$/, "")}${localPath}`);
      if (resp.ok) buf = Buffer.from(await resp.arrayBuffer());
    }

    if (!buf) { lastError = "无法获取图片数据"; continue; }

    saveImage(buf, outputPath);
    console.log(JSON.stringify({
      success: true,
      path: outputPath,
      url: img.url || "",
      attempts: attempt + 1,
    }));
    return;
  }

  console.log(JSON.stringify({
    success: false,
    error: lastError || "未知错误",
    attempts: retries + 1,
  }));
  process.exit(1);
}

main().catch((err) => {
  console.log(JSON.stringify({ success: false, error: err.message }));
  process.exit(1);
});
