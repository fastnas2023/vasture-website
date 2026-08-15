#!/usr/bin/env python3
"""Build public website records from reviewed Catalogue 78 crop drafts.

The source catalogue is flattened artwork. This script publishes only the
reviewed product-level crops and keeps supplier claims out of public copy.
Confirmed colour variants are merged into one website product.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "data/catalogue-78-products-draft.json"
INVENTORY = ROOT / "data/catalogue-78-inventory.json"
OUTPUT = ROOT / "data/catalogue-78-public.json"

VARIANT_LABELS = {
    "xk-017-018-multinorm-sweatshirt": {
        "XK-017": ("荧光黄", "Hi Vis Yellow"),
        "XK-018": ("藏青色", "Navy Blue"),
    },
    "xk-029-033-pullover-hoodie": {
        "XK-029": ("藏青色模特参考", "Navy Model Reference"),
        "XK-030": ("浅灰色", "Light Grey"),
        "XK-031": ("深灰色", "Dark Grey"),
        "XK-032": ("黑色", "Black"),
        "XK-033": ("黄色", "Yellow"),
    },
    "xk-047-048-cotton-fr-jeans": {
        "XK-047": ("直筒款", "Straight Leg"),
        "XK-048": ("工装口袋款", "Cargo Pocket"),
    },
    "xk-149-150-womens-reflective-shirts": {
        "XK-149": ("连续反光带", "Solid Reflective Tape"),
        "XK-150": ("分段反光带", "Segmented Reflective Tape"),
    },
}

TYPE_NORMALIZATION = {
    "tshirt": "workshirt",
    "polo": "workshirt",
    "sweatshirt": "hoodie",
    "bibs": "coverall",
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "catalogue-product"


def product_tags(product_type: str, title: str) -> list[str]:
    lowered = title.lower()
    tags = [product_type, "workwear", "catalogue"]
    rules = {
        "reflective": ("hi-vis", "hi vis", "visibility", "reflective"),
        "stretch": ("stretch",),
        "waterproof": ("waterproof", "rainwear"),
        "winter": ("winter", "insulated"),
        "mesh": ("mesh", "birdseye"),
        "functional": ("cargo", "utility", "multi-pocket", "multi pocket"),
        "outdoor": ("outdoor", "rainwear", "waterproof"),
        "polo": ("polo",),
        "hoodie": ("hoodie", "sweatshirt"),
        "knitwear": ("hoodie", "sweatshirt", "sweater"),
        "flame-resistant": ("flame", "anti-flame", " fr ", "multinorm"),
    }
    padded = f" {lowered} "
    for tag, needles in rules.items():
        if any(needle in padded for needle in needles):
            tags.append(tag)
    if product_type == "workshirt":
        tags.append("business")
    return list(dict.fromkeys(tags))


def display_sku(records: list[dict]) -> str:
    if len(records) == 1:
        return records[0]["sku"]
    numbers = [record["sku"].removeprefix("XK-") for record in records]
    return f"XK-{'/'.join(numbers)}"


def choose_main(records: list[dict]) -> dict:
    clean = [
        record for record in records
        if record["crop_status"].startswith("reviewed-clean")
    ]
    return clean[0] if clean else records[0]


def main() -> None:
    drafts = json.loads(DRAFT.read_text(encoding="utf-8"))["products"]
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    inventory_by_sku = {product["sku"]: product for product in inventory["products"]}

    grouped: dict[str, list[dict]] = {}
    group_order: list[str] = []
    for record in drafts:
        group_id = record.get("variant_group_id") or record["sku"]
        if group_id not in grouped:
            grouped[group_id] = []
            group_order.append(group_id)
        grouped[group_id].append(record)

    products = []
    for index, group_id in enumerate(group_order, start=70):
        records = grouped[group_id]
        anchor = choose_main(records)
        pages = sorted({page for record in records for page in record["source_pages"]})
        product_type = TYPE_NORMALIZATION.get(anchor["product_type"], anchor["product_type"])
        title_en = anchor["name_en"]
        title_zh = anchor["name_zh"]
        sku_label = display_sku(records)
        product_id = f"{records[0]['sku'].lower()}-{slugify(title_en)}"
        unresolved = any(inventory_by_sku[record["sku"]]["title_en"] is None for record in records)
        public_title_en = f"{sku_label} {'Catalogue Product' if unresolved else title_en.upper()}"
        public_title_zh = f"{sku_label} {'画册款式（名称待确认）' if unresolved else title_zh}"
        page_label = "、".join(str(page) for page in pages)
        description = (
            f"英文工作服画册第{page_label}页产品资料，用于选款、询价与OEM/ODM沟通。"
            "具体面料、颜色、功能标准、认证、库存与起订条件需按订单确认。"
        )

        labels = VARIANT_LABELS.get(group_id, {})
        variants = [
            {
                "label_zh": labels.get(record["sku"], (record["sku"], record["sku"]))[0],
                "label_en": labels.get(record["sku"], (record["sku"], record["sku"]))[1],
                "image": record["main_image"],
            }
            for record in records
        ] if len(records) > 1 else []

        products.append({
            "id": product_id,
            "sku": sku_label,
            "name_zh": public_title_zh,
            "name_en": public_title_en,
            "description_zh": description,
            "product_type": product_type,
            "tags": product_tags(product_type, title_en),
            "main_image": anchor["main_image"],
            "image_alt_zh": f"{public_title_zh}画册单品参考图",
            "gallery_images": [record["main_image"] for record in records] if len(records) > 1 else [],
            "color_variants": variants,
            "badge": "英文画册",
            "supply_mode": "catalogue_inquiry",
            "moq_label": "供货",
            "moq_value": "询价确认",
            "stock_status": "not_claimed",
            "catalogue_id": "catalogue-78-en",
            "catalogue_name": "Safety Workwear Catalogue (English, 78 pages)",
            "source_file": "产品图册/catalogue-78-en.pdf",
            "source_pages": pages,
            "added_date": "2026-08-15",
            "source_status": "catalogue_linked",
            "visibility": "public",
            "sort_order": index,
        })

    payload = {
        "schema_version": 1,
        "updated_date": "2026-08-15",
        "asset_base_url": "https://fastnas2023.github.io/vasture-website/",
        "products": products,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(products)} public products from {len(drafts)} source SKUs -> {OUTPUT}")


if __name__ == "__main__":
    main()
