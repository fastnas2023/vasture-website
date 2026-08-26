<?php
/** Theme bootstrap for the VASTURE B2B catalogue. */

if (!defined('ABSPATH')) {
    exit;
}

function vasture_asset_url(string $path = ''): string {
    return trailingslashit(get_template_directory_uri()) . 'static/' . ltrim($path, '/');
}

function vasture_setup(): void {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('html5', ['search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script']);
}
add_action('after_setup_theme', 'vasture_setup');

function vasture_language_attributes(string $attributes): string {
    return vasture_is_en() ? 'lang="en" dir="ltr"' : $attributes;
}
add_filter('language_attributes', 'vasture_language_attributes');

function vasture_document_title(array $parts): array {
    if (!vasture_is_en()) {
        return $parts;
    }
    if (is_singular('vasture_product')) {
        $parts['title'] = vasture_product_display_name((int) get_queried_object_id());
    } elseif (is_post_type_archive('vasture_product')) {
        $parts['title'] = 'Workwear Catalogue';
    } elseif (is_front_page()) {
        $parts['title'] = 'Workwear OEM/ODM & Ready Stock';
    } elseif (is_page('contact')) {
        $parts['title'] = 'Contact for Inquiry';
    } elseif (is_page()) {
        $titles = ['about' => 'About ZSX Garment', 'factory' => 'Supply Chain Capability', 'services' => 'OEM / ODM Workwear Services', 'blog' => 'Workwear Sourcing Insights', 'resources' => 'Procurement Resources', 'certifications' => 'Certifications & Compliance'];
        $slug = (string) get_post_field('post_name', get_queried_object_id());
        if (isset($titles[$slug])) {
            $parts['title'] = $titles[$slug];
        }
    }
    return $parts;
}
add_filter('document_title_parts', 'vasture_document_title');

function vasture_enqueue_assets(): void {
    wp_enqueue_style('vasture-brand', vasture_asset_url('css/brand.css'), [], '20260821');
    wp_enqueue_style('vasture-theme', get_stylesheet_uri(), ['vasture-brand'], '20260826-13');
    // The legacy filter is client-side and assumes all product cards are present.
    // The WordPress archive queries filters server-side, so do not let that script
    // overwrite server result counts or pagination on the archive.
    if (!is_post_type_archive('vasture_product')) {
        wp_enqueue_script('vasture-main', vasture_asset_url('js/main.js'), [], '20260826', true);
    }
    if (is_singular('vasture_product')) {
        wp_enqueue_script('vasture-variants', get_template_directory_uri() . '/assets/js/product-variants.js', [], '1.0.0', true);
    }
}
add_action('wp_enqueue_scripts', 'vasture_enqueue_assets');

function vasture_page_url(string $slug): string {
    $url = '';
    if ($slug === 'index') {
        $url = home_url('/');
    } elseif ($slug === 'products') {
        $url = get_post_type_archive_link('vasture_product') ?: home_url('/products/');
    } else {
        $page = get_page_by_path($slug);
        $url = $page ? get_permalink($page) : home_url('/' . $slug . '/');
    }
    return vasture_lang_url($url);
}

function vasture_locale(): string {
    return isset($_GET['lang']) && sanitize_key(wp_unslash($_GET['lang'])) === 'en' ? 'en' : 'zh';
}

/**
 * Repair links such as ?lang=en?type=coverall into normal query parameters.
 * Older shared URLs used a second question mark, which made WordPress treat
 * "en?type=coverall" as the language value and broke both filters and paging.
 */
function vasture_normalize_malformed_language_query(): void {
    if (empty($_GET['lang']) || !is_string($_GET['lang'])) {
        return;
    }

    $raw_language = wp_unslash($_GET['lang']);
    if (!preg_match('/^(en|zh)\\?(.+)$/', $raw_language, $matches)) {
        return;
    }

    parse_str($matches[2], $embedded_args);
    $args = $_GET;
    $args['lang'] = $matches[1];
    foreach ($embedded_args as $key => $value) {
        if (!isset($args[$key])) {
            $args[$key] = $value;
        }
    }

    $request_path = wp_parse_url(wp_unslash($_SERVER['REQUEST_URI'] ?? '/'), PHP_URL_PATH);
    $target = add_query_arg($args, home_url($request_path ?: '/'));
    wp_safe_redirect($target, 302);
    exit;
}
add_action('template_redirect', 'vasture_normalize_malformed_language_query', 1);

