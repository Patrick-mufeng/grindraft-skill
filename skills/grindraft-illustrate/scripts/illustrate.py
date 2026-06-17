#!/usr/bin/env python3
"""
grindraft 配图生成 — 独立调用脚本

用法:
    # 设置 API Key（只需设置一次）
    set YUNWU_API_KEY=sk-xxx          # Windows
    export YUNWU_API_KEY=sk-xxx       # macOS/Linux

    # 生成一张配图
    python illustrate.py --prompt "一只黑色小怪物在操作三台旧终端" --output demo.png

    # 指定尺寸和超时
    python illustrate.py --prompt "..." --output demo.png --size 1024x576 --timeout 300

    # 指定备选 API 地址
    python illustrate.py --prompt "..." --output demo.png --fallback-url https://备选地址/

依赖: Python 3.9+, requests（pip install requests）
模型: gpt-image-2（固定输出 16:9 / 1:1）
"""

import argparse
import base64
import json
import os
import sys
import time

try:
    import requests
except ImportError:
    print(json.dumps({"success": False, "error": "缺少依赖 requests，请执行: pip install requests"}))
    sys.exit(1)


# ── API 配置 ─────────────────────────────────────────────────


def load_api_config() -> dict:
    """从环境变量加载 API 配置（优先级：环境变量 > .env 文件）"""
    config = {
        "api_key": os.environ.get("YUNWU_API_KEY", ""),
        "base_url": os.environ.get("YUNWU_BASE_URL", "https://yunwu.ai/").rstrip("/"),
    }
    # 尝试从 .env 文件补充（如果有的话）
    for env_path in [".env", "../.env"]:
        if os.path.isfile(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, _, val = line.partition("=")
                        key = key.strip()
                        val = val.strip()
                        if key == "YUNWU_API_KEY" and not config["api_key"]:
                            config["api_key"] = val
                        elif key == "YUNWU_BASE_URL" and config["base_url"] == "https://yunwu.ai":
                            config["base_url"] = val.rstrip("/")
            except (OSError, IOError):
                pass
    return config


# ── 生图核心函数 ─────────────────────────────────────────────


def generate(prompt: str, output: str, *,
             api_key: str = "",
             base_url: str = "https://yunwu.ai",
             size: str = "1024x576",
             timeout: int = 300,
             retries: int = 2,
             fallback_url: str = "") -> dict:
    """生成配图的主函数——阻塞直到生成完成或重试耗尽

    参数:
        prompt: 英文提示词
        output: 输出 PNG 路径
        api_key: API Key（以 sk- 开头）
        base_url: API 地址
        size: 图片尺寸（1024x576 / 1024x1024 / 1792x1024）
        timeout: 每次 API 调用超时秒数
        retries: 失败重试次数
        fallback_url: 备选 API 地址（连续失败 2 次后自动切换）

    返回:
        成功 → {"success": true, "path": "xxx.png", "attempts": 1}
        失败 → {"success": false, "error": "...", "all_errors": [...]}
    """
    # ── 参数校验 ──
    if not api_key or not api_key.startswith("sk-"):
        return {"success": False, "error": "API Key 无效，需要以 sk- 开头。设置环境变量 YUNWU_API_KEY=sk-..."}

    if not output:
        return {"success": False, "error": "未指定输出路径（--output）"}

    aspect_map = {
        "1024x576": "16:9",
        "1024x1024": "1:1",
        "1792x1024": "16:9",
    }
    if size not in aspect_map:
        print(f"[WARN] 未知尺寸 {size}，默认 16:9", file=sys.stderr)
    aspect_ratio = aspect_map.get(size, "16:9")
    base_url = base_url.rstrip("/")

    payload = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "n": 1,
        "aspect_ratio": aspect_ratio,
        "response_format": "b64_json",
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    # ── 重试循环 ──
    all_errors = []
    used_fallback = False

    for attempt in range(retries + 1):
        if attempt > 0:
            wait = 3 * (3 ** (attempt - 1))  # 3s → 9s → 27s
            print(f"[INFO] 第 {attempt + 1} 次重试，等待 {wait}s...", file=sys.stderr)
            time.sleep(wait)

        # 连续失败 2 次后自动切换备选地址
        current_url = base_url
        if attempt >= 2 and fallback_url and not used_fallback:
            current_url = fallback_url.rstrip("/")
            used_fallback = True
            print(f"[INFO] 切换到备选 API: {current_url}", file=sys.stderr)

        # ── 连通性预检 ──
        try:
            r = requests.get(f"{current_url}/v1/models", headers=headers, timeout=5)
        except requests.RequestException:
            all_errors.append(f"第 {attempt + 1} 次: 无法连接 API 服务（{current_url}）")
            continue

        # ── 发请求 ──
        try:
            resp = requests.post(
                f"{current_url}/v1/images/generations",
                json=payload, headers=headers, timeout=timeout,
            )
        except requests.Timeout:
            all_errors.append(f"第 {attempt + 1} 次: 请求超时（>{timeout}s）")
            continue
        except requests.ConnectionError:
            all_errors.append(f"第 {attempt + 1} 次: 连接失败（{current_url}）")
            continue
        except requests.RequestException as e:
            all_errors.append(f"第 {attempt + 1} 次: 网络异常: {e}")
            continue

        # ── 解析响应 ──
        if resp.status_code != 200:
            all_errors.append(f"第 {attempt + 1} 次: API 返回 {resp.status_code}: {resp.text[:200]}")
            continue

        try:
            data = resp.json()
        except (json.JSONDecodeError, ValueError):
            all_errors.append(f"第 {attempt + 1} 次: API 返回非 JSON: {resp.text[:100]}")
            continue

        images = (data or {}).get("data", [])
        if not images:
            all_errors.append(f"第 {attempt + 1} 次: API 返回空列表")
            continue

        img = images[0]

        # ── 保存图片（优先 b64_json） ──
        if img.get("b64_json"):
            try:
                os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
                with open(output, "wb") as f:
                    f.write(base64.b64decode(img["b64_json"]))
                return {
                    "success": True,
                    "path": os.path.abspath(output),
                    "attempts": attempt + 1,
                }
            except Exception as e:
                all_errors.append(f"第 {attempt + 1} 次: 保存失败: {e}")
                continue

        # ── 回退：从 URL 下载 ──
        if img.get("url"):
            try:
                r = requests.get(img["url"], timeout=60)
                if r.status_code == 200:
                    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
                    with open(output, "wb") as f:
                        f.write(r.content)
                    return {
                        "success": True,
                        "path": os.path.abspath(output),
                        "attempts": attempt + 1,
                    }
                all_errors.append(f"第 {attempt + 1} 次: 下载失败 HTTP {r.status_code}")
            except Exception as e:
                all_errors.append(f"第 {attempt + 1} 次: 下载异常: {e}")
            continue

        all_errors.append(f"第 {attempt + 1} 次: 响应中无图片数据")

    # ── 全部失败 ──
    hint = "（已尝试主地址和备选地址）" if used_fallback else ""
    return {
        "success": False,
        "error": all_errors[-1] + hint if all_errors else "未知错误",
        "all_errors": all_errors,
        "attempts": retries + 1,
    }


# ── CLI 入口 ─────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="grindraft 配图生成 — 独立调用脚本")
    parser.add_argument("--prompt", "-p", required=True, help="英文提示词")
    parser.add_argument("--output", "-o", required=True, help="输出 PNG 路径")
    parser.add_argument("--size", "-s", default="1024x576",
                        choices=["1024x576", "1024x1024", "1792x1024"],
                        help="图片尺寸（默认 1024x576 16:9）")
    parser.add_argument("--timeout", "-t", type=int, default=300,
                        help="API 超时秒数（默认 300）")
    parser.add_argument("--retries", "-r", type=int, default=2,
                        help="失败重试次数（默认 2）")
    parser.add_argument("--fallback-url", "-f", default="",
                        help="备选 API 地址（主地址连续失败后自动切换）")
    parser.add_argument("--api-key", "-k", default="",
                        help="API Key（默认取 YUNWU_API_KEY 环境变量）")
    parser.add_argument("--base-url", "-b", default="",
                        help="API 地址（默认取 YUNWU_BASE_URL 环境变量，兜底 https://yunwu.ai）")
    parser.add_argument("--json", "-j", action="store_true",
                        help="只输出 JSON 结果，无人类可读信息")
    args = parser.parse_args()

    # 加载配置（环境变量 > .env > 命令行参数覆盖）
    env_config = load_api_config()
    api_key = args.api_key or env_config["api_key"]
    base_url = args.base_url or env_config["base_url"]

    if not args.json:
        print(f"[·] 生成中（{args.size}，超时 {args.timeout}s）...", file=sys.stderr)
        t0 = time.time()

    result = generate(
        prompt=args.prompt,
        output=args.output,
        api_key=api_key,
        base_url=base_url,
        size=args.size,
        timeout=args.timeout,
        retries=args.retries,
        fallback_url=args.fallback_url,
    )

    if not args.json:
        elapsed = time.time() - t0
        if result["success"]:
            print(f"[OK] 已保存: {result['path']}（{elapsed:.1f}s，{result['attempts']} 次尝试）", file=sys.stderr)
        else:
            print(f"[FAIL] {result['error']}", file=sys.stderr)

    # stdout 始终输出 JSON（便于程序解析）
    print(json.dumps(result, ensure_ascii=False))
    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
