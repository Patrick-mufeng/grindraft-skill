#!/usr/bin/env python3
"""
grindraft-illustrate 生图脚本（Python）

替代原 generate-illustration.mjs（Node.js），提供完全一致的功能：
  读取 .env 配置 → 调用 OpenAI 兼容 API → 解码 b64_json → 保存 PNG

用法:
    python generate-illustration.py \\
        --prompt "..." \\
        --output "articles/{标题}_{日期}/illustrations/01-xxx.png" \\
        [--size "1024x576"] \\
        [--retries 2]

依赖: Python 3.9+, requests
模型: gpt-image-2（固定）

流程:
    1. 从项目根目录加载 .env（先）和 .grindraft/config.env（后覆盖）
    2. 调用 image-2 服务的 POST /v1/images/generations 生成图片
    3. 从返回的 b64_json 解码保存到本地
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print(json.dumps({
        "success": False,
        "error": "缺少依赖 requests，请执行: pip install requests"
    }))
    sys.exit(1)


# ── 配置加载 ─────────────────────────────────────────────────


def _parse_env_file(filepath: str) -> dict:
    """手动解析 .env 文件，返回 {key: value} 字典"""
    result = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                result[key.strip()] = val.strip()
    except (OSError, IOError):
        pass
    return result


def load_config(project_root: str) -> dict:
    """加载 .env → .grindraft/config.env（后者覆盖前者）

    与 Node.js 版行为完全一致：
      1. 先读项目根 .env
      2. 再读 .grindraft/config.env 覆盖同名键
      3. IMAGE2_BASE_URL 未设置时回退到 YUNWU_BASE_URL
    """
    candidates = [
        os.path.join(project_root, ".env"),
        os.path.join(project_root, ".grindraft", "config.env"),
    ]

    # 手动合并：先 .env，再 config.env 覆盖
    merged = {}
    for env_path in candidates:
        if os.path.isfile(env_path):
            merged.update(_parse_env_file(env_path))

    config = {
        "YUNWU_API_KEY": merged.get("YUNWU_API_KEY", ""),
        "YUNWU_BASE_URL": merged.get("YUNWU_BASE_URL", "https://yunwu.ai/"),
        "IMAGE2_BASE_URL": merged.get("IMAGE2_BASE_URL", ""),
    }

    # IMAGE2_BASE_URL 未显式设置时回退到 YUNWU_BASE_URL
    if not config["IMAGE2_BASE_URL"]:
        config["IMAGE2_BASE_URL"] = config["YUNWU_BASE_URL"]

    return config


# ── API 调用 ─────────────────────────────────────────────────


def call_generation_api(prompt: str, base_url: str, api_key: str,
                        size: str, timeout: int = 500) -> dict:
    """调用 OpenAI 兼容的 /v1/images/generations 接口

    参数:
        prompt: 英文提示词
        base_url: API 基础地址（如 https://yunwu.ai/）
        api_key: API Key
        size: 图片尺寸（如 "1024x576"）
        timeout: 超时秒数（默认 500s）
    返回:
        成功 → {"success": True, "data": <API 完整响应 dict>}
        失败 → {"success": False, "error": "..."}
    """
    aspect_map = {
        "1024x576": "16:9",
        "1024x1024": "1:1",
        "1792x1024": "16:9",
    }
    if size not in aspect_map:
        import sys as _sys
        print(json.dumps({"warning": f"[WARN] 未知尺寸 {size}，默认使用 16:9"}), file=_sys.stderr)
    aspect_ratio = aspect_map.get(size, "16:9")

    url = f"{base_url.rstrip('/')}/v1/images/generations"

    payload = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "n": 1,
        "aspect_ratio": aspect_ratio,
        "response_format": "b64_json",
    }

    headers = {
        "Content-Type": "application/json",
        **({"Authorization": f"Bearer {api_key}"} if api_key else {}),
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except requests.Timeout:
        return {"success": False, "error": f"API 请求超时（>{timeout}s）"}
    except requests.ConnectionError:
        return {"success": False, "error": f"无法连接 API 服务: {base_url}"}
    except requests.RequestException as e:
        return {"success": False, "error": f"网络异常: {e}"}

    if resp.status_code != 200:
        body = resp.text[:500]
        return {"success": False, "error": f"API 返回 {resp.status_code}: {body}"}

    try:
        data = resp.json()
    except (json.JSONDecodeError, ValueError):
        return {"success": False, "error": f"API 返回非 JSON 响应: {resp.text[:300]}"}

    if not data or "data" not in data or not data["data"]:
        return {"success": False, "error": f"API 返回数据异常: {json.dumps(data)[:300]}"}

    return {"success": True, "data": data}


# ── 图片保存 ─────────────────────────────────────────────────


def save_image(b64_data: str, output_path: str) -> None:
    """将 base64 图片数据解码并保存到文件"""
    import base64

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img_bytes = base64.b64decode(b64_data)
    with open(output_path, "wb") as f:
        f.write(img_bytes)


# ── 主流程 ─────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="grindraft-illustrate 生图脚本")
    parser.add_argument("--prompt", required=True, help="英文提示词")
    parser.add_argument("--output", required=True, help="输出 PNG 路径")
    parser.add_argument("--size", default="1024x576", help="图片尺寸（默认 1024x576）")
    parser.add_argument("--retries", type=int, default=2, help="失败重试次数（默认 2）")
    parser.add_argument("--project-root", default=None, help="项目根目录（默认从脚本位置自动推断）")
    args = parser.parse_args()

    # 确定项目根目录
    if args.project_root:
        project_root = os.path.abspath(args.project_root)
    else:
        # 从脚本位置向上: scripts/ -> grindraft-illustrate/ -> skills/ -> 项目根
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent.parent.parent  # 上 3 级
        project_root = str(project_root)

    # 加载配置
    config = load_config(project_root)

    if not config["YUNWU_API_KEY"] or not config["YUNWU_API_KEY"].startswith("sk-"):
        hint = ""
        if config["YUNWU_API_KEY"]:
            hint = f"（当前值以 {config['YUNWU_API_KEY'][:4]}... 开头，应为 sk-...）"
        print(json.dumps({
            "success": False,
            "error": f"YUNWU_API_KEY 未正确配置{hint}。请在 .env 或 .grindraft/config.env 中配置有效的 API Key（以 sk- 开头）",
        }))
        sys.exit(1)

    base_url = config["IMAGE2_BASE_URL"]
    api_key = config["YUNWU_API_KEY"]
    output_path = os.path.abspath(args.output)
    retries = args.retries

    errors = []
    for attempt in range(retries + 1):
        if attempt > 0:
            time.sleep(3)

        result = call_generation_api(
            prompt=args.prompt,
            base_url=base_url,
            api_key=api_key,
            size=args.size,
        )

        if not result["success"]:
            errors.append(f"第 {attempt + 1} 次: {result['error']}")
            continue

        images = result["data"].get("data", [])
        if not images:
            errors.append(f"第 {attempt + 1} 次: API 返回空图片列表")
            continue

        img = images[0]

        # 优先使用 b64_json
        if img.get("b64_json"):
            try:
                save_image(img["b64_json"], output_path)
                print(json.dumps({
                    "success": True,
                    "path": output_path,
                    "url": img.get("url", ""),
                    "attempts": attempt + 1,
                }))
                return
            except Exception as e:
                errors.append(f"第 {attempt + 1} 次: 图片保存失败: {e}")
                continue

        # 备选：从 URL 下载
        if img.get("url"):
            try:
                resp = requests.get(img["url"], timeout=60)
                if resp.status_code == 200:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, "wb") as f:
                        f.write(resp.content)
                    print(json.dumps({
                        "success": True,
                        "path": output_path,
                        "url": img["url"],
                        "attempts": attempt + 1,
                    }))
                    return
                errors.append(f"第 {attempt + 1} 次: 下载图片失败 HTTP {resp.status_code}")
            except Exception as e:
                errors.append(f"第 {attempt + 1} 次: 下载图片异常: {e}")
            continue

        errors.append(f"第 {attempt + 1} 次: API 返回数据中既无 b64_json 也无 url")

    # 全部重试失败
    print(json.dumps({
        "success": False,
        "error": errors[-1] if errors else "未知错误",
        "all_errors": errors,
        "attempts": retries + 1,
    }))
    sys.exit(1)


if __name__ == "__main__":
    main()
