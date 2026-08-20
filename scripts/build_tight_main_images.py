#!/usr/bin/env python3
"""Create tighter main-image derivatives from whitespace-heavy catalogue crops.

Only images already flagged by ``audit_product_main_images.py`` are considered.
The source garment pixels are retained; this is a deterministic crop and
background normalisation step, not an AI redraw. Each resulting image is a
4:3 WebP with a #F2F4F5 background so it matches the detail-page main-media
frame. A manifest records every source/output mapping for later CMS import.
"""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "output/main-image-audit-20260818/main-image-audit.json"
DATASETS = (ROOT / "data/products.json", ROOT / "data/catalogue-a4-remaining.json", ROOT / "data/catalogue-78-public.json")
MANIFEST = ROOT / "data/main-image-processing-20260818.json"
BACKGROUND = (242, 244, 245)
CANVAS = (1200, 900)


def image_mask(image: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    sample = np.asarray(image.convert("RGB").resize((400, 400), Image.Resampling.LANCZOS), dtype=np.int16)
    edge = np.concatenate((
        sample[:12].reshape(-1, 3), sample[-12:].reshape(-1, 3),
        sample[:, :12].reshape(-1, 3), sample[:, -12:].reshape(-1, 3),
    ))
    background = np.median(edge, axis=0)
    distance = np.linalg.norm(sample - background, axis=2)
    return distance > 28, background


def largest_component(mask: np.ndarray) -> tuple[np.ndarray, tuple[int, int, int, int, int]]:
    """Return the largest 8-connected foreground component without OpenCV."""
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    largest = (0, 0, 0, 0, 0)
    largest_cells: list[tuple[int, int]] = []
    for start_y, start_x in zip(*np.where(mask & ~seen)):
        if seen[start_y, start_x]:
            continue
        queue: deque[tuple[int, int]] = deque([(int(start_y), int(start_x))])
        seen[start_y, start_x] = True
        cells: list[tuple[int, int]] = []
        count = 0
        min_x = max_x = int(start_x)
        min_y = max_y = int(start_y)
        while queue:
            y, x = queue.popleft()
            cells.append((y, x))
            count += 1
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
            for ny in range(max(0, y - 1), min(height, y + 2)):
                for nx in range(max(0, x - 1), min(width, x + 2)):
                    if mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        queue.append((ny, nx))
        if count > largest[4]:
            largest = (min_x, min_y, max_x, max_y, count)
            largest_cells = cells
    component = np.zeros_like(mask, dtype=bool)
    if largest_cells:
        ys, xs = zip(*largest_cells)
        component[list(ys), list(xs)] = True
    return component, largest


def crop_box(image: Image.Image) -> tuple[int, int, int, int, list[float], np.ndarray]:
    mask, background = image_mask(image)
    component, (x0, y0, x1, y1, count) = largest_component(mask)
    if count < 120:
        raise ValueError("No usable foreground component")
    scale_x = image.width / 400
    scale_y = image.height / 400
    x0, x1 = x0 * scale_x, (x1 + 1) * scale_x
    y0, y1 = y0 * scale_y, (y1 + 1) * scale_y
    box_w, box_h = x1 - x0, y1 - y0
    # Retain 12% breathable space around the garment while making a 4:3 main image.
    target_w = box_w * 1.24
    target_h = box_h * 1.24
    if target_w / target_h < CANVAS[0] / CANVAS[1]:
        target_w = target_h * CANVAS[0] / CANVAS[1]
    else:
        target_h = target_w * CANVAS[1] / CANVAS[0]
    center_x, center_y = (x0 + x1) / 2, (y0 + y1) / 2
    left, top = center_x - target_w / 2, center_y - target_h / 2
    right, bottom = center_x + target_w / 2, center_y + target_h / 2
    return (round(left), round(top), round(right), round(bottom), background.tolist(), component)


def build_derivative(source: Path, destination: Path) -> dict:
    image = Image.open(source).convert("RGB")
    left, top, right, bottom, detected_background, component = crop_box(image)
    # Extend beyond the original crop with the site's exact main-image background.
    expanded = Image.new("RGB", (max(right - left, 1), max(bottom - top, 1)), BACKGROUND)
    paste_box = (-left, -top)
    component_mask = Image.fromarray((component * 255).astype(np.uint8), "L")
    component_mask = component_mask.resize(image.size, Image.Resampling.NEAREST)
    # A small dilation preserves anti-aliased garment edges while removing
    # detached catalogue labels, colour chips and explanatory callout lines.
    component_mask = component_mask.filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.GaussianBlur(1.2))
    expanded.paste(image, paste_box, component_mask)
    normalised = expanded
    normalised = normalised.resize(CANVAS, Image.Resampling.LANCZOS)
    normalised.save(destination, "WEBP", quality=92, method=6)
    return {
        "source": source.relative_to(ROOT).as_posix(),
        "output": destination.relative_to(ROOT).as_posix(),
        "source_size": [image.width, image.height],
        "output_size": list(CANVAS),
        "crop_box": [left, top, right, bottom],
        "detected_background_rgb": [round(value, 1) for value in detected_background],
        "method": "python-tight-crop-background-normalisation",
    }


def collect_target_products() -> set[str]:
    report = json.loads(AUDIT.read_text(encoding="utf-8"))
    return {record["id"] for record in report["candidates"] if record.get("flags") == ["suspected_too_small"]}


def output_path(relative_source: str) -> str:
    path = Path(relative_source)
    return str(path.with_name(f"{path.stem}-tight.webp"))


def main() -> None:
    targets = collect_target_products()
    mappings: dict[str, str] = {}
    if MANIFEST.exists():
        previous = json.loads(MANIFEST.read_text(encoding="utf-8"))
        mappings.update({
            item["source"]: item["output"]
            for item in previous.get("items", [])
            if not item["source"].endswith("-tight.webp")
        })
    for dataset in DATASETS:
        payload = json.loads(dataset.read_text(encoding="utf-8"))
        for product in payload["products"]:
            if product["id"] not in targets:
                continue
            image_paths = [product["main_image"]] + [item["image"] for item in product.get("color_variants", [])]
            for source_path in image_paths:
                if source_path.endswith("-tight.webp"):
                    continue
                mappings.setdefault(source_path, output_path(source_path))

    processed: list[dict] = []
    for source_path, target_path in sorted(mappings.items()):
        source, destination = ROOT / source_path, ROOT / target_path
        if not source.exists():
            raise FileNotFoundError(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        processed.append(build_derivative(source, destination))

    for dataset in DATASETS:
        payload = json.loads(dataset.read_text(encoding="utf-8"))
        changed = False
        for product in payload["products"]:
            if product["id"] not in targets:
                continue
            product["main_image"] = mappings.get(product["main_image"], product["main_image"])
            for variant in product.get("color_variants", []):
                variant["image"] = mappings.get(variant["image"], variant["image"])
            changed = True
        if changed:
            payload["updated_date"] = "2026-08-18"
            dataset.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    MANIFEST.write_text(json.dumps({
        "generated_at": "2026-08-18",
        "background": "#F2F4F5",
        "purpose": "Storefront main-image whitespace remediation; originals remain in assets for traceability.",
        "items": processed,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Processed {len(processed)} source images across {len(targets)} products.")


if __name__ == "__main__":
    main()
