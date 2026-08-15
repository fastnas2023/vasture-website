#!/usr/bin/env python3
"""Directly crop standalone product colour images from Catalogue A4.

Coordinates are recorded against the 250-DPI review renders so the script can
reuse the higher-resolution JPEG images embedded in the PDF. It does not use
AI generation, background replacement, or synthetic detail enhancement.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ORIGINALS = ROOT / "tmp/pdfs/catalogue-a4-originals"
OUTPUT = ROOT / "assets/catalogue-a4/main"
PREVIEW = ROOT / "tmp/pdfs/catalogue-a4-batch-preview"


@dataclass(frozen=True)
class ProductCrop:
    sku: str
    page: int
    box: tuple[int, int, int, int]
    colours: tuple[str, ...]
    slot_inset: int = 10


PRODUCTS = (
    ProductCrop("HVJ510", 1, (710, 575, 2075, 805), ("hi-vis-yellow", "hi-vis-orange", "yellow-navy", "orange-navy", "black", "navy")),
    ProductCrop("HVK05", 1, (710, 933, 2075, 1165), ("hi-vis-yellow", "hi-vis-orange", "yellow-navy", "orange-navy", "black", "navy"), 22),
    ProductCrop("HVK07", 1, (710, 1289, 2075, 1518), ("hi-vis-yellow", "hi-vis-orange", "yellow-navy", "orange-navy", "black", "navy"), 22),
    ProductCrop("HVK09", 1, (710, 1645, 2075, 1878), ("hi-vis-yellow", "hi-vis-orange", "yellow-navy", "orange-navy", "black", "navy")),
    ProductCrop("HV016T", 1, (710, 2005, 2075, 2247), ("hi-vis-yellow", "hi-vis-orange", "yellow-navy", "orange-navy", "black", "navy")),
    ProductCrop("HVK06", 1, (710, 2385, 1005, 2595), ("hi-vis-yellow", "hi-vis-orange"), 8),
    ProductCrop("HV006", 1, (1635, 2395, 2060, 2605), ("hi-vis-yellow", "hi-vis-orange", "yellow-navy", "orange-navy"), 7),
    ProductCrop("HVP711", 2, (1070, 500, 2075, 730), ("hi-vis-yellow", "hi-vis-orange", "yellow-navy", "orange-navy"), 8),
)


def trim_white(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white")).convert("L")
    mask = diff.point(lambda value: 255 if value > 28 else 0)
    box = mask.getbbox()
    if not box:
        return rgb
    left, top, right, bottom = box
    breathing = 8
    return rgb.crop((
        max(0, left - breathing),
        max(0, top - breathing),
        min(rgb.width, right + breathing),
        min(rgb.height, bottom + breathing),
    ))


def product_canvas(image: Image.Image) -> Image.Image:
    image = trim_white(image)
    scale = min(760 / image.width, 760 / image.height, 3.0)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    image = image.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (1000, 1000), "white")
    canvas.paste(image, ((1000 - image.width) // 2, (1000 - image.height) // 2))
    return canvas


def extract_product(config: ProductCrop) -> list[Path]:
    source = Image.open(ORIGINALS / f"page-{config.page}.jpg").convert("RGB")
    review = Image.open(ROOT / f"tmp/pdfs/catalogue-a4-render/page-{config.page}.jpg")
    sx, sy = source.width / review.width, source.height / review.height
    x1, y1, x2, y2 = config.box
    x1, y1, x2, y2 = round(x1 * sx), round(y1 * sy), round(x2 * sx), round(y2 * sy)
    width = x2 - x1
    paths: list[Path] = []
    for index, colour in enumerate(config.colours):
        left = x1 + round(width * index / len(config.colours))
        right = x1 + round(width * (index + 1) / len(config.colours))
        inset = round(config.slot_inset * sx)
        crop = source.crop((left + inset, y1, right - inset, y2))
        output = OUTPUT / f"{config.sku.lower()}-{colour}.webp"
        product_canvas(crop).save(output, "WEBP", quality=90, method=6)
        paths.append(output)
    return paths


def build_preview(config: ProductCrop, paths: list[Path]) -> None:
    thumb_size = 320
    label_height = 58
    columns = min(4, len(paths))
    rows = (len(paths) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_size, rows * (thumb_size + label_height)), "#e8edf0")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=24)
    for index, (colour, path) in enumerate(zip(config.colours, paths)):
        image = Image.open(path).convert("RGB").resize((thumb_size, thumb_size), Image.Resampling.LANCZOS)
        x = (index % columns) * thumb_size
        y = (index // columns) * (thumb_size + label_height)
        sheet.paste(image, (x, y))
        draw.text((x + 12, y + thumb_size + 12), colour, fill="#152a35", font=font)
    sheet.save(PREVIEW / f"{config.sku.lower()}-colours.jpg", "JPEG", quality=92)


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    for config in PRODUCTS:
        paths = extract_product(config)
        build_preview(config, paths)
        print(f"{config.sku}: {len(paths)} direct crops")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
