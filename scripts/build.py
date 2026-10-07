#!/usr/bin/env python3
"""Build the offline course from its Markdown source."""
from pathlib import Path
import html
import re
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'course' / 'tutorial.md'
GROUPS = [(0, 0, '开始学习'), (1, 3, '一 · 通信基础'), (4, 7, '二 · 业务与网络'),
          (8, 11, '三 · 投入运行'), (12, 15, '四 · 保障运行'),
          (16, 20, '五 · 长期维护'), (21, 23, '六 · 案例与复习')]


def build(source_rel='course/tutorial.md', output_rel='index.html'):
    source_path = ROOT / source_rel
    if not source_path.exists():
        print(f'源文件不存在：{source_path}')
        return
    source = source_path.read_text(encoding='utf-8')
    parts = re.split(r'^## (\d{2}) · (.+)$', source, flags=re.M)
    parser = MarkdownIt('commonmark', {'html': True}).enable('table')
    chapters = []
    for i in range(1, len(parts), 3):
        number, title, body = parts[i:i + 3]
        chapters.append((number, title, body))
    sections = []
    navigation = []
    for start, end, label in GROUPS:
        entries = ''.join(f'<a class="toc-link" href="#chapter-{n}" data-chapter="chapter-{n}"><span class="toc-number">{n}</span><span>{html.escape(t)}</span><span class="toc-check" aria-hidden="true"></span></a>'
                          for n, t, _ in chapters if start <= int(n) <= end)
        navigation.append(f'<div class="toc-group"><p>{label}</p>{entries}</div>')
    for index, (number, title, body) in enumerate(chapters):
        rendered = parser.render(body)
        # A paragraph containing only strong text carries a standalone conclusion.
        rendered = re.sub(r'<p>(<strong>[^<]+</strong>)</p>', r'<p class="key-point">\1</p>', rendered)
        rendered = re.sub(r'<table>(.*?)</table>', r'<div class="table-wrap" tabindex="0" role="region" aria-label="课程表格"><table>\1</table></div>', rendered, flags=re.S)
        links = []
        if index > 0:
            links.append(f'<a href="#chapter-{chapters[index-1][0]}" class="chapter-prev">← 上一章</a>')
        if index < len(chapters)-1:
            links.append(f'<a href="#chapter-{chapters[index+1][0]}" class="chapter-next">下一章 →</a>')
        sections.append(f'''<section class="chapter" id="chapter-{number}" aria-labelledby="heading-{number}" data-number="{number}">
<div class="chapter-kicker">CHAPTER {number}</div><h2 id="heading-{number}">{html.escape(title)}</h2>
<div class="prose">{rendered}</div>
<footer class="chapter-footer"><button class="complete-button" type="button" data-complete="chapter-{number}" aria-pressed="false">标记本章已学完</button><nav aria-label="{number} 章前后导航">{''.join(links)}</nav></footer></section>''')
    
    download_md = source_rel
    document = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="面向计算机专业读者的运营商网络运维全流程课程，从通信基础到业务路径、网络交付、服务保障与退网。">
