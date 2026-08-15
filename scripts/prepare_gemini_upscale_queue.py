#!/usr/bin/env python3
"""Prepare a single-tab Gemini "保真放大" image queue.

This script only prepares local upload files and a manifest. Browser automation
reuses one signed-in Gemini tab, uploads one item at a time, and sends the exact
prompt stored here. Generated files still require visual review before import.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


PROMPT = "保真放大"
SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="准备 Gemini 保真放大任务队列")
    parser.add_argument("images", nargs="+", type=Path, help="待上传的产品图片")
    parser.add_argument("--product-id", required=True, help="产品 ID，例如 hvp211")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("tmp/gemini-upscale"),
        help="任务目录根路径",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    product_id = args.product_id.strip().lower()
    if not product_id:
        raise SystemExit("product-id 不能为空")

    sources = [image.expanduser().resolve() for image in args.images]
    for source in sources:
        if not source.is_file():
            raise SystemExit(f"找不到图片：{source}")
        if source.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise SystemExit(f"不支持的图片格式：{source.suffix}")

    task_dir = (args.output_root / product_id).resolve()
    upload_dir = task_dir / "uploads"
    result_dir = task_dir / "results"
    upload_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)

    items = []
    for index, source in enumerate(sources, start=1):
        upload_name = f"{product_id}-{index:02d}{source.suffix.lower()}"
        upload_path = upload_dir / upload_name
        shutil.copy2(source, upload_path)
        items.append({
            "index": index,
            "source_file": str(source),
            "upload_file": str(upload_path),
            "prompt": PROMPT,
            "expected_result_stem": f"{product_id}-{index:02d}-upscaled",
            "status": "pending",
        })

    manifest = {
        "schema_version": 1,
        "task_kind": "gemini_fidelity_upscale",
        "product_id": product_id,
        "prompt": PROMPT,
        "browser_policy": {
            "reuse_single_gemini_tab": True,
            "max_concurrent_uploads": 1,
        },
        "quality_gate": {
            "reject_if_structure_changed": True,
            "reject_if_colour_changed": True,
            "reject_if_trim_or_reflective_layout_changed": True,
            "requires_visual_review": True,
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "result_directory": str(result_dir),
        "items": items,
    }
    manifest_path = task_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(manifest_path)


if __name__ == "__main__":
    main()