function vasture_is_en(): bool {
    return vasture_locale() === 'en';
}

function vasture_lang_url(string $url, ?string $locale = null): string {
    $locale = $locale ?: vasture_locale();
    return $locale === 'en' ? add_query_arg('lang', 'en', $url) : remove_query_arg('lang', $url);
}

function vasture_t(string $zh, string $en): string {
    return vasture_is_en() ? $en : $zh;
}

function vasture_language_switch_url(string $locale): string {
    if (is_singular()) {
        $url = get_permalink();
    } elseif (is_post_type_archive('vasture_product')) {
        $url = get_post_type_archive_link('vasture_product') ?: home_url('/products/');
    } else {
        $url = home_url('/');
    }
    return vasture_lang_url($url, $locale);
}

function vasture_term_label(WP_Term $term): string {
    if (!vasture_is_en()) {
        return $term->name;
    }
    $labels = [
        'vasture_product_type:hoodie' => 'Hoodies & Sweatshirts',
        'vasture_product_type:workshirt' => 'Work Shirts, Polos & Tees',
        'vasture_product_type:jacket' => 'Jackets & Waterproof Outerwear',
        'vasture_product_type:vest' => 'Work & Utility Vests',
        'vasture_product_type:pants' => 'Work & Utility Pants',
        'vasture_product_type:coverall' => 'Coveralls & Workwear',
        'vasture_product_type:accessory' => 'Workwear Accessories',
        'vasture_product_type:polo' => 'Polos & Tees',
        'vasture_product_feature:保暖' => 'Thermal / Insulated',
        'vasture_product_feature:反光 / 高可视' => 'High visibility',
        'vasture_product_feature:弹力' => 'Stretch',
        'vasture_product_feature:防水' => 'Waterproof',
        'vasture_product_feature:阻燃' => 'Flame resistant',
        'vasture_product_material:网眼' => 'Mesh',
        'vasture_product_material:软壳' => 'Softshell',
        'vasture_product_material:针织 / 抓绒' => 'Knit / Fleece',
    ];
    return $labels[$term->taxonomy . ':' . $term->slug] ?? $labels[$term->taxonomy . ':' . $term->name] ?? $term->name;
}

function vasture_product_display_name(int $post_id): string {
    $english = (string) vasture_product_meta($post_id, 'name_en');
    return vasture_is_en() && $english !== '' ? $english : get_the_title($post_id);
}

function vasture_product_summary(int $post_id): string {
    if (vasture_is_en()) {
        return 'For workwear sourcing, OEM and ODM projects. Materials, colours, standards, stock and order terms are confirmed per order.';
    }
    return (string) get_post_field('post_content', $post_id);
}

function vasture_product_badge(int $post_id): string {
    $badge = (string) vasture_product_meta($post_id, 'badge', vasture_t('画册款', 'Catalogue Product'));
    // Catalogue labels are import provenance, not a buyer-facing product benefit.
    if (preg_match('/画册|catalogue/i', $badge)) {
        return '';
    }
    if (!vasture_is_en()) {
        return $badge;
    }
    $labels = [
        '新画册' => 'Latest Catalogue',
        '英文画册' => 'English Catalogue',
        '画册单品参考图' => 'Catalogue Reference',
        '画册款' => 'Catalogue Product',
    ];
    return $labels[$badge] ?? $badge;
}

function vasture_supply_mode_label(string $mode): string {
    if (!vasture_is_en()) {
        return $mode;
    }
    $labels = [
        'catalogue_inquiry' => 'Supply on Inquiry',
        'ready_stock' => 'Ready Stock',
        'oem' => 'OEM Manufacturing',
        'odm' => 'ODM Development',
        'odm_proposal' => 'ODM Proposal',
    ];
    return $labels[$mode] ?? $mode;
}

function vasture_moq_label(int $post_id): string {
    $label = (string) vasture_product_meta($post_id, 'moq_label');
    if (!vasture_is_en()) {
        return $label;
    }
    return $label === '供货' ? 'Supply' : ($label === 'MOQ' ? 'MOQ' : 'Order Terms');
}

function vasture_moq_value(int $post_id): string {
    $value = (string) vasture_product_meta($post_id, 'moq_value');
    if (!vasture_is_en()) {
        return $value;
    }
    $labels = ['询价确认' => 'On Inquiry', '待确认' => 'To Be Confirmed'];
    return $labels[$value] ?? $value;
}

