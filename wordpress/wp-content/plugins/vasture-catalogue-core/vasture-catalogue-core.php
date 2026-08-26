<?php
/**
 * Plugin Name: VASTURE Catalogue Core
 * Description: To B product, catalogue provenance and inquiry management for the VASTURE website. WooCommerce is intentionally not used.
 * Version: 1.0.0
 * Author: 卓圣轩服贸
 */

if (!defined('ABSPATH')) {
    exit;
}

final class Vasture_Catalogue_Core {
    private const PRODUCT_TYPE = 'vasture_product';
    private const INQUIRY_TYPE = 'vasture_inquiry';
    private const PRODUCT_ID_META = '_vasture_product_id';
    private const SOURCE_META = '_vasture_source_path';

    public static function init(): void {
        add_action('init', [self::class, 'register_content_types']);
        add_action('admin_menu', [self::class, 'register_admin_pages']);
        add_action('admin_post_vasture_import_catalogue', [self::class, 'handle_import']);
        add_action('admin_post_vasture_submit_inquiry', [self::class, 'handle_inquiry']);
        add_action('admin_post_nopriv_vasture_submit_inquiry', [self::class, 'handle_inquiry']);
        add_action('add_meta_boxes', [self::class, 'add_product_meta_box']);
        add_action('save_post_' . self::PRODUCT_TYPE, [self::class, 'save_product_meta']);
        add_filter('manage_' . self::PRODUCT_TYPE . '_posts_columns', [self::class, 'product_columns']);
        add_action('manage_' . self::PRODUCT_TYPE . '_posts_custom_column', [self::class, 'render_product_column'], 10, 2);
        add_shortcode('vasture_inquiry_form', [self::class, 'inquiry_form_shortcode']);
    }

    public static function activate(): void {
        self::register_content_types();
        self::setup_site_pages();
        flush_rewrite_rules();
    }

    public static function deactivate(): void {
        flush_rewrite_rules();
    }

    public static function register_content_types(): void {
        register_post_type(self::PRODUCT_TYPE, [
            'labels' => [
                'name' => '产品', 'singular_name' => '产品', 'add_new_item' => '新增产品',
                'edit_item' => '编辑产品', 'all_items' => '全部产品', 'menu_name' => '产品管理',
            ],
            'public' => true,
            'show_in_rest' => true,
            'has_archive' => 'products',
            'rewrite' => ['slug' => 'product', 'with_front' => false],
            'menu_icon' => 'dashicons-products',
            'supports' => ['title', 'editor', 'excerpt', 'thumbnail', 'revisions'],
        ]);

        register_post_type(self::INQUIRY_TYPE, [
            'labels' => ['name' => '询盘', 'singular_name' => '询盘', 'all_items' => '询盘管理', 'menu_name' => '询盘管理'],
            'public' => false,
            'show_ui' => true,
            'show_in_menu' => true,
            'supports' => ['title', 'editor', 'custom-fields'],
            'menu_icon' => 'dashicons-email-alt',
        ]);

        register_taxonomy('vasture_product_type', [self::PRODUCT_TYPE], [
            'labels' => ['name' => '产品类别', 'singular_name' => '产品类别'],
            'public' => true, 'show_in_rest' => true, 'hierarchical' => true,
            'rewrite' => ['slug' => 'product-type'],
        ]);
        register_taxonomy('vasture_product_feature', [self::PRODUCT_TYPE], [
            'labels' => ['name' => '核心功能', 'singular_name' => '核心功能'],
            'public' => true, 'show_in_rest' => true, 'hierarchical' => false,
        ]);
        register_taxonomy('vasture_product_material', [self::PRODUCT_TYPE], [
            'labels' => ['name' => '面料偏好', 'singular_name' => '面料偏好'],
            'public' => true, 'show_in_rest' => true, 'hierarchical' => false,
        ]);

        foreach (['product_id', 'sku', 'name_en', 'badge', 'supply_mode', 'moq_label', 'moq_value', 'catalogue_id', 'catalogue_name', 'source_file', 'source_pages', 'added_date', 'certification_ids'] as $key) {
            register_post_meta(self::PRODUCT_TYPE, '_vasture_' . $key, ['single' => true, 'type' => 'string', 'show_in_rest' => true]);
        }
        foreach (['gallery_ids', 'detail_ids', 'color_variants'] as $key) {
            register_post_meta(self::PRODUCT_TYPE, '_vasture_' . $key, ['single' => true, 'type' => 'array', 'show_in_rest' => ['schema' => ['type' => 'array']]]);
        }
        self::ensure_product_type_terms();
    }

