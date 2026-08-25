<?php if (!defined('ABSPATH')) { exit; } ?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="#0D2735" />
  <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="vasture-skip-link" href="#main-content"><?php echo esc_html(vasture_t('跳至主要内容', 'Skip to main content')); ?></a>
<header class="site-header" role="banner">
  <div class="cf-container">
    <a href="<?php echo esc_url(vasture_page_url('index')); ?>" class="logo-link"><span class="logo-link__text"><strong><?php echo esc_html(vasture_t('卓圣轩服贸', 'ZSX Garment')); ?></strong><small><?php echo esc_html(vasture_t('扬州卓圣轩服装贸易有限公司', 'Yangzhou ZSX Garment Trading Co., Ltd.')); ?></small></span></a>
    <nav role="navigation" aria-label="<?php echo esc_attr(vasture_t('主导航', 'Main navigation')); ?>">
      <a href="<?php echo esc_url(vasture_page_url('index')); ?>" class="<?php echo vasture_nav_is_current('index') ? 'is-current' : ''; ?>"<?php echo vasture_nav_current_attribute('index'); ?>><?php echo esc_html(vasture_t('首页', 'Home')); ?></a>
      <a href="<?php echo esc_url(vasture_page_url('products')); ?>" class="<?php echo vasture_nav_is_current('products') ? 'is-current' : ''; ?>"<?php echo vasture_nav_current_attribute('products'); ?>><?php echo esc_html(vasture_t('产品中心', 'Products')); ?></a>
      <a href="<?php echo esc_url(vasture_page_url('factory')); ?>" class="<?php echo vasture_nav_is_current('factory') ? 'is-current' : ''; ?>"<?php echo vasture_nav_current_attribute('factory'); ?>><?php echo esc_html(vasture_t('供应链能力', 'Supply Chain')); ?></a>
      <a href="<?php echo esc_url(vasture_page_url('services')); ?>" class="<?php echo vasture_nav_is_current('services') ? 'is-current' : ''; ?>"<?php echo vasture_nav_current_attribute('services'); ?>>OEM/ODM</a>
      <a href="<?php echo esc_url(vasture_page_url('blog')); ?>" class="<?php echo vasture_nav_is_current('blog') ? 'is-current' : ''; ?>"<?php echo vasture_nav_current_attribute('blog'); ?>><?php echo esc_html(vasture_t('行业资讯', 'Insights')); ?></a>
      <a href="<?php echo esc_url(vasture_page_url('resources')); ?>" class="<?php echo vasture_nav_is_current('resources') ? 'is-current' : ''; ?>"<?php echo vasture_nav_current_attribute('resources'); ?>><?php echo esc_html(vasture_t('采购资料', 'Resources')); ?></a>
    </nav>
    <div class="vasture-lang-switch" role="group" aria-label="Language"><a class="lang-btn <?php echo !vasture_is_en() ? 'is-active' : ''; ?>" lang="zh-CN" hreflang="zh-CN" href="<?php echo esc_url(vasture_language_switch_url('zh')); ?>">中文</a><span aria-hidden="true">|</span><a class="lang-btn <?php echo vasture_is_en() ? 'is-active' : ''; ?>" lang="en" hreflang="en" href="<?php echo esc_url(vasture_language_switch_url('en')); ?>">EN</a></div>
    <details class="vasture-mobile-nav">
      <summary aria-label="<?php echo esc_attr(vasture_t('打开主导航', 'Open main navigation')); ?>"><?php echo esc_html(vasture_t('菜单', 'Menu')); ?></summary>
      <div class="vasture-mobile-nav__panel">
        <a href="<?php echo esc_url(vasture_page_url('index')); ?>"<?php echo vasture_nav_current_attribute('index'); ?>><?php echo esc_html(vasture_t('首页', 'Home')); ?></a>
        <a href="<?php echo esc_url(vasture_page_url('products')); ?>"<?php echo vasture_nav_current_attribute('products'); ?>><?php echo esc_html(vasture_t('产品中心', 'Products')); ?></a>
        <a href="<?php echo esc_url(vasture_page_url('factory')); ?>"<?php echo vasture_nav_current_attribute('factory'); ?>><?php echo esc_html(vasture_t('供应链能力', 'Supply Chain')); ?></a>
        <a href="<?php echo esc_url(vasture_page_url('services')); ?>"<?php echo vasture_nav_current_attribute('services'); ?>>OEM/ODM</a>
        <a href="<?php echo esc_url(vasture_page_url('blog')); ?>"<?php echo vasture_nav_current_attribute('blog'); ?>><?php echo esc_html(vasture_t('行业资讯', 'Insights')); ?></a>
        <a href="<?php echo esc_url(vasture_page_url('resources')); ?>"<?php echo vasture_nav_current_attribute('resources'); ?>><?php echo esc_html(vasture_t('采购资料', 'Resources')); ?></a>
      </div>
    </details>
    <div class="header-actions"><a href="<?php echo esc_url(vasture_page_url('contact')); ?>" class="cf-btn cf-btn-primary"><?php echo esc_html(vasture_t('获取报价', 'Request a Quote')); ?> <span aria-hidden="true">→</span></a></div>
  </div>
</header>
<main id="main-content" role="main" tabindex="-1">
<?php vasture_breadcrumbs(); ?>