function vasture_whatsapp_url(string $phone): string {
    $message = vasture_t('您好，我想咨询工作服产品、现货或 OEM/ODM 合作。', 'Hello, I would like to discuss workwear sourcing, ready stock or OEM/ODM cooperation.');
    return 'https://wa.me/' . preg_replace('/\D+/', '', $phone) . '?text=' . rawurlencode($message);
}

function vasture_social_profiles(): array {
    // Add the public profile URL for each channel here when it is ready.
    // Empty URLs deliberately render as non-clickable icons instead of fake links.
    return [
        'linkedin' => ['label' => 'LinkedIn', 'url' => ''],
        'facebook' => ['label' => 'Facebook', 'url' => ''],
        'instagram' => ['label' => 'Instagram', 'url' => ''],
        'tiktok' => ['label' => 'TikTok', 'url' => ''],
        'pinterest' => ['label' => 'Pinterest', 'url' => ''],
        'youtube' => ['label' => 'YouTube', 'url' => ''],
        'x' => ['label' => 'X', 'url' => ''],
        'telegram' => ['label' => 'Telegram', 'url' => ''],
    ];
}

function vasture_social_icon_svg(string $platform): string {
    $icons = [
        'whatsapp' => '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16.02 3.2A12.7 12.7 0 0 0 5.1 22.4L3.2 28.8l6.55-1.72A12.8 12.8 0 1 0 16.02 3.2Zm0 22.9c-2.05 0-4.05-.55-5.78-1.6l-.42-.25-3.88 1.02 1.05-3.78-.28-.44a10.19 10.19 0 1 1 9.31 5.05Zm5.58-7.62c-.3-.16-1.75-.86-2.02-.96-.27-.1-.47-.16-.67.16-.2.3-.77.95-.95 1.15-.17.2-.35.22-.64.07a8.29 8.29 0 0 1-2.44-1.5 9.16 9.16 0 0 1-1.69-2.1c-.18-.3-.02-.45.13-.6.13-.13.3-.35.45-.52.15-.18.2-.3.3-.5.1-.2.05-.38-.02-.53-.07-.16-.67-1.62-.92-2.22-.24-.57-.49-.49-.67-.5h-.57c-.2 0-.52.07-.8.37-.27.3-1.05 1.03-1.05 2.5 0 1.48 1.08 2.92 1.23 3.12.15.2 2.12 3.24 5.14 4.55.72.31 1.28.5 1.72.64.72.23 1.38.2 1.9.12.58-.09 1.75-.72 2-1.42.25-.7.25-1.3.18-1.42-.08-.13-.27-.2-.57-.35Z"/></svg>',
        'linkedin' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.45 20.45H16.9v-5.57c0-1.33-.03-3.04-1.86-3.04-1.85 0-2.13 1.45-2.13 2.94v5.67H9.35V9h3.41v1.56h.05c.47-.9 1.63-1.85 3.36-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13ZM7.12 20.45H3.56V9h3.56v11.45ZM22.23 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0h.01Z"/></svg>',
        'facebook' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M24 12.07C24 5.45 18.63.07 12 .07S0 5.45 0 12.07c0 5.99 4.39 10.95 10.13 11.85v-8.38H7.08v-3.47h3.05V9.43c0-3.01 1.79-4.67 4.53-4.67 1.31 0 2.69.24 2.69.24v2.95h-1.52c-1.49 0-1.96.92-1.96 1.87v2.25h3.33l-.53 3.47h-2.8v8.38C19.61 23.03 24 18.06 24 12.07Z"/></svg>',
        'instagram' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.05.07C2.7.27.27 2.7.07 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.2 4.36 2.63 6.78 6.98 6.98C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c4.35-.2 6.78-2.62 6.98-6.98.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95C23.73 2.7 21.3.27 16.95.07 15.67.01 15.26 0 12 0S8.33.01 7.05.07ZM12 5.84A6.16 6.16 0 1 1 12 18.16 6.16 6.16 0 0 1 12 5.84Zm0 10.16a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm4.97-10.41a1.44 1.44 0 1 1 0 2.88 1.44 1.44 0 0 1 0-2.88Z"/></svg>',
        'tiktok' => '<svg viewBox="0 0 448 512" aria-hidden="true"><path d="M448 209.9a210.1 210.1 0 0 1-122.8-39.2v178.8A162.5 162.5 0 1 1 185 188v89.9a74.6 74.6 0 1 0 52.2 71.2V0h88a121.2 121.2 0 0 0 1.9 22.2A122.2 122.2 0 0 0 381 102.4a121.4 121.4 0 0 0 67 20.1z"/></svg>',
        'pinterest' => '<svg viewBox="0 0 496 512" aria-hidden="true"><path d="M204 6.5C104.9 6.5 38 78.5 38 172.7c0 44.6 16.6 84.3 52.5 99.1 5.9 2.4 11.2.1 12.9-6.4 1.2-4.5 4-15.8 5.2-20.5.8-3.3.5-4.5-1.9-7.3-10.3-12-16.9-27.5-16.9-49.6 0-73.9 55.4-141 144.3-141 78.7 0 122 48.1 122 112.3 0 84.5-37.4 155.9-92.9 155.9-30.7 0-53.7-25.4-46.3-56.6 8.8-37.3 26-77.5 26-104.5 0-24.1-13-44.2-39.8-44.2-31.6 0-56.9 32.7-56.9 76.6 0 28 9.5 46.9 9.5 46.9s-32.7 138.5-38.4 162.7c-11.4 48.3-1.7 107.5-.9 113.5.5 3.5 5 4.3 7 .8 2.9-4.7 40.4-50.1 53.1-96.4 3.6-13.1 20.6-80.6 20.6-80.6 10.2 19.5 40 36.7 71.6 36.7 94.2 0 158-85.9 158-200.9C458 72.7 372.8 6.5 204 6.5z"/></svg>',
        'youtube' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M23.5 6.19a3.02 3.02 0 0 0-2.12-2.14C19.5 3.55 12 3.55 12 3.55s-7.5 0-9.38.5A3.02 3.02 0 0 0 .5 6.19C0 8.07 0 12 0 12s0 3.93.5 5.81a3.02 3.02 0 0 0 2.12 2.14c1.88.5 9.38.5 9.38.5s7.5 0 9.38-.5a3.02 3.02 0 0 0 2.12-2.14C24 15.93 24 12 24 12s0-3.93-.5-5.81ZM9.55 15.57V8.43L15.82 12l-6.27 3.57Z"/></svg>',
        'x' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18.9 2H22l-6.78 7.75L23.2 22h-6.25l-4.9-7.56L5.44 22H2.33l7.25-8.29L1.92 2h6.4l4.43 6.9L18.9 2Zm-1.1 18h1.72L7.38 3.9H5.53L17.8 20Z"/></svg>',
        'telegram' => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21.9 3.3 2.8 10.67c-1.3.52-1.29 1.24-.24 1.56l4.9 1.53 1.89 5.77c.23.64.12.9.79.9.51 0 .73-.23 1.02-.5l2.4-2.34 5 3.69c.93.51 1.6.25 1.83-.86l3.25-15.3c.34-1.36-.52-1.98-1.6-1.82ZM8.22 13.41l11.05-6.97c.55-.33 1.05-.15.64.21l-9.47 8.55-.37 3.95-1.85-5.74Z"/></svg>',
    ];
    return $icons[$platform] ?? '';
}

