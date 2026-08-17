#!/usr/bin/env python3
"""Move the remaining known model image out of the XK-029 main-image slot."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/catalogue-78-public.json"
CLEAN = "assets/catalogue-78/main/xk-029-front-clean.webp"
MODEL = "assets/catalogue-78/main/xk-029-front.webp"


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    product = next(item for item in payload["products"] if item["id"] == "xk-029-fr-pull-over-hoodie")
    product["main_image"] = CLEAN
    product["color_variants"][0].update({
        "label_zh": "藏青色",
        "label_en": "Navy",
        "image": CLEAN,
    })
    details = list(product.get("detail_images", []))
    if MODEL not in details:
        details.append(MODEL)
    product["detail_images"] = details
    product["wearing_reference"] = True
    payload["updated_date"] = "2026-08-18"
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Moved XK-029 model imagery into detail_images.")


if __name__ == "__main__":
    main()
