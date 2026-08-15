#!/usr/bin/env python3
"""Archive the English source text and draft SKU map for Catalogue.pdf.

This script does not publish products. It preserves the two OCR passes produced
from the flattened page images and creates a review-first inventory so future
English-site work does not need to repeat PDF extraction or OCR.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "产品图册/catalogue-78-en.pdf"
OCR_SPARSE = ROOT / "tmp/pdfs/catalogue-78-analysis/text"
OCR_BLOCK = ROOT / "tmp/pdfs/catalogue-78-analysis/text-psm6"
SOURCE_OUTPUT = ROOT / "data/catalogue-78-english-source.json"
INVENTORY_OUTPUT = ROOT / "data/catalogue-78-inventory.json"
DRAFT_PRODUCTS = ROOT / "data/catalogue-78-products-draft.json"
TITLE_REVIEW = ROOT / "data/catalogue-78-title-review.json"


PAGE_SKUS = {
    4: (1, 2), 5: (3, 4), 6: (5, 6), 7: (7, 8), 8: (9, 10), 9: (11, 12),
    10: (13,), 11: (14,), 12: (15,), 13: (16, 17, 18), 14: (19, 20),
    15: (21, 22), 16: (23, 24), 17: (25, 26), 18: (27,),
    20: (28, 29, 30, 31, 32, 33),
    22: (34, 35), 23: (36, 37), 24: (38,), 25: (39, 40), 26: (41, 42),
    28: (43, 44), 29: (45, 46), 30: (47, 48), 31: (49, 50), 32: (51, 52),
    33: (53, 54), 34: (55, 56), 35: (57, 58), 36: (59, 60), 37: (61, 62),
    38: (63, 64), 39: (65, 66, 67), 40: (68, 69),
    42: (70, 71), 43: (72, 73), 44: (74, 75), 45: (76, 77), 46: (78,),
    47: (79, 80, 81), 48: (82, 83),
    50: (84, 85, 86), 51: (87, 88, 89, 90), 52: (91, 92, 93, 94),
    53: (95, 96, 97), 54: (98, 99),
    56: (100, 101), 57: (102, 103), 58: (104,), 59: (105, 106),
    60: (107, 108, 109, 110), 61: (111, 112, 113), 62: (114, 115, 116),
    63: (117, 118), 64: (119, 120), 65: (121, 122, 123), 66: (124,),
    67: (125, 126), 68: (127, 128), 69: (131, 132), 70: (133, 134),
    71: (135, 136), 72: (137, 138), 73: (139, 140), 74: (141, 142, 143),
    75: (144, 145), 76: (146, 147), 77: (148, 149, 150, 151),
}


NON_PRODUCT_PAGES = {
    1: "cover",
    2: "contents-and-source-contact",
    3: "workshirts-section",
    19: "hoodies-section",
    21: "jackets-section",
    27: "pants-section",
    41: "coveralls-section",
    49: "stretch-section",
    55: "hi-vis-section",
    78: "flame-retardant-accessories-section",
}


def section_for_page(page: int) -> str:
    if 3 <= page <= 18:
        return "workshirts-polo-tees"
    if 19 <= page <= 20:
        return "hoodies"
    if 21 <= page <= 26:
        return "jackets"
    if 27 <= page <= 40:
        return "pants-shorts"
    if 41 <= page <= 48:
        return "bibs-coveralls"
    if 49 <= page <= 54:
        return "stretch-series"
    if 55 <= page <= 77:
        return "hi-vis-clothing"
    if page == 78:
        return "flame-retardant-accessories"
    return "front-matter"


def family_for_sku(number: int) -> str | None:
    groups = {
        "xk-017-018-multinorm-sweatshirt": {17, 18},
        "xk-029-033-pullover-hoodie": {29, 30, 31, 32, 33},
        "xk-047-048-cotton-fr-jeans": {47, 48},
        "xk-149-150-womens-reflective-shirts": {149, 150},
    }
    for family, members in groups.items():
        if number in members:
            return family
    return None


def layout_for_page(page: int) -> str:
    if page in NON_PRODUCT_PAGES:
        return "non-product-section-page"
    count = len(PAGE_SKUS.get(page, ()))
    return {
        1: "single-product-spread",
        2: "split-two-product-spread",
        3: "mixed-three-product-grid",
        4: "two-by-two-product-grid",
        6: "mixed-six-sku-spread",
    }.get(count, "manual-layout-review-required")


def read_ocr(folder: Path, page: int) -> str:
    path = folder / f"page-{page:02d}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Missing OCR source: {path}")
    return path.read_text(encoding="utf-8", errors="replace").strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    if not PDF.exists():
        raise FileNotFoundError(f"Archive the PDF first: {PDF}")

    archived_on = date.today().isoformat()
    pages = []
    for page in range(1, 79):
        pages.append({
            "page": page,
            "page_role": NON_PRODUCT_PAGES.get(page, "product-page"),
            "layout_type": layout_for_page(page),
            "section_id": section_for_page(page),
            "sku_refs": [f"XK-{number:03d}" for number in PAGE_SKUS.get(page, ())],
            "ocr_sparse_en": read_ocr(OCR_SPARSE, page),
            "ocr_block_en": read_ocr(OCR_BLOCK, page),
            "ocr_status": "machine-extracted-needs-visual-review",
        })

    source_data = {
        "schema_version": 1,
        "catalogue_id": "catalogue-78-en",
        "catalogue_name": "Safety Workwear Catalogue (English, 78 pages)",
        "source_file": "产品图册/catalogue-78-en.pdf",
        "source_sha256": sha256(PDF),
        "page_count": 78,
        "source_language": "en",
        "source_format": "one-flattened-image-per-pdf-page",
        "text_layer_present": False,
        "archived_date": archived_on,
        "usage_note": "Internal English source only. Supplier contact and certification text are not current company claims.",
        "pages": pages,
    }

    products = []
    for page, numbers in PAGE_SKUS.items():
        for number in numbers:
            sku = f"XK-{number:03d}"
            products.append({
                "id": sku.lower(),
                "sku": sku,
                "source_page": page,
                "section_id": section_for_page(page),
                "family_group_id": family_for_sku(number),
                "relationship_status": "unreviewed",
                "title_en": None,
                "title_en_status": "pending-visual-review-from-archived-ocr",
                "description_en": None,
                "description_en_status": "not-transcribed",
                "source_text_ref": f"data/catalogue-78-english-source.json#page-{page:02d}",
                "crop_status": "not-started",
                "frontend_status": "not-imported",
                "claim_status": "catalogue-source-only",
            })

    title_review_by_sku = {}
    if TITLE_REVIEW.exists():
        title_review_payload = json.loads(TITLE_REVIEW.read_text(encoding="utf-8"))
        title_review_by_sku = {
            product["sku"]: product
            for product in title_review_payload.get("products", [])
        }
        for product in products:
            reviewed = title_review_by_sku.get(product["sku"])
            if not reviewed:
                continue
            product.update({
                "title_en": reviewed.get("title_en"),
                "title_en_status": reviewed["title_en_status"],
                "relationship_status": reviewed["relationship_status"],
                "family_group_id": reviewed.get("variant_group_id"),
            })

    reviewed_by_sku = {}
    if DRAFT_PRODUCTS.exists():
        draft_payload = json.loads(DRAFT_PRODUCTS.read_text(encoding="utf-8"))
        reviewed_by_sku = {
            product["sku"]: product for product in draft_payload.get("products", [])
        }
        for product in products:
            reviewed = reviewed_by_sku.get(product["sku"])
            if not reviewed:
                continue
            product.update({
                "title_zh": reviewed["name_zh"],
                "main_image": reviewed["main_image"],
                "source_crop": reviewed["source_crop"],
                "crop_status": reviewed["crop_status"],
                "claim_status": reviewed["claims_status"],
            })

    inventory = {
        "schema_version": 1,
        "catalogue_id": "catalogue-78-en",
        "catalogue_name": "Safety Workwear Catalogue (English, 78 pages)",
        "source_file": "产品图册/catalogue-78-en.pdf",
        "source_sha256": source_data["source_sha256"],
        "created_date": archived_on,
        "product_code_count": len(products),
        "english_title_reviewed_count": sum(
            1 for product in products if product["title_en"] is not None
        ),
        "english_title_unresolved_count": sum(
            1 for product in products if product["title_en"] is None
        ),
        "visually_reviewed_crop_count": len(reviewed_by_sku),
        "missing_product_codes_in_source": ["XK-129", "XK-130"],
        "non_product_pages": [
            {"page": page, "role": role} for page, role in NON_PRODUCT_PAGES.items()
        ],
        "import_policy": {
            "publish_to_frontend": False,
            "english_text_requires_visual_review": True,
            "supplier_contact_is_not_company_contact": True,
            "certification_claims_require_independent_confirmation": True,
        },
        "products": products,
    }

    SOURCE_OUTPUT.write_text(json.dumps(source_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    INVENTORY_OUTPUT.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Archived English OCR for {len(pages)} pages -> {SOURCE_OUTPUT}")
    print(f"Created {len(products)} draft SKU records -> {INVENTORY_OUTPUT}")


if __name__ == "__main__":
    main()
