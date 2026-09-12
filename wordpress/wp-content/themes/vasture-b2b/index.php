<?php
get_header();
?><section class="cf-container" style="padding:72px 0"><h1>内容</h1><?php while (have_posts()) { the_post(); the_title('<h2>', '</h2>'); the_excerpt(); } ?></section><?php
get_footer();