function vasture_nav_is_current(string $slug): bool {
    if ($slug === 'index') {
        return is_front_page();
    }
    if ($slug === 'products') {
        return is_post_type_archive('vasture_product') || is_singular('vasture_product');
    }
    return is_page($slug);
}

function vasture_nav_current_attribute(string $slug): string {
    return vasture_nav_is_current($slug) ? ' aria-current="page"' : '';
}

function vasture_page_display_title(int $post_id): string {
    if (!vasture_is_en()) {
        return get_the_title($post_id);
    }
    $titles = [
        'about' => 'About ZSX Garment',
        'factory' => 'Supply Chain Capability',
        'services' => 'OEM / ODM Services',
        'blog' => 'Workwear Sourcing Insights',
        'resources' => 'Procurement Resources',
        'certifications' => 'Certifications & Compliance',
        'contact' => 'Contact for Inquiry',
    ];
    $slug = (string) get_post_field('post_name', $post_id);
    return $titles[$slug] ?? get_the_title($post_id);
}

function vasture_breadcrumbs(): void {
    if (is_front_page()) {
        return;
    }

    $items = [[
        'label' => vasture_t('首页', 'Home'),
        'url' => vasture_page_url('index'),
    ]];

    if (is_post_type_archive('vasture_product')) {
        $items[] = ['label' => vasture_t('产品中心', 'Products'), 'url' => ''];
    } elseif (is_singular('vasture_product')) {
        $items[] = ['label' => vasture_t('产品中心', 'Products'), 'url' => vasture_page_url('products')];
        $items[] = ['label' => vasture_product_display_name((int) get_queried_object_id()), 'url' => ''];
    } elseif (is_page()) {
        $items[] = ['label' => vasture_page_display_title((int) get_queried_object_id()), 'url' => ''];
    } elseif (is_404()) {
        $items[] = ['label' => vasture_t('页面未找到', 'Page Not Found'), 'url' => ''];
    } else {
        $items[] = ['label' => wp_get_document_title(), 'url' => ''];
    }
    ?>
    <nav class="vasture-breadcrumb" aria-label="<?php echo esc_attr(vasture_t('面包屑导航', 'Breadcrumb')); ?>">
      <div class="cf-container">
        <ol>
          <?php foreach ($items as $index => $item) : ?>
            <li><?php if ($item['url'] !== '') : ?><a href="<?php echo esc_url($item['url']); ?>"><?php echo esc_html($item['label']); ?></a><?php else : ?><span aria-current="page"><?php echo esc_html($item['label']); ?></span><?php endif; ?></li>
          <?php endforeach; ?>
        </ol>
      </div>
    </nav>
    <?php
}

