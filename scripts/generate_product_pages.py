#!/usr/bin/env python3
"""Generate one indexable static product page per product in data/products.json.

The generator deliberately reads the existing products page for the shared
header/footer so generated detail pages stay aligned with the site's current
navigation and brand shell. Run from the vasture-website directory or pass
the project directory as the first argument.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlencode


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://fastnas2023.github.io/vasture-website/"
CATALOGUE_IMAGE_VERSION = "20260815-product-images-4"
PRODUCT_TYPE_LABELS = {
    "hoodie": "卫衣 / 帽衫",
    "jacket": "夹克 / 防水外套",
    "vest": "工作背心 / 功能背心",
    "pants": "工作裤 / 功能裤",
    "workshirt": "工作衫 / Polo / T恤",
    "accessory": "工装配件 / 周边",
    "coverall": "连体服 / 工装",
    "polo": "Polo / T恤",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def inquiry_query(product: dict) -> str:
    """Build an HTML-safe query that works on file:// as well as HTTP."""
    return esc(urlencode({
        "product": product["id"],
        "type": product["product_type"],
        "name": product["name_zh"],
        "need": f'咨询{product["name_zh"]}的供货与定制方案',
    }))


def load_products() -> list[dict]:
    """Load hand-maintained products plus generated catalogue batches."""
    primary = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))["products"]
    generated_path = ROOT / "data/catalogue-a4-remaining.json"
    generated = []
    if generated_path.exists():
        generated = json.loads(generated_path.read_text(encoding="utf-8"))["products"]
    catalogue_78_path = ROOT / "data/catalogue-78-public.json"
    catalogue_78 = []
    if catalogue_78_path.exists():
        catalogue_78 = json.loads(catalogue_78_path.read_text(encoding="utf-8"))["products"]
    products = primary + generated + catalogue_78
    ids = [product["id"] for product in products]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate product ids across product datasets")
    return products


def listing_card(product: dict, index: int) -> str:
    tags = list(dict.fromkeys([product["product_type"], *product.get("tags", [])]))
    variants = product.get("color_variants", [])
    badge = f'{len(variants)}色可选' if len(variants) > 1 else product.get("badge", "画册款")
    loading = "eager" if index < 3 else "lazy"
    return f'''            <div class="product-card reveal" data-filters="{esc(' '.join(tags))}" data-sku="{esc(product.get('sku') or '')}" data-sort-order="{esc(product.get('sort_order') or index + 1)}" data-catalogue-id="{esc(product.get('catalogue_id') or '')}" data-catalogue-name="{esc(product.get('catalogue_name') or '')}" data-added-date="{esc(product.get('added_date') or '')}" data-source-pages="{esc(','.join(str(page) for page in product.get('source_pages', [])))}">
              <div class="product-card__img"><a class="product-card__link" href="product/{esc(product['id'])}.html" aria-label="查看{esc(product['name_zh'])}详情"><img src="{esc(product['main_image'] + '?v=' + CATALOGUE_IMAGE_VERSION)}" alt="{esc(product['image_alt_zh'])}" loading="{loading}" /></a><span class="product-card__badge">{esc(badge)}</span><button class="product-favorite" type="button" data-favorite-id="{esc(product['id'])}" aria-label="收藏{esc(product['name_zh'])}" aria-pressed="false"><span aria-hidden="true">♡</span></button></div>
              <div class="product-card__body">
                <span class="product-card__cat">{esc(product['name_en'])}</span>
                <h3 class="product-card__title"><a href="product/{esc(product['id'])}.html">{esc(product['name_zh'])}</a></h3>
                <p class="product-card__desc">{esc(product['description_zh'])}</p>
                <div class="product-card__meta"><div class="product-card__moq">{esc(product['moq_label'])} <strong>{esc(product['moq_value'])}</strong></div><a href="contact.html?{inquiry_query(product)}" class="product-card__view">咨询 <span aria-hidden="true">→</span></a></div>
              </div>
            </div>'''