    private static function ensure_product_type_terms(): void {
        $types = ['hoodie' => '卫衣 / 帽衫', 'workshirt' => '工作衫 / Polo / T恤', 'jacket' => '夹克 / 防水外套', 'vest' => '工作背心 / 功能背心', 'pants' => '工作裤 / 功能裤', 'coverall' => '连体服 / 工装', 'accessory' => '工装配件 / 周边', 'polo' => 'Polo / T恤'];
        foreach ($types as $slug => $label) {
            $existing = get_term_by('slug', $slug, 'vasture_product_type');
            if ($existing) {
                continue;
            }
            $by_name = get_term_by('name', $label, 'vasture_product_type');
            if ($by_name) {
                wp_update_term($by_name->term_id, 'vasture_product_type', ['slug' => $slug]);
            } else {
                wp_insert_term($label, 'vasture_product_type', ['slug' => $slug]);
            }
        }
    }

    public static function register_admin_pages(): void {
        add_management_page('导入产品画册', 'VASTURE Import', 'manage_options', 'vasture-import', [self::class, 'render_import_page']);
    }

    public static function render_import_page(): void {
        if (!current_user_can('manage_options')) {
            return;
        }
        $counts = self::dataset_counts();
        $result = isset($_GET['vasture_imported']) ? absint($_GET['vasture_imported']) : null;
        ?>
        <div class="wrap">
          <h1>导入 VASTURE 产品画册</h1>
          <p>导入源：现有网站三份产品 JSON。稳定产品 ID 用于新增或更新，不会重复生成产品。</p>
          <ul>
            <?php foreach ($counts as $name => $count) : ?><li><?php echo esc_html($name . '：' . $count . ' 款'); ?></li><?php endforeach; ?>
          </ul>
          <?php if ($result !== null) : ?><div class="notice notice-success"><p>已处理 <?php echo esc_html((string) $result); ?> 款产品。主图、颜色图与画册资料已同步到媒体库；重复导入只更新已有产品。</p></div><?php endif; ?>
          <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
            <?php wp_nonce_field('vasture_import_catalogue'); ?>
            <input type="hidden" name="action" value="vasture_import_catalogue" />
            <p><label><input type="checkbox" name="copy_images" value="1" checked /> 同步图片到 WordPress 媒体库（首次导入耗时较长）</label></p>
            <?php submit_button('导入 / 更新全部产品'); ?>
          </form>
        </div>
        <?php
    }

    public static function handle_import(): void {
        if (!current_user_can('manage_options')) {
            wp_die('没有权限执行导入。');
        }
        check_admin_referer('vasture_import_catalogue');
        $imported = self::import_catalogue(!empty($_POST['copy_images']));
        wp_safe_redirect(add_query_arg(['page' => 'vasture-import', 'vasture_imported' => $imported], admin_url('tools.php')));
        exit;
    }

    /** Safe to call from a deployment command or the WordPress import screen. */
    public static function import_catalogue(bool $copy_images = true): int {
        $products = self::load_products();
        foreach ($products as $product) {
            self::upsert_product($product, $copy_images);
        }
        return count($products);
    }

    private static function dataset_counts(): array {
        $counts = [];
        foreach (self::dataset_paths() as $path) {
            $payload = self::read_json($path);
            $counts[basename($path)] = count($payload['products'] ?? []);
        }
        return $counts;
    }

    private static function dataset_paths(): array {
        $root = self::source_root();
        return [
            $root . '/data/products.json',
            $root . '/data/catalogue-a4-remaining.json',
            $root . '/data/catalogue-78-public.json',
        ];
    }

    private static function source_root(): string {
        $root = getenv('VASTURE_CATALOGUE_SOURCE') ?: (defined('VASTURE_CATALOGUE_SOURCE') ? VASTURE_CATALOGUE_SOURCE : '');
        return untrailingslashit($root ?: dirname(__DIR__, 4));
    }

    private static function read_json(string $path): array {
        if (!is_readable($path)) {
            wp_die('无法读取产品导入文件：' . esc_html($path));
        }
        $data = json_decode((string) file_get_contents($path), true);
        if (!is_array($data)) {
            wp_die('产品导入文件不是有效 JSON：' . esc_html($path));
        }
        return $data;
    }

