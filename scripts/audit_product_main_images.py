#!/usr/bin/env python3
"""Audit storefront product main images before changing any product data.

This script is deliberately conservative: it flags candidates for visual
review instead of attempting to decide that an image is defective on its own.
The report combines:

* foreground bounding-box / occupancy estimates for product images that look
  visually too small in the 4:3 storefront media frame;
* labelled contact sheets for the final human review, including a complete
  all-products set so model imagery can be identified accurately.

It never edits product JSON, generated pages, or assets.
"""

from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "data/products.json",
    ROOT / "data/catalogue-a4-remaining.json",
    ROOT / "data/catalogue-78-public.json",
)
OUTPUT = ROOT / "output/main-image-audit-20260818"
THUMBNAIL_SIZE = (260, 195)
SHEET_COLUMNS = 4
SHEET_ROWS = 4
LABEL_HEIGHT = 62


def load_products() -> list[dict]:
    products: list[dict] = []
    for path in DATASETS:
        products.extend(json.loads(path.read_text(encoding="utf-8"))["products"])
    ids = [product["id"] for product in products]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate product id found while auditing")
    return products


def readable_font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def foreground_metrics(image: Image.Image) -> dict[str, float | int]:
    """Estimate the visual foreground against a mostly uniform studio background."""
    rgb = np.asarray(image.convert("RGB").resize((400, 400), Image.Resampling.LANCZOS), dtype=np.int16)
    h, w, _ = rgb.shape
    edge = np.concatenate((
        rgb[:12].reshape(-1, 3),
        rgb[-12:].reshape(-1, 3),
        rgb[:, :12].reshape(-1, 3),
        rgb[:, -12:].reshape(-1, 3),
    ), axis=0)
    background = np.median(edge, axis=0)
    distance = np.linalg.norm(rgb - background, axis=2)
    # Textile pixels normally differ visibly from the border. With no native
    # computer-vision dependency in the site workspace, retain only pixels that
    # differ from that border and calculate the outer visual footprint. This is
    # intentionally a candidate signal, not an automatic crop decision.
    mask = distance > 28
    if int(mask.sum()) < 180:
        return {
            "bbox_width_ratio": 0.0,
            "bbox_height_ratio": 0.0,
            "foreground_area_ratio": 0.0,
            "edge_touch_count": 0,
        }
    ys, xs = np.where(mask)
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    edge_touch_count = sum((
        x0 <= 1,
        y0 <= 1,
        x1 >= w - 2,
        y1 >= h - 2,
    ))
    return {
        "bbox_width_ratio": round((x1 - x0 + 1) / w, 3),
        "bbox_height_ratio": round((y1 - y0 + 1) / h, 3),
        "foreground_area_ratio": round(float(mask.mean()), 3),
        "edge_touch_count": edge_touch_count,
    }


def classify(metrics: dict[str, float | int]) -> list[str]:
    flags: list[str] = []
    # Do not use a width-only condition: full-length coveralls and trousers are
    # legitimately narrow.  A short and narrow foreground, or a very low total
    # foreground area, is a better candidate for the "too small" review group.
    # Tall trousers, ties and narrow coveralls legitimately use little of a
    # landscape frame. Once a full subject reaches 55% of the media height it
    # has sufficient visual presence without violating the no-overfill rule.
    if metrics["bbox_height_ratio"] < 0.55 and metrics["bbox_width_ratio"] < 0.50:
        flags.append("suspected_too_small")
    if metrics["edge_touch_count"] >= 3:
        flags.append("suspected_incomplete_or_overcropped")
    return flags


def image_panel(record: dict) -> Image.Image:
    image = Image.open(ROOT / record["main_image"]).convert("RGB")
    image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (THUMBNAIL_SIZE[0], THUMBNAIL_SIZE[1] + LABEL_HEIGHT), "#f2f4f5")
    offset_x = (THUMBNAIL_SIZE[0] - image.width) // 2
    offset_y = (THUMBNAIL_SIZE[1] - image.height) // 2
    canvas.paste(image, (offset_x, offset_y))
    draw = ImageDraw.Draw(canvas)
    font = readable_font(15)
    small = readable_font(12)
    flags = ", ".join(record["flags"]) or "review"
    draw.rectangle((0, THUMBNAIL_SIZE[1], canvas.width, canvas.height), fill="#102b3a")
    draw.text((8, THUMBNAIL_SIZE[1] + 7), record["sku"] or record["id"], font=font, fill="white")
    draw.text(
        (8, THUMBNAIL_SIZE[1] + 31),
        f"{flags} | {record['bbox_width_ratio']:.2f}w {record['bbox_height_ratio']:.2f}h {record['foreground_area_ratio']:.2f}a",
        font=small,
        fill="#d8e3ea",
    )
    return canvas


def write_contact_sheets(records: list[dict], name: str) -> list[Path]:
    if not records:
        return []
    paths: list[Path] = []
    page_size = SHEET_COLUMNS * THUMBNAIL_SIZE[0], SHEET_ROWS * (THUMBNAIL_SIZE[1] + LABEL_HEIGHT)
    per_sheet = SHEET_COLUMNS * SHEET_ROWS
    for index in range(0, len(records), per_sheet):
        subset = records[index:index + per_sheet]
        sheet = Image.new("RGB", page_size, "#ffffff")
        for offset, record in enumerate(subset):
            panel = image_panel(record)
            x = (offset % SHEET_COLUMNS) * THUMBNAIL_SIZE[0]
            y = (offset // SHEET_COLUMNS) * (THUMBNAIL_SIZE[1] + LABEL_HEIGHT)
            sheet.paste(panel, (x, y))
        path = OUTPUT / f"{name}-{index // per_sheet + 1:02d}.jpg"
        sheet.save(path, quality=90, optimize=True)
        paths.append(path)
    return paths


def main() -> None:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)
    records: list[dict] = []
    for product in load_products():
        path = ROOT / product["main_image"]
        if not path.exists():
            records.append({
                "id": product["id"], "sku": product.get("sku"), "name_zh": product["name_zh"],
                "main_image": product["main_image"], "flags": ["missing_asset"],
            })
            continue
        image = Image.open(path)
        metrics = foreground_metrics(image)
        record = {
            "id": product["id"],
            "sku": product.get("sku"),
            "name_zh": product["name_zh"],
            "product_type": product["product_type"],
            "catalogue_id": product.get("catalogue_id"),
            "main_image": product["main_image"],
            "width": image.width,
            "height": image.height,
            **metrics,
        }
        record["flags"] = classify(metrics)
        records.append(record)

    candidates = [record for record in records if record.get("flags")]
    report = {
        "generated_at": "2026-08-18",
        "scope": "All public product main_image values. Candidate flags require visual review; no asset was changed.",
        "totals": {
            "products": len(records),
            "candidates": len(candidates),
            "by_flag": Counter(flag for record in candidates for flag in record["flags"]),
        },
        "candidates": candidates,
        "records": records,
    }
    (OUTPUT / "main-image-audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=dict), encoding="utf-8"
    )
    for flag in ("suspected_too_small", "suspected_incomplete_or_overcropped"):
        write_contact_sheets([record for record in candidates if flag in record["flags"]], flag)
    write_contact_sheets(candidates, "all-candidates")
    # Every main image is also output as compact sheets. Model detection is a
    # visual decision here because the local runtime does not include a face
    # detector; this avoids false claims from a weak heuristic.
    write_contact_sheets(records, "all-main-images")
    print(json.dumps(report["totals"], ensure_ascii=False, default=dict))
    print(f"Report: {OUTPUT / 'main-image-audit.json'}")


if __name__ == "__main__":
    main()
