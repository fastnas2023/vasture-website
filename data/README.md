# 产品数据维护与后台导入

`products.json` 是后续开发产品后台时的标准导入数据，`product.schema.json` 是字段约束，`product-catalogues.json` 记录画册来源。

## 图片地址

- `main_image` 和 `gallery_images` 保存仓库内的相对路径。
- `main_image` 只放单件产品、主体清楚的主视觉，不能使用正反面拼图、功能说明页或多色组合图。
- `gallery_images` 保留原画册页面裁图、背面、细节和配色资料，供后续产品详情页与后台维护使用。
- 当前 `assets/modish/main/` 图片依据画册产品外观重建为整洁展示图，不等同于实物摄影或现货证明。
- 需要远程地址时，将 `asset_base_url` 与图片相对路径拼接。
- 后台导入时应下载图片并上传到后台媒体库，不应长期依赖 GitHub Pages 外链。

## 导入键

- `id` 是稳定且唯一的产品导入键，后续更新产品时不要修改。
- `sku` 只在画册明确给出型号时填写，不猜测型号。
- `catalogue_id` + `source_pages` + `added_date` 用于追溯画册和录入时间。
- 当前产品均必须使用 `source_status=catalogue_linked` 并填写真实画册来源，不应伪造型号或页码。

## 后台建议字段

Strapi 或其他 CMS 可按如下类型建立字段：

- 单行文本：`id`、`sku`、`name_zh`、`name_en`、`product_type`、`badge`、`moq_label`、`moq_value`、`catalogue_id`、`catalogue_name`、`source_file`。
- 多行文本：`description_zh`。
- JSON/多选：`tags`、`source_pages`。
- 媒体：`main_image`、`gallery_images`。
- 日期：`added_date`。
- 枚举：`supply_mode`、`stock_status`、`source_status`、`visibility`。
- 整数：`sort_order`。

每次新增产品时，先更新 `products.json` 并通过 Schema 校验，再同步网页产品卡或执行后台导入。