function vasture_rewrite_source_markup(string $html): string {
    $theme_static = esc_url(vasture_asset_url());
    $map = ['index' => vasture_page_url('index'), 'products' => vasture_page_url('products'), 'factory' => vasture_page_url('factory'), 'services' => vasture_page_url('services'), 'blog' => vasture_page_url('blog'), 'resources' => vasture_page_url('resources'), 'about' => vasture_page_url('about'), 'contact' => vasture_page_url('contact')];
    foreach ($map as $file => $url) {
        $html = preg_replace_callback('/href=(["\'])' . preg_quote($file, '/') . '\\.html([^"\']*)\\1/', static function ($matches) use ($url) {
            return 'href=' . $matches[1] . esc_url($url . $matches[2]) . $matches[1];
        }, $html) ?: $html;
    }
    $html = preg_replace_callback('/href="product\/([a-z0-9-]+)\.html"/', static function ($matches) {
        return 'href="' . esc_url(home_url('/product/' . $matches[1] . '/')) . '"';
    }, $html) ?: $html;
    $html = preg_replace('/(?:(?:\.\.\/)?)(assets\/|css\/|js\/)/', $theme_static . '$1', $html) ?: $html;
    $html = str_replace("location.href='contact.html'", "location.href='" . esc_url(vasture_page_url('contact')) . "'", $html);
    return $html;
}

