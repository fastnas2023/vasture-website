# VASTURE WordPress migration

This is the WordPress runtime for the existing VASTURE catalogue site. It deliberately does **not** include WooCommerce: the public path is product discovery, temporary favourites, and inquiry follow-up.

## Local start

1. Copy `.env.example` to `.env` and replace the two passwords.
2. Run `docker compose up -d` from this directory.
3. Open `http://127.0.0.1:8088`, finish the one-time WordPress installer, then log in to `/wp-admin/`.
4. Activate **VASTURE Catalogue Core** and **VASTURE B2B**.
5. In the WordPress sidebar, open **VASTURE Import** and run the catalogue import once.

The importer reads the three existing JSON datasets, uses each stable `id` as the update key, and copies source images to the WordPress Media Library. It is safe to run again after updating a catalogue JSON file.

## What is managed in WordPress

- Product, product type, function and material facets
- Main image, gallery images and colour variants
- Catalogue ID, source PDF/page, added date, supply/MOQ fields
- Chinese/English product copy
- Inquiry records and sales follow-up status

The static pages in the existing repository are used as the initial visual templates. `front-page.php` and the source-page templates preserve their existing page body; the product archive and detail page are WordPress-driven.

## Production packaging

Before deploying to a PHP host, package the `wp-content` directory and copy `css/`, `js/`, and non-product `assets/` into `wp-content/themes/vasture-b2b/static/`. Product images are imported to the Media Library by the importer and should be served from an object-storage CDN in production.
