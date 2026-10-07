# 系统组织

course/tutorial.md 是教材正文的来源。scripts/build.py 将正文按二级标题切分为章节，并使用 Markdown 解析器转换为 HTML。根目录 index.html 是阅读入口，通过相对路径加载 assets/style.css、assets/app.js 和 assets/annotations.js。正文与页面保持同源，页面内容由构建脚本生成。

assets/style.css 管理桌面、移动与打印布局。assets/app.js 管理章节搜索、目录位置、学习进度和阅读字号；正文内容不依赖脚本。assets/annotations.js 独立管理选区与点击标注共用的工具条、标注渲染和底部注释面板，同时管理注释编辑与个人标注列表，并处理本地保存、JSON 导入导出与打印注释。

scripts/check.py 检查章节顺序、内部链接与本地资源，并核对学习目标、答案块和表格结构。scripts/browser_check.py 使用 Playwright 验证离线阅读器，把截图和结构化结果保存到 docs/execution/qa。scripts/annotation_check.py 验证标注选区、重叠、持久化、编辑与文件操作，证据也保存在同一目录；摘录歧义场景使用独立测试文本，避免依赖教材措辞。

本项目没有后端服务，也没有外部资源加载。外部链接仅在读者打开参考资料时访问。浏览器本地存储保存学习状态、字号偏好与个人标注，三者使用独立存储键。

scripts/package.py 在生成和结构检查后创建 dist/telecom-network-operations-course.zip，其中包含阅读说明、HTML、本地样式、本地脚本和 Markdown 正文。requirements.txt 保存构建与验证依赖。

docs/execution/tutorial-emphasis.md 记录主教材重点层级的修订、独立阅读审阅及交付验证。此前的表达修订保存在 tutorial-expression.md，初版建设、技术扩展和叙述重组的历史分别保存在 tutorial.md、tutorial-depth.md 和 tutorial-coherence.md。tutorial-optimization.md 保留曾经开展的版本扩展工作记录；个人标注的建设与交互记录保存在同一执行目录。
