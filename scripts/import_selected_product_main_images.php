<?php
/**
 * Import a narrowly approved set of regenerated main images into WordPress.
 *
 * Usage:
 *   php import_selected_product_main_images.php /absolute/path/to/wp-load.php
 *
 * The script is intentionally idempotent. It reuses an attachment by its
 * source-path meta value, never deletes the previous attachment, and changes
 * only the named products below.
 */

if ($argc < 2 || !is_readable($argv[1])) {
    fwrite(STDERR, "Usage: php {$argv[0]} /absolute/path/to/wp-load.php\n");
    exit(1);
}

require $argv[1];
require_once ABSPATH . 'wp-admin/includes/image.php';

$source_root = dirname(__DIR__);
$updates = [
    'xk-019-short-sleeve-t-shirt' => [
        'source' => 'assets/catalogue-78/main/xk-019-front-complete-ai.webp',
        'alt' => 'XK-019 短袖T恤完整单品主图',
    ],
    'rp01-heat-apply-reflective-tape' => [
        'source' => 'assets/catalogue-a4/main/rp01-silver-clean-ai.webp',
        'alt' => 'RP01 热转印反光条银色单品主图',
        'replace_gallery' => true,
        'replace_variant' => true,
    ],
];

function vasture_import_selected_attachment(string $source_root, string $relative_path, int $post_id, string $alt): int {
    $existing = get_posts([
        'post_type' => 'attachment', 'post_status' => 'inherit', 'posts_per_page' => 1,
        'fields' => 'ids', 'meta_key' => '_vasture_source_path', 'meta_value' => $relative_path,
    ]);
    if ($existing) {
        return (int) $existing[0];
    }
    $source = $source_root . '/' . ltrim($relative_path, '/');
    if (!is_readable($source)) {
        throw new RuntimeException("Image source is missing: {$source}");
    }
    $upload = wp_upload_dir();
    if (!empty($upload['error'])) {
        throw new RuntimeException('WordPress upload directory error: ' . $upload['error']);
    }
    $filename = wp_unique_filename($upload['path'], wp_basename($source));
    $destination = trailingslashit($upload['path']) . $filename;
    if (!copy($source, $destination)) {
        throw new RuntimeException("Could not copy {$source} to WordPress uploads");
    }
    $attachment_id = wp_insert_attachment([
        'post_mime_type' => wp_check_filetype($filename, null)['type'] ?? 'image/webp',
        'post_title' => sanitize_file_name(pathinfo($filename, PATHINFO_FILENAME)),
        'post_status' => 'inherit',
        'post_parent' => $post_id,
    ], $destination, $post_id);
    if (is_wp_error($attachment_id) || !$attachment_id) {
        throw new RuntimeException('Could not create WordPress media attachment');
    }
    wp_update_attachment_metadata($attachment_id, wp_generate_attachment_metadata($attachment_id, $destination));
    update_post_meta($attachment_id, '_vasture_source_path', $relative_path);
    update_post_meta($attachment_id, '_wp_attachment_image_alt', sanitize_text_field($alt));
    return (int) $attachment_id;
}

$result = [];
foreach ($updates as $product_id => $update) {
    $posts = get_posts([
        'post_type' => 'vasture_product', 'post_status' => 'publish', 'posts_per_page' => 1,
        'meta_key' => '_vasture_product_id', 'meta_value' => $product_id,
    ]);
    if (!$posts) {
        throw new RuntimeException("Product not found: {$product_id}");
    }
    $post_id = (int) $posts[0]->ID;
    $attachment_id = vasture_import_selected_attachment($source_root, $update['source'], $post_id, $update['alt']);
    set_post_thumbnail($post_id, $attachment_id);

    if (!empty($update['replace_gallery'])) {
        update_post_meta($post_id, '_vasture_gallery_ids', [$attachment_id]);
    }
    if (!empty($update['replace_variant'])) {
        $variants = (array) get_post_meta($post_id, '_vasture_color_variants', true);
        foreach ($variants as &$variant) {
            $variant['attachment_id'] = $attachment_id;
            $variant['source'] = $update['source'];
        }
        unset($variant);
        update_post_meta($post_id, '_vasture_color_variants', $variants);
    }
    $result[] = ['product_id' => $product_id, 'post_id' => $post_id, 'attachment_id' => $attachment_id, 'source' => $update['source']];
}

echo wp_json_encode($result, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . PHP_EOL;