    private static function load_products(): array {
        $products = [];
        foreach (self::dataset_paths() as $path) {
            $payload = self::read_json($path);
            foreach ($payload['products'] ?? [] as $product) {
                if (!empty($product['id'])) {
                    $products[$product['id']] = $product;
                }
            }
        }
        return array_values($products);
    }

    private static function find_product(string $stable_id): int {
        $posts = get_posts([
            'post_type' => self::PRODUCT_TYPE,
            'post_status' => 'any',
            'posts_per_page' => 1,
            'fields' => 'ids',
            'meta_key' => self::PRODUCT_ID_META,
            'meta_value' => $stable_id,
        ]);
        return $posts ? (int) $posts[0] : 0;
    }

    private static function upsert_product(array $product, bool $copy_images): int {
        $post_id = self::find_product((string) $product['id']);
        $status_map = ['public' => 'publish', 'draft' => 'draft', 'hidden' => 'private'];
        $postarr = [
            'post_type' => self::PRODUCT_TYPE,
            'post_status' => $status_map[$product['visibility'] ?? 'public'] ?? 'draft',
            'post_title' => sanitize_text_field((string) ($product['name_zh'] ?? $product['id'])),
            'post_name' => sanitize_title((string) $product['id']),
            'post_content' => wp_kses_post((string) ($product['description_zh'] ?? '')),
            'post_excerpt' => sanitize_textarea_field((string) ($product['description_zh'] ?? '')),
            'menu_order' => absint($product['sort_order'] ?? 0),
        ];
        if ($post_id) {
            $postarr['ID'] = $post_id;
            wp_update_post(wp_slash($postarr));
        } else {
            $post_id = wp_insert_post(wp_slash($postarr));
        }
        if (is_wp_error($post_id) || !$post_id) {
            return 0;
        }

        $fields = ['id' => 'product_id', 'sku' => 'sku', 'name_en' => 'name_en', 'badge' => 'badge', 'supply_mode' => 'supply_mode', 'moq_label' => 'moq_label', 'moq_value' => 'moq_value', 'catalogue_id' => 'catalogue_id', 'catalogue_name' => 'catalogue_name', 'source_file' => 'source_file', 'added_date' => 'added_date'];
        foreach ($fields as $source => $meta) {
            update_post_meta($post_id, '_vasture_' . $meta, sanitize_text_field((string) ($product[$source] ?? '')));
        }
        update_post_meta($post_id, '_vasture_source_pages', implode(', ', array_map('absint', (array) ($product['source_pages'] ?? []))));
        update_post_meta($post_id, '_vasture_stock_status', sanitize_key((string) ($product['stock_status'] ?? '')));
        update_post_meta($post_id, '_vasture_source_status', sanitize_key((string) ($product['source_status'] ?? 'catalogue_linked')));

        $type = sanitize_title((string) ($product['product_type'] ?? ''));
        $type_term = $type ? get_term_by('slug', $type, 'vasture_product_type') : false;
        if ($type_term) {
            wp_set_object_terms($post_id, [(int) $type_term->term_id], 'vasture_product_type', false);
        }
        $tag_map = [
            'reflective' => ['reflective', 'hi-vis', 'high-visibility'],
            'flame-resistant' => ['flame-resistant', 'flame-retardant', 'fr'],
            'waterproof' => ['waterproof', 'rainproof'],
            'stretch' => ['stretch'],
            'winter' => ['winter', 'insulated'],
        ];
        $feature_labels = ['reflective' => '反光 / 高可视', 'flame-resistant' => '阻燃', 'waterproof' => '防水', 'stretch' => '弹力', 'winter' => '保暖'];
        $material_map = ['mesh' => ['mesh'], 'softshell' => ['softshell'], 'knitwear' => ['knitwear', 'fleece']];
        $material_labels = ['mesh' => '网眼', 'softshell' => '软壳', 'knitwear' => '针织 / 抓绒'];
        $tags = array_map('sanitize_title', (array) ($product['tags'] ?? []));
        $features = [];
        foreach ($tag_map as $slug => $candidates) { if (array_intersect($tags, $candidates)) { $features[] = $feature_labels[$slug]; } }
        $materials = [];
        foreach ($material_map as $slug => $candidates) { if (array_intersect($tags, $candidates)) { $materials[] = $material_labels[$slug]; } }
        wp_set_object_terms($post_id, $features, 'vasture_product_feature', false);
        wp_set_object_terms($post_id, $materials, 'vasture_product_material', false);

        if ($copy_images) {
            $main = self::import_image((string) ($product['main_image'] ?? ''), $post_id, (string) ($product['image_alt_zh'] ?? ''));
            if ($main) { set_post_thumbnail($post_id, $main); }
            $gallery = self::import_images((array) ($product['gallery_images'] ?? []), $post_id, (string) ($product['name_zh'] ?? '产品') . ' 画册资料');
            $detail = self::import_images((array) ($product['detail_images'] ?? []), $post_id, (string) ($product['name_zh'] ?? '产品') . ' 细节参考');
            update_post_meta($post_id, '_vasture_gallery_ids', $gallery);
            update_post_meta($post_id, '_vasture_detail_ids', $detail);
            $variants = [];
            foreach ((array) ($product['color_variants'] ?? []) as $variant) {
                $image_id = self::import_image((string) ($variant['image'] ?? ''), $post_id, (string) ($variant['label_zh'] ?? '产品颜色'));
                $variants[] = ['label_zh' => sanitize_text_field((string) ($variant['label_zh'] ?? '')), 'label_en' => sanitize_text_field((string) ($variant['label_en'] ?? '')), 'attachment_id' => $image_id, 'source' => sanitize_text_field((string) ($variant['image'] ?? ''))];
            }
            update_post_meta($post_id, '_vasture_color_variants', $variants);
        }
        return (int) $post_id;
    }

