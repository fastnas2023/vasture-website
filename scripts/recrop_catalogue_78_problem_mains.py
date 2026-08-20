#!/usr/bin/env python3
"""Replace incomplete or model-led catalogue mains with whole product views.

The catalogue contains complete front views for the products below, but earlier
imports used a too-tight or lifestyle crop.  This script re-renders the exact
source spread at 400 dpi, selects one complete front product per SKU, and
normalises it onto the storefront's #F2F4F5 main-image background.  It changes
only ``main_image``; original catalogue/lifestyle material remains available
in the detail gallery for reference.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image

from build_tight_main_images import build_derivative


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "产品图册/catalogue-78-en.pdf"
DATA = ROOT / "data/catalogue-78-public.json"
WORK = ROOT / "output/catalogue-78-main-recrop"
MANIFEST = ROOT / "data/catalogue-78-main-image-recrop-20260820.json"
SCALE = 2  # Crop coordinates were measured on 200 dpi review renders.

# page number, left, top, right, bottom (200 dpi).  Each box deliberately
# contains one full front product only; rear views, model photos and callouts
# are excluded from the primary image.
CROPS_200_DPI = {
    "xk-002-fr-solid-vent-work-shirt": (4, 1880, 380, 2210, 1260),
    "xk-003-inherent-lightweight-fr-rip-stop-work-shirt": (5, 365, 455, 950, 1480),
    "xk-008-women-s-non-fr-work-shirt": (7, 2535, 395, 3150, 1330),
    "xk-009-women-s-work-shirt": (8, 1080, 635, 1625, 1515),
    "xk-026-apple-green-work-shirt": (17, 1740, 505, 2310, 1295),
    "xk-076-flame-retardant-coverall": (45, 205, 395, 690, 2125),
    "xk-077-flame-retardant-coverall": (45, 2035, 1010, 2415, 2190),
    "xk-086-hi-vis-stretch-trousers": (50, 1730, 1040, 2015, 2150),
    "xk-090-4-way-stretch-cargo-pants": (51, 1880, 1320, 2140, 2160),
    "xk-095-stretch-reflective-softshell-jacket": (53, 330, 405, 720, 1365),
    "xk-096-stretch-reflective-softshell-jacket": (53, 2015, 405, 2480, 1370),
    "xk-105-inherent-lightweight-hi-vis-long-sleeve-shirt": (59, 400, 420, 920, 1465),
    "xk-106-inherent-fr-hi-vis-two-tone-work-shirt": (59, 1940, 430, 2450, 1465),
    "xk-107-fr-crew-neck-tee-shirt": (60, 350, 420, 895, 1435),
    "xk-111-multinorm-polo-shirt": (61, 900, 270, 1560, 1070),
    "xk-112-multinorm-polo-shirt": (61, 330, 1315, 950, 2190),
    "xk-127-hi-vis-cargo-suit": (68, 1950, 470, 2555, 1645),
    "xk-134-half-sleeved-fr-dual-stripe-mesh-vest": (70, 1800, 475, 2450, 1320),
    "xk-139-hi-vis-cargo-vest-and-short": (73, 2040, 435, 2535, 1425),
    "xk-141-high-visibility-birdseye-mesh-shirt": (74, 295, 410, 730, 1170),
    "xk-142-catalogue-product": (74, 295, 1390, 760, 2280),
    "xk-145-hi-vis-long-sleeves-birdseye-safety-t-shirt": (75, 1830, 1250, 2350, 2200),
}

# Rebuild only the entries whose crop coordinates were corrected during visual QA.
REBUILD_IDS = {
    "xk-002-fr-solid-vent-work-shirt",
    "xk-008-women-s-non-fr-work-shirt",
    "xk-086-hi-vis-stretch-trousers",
    "xk-090-4-way-stretch-cargo-pants",
    "xk-095-stretch-reflective-softshell-jacket",
    "xk-105-inherent-lightweight-hi-vis-long-sleeve-shirt",
    "xk-106-inherent-fr-hi-vis-two-tone-work-shirt",
    "xk-134-half-sleeved-fr-dual-stripe-mesh-vest",
    "xk-141-high-visibility-birdseye-mesh-shirt",
    "xk-142-catalogue-product",
    "xk-145-hi-vis-long-sleeves-birdseye-safety-t-shirt",
}


def render_page(page_number: int) -> Path:
    output = WORK / f"page-{page_number}.png"
    if output.exists():
        return output
    subprocess.run(
        [
            "pdftoppm", "-f", str(page_number), "-l", str(page_number),
            "-r", "400", "-png", "-singlefile", str(PDF), str(WORK / f"page-{page_number}"),
        ],
        check=True,
    )
    if not output.exists():
        raise FileNotFoundError(output)
    return output


def scale_box(box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return tuple(value * SCALE for value in box)


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    rendered: dict[int, Image.Image] = {}
    replacements: dict[str, str] = {}
    manifest_items: list[dict] = []

    for product_id, (page_number, *box) in CROPS_200_DPI.items():
        if page_number not in rendered:
            rendered[page_number] = Image.open(render_page(page_number)).convert("RGB")
        raw = WORK / f"{product_id}-source.png"
        output = ROOT / f"assets/catalogue-78/main/{product_id}-front-clean.webp"
        if not output.exists() or product_id in REBUILD_IDS:
            rendered[page_number].crop(scale_box(tuple(box))).save(raw, "PNG")
            result = build_derivative(raw, output)
        else:
            result = {
                "source": raw.relative_to(ROOT).as_posix(),
                "output": output.relative_to(ROOT).as_posix(),
                "method": "python-tight-crop-background-normalisation (reused)",
            }
        replacements[product_id] = output.relative_to(ROOT).as_posix()
        manifest_items.append({"product_id": product_id, "source_page": page_number, **result})

    payload = json.loads(DATA.read_text(encoding="utf-8"))
    updated = []
    for product in payload["products"]:
        replacement = replacements.get(product["id"])
        if not replacement:
            continue
        product["main_image"] = replacement
        product["image_alt_zh"] = f"{product['name_zh']}完整单品主图"
        updated.append(product["id"])
    if set(updated) != set(CROPS_200_DPI):
        missing = sorted(set(CROPS_200_DPI) - set(updated))
        raise ValueError(f"Missing product records: {missing}")
    payload["updated_date"] = "2026-08-20"
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "generated_at": "2026-08-20",
        "source": "产品图册/catalogue-78-en.pdf rendered at 400 dpi",
        "background": "#F2F4F5",
        "purpose": "Replace incomplete, composite or model-led product mains with a complete single-product front view.",
        "items": manifest_items,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Re-cropped {len(updated)} complete catalogue-78 main images.")


if __name__ == "__main__":
    main()
