#!/usr/bin/env python3
"""Promote the reviewed 2026-09-10 main-image replacements in source data."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "data/catalogue-a4-remaining.json",
    ROOT / "data/catalogue-78-public.json",
)
REPLACEMENTS = {
    "hvj259-reflective-border-tabard": "assets/catalogue-a4/main/hvj259-hi-vis-yellow-ai-v2.webp",
    "hvj910-top-cool-v-neck-t-shirt": "assets/catalogue-a4/main/hvj910-hi-vis-yellow-ai-v2.webp",
    "hvw706-kensington-jacket": "assets/catalogue-a4/main/hvw706-hi-vis-yellow-ai-v2.webp",
    "hvw066-print-me-arm-bands": "assets/catalogue-a4/main/hvw066-hi-vis-yellow-ai-v2.webp",
    "xk-027-green-quick-drying-work-shirt": "assets/catalogue-78/main/xk-027-front-high-source-v2.webp",
    "xk-059-stretch-utility-shorts": "assets/catalogue-78/main/xk-059-front-high-source-v2.webp",
    "xk-121-hi-vis-waterproof-jacket": "assets/catalogue-78/main/xk-121-front-ai-v2.webp",
}


def main() -> None:
    changed: dict[str, list[str]] = {}
    seen: set[str] = set()
    for dataset in DATASETS:
        payload = json.loads(dataset.read_text(encoding="utf-8"))
        dataset_changed = []
        for product in payload["products"]:
            replacement = REPLACEMENTS.get(product["id"])
            if not replacement:
                continue
            previous = product["main_image"]
            product["main_image"] = replacement
            product["image_alt_zh"] = f"{product['name_zh']}完整单品主图"
            product["gallery_images"] = [
                replacement if image == previous else image
                for image in product.get("gallery_images", [])
            ]
            variants = product.get("color_variants", [])
            if variants and variants[0].get("image") == previous:
                variants[0]["image"] = replacement
            product["main_image_review"] = {
                "status": "reviewed",
                "date": "2026-09-10",
                "previous": previous,
                "method": "300-dpi-pdf-recrop" if "high-source" in replacement else "reviewed-ai-restoration",
            }
            dataset_changed.append(product["id"])
            seen.add(product["id"])
        dataset.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        changed[dataset.relative_to(ROOT).as_posix()] = dataset_changed

    missing = sorted(set(REPLACEMENTS) - seen)
    if missing:
        raise RuntimeError(f"Products missing from source datasets: {missing}")
    print(json.dumps({"changed": changed}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