    private static function import_images(array $paths, int $post_id, string $alt): array {
        $ids = [];
        foreach ($paths as $path) {
            $id = self::import_image((string) $path, $post_id, $alt);
            if ($id) { $ids[] = $id; }
        }
        return array_values(array_unique($ids));
    }

    private static function import_image(string $relative_path, int $post_id, string $alt): int {
        $relative_path = ltrim(str_replace('\\', '/', $relative_path), '/');
        if (!$relative_path || str_contains($relative_path, '../')) {
            return 0;
        }
        $existing = get_posts(['post_type' => 'attachment', 'post_status' => 'inherit', 'posts_per_page' => 1, 'fields' => 'ids', 'meta_key' => self::SOURCE_META, 'meta_value' => $relative_path]);
        if ($existing) {
            return (int) $existing[0];
        }
        $source = self::source_root() . '/' . $relative_path;
        if (!is_readable($source)) {
            return 0;
        }
        $upload = wp_upload_dir();
        if (!empty($upload['error'])) {
            return 0;
        }
        $filename = wp_unique_filename($upload['path'], wp_basename($source));
        $destination = trailingslashit($upload['path']) . $filename;
        if (!copy($source, $destination)) {
            return 0;
        }
        $filetype = wp_check_filetype($filename, null);
        $attachment_id = wp_insert_attachment([
            'post_mime_type' => $filetype['type'] ?: 'image/webp',
            'post_title' => sanitize_file_name(pathinfo($filename, PATHINFO_FILENAME)),
            'post_status' => 'inherit',
            'post_parent' => $post_id,
        ], $destination, $post_id);
        if (is_wp_error($attachment_id) || !$attachment_id) {
            return 0;
        }
        require_once ABSPATH . 'wp-admin/includes/image.php';
        wp_update_attachment_metadata($attachment_id, wp_generate_attachment_metadata($attachment_id, $destination));
        update_post_meta($attachment_id, self::SOURCE_META, $relative_path);
        update_post_meta($attachment_id, '_wp_attachment_image_alt', sanitize_text_field($alt));
        return (int) $attachment_id;
    }

    public static function add_product_meta_box(): void {
        add_meta_box('vasture-product-data', 'To B 产品资料与画册溯源', [self::class, 'render_product_meta_box'], self::PRODUCT_TYPE, 'normal', 'high');
    }