def update_listing(products: list[dict]) -> None:
    path = ROOT / "products.html"
    source = path.read_text(encoding="utf-8")
    cards = "\n\n".join(listing_card(product, index) for index, product in enumerate(products))
    source, count = re.subn(
        r'(\s*<!-- PRODUCT_CARDS_START -->).*?(\s*<!-- PRODUCT_CARDS_END -->)',
        lambda match: f'{match.group(1)}\n{cards}\n{match.group(2)}',
        source,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise ValueError("Product card markers are missing")

    type_counts: dict[str, int] = {}
    token_counts: dict[str, int] = {}
    for product in products:
        product_type = product["product_type"]
        type_counts[product_type] = type_counts.get(product_type, 0) + 1
        for token in set([product_type, *product.get("tags", [])]):
            token_counts[token] = token_counts.get(token, 0) + 1

    def replace_count(match: re.Match[str]) -> str:
        value = match.group("value")
        if value == "all":
            count_value = len(products)
        else:
            count_value = type_counts.get(value, token_counts.get(value, 0))
        return f'{match.group("prefix")}{count_value}{match.group("suffix")}'

    source = re.sub(
        r'(?P<prefix><input[^>]+value="(?P<value>[^"]+)"[^>]*/>\s*<span>.*?</span>\s*<span class="count">)\d+(?P<suffix></span>)',
        replace_count,
        source,
        flags=re.S,
    )
    category_count = len(type_counts)
    source = re.sub(r'(<div class="page-header__meta-num">)\d+(</div>\s*<div class="page-header__meta-label">画册产品方案</div>)', rf'\g<1>{len(products)}\2', source, count=1)
    source = re.sub(r'(<div class="page-header__meta-num">)\d+(</div>\s*<div class="page-header__meta-label">产品分类</div>)', rf'\g<1>{category_count}\2', source, count=1)
    source = re.sub(r'(共\s*<strong>)\d+(</strong>\s*款产品)', rf'\g<1>{len(products)}\2', source, count=1)
    path.write_text(source, encoding="utf-8")


def update_sitemap(products: list[dict]) -> None:
    path = ROOT / "sitemap.xml"
    source = path.read_text(encoding="utf-8")
    source = re.sub(r'\n\s*<url><loc>[^<]+/product/[^<]+</loc></url>', '', source)
    urls = "\n".join(
        f'  <url><loc>{BASE_URL}product/{esc(product["id"])}.html</loc></url>'
        for product in products if product.get("visibility") == "public"
    )
    source = source.replace("</urlset>", f"{urls}\n</urlset>")
    path.write_text(source, encoding="utf-8")


def development_copy(product: dict) -> tuple[str, str, str, str]:
    """Return truthful front-end copy for the product's recorded supply mode."""
    if product.get("supply_mode") == "catalogue_inquiry":
        return (
            product.get("badge", "画册款"),
            "CATALOGUE PRODUCT · 画册选款询价",
            "画册款 / 供货与定制条件待确认",
            "本页为画册产品资料，用于选款、询价与定制沟通。",
        )
    return (
        product.get("badge", "ODM方案"),
        "ODM PROPOSAL · 用于开发沟通",
        "ODM方案 / 用于开发沟通",
        "本页为ODM方案，用于选款、来图来样与开发沟通。",
    )


def update_listing_inquiry_links(products: list[dict]) -> None:
    """Keep listing CTAs in sync with the structured catalogue data."""
    path = ROOT / "products.html"
    source = path.read_text(encoding="utf-8")
    updated = source
    for product in products:
        pattern = rf'href="contact\.html\?product={re.escape(product["id"])}[^"]*"'
        replacement = f'href="contact.html?{inquiry_query(product)}"'
        updated, count = re.subn(pattern, replacement, updated, count=1)
        if count != 1:
            raise ValueError(f'Expected one listing inquiry link for {product["id"]}, found {count}')
    if updated != source:
        path.write_text(updated, encoding="utf-8")


def read_shell() -> tuple[str, str]:
    source = (ROOT / "products.html").read_text(encoding="utf-8")
    header_start = source.index("  <!-- ============ Header ============ -->")
    main_start = source.index("  <main", header_start)
    footer_start = source.index("  <!-- ============ Footer ============ -->")
    footer_end = source.index("</body>", footer_start)
    footer = source[footer_start:footer_end]
    footer = re.sub(r'\n\s*<script\s+src="js/main\.js[^"]*"[^>]*></script>\s*$', '', footer)
    return source[header_start:main_start], footer


def prefix_relative_urls(fragment: str) -> str:
    """Make links/assets in the shared shell work from product/<id>.html."""

    def replace(match: re.Match[str]) -> str:
        attr, value = match.group(1), match.group(2)
        if value.startswith(("../", "/", "#", "http:", "https:", "mailto:", "tel:", "javascript:")):
            return match.group(0)
        return f'{attr}="../{value}"'

    fragment = re.sub(r'(href|src)="([^"]+)"', replace, fragment)
    return fragment.replace("location.href='contact.html'", "location.href='../contact.html'")


def page_html(product: dict, related: list[dict], header: str, footer: str) -> str:
    product_id = product["id"]
    title = f'{product["name_zh"]}｜{product["name_en"]} - 卓圣轩服贸'
    badge, eyebrow, development_value, description_suffix = development_copy(product)
    description = f'{product["description_zh"]} {description_suffix}'
    canonical = f"{BASE_URL}product/{product_id}.html"
    category = PRODUCT_TYPE_LABELS.get(product["product_type"], product["product_type"])
    inquiry = inquiry_query(product)
    pages = "、".join(str(page) for page in product["source_pages"])
    main_image = "../" + product["main_image"] + "?v=" + CATALOGUE_IMAGE_VERSION
    gallery = [
        f"../{image}?v={CATALOGUE_IMAGE_VERSION}"
        for image in product.get("gallery_images", [])
    ]
    detail_images = [
        f"../{image}?v={CATALOGUE_IMAGE_VERSION}"
        for image in product.get("detail_images", [])
    ]
    colour_variants = product.get("color_variants", [])
    is_colour_gallery = bool(colour_variants)
    gallery_eyebrow = "COLOUR OPTIONS" if is_colour_gallery else "CATALOGUE REFERENCE"
    gallery_title = "同款颜色单品参考" if is_colour_gallery else "画册原页与方案参考"
    gallery_description = (
        "以下颜色图均为对应PDF画册页直接裁切的单品图，不使用整页画册，也未重新生成产品细节。"
        if is_colour_gallery
        else "以下图片保留画册中的原始方案信息，用于选款、细节确认和后续开发沟通。"
    )
    gallery_markup = "\n".join(
        f'''            <figure class="product-detail__gallery-item">
              <a href="{esc(image)}" data-catalogue-lightbox aria-label="放大查看{esc(product["name_zh"])}单品图">
                <img src="{esc(image)}" alt="{esc(product["image_alt_zh"])}" loading="lazy" />
                <span class="product-detail__zoom-hint" aria-hidden="true">查看单品图 <span>↗</span></span>
              </a>
              <figcaption>画册原页图 · PDF第 {esc(pages)} 页 · 点击可放大</figcaption>
            </figure>'''
        for image in gallery
    ) or '<p class="product-detail__empty">当前数据未配置画册原页图。</p>'
    colour_picker_markup = ""
    if is_colour_gallery:
        colour_links = "\n".join(
            f'''              <button type="button" class="product-detail__colour-thumb{' is-active' if variant["image"] == product["main_image"] else ''}" data-colour-src="{esc('../' + variant["image"] + '?v=' + CATALOGUE_IMAGE_VERSION)}" data-colour-alt="{esc(product["name_zh"])}{esc(variant["label_zh"])}单品图" data-colour-label="{esc(variant["label_zh"])}" aria-label="切换主图为{esc(variant["label_zh"])}" aria-pressed="{'true' if variant["image"] == product["main_image"] else 'false'}">
                <img src="{esc('../' + variant["image"])}" alt="{esc(product["name_zh"])}{esc(variant["label_zh"])}单品图" />
                <span>{esc(variant["label_zh"])}</span>
              </button>'''
            for variant in colour_variants
        )
        initial_colour = next(
            (variant["label_zh"] for variant in colour_variants if variant["image"] == product["main_image"]),
            colour_variants[0]["label_zh"],
        )
        colour_picker_markup = f'''          <div class="product-detail__colour-picker" data-product-colour-picker aria-label="{esc(product["name_zh"])}颜色选择">
            <div class="product-detail__colour-heading"><span>颜色选择</span><strong data-product-colour-label>{esc(initial_colour)}</strong></div>
            <div class="product-detail__colour-list">
{colour_links}
            </div>
          </div>'''

    if is_colour_gallery and detail_images:
        detail_markup = "\n".join(
            f'''            <figure class="product-detail__gallery-item">
              <a href="{esc(image)}" data-catalogue-lightbox aria-label="放大查看{esc(product["name_zh"])}工艺细节">
                <img src="{esc(image)}" alt="{esc(product["name_zh"])}面料与反光条工艺细节" loading="lazy" />
                <span class="product-detail__zoom-hint" aria-hidden="true">查看细节 <span>↗</span></span>
              </a>
              <figcaption>产品工艺细节参考 · 点击可放大</figcaption>
            </figure>'''
            for image in detail_images
        )
        gallery_section_markup = f'''    <section class="product-detail-section">
      <div class="cf-container">
        <div class="product-detail__section-heading">
          <p class="cf-eyebrow"><span class="cf-eyebrow-line"></span><span>DETAIL VIEW</span></p>
          <h2>面料与工艺细节</h2>
          <p>用于查看面料纹理、口袋结构、门襟与反光条等局部细节；颜色与规格仍以询价确认结果为准。</p>
        </div>
        <div class="product-detail__gallery product-detail__gallery--detail">{detail_markup}
        </div>
      </div>
    </section>
'''
    elif is_colour_gallery:
        gallery_section_markup = ""
    else:
        gallery_section_markup = f'''    <section class="product-detail-section">
      <div class="cf-container">
        <div class="product-detail__section-heading">
          <p class="cf-eyebrow"><span class="cf-eyebrow-line"></span><span>{esc(gallery_eyebrow)}</span></p>
          <h2>{esc(gallery_title)}</h2>
          <p>{esc(gallery_description)}</p>
        </div>
        <div class="product-detail__gallery">{gallery_markup}
        </div>
      </div>
    </section>
'''

    related_markup = "\n".join(
        f'''            <a class="product-detail__related-card" href="{esc("../product/" + item["id"] + ".html")}">
              <img src="{esc("../" + item["main_image"] + "?v=" + CATALOGUE_IMAGE_VERSION)}" alt="{esc(item["image_alt_zh"])}" loading="lazy" />
              <span><small>{esc(item["name_en"])}</small><strong>{esc(item["name_zh"])}</strong></span>
            </a>'''
        for item in related
    )
    product_images = list(dict.fromkeys(
        [BASE_URL + product["main_image"]]
        + [BASE_URL + item for item in product.get("gallery_images", [])]
        + [BASE_URL + item for item in product.get("detail_images", [])]
    ))
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product["name_en"],
        "alternateName": product["name_zh"],
        "description": product["description_zh"],
        "image": product_images,
        "category": category,
        "identifier": product_id,
        "additionalProperty": [
            {"@type": "PropertyValue", "name": "供货方式", "value": development_value},
            {"@type": "PropertyValue", "name": "画册来源", "value": product["catalogue_name"]},
            {"@type": "PropertyValue", "name": "来源页码", "value": pages},
        ],
    }
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <link rel="canonical" href="{esc(canonical)}" />
  <meta property="og:type" content="product" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:url" content="{esc(canonical)}" />
  <meta property="og:image" content="{esc(BASE_URL + product["main_image"])}" />
  <link rel="icon" href="../assets/favicon.ico" sizes="any" />
  <link rel="apple-touch-icon" href="../assets/logo-mark.png" />
  <link rel="stylesheet" href="../css/brand.css?v=20260815-catalogue-final-5" />
  <script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False, separators=(",", ":"))}</script>
