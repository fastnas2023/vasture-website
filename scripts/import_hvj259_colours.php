<?php
require $argv[1];
require_once ABSPATH.'wp-admin/includes/image.php';
$root=dirname(__DIR__);
$items=json_decode(file_get_contents($root.'/assets/catalogue-a4/hvj259-colours-v3/manifest.json'),true);
$posts=get_posts(['post_type'=>'vasture_product','meta_key'=>'_vasture_product_id','meta_value'=>'hvj259-reflective-border-tabard','posts_per_page'=>1]);
if(count($items)!==15 || !$posts) throw new RuntimeException('Missing product or colour manifest');
$id=$posts[0]->ID;
$old=get_post_meta($id,'_vasture_color_variants',true);
if(!get_post_meta($id,'_vasture_hvj259_before_v3',true)) update_post_meta($id,'_vasture_hvj259_before_v3',['variants'=>$old,'gallery'=>get_post_meta($id,'_vasture_gallery_ids',true),'detail'=>get_post_meta($id,'_vasture_detail_ids',true),'thumbnail'=>get_post_thumbnail_id($id)]);
$variants=[];$ids=[];
foreach($items as $item){
 $found=get_posts(['post_type'=>'attachment','post_status'=>'inherit','meta_key'=>'_vasture_source_path','meta_value'=>$item['source'],'fields'=>'ids','posts_per_page'=>1]);
 if($found){$aid=$found[0];}else{
 $up=wp_upload_dir();$dest=$up['path'].'/'.wp_unique_filename($up['path'],basename($item['source']));
 if(!copy($root.'/'.$item['source'],$dest)) throw new RuntimeException('Copy failed');
 $aid=wp_insert_attachment(['post_mime_type'=>'image/webp','post_title'=>'HVJ259 '.$item['label_en'],'post_status'=>'inherit'],$dest,$id,true);
 if(is_wp_error($aid)) throw new RuntimeException($aid->get_error_message());
 wp_update_attachment_metadata($aid,wp_generate_attachment_metadata($aid,$dest));
 update_post_meta($aid,'_vasture_source_path',$item['source']);
 update_post_meta($aid,'_wp_attachment_image_alt','HVJ259 '.$item['label_en']);
 }
 $variants[]=['label_zh'=>$item['label_zh'],'label_en'=>$item['label_en'],'attachment_id'=>$aid,'source'=>$item['source']];$ids[]=$aid;
}
set_post_thumbnail($id,$ids[0]);
update_post_meta($id,'_vasture_color_variants',$variants);
update_post_meta($id,'_vasture_gallery_ids',$ids);
update_post_meta($id,'_vasture_detail_ids',[]);
update_post_meta($id,'_vasture_colour_image_method','HD master colour illustrations; catalogue colour reference; 2026-09-12');
clean_post_cache($id);
echo json_encode(['post'=>$id,'colours'=>count($variants),'attachments'=>$ids]).PHP_EOL;
