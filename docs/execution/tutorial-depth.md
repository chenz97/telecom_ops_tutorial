# 完善教程的技术讲解与阅读衔接

## Purpose / Big Picture

本次工作使具有计算机背景、没有通信基础的读者能够解释网络如何工作，并根据技术机制理解运维判断。阅读入口为根目录 index.html，正文来源为 course/tutorial.md。保留 00—23 的章节编号和已有阅读工具，补充协议过程、状态转换与数值推理，重写章节和段落衔接。本文按 /Users/zeno/.codex/PLANS.md 维护。

## Progress

- [x] 2026-10-01：通读正文、维护文档和生成检查脚本，识别概念与流程之间缺少机制解释的问题。
- [x] 2026-10-01：更新需求与项目目标，保存正文工作前副本到 /private/tmp/telecom-tutorial-before.md。
- [x] 2026-10-01：核对 TCP、宽带、5G、语音与承载的一手资料，完善 01—07 的机制与示例。
- [x] 2026-10-01：完善 08—20 的技术判断，扩展四个综合案例，增加 11 组机制练习，补齐技术索引与 30 项参考资料。
- [x] 2026-10-01：通读全文并完成独立读者首轮审阅，修订缓存题干、主备拓扑、交换与路由定义、术语次序及会话异常结论。
- [x] 2026-10-01：生成最终 HTML，通过结构、链接和 JavaScript 检查及 17 项浏览器检查；人工核查新增协议表格、算例和主备路径版面。
- [x] 2026-10-01：同步 overview、requirements、architecture、design 与 planning；生成分享包并核对校验和四个源文件一致性。

## Context and Orientation

项目为离线静态课程，没有后端。scripts/build.py 使用 markdown-it-py 将正文转为 index.html，assets 保存样式和交互。scripts/check.py 检查 24 章、引用、练习和本地资源，scripts/browser_check.py 用 Playwright 检查交互与多种页面宽度。scripts/package.py 生成 dist/telecom-network-operations-course.zip。原教程共有 27 个答案块和 16 个引用，检查脚本中存在固定数字断言。已改为按正文核对实际答案块数量，并确认行内引用收录于参考章。扩展后为 38 个答案块和 30 项引用。

## Plan of Work

第一阶段补充通信分层、队列与时延、宽带上线、移动注册与会话，以及语音、VPN 和承载机制。新增说明融入原有主题，按原因、过程和结果展开，使后续流程获得技术依据。第二阶段将规划、开通、资源管理与监控等流程连接到可观测状态，提供实际字段、差分判断和算例，并扩展四个综合案例的技术证据。第三阶段通读全文，交给只阅读教材的审阅者检查自洽性与可读性，修订后生成并验证离线版本。

## Milestones

第一阶段完成后，读者应能解释一份数据经过各层封装和转发的过程，描述家庭宽带与 5G 数据会话的主要阶段，并用数值解释排队和传输时间。第二阶段完成后，读者应能据指标计算容量、据计数器分析异常、据状态转换确定开通和变更的验证点。第三阶段完成后，所有章节与练习在离线页面中可阅读，搜索能找到新增机制，移动和打印布局可用，分享包正文与工作区保持一致。

## Concrete Steps

在 /Users/zeno/projects/telecom_ops_tutorial 编辑 course/tutorial.md。执行 python3 scripts/build.py 和 python3 scripts/check.py，确认章节编号、内部链接和资源完整。运行 python3 scripts/browser_check.py 检查阅读器，再检查新增长表格、公式和技术流程所在位置的截图。执行 python3 scripts/package.py，使用 Python zipfile 检查分享包校验与源文件一致性。

## Validation and Acceptance

内容验收采用独立读者审阅，重点检查术语首次解释、段落因果、公式单位、示例边界与流程闭环。技术定义依据一手资料核对。结构检查必须覆盖新增引用和答案块。浏览器应在 390、760、1024 和 1440 像素宽度无整页水平溢出；练习展开、搜索和无脚本阅读仍有效。新增内容不得出现未渲染 Markdown 或不可读的公式。

