# 教程建设进度

## 当前状态

当前交付为 course/tutorial.md 与同源的 index.html，包含 24 章、四个综合案例、38 组可展开练习及 30 项一手参考资料。教材沿数据交付过程解释通信，再沿服务生命周期讲解运维。重要计算呈现公式、代入、结果与判断，协议和工作流程给出阶段结果及调查方向，案例体现容量、恢复时间与服务优先级的取舍。

全文已建立核心机制、行动规则与支撑细节的阅读层级，42 个独立结论与相邻原理、数值和案例相连，段内选择性强调具体检查规则。网页从正文生成对应的重点样式，桌面、手机和打印均保持清晰主次。独立读者通读 24 章，确认内容自洽、重点有解释支持，并能复述规则及推演条件变化后的结果。实施记录见 execution/tutorial-emphasis.md；此前的表达和教学修订记录保存在 execution/tutorial-expression.md。

阅读器提供目录、搜索、进度、字号和打印，并支持下划线、强调与注释。页面内容与正文同步，离线资源继续使用本地相对路径。

## 验证与维护

本轮结构检查确认章节、内部链接与本地资源完整，42 个独立结论均正确渲染。阅读器的 17 项浏览器检查与标注的 31 项检查通过，无 JavaScript 错误；四种页面宽度无整页水平溢出。桌面上线协议、手机突发分析与打印时延截图已核查。分享包由当前正文与页面生成，归档完整，六项交付文件与工作区逐字节一致，验证证据保存在 execution/qa。

后续维护先更新 course/tutorial.md，再生成页面和教程包。技术内容变动时核对相关一手材料，检查受影响章节与案例，并安排独立读者验证全文的学习依赖。页面与交互变动时运行对应的浏览器检查。

初版建设历史保存在 execution/tutorial.md，技术扩展和叙述重组历史分别保存在 execution/tutorial-depth.md 和 execution/tutorial-coherence.md。execution/tutorial-optimization.md 保留版本扩展的历史记录。个人标注功能及交互改进分别记录在 execution/annotations.md 和 execution/annotation-interaction.md；慢速拖选与波浪下划线的实施及验证记录见 execution/drag-selection-wave.md。