    public static function render_product_meta_box(WP_Post $post): void {
        wp_nonce_field('vasture_product_meta', 'vasture_product_meta_nonce');
        $fields = ['product_id' => '稳定产品 ID', 'sku' => '型号 / SKU', 'name_en' => '英文名称', 'badge' => '前台标记', 'supply_mode' => '供货方式', 'moq_label' => 'MOQ 标签', 'moq_value' => 'MOQ 值', 'catalogue_id' => '画册 ID', 'catalogue_name' => '画册名称', 'source_file' => 'PDF 文件', 'source_pages' => 'PDF 页码', 'added_date' => '录入日期', 'certification_ids' => '认证文件 ID（逗号分隔）'];
        echo '<table class="form-table"><tbody>';
        foreach ($fields as $key => $label) {
            $value = get_post_meta($post->ID, '_vasture_' . $key, true);
            echo '<tr><th><label for="vasture_' . esc_attr($key) . '">' . esc_html($label) . '</label></th><td><input class="regular-text" id="vasture_' . esc_attr($key) . '" name="vasture_meta[' . esc_attr($key) . ']" value="' . esc_attr((string) $value) . '" />' . ($key === 'certification_ids' ? '<p class="description">例如：dk-ppe002779-i01。仅在产品型号明确属于证书范围后填写。</p>' : '') . '</td></tr>';
        }
        $variants = get_post_meta($post->ID, '_vasture_color_variants', true);
        echo '<tr><th><label for="vasture_color_variants">颜色图数据</label></th><td><textarea class="large-text code" rows="7" id="vasture_color_variants" name="vasture_color_variants" placeholder="导入产品会自动生成。">' . esc_textarea(wp_json_encode($variants ?: [], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT)) . '</textarea><p class="description">每项包含中文/英文颜色名和媒体库 attachment_id。首次维护建议通过重新导入 JSON 完成。</p></td></tr>';
        echo '</tbody></table>';
    }

