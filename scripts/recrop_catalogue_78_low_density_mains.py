#!/usr/bin/env python3
"""Rebuild two low-density catalogue mains from 300 DPI source pages.

These products have isolated, complete catalogue views, but their original
storefront assets were extracted from low-resolution review renders. This
script re-renders only the two source pages, crops the exact front view, and
creates a square detail image plus a 4:5 list derivative on the shared
``#F3F3F5`` background. It does not redraw the garment.

XK-121 is intentionally excluded: its front view overlaps the adjacent angled
view in the flattened PDF, so a rectangular source crop cannot produce a
complete isolated main image.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "产品图册/catalogue-78-en.pdf"
WORK = ROOT / "output/catalogue-78-low-density-recrop"
BACKGROUND = np.array([243, 243, 245], dtype=np.float32)


@dataclass(frozen=True)
class CropSpec:
    stable_key: str
    sku: str
    page: int
    # Coordinates measured on the catalogue's existing 150 DPI review render.
    box_150_dpi: tuple[int, int, int, int]


SPECS = (
    CropSpec("xk-027-green-quick-drying-work-shirt", "xk-027", 18, (1285, 315, 1750, 960)),
    CropSpec("xk-059-stretch-utility-shorts", "xk-059", 36, (220, 270, 745, 930)),
)


def render_page(page: int) -> Path:
    output = WORK / f"page-{page}.png"
    if output.exists():
        return output
    subprocess.run(
        [
            "pdftoppm", "-f", str(page), "-l", str(page), "-r", "300",
            "-png", "-singlefile", str(PDF), str(WORK / f"page-{page}"),
        ],
        check=True,
    )
    return output


def edge_background(rgb: np.ndarray) -> np.ndarray:
    h, w = rgb.shape[:2]
    eh, ew = max(2, h // 80), max(2, w // 80)
    edge = np.concatenate((
        rgb[:eh].reshape(-1, 3), rgb[-eh:].reshape(-1, 3),
        rgb[:, :ew].reshape(-1, 3), rgb[:, -ew:].reshape(-1, 3),
    ))
    return np.median(edge, axis=0).astype(np.float32)


def isolate(crop: Image.Image) -> Image.Image:
    rgb = np.asarray(crop.convert("RGB"), dtype=np.uint8)
    background = edge_background(rgb)
    distance = np.linalg.norm(rgb.astype(np.float32) - background, axis=2)
    mask = distance > 22
    if int(mask.sum()) < 300:
        raise ValueError("No usable product foreground detected")
    ys, xs = np.where(mask)
    x0, x1 = np.quantile(xs, [0.001, 0.999]).astype(int)
    y0, y1 = np.quantile(ys, [0.001, 0.999]).astype(int)
    pad_x = max(8, round((x1 - x0 + 1) * 0.025))
    pad_y = max(8, round((y1 - y0 + 1) * 0.025))
    x0, y0 = max(0, x0 - pad_x), max(0, y0 - pad_y)
    x1, y1 = min(rgb.shape[1], x1 + pad_x + 1), min(rgb.shape[0], y1 + pad_y + 1)
    subject = rgb[y0:y1, x0:x1].astype(np.float32)
    local_distance = np.linalg.norm(subject - background, axis=2)
    alpha = np.clip((local_distance - 7.0) / 28.0, 0.0, 1.0)[..., None]
    matched = subject * alpha + BACKGROUND * (1.0 - alpha)
    return Image.fromarray(np.uint8(np.clip(matched, 0, 255)), "RGB")


def place(subject: Image.Image, canvas_size: tuple[int, int], box: tuple[int, int]) -> Image.Image:
    scale = min(box[0] / subject.width, box[1] / subject.height)
    size = (max(1, round(subject.width * scale)), max(1, round(subject.height * scale)))
    resized = subject.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", canvas_size, tuple(int(value) for value in BACKGROUND))
    canvas.paste(resized, ((canvas_size[0] - size[0]) // 2, (canvas_size[1] - size[1]) // 2))
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wordpress-root", type=Path)
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    manifest = []

    for spec in SPECS:
        page = Image.open(render_page(spec.page)).convert("RGB")
        box = tuple(value * 2 for value in spec.box_150_dpi)
        raw = page.crop(box)
        raw_path = WORK / f"{spec.sku}-source-300dpi.png"
        raw.save(raw_path, "PNG")
        subject = isolate(raw)

        detail_path = ROOT / f"assets/catalogue-78/main/{spec.sku}-front-high-source-v2.webp"
        detail_path.parent.mkdir(parents=True, exist_ok=True)
        detail = place(subject, (1400, 1400), (1160, 1160))
        detail.save(detail_path, "WEBP", quality=90, method=6)

        list_path = None
        if args.wordpress_root:
            list_path = args.wordpress_root / "wp-content/uploads/vasture-list-cards-v2" / f"{spec.stable_key}.webp"
            list_path.parent.mkdir(parents=True, exist_ok=True)
            listing = place(subject, (1000, 1250), (840, 1030))
            listing.save(list_path, "WEBP", quality=88, method=6)

        manifest.append({
            "stable_key": spec.stable_key,
            "sku": spec.sku,
            "source_page": spec.page,
            "source_crop_300_dpi": list(box),
            "detail_output": detail_path.relative_to(ROOT).as_posix(),
            "list_output": str(list_path) if list_path else None,
            "method": "300-dpi PDF recrop; no AI redraw",
        })

    manifest_path = WORK / "manifest.json"
    manifest_path.write_text(json.dumps({"items": manifest}, indent=2), encoding="utf-8")
    print(json.dumps({"generated": len(manifest), "manifest": str(manifest_path)}, indent=2))


if __name__ == "__main__":
    main()
