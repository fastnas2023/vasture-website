# VASTURE 华盛智造官网 - 项目会话上下文

> 用于在另一台电脑上恢复任务上下文。最后更新：2026-08-12

## 项目概述

基于用户上传的设计稿（7个HTML页面），搭建完整的可运行前端项目。要求保持与设计稿一致的视觉效果，补充页面交互和多端适配。

## 技术栈

- 纯 HTML / CSS / JavaScript（无构建工具）
- Tailwind CSS v4.3.1（设计稿原用）
- Lucide 图标库
- 共享 CSS：`css/brand.css`（品牌色系统 + 组件 + 响应式）
- 共享 JS：`js/main.js`（12个交互模块）

## GitHub 仓库

- 地址：https://github.com/fastnas2023/vasture-website
- 可见性：Private
- 账号：fastnas2023
- 分支：main

## 文件结构

```
vasture-website/
├── .gitignore
├── css/
│   └── brand.css          # 共享样式（34KB）品牌色变量+组件+响应式
├── js/
│   └── main.js            # 共享交互（12KB）12个功能模块
├── assets/                # 15张图片
│   ├── image_0_yi19x4.jpg   # 女装/连衣裙
│   ├── image_1_yi19x4.jpg   # 男装/Polo
│   ├── image_2_yi19x4.jpg   # 童装
│   ├── image_3_yi19x4.jpg   # 运动/功能性运动服
│   ├── image_4_yi19x4.jpg   # 针织/经典T恤
│   ├── image_5_yi19x4.jpg   # 外套/飞行夹克
│   ├── image_6_yi19x4.jpg   # Hero背景图
│   ├── image_7_yi19x4.jpg   # Oversized卫衣
│   ├── image_8_yi19x4.jpg   # 运动裤
│   ├── image_9_yi19x4.jpg   # 工厂介绍
│   ├── image_10_yi19x4.jpg  # 厂区展示1
│   ├── image_11_yi19x4.jpg  # 厂区展示2
│   ├── image_12_yi19x4.jpg  # 厂区展示3
│   ├── image_13_yi19x4.jpg  # 新闻头图/设计师案例
│   └── image_14_yi19x4.jpg  # 地图
├── index.html             # 首页：Hero+数据+产品品类+工厂优势+CTA
├── products.html          # 产品中心：筛选侧栏+8产品卡片+排序
├── factory.html           # 工厂实力：介绍+6步流程+质量体系+设备+证书
├── services.html          # 定制服务：OEM/ODM+8步流程+能力+案例
├── blog.html              # 新闻资讯：分类Tab+精选文章+网格+分页
├── resources.html         # 资源下载：分类Tab+搜索+8资源卡片+申请表单
└── contact.html           # 联系询价：联系信息+询价表单+地图
```

## 设计稿来源

原始设计稿压缩包路径（本机）：
`c:\Users\Administrator\.trae-cn\attachments\6a7b39e14cd17a14397e0930\64f77b2f-d154-4423-a6b3-6bd8ccbdd1c4_9d3a05a2-c170-4ed9-8c5d-93234cbb03cb_首页 等 7 个设计.zip`

解压后路径（本机）：
`c:\Users\Administrator\.trae-cn\attachments\6a7b39e14cd17a14397e0930\design_files\pages\`

## 品牌色系统

```css
--cf-brand-50:  #E8F0F5;
--cf-brand-100: #C8DBE6;
--cf-brand-200: #9CBFD2;
--cf-brand-300: #7A9CB5;
--cf-brand-400: #5B7F99;
--cf-brand-500: #40647E;
--cf-brand-600: #2D4D66;
--cf-brand-700: #143D66;
--cf-brand-800: #0F2E4F;
--cf-brand-900: #091F38;
```

## 已实现的交互功能（main.js 12个模块）

1. **Header滚动状态** - 滚动时添加scrolled类
2. **导航高亮** - 根据当前页面URL自动高亮菜单项（data-dom-id匹配）
3. **移动端抽屉** - 右侧滑出菜单，ESC/遮罩点击关闭
4. **主题切换** - 明/暗模式，localStorage持久化
5. **语言切换** - 中/EN视觉切换
6. **滚动显现** - IntersectionObserver动画
7. **平滑锚点** - 固定Header偏移
8. **表单交互** - 必填校验+文件上传预览+提交状态+Toast提示
9. **Toast通知** - success/error/info三种类型
10. **产品筛选排序** - 复选框多维度筛选+MOQ排序+重置
11. **Tab切换** - data-tabs属性结构
12. **全局API** - window.VASTURE.showToast

## 响应式断点

- 1100px - 平板适配
- 900px - 移动端导航抽屉激活
- 768px - 网格列数减少
- 560px - 单列布局

## 页面导航映射

| 页面文件 | data-dom-id | 导航标签 |
|----------|-------------|----------|
| index.html | nav-home | 首页 |
| products.html | nav-products | 产品中心 |
| factory.html | nav-factory | 工厂实力 |
| services.html | nav-services | 服务方案 |
| blog.html | nav-blog | 行业资讯 |
| resources.html | nav-resources | 资源中心 |
| contact.html | nav-contact | 联系我们 |

## 本地预览

```bash
cd vasture-website
python -m http.server 8080
# 浏览器打开 http://localhost:8080/index.html
```

## 验证状态

- 7个页面全部通过浏览器验证，无控制台错误
- CSS/JS/图片资源均正常加载
- 移动端响应式正常
- Git提交：`fd8dd45` - feat: init VASTURE website with 7 pages

## 已完成任务清单

- [x] 读取所有7个设计稿页面，了解完整结构
- [x] 创建项目目录结构和资源复制
- [x] 提取共享CSS样式到brand.css
- [x] 创建共享JS文件main.js（12个交互模块）
- [x] 创建首页 index.html
- [x] 创建产品中心 products.html
- [x] 创建工厂实力 factory.html
- [x] 创建定制服务 services.html
- [x] 创建新闻资讯 blog.html
- [x] 创建资源下载 resources.html
- [x] 创建联系询价 contact.html
- [x] 验证所有文件完整性并启动本地服务器预览
- [x] 上传到 GitHub 私有仓库

## 可能的后续优化方向

- [ ] 接入真实后端API（表单提交、产品数据）
- [ ] 添加更多产品详情页
- [ ] SEO优化（meta标签、结构化数据）
- [ ] 性能优化（图片懒加载、WebP转换）
- [ ] 国际化（i18n）完整实现
- [ ] 添加页面加载动画
- [ ] 表单后端对接（邮件通知、CRM集成）