    public static function save_product_meta(int $post_id): void {
        if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) { return; }
        if (!isset($_POST['vasture_product_meta_nonce']) || !wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['vasture_product_meta_nonce'])), 'vasture_product_meta')) { return; }
        if (!current_user_can('edit_post', $post_id)) { return; }
        foreach ((array) ($_POST['vasture_meta'] ?? []) as $key => $value) {
            update_post_meta($post_id, '_vasture_' . sanitize_key($key), sanitize_text_field(wp_unslash($value)));
        }
        if (isset($_POST['vasture_color_variants'])) {
            $variants = json_decode(wp_unslash($_POST['vasture_color_variants']), true);
            if (is_array($variants)) { update_post_meta($post_id, '_vasture_color_variants', $variants); }
        }
    }

    public static function product_columns(array $columns): array {
        return ['cb' => $columns['cb'], 'thumbnail' => '主图', 'title' => '产品名称', 'product_id' => '稳定 ID', 'sku' => 'SKU', 'catalogue' => '画册来源', 'date' => '日期'];
    }

    public static function render_product_column(string $column, int $post_id): void {
        if ($column === 'thumbnail') { echo get_the_post_thumbnail($post_id, [48, 48]); }
        if ($column === 'product_id') { echo esc_html((string) get_post_meta($post_id, '_vasture_product_id', true)); }
        if ($column === 'sku') { echo esc_html((string) get_post_meta($post_id, '_vasture_sku', true)); }
        if ($column === 'catalogue') { echo esc_html((string) get_post_meta($post_id, '_vasture_catalogue_name', true)); }
    }

    public static function inquiry_form_shortcode(array $atts): string {
        $atts = shortcode_atts(['product_id' => '', 'lang' => 'zh'], $atts, 'vasture_inquiry_form');
        $product_id = sanitize_title((string) $atts['product_id']);
        $is_en = sanitize_key((string) $atts['lang']) === 'en';
        $success = isset($_GET['inquiry']) && $_GET['inquiry'] === 'sent';
        ob_start(); ?>
        <div class="vasture-inquiry-form" id="inquiry-form">
          <h2 style="margin-top:0"><?php echo esc_html($is_en ? 'Inquiry & Customisation' : '询价与定制沟通'); ?></h2>
          <?php if ($success) : ?><p class="vasture-inquiry-success"><?php echo esc_html($is_en ? 'We have received your request and will reply shortly.' : '已收到您的需求，我们会尽快回复。'); ?></p><?php endif; ?>
          <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
            <?php wp_nonce_field('vasture_submit_inquiry', 'vasture_inquiry_nonce'); ?>
            <input type="hidden" name="action" value="vasture_submit_inquiry" />
            <input type="hidden" name="product_id" value="<?php echo esc_attr($product_id); ?>" />
            <input type="hidden" name="redirect_to" value="<?php echo esc_url($is_en ? add_query_arg('lang', 'en', get_permalink()) : get_permalink()); ?>" />
            <div class="vasture-inquiry-form__grid"><label><?php echo esc_html($is_en ? 'Name' : '姓名'); ?> <input required name="name" autocomplete="name" /></label><label><?php echo esc_html($is_en ? 'Company' : '企业名称'); ?> <input required name="company" autocomplete="organization" /></label><label><?php echo esc_html($is_en ? 'Business Email' : '企业邮箱'); ?> <input required type="email" name="email" autocomplete="email" /></label><label><?php echo esc_html($is_en ? 'Quantity' : '采购数量'); ?> <input name="quantity" placeholder="<?php echo esc_attr($is_en ? 'e.g. 500 pcs' : '例如：500 件'); ?>" /></label></div>
            <label style="margin-top:12px"><?php echo esc_html($is_en ? 'Requirements' : '需求说明'); ?> <textarea required name="message" placeholder="<?php echo esc_attr($is_en ? 'Please include colours, sizes, branding, target market or delivery requirements.' : '请说明颜色、尺码、标识、目标市场或交付要求'); ?>"></textarea></label>
            <p><button type="submit"><?php echo esc_html($is_en ? 'Submit Inquiry' : '提交询盘'); ?></button></p>
          </form>
        </div>
        <?php return (string) ob_get_clean();
    }

    public static function handle_inquiry(): void {
        if (!isset($_POST['vasture_inquiry_nonce']) || !wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['vasture_inquiry_nonce'])), 'vasture_submit_inquiry')) { wp_die('请求已失效，请返回后重试。'); }
        $name = sanitize_text_field(wp_unslash($_POST['name'] ?? ''));
        $company = sanitize_text_field(wp_unslash($_POST['company'] ?? ''));
        $email = sanitize_email(wp_unslash($_POST['email'] ?? ''));
        $message = sanitize_textarea_field(wp_unslash($_POST['message'] ?? ''));
        if (!$name || !$company || !$email || !$message) { wp_die('请完整填写必填信息。'); }
        $inquiry_id = wp_insert_post(['post_type' => self::INQUIRY_TYPE, 'post_status' => 'publish', 'post_title' => $company . ' · ' . $name . ' · ' . current_time('Y-m-d H:i'), 'post_content' => $message]);
        if ($inquiry_id && !is_wp_error($inquiry_id)) {
            update_post_meta($inquiry_id, '_vasture_product_id', sanitize_title(wp_unslash($_POST['product_id'] ?? '')));
            update_post_meta($inquiry_id, '_vasture_name', $name);
            update_post_meta($inquiry_id, '_vasture_company', $company);
            update_post_meta($inquiry_id, '_vasture_email', $email);
            update_post_meta($inquiry_id, '_vasture_quantity', sanitize_text_field(wp_unslash($_POST['quantity'] ?? '')));
            update_post_meta($inquiry_id, '_vasture_status', 'new');
        }
        $redirect = wp_validate_redirect(wp_unslash($_POST['redirect_to'] ?? home_url('/')), home_url('/'));
        wp_safe_redirect(add_query_arg('inquiry', 'sent', $redirect));
        exit;
    }

    public static function setup_site_pages(): void {
        $pages = ['home' => ['首页', 'index.html'], 'about' => ['关于我们', 'about.html'], 'factory' => ['供应链能力', 'factory.html'], 'services' => ['OEM/ODM定制', 'services.html'], 'blog' => ['行业资讯', 'blog.html'], 'resources' => ['采购资料', 'resources.html'], 'contact' => ['联系询价', '']];
        $page_ids = [];
        foreach ($pages as $slug => [$title, $source]) {
            $page = get_page_by_path($slug);
            $page_id = $page ? $page->ID : wp_insert_post(['post_type' => 'page', 'post_status' => 'publish', 'post_title' => $title, 'post_name' => $slug]);
            if ($page_id && $source) { update_post_meta($page_id, '_vasture_source_template', $source); }
            $page_ids[$slug] = (int) $page_id;
        }
        update_option('show_on_front', 'page');
        update_option('page_on_front', $page_ids['home'] ?? 0);
    }
}

Vasture_Catalogue_Core::init();
register_activation_hook(__FILE__, [Vasture_Catalogue_Core::class, 'activate']);
register_deactivation_hook(__FILE__, [Vasture_Catalogue_Core::class, 'deactivate']);
