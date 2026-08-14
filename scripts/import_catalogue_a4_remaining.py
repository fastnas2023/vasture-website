#!/usr/bin/env python3
"""Fast deterministic import for the remaining Catalogue A4 products.

All images are direct crops from the JPEGs embedded in the supplied PDF.
No product detail, colour, background or certification claim is generated.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
ORIGINALS = ROOT / "tmp/pdfs/catalogue-a4-originals"
REVIEWS = ROOT / "tmp/pdfs/catalogue-a4-render"
OUTPUT = ROOT / "assets/catalogue-a4/main"
DATA_OUTPUT = ROOT / "data/catalogue-a4-remaining.json"


COLOURS = {
    "hi-vis-yellow": ("荧光黄", "Hi Vis Yellow"), "hi-vis-orange": ("荧光橙", "Hi Vis Orange"),
    "yellow-navy": ("黄/藏青", "Yellow/Navy"), "orange-navy": ("橙/藏青", "Orange/Navy"),
    "black": ("黑色", "Black"), "navy": ("藏青色", "Navy"), "sky-blue": ("天蓝", "Sky Blue"),
    "lake-blue": ("湖蓝", "Lake Blue"), "red": ("红色", "Red"), "pink": ("粉色", "Pink"),
    "lime": ("亮绿", "Lime"), "purple": ("紫色", "Purple"), "maroon": ("酒红", "Maroon"),
    "white": ("白色", "White"), "green": ("绿色", "Green"), "royal-blue": ("宝蓝", "Royal Blue"),
    "raspberry": ("树莓红", "Raspberry"), "grey": ("灰色", "Grey"),
    "washed-denim": ("水洗丹宁", "Washed Denim"), "dark-denim": ("深丹宁", "Dark Denim"),
    "silver": ("银色", "Silver"), "green-yellow": ("绿/黄", "Green/Yellow"),
    "orange-yellow": ("橙/黄", "Orange/Yellow"), "navy-yellow": ("藏青/黄", "Navy/Yellow"),
    "lime-yellow": ("亮绿/黄", "Lime/Yellow"), "black-yellow": ("黑/黄", "Black/Yellow"),
    "red-yellow": ("红/黄", "Red/Yellow"), "royal-blue-yellow": ("宝蓝/黄", "Royal Blue/Yellow"),
    "purple-yellow": ("紫/黄", "Purple/Yellow"), "raspberry-yellow": ("树莓红/黄", "Raspberry/Yellow"),
    "grey-yellow": ("灰/黄", "Grey/Yellow"), "orange-black": ("橙/黑", "Orange/Black"),
    "orange-grey": ("橙/灰", "Orange/Grey"), "orange-royal-blue": ("橙/宝蓝", "Orange/Royal Blue"),
    "red-black": ("红/黑", "Red/Black"),
}


@dataclass(frozen=True)
class Group:
    box: tuple[int, int, int, int]
    colours: tuple[str, ...]
    inset: int = 8


@dataclass(frozen=True)
class Spec:
    sku: str
    slug: str
    name_en: str
    name_zh: str
    product_type: str
    page: int
    groups: tuple[Group, ...]
    model_reference: bool = False


G = Group
SPECS = (
    # Page 2: the catalogue only provides model/reference views for these styles.
    Spec("HVP218", "hvp218-two-tone-bomber-jacket", "HVP218 TWO TONE BOMBER JACKET", "HVP218 双色反光飞行夹克", "jacket", 2, (G((610, 820, 805, 1148), ("hi-vis-yellow",), 2), G((810, 820, 1060, 1148), ("hi-vis-orange",), 2)), True),
    Spec("HVS461", "hvs461-waterproof-over-trousers", "HVS461 WATERPROOF OVER TROUSERS", "HVS461 高可视防水套裤", "pants", 2, (G((1600, 820, 1790, 1148), ("hi-vis-yellow",), 2), G((1800, 820, 2005, 1148), ("hi-vis-orange",), 2)), True),
    Spec("HVP209", "hvp209-fontaine-flight-jacket", "HVP209 FONTAINE FLIGHT JACKET", "HVP209 Fontaine反光飞行夹克", "jacket", 2, (G((495, 1200, 730, 1538), ("hi-vis-yellow",), 2), G((732, 1200, 955, 1538), ("hi-vis-orange",), 2)), True),
    Spec("HVP309", "hvp309-fontaine-storm-jacket", "HVP309 FONTAINE STORM JACKET", "HVP309 Fontaine反光风雨夹克", "jacket", 2, (G((1602, 1200, 1790, 1538), ("hi-vis-yellow",), 2), G((1800, 1200, 2005, 1538), ("hi-vis-orange",), 2)), True),
    Spec("HV008F", "hv008f-reversible-fleece-body-warmer", "HV008F REVERSIBLE FLEECE BODY WARMER", "HV008F 双面穿抓绒保暖背心", "vest", 2, (G((495, 1570, 730, 1892), ("hi-vis-yellow",), 2), G((732, 1570, 955, 1892), ("hi-vis-orange",), 2)), True),
    Spec("HV005", "hv005-multi-pocket-body-warmer", "HV005 MULTI-POCKET BODY WARMER", "HV005 多口袋保暖背心", "vest", 2, (G((1602, 1570, 1790, 1892), ("hi-vis-yellow",), 2), G((1800, 1570, 2005, 1892), ("hi-vis-orange",), 2)), True),
    Spec("HVP300", "hvp300-classic-motorway-jacket", "HVP300 CLASSIC MOTORWAY JACKET", "HVP300 经典高速公路反光夹克", "jacket", 2, (G((495, 1920, 730, 2210), ("hi-vis-yellow",), 2), G((732, 1920, 955, 2210), ("hi-vis-orange",), 2)), True),
    Spec("HVP302", "hvp302-two-tone-motorway-jacket", "HVP302 TWO TONE MOTORWAY JACKET", "HVP302 双色高速公路反光夹克", "jacket", 2, (G((1602, 1920, 1790, 2210), ("hi-vis-yellow",), 2), G((1800, 1920, 2005, 2210), ("hi-vis-orange",), 2)), True),

    # Page 3 waistcoats.
    Spec("HVW120", "hvw120-renewable-open-mesh-waistcoat", "HVW120 RENEWABLE TOP COOL OPEN MESH 2 BAND & BRACES", "HVW120 可再生网眼反光背心", "vest", 3, (
        G((744, 110, 2095, 320), ("hi-vis-yellow", "hi-vis-orange", "sky-blue", "black", "lake-blue", "red")),
        G((744, 420, 2095, 610), ("pink", "lime", "purple", "maroon", "navy", "white")),)),
    Spec("HVJ259", "hvj259-reflective-border-tabard", "HVJ259 REFLECTIVE BORDER TABARD", "HVJ259 反光包边套头背心", "vest", 3, (
        G((744, 765, 2095, 955), ("hi-vis-yellow", "hi-vis-orange", "red", "lake-blue", "green", "purple", "sky-blue")),
        G((744, 1050, 2095, 1225), ("white", "raspberry", "navy", "black", "lime", "royal-blue", "pink", "grey")),)),
    Spec("HVW820", "hvw820-renewable-executive-waistcoat", "HVW820 RENEWABLE EXECUTIVE OPEN MESH WAISTCOAT", "HVW820 可再生网眼多口袋背心", "vest", 3, (G((744, 1430, 2095, 1620), ("hi-vis-yellow", "hi-vis-orange", "yellow-navy", "royal-blue-yellow", "orange-grey", "orange-yellow", "red-yellow")),)),
    Spec("HVW108-MASH", "hvw108-mash-multi-pocket-mesh-vest", "HVW108-MASH MULTI-POCKET MESH REFLECTIVE VEST", "HVW108-MASH 多口袋网眼反光背心", "vest", 3, (G((744, 1900, 1125, 2075), ("hi-vis-yellow", "hi-vis-orange"), 5),)),
    Spec("HVWN4", "hvwn4-black-red-mesh-vest", "HVWN4 BLACK & RED MESH VEST", "HVWN4 黑红网眼反光背心", "vest", 3, (G((1850, 1900, 2070, 2110), ("red",), 2),)),

    # Page 4 waistcoats. Duplicate colour names use unique asset keys.
    Spec("HVW100", "hvw100-two-band-braces-waistcoat", "HVW100 2 BAND & BRACES WAISTCOAT", "HVW100 两横两竖反光背心", "vest", 4, (
        G((440, 45, 2090, 250), ("hi-vis-yellow", "hi-vis-orange", "sky-blue", "black", "lake-blue", "red", "royal-blue", "raspberry")),
        G((440, 380, 2090, 560), ("pink", "lime", "purple", "maroon", "navy", "white", "green-yellow", "orange-yellow")),
        G((440, 700, 2090, 870), ("navy-yellow", "lime-yellow", "black-yellow", "red-yellow", "royal-blue-yellow", "purple-yellow", "raspberry-yellow", "green-yellow-2")),)),
    Spec("HVW801", "hvw801-multi-functional-executive-waistcoat", "HVW801 MULTI-FUNCTIONAL EXECUTIVE WAISTCOAT", "HVW801 多功能行政反光背心", "vest", 4, (
        G((440, 1000, 2090, 1190), ("hi-vis-yellow", "hi-vis-orange", "red", "pink", "royal-blue", "black", "green", "lime")),
        G((440, 1335, 2090, 1500), ("navy", "white", "purple", "lake-blue", "sky-blue", "black-yellow", "purple-yellow", "navy-yellow", "grey-yellow")),
        G((440, 1645, 2090, 1815), ("royal-blue-yellow", "orange-black", "orange-yellow", "orange-navy", "orange-grey", "orange-royal-blue", "red-yellow", "red-black", "green-yellow")),)),
    Spec("HVW108", "hvw108-multi-pocket-oxford-vest", "HVW108 MULTI-POCKET OXFORD REFLECTIVE VEST", "HVW108 多口袋牛津布反光背心", "vest", 4, (G((695, 1960, 1055, 2160), ("hi-vis-yellow", "hi-vis-orange"), 5),)),
    Spec("LHVW802", "lhvw802-reflective-mesh-vest", "LHVW802 REFLECTIVE MESH VEST", "LHVW802 反光网眼背心", "vest", 4, (G((1740, 1960, 2090, 2160), ("hi-vis-yellow", "hi-vis-orange"), 5),)),

    # Page 5 shirts and jacket.
    Spec("HVJ210", "hvj210-short-sleeve-polo", "HVJ210 SHORT SLEEVE POLO", "HVJ210 高可视短袖Polo衫", "workshirt", 5, (G((1075, 160, 2080, 355), ("hi-vis-yellow", "hi-vis-orange", "black", "navy")),)),
    Spec("HVJ410", "hvj410-short-sleeve-t-shirt", "HVJ410 SHORT SLEEVE T-SHIRT", "HVJ410 高可视短袖T恤", "workshirt", 5, (G((1075, 510, 2080, 710), ("hi-vis-yellow", "hi-vis-orange", "black", "navy")),)),
    Spec("HVJ910", "hvj910-top-cool-v-neck-t-shirt", "HVJ910 TOP COOL V-NECK T-SHIRT", "HVJ910 Top Cool V领反光T恤", "workshirt", 5, (G((1075, 865, 2080, 1075), ("hi-vis-yellow", "hi-vis-orange", "yellow-navy", "orange-navy")),)),
    Spec("HVJ220", "hvj220-two-tone-short-sleeve-polo", "HVJ220 TWO TONE SHORT SLEEVE POLO", "HVJ220 双色短袖反光Polo衫", "workshirt", 5, (G((510, 1220, 1070, 1510), ("hi-vis-yellow", "hi-vis-orange"), 4),), True),
    Spec("HVJ400", "hvj400-two-tone-short-sleeve-t-shirt", "HVJ400 TWO TONE SHORT SLEEVE T-SHIRT", "HVJ400 双色短袖反光T恤", "workshirt", 5, (G((1580, 1220, 2080, 1510), ("hi-vis-yellow", "hi-vis-orange"), 4),), True),
    Spec("HVJ310", "hvj310-long-sleeve-polo", "HVJ310 LONG SLEEVE POLO", "HVJ310 高可视长袖Polo衫", "workshirt", 5, (G((510, 1575, 1070, 1880), ("hi-vis-yellow", "hi-vis-orange"), 4),), True),
    Spec("HVJ420", "hvj420-long-sleeve-t-shirt", "HVJ420 LONG SLEEVE T-SHIRT", "HVJ420 高可视长袖T恤", "workshirt", 5, (G((1580, 1575, 2080, 1880), ("hi-vis-yellow", "hi-vis-orange"), 4),), True),
    Spec("HVW706", "hvw706-kensington-jacket", "HVW706 KENSINGTON JACKET WITH FLEECE LINING", "HVW706 Kensington抓绒里反光夹克", "jacket", 5, (G((1075, 1970, 2080, 2135), ("hi-vis-yellow", "hi-vis-orange", "black", "navy", "pink")),)),

    # Page 6 accessories.
    Spec("HVDW15", "hvdw15-reflective-border-dog-vest", "HVDW15 REFLECTIVE BORDER DOG'S VEST", "HVDW15 反光包边宠物背心", "accessory", 6, (G((695, 115, 2070, 285), ("hi-vis-yellow", "hi-vis-orange", "pink", "red", "royal-blue", "washed-denim", "dark-denim"), 18),)),
    Spec("HVW066", "hvw066-print-me-arm-bands", "HVW066 PRINT ME ARM BANDS", "HVW066 可印刷反光臂带", "accessory", 6, (G((700, 435, 2070, 560), ("hi-vis-yellow", "hi-vis-orange", "pink", "lime", "red", "royal-blue", "white")),)),
    Spec("ID03", "id03-id-arm-bands", "ID03 ID ARM BANDS", "ID03 证件卡臂带", "accessory", 6, (G((700, 735, 2070, 880), ("hi-vis-yellow", "hi-vis-orange", "royal-blue", "lime", "pink", "red", "black", "silver")),)),
    Spec("TFC100", "tfc100-safety-bump-cap", "TFC100 SAFETY BUMP CAP", "TFC100 安全防撞帽", "accessory", 6, (G((700, 1020, 2070, 1150), ("hi-vis-yellow", "green", "navy", "red", "royal-blue")),)),
    Spec("C6713", "c6713-baseball-cap", "C6713 BASEBALL CAP", "C6713 反光棒球帽", "accessory", 6, (G((420, 1330, 985, 1555), ("hi-vis-yellow", "hi-vis-orange"), 5),)),
    Spec("CT01", "ct01-clip-on-ties", "CT01 CLIP-ON TIES", "CT01 夹式领带", "accessory", 6, (G((1480, 1320, 2070, 1560), ("black", "navy"), 12),)),
    Spec("YK8001", "yk8001-london-rucksack", "YK8001 LONDON RUCKSACK", "YK8001 London反光背包", "accessory", 6, (G((420, 1615, 985, 1880), ("hi-vis-yellow", "hi-vis-orange"), 5),)),
    Spec("YK2518", "yk2518-seattle-holdall", "YK2518 SEATTLE HOLDALL", "YK2518 Seattle反光旅行包", "accessory", 6, (G((1480, 1615, 2070, 1870), ("hi-vis-yellow", "hi-vis-orange"), 5),)),
    Spec("HVW068", "hvw068-rucksack-cover", "HVW068 RUCKSACK COVER", "HVW068 反光背包防雨罩", "accessory", 6, (G((420, 1940, 690, 2200), ("hi-vis-yellow",), 3),), True),
    Spec("WK006", "wk006-knee-pads", "WK006 KNEE PADS", "WK006 EVA护膝", "accessory", 6, (G((1015, 1940, 1305, 2200), ("black",), 3),)),
    Spec("RP01", "rp01-heat-apply-reflective-tape", "RP01 HEAT APPLY REFLECTIVE TAPE", "RP01 热转印反光条", "accessory", 6, (G((1760, 1940, 2070, 2200), ("silver",), 3),)),
)


def colour_label(key: str) -> tuple[str, str]:
    base = key.removesuffix("-2")
    return COLOURS[base]


def trim_white(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white")).convert("L")
    box = diff.point(lambda value: 255 if value > 28 else 0).getbbox()
    if not box:
        return rgb
    left, top, right, bottom = box
    pad = 8
    return rgb.crop((max(0, left-pad), max(0, top-pad), min(rgb.width, right+pad), min(rgb.height, bottom+pad)))


def product_canvas(image: Image.Image) -> Image.Image:
    image = trim_white(image)
    scale = min(680 / image.width, 680 / image.height, 3.0)
    image = image.resize((max(1, round(image.width*scale)), max(1, round(image.height*scale))), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (1000, 1000), "white")
    canvas.paste(image, ((1000-image.width)//2, (1000-image.height)//2))
    return canvas


def extract(spec: Spec) -> list[dict[str, str]]:
    source = Image.open(ORIGINALS / f"page-{spec.page}.jpg").convert("RGB")
    review = Image.open(REVIEWS / f"page-{spec.page}.jpg")
    sx, sy = source.width / review.width, source.height / review.height
    variants: list[dict[str, str]] = []
    seen: dict[str, int] = {}
    for group in spec.groups:
        x1, y1, x2, y2 = group.box
        x1, y1, x2, y2 = round(x1*sx), round(y1*sy), round(x2*sx), round(y2*sy)
        width = x2-x1
        for index, colour in enumerate(group.colours):
            left = x1 + round(width*index/len(group.colours))
            right = x1 + round(width*(index+1)/len(group.colours))
            inset = round(group.inset*sx)
            crop = source.crop((left+inset, y1, right-inset, y2))
            seen[colour] = seen.get(colour, 0) + 1
            file_colour = colour if seen[colour] == 1 else f"{colour}-{seen[colour]}"
            path = f"assets/catalogue-a4/main/{spec.sku.lower()}-{file_colour}.webp"
            product_canvas(crop).save(ROOT/path, "WEBP", quality=88, method=6)
            zh, en = colour_label(colour)
            variants.append({"label_zh": zh, "label_en": en, "image": path})
    return variants


def product_record(spec: Spec, variants: list[dict[str, str]], sort_order: int) -> dict:
    count = len(variants)
    source_kind = "颜色模特参考图" if spec.model_reference else "颜色单品图"
    description = f"画册第{spec.page}页展示{count}张{source_kind}；本页用于选款和询价，具体规格、认证、库存与起订条件需确认。"
    tags = [spec.product_type, "workwear", "functional", "outdoor", "project", "reflective"]
    if spec.product_type == "accessory":
        tags = ["accessory", "functional", "outdoor", "project", "reflective"]
    if spec.sku in {"HVW120", "HVW820", "HVW108-MASH", "HVWN4", "LHVW802"}:
        tags.append("mesh")
    if spec.sku in {"HVP218", "HVS461", "HVP209", "HVP309", "HVP300", "HVP302"}:
        tags.append("waterproof")
    images = [variant["image"] for variant in variants]
    return {
        "id": spec.slug, "sku": spec.sku, "name_zh": spec.name_zh, "name_en": spec.name_en,
        "description_zh": description, "product_type": spec.product_type, "tags": list(dict.fromkeys(tags)),
        "main_image": images[0], "image_alt_zh": f"{spec.name_zh}{variants[0]['label_zh']}画册参考图",
        "gallery_images": images, "color_variants": variants, "badge": "新画册",
        "supply_mode": "catalogue_inquiry", "moq_label": "供货", "moq_value": "询价确认",
        "stock_status": "not_claimed", "catalogue_id": "catalogue-a4", "catalogue_name": "Catalogue A4",
        "source_file": "产品图册/catalogue-a4.pdf", "source_pages": [spec.page], "added_date": "2026-08-15",
        "source_status": "catalogue_linked", "visibility": "public", "sort_order": sort_order,
    }


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    products = []
    for sort_order, spec in enumerate(SPECS, start=34):
        variants = extract(spec)
        products.append(product_record(spec, variants, sort_order))
        print(f"{spec.sku}: {len(variants)} images")
    DATA_OUTPUT.write_text(json.dumps({
        "schema_version": 1,
        "updated_date": "2026-08-15",
        "asset_base_url": "https://fastnas2023.github.io/vasture-website/",
        "products": products,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(products)} products to {DATA_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
