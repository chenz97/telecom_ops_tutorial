# 突出教程的核心机制与判断规则

状态：已完成。本文保留修订、审阅和验证记录；长期约定维护在 docs/design.md 与 docs/requirements.md。

## Purpose / Big Picture


本轮修订让具有计算机背景、缺少通信知识的读者能够在阅读和回查时迅速辨认决定运维判断的核心概念，并沿其后的原理、算例和案例理解依据。交付正文为 course/tutorial.md，网页由 scripts/build.py 生成到 index.html。保留 00—23 章、既有学习目标、38 组练习及阅读和标注功能。本文依据 /Users/zeno/.codex/PLANS.md 维护。


## Progress


- [x] 2026-10-06：读取写作规范、项目长期文档和生成机制，确认正文已有解释深度，但强调集中于术语，重要判断缺少层级。
- [x] 2026-10-06：启动独立教材审阅；建立本执行记录，并保存修改前正文、生成器和样式副本。
- [x] 2026-10-06：通读全部正文，完成核心机制与规则强调；42 个独立结论均有相邻机制、实例或数值依据。
- [x] 2026-10-06：完成网页重点样式与同源生成，结构检查通过；同步 design、requirements、architecture 和 planning。
- [x] 2026-10-06：完成 17 项阅读器检查和 31 项标注检查；核查桌面 PPPoE、手机突发分析与打印时延截图，重点与解释的层级清晰。
- [x] 2026-10-06：新的独立读者逐章审读最终教材并核对 HTML，确认能够交付，没有必须修订的问题。
- [x] 2026-10-06：同步最终维护状态，生成分享包并完成归档与六项文件一致性核对。


## Context and Orientation


这是离线静态教程。course/tutorial.md 是完整正文，scripts/build.py 用 markdown-it-py 将章节、表格及原生 details 答案块转为 index.html。assets/style.css 负责桌面、手机和打印呈现；assets/app.js 与 assets/annotations.js 负责搜索、进度和个人标注。scripts/check.py 验证内容结构与本地资源，scripts/browser_check.py 验证阅读交互及版面，scripts/annotation_check.py 验证标注。scripts/package.py 生成 dist/telecom-network-operations-course.zip。项目目录没有 Git 仓库，修改前文件保存在 /private/tmp/telecom-emphasis-before/。


## Plan of Work


先通读正文，辨认各章用于解释现象或决定行动的主导机制，再将关键句从密集叙述中独立呈现，保留紧随其后的原因、后果和具体例子。术语首次定义继续加粗，辅助条件和例子保持正常字重。根据各章内容使用独立结论段或段内重点，避免每段同等强调，也避免重复章前章后摘要。

网页使用正文已有的 Markdown 加粗语义呈现层级。如需增加独立结论段样式，在 scripts/build.py 与 assets/style.css 中集中实现，兼顾窄屏和打印，并保持文字内容与标注定位的一致性。每阶段完成后检查 docs/overview.md、docs/architecture.md、docs/planning.md 与 docs/design.md，稳定教学约定同步到 design，当前进度同步 planning，只有系统组织改变时才更新 architecture。

最后交由独立子代理只读教材，诚实评价是否能识别核心思想、解释其原因并用于判断；发现断层后修订，再完成生成、检查和打包。


## Milestones


正文阶段完成后，读者扫读即可指出每章最重要的机制或判断规则，细读后能够从公式与场景解释该规则。网页阶段完成后，普通术语与独立结论在桌面、手机及打印中层级清晰。交付阶段完成后，全文独立审阅通过，页面与 Markdown 同源，搜索、学习进度和标注正常，分享包与工作区一致。


## Concrete Steps


在 /Users/zeno/projects/telecom_ops_tutorial 修订 course/tutorial.md，必要时调整 scripts/build.py 与 assets/style.css。执行 python3 scripts/build.py 与 python3 scripts/check.py；预期 24 章、38 组练习、30 项资料，内部链接与资源完整。再执行 python3 scripts/browser_check.py 和 python3 scripts/annotation_check.py，检查相应截图。执行 python3 scripts/package.py，并以 Python zipfile 检查归档完整性和六项交付文件逐字节一致性。


## Validation and Acceptance


内容检查以读者能否辨认主次、说明机制、解释数值后果和选择行动为依据。每条独立结论必须在相邻正文中获得因果解释或具体实例，避免无依据的口号。全文复读确认术语、案例和练习一致，没有修订说明和对话痕迹。技术检查确认稳定章节身份、答案展开、搜索、进度、无脚本阅读及多种宽度无整页水平溢出。浏览器截图确认独立结论不压过标题、不挤压正文，打印时字重和层级仍清晰。正文修改需完成标注重定位、重叠和导入导出检查。


## Idempotence and Recovery


生成与打包可重复执行。修改前副本用于对比，按需恢复单个文件。个人标注存储键及记录结构保持现有约定。


## Surprises & Discoveries


当前教材的技术解释与数值案例已有相当深度，重点问题主要发生在呈现层级：术语得到加粗，承担方案判断的完整结论仍常与普通说明同等呈现。