</head>
<body>
{prefix_relative_urls(header)}
  <main role="main">
    <section class="product-detail-hero">
      <div class="cf-container">
        <nav class="product-detail__breadcrumb" aria-label="面包屑导航">
          <a href="../index.html">首页</a><span aria-hidden="true">/</span>
          <a href="../products.html">产品中心</a><span aria-hidden="true">/</span>
          <span>{esc(product["name_zh"])}</span>
        </nav>
        <div class="product-detail__hero-grid">
          <div class="product-detail__media-column">
            <div class="product-detail__main-media{' product-detail__main-media--contain' if is_colour_gallery else ''}">
              <img src="{esc(main_image)}" alt="{esc(product["image_alt_zh"])}" data-product-colour-main />
              <span class="product-detail__badge">{esc(badge)}</span>
            </div>
{colour_picker_markup}
          </div>
          <div class="product-detail__intro">
            <p class="product-detail__eyebrow">{esc(eyebrow)}</p>
            <h1>{esc(product["name_zh"])}</h1>
            <p class="product-detail__name-en">{esc(product["name_en"])}</p>
            <p class="product-detail__description">{esc(product["description_zh"])}</p>
            <div class="product-detail__actions">
              <a class="cf-btn cf-btn-primary" href="../contact.html?{inquiry}">咨询此产品 <span aria-hidden="true">→</span></a>
              <button class="product-detail__favorite product-favorite" type="button" data-favorite-id="{esc(product['id'])}" aria-label="收藏{esc(product['name_zh'])}" aria-pressed="false"><span aria-hidden="true">♡</span> 收藏</button>
              <a class="product-detail__back-link" href="../products.html">返回产品中心</a>
            </div>
            <dl class="product-detail__facts">
              <div><dt>产品类别</dt><dd>{esc(category)}</dd></div>
              <div><dt>供货方式</dt><dd>{esc(development_value)}</dd></div>
              <div><dt>画册来源</dt><dd>{esc(product["catalogue_name"])}</dd></div>
              <div><dt>来源页码</dt><dd>第 {esc(pages)} 页</dd></div>
            </dl>
          </div>
        </div>
      </div>
    </section>