<meta name="color-scheme" content="light"><title>运营商网络运维全流程教程</title>
<link rel="stylesheet" href="assets/style.css"><script defer src="assets/app.js"></script><script defer src="assets/annotations.js"></script></head>
<body><a class="skip-link" href="#main">跳到课程正文</a>
<div class="site-shell"><aside class="sidebar" aria-label="课程目录与学习工具">
<a class="brand" href="#top"><span class="brand-mark" aria-hidden="true">N</span><span>网络运维课堂<small>从基础到完整流程</small></span></a>
<div class="tools js-tools"><label for="search">搜索章节与正文</label><div class="search-box"><span aria-hidden="true">⌕</span><input id="search" type="search" placeholder="例如：光纤、开通、回退" maxlength="80" autocomplete="off"><button id="clear-search" type="button" aria-label="清空搜索" title="清空搜索" hidden>×</button></div><p class="search-status" id="search-status" role="status" aria-live="polite">24 个章节 · 可离线阅读</p></div>
<div class="progress-panel js-tools"><div><span>学习进度</span><strong id="progress-label">0 / 24</strong></div><progress id="progress" max="24" value="0" aria-label="已完成章节"></progress><p id="storage-note">进度保存在当前浏览器</p></div>
<details class="course-menu" open><summary>课程目录 <span aria-hidden="true">⌄</span></summary><nav id="toc" aria-label="章节目录">__NAV__</nav></details>
<div class="sidebar-bottom"><a href="{download_md}" download>下载 Markdown 正文 ↗</a><button id="reset-progress" class="text-button js-tools" type="button">清除学习进度</button></div>
</aside><main id="main" tabindex="-1">
<header class="hero" id="top"><div class="eyebrow">通信基础 · 网络架构 · 服务保障</div><h1>运营商网络运维<br>全流程教程</h1><p>沿用户的数据路径解释通信机制，再跟随一项服务完成规划、交付与长期维护，学习怎样定位故障、选择措施并验证结果。</p><div class="hero-meta"><span>面向计算机专业读者</span><span>24 个章节</span><span>4 个综合案例</span></div><a class="start-link" href="#chapter-00">开始学习 <span aria-hidden="true">→</span></a><div class="hero-network" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div></header>
<div class="reading-toolbar js-tools"><span>选中正文可划线、强调或添加注释</span><div><label for="font-size">正文大小</label><select id="font-size"><option value="standard">标准</option><option value="large">较大</option><option value="larger">大字</option></select><button id="open-annotations" type="button">我的标注 <span id="annotation-count">0</span></button><button id="print" type="button">打印 / 保存 PDF</button></div></div>
<p id="annotation-status" class="annotation-status js-tools" role="status" aria-live="polite">标注保存在当前浏览器，可导出备份</p>
<div class="path-cards"><a href="#chapter-01"><small>01—03</small><strong>解释通信机制</strong><span>用指标与计算判断质量</span></a><a href="#chapter-04"><small>04—07</small><strong>追踪业务路径</strong><span>按接入与转发阶段定位</span></a><a href="#chapter-08"><small>08—20</small><strong>掌握运维流程</strong><span>从规划到运行与退网</span></a><a href="#chapter-21"><small>21—23</small><strong>案例与知识复习</strong><span>用完整案例练习判断</span></a></div>
<div id="no-results" role="status" hidden><h2>没有找到匹配章节</h2><p>可以缩短关键词，或清空搜索后查看完整目录。</p><button id="restore" type="button">查看全部章节</button></div>
<div class="chapters">__SECTIONS__</div><footer class="site-footer"><p>运营商网络运维全流程教程</p><a href="#top">回到课程首页 ↑</a><span>参考资料核对：2026 年 10 月</span></footer>
<section id="annotation-print-notes" aria-label="个人注释"></section>
</main></div>
<div id="annotation-feedback" class="annotation-feedback js-tools" aria-hidden="true" hidden></div>
<div id="annotation-toolbar" class="annotation-toolbar js-tools" role="toolbar" aria-label="文字标注操作" hidden><select id="annotation-target" aria-label="选择标注文字范围" title="选择标注文字范围" hidden></select><button type="button" data-annotation-action="underline">下划线</button><button type="button" data-annotation-action="wave">波浪线</button><button type="button" data-annotation-action="emphasis">强调</button><button type="button" data-annotation-action="comment">注释</button><button type="button" id="close-annotation-toolbar" aria-label="关闭标注工具">×</button></div>
<section id="annotation-preview" class="annotation-preview js-tools" role="dialog" aria-modal="false" aria-labelledby="annotation-preview-title" hidden><div class="annotation-preview-heading"><h2 id="annotation-preview-title">我的注释</h2><button type="button" id="close-annotation-preview" aria-label="关闭注释">×</button></div><blockquote id="annotation-preview-quote"></blockquote><p id="annotation-preview-note"></p><div class="annotation-preview-actions"><button id="edit-annotation-preview" type="button">编辑</button><button id="delete-annotation-preview" type="button">删除</button></div></section>
<dialog id="annotation-editor" class="annotation-dialog js-tools" aria-labelledby="annotation-editor-title"><form id="annotation-form"><div class="annotation-dialog-heading"><h2 id="annotation-editor-title">添加注释</h2><button type="button" data-close-editor aria-label="关闭注释编辑">×</button></div><blockquote id="annotation-quote"></blockquote><label for="annotation-note">我的注释</label><textarea id="annotation-note" rows="6" maxlength="2000" placeholder="记下你的理解、疑问或补充资料" required></textarea><p id="annotation-editor-error" class="annotation-error" role="alert"></p><div class="annotation-dialog-actions"><button type="button" data-close-editor>取消</button><button type="submit" class="annotation-primary">保存注释</button></div></form></dialog>
<dialog id="annotation-library" class="annotation-dialog annotation-library js-tools" aria-labelledby="annotation-library-title"><div class="annotation-dialog-heading"><h2 id="annotation-library-title">我的标注</h2><button type="button" id="close-annotation-library" aria-label="关闭我的标注">×</button></div><p class="annotation-library-intro">在这里查看摘录与注释，或回到原文继续阅读。</p><div class="annotation-file-tools"><button id="export-annotations" type="button">导出标注</button><button id="import-annotations" type="button">导入标注</button><input id="annotation-file" type="file" accept=".json,application/json" hidden></div><p id="annotation-library-status" role="status" aria-live="polite"></p><div id="annotation-list"></div></dialog>
<noscript><style>.js-tools,.complete-button{{display:none!important}}</style></noscript></body></html>'''
    (ROOT / output_rel).write_text(document.replace('__NAV__', ''.join(navigation)).replace('__SECTIONS__', '\n'.join(sections)), encoding='utf-8')
    print(f'生成 {output_rel}：{len(chapters)} 个章节；正文 {len(source):,} 字符')


def build_all():
    build('course/tutorial.md', 'index.html')
    v2_source = ROOT / 'course' / 'tutorial_v2.md'
    if v2_source.exists():
        build('course/tutorial_v2.md', 'index_v2.html')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--v2':
        build('course/tutorial_v2.md', 'index_v2.html')
    else:
        build_all()