function vasture_translate_source_markup(string $html): string {
    if (!vasture_is_en()) {
        return $html;
    }
    $map = [
        '工作服采购 · OEM / ODM · 现货供应' => 'WORKWEAR SOURCING · OEM / ODM · READY STOCK',
        '工作服现货' => 'Ready-stock Workwear',
        '与 OEM / ODM 定制' => '& OEM / ODM Manufacturing',
        '面向海外品牌、批发商与项目采购，提供功能夹克、工作背心、工作裤、企业上装、连体服与工装配件等产品方案和品牌定制沟通。' => 'For brands, distributors and project buyers: functional jackets, work vests, trousers, corporate tops, coveralls and accessories, with product sourcing and brand manufacturing support.',
        '面向海外品牌、批发商与项目采购，提供反光服、夹克、背心、工作裤与连体服等产品目录、现货确认和品牌定制沟通。' => 'For brands, distributors and project buyers: high-visibility workwear, jackets, vests, trousers and coveralls, with catalogue selection, stock confirmation and private-label support.',
        '获取报价' => 'Request a Quote',
        '查看产品目录' => 'View Product Catalogue',
        '目录选款与库存确认' => 'Catalogue selection & stock confirmation',
        '来图来样与贴牌沟通' => 'Artwork, samples & private-label support',
        '版型、面料与系列开发' => 'Design, fabric & collection development',
        '批发商、品牌与项目采购' => 'Distributors, brands & project buyers',
        '采购流程' => 'PROCUREMENT PROCESS',
        '从选款到交付，按采购节点推进' => 'From selection to delivery, managed by purchase milestones',
        '先从目录或设计需求开始，再逐项确认产品、定制和交付信息。' => 'Start from a catalogue style or design brief, then confirm product, customization and delivery requirements step by step.',
        '选款' => 'Product selection',
        '需求确认' => 'Requirement review',
        '样衣 / 方案' => 'Samples / proposal',
        '批量交付' => 'Bulk delivery',
        '从目录确认产品与应用场景' => 'Confirm product and application from the catalogue',
        '颜色、尺码、标识与包装要求' => 'Colours, sizes, branding and packaging requirements',
        '确认面料、版型与定制路径' => 'Confirm fabric, fit and customisation route',
        '按项目沟通装箱、交期与资料' => 'Confirm packing, lead time and documentation by project',
        '提交采购需求' => 'Send Requirements',
        '了解定制服务' => 'Explore Customisation',
        '咨询交付方案' => 'Discuss Delivery',
        '面向采购的工作服产品目录' => 'Workwear Catalogue for Procurement',
        '按新产品画册的实际品类展示，用于选款、功能确认与 OEM/ODM 开发沟通。' => 'Built around the actual product categories in the latest catalogues for sourcing, feature review and OEM/ODM development.',
        '产品分类快捷入口' => 'Product category shortcuts',
        '全部产品' => 'All Products',
        '工作衫 / Polo / T恤' => 'Work Shirts / Polos / Tees',
        '夹克 / 防水外套' => 'Jackets / Waterproof Outerwear',
        '工作背心 / 功能背心' => 'Work & Utility Vests',
        '工作裤 / 功能裤' => 'Work & Utility Pants',
        '连体服 / 工装' => 'Coveralls / Workwear',
        '工装配件 / 周边' => 'Workwear Accessories',
        '工作衫与企业上装' => 'Work Shirts & Corporate Tops',
        '功能工作衫、T恤、商务衬衫与企业 Polo，支持版型和品牌细节开发' => 'Functional work shirts, tees, business shirts and corporate polos with fit and branding development support.',
        '功能夹克与防水外套' => 'Functional Jackets & Waterproof Outerwear',
        '通风、防水、软壳与多口袋结构，面向户外作业和技术团队' => 'Ventilated, waterproof, softshell and multi-pocket designs for outdoor and technical teams.',
        '工作背心与降温背心' => 'Work Vests & Cooling Vests',
        '多口袋工具背心、蒸发降温与相变降温方案，适合不同作业环境' => 'Multi-pocket utility vests and evaporative or phase-change cooling options for different worksites.',
        '工作裤与功能裤' => 'Work Pants & Utility Pants',
        '保暖、弹力、可拆卸裤腿与护膝结构，适配施工和移动作业' => 'Thermal, stretch, detachable-leg and knee-pad options for construction and mobile work.',
        '冬季防雨连体服' => 'Winter Waterproof Coveralls',
        '防水外层与保暖内里结合，适合寒冷及雨雪作业环境' => 'Waterproof shell with thermal lining for cold, rainy and snowy work environments.',
        '工装配件与装备' => 'Workwear Accessories & Gear',
        '工作帽、背包、装备包、保温餐包与企业礼赠方案' => 'Work caps, backpacks, gear bags, insulated meal bags and corporate gift options.',
        '查看方案' => 'View Range',
        '开始您的采购需求' => 'Start with Your Requirement',
        '按你的采购方式开始' => 'Start with Your Buying Route',
        '不同采购目标对应不同的资料和沟通方式，先选路径，再提交具体需求。' => 'Different buying targets need different information and workflows. Choose a route, then share the specific requirement.',
        '找现货' => 'Find Ready Stock',
        '先看目录款，再询库存、颜色、尺码和装箱信息。' => 'Start with catalogue styles, then confirm stock, colours, sizes and packing.',
        '做 OEM / ODM' => 'Develop OEM / ODM',
        '提交设计稿、样衣或品牌要求，沟通贴牌与产品开发路径。' => 'Share artwork, samples or brand requirements to discuss private-label and product development.',
        '项目采购' => 'Project Procurement',
        '说明数量、目标市场、交付要求和时间节点，获取采购建议。' => 'Share quantity, target market, delivery requirements and timing for sourcing advice.',
        '采购前，先把关键信息说清楚' => 'Clarify the Key Details Before You Buy',
        '产品资料、库存状态和定制要求都按询盘逐项确认，减少反复沟通，让采购判断更直接。' => 'Product information, stock status and custom requirements are confirmed inquiry by inquiry for clearer buying decisions.',
        '产品资料' => 'Product Information',
        '库存与颜色' => 'Stock & Colours',
        '贴牌与开发' => 'Private Label & Development',
        '包装与交付' => 'Packaging & Delivery',
        '看清产品结构，再开始询盘' => 'See the Product Details Before You Inquire',
        '展示面料、反光条、功能口袋、版型细节与定制流程，帮助采购在沟通前快速了解产品方向。' => 'See fabrics, reflective trim, utility pockets, fit details and the customisation process before you start a conversation.',
        '获取产品展示资料' => 'Request Product Presentation',
        '从产品目录或你的设计开始' => 'Start with the Catalogue or Your Design',
        '告诉我们产品型号、数量、目标市场和定制要求，我们会先确认库存或开发路径，再给出合作建议。' => 'Tell us the product ID, quantity, target market and custom requirements. We will confirm stock or the development route, then recommend the next step.',
        '现货与批发' => 'Ready Stock & Wholesale',
        'OEM / ODM 定制' => 'OEM / ODM Customisation',
        '项目采购' => 'Project Procurement',
        '联系我们' => 'Contact Us',
        '现货' => 'STOCK',
        '进入产品目录选款' => 'Browse the product catalogue',
        '进入产品目录' => 'Product selection',
        '了解样衣与定制方案' => 'Explore samples & customisation',
        '咨询批量交付' => 'Discuss bulk delivery',
        '咨询' => 'Discuss delivery',
        '透气拼色企业 Polo 产品方案' => 'Breathable colour-block corporate polo solution',
        '三层弹力软壳工作夹克产品方案' => 'Three-layer stretch softshell work jacket solution',
        '透气多口袋功能工作背心产品方案' => 'Breathable multi-pocket utility vest solution',
        '隐藏护膝功能工作裤产品方案' => 'Utility work pants with concealed knee-pad pockets',
        '冬季防雨保暖连体工作服产品方案' => 'Winter waterproof insulated coverall solution',
        '多分区工具工作背包产品方案' => 'Multi-compartment work gear backpack solution',
        '查看 OEM/ODM 服务 →' => 'Explore OEM/ODM Services →',
        '目录提供型号、面料/克重、反光材料、标准、装箱数量和尺码等采购信息。' => 'The catalogue covers product IDs, fabric weights, reflective materials, standards, packing quantities and size information.',
        '目录款的库存、颜色和尺码以询价确认，先确认可供范围，再进入报价。' => 'Catalogue stock, colours and sizes are confirmed by inquiry before quotation.',
        '支持来图来样、贴牌换标和产品开发沟通，先确认需求，再确认样衣、数量与交期。' => 'We support artwork and sample review, private-label changes and product development, with requirements, samples, quantities and lead times confirmed in order.',
        '面向批发商、品牌方和企业项目采购，支持颜色、尺码、包装和交付要求逐项确认。' => 'For distributors, brands and corporate projects, colours, sizes, packing and delivery requirements are confirmed item by item.',
        '工作服展厅与产品展示视频封面' => 'Workwear showroom and product presentation video cover',
    ];
    return strtr($html, $map);
}

