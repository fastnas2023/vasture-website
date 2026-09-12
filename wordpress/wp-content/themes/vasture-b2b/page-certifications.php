<?php
if (!defined('ABSPATH')) { exit; }
get_header();
$is_en = vasture_is_en();
$certifications = vasture_certification_documents();
?>
<section class="vasture-page-header vasture-certifications-header"><div class="cf-container"><span class="vasture-certifications-header__eyebrow">COMPLIANCE DOCUMENTS</span><h1><?php echo esc_html(vasture_t('证书与认证', 'Certifications & Compliance')); ?></h1><p><?php echo esc_html(vasture_t('按证书编号、适用型号与标准核验高可视工作服文件。下单前请以具体产品型号和订单规格确认适用范围。', 'Verify high-visibility workwear documentation by certificate number, covered model and standard. Confirm the scope against the selected product and order specification before purchase.')); ?></p></div></section>
<?php vasture_breadcrumbs(); ?>
<section class="cf-container vasture-certifications">
  <div class="vasture-certifications__intro"><span><?php echo esc_html(vasture_t('文件核验', 'Document Verification')); ?></span><p><?php echo esc_html(vasture_t('证书文件用于采购与合规核验；仅附件中列明的型号在该证书范围内。', 'These documents support procurement and compliance review. Only models listed in the annex are within this certificate scope.')); ?></p></div>
  <div class="vasture-certifications__grid">
    <?php foreach ($certifications as $certificate) : ?>
      <article class="vasture-certificate-card">
        <div class="vasture-certificate-card__top"><span class="vasture-certificate-card__mark">CE</span><div><span class="vasture-certificate-card__eyebrow"><?php echo esc_html(vasture_t('EU 个人防护装备', 'EU Personal Protective Equipment')); ?></span><h2><?php echo esc_html($is_en ? ($certificate['name_en'] ?? '') : ($certificate['name_zh'] ?? '')); ?></h2></div></div>
        <dl class="vasture-certificate-card__facts"><div><dt><?php echo esc_html(vasture_t('证书编号', 'Certificate No.')); ?></dt><dd><?php echo esc_html($certificate['certificate_no'] ?? ''); ?></dd></div><div><dt><?php echo esc_html(vasture_t('签发机构', 'Issued by')); ?></dt><dd><?php echo esc_html($certificate['issuer'] ?? ''); ?></dd></div><div><dt><?php echo esc_html(vasture_t('适用产品', 'Product Scope')); ?></dt><dd><?php echo esc_html($certificate['product_scope'] ?? ''); ?></dd></div><div><dt><?php echo esc_html(vasture_t('有效至', 'Valid Until')); ?></dt><dd><?php echo esc_html($certificate['valid_until'] ?? ''); ?></dd></div></dl>
        <div class="vasture-certificate-card__scope"><span><?php echo esc_html(vasture_t('证书列明型号', 'Models Listed on Certificate')); ?></span><strong><?php echo esc_html(implode(', ', (array) ($certificate['models'] ?? []))); ?></strong></div>
        <div class="vasture-certificate-card__standards"><?php foreach ((array) ($certificate['standards'] ?? []) as $standard) : ?><span><?php echo esc_html($standard); ?></span><?php endforeach; ?></div>
        <div class="vasture-certificate-card__actions"><?php foreach ((array) ($certificate['files'] ?? []) as $file_index => $file) : ?><a class="<?php echo $file_index === 0 ? 'cf-btn cf-btn-primary' : 'vasture-certificate-card__secondary'; ?>" href="<?php echo esc_url(vasture_certification_file_url((string) ($file['file'] ?? ''))); ?>" target="_blank" rel="noopener noreferrer"><?php echo esc_html($is_en ? ($file['label_en'] ?? '') : ($file['label_zh'] ?? '')); ?> <span aria-hidden="true">↗</span></a><?php endforeach; ?></div>
      </article>
    <?php endforeach; ?>
  </div>
</section>
<?php get_footer();
