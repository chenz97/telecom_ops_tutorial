# 教程表达与教学内容修订

状态：已完成。本文保留本轮实施、审阅和验证记录；长期教学约定以 docs/requirements.md 与 docs/design.md 为准。


## Purpose / Big Picture


本轮修订面向具有计算机背景、缺少通信知识的读者。教材应帮助读者解释通信机制，并据测量结果作出开通、故障恢复和运行调整的判断。交付为 course/tutorial.md 与由其生成的 index.html，保留 00—23 章及现有阅读、搜索和标注交互。


## Progress


- [x] 2026-10-05：读取写作规范、构建与检查脚本、项目长期文档，确认正文是生成页面的唯一来源。
- [x] 2026-10-05：通读全部 24 章，完成 00—07 章的基础机制、计算和业务检查点修订。
- [x] 2026-10-05：完成 08—23 章、38 组练习答案和术语索引修订，开始独立阅读审阅。
- [x] 2026-10-05：独立读者通读后确认无交付前必须修订的问题，采纳光缆走向与 MTU 索引的两项措辞建议，完成最终文本复核。
- [x] 2026-10-05：生成页面，完成结构检查、17 项阅读器检查与 31 项标注检查，核查桌面、手机及打印截图。
- [x] 2026-10-05：同步长期文档与阅读说明；独立读者确认页面入口和 README 读者说明与教材一致。
- [x] 2026-10-05：生成最终教程包，完成归档及六文件逐字节一致性检查。


## Context and Orientation


course/tutorial.md 包含 24 章、四个综合案例、38 个答案块和 30 项参考资料。scripts/build.py 使用 markdown-it-py 将正文生成 index.html，assets/style.css、assets/app.js 和 assets/annotations.js 提供离线阅读及标注。scripts/check.py 检查章节与链接，scripts/browser_check.py 检查阅读行为与版面，scripts/annotation_check.py 检查个人标注，scripts/package.py 生成六文件分享包。项目当前目录没有 Git 仓库；修改前正文副本保存在 /private/tmp/telecom-tutorial-before-expression.md。


## Surprises & Discoveries


长期文档还描述一个深度优化版本，但当前工作区不存在 course/tutorial_v2.md 和 index_v2.html。本轮明确针对现有主教材，不建立额外版本。原稿已有连续服务主线，重点在于提高解释和判断的具体程度，并统一表达。

标注检查中的摘录歧义场景依赖第 01 章某个词重复出现。正文修改后只剩一次，旧测试数据不再代表歧义。测试现使用独立插入的重复摘录，在标注脚本初始化前建立场景；标注实现未改动，完整的 31 项检查重新运行并通过。

本机沙箱中 Chromium 启动遇到 MachPortRendezvous 权限拒绝。浏览器检查改为获得自动审批的提升权限执行，页面运行和交互检查均正常。


## Decision Log


2026-10-05：以现有正文逐章修订，页面通过构建同步。章节编号保持稳定，以支持已有目录、学习进度和标注定位。

2026-10-05：对重要数值说明计算条件和使用依据，公式、代入、结果和判断分开呈现；技术事实如需补充或精确核对，使用标准组织的一手资料。

2026-10-05：38 组参考答案统一先给结论，再按问题展开理由、步骤或计算。优先保留情境判断和方案取舍，使答案解释行动选择。

2026-10-05：长期架构与进度文档按当前工作区的主教材和阅读页面维护，旧版本实施文档作为历史记录保留。


## Plan of Work


首先通读 00—07 章，检查术语引入、协议过程和物理量解释。随后修订 08—20 章，使流程步骤包含责任、通过标准和失败后的调查方向，删减重复的通用流程说明。最后检查综合案例、索引和参考资料，使其与前文术语、计算及判断规则一致。对修改后的全文安排独立阅读审阅，并根据反馈继续完善。


## Milestones


第一阶段完成后，通信基础和业务路径能支持读者解释具体失败现象。第二阶段完成后，运维流程能支持读者判断下一步行动与完成条件。第三阶段完成后，综合案例和练习可以独立推理，生成页面与正文一致，离线阅读与标注正常。


## Concrete Steps


在 /Users/zeno/projects/telecom_ops_tutorial 编辑 course/tutorial.md。完成正文后执行 python3 scripts/build.py 和 python3 scripts/check.py；预期章节数量为 24，内部链接与本地资源完整。再执行 python3 scripts/browser_check.py 和 python3 scripts/annotation_check.py，核查桌面、移动与打印截图。最后执行 python3 scripts/package.py，并用 zipfile 核对归档中的正文、页面和资源与工作区一致。


## Validation and Acceptance


