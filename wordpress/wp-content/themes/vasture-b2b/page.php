<?php
get_header();
$source = get_post_meta(get_the_ID(), '_vasture_source_template', true);
if (vasture_is_en() && $source && ($english_page = vasture_english_static_page((string) get_post_field('post_name', get_the_ID())))) {
    echo $english_page; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
} elseif ($source) {
    echo vasture_source_main((string) $source); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped
} else {
    while (have_posts()) { the_post(); ?>
      <section class="cf-container" style="padding:72px 0"><h1><?php the_title(); ?></h1><div class="entry-content"><?php the_content(); ?></div></section>
    <?php }
}
get_footer();
