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
PRODUCT_TYPE_LABELS = {
    "jacket": "夹克 / 防水外套",
    "vest": "工作背心 / 功能背心",
    "pants": "工作裤 / 功能裤",
    "workshirt": "工作衫 / Polo / T恤",
    "accessory": "工装配件 / 周边",
    "coverall": "连体服 / 工装",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def inquiry_query(product: dict) -> str:
    """Build an HTML-safe query that works on file:// as well as HTTP."""
    return esc(urlencode({
        "product": product["id"],
        "type": product["product_type"],
        "name": product["name_zh"],
        "need": f'咨询{product["name_zh"]}的ODM开发方案',
    }))


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
    description = f'{product["description_zh"]} 本页为ODM方案，用于选款、来图来样与开发沟通。'
    canonical = f"{BASE_URL}product/{product_id}.html"
    category = PRODUCT_TYPE_LABELS.get(product["product_type"], product["product_type"])
    inquiry = inquiry_query(product)
    pages = "、".join(str(page) for page in product["source_pages"])
    main_image = "../" + product["main_image"]
    gallery = ["../" + image for image in product.get("gallery_images", [])]
    gallery_markup = "\n".join(
        f'''            <figure class="product-detail__gallery-item">
              <a href="{esc(image)}" data-catalogue-lightbox aria-label="放大查看{esc(product["name_zh"])}画册原页">
                <img src="{esc(image)}" alt="{esc(product["image_alt_zh"])}｜画册原页图" loading="lazy" />
                <span class="product-detail__zoom-hint" aria-hidden="true">查看高清原页 <span>↗</span></span>
              </a>
              <figcaption>画册原页图 · 第 {esc(pages)} 页 · 点击可放大</figcaption>
            </figure>'''
        for image in gallery
    ) or '<p class="product-detail__empty">当前数据未配置画册原页图。</p>'

    related_markup = "\n".join(
        f'''            <a class="product-detail__related-card" href="{esc("../product/" + item["id"] + ".html")}">
              <img src="{esc("../" + item["main_image"])}" alt="{esc(item["image_alt_zh"])}" loading="lazy" />
              <span><small>{esc(item["name_en"])}</small><strong>{esc(item["name_zh"])}</strong></span>
            </a>'''
        for item in related
    )
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product["name_en"],
        "alternateName": product["name_zh"],
        "description": product["description_zh"],
        "image": [BASE_URL + product["main_image"]] + [BASE_URL + item for item in product.get("gallery_images", [])],
        "category": category,
        "identifier": product_id,
        "additionalProperty": [
            {"@type": "PropertyValue", "name": "开发方式", "value": "ODM方案"},
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
  <link rel="stylesheet" href="../css/brand.css?v=20260815-full-catalogue-page-3" />
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
          <div class="product-detail__main-media">
            <img src="{esc(main_image)}" alt="{esc(product["image_alt_zh"])}" />
            <span class="product-detail__badge">ODM方案</span>
          </div>
          <div class="product-detail__intro">
            <p class="product-detail__eyebrow">ODM PROPOSAL · 用于开发沟通</p>
            <h1>{esc(product["name_zh"])}</h1>
            <p class="product-detail__name-en">{esc(product["name_en"])}</p>
            <p class="product-detail__description">{esc(product["description_zh"])}</p>
            <div class="product-detail__actions">
              <a class="cf-btn cf-btn-primary" href="../contact.html?{inquiry}">咨询此产品 <span aria-hidden="true">→</span></a>
              <a class="product-detail__back-link" href="../products.html">返回产品中心</a>
            </div>
            <dl class="product-detail__facts">
              <div><dt>产品类别</dt><dd>{esc(category)}</dd></div>
              <div><dt>开发方式</dt><dd>ODM方案 / 用于开发沟通</dd></div>
              <div><dt>画册来源</dt><dd>{esc(product["catalogue_name"])}</dd></div>
              <div><dt>来源页码</dt><dd>第 {esc(pages)} 页</dd></div>
            </dl>
          </div>
        </div>
      </div>
    </section>

    <section class="product-detail-section">
      <div class="cf-container">
        <div class="product-detail__section-heading">
          <p class="cf-eyebrow"><span class="cf-eyebrow-line"></span><span>CATALOGUE REFERENCE</span></p>
          <h2>画册原页与方案参考</h2>
          <p>以下图片保留画册中的原始方案信息，用于选款、细节确认和后续开发沟通。</p>
        </div>
        <div class="product-detail__gallery">{gallery_markup}
        </div>
      </div>
    </section>

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
  <script src="../js/main.js?v=20260815-full-catalogue-page-3"></script>
</body>
</html>
'''


def generate() -> int:
    data = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))
    products = data["products"]
    update_listing_inquiry_links(products)
    header, footer = read_shell()
    output_dir = ROOT / "product"
    output_dir.mkdir(exist_ok=True)
    for index, product in enumerate(products):
        related = [item for item in products if item["id"] != product["id"]]
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
