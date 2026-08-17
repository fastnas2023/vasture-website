#!/usr/bin/env python3
"""Repair a failed second-pass suffix without changing any source imagery."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (ROOT / "data/products.json", ROOT / "data/catalogue-a4-remaining.json", ROOT / "data/catalogue-78-public.json")


def normalise(path: str) -> str:
    while "-tight-tight.webp" in path:
        path = path.replace("-tight-tight.webp", "-tight.webp")
    return path


def main() -> None:
    changed = 0
    for dataset in DATASETS:
        payload = json.loads(dataset.read_text(encoding="utf-8"))
        for product in payload["products"]:
            old = product["main_image"]
            product["main_image"] = normalise(old)
            changed += old != product["main_image"]
            for variant in product.get("color_variants", []):
                old = variant["image"]
                variant["image"] = normalise(old)
                changed += old != variant["image"]
        dataset.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Repaired {changed} product-image references.")


if __name__ == "__main__":
    main()