function vasture_source_main(string $source_file): string {
    $source = get_template_directory() . '/static/' . ltrim($source_file, '/');
    if (!is_readable($source)) {
        return '<section class="cf-container" style="padding:80px 0"><p>页面模板暂不可读，请检查主题静态资源挂载。</p></section>';
    }
    $html = (string) file_get_contents($source);
    if (!preg_match('/<main\b[^>]*>(.*?)<\/main>/is', $html, $match)) {
        return '<section class="cf-container" style="padding:80px 0"><p>未能读取页面主体。</p></section>';
    }
    return '<div class="vasture-static-page">' . vasture_translate_source_markup(vasture_rewrite_source_markup($match[1])) . '</div>';
}

function vasture_english_static_page(string $slug): string {
    $pages = [
        'about' => [
            'About ZSX Garment',
            'A B2B workwear sourcing partner for overseas brands, distributors and project buyers.',
            [
                ['Catalogue-led sourcing', 'Select styles from catalogue references, then confirm application, quantities and availability.'],
                ['OEM / ODM collaboration', 'Discuss branding, colours, packaging, samples and development requirements in a practical sequence.'],
                ['Project coordination', 'Confirm samples, production, documentation and delivery milestones around the actual project.'],
            ],
        ],
        'factory' => [
            'Supply Chain Capability',
            'A clear workwear sourcing process from product selection and material review to production coordination and delivery confirmation.',
            [
                ['Product and material review', 'Confirm use case, construction, fabrics, high-visibility requirements and relevant standards before quotation.'],
                ['Sampling and brand execution', 'Coordinate size sets, colour references, logo application, labels and packaging before bulk production.'],
                ['Production and delivery', 'Confirm order quantities, inspection requirements, packing, documents and delivery timing by project.'],
            ],
        ],
        'services' => [
            'OEM / ODM Workwear Services',
            'Use a catalogue product as a starting point, or bring your own design brief for private-label workwear development.',
            [
                ['Ready-stock and wholesale', 'Start with existing catalogue styles and confirm inventory, colours, sizes and packing.'],
                ['OEM private label', 'Apply your branding through labels, logos, packaging and agreed colour or trim changes.'],
                ['ODM development', 'Develop a workwear solution around your target market, required function, fabric direction and delivery plan.'],
            ],
        ],
        'blog' => [
            'Workwear Sourcing Insights',
            'Useful checkpoints for brands, distributors and procurement teams planning functional workwear orders.',
            [
                ['Define the application', 'Clarify trade, working environment, performance needs and relevant safety requirements before choosing a style.'],
                ['Confirm the order specification', 'Use a written brief for colour, sizing, branding, packing, quantity and delivery requirements.'],
                ['Validate before bulk production', 'Confirm approved samples and delivery details before a production order is released.'],
            ],
        ],
        'resources' => [
            'Procurement Resources',
            'Catalogue materials for initial workwear selection, OEM/ODM communication and quotation preparation.',
            [
                ['Product catalogues', 'Use the catalogue to identify product IDs, construction direction, colours and reference images.'],
                ['Inquiry checklist', 'Share product ID, quantity, target market, colour and size requirements, branding and delivery timing.'],
                ['Order confirmation', 'Materials, standards, stock, minimum order quantity and final delivery terms are confirmed per order.'],
            ],
        ],
    ];
    if (!isset($pages[$slug])) {
        return '';
    }
    [$title, $lead, $cards] = $pages[$slug];
    ob_start(); ?>
    <section class="vasture-page-header"><div class="cf-container"><h1><?php echo esc_html($title); ?></h1><p><?php echo esc_html($lead); ?></p></div></section>
    <section class="cf-container vasture-en-page"><div class="vasture-en-page__grid"><?php foreach ($cards as [$card_title, $copy]) : ?><article class="vasture-en-page__card"><h2><?php echo esc_html($card_title); ?></h2><p><?php echo esc_html($copy); ?></p></article><?php endforeach; ?></div><div class="vasture-en-page__cta"><div><span>READY TO DISCUSS YOUR REQUIREMENT?</span><h2>Tell us the product ID, quantity and target market.</h2></div><a class="cf-btn cf-btn-primary" href="<?php echo esc_url(vasture_page_url('contact')); ?>">Request a Quote <span aria-hidden="true">→</span></a></div></section>
    <?php return (string) ob_get_clean();
}

