#!/usr/bin/env python3
"""Promote already-reviewed clean product assets into the storefront.

The source image that previously appeared as the main image is retained in
``detail_images`` as a wearing reference. This migration only uses assets that
already exist in the repository; it does not generate or crop any image.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

# product-id -> {old source path: reviewed clean replacement path}
MIGRATIONS = {
    "data/catalogue-a4-remaining.json": {
        "hv008f-reversible-fleece-body-warmer": {
            "assets/catalogue-a4/main/hv008f-hi-vis-yellow.webp": "assets/catalogue-a4/main/hv008f-hi-vis-yellow-clean.webp",
            "assets/catalogue-a4/main/hv008f-hi-vis-orange.webp": "assets/catalogue-a4/main/hv008f-hi-vis-orange-clean.webp",
        },
        "hvp300-classic-motorway-jacket": {
            "assets/catalogue-a4/main/hvp300-hi-vis-yellow.webp": "assets/catalogue-a4/main/hvp300-hi-vis-yellow-clean.webp",
            "assets/catalogue-a4/main/hvp300-hi-vis-orange.webp": "assets/catalogue-a4/main/hvp300-hi-vis-orange-clean.webp",
        },
        "hvp302-two-tone-motorway-jacket": {
            "assets/catalogue-a4/main/hvp302-hi-vis-yellow.webp": "assets/catalogue-a4/main/hvp302-hi-vis-yellow-clean.webp",
            "assets/catalogue-a4/main/hvp302-hi-vis-orange.webp": "assets/catalogue-a4/main/hvp302-hi-vis-orange-clean.webp",
        },
        "hvj220-two-tone-short-sleeve-polo": {
            "assets/catalogue-a4/main/hvj220-hi-vis-yellow.webp": "assets/catalogue-a4/main/hvj220-hi-vis-yellow-clean.webp",
            "assets/catalogue-a4/main/hvj220-hi-vis-orange.webp": "assets/catalogue-a4/main/hvj220-hi-vis-orange-clean.webp",
        },
        "hvj400-two-tone-short-sleeve-t-shirt": {
            "assets/catalogue-a4/main/hvj400-hi-vis-yellow.webp": "assets/catalogue-a4/main/hvj400-hi-vis-yellow-clean.webp",
            "assets/catalogue-a4/main/hvj400-hi-vis-orange.webp": "assets/catalogue-a4/main/hvj400-hi-vis-orange-clean.webp",
        },
        "hvj310-long-sleeve-polo": {
            "assets/catalogue-a4/main/hvj310-hi-vis-yellow.webp": "assets/catalogue-a4/main/hvj310-hi-vis-yellow-clean.webp",
            "assets/catalogue-a4/main/hvj310-hi-vis-orange.webp": "assets/catalogue-a4/main/hvj310-hi-vis-orange-clean.webp",
        },
        "hvj420-long-sleeve-t-shirt": {
            "assets/catalogue-a4/main/hvj420-hi-vis-yellow.webp": "assets/catalogue-a4/main/hvj420-hi-vis-yellow-clean.webp",
            "assets/catalogue-a4/main/hvj420-hi-vis-orange.webp": "assets/catalogue-a4/main/hvj420-hi-vis-orange-clean.webp",
        },
        "hvw068-rucksack-cover": {
            "assets/catalogue-a4/main/hvw068-hi-vis-yellow.webp": "assets/catalogue-a4/main/hvw068-hi-vis-yellow-clean.webp",
        },
    },
    "data/catalogue-78-public.json": {
        "xk-044-fr-stretch-pants": {
            "assets/catalogue-78/main/xk-044-front.webp": "assets/catalogue-78/main/xk-044-front-clean.webp",
        },
        "xk-011-fr-stretch-crew-neck-tee-shirt": {
            "assets/catalogue-78/main/xk-011-front.webp": "assets/catalogue-78/main/xk-011-front-clean.webp",
        },
        "xk-012-fr-crew-neck-tee-shirt": {
            "assets/catalogue-78/main/xk-012-front.webp": "assets/catalogue-78/main/xk-012-front-clean.webp",
        },
        "xk-013-fr-henley-shirt-raglan-sleeve": {
            "assets/catalogue-78/main/xk-013-front.webp": "assets/catalogue-78/main/xk-013-front-clean.webp",
        },
        "xk-070-flame-retardant-coverall": {
            "assets/catalogue-78/main/xk-070-front.webp": "assets/catalogue-78/main/xk-070-front-clean.webp",
        },
        "xk-072-inherent-fr-coverall": {
            "assets/catalogue-78/main/xk-072-front.webp": "assets/catalogue-78/main/xk-072-front-clean.webp",
        },
        "xk-073-offshore-anti-flame-coverall": {
            "assets/catalogue-78/main/xk-073-front.webp": "assets/catalogue-78/main/xk-073-front-clean.webp",
        },
        "xk-074-offshore-anti-flame-coverall": {
            "assets/catalogue-78/main/xk-074-front.webp": "assets/catalogue-78/main/xk-074-front-clean.webp",
        },
        "xk-078-pilot-coverall": {
            "assets/catalogue-78/main/xk-078-front.webp": "assets/catalogue-78/main/xk-078-front-clean.webp",
        },
        "xk-113-hi-vis-yellow-pullover-hoodie": {
            "assets/catalogue-78/main/xk-113-front.webp": "assets/catalogue-78/main/xk-113-front-clean.webp",
        },
    },
}


def update_dataset(relative_path: str, changes: dict[str, dict[str, str]]) -> int:
    path = ROOT / relative_path
    payload = json.loads(path.read_text(encoding="utf-8"))
    updated = 0
    for product in payload["products"]:
        replacements = changes.get(product["id"])
        if not replacements:
            continue
        original_main = product["main_image"]
        if original_main not in replacements and original_main not in replacements.values():
            raise ValueError(f"Unexpected main image for {product['id']}: {original_main}")
        detail_images = list(product.get("detail_images", []))
        for source in replacements:
            if source not in detail_images:
                detail_images.append(source)
        product["detail_images"] = detail_images
        product["wearing_reference"] = True
        product["main_image"] = replacements.get(original_main, original_main)
        for variant in product.get("color_variants", []):
            if variant["image"] in replacements:
                variant["image"] = replacements[variant["image"]]
        product["gallery_images"] = [replacements.get(image, image) for image in product.get("gallery_images", [])]
        updated += 1
    if updated != len(changes):
        raise ValueError(f"Expected {len(changes)} updates in {relative_path}, got {updated}")
    payload["updated_date"] = "2026-08-18"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return updated


def main() -> None:
    total = sum(update_dataset(path, changes) for path, changes in MIGRATIONS.items())
    print(f"Promoted {total} verified clean main images.")


if __name__ == "__main__":
    main()