{gallery_section_markup}
    <section class="product-detail-related">
      <div class="cf-container">
        <div class="product-detail__section-heading">
          <p class="cf-eyebrow"><span class="cf-eyebrow-line"></span><span>RELATED PROPOSALS</span></p>
          <h2>相关产品方案</h2>
        </div>
        <div class="product-detail__related-grid">{related_markup}
        </div>
      </div>
    </section>

    <section class="product-detail-cta">
      <div class="cf-container product-detail-cta__inner">
        <div><p class="cf-eyebrow"><span class="cf-eyebrow-line"></span><span>START YOUR PROJECT</span></p><h2>需要确认这款产品的开发路径？</h2><p>提交产品名称、目标数量、市场和设计要求，我们根据方案资料继续沟通。</p></div>
        <a class="cf-btn cf-btn-primary" href="../contact.html?{inquiry}">获取供应方案 <span aria-hidden="true">→</span></a>
      </div>
    </section>
  </main>
{prefix_relative_urls(footer)}
  <script src="../js/main.js?v=20260815-catalogue-final-5"></script>
</body>
</html>
'''


def generate() -> int:
    products = load_products()
    update_listing(products)
    update_listing_inquiry_links(products)
    update_sitemap(products)
    header, footer = read_shell()
    output_dir = ROOT / "product"
    output_dir.mkdir(exist_ok=True)
    for index, product in enumerate(products):
        sku = product.get("sku")
        related = [
            item for item in products
            if item["id"] != product["id"] and (not sku or item.get("sku") != sku)
        ]
        # Adjacent catalogue entries make the related rail predictable and stable.
        start = index % len(related)
        related = (related[start:] + related[:start])[:3]
        (output_dir / f'{product["id"]}.html').write_text(
            page_html(product, related, header, footer), encoding="utf-8"
        )
    print(f"Generated {len(products)} product pages in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(generate())