独立读者只收到教材文件，需诚实判断是否能独立理解，指出具体的前置知识缺口、因果跳跃、难以执行的规则及不能依据正文作答的练习。修订后重新审阅。每个主题应能说明机制为什么存在、怎样作用及如何用于判断；计算明确单位并解释结果。技术检查须确认 24 章和四个综合案例完整，答案可展开，搜索与学习进度正常，四种屏幕宽度无整页水平溢出，打印呈现完整内容。

最终结果：

- scripts/package.py 完成构建和结构检查：24 章、四个案例、38 组练习、30 项一手参考资料、91 个唯一 HTML 标识；内部链接和本地资源完整。
- scripts/browser_check.py 的 17 项检查通过，覆盖搜索、学习状态、答案、导航和打印，四种页面宽度无整页水平溢出；无 JavaScript 错误。
- scripts/annotation_check.py 的 31 项检查通过，覆盖拖选、重叠、编辑、持久化和导入导出；正文修改后的重新定位与歧义保留场景通过，无 JavaScript 错误。
- 视觉核查桌面 PPPoE 表格、手机排队计算与打印时延分析，计算块和表格呈现完整。截图与结构化结果保存在 docs/execution/qa。
- 补充核对正文 30 项行内来源均收录于参考资料章，38 组答案均包含结论段和后续有序解释。
- zipfile 验证归档无损坏，文件集合恰为六项；阅读说明与 README 读者部分一致，其余五个文件与工作区逐字节一致。

补充技术核对采用一手资料，包括 RFC 2516 的 PPPoE 过程及开销、RFC 6241 的确认提交与启动配置、RFC 4364 的 VPN 路由，以及 GPON、TCP 和质量测量相关参考材料。阈值的项目设计条件、同方向容量口径和回退时间计算在正文中逐项说明。


## Idempotence and Recovery


正文以 Markdown 为准，生成和打包可重复执行。备份只用于比较和恢复，不修改已有个人笔记或存储键。已有执行文档作为历史记录保留。


## Outcomes & Retrospective


正文修订与交付已完成，当前 73,606 字符，保留 24 章、四个综合案例和 38 组答案。计算给出单位、条件和判断，协议阶段对应具体响应，交付流程明确推进条件，综合案例呈现容量与恢复时间的取舍。index.html 与正文同源，教程包及维护记录已同步，没有剩余交付工作。

独立读者不带对话历史，只阅读教材，诚实评价可理解性与推理依据。首次全文审阅未发现必须修订的问题，能够复述排队、协议分阶段检查及主备容量机制，并正确预测扩大缓存、用户面失效和增加备用容量后的结果。采纳“实际光缆走向和接入连接”及 MTU “最大长度”两项精确措辞建议后，最终复核确认概念依赖、案例状态和答案依据完整，正文没有编辑说明或修订痕迹。最后仅核查首页介绍、学习路径卡片和 README 读者说明，也确认一致且能够独立理解。


## Artifacts and Notes


主要交付文件为 course/tutorial.md、index.html 和 dist/telecom-network-operations-course.zip。审阅发现与验证结果在本文追加，稳定教学约定同步 docs/design.md 和 docs/requirements.md，当前状态同步 docs/planning.md。

最终文件 SHA-256：

| 文件 | 摘要 |
| --- | --- |
| course/tutorial.md | 027474873b238ac828adf08946026cabbd61e1187010705c970dac9fb9e643a7 |
| index.html | 722f195da9adda766af5355bad2a41cc674284bbe623c4d92c5d6722aadbc119 |
| dist/telecom-network-operations-course.zip | 704e6d6d52a854297a05d866a39b24ae0e64ee3b90ff8eb1da303a82dd60e484 |


## Interfaces and Dependencies


继续使用现有 Markdown 表格、原生 details 答案块和文字流程图，不添加运行依赖。浏览器验证使用 requirements.txt 中的 Playwright。构建模板中的读者可见文字随正文表达同步调整。


## Revision Notes


2026-10-05：建立执行记录，明确主教材修订范围和完整交付验证方法。

2026-10-05：完成 00—07 章后检查 overview、architecture、planning、design 与执行记录。项目范围和系统结构未改变；计算展示及流程通过标准的稳定约定同步到 design 和 requirements，当前完成状态在本记录保存。

2026-10-05：完成 08—23 章和全部答案后检查长期文档。overview 的读者与范围仍准确；architecture 和 planning 中引用当前不存在的 v2 文件及写作技能，待最终维护同步时整理为现有交付状态。design 与 requirements 的教学约定已覆盖本轮改动。独立读者使用无对话历史的子代理，只读取教材。

2026-10-05：交付前再次检查 overview、architecture、planning、design、requirements 与本执行记录。overview 的目标和范围仍准确，保留原文；architecture 与 planning 已按当前交付整理，design 与 requirements 保存计算、术语及检查点约定，README 同步读者说明和维护入口。本执行记录标记完成，旧执行文档保留为历史。
