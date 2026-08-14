# 产品图册维护说明

本目录保存用于产品录入和追溯的原始 PDF 画册。

新增画册时：

1. 将 PDF 放入本目录，文件名使用稳定的小写英文名。
2. 在 `data/product-catalogues.json` 登记画册 ID、画册名、添加日期、文件路径及产品来源页码。
3. 由画册新增的产品卡必须保留 `data-catalogue-id`、`data-catalogue-name`、`data-added-date` 和 `data-source-pages` 属性。
4. 这些属性不在前台显示，仅供后续维护、搜索和追溯使用。

未经供应链确认的现货、MOQ 或认证信息，不应从画册直接写入前台。
