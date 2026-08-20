#!/usr/bin/env python3
"""Re-crop complete A4 catalogue page-5 product views for storefront mains.

The prior assets for HVJ210, HVJ410, HVJ910 and HVW706 were cut from the
catalogue too tightly, despite the original PDF containing complete isolated
product views.  This script renders that source page at 400 dpi, extracts the
complete individual product areas, then applies the site's deterministic
``#F2F4F5`` background normalisation.  It only updates the listed products.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image

from build_tight_main_images import build_derivative


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "产品图册/catalogue-a4.pdf"
DATA = ROOT / "data/catalogue-a4-remaining.json"
WORK = ROOT / "output/catalogue-a4-page5-recrop"
RENDER = WORK / "catalogue-a4-page-5.png"
MANIFEST = ROOT / "data/catalogue-a4-page5-main-image-recrop-20260820.json"
SCALE = 2  # Coordinates were measured on a 200 dpi review render.

# Each crop includes the full isolated product only.  The normaliser removes
# the source's white paper background and puts it on the website's main-image
# background, while retaining the product pixels unchanged.
CROPS_200_DPI = {
    "hvj210": {
        "hi-vis-yellow": (858, 116, 1050, 308),
        "hi-vis-orange": (1052, 116, 1236, 308),
        "black": (1246, 116, 1433, 308),
        "navy": (1438, 116, 1642, 308),
    },
    "hvj410": {
        "hi-vis-yellow": (858, 404, 1052, 604),
        "hi-vis-orange": (1052, 404, 1238, 604),
        "black": (1246, 404, 1435, 604),
        "navy": (1438, 404, 1642, 604),
    },
    "hvj910": {
        "hi-vis-yellow": (858, 694, 1052, 912),
        "hi-vis-orange": (1052, 694, 1238, 912),
        "yellow-navy": (1246, 694, 1435, 912),
        "orange-navy": (1438, 694, 1642, 912),
    },
    "hvw706": {
        "hi-vis-yellow": (858, 1550, 1052, 1780),
        "hi-vis-orange": (1052, 1550, 1238, 1780),
        "black": (1246, 1550, 1435, 1780),
        "navy": (1438, 1550, 1548, 1780),
        "pink": (1549, 1550, 1655, 1780),
    },
}


def scaled(box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return tuple(value * SCALE for value in box)


def render_source() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["pdftoppm", "-f", "5", "-l", "5", "-r", "400", "-png", str(PDF), str(WORK / "catalogue-a4-page")],
        check=True,
    )
    generated = WORK / "catalogue-a4-page-5.png"
    if not generated.exists():
        raise FileNotFoundError(generated)


def main() -> None:
    render_source()
    page = Image.open(RENDER).convert("RGB")
    replacements: dict[str, str] = {}
    items: list[dict] = []

    for sku, variants in CROPS_200_DPI.items():
        for colour, box in variants.items():
            raw = WORK / f"{sku}-{colour}-source.png"
            final = ROOT / f"assets/catalogue-a4/main/{sku}-{colour}-clean.webp"
            page.crop(scaled(box)).save(raw, "PNG")
            result = build_derivative(raw, final)
            original = f"assets/catalogue-a4/main/{sku}-{colour}.webp"
            replacements[original] = final.relative_to(ROOT).as_posix()
            items.append({
                "sku": sku.upper(),
                "colour": colour,
                "original": original,
                **result,
            })

    payload = json.loads(DATA.read_text(encoding="utf-8"))
    # Explicit ids prevent an accidental update of similarly named assets.
    target_ids = {
        "hvj210-short-sleeve-polo",
        "hvj410-short-sleeve-t-shirt",
        "hvj910-top-cool-v-neck-t-shirt",
        "hvw706-kensington-jacket",
    }
    for product in payload["products"]:
        if product["id"] not in target_ids:
            continue
        product["main_image"] = replacements[product["main_image"]]
        product["gallery_images"] = [replacements.get(image, image) for image in product.get("gallery_images", [])]
        for variant in product.get("color_variants", []):
            variant["image"] = replacements.get(variant["image"], variant["image"])
        product["image_alt_zh"] = f"{product['name_zh']}完整单品图"
    payload["updated_date"] = "2026-08-20"
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    MANIFEST.write_text(json.dumps({
        "generated_at": "2026-08-20",
        "source": "产品图册/catalogue-a4.pdf page 5 rendered at 400 dpi",
        "background": "#F2F4F5",
        "purpose": "Replace incorrectly cropped A4 page-5 storefront product mains with complete isolated product views.",
        "items": items,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Re-cropped {len(items)} complete product assets.")


if __name__ == "__main__":
    main()
