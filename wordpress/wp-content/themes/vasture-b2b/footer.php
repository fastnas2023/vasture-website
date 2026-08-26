<?php if (!defined('ABSPATH')) { exit; } ?>
</main>
<footer class="site-footer">
  <div class="cf-container">
    <div class="footer-top">
      <div class="footer-main">
        <a href="<?php echo esc_url(vasture_page_url('index')); ?>" class="logo-link"><span class="logo-link__text"><strong><?php echo esc_html(vasture_t('卓圣轩服贸', 'ZSX Garment')); ?></strong><small><?php echo esc_html(vasture_t('扬州卓圣轩服装贸易有限公司', 'Yangzhou ZSX Garment Trading Co., Ltd.')); ?></small></span></a>
        <p><?php echo esc_html(vasture_t('面向海外品牌、批发商与项目采购，提供工作服现货、OEM贴牌与ODM开发沟通。', 'For brands, distributors and project buyers: ready-stock workwear, OEM private label and ODM development support.')); ?></p>
        <p><a href="mailto:allen@zsxgarment.com">allen@zsxgarment.com</a></p>
        <div class="footer-whatsapp">
          <span><?php echo vasture_social_icon_svg('whatsapp'); ?></span>
          <div>
            <a href="<?php echo esc_url(vasture_whatsapp_url('8617826699113')); ?>" target="_blank" rel="noopener noreferrer"><?php echo esc_html(vasture_t('周翔 · WhatsApp', 'Zhou Xiang · WhatsApp')); ?> +86 178 2669 9113</a>
          </div>
        </div>
        <div class="footer-social" aria-label="<?php echo esc_attr(vasture_t('社交媒体', 'Social media')); ?>">
          <span><?php echo esc_html(vasture_t('关注我们', 'Follow us')); ?></span>
          <div class="social-icons">
            <?php foreach (vasture_social_profiles() as $platform => $profile) : ?>
              <?php if ($profile['url'] !== '') : ?>
                <a class="social-icon" href="<?php echo esc_url($profile['url']); ?>" target="_blank" rel="noopener noreferrer" aria-label="<?php echo esc_attr($profile['label'] . ' · ' . vasture_t('新窗口打开', 'opens in a new window')); ?>" title="<?php echo esc_attr($profile['label']); ?>"><?php echo vasture_social_icon_svg($platform); ?></a>
              <?php else : ?>
                <span class="social-icon social-icon--placeholder" aria-label="<?php echo esc_attr($profile['label'] . ' · ' . vasture_t('链接待添加', 'link pending')); ?>" title="<?php echo esc_attr($profile['label'] . ' · ' . vasture_t('链接待添加', 'link pending')); ?>"><?php echo vasture_social_icon_svg($platform); ?></span>
              <?php endif; ?>
            <?php endforeach; ?>
          </div>
        </div>
      </div>
      <nav class="footer-links" aria-label="<?php echo esc_attr(vasture_t('页尾快捷导航', 'Footer quick links')); ?>">
        <span><?php echo esc_html(vasture_t('快捷入口', 'Quick Links')); ?></span>
        <a href="<?php echo esc_url(vasture_page_url('products')); ?>"><?php echo esc_html(vasture_t('产品中心', 'Products')); ?></a>
        <a href="<?php echo esc_url(vasture_page_url('services')); ?>">OEM/ODM</a>
        <a href="<?php echo esc_url(vasture_page_url('factory')); ?>"><?php echo esc_html(vasture_t('供应链能力', 'Supply Chain')); ?></a>
        <a href="<?php echo esc_url(vasture_page_url('resources')); ?>"><?php echo esc_html(vasture_t('采购资料', 'Resources')); ?></a>
        <a href="<?php echo esc_url(vasture_page_url('certifications')); ?>"><?php echo esc_html(vasture_t('证书与认证', 'Certifications')); ?></a>
        <a href="<?php echo esc_url(vasture_page_url('contact')); ?>"><?php echo esc_html(vasture_t('联系询价', 'Contact for Inquiry')); ?></a>
      </nav>
    </div>
    <div class="footer-bottom"><span>© <?php echo esc_html(wp_date('Y')); ?> <?php echo esc_html(vasture_t('卓圣轩服贸', 'ZSX Garment')); ?></span><a href="<?php echo esc_url(vasture_page_url('contact')); ?>"><?php echo esc_html(vasture_t('联系询价', 'Contact for Inquiry')); ?></a></div>
  </div>
</footer>
<details class="vasture-whatsapp-float">
  <summary aria-label="<?php echo esc_attr(vasture_t('打开 WhatsApp 联系方式', 'Open WhatsApp contacts')); ?>"><?php echo vasture_social_icon_svg('whatsapp'); ?><span>WhatsApp</span></summary>
  <div class="vasture-whatsapp-float__panel">
    <strong><?php echo esc_html(vasture_t('WhatsApp 咨询', 'WhatsApp inquiry')); ?></strong>
    <a href="<?php echo esc_url(vasture_whatsapp_url('8617826699113')); ?>" target="_blank" rel="noopener noreferrer"><span><?php echo esc_html(vasture_t('周翔', 'Zhou Xiang')); ?></span><b>+86 178 2669 9113</b></a>
  </div>
</details>
<?php wp_footer(); ?>
</body>
</html>