function vasture_product_meta(int $post_id, string $key, $default = '') {
    $value = get_post_meta($post_id, '_vasture_' . $key, true);
    return $value === '' || $value === null ? $default : $value;
}

function vasture_certification_documents(): array {
    static $certifications = null;
    if ($certifications !== null) {
        return $certifications;
    }
    $file = get_template_directory() . '/assets/certifications/certifications.json';
    if (!is_readable($file)) {
        return $certifications = [];
    }
    $decoded = json_decode((string) file_get_contents($file), true);
    return $certifications = is_array($decoded) ? $decoded : [];
}

function vasture_certification_file_url(string $filename): string {
    return trailingslashit(get_template_directory_uri()) . 'assets/certifications/' . rawurlencode(basename($filename));
}

function vasture_product_has_certification(int $post_id, string $certificate_id): bool {
    $assigned = array_filter(array_map('sanitize_title', array_map('trim', explode(',', (string) vasture_product_meta($post_id, 'certification_ids', '')))));
    return in_array(sanitize_title($certificate_id), $assigned, true);
}

function vasture_product_image_url(int $post_id, string $size = 'large'): string {
    $image_id = get_post_thumbnail_id($post_id);
    if ($image_id) {
        $url = wp_get_attachment_image_url($image_id, $size);
        if ($url) {
            return $url;
        }
    }
    return vasture_asset_url('assets/logo-mark.png');
}

function vasture_product_type_label(int $post_id): string {
    $terms = get_the_terms($post_id, 'vasture_product_type');
    return $terms && !is_wp_error($terms) ? vasture_term_label($terms[0]) : vasture_t('工作服产品', 'Workwear Product');
}
