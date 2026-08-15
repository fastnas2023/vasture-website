#!/usr/bin/env python3
"""Extract visually reviewed product crops from the 78-page catalogue.

The catalogue is one flattened image per PDF page, so crop coordinates are
reviewed per product rather than inferred from a single page-wide rule. This
script writes draft assets and data only; it does not publish them to the site.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "tmp/pdfs/catalogue-78-analysis/originals"
ASSET_DIR = ROOT / "assets/catalogue-78/main"
DATA_OUTPUT = ROOT / "data/catalogue-78-products-draft.json"
CONTACT_DIR = ROOT / "tmp/pdfs/catalogue-78-analysis/contact-crops"


@dataclass(frozen=True)
class CropSpec:
    sku: str
    page: int
    title_en: str
    title_zh: str
    crop: tuple[int, int, int, int]
    product_type: str = "workshirt"
    crop_status: str = "reviewed-clean-single-product"
    variant_group_id: str | None = None


PRODUCTS = (
    CropSpec("XK-001", 4, "Long Sleeve Camo Shirt", "长袖迷彩工作衫", (220, 405, 620, 960)),
    CropSpec("XK-002", 4, "FR Solid Vent Work Shirt", "阻燃纯色透气工作衫", (1350, 310, 1680, 860), crop_status="needs-annotation-cleanup"),
    CropSpec("XK-003", 5, "Inherent Lightweight FR Rip-Stop Work Shirt", "本质阻燃轻量防撕裂工作衫", (340, 370, 610, 840)),
    CropSpec("XK-004", 5, "FR Stretch Work Shirt with Pearl Snaps", "阻燃弹力珍珠按扣工作衫", (1450, 385, 1755, 850)),
    CropSpec("XK-005", 6, "Classic Button Down FR Work Shirt", "经典纽扣阻燃工作衫", (505, 345, 770, 850), crop_status="needs-background-isolation"),
    CropSpec("XK-006", 6, "FR Plaid Work Shirt", "阻燃格纹工作衫", (1420, 375, 1700, 850), crop_status="needs-background-isolation"),
    CropSpec("XK-007", 7, "Denim FR Work Shirt with Pearl Snaps", "珍珠按扣阻燃牛仔工作衫", (600, 270, 1000, 910)),
    CropSpec("XK-008", 7, "Women's Non-FR Work Shirt", "女式非阻燃工作衫", (1800, 320, 2190, 870)),
    CropSpec("XK-009", 8, "Women's Work Shirt", "女式工作衫", (815, 465, 1120, 985)),
    CropSpec("XK-010", 8, "Women's FR Crew Neck Shirt", "女式阻燃圆领衫", (1410, 285, 1805, 810)),
    CropSpec("XK-011", 9, "FR Stretch Crew Neck Tee Shirt", "阻燃弹力圆领长袖T恤", (455, 350, 720, 900), crop_status="needs-product-only-image"),
    CropSpec("XK-012", 9, "FR Crew Neck Tee Shirt", "阻燃圆领长袖T恤", (1740, 280, 2110, 985), crop_status="needs-product-only-image"),
    CropSpec("XK-013", 10, "FR Henley Shirt-Raglan Sleeve", "阻燃插肩袖亨利领衫", (670, 125, 1145, 1540), crop_status="needs-product-only-image"),
    CropSpec("XK-014", 11, "Functional Base Layer", "功能性阻燃打底套装", (310, 300, 700, 805)),
    CropSpec("XK-015", 12, "FR Polo Shirts", "阻燃Polo衫", (1370, 700, 1635, 1080), crop_status="reviewed-clean-low-source-resolution"),
    CropSpec("XK-016", 13, "Multinorm Sweater", "多标准防护半拉链卫衣", (255, 935, 475, 1215), crop_status="reviewed-clean-low-source-resolution"),
    CropSpec("XK-017", 13, "Multinorm Sweatshirt", "多标准防护圆领卫衣", (1270, 260, 1685, 725), product_type="sweatshirt", variant_group_id="xk-017-018-multinorm-sweatshirt"),
    CropSpec("XK-018", 13, "Multinorm Sweatshirt", "多标准防护圆领卫衣", (1265, 855, 1685, 1385), product_type="sweatshirt", variant_group_id="xk-017-018-multinorm-sweatshirt"),
    CropSpec("XK-019", 14, "Short Sleeve T-Shirt", "短袖T恤", (205, 275, 645, 875), product_type="tshirt"),
    CropSpec("XK-020", 14, "Round Neck Sweatshirts", "圆领卫衣", (1235, 865, 1695, 1510), product_type="sweatshirt"),
    CropSpec("XK-021", 15, "Hi-Visibility Closed Front Long Sleeve Shirt", "高可视封闭前襟长袖工作衫", (560, 375, 960, 935)),
    CropSpec("XK-022", 15, "Mens Hi Vis Work Shirt Underarm Mesh Vent", "男式高可视腋下网眼透气工作衫", (1860, 620, 2195, 1030), crop_status="reviewed-clean-low-source-resolution"),
    CropSpec("XK-023", 16, "High Visibility Birdseye Mesh Crew Neck Shirt", "高可视鸟眼网布反光圆领衫", (185, 325, 650, 875), product_type="tshirt"),
    CropSpec("XK-024", 16, "Hi-Vis Lime Birdseye Safety Short Sleeve Shirt", "荧光黄鸟眼网布安全短袖衫", (1260, 320, 1685, 885), product_type="tshirt"),
    CropSpec("XK-025", 17, "Lightweight Work Shirt", "轻量反光工作衫", (215, 295, 665, 890)),
    CropSpec("XK-026", 17, "Apple Green Work Shirt", "苹果绿反光工作衫", (1350, 350, 1605, 720), crop_status="reviewed-clean-low-source-resolution"),
    CropSpec("XK-027", 18, "Green Quick Drying Work Shirt", "绿色速干工作衫", (1285, 315, 1695, 900)),
    CropSpec("XK-028", 20, "Stretched Front Zip Hoodie", "弹力全拉链连帽卫衣", (775, 245, 1085, 765), product_type="hoodie"),
    CropSpec("XK-029", 20, "FR Pull Over Hoodie", "阻燃套头连帽卫衣", (1815, 85, 2200, 1030), product_type="hoodie", crop_status="needs-product-only-image", variant_group_id="xk-029-033-pullover-hoodie"),
    CropSpec("XK-030", 20, "FR Pull Over Hoodie", "阻燃套头连帽卫衣", (1275, 1070, 1485, 1380), product_type="hoodie", crop_status="reviewed-clean-low-source-resolution", variant_group_id="xk-029-033-pullover-hoodie"),
    CropSpec("XK-031", 20, "FR Pull Over Hoodie", "阻燃套头连帽卫衣", (1495, 1070, 1745, 1380), product_type="hoodie", crop_status="reviewed-clean-low-source-resolution", variant_group_id="xk-029-033-pullover-hoodie"),
    CropSpec("XK-032", 20, "FR Pull Over Hoodie", "阻燃套头连帽卫衣", (1760, 1065, 1950, 1380), product_type="hoodie", crop_status="reviewed-clean-low-source-resolution", variant_group_id="xk-029-033-pullover-hoodie"),
    CropSpec("XK-033", 20, "FR Pull Over Hoodie", "阻燃套头连帽卫衣", (1960, 1050, 2180, 1380), product_type="hoodie", crop_status="reviewed-clean-low-source-resolution", variant_group_id="xk-029-033-pullover-hoodie"),
    CropSpec("XK-034", 22, "FR Insulated Duck Jacket", "阻燃鸭绒保暖夹克", (320, 320, 720, 860), product_type="jacket"),
    CropSpec("XK-035", 22, "Flame Retardant Jacket", "阻燃反光夹克", (1510, 400, 1900, 900), product_type="jacket"),
    CropSpec("XK-036", 23, "Polyester Cotton Basic Jacket", "涤棉基础夹克", (230, 330, 700, 850), product_type="jacket"),
    CropSpec("XK-037", 23, "Polyester Cotton Jacket", "涤棉功能夹克", (1330, 480, 1690, 850), product_type="jacket"),
    CropSpec("XK-038", 24, "Polyester Cotton Basic Jacket", "涤棉基础夹克", (600, 930, 870, 1300), product_type="jacket"),
    CropSpec("XK-039", 25, "Zip Base Layer-Top", "拉链打底上衣", (220, 300, 700, 850)),
    CropSpec("XK-040", 25, "Waterproof Outdoor Winter Jacket", "防水户外冬季夹克", (1270, 300, 1710, 860), product_type="jacket"),
    CropSpec("XK-041", 26, "Offshore Anti-Flame Jacket", "海工阻燃反光夹克", (220, 340, 610, 870), product_type="jacket"),
    CropSpec("XK-042", 26, "Offshore Anti-Flame Winter Jacket", "海工阻燃冬季夹克", (1400, 320, 1840, 870), product_type="jacket"),
    CropSpec("XK-043", 28, "FR Stretch Pants", "阻燃弹力长裤", (780, 280, 1050, 970), product_type="pants"),
    CropSpec("XK-044", 28, "FR Stretch Pants", "阻燃弹力长裤", (1260, 300, 1690, 1500), product_type="pants", crop_status="needs-background-isolation"),
    CropSpec("XK-045", 29, "Offshore Anti-Flame Trousers", "海工阻燃反光长裤", (240, 320, 590, 1160), product_type="pants"),
    CropSpec("XK-046", 29, "Industry Hi-Vis Trousers", "工业高可视长裤", (1300, 270, 1640, 1160), product_type="pants"),
    CropSpec("XK-047", 30, "100% Cotton FR Jeans", "纯棉阻燃牛仔裤", (280, 300, 590, 1100), product_type="pants", variant_group_id="xk-047-048-cotton-fr-jeans"),
    CropSpec("XK-048", 30, "100% Cotton FR Jeans", "纯棉阻燃牛仔裤", (1260, 680, 1590, 1510), product_type="pants", variant_group_id="xk-047-048-cotton-fr-jeans"),
    CropSpec("XK-049", 31, "Basical Man FR Stretch Jeans", "男式阻燃弹力牛仔裤", (240, 390, 530, 1110), product_type="pants"),
    CropSpec("XK-050", 31, "Women FR Stretch Jeans", "女式阻燃弹力牛仔裤", (1260, 760, 1600, 1510), product_type="pants"),
    CropSpec("XK-051", 32, "Cotton Basic Pants", "棉质基础工装裤", (270, 830, 600, 1580), product_type="pants"),
    CropSpec("XK-052", 32, "Polyester Cotton Pants", "涤棉工装裤", (1340, 300, 1640, 1050), product_type="pants"),
    CropSpec("XK-053", 33, "Polyester Cotton Cargo Pants", "涤棉工装多袋裤", (250, 300, 630, 980), product_type="pants"),
    CropSpec("XK-054", 33, "Lightweight Trouser", "轻量反光工装裤", (1370, 950, 1710, 1570), product_type="pants"),
    CropSpec("XK-055", 34, "Utility Pants", "多功能工装裤", (260, 280, 620, 1030), product_type="pants"),
    CropSpec("XK-056", 34, "Stretch Utility Pants", "弹力多功能工装裤", (1250, 300, 1530, 920), product_type="pants"),
    CropSpec("XK-057", 35, "Ripstop Stretch Shorts", "防撕裂弹力短裤", (280, 300, 670, 870), product_type="pants"),
    CropSpec("XK-058", 35, "Ripstop Stretch Pants", "防撕裂弹力长裤", (1810, 270, 2160, 1010), product_type="pants"),
    CropSpec("XK-059", 36, "Stretch Utility Shorts", "弹力多功能短裤", (240, 280, 650, 880), product_type="pants"),
    CropSpec("XK-060", 36, "3/4 Length Stretch Trousers", "七分弹力工装裤", (1280, 780, 1650, 1530), product_type="pants"),
    CropSpec("XK-061", 37, "Stretch Work Jeans", "弹力工装牛仔裤", (230, 280, 590, 940), product_type="pants"),
    CropSpec("XK-062", 37, "Stretch Jeans with Holster Pockets", "带工具袋弹力牛仔裤", (1500, 870, 1830, 1530), product_type="pants"),
    CropSpec("XK-063", 38, "Base Layer-Trousers", "弹力保暖打底裤", (810, 280, 1090, 980), product_type="pants"),
    CropSpec("XK-064", 38, "4-Way Stretch Cargo Pants", "四向弹力工装多袋裤", (1370, 300, 1730, 980), product_type="pants"),
    CropSpec("XK-065", 39, "Eco Work Pants", "环保工装裤", (220, 220, 530, 880), product_type="pants"),
    CropSpec("XK-066", 39, "Eco Work Pants", "环保工装裤", (220, 930, 530, 1580), product_type="pants"),
    CropSpec("XK-067", 39, "White Cargo Pants", "白色工装多袋裤", (1480, 760, 1830, 1560), product_type="pants"),
    CropSpec("XK-068", 40, "Hi-Vis Cargo Pants", "高可视工装多袋裤", (500, 470, 870, 1210), product_type="pants"),
    CropSpec("XK-069", 40, "Safety Work Pants with Reflective Tape", "带反光带安全工装裤", (1480, 470, 1810, 1190), product_type="pants"),
    CropSpec("XK-070", 42, "Flame Retardant Coverall", "阻燃连体工作服", (220, 280, 680, 1530), product_type="coverall", crop_status="needs-background-isolation"),
    CropSpec("XK-071", 42, "Flame Retardant Coverall", "阻燃连体工作服", (1370, 310, 1720, 1510), product_type="coverall"),
    CropSpec("XK-072", 43, "Inherent FR Coverall", "本质阻燃连体工作服", (750, 280, 1110, 1530), product_type="coverall", crop_status="needs-background-isolation"),
    CropSpec("XK-073", 43, "Offshore Anti-Flame Coverall", "海工阻燃连体工作服", (1810, 300, 2160, 1530), product_type="coverall", crop_status="needs-background-isolation"),
    CropSpec("XK-074", 44, "Offshore Anti-Flame Coverall", "海工阻燃高可视连体服", (640, 280, 1110, 1530), product_type="coverall", crop_status="needs-background-isolation"),
    CropSpec("XK-075", 44, "Flame Retardant Coverall", "阻燃反光连体工作服", (1250, 280, 1580, 1080), product_type="coverall"),
    CropSpec("XK-076", 45, "Flame Retardant Coverall", "阻燃连体工作服", (210, 280, 590, 1040), product_type="coverall"),
    CropSpec("XK-077", 45, "Flame Retardant Coverall", "阻燃反光连体工作服", (1370, 690, 1710, 1530), product_type="coverall"),
    CropSpec("XK-078", 46, "Pilot Coverall", "飞行员连体工作服", (1120, 120, 1570, 1610), product_type="coverall", crop_status="needs-background-isolation"),
    CropSpec("XK-079", 47, "Hi-Visibility Two Tone Coverall", "高可视双色连体工作服", (210, 850, 560, 1570), product_type="coverall"),
    CropSpec("XK-080", 47, "Cotton Coverall", "棉质连体工作服", (970, 120, 1280, 820), product_type="coverall"),
    CropSpec("XK-081", 47, "Women's Non-FR Coverall", "女式非阻燃连体工作服", (970, 850, 1280, 1580), product_type="coverall"),
    CropSpec("XK-082", 48, "FR Insulated Bib Pants", "阻燃加厚背带裤", (260, 220, 560, 940), product_type="pants"),
    CropSpec("XK-083", 48, "Catalogue Product", "阻燃加厚背带裤（标题待确认）", (1510, 250, 1840, 950), product_type="pants"),
    CropSpec("XK-084", 50, "HI-VIS STRETCH TROUSERS", "高可视弹力工作裤", (255, 970, 455, 1510), product_type="pants"),
    CropSpec("XK-085", 50, "HI-VIS STRETCH TROUSERS", "高可视弹力工作裤", (1280, 330, 1505, 790), product_type="pants"),
    CropSpec("XK-086", 50, "HI-VIS STRETCH TROUSERS", "高可视弹力工作裤", (1270, 900, 1500, 1470), product_type="pants"),
    CropSpec("XK-087", 51, "HI-VIS STRETCH TROUSERS", "高可视弹力工作裤", (210, 310, 450, 810), product_type="pants"),
    CropSpec("XK-088", 51, "HI-VIS STRETCH TROUSERS", "高可视弹力工作裤", (205, 910, 455, 1485), product_type="pants"),
    CropSpec("XK-089", 51, "4-WAY STRETCH CARGO PANTS", "四向弹力工装裤", (1285, 310, 1515, 810), product_type="pants"),
    CropSpec("XK-090", 51, "4-WAY STRETCH CARGO PANTS", "四向弹力工装裤", (1280, 920, 1520, 1480), product_type="pants"),
    CropSpec("XK-091", 52, "STRETCH SOFTSHELL JACKET", "弹力软壳夹克", (175, 335, 475, 835), product_type="jacket"),
    CropSpec("XK-092", 52, "STRETCH SOFTSHELL JACKET", "弹力软壳夹克", (180, 970, 490, 1500), product_type="jacket"),
    CropSpec("XK-093", 52, "STRETCH SOFTSHELL JACKET", "弹力软壳夹克", (1260, 335, 1540, 835), product_type="jacket"),
    CropSpec("XK-094", 52, "STRETCH SOFTSHELL JACKET", "弹力软壳夹克", (1260, 970, 1545, 1500), product_type="jacket"),
    CropSpec("XK-095", 53, "STRETCH REFLECTIVE SOFTSHELL JACKET", "弹力反光软壳夹克", (160, 295, 445, 805), product_type="jacket"),
    CropSpec("XK-096", 53, "STRETCH REFLECTIVE SOFTSHELL JACKET", "弹力反光软壳夹克", (145, 965, 510, 1495), product_type="jacket"),
    CropSpec("XK-097", 53, "STRETCH REFLECTIVE SOFTSHELL JACKET", "弹力反光软壳夹克", (1590, 300, 1910, 820), product_type="jacket"),
    CropSpec("XK-098", 54, "4-WAY STRETCH MULTINORM TROUSERS", "四向弹力多标准防护裤", (245, 315, 525, 1045), product_type="pants"),
    CropSpec("XK-099", 54, "Catalogue Product", "四向弹力工装裤（标题待确认）", (1560, 745, 1885, 1525), product_type="pants"),
    CropSpec("XK-100", 56, "4-WAY STRETCH MULTINORM JACKET", "四向弹力多标准防护夹克", (190, 300, 600, 860), product_type="jacket"),
    CropSpec("XK-101", 56, "FLAME RETARDANT HI-VIS JACKET", "阻燃高可视夹克", (1330, 300, 1710, 860), product_type="jacket"),
    CropSpec("XK-102", 57, "INHERENT MULTINORM JACKET", "本质阻燃多标准防护夹克", (210, 300, 610, 860), product_type="jacket"),
    CropSpec("XK-103", 57, "FR/ARC RATED RAINWEAR", "阻燃及防电弧雨衣", (1340, 300, 1710, 860), product_type="jacket"),
    CropSpec("XK-104", 58, "INHERENT LIGHTWEIGHT HI-VIS SOLID SHIRT", "本质阻燃轻量高可视纯色工作衫", (1515, 420, 1920, 945), product_type="workshirt"),
    CropSpec("XK-105", 59, "INHERENT LIGHTWEIGHT HI-VIS LONG SLEEVE SHIRT", "本质阻燃轻量高可视长袖工作衫", (280, 320, 585, 900), product_type="workshirt"),
    CropSpec("XK-106", 59, "INHERENT FR HI-VIS TWO TONE WORK SHIRT", "本质阻燃高可视双色工作衫", (1420, 320, 1730, 900), product_type="workshirt"),
    CropSpec("XK-107", 60, "FR CREW NECK TEE SHIRT", "阻燃圆领长袖T恤", (220, 315, 500, 900), product_type="tshirt"),
    CropSpec("XK-108", 60, "FR CREW NECK TEE SHIRT", "阻燃圆领长袖T恤", (1810, 320, 2110, 900), product_type="tshirt"),
    CropSpec("XK-109", 60, "Catalogue Product", "阻燃圆领衫（标题待确认）", (1260, 1000, 1700, 1530), product_type="tshirt"),
    CropSpec("XK-110", 60, "Catalogue Product", "阻燃圆领衫（标题待确认）", (1700, 1000, 2200, 1530), product_type="tshirt"),
    CropSpec("XK-111", 61, "MULTINORM POLO SHIRT", "多标准防护Polo衫", (800, 240, 1110, 870), product_type="workshirt"),
    CropSpec("XK-112", 61, "MULTINORM POLO SHIRT", "多标准防护Polo衫", (210, 930, 520, 1510), product_type="workshirt"),
    CropSpec("XK-113", 61, "HI-VIS YELLOW PULLOVER HOODIE", "高可视黄色套头连帽卫衣", (1790, 430, 2200, 1540), product_type="hoodie"),
    CropSpec("XK-114", 62, "FLEECE HOODED SWEATSHIRT", "抓绒连帽卫衣", (350, 300, 720, 890), product_type="hoodie"),
    CropSpec("XK-115", 62, "FLEECE HOODED SWEATSHIRT", "抓绒连帽卫衣", (1350, 280, 1640, 880), product_type="hoodie"),
    CropSpec("XK-116", 62, "FLEECE HOODED SWEATSHIRT", "抓绒连帽卫衣", (1390, 930, 1685, 1500), product_type="hoodie"),
    CropSpec("XK-117", 63, "4-WAY STRETCH MULTINORM COVERALL", "四向弹力多标准防护连体服", (480, 740, 795, 1510), product_type="coverall"),
    CropSpec("XK-118", 63, "MULTI NORM COVERALL", "多标准防护连体服", (1380, 475, 1615, 1070), product_type="coverall", crop_status="reviewed-clean-low-source-resolution"),
    CropSpec("XK-119", 64, "INHERENT MULTINORM WINTER COVERALL", "本质阻燃多标准冬季连体服", (230, 310, 500, 1050), product_type="coverall"),
    CropSpec("XK-120", 64, "ANTI-FLAME WINTER COVERALL", "防火冬季连体服", (1500, 410, 1880, 1120), product_type="coverall"),
    CropSpec("XK-121", 65, "HI-VIS WATERPROOF JACKET", "高可视防水夹克", (190, 300, 650, 900), product_type="jacket"),
    CropSpec("XK-122", 65, "REFLECTIVE SAFETY JACKETS", "反光安全夹克", (1320, 430, 1740, 985), product_type="jacket"),
    CropSpec("XK-123", 65, "Catalogue Product", "高可视夹克（标题待确认）", (1890, 995, 2210, 1470), product_type="jacket", crop_status="reviewed-clean-low-source-resolution"),
    CropSpec("XK-124", 66, "HI-VIS CARGO SUIT", "高可视工装套装", (850, 350, 1120, 1480), product_type="coverall"),
    CropSpec("XK-125", 67, "HI-VIS CARGO SUIT", "高可视工装套装", (820, 350, 1100, 1480), product_type="coverall"),
    CropSpec("XK-126", 67, "HI-VIS CARGO SUIT", "高可视工装套装", (1825, 305, 2210, 1470), product_type="coverall"),
    CropSpec("XK-127", 68, "HI-VIS CARGO SUIT", "高可视工装套装", (700, 350, 1010, 1480), product_type="coverall"),
    CropSpec("XK-128", 68, "HI VIS REVERSIBLE SAFETY VEST", "高可视双面安全背心", (1550, 390, 1900, 1030), product_type="vest"),
    CropSpec("XK-131", 69, "HI VIS SAFETY VESTS", "高可视安全背心", (255, 330, 610, 900), product_type="vest"),
    CropSpec("XK-132", 69, "HIGH VISIBILITY MESH SAFETY REFLECTIVE VEST", "高可视网眼反光安全背心", (1330, 315, 1725, 900), product_type="vest"),
    CropSpec("XK-133", 70, "FLAME RESISTANT DUAL STRIPE MESH VEST", "阻燃双条纹网眼背心", (170, 330, 450, 930), product_type="vest"),
    CropSpec("XK-134", 70, "HALF SLEEVED FR DUAL STRIPE MESH VEST", "短袖阻燃双条纹网眼背心", (1420, 330, 1830, 930), product_type="vest"),
    CropSpec("XK-135", 71, "STRETCH PANTS", "弹力工作裤", (520, 420, 820, 1130), product_type="pants"),
    CropSpec("XK-136", 71, "HI-VIS CARGO PANTS", "高可视工装裤", (1650, 790, 1985, 1530), product_type="pants"),
    CropSpec("XK-137", 72, "HI-VIS CARGO PANTS", "高可视工装裤", (550, 480, 825, 1250), product_type="pants"),
    CropSpec("XK-138", 72, "HI-VIS CARGO PANTS", "高可视工装裤", (1520, 295, 1825, 1015), product_type="pants"),
    CropSpec("XK-139", 73, "HI-VIS CARGO VEST AND SHORT", "高可视工装背心及短裤套装", (470, 520, 1120, 1150), product_type="coverall"),
    CropSpec("XK-140", 73, "HI-VIS CARGO VEST AND TROUSERS", "高可视工装背心及长裤套装", (1830, 350, 2190, 1520), product_type="coverall"),
    CropSpec("XK-141", 74, "HIGH VISIBILITY BIRDSEYE MESH SHIRT", "高可视鸟眼网眼工作衫", (195, 295, 500, 780), product_type="workshirt"),
    CropSpec("XK-142", 74, "Catalogue Product", "高可视连帽衫（标题待确认）", (205, 1070, 505, 1530), product_type="hoodie"),
    CropSpec("XK-143", 74, "HI-VIS LONG SLEEVES BREATHABLE BIRDSEYE SAFETY T-SHIRT", "高可视长袖透气鸟眼网眼安全T恤", (1320, 300, 1740, 800), product_type="tshirt"),
    CropSpec("XK-144", 75, "HIGH VISIBILITY T-SHIRT", "高可视T恤", (230, 330, 580, 890), product_type="tshirt"),
    CropSpec("XK-145", 75, "HI-VIS LONG SLEEVES BIRDSEYE SAFETY T-SHIRT", "高可视长袖鸟眼网眼安全T恤", (1340, 980, 1640, 1540), product_type="tshirt"),
    CropSpec("XK-146", 76, "HI-VIS TC COVERALLS", "高可视TC连体服", (520, 460, 720, 1120), product_type="coverall"),
    CropSpec("XK-147", 76, "HI-VIS TC COVERALLS", "高可视TC连体服", (1420, 540, 1660, 1090), product_type="coverall"),
    CropSpec("XK-148", 77, "WOMEN'S BASICAL SAFETY MESH VEST", "女式基础款安全网眼背心", (145, 1030, 475, 1545), product_type="vest"),
    CropSpec("XK-149", 77, "WOMEN'S REFLECTIVE SHIRTS", "女式反光工作衫", (1140, 270, 1495, 830), product_type="workshirt", variant_group_id="xk-149-150-womens-reflective-shirts"),
    CropSpec("XK-150", 77, "WOMEN'S REFLECTIVE SHIRTS", "女式反光工作衫", (1465, 270, 1810, 830), product_type="workshirt", variant_group_id="xk-149-150-womens-reflective-shirts"),
    CropSpec("XK-151", 77, "REFLECTIVE SHIRTS", "反光工作衫", (1145, 1025, 1475, 1520), product_type="workshirt"),
)


def source_image(page: int) -> Path:
    return SOURCE_DIR / f"page-{page:02d}.jpg"


def asset_name(sku: str) -> str:
    return f"{sku.lower()}-front.webp"


def normalize_crop(image: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    crop = image.crop(box).convert("RGB")
    crop.thumbnail((900, 900), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (1000, 1000), "#f5f6f6")
    x = (canvas.width - crop.width) // 2
    y = (canvas.height - crop.height) // 2
    canvas.paste(crop, (x, y))
    return canvas


def build_contact_sheets(records: list[dict]) -> list[Path]:
    tile_width, tile_height = 520, 620
    batch_size = 24
    outputs: list[Path] = []
    CONTACT_DIR.mkdir(parents=True, exist_ok=True)

    for start in range(0, len(records), batch_size):
        batch = records[start:start + batch_size]
        rows = math.ceil(len(batch) / 4)
        sheet = Image.new("RGB", (tile_width * 4, tile_height * rows), "#e9eef0")
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.load_default(size=24)
        small = ImageFont.load_default(size=18)

        for index, record in enumerate(batch):
            image = Image.open(ROOT / record["main_image"]).convert("RGB")
            image.thumbnail((480, 500), Image.Resampling.LANCZOS)
            col, row = index % 4, index // 4
            x = col * tile_width + (tile_width - image.width) // 2
            y = row * tile_height + 18
            sheet.paste(image, (x, y))
            text_y = row * tile_height + 525
            draw.text((col * tile_width + 20, text_y), record["sku"], fill="#0b2b3c", font=font)
            draw.text((col * tile_width + 20, text_y + 36), record["name_en"], fill="#344a56", font=small)

        first_sku = batch[0]["sku"].removeprefix("XK-")
        last_sku = batch[-1]["sku"].removeprefix("XK-")
        output = CONTACT_DIR / f"products-{first_sku}-{last_sku}.jpg"
        sheet.save(output, quality=92, optimize=True)
        outputs.append(output)

    return outputs


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    records = []

    for spec in PRODUCTS:
        path = source_image(spec.page)
        if not path.exists():
            raise FileNotFoundError(f"Missing rendered catalogue page: {path}")
        image = Image.open(path)
        output = ASSET_DIR / asset_name(spec.sku)
        normalize_crop(image, spec.crop).save(output, "WEBP", quality=90, method=6)
        records.append({
            "id": spec.sku.lower(),
            "sku": spec.sku,
            "name_en": spec.title_en,
            "name_zh": spec.title_zh,
            "product_type": spec.product_type,
            "variant_group_id": spec.variant_group_id,
            "main_image": output.relative_to(ROOT).as_posix(),
            "image_alt_zh": f"{spec.title_zh}画册正面参考图",
            "catalogue_id": "catalogue-78-en",
            "catalogue_name": "Safety Workwear Catalogue (English, 78 pages)",
            "source_file": "产品图册/catalogue-78-en.pdf",
            "source_pages": [spec.page],
            "source_crop": list(spec.crop),
            "crop_status": spec.crop_status,
            "added_date": "2026-08-15",
            "source_status": "catalogue-linked",
            "frontend_status": "draft-not-imported",
            "claims_status": "not-reviewed-not-published",
        })

    payload = {
        "schema_version": 1,
        "catalogue_id": "catalogue-78-en",
        "batch": "XK-001-XK-151",
        "publish_to_frontend": False,
        "products": records,
    }
    DATA_OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    contact_sheets = build_contact_sheets(records)
    clean = sum(record["crop_status"].startswith("reviewed-clean") for record in records)
    print(f"Extracted {len(records)} draft products ({clean} reviewed clean, {len(records) - clean} need follow-up) -> {ASSET_DIR}")
    print(f"Draft data -> {DATA_OUTPUT}")
    print(f"Contact sheets -> {CONTACT_DIR} ({len(contact_sheets)} files)")


if __name__ == "__main__":
    main()
