<?php
if (!defined('ABSPATH')) {
    exit;
}
get_header();
?>
<section class="vasture-not-found">
  <div class="cf-container">
    <div class="vasture-not-found__card">
      <p class="vasture-not-found__eyebrow">404</p>
      <h1><?php echo esc_html(vasture_t('页面未找到', 'Page Not Found')); ?></h1>
      <p><?php echo esc_html(vasture_t('您访问的页面可能已移动、改名或不存在。您可以返回首页、浏览产品目录，或直接提交采购需求。', 'The page may have moved, been renamed or no longer exist. Return home, browse the catalogue, or send us your sourcing requirement.')); ?></p>
      <div class="vasture-not-found__actions">
        <a class="cf-btn cf-btn-primary" href="<?php echo esc_url(vasture_page_url('index')); ?>"><?php echo esc_html(vasture_t('返回首页', 'Back to Home')); ?> <span aria-hidden="true">→</span></a>
        <a class="cf-btn cf-btn-secondary" href="<?php echo esc_url(vasture_page_url('products')); ?>"><?php echo esc_html(vasture_t('查看产品目录', 'Browse Products')); ?> <span aria-hidden="true">→</span></a>
      </div>
    </div>
  </div>
</section>
<?php get_footer();