## Idempotence and Recovery

生成和打包命令可反复运行，覆盖派生文件。正文编辑前副本保存在 /private/tmp，可用于比较原文。维护文件与正文分开，读者不依赖执行记录即可理解教材。

## Surprises & Discoveries

浏览器检查原先假定每章只有一个答案块，扩展练习后严格定位报错；已将单个答案展开检查明确定位到第一项，其余练习仍受总数与打印展开检查覆盖。浏览器启动受系统沙箱限制，使用获准的本地进程执行权限验证。

原需求将协议报文与算法推导全部排除，这使概念到实现之间缺少教学层次。已调整为解释代表性的交互与简单计算，保留实际设备命令由操作手册承接的课程边界。工作目录没有 Git 仓库，修改比较使用正文副本。

## Decision Log

2026-10-01：保留稳定章节编号，技术说明融入相应章节。理由是读者已有导航和进度可继续使用，相关原理也能在使用它的上下文中理解。

2026-10-01：采用因果解释、简化时序和可演算案例提高深度，同时将技术状态落实到运维证据。理由是读者需要理解判断依据，补充缩略词清单不足以达到教学目的。

## Outcomes & Retrospective

状态：已完成。正文从 40,055 字符扩展为 71,213 字符，增长约 78%，保留 24 章编号，包含 38 组答案块和 30 项参考资料。技术机制按场景融入正文，流程使用具体状态与测量结果解释判断；四个案例补齐路径、容量和验证证据。独立读者完成全文审阅与复审，案例顺序调整也经再次检查。页面和分享包同步完成，全部验收通过，无剩余任务。

本次改进表明，技术深度与阅读衔接需要共同设计：原理建立因果关系，状态提供观察入口，计算解释资源边界，案例将这些依据连接到完整工作流程。

## Artifacts and Notes

主要交付文件为 course/tutorial.md、index.html 和 dist/telecom-network-operations-course.zip。原建设记录 docs/execution/tutorial.md 作为历史记录保留，新验证证据写入本执行文档。

## Interfaces and Dependencies

沿用 Markdown 表格和原生 details 答案块，流程图沿用 flow 样式。正文使用可直接显示的文字公式，无外部数学脚本。构建与验证依赖保存在 requirements.txt，新增一手资料通过正文链接提供。

## Revision Notes

2026-10-01：建立本轮执行记录，更新课程技术深度与衔接要求。


## Validation Evidence

2026-10-01：python3 scripts/check.py 输出 24 个章节、38 组练习、30 项一手参考资料和 62 个唯一标识，内部链接和本地资源完整；所有行内引用已收录于参考章。node --check assets/app.js 通过。

python3 scripts/browser_check.py 完成 17 项检查，覆盖搜索、答案、进度、字号与打印，以及四种页面宽度、无脚本阅读和存储异常。浏览器脚本错误为零，结果保存于 docs/execution/qa/results.json。新增截图 desktop-pppoe.png、mobile-optical-budget.png、mobile-queue-analysis.png、desktop-vpn-case.png 和 print-delay-analysis.png 经人工核查，协议表格和公式显示正常。

python3 scripts/package.py 生成 dist/telecom-network-operations-course.zip，压缩包包含五个可分享文件。zipfile.testzip() 返回 None；包内 index.html、course/tutorial.md 及两个 assets 文件与工作区逐字节一致；阅读说明包含当前的 30 项资料与 38 组练习。

独立读者首轮提出五项具体问题，分别涉及缓存题干、完整主备路径、交换与路由定义、术语次序和结论证据。修订后全文复审确认可以交付，补齐一处前缀定义。最终案例顺序检查确认规划到退网、证据到优化结果的叙述连贯。

2026-10-01：完成全部内容与交付验证，本执行记录标记为已完成。
