# 创建运营商网络运维全流程教程

本文为初版建设的已完成历史记录。后续技术讲解与衔接完善，以及当前交付验证，见 tutorial-depth.md；qa 目录保存最新验证截图与结果。

## Purpose / Big Picture

本项目将空白仓库转为可离线阅读的中文教程。读者打开根目录 index.html 即可从通信基础学习到网络运行维护的完整流程，也能直接阅读 course/tutorial.md。本文按照 /Users/zeno/.codex/PLANS.md 的执行文档规则维护。

## Progress

- [x] 2026-10-01：确认读者、教学范围与交付方式，编写 docs/requirements.md 和 docs/overview.md。
- [x] 2026-10-01：核对 16 项一手资料，完成 24 章正文与四个案例。
- [x] 2026-10-01：实现 HTML、搜索、进度、字号、移动目录和打印支持。
- [x] 2026-10-01：通过结构与链接检查、JavaScript 语法检查和 16 项浏览器行为检查；人工检查桌面、手机与打印截图。
- [x] 2026-10-01：完成两轮独立读者审阅，修订证据结论、案例闭环和术语解释；维护文档已同步。
- [x] 2026-10-01：生成 dist/telecom-network-operations-course.zip，并验证压缩包内容和校验结果。

## Surprises & Discoveries

仓库只有 AGENTS.md，没有现有课程或应用代码。Python 环境具备 markdown-it-py 和 Playwright；浏览器原始沙箱启动被系统限制，需要使用允许本地浏览器进程的执行权限进行验证。教程需要从内容到阅读界面完整构建。运营商网络的固定与移动路径必须分别展开，避免用单一路径代替所有业务。

## Decision Log

2026-10-01：采用静态 HTML 和 Markdown 同源生成。离线阅读无需安装依赖，正文可独立复用，避免两份正文产生差异。

2026-10-01：先写 requirements.md，再确定章节和实现。课程以用户体验和业务生命周期为主线，缩略词随解释引入。

## Outcomes & Retrospective

状态：已完成。正文为 24 章，包含四个综合案例、27 组可展开练习和 16 项一手参考资料。两轮独立读者审阅确认主要流程完整、可读。结构检查与 16 项浏览器行为检查通过，无浏览器脚本错误。桌面、手机及打印模式截图经人工检查，版面清晰，正文无原始 Markdown 强调标记。已生成可分享的五文件离线教程包，全部交付工作完成。

## Context and Orientation

工作目录为 /Users/zeno/projects/telecom_ops_tutorial。course/tutorial.md 将保存课程正文。scripts/build.py 将把正文转为根目录 index.html，assets 下保存页面样式和交互脚本。docs 下保存稳定项目说明，docs/execution/tutorial.md 保存本次实施进展。静态页面指不需要服务器计算即可显示的页面。scripts/package.py 在重新生成和结构检查后创建分享压缩包。requirements.txt 记录构建与验证依赖。

## Plan of Work

首先使用 3GPP、ITU、IETF 和 TM Forum 的公开资料核对架构与术语，将参考链接放入教材对应章节及来源导航。然后按基础知识、网络路径、全生命周期和综合案例组织正文，每章包含学习目标与自测。最后用生成脚本将 Markdown 转为可浏览的 HTML，加入目录、搜索、学习进度和打印支持。

正文完成后执行独立读者审阅，审阅者只阅读教材，检查知识跳跃、术语负担、逻辑矛盾和流程闭环。根据反馈修订全文并重新生成 HTML。修改长期稳定结论时同步 docs/overview.md、docs/architecture.md、docs/planning.md 或 docs/design.md。

## Concrete Steps

在项目根目录执行 python3 scripts/build.py 生成页面；执行 python3 scripts/check.py 检查章节和链接。浏览器直接打开 index.html，或运行 python3 -m http.server 8765 通过本机地址查看页面。维护正文时编辑 course/tutorial.md，修改页面体验时编辑 assets/style.css 与 assets/app.js，再重新生成页面。

## Validation and Acceptance

顺序阅读时，读者能够沿家庭宽带和移动数据的路径说明各环节职责；通过故障、开通和变更案例描述输入、判断依据、协作以及结束条件。搜索“光纤”能显示相关章节，搜索不存在的词有提示，清空搜索可恢复全目录。章节完成状态刷新后保留，浏览器阻止存储也可继续阅读。桌面、窄屏和打印预览均无正文裁切，脚本关闭仍显示完整教材。检查脚本报告无重复标识、内部链接失效和正文缺失。

## Idempotence and Recovery

生成脚本可反复执行，只覆盖生成的 index.html。正文和资源保留独立源文件。学习状态可在界面清除。验证所用浏览器、截图和临时文件不影响教材内容。

## Artifacts and Notes

交付物是 index.html、course/tutorial.md 及 assets 中的页面资源。docs 文档用于维护，教材不依赖执行文档或对话上下文。

## Interfaces and Dependencies

页面交互使用原生 JavaScript。生成器优先使用当前环境可用的 Markdown 解析器；使用 markdown-it-py，依赖已记录在 requirements.txt。图示使用 HTML 和 CSS，不调用外部服务。搜索按章节匹配标题和正文；完成状态用章节标识保存到浏览器本地存储。

## Revision Notes

2026-10-01：建立需求与执行文档，开始权威资料核对。

2026-10-01：完成正文、页面与两轮读者审阅。结构检查确认 24 章、27 组练习、62 个唯一标识和全部内部链接完整。

## Validation Evidence

结构检查输出为：24 个章节、27 组练习、16 项参考资料、62 个唯一标识，内部链接完整且无外部加载依赖。node --check assets/app.js 通过。python3 scripts/browser_check.py 完成 16 项检查：搜索与空结果、完成与重载、清除进度、字号持久化、答案展开、被搜索隐藏的章节跳转、打印显示全章与答案、390/760/1024/1440 像素页面无水平溢出、手机目录跳转、脚本错误检查、存储受阻、存储数据损坏和无脚本阅读。

浏览器结果保存在 docs/execution/qa/results.json。人工检查 desktop-home.png、desktop-broadband.png、mobile-home.png、mobile-broadband.png、mobile-cases.png 和 print-preview.png。修正了中文标点与 Markdown 强调边界的兼容问题，并把未渲染标记检查加入结构与浏览器检查。

独立读者审阅第一轮提出综合案例证据边界、最终结果、资源编号关联和术语解释问题；第二轮确认整体可读与闭环，仅提出两处局部设备位置及数量表述，已修正。

2026-10-01：完成浏览器与人工版面验证，同步长期文档，生成最终教程包；无剩余实施事项。
