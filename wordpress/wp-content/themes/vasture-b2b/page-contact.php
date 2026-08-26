<?php
get_header();
$requested_product = isset($_GET['product']) ? sanitize_title(wp_unslash($_GET['product'])) : '';
$is_en = vasture_is_en();
?>
<section class="vasture-page-header"><div class="cf-container"><h1><?php echo esc_html(vasture_t('联系询价', 'Contact for Inquiry')); ?></h1><p><?php echo esc_html(vasture_t('提交产品编号、采购数量、目标市场和定制要求。我们的销售团队会按画册资料、供货条件与项目要求回复。', 'Share the product ID, quantity, target market and custom requirements. Our sales team will respond based on catalogue references, supply conditions and your project needs.')); ?></p></div></section>
<?php vasture_breadcrumbs(); ?>
<section class="cf-container" style="padding:56px 0 80px"><div class="contact-main"><div class="contact-info-col"><div class="info-card"><div class="ic-head"><div class="ic-icon">✉</div><h3><?php echo esc_html(vasture_t('企业邮箱', 'Business Email')); ?></h3></div><div class="info-list"><div class="info-item"><span class="ii-label"><?php echo esc_html(vasture_t('邮箱', 'Email')); ?></span><span class="ii-value"><a href="mailto:allen@zsxgarment.com">allen@zsxgarment.com</a></span></div></div></div><div class="info-card"><div class="ic-head"><div class="ic-icon">✓</div><h3><?php echo esc_html(vasture_t('询盘资料建议', 'What to Include')); ?></h3></div><div class="info-list"><div class="info-item"><span class="ii-value"><?php echo esc_html(vasture_t('产品型号、目标数量、颜色尺码、标识/包装、目标市场和交期。', 'Product ID, quantity, colours and sizes, branding or packing, target market and delivery timing.')); ?></span></div></div></div></div><div class="quote-form-col"><?php echo do_shortcode('[vasture_inquiry_form product_id="' . esc_attr($requested_product) . '" lang="' . ($is_en ? 'en' : 'zh') . '"]'); ?></div></div></section>
<?php get_footer();
