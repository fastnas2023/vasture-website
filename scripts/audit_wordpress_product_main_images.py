#!/usr/bin/env python3
"""Create a conservative visual-review pack for current WordPress product mains.

The site currently serves WordPress media, so the old JSON-asset audit cannot
describe the images visitors see. This script reads published product thumbnails
from the local WordPress runtime, measures only safe candidate signals, and
creates labelled contact sheets for a human visual decision. It never changes
the database, product metadata, or image files.
"""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
WP_LOAD = Path('/Users/zhangjianhua/zsxgarment.test/wp-load.php')
OUTPUT = ROOT / 'tmp/wp-main-image-audit-20260826'
THUMB = (256, 192)
LABEL_HEIGHT = 62
COLS = 4
ROWS = 4


def published_products() -> list[dict]:
    php = r'''require $argv[1]; $query = new WP_Query([
      'post_type' => 'vasture_product', 'post_status' => 'publish',
      'posts_per_page' => -1, 'fields' => 'ids', 'orderby' => 'ID', 'order' => 'ASC'
    ]); $items = []; foreach ($query->posts as $id) {
      $attachment = get_post_thumbnail_id($id);
      $items[] = ['post_id' => $id, 'product_id' => (string) get_post_meta($id, '_vasture_product_id', true),
        'title' => get_the_title($id), 'attachment_id' => $attachment, 'file' => $attachment ? get_attached_file($attachment) : ''];
    } echo wp_json_encode($items, JSON_UNESCAPED_UNICODE);'''
    result = subprocess.run(['php', '-r', php, str(WP_LOAD)], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def metrics(path: Path) -> dict[str, float | int]:
    rgb = np.asarray(Image.open(path).convert('RGB').resize((400, 400), Image.Resampling.LANCZOS), dtype=np.int16)
    edge = np.concatenate((rgb[:14].reshape(-1, 3), rgb[-14:].reshape(-1, 3), rgb[:, :14].reshape(-1, 3), rgb[:, -14:].reshape(-1, 3)))
    background = np.median(edge, axis=0)
    distance = np.linalg.norm(rgb - background, axis=2)
    mask = distance > 28
    edge_spread = np.linalg.norm(edge - background, axis=1)
    if int(mask.sum()) < 180:
        return {'bbox_width_ratio': 0.0, 'bbox_height_ratio': 0.0, 'foreground_area_ratio': 0.0, 'edge_touch_count': 0, 'edge_variation': round(float(np.percentile(edge_spread, 90)), 1)}
    ys, xs = np.where(mask)
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    return {
        'bbox_width_ratio': round((x1 - x0 + 1) / 400, 3),
        'bbox_height_ratio': round((y1 - y0 + 1) / 400, 3),
        'foreground_area_ratio': round(float(mask.mean()), 3),
        'edge_touch_count': sum((x0 <= 1, y0 <= 1, x1 >= 398, y1 >= 398)),
        'edge_variation': round(float(np.percentile(edge_spread, 90)), 1),
    }


def flags(value: dict[str, float | int]) -> list[str]:
    found: list[str] = []
    if value['edge_touch_count'] >= 3:
        found.append('possible_incomplete_or_overcrop')
    if value['bbox_height_ratio'] < 0.55 and value['bbox_width_ratio'] < 0.50:
        found.append('possible_too_small')
    # Uniform studio backgrounds normally have a low border variation. High
    # variation can also be a legitimate lifestyle shot, so it remains review-
    # only rather than an automated background replacement decision.
    if value['edge_variation'] > 62:
        found.append('possible_unclean_or_scene_background')
    return found


def font(size: int) -> ImageFont.ImageFont:
    candidate = Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf')
    return ImageFont.truetype(candidate, size=size) if candidate.exists() else ImageFont.load_default()


def panel(item: dict) -> Image.Image:
    image = Image.open(item['file']).convert('RGB')
    image.thumbnail(THUMB, Image.Resampling.LANCZOS)
    canvas = Image.new('RGB', (THUMB[0], THUMB[1] + LABEL_HEIGHT), '#f2f4f5')
    canvas.paste(image, ((THUMB[0] - image.width) // 2, (THUMB[1] - image.height) // 2))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, THUMB[1], canvas.width, canvas.height), fill='#102b3a')
    draw.text((8, THUMB[1] + 6), item['product_id'] or str(item['post_id']), font=font(14), fill='white')
    draw.text((8, THUMB[1] + 28), ', '.join(item['flags']) or 'visual review', font=font(10), fill='#d8e3ea')
    return canvas


def contact_sheets(items: list[dict], prefix: str) -> list[str]:
    paths: list[str] = []
    per_sheet = COLS * ROWS
    size = (COLS * THUMB[0], ROWS * (THUMB[1] + LABEL_HEIGHT))
    for start in range(0, len(items), per_sheet):
        sheet = Image.new('RGB', size, '#fff')
        for offset, item in enumerate(items[start:start + per_sheet]):
            x, y = (offset % COLS) * THUMB[0], (offset // COLS) * (THUMB[1] + LABEL_HEIGHT)
            sheet.paste(panel(item), (x, y))
        destination = OUTPUT / f'{prefix}-{start // per_sheet + 1:02d}.jpg'
        sheet.save(destination, quality=88, optimize=True)
        paths.append(str(destination))
    return paths


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    for item in published_products():
        path = Path(item['file']) if item['file'] else None
        if not path or not path.exists():
            records.append({**item, 'flags': ['missing_main_image']})
            continue
        value = metrics(path)
        records.append({**item, **value, 'flags': flags(value)})
    candidates = [record for record in records if record['flags']]
    report = {
        'scope': 'Current local WordPress published product thumbnails; candidate flags require visual review.',
        'totals': {'products': len(records), 'candidates': len(candidates), 'by_flag': Counter(flag for item in candidates for flag in item['flags'])},
        'candidates': candidates,
        'contact_sheets': {
            'candidates': contact_sheets(candidates, 'candidates'),
            'all': contact_sheets(records, 'all-main-images'),
        },
    }
    (OUTPUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, default=dict), encoding='utf-8')
    print(json.dumps(report['totals'], ensure_ascii=False, default=dict))
    print(OUTPUT / 'report.json')


if __name__ == '__main__':
    main()
