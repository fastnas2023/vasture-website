<?php
/**
 * Import the reviewed catalogue-quality replacements into local WordPress.
 *
 * Usage:
 *   php scripts/import_catalogue_quality_replacements.php /absolute/path/to/wp-load.php
 *
 * Existing attachments are retained for rollback. For products whose first
 * colour thumbnail represented the former main image, only that first variant
 * is pointed at the replacement; the remaining colours are untouched.
 */

if ($argc < 2 || !is_readable($argv[1])) {
    fwrite(STDERR, "Usage: php {$argv[0]} /absolute/path/to/wp-load.php\n");
    exit(1);
}

require $argv[1];
require_once ABSPATH . 'wp-admin/includes/image.php';

$source_root = dirname(__DIR__);
$updates = [
    'hvj259-reflective-border-tabard' => [
        'source' => 'assets/catalogue-a4/main/hvj259-hi-vis-yellow-ai-v2.webp',
        'alt' => 'HVJ259 反光包边套头背心荧光黄完整单品主图',
        'method' => 'reviewed-ai-restoration',
        'replace_first_variant' => true,
    ],
    'hvj910-top-cool-v-neck-t-shirt' => [
        'source' => 'assets/catalogue-a4/main/hvj910-hi-vis-yellow-ai-v2.webp',
        'alt' => 'HVJ910 Top Cool V领反光T恤荧光黄完整单品主图',
        'method' => 'reviewed-ai-restoration',
        'replace_first_variant' => true,
    ],
    'hvw706-kensington-jacket' => [
        'source' => 'assets/catalogue-a4/main/hvw706-hi-vis-yellow-ai-v2.webp',
        'alt' => 'HVW706 Kensington反光保暖夹克荧光黄完整单品主图',
        'method' => 'reviewed-ai-restoration',
        'replace_first_variant' => true,
    ],
    'hvw066-print-me-arm-bands' => [
        'source' => 'assets/catalogue-a4/main/hvw066-hi-vis-yellow-ai-v2.webp',
        'alt' => 'HVW066 Print Me荧光黄臂带完整单品主图',
        'method' => 'reviewed-ai-restoration',
        'replace_first_variant' => true,
    ],
    'xk-027-green-quick-drying-work-shirt' => [
        'source' => 'assets/catalogue-78/main/xk-027-front-high-source-v2.webp',
        'alt' => 'XK-027 绿色速干工作衫完整单品主图',
        'method' => '300-dpi-pdf-recrop',
    ],
    'xk-059-stretch-utility-shorts' => [
        'source' => 'assets/catalogue-78/main/xk-059-front-high-source-v2.webp',
        'alt' => 'XK-059 弹力多功能短裤完整单品主图',
        'method' => '300-dpi-pdf-recrop',
    ],
    'xk-121-hi-vis-waterproof-jacket' => [
        'source' => 'assets/catalogue-78/main/xk-121-front-ai-v2.webp',
        'alt' => 'XK-121 高可视防水夹克完整单品主图',
        'method' => 'reviewed-ai-restoration-from-overlapped-catalogue-view',
    ],
];

function vasture_quality_attachment(string $source_root, string $relative_path, int $post_id, string $alt): int {
    $existing = get_posts([
        'post_type' => 'attachment',
        'post_status' => 'inherit',
        'posts_per_page' => 1,
        'fields' => 'ids',
        'meta_key' => '_vasture_source_path',
        'meta_value' => $relative_path,
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
foreach ($updates as $stable_key => $update) {
    $posts = get_posts([
        'post_type' => 'vasture_product',
        'post_status' => 'publish',
        'posts_per_page' => 1,
        'meta_key' => '_vasture_product_id',
        'meta_value' => $stable_key,
    ]);
    if (!$posts) {
        throw new RuntimeException("Product not found: {$stable_key}");
    }
    $post_id = (int) $posts[0]->ID;
    $old_attachment_id = (int) get_post_thumbnail_id($post_id);
    $attachment_id = vasture_quality_attachment($source_root, $update['source'], $post_id, $update['alt']);

    if ($old_attachment_id && $old_attachment_id !== $attachment_id && !get_post_meta($post_id, '_vasture_previous_thumbnail_id', true)) {
        update_post_meta($post_id, '_vasture_previous_thumbnail_id', $old_attachment_id);
    }
    set_post_thumbnail($post_id, $attachment_id);
    update_post_meta($post_id, '_vasture_main_image_method', $update['method']);
    update_post_meta($post_id, '_vasture_main_image_reviewed_at', '2026-09-10');

    if (!empty($update['replace_first_variant'])) {
        $variants = (array) get_post_meta($post_id, '_vasture_color_variants', true);
        if ($variants) {
            $variants[0]['attachment_id'] = $attachment_id;
            $variants[0]['source'] = $update['source'];
            update_post_meta($post_id, '_vasture_color_variants', $variants);
        }
    }

    $result[] = [
        'stable_key' => $stable_key,
        'post_id' => $post_id,
        'old_attachment_id' => $old_attachment_id,
        'attachment_id' => $attachment_id,
        'source' => $update['source'],
    ];
}

echo wp_json_encode($result, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . PHP_EOL;