CommonMark 对紧邻中文正文、末尾为句号的加粗片段有定界符限制，段内强调将句末标点放在定界符外，独立结论保留完整句子。结构检查已确认生成页面没有未渲染的 Markdown 标记。

本机 Chromium 在沙箱内启动时报告 MachPortRendezvous 权限拒绝；本地浏览器验证获自动审批后在沙箱外执行，阅读器与标注检查均通过。


## Decision Log


2026-10-06：以既有正文为基础选择核心结论，并让强调对应解释价值。原因是重复摘要或全面加粗会增加阅读负担，削弱重点与支撑细节的区别。

2026-10-06：保留章节编号及同源生成方式。原因是已有导航、学习进度与标注依赖稳定章节身份，网页应持续准确反映正文。

2026-10-06：纯文字独立加粗段落生成 key-point 样式，保持普通段落及 strong 语义，不增加 JavaScript。原因是同一正文可直接用于 Markdown、网页和打印，个人标注能够继续读取相同文本。

2026-10-06：按初步独立审阅补齐回退执行与验证的分项时间，明确医院及数据中心业务网关承担主备出口选择和探测。原因是计算应逐项对应公式，案例中的路径选择必须有明确执行对象。


## Outcomes & Retrospective


正文、网页及分享包已完成交付，正文 76,285 字符，保留 24 章、四个案例、38 组练习和 30 项资料。42 个独立结论逐项渲染，全部加粗文字约占源稿字符数的 5.5%，其余段落与例子承担解释和推理。独立审阅确认重点能够被识别且有机制支持，没有重复摘要、计算矛盾或编辑痕迹。

初步审阅指出原稿的术语比行动规则更醒目，并发现回退时间合计与公式分项、主备出口选择对象两处细节缺口。修订后使用新的无对话历史子代理，只读取最终教材与生成页面。该读者覆盖 00—23 章并核对逐章正文一致，明确认为可以交付；能够复述分阶段验证、测量条件、容量时间尺度、备用保障及实际结果驱动状态五项规则。对增加缓存、既有与新建会话差异、单故障容量不足和 RTO/RPO 分别验收四种条件变化，推理与教材吻合。两项可选建议是增加医院路径图和细化表格区域名称；现有路径表及表头已支持理解，不属于本轮交付缺口。

结构检查确认 91 个唯一标识，章节、内部链接与本地资源完整。阅读器的 17 项检查与标注的 31 项检查均通过，没有 JavaScript 错误，四种宽度无整页水平溢出；标注检查覆盖跨段加粗、重定位、重叠及导入导出。桌面 PPPoE、手机突发分析和打印时延截图已核查，重点段完整换行且与公式、学习目标和普通解释层级分明。分享包归档完整、六项内容与工作区逐字节一致，无剩余交付工作。


## Artifacts and Notes


主要交付为 course/tutorial.md、index.html 和同步的教程分享包；本文件记录具体实施和验证。长期教学约定维护在 docs/design.md，当前交付状态维护在 docs/planning.md。

浏览器证据保存在 docs/execution/qa/results.json 和 annotation-results.json；视觉核查使用 desktop-pppoe.png、mobile-queue-analysis.png 和 print-delay-analysis.png。分享包为 dist/telecom-network-operations-course.zip。

最终 SHA-256：course/tutorial.md 为 47bd5fe06846a3a75d482e748cb70874afa056084fec171ed47cdb57b6c3f494；index.html 为 481749bc9ab12047fd7dd80c04d322771ee1dd360318625d2a44f5b2549c0b92；分享包为 91fdbbe6ed6904297e028bcc85b7c66b1baa8f1018988ac7922cf1fb4b2e4b28。


## Interfaces and Dependencies


沿用 Markdown 加粗、原生 HTML 答案块和既有本地样式，不引入运行依赖。浏览器验证依赖 requirements.txt 中的 Playwright；受沙箱限制的本机 Chromium 启动按实际错误处理。


## Revision Notes


2026-10-06：建立执行记录，明确重点选择、解释依据、网页层级与独立审读的验收方法。已检查 overview、architecture、planning 与 design；目标、范围及架构当前准确，正文层级约定与最终状态在相应阶段同步。

2026-10-06：正文阶段完成后复核长期文档。overview 的目标及范围仍准确；design 与 requirements 补入重点层级和相邻解释约定，architecture 更新当前执行记录入口，planning 记录本轮进度和已完成的结构验证。

2026-10-06：页面验证阶段完成后复核长期文档，design 的桌面、手机及打印约定与实际截图一致，系统结构与项目目标保持原有范围，planning 将在独立审阅和分享包验证完成后记录最终状态。README 的维护入口已指向本执行记录。

2026-10-06：交付前再次检查 overview、architecture、planning、design、requirements 和本执行记录。overview 的读者、范围和目的仍准确；architecture 的维护入口与现有生成流程一致，design 与 requirements 已保存稳定重点约定，planning 已记录完整交付状态，本执行记录标记完成。最终审读、浏览器检查与分享包核对的结果同步到本文。
