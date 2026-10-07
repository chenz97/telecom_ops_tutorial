# 增加个人阅读标注

## Purpose / Big Picture

读者在离线教程 index.html 中选中文字后，可以划线、强调并记下理解或问题；刷新后继续使用自己的标注，也可以从“我的标注”回到相应原文。本文按 /Users/zeno/.codex/PLANS.md 维护。

## Progress

- [x] 2026-10-02：检查现有阅读器，补充阅读标注需求与交互边界。
- [x] 实现选区工具条、分层标注渲染和本地保存。
- [x] 实现注释编辑、标注列表、定位与导出导入，以及打印注释。
- [x] 完成新增行为测试、原阅读器回归与桌面手机截图核查。
- [x] 进行独立读者审阅，同步维护文档并生成分享包。

## Context and Orientation

项目是本地可直接打开的静态教程。scripts/build.py 从 course/tutorial.md 生成 index.html，assets/app.js 管理搜索、进度与字号，assets/style.css 管理阅读布局。新增 assets/annotations.js 管理个人标注，生成模板添加工具条和对话框，scripts/package.py 将新脚本打入分享包。正文继续作为原文来源，个人标注只影响浏览器中的阅读展示。

## Plan of Work

首先在生成模板中添加选区操作和“我的标注”入口，使用浏览器 Selection 与 Range 获取同一章节内的选区。将标注保存为章节标识、文本起止位置、摘录和上下文，按文本节点分段渲染，支持跨原有内联元素及重叠类型。随后添加注释编辑和统一列表，处理跳转、删除、导入导出与持久化异常。最后验证原阅读功能与新增行为，并更新阅读说明与分享包。

## Milestones

第一阶段完成后，鼠标或键盘选择正文可划线与强调，刷新后正确恢复，原有链接与答案仍可用。第二阶段完成后，读者可编辑注释、管理所有标注、导出导入并打印个人注释；模糊定位和存储异常有明确反馈。第三阶段完成后，桌面与手机工具条及对话框可操作，自动化检查和读者审阅通过，压缩包包含完整离线资源。

## Concrete Steps

在 /Users/zeno/projects/telecom_ops_tutorial 维护 scripts/build.py、assets/annotations.js 和 assets/style.css。运行 python3 scripts/build.py、python3 scripts/check.py 与 node --check assets/annotations.js。新增 scripts/annotation_check.py 用 Playwright 验证选区、重叠、持久化、编辑、导入导出和移动布局；继续运行 python3 scripts/browser_check.py 回归阅读器。执行 python3 scripts/package.py，核对包内资源与工作区一致。

## Validation and Acceptance

关键行为是跨加粗与链接的标注不会改变原文，重叠样式可独立删除，注释包含任意纯文本时正确显示。刷新后位置与记录一致，前文插入后摘录可重新定位，重复文本无法唯一识别时保留为待定位。取消编辑保留原注释，错误导入保留现有数据，存储失败仍可导出。测试真实拖选和键盘选择，并核查手机工具条、对话框以及打印展示。

## Idempotence and Recovery

构建与打包可重复执行。标注保存在独立的 telecom-course-annotations-v1 键中，清除学习进度保持标注。导入采用验证后合并，导出保存当前有效记录。无法定位的标注不会被删除或贴到猜测的位置。

## Surprises & Discoveries

原阅读器不修改正文 DOM，只保存章节进度。直接包裹选区会破坏跨段落或跨原有元素的结构，因此将每个文本节点按区间拆分，原有元素保持完整。DOM 指浏览器中的页面节点结构。

## Decision Log

2026-10-02：使用原生 Selection、Range 和文本节点操作。当前单一静态课程的交互可用这些接口实现，能够继续离线运行并保持依赖简单。接口核对见 [MDN Selection](https://developer.mozilla.org/en-US/docs/Web/API/Selection) 与 [Range](https://developer.mozilla.org/en-US/docs/Web/API/Range) 文档；位置恢复借鉴 [W3C Web Annotation](https://www.w3.org/TR/annotation-model/#text-quote-selector) 的文本位置与摘录上下文模型。

2026-10-02：强调采用背景加适当字重，下划线采用独立样式，注释采用虚线提示与单独编辑。三种标注可叠加，并在列表中独立管理。

## Outcomes & Retrospective

状态：已完成，作为历史实施记录保留。选区工具条、三种可重叠标注、注释编辑、列表定位和删除均已交付。个人标注独立持久化，并支持导出、合并导入与打印附录。

2026-10-02 验证结果：scripts/check.py 检查通过，JavaScript 语法检查通过，scripts/annotation_check.py 完成 18 项检查，原有 scripts/browser_check.py 完成 17 项回归检查。浏览器未报告脚本错误。新增检查覆盖真实鼠标拖选、键盘与触屏点击，包含跨段落、加粗、链接、表格和 emoji 的选区；验证编辑与取消、重叠删除、刷新恢复、搜索与答案定位，并验证错误导入、重复导入及旧备份保留已编辑注释。前文插入后的恢复、歧义位置保留和存储不可用时导出也已通过。

独立读者完成审阅与复核，确认界面和说明自洽。审阅提出的重复导入旧注释、阅读深处错误反馈两项问题均已解决，并加入相应行为检查。桌面、手机与打印截图已核查。维护说明已同步到 README，以及 overview、requirements、architecture、design 和 planning。

构建和打包重新执行，分享包包含六个文件，资源逐文件核对一致。

## Interfaces and Dependencies

annotations.js 仅依赖原生浏览器接口，并通过现有搜索控件恢复被隐藏的章节。存储格式采用版本化 JSON，用户输入使用 textContent。新增脚本在 app.js 后加载，延续当前的 file:// 离线入口。浏览器验证使用现有 Playwright。

## Artifacts and Notes

交付入口保持 index.html，个人标注导出为 JSON。技术与维护说明保存在 docs，界面提供选择、保存和错误等实际反馈。

## Revision Notes

2026-10-02：建立标注功能执行记录并同步需求；实现、审阅与验证完成后同步稳定设计，并将本文标记为已完成。

验证证据：docs/execution/qa/annotation-results.json 记录 18 项检查；results.json 记录 17 项回归。annotation-selection.png 与 annotation-selection-mobile.png 展示选区工具条，annotation-library-desktop.png 与 annotation-library-mobile.png 展示标注管理，annotation-editor-mobile.png 展示注释编辑，annotation-print.png 展示打印附录。安全输入专项截图保存在 annotation-library-safe-text.png。
