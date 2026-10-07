#!/usr/bin/env python3
"""Check the course's structure and navigation without external access."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.assets, self.chapter_ids = [], [], [], []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a' and 'href' in a:
            self.links.append(a['href'])
        if tag == 'section' and a.get('class') == 'chapter':
            self.chapter_ids.append(a['id'])
        if tag == 'script' and 'src' in a:
            self.assets.append(a['src'])
        if tag == 'link' and a.get('rel') == 'stylesheet':
            self.assets.append(a['href'])


def check(html_path='index.html', md_path='course/tutorial.md'):
    doc_file = ROOT / html_path
    md_file = ROOT / md_path
    if not doc_file.exists() or not md_file.exists():
        print(f'跳过检查：{html_path} 或 {md_path} 不存在')
        return
    document = doc_file.read_text(encoding='utf-8')
    source = md_file.read_text(encoding='utf-8')
    page = Page()
    page.feed(document)
    assert len(page.ids) == len(set(page.ids)), f'{html_path}: Duplicate HTML identifiers'
    assert page.chapter_ids == [f'chapter-{n:02d}' for n in range(24)], f'{html_path}: Missing or unordered chapters'
    for link in page.links:
        if link.startswith('#'):
            assert link[1:] in page.ids, f'{html_path}: Broken anchor: {link}'
        elif not link.startswith(('https://', 'http://')):
            assert (ROOT / link).is_file(), f'{html_path}: Missing local file: {link}'
    for asset in page.assets:
        assert not asset.startswith(('http:', 'https:', '//')), f'{html_path}: External resource dependency'
        assert (ROOT / asset).is_file(), f'{html_path}: Missing asset: {asset}'
    chapters = re.split(r'^## \d{2} · .+$', source, flags=re.M)[1:]
    assert len(chapters) == 24
    for number, body in enumerate(chapters):
        assert '学习目标' in body, f'{md_path}: Missing objective: {number}'
        if number < 23:
            assert '<details>' in body, f'{md_path}: Missing practice: {number}'
    assert source.count('<details>') == source.count('</details>'), f'{md_path}: Unbalanced answer blocks'
    assert document.count('<table>') == document.count('</table>'), f'{html_path}: Unbalanced tables'
    assert '<html lang="zh-CN">' in document
    assert '__NAV__' not in document and '__SECTIONS__' not in document
    assert '**' not in document, f'{html_path}: Unrendered Markdown emphasis'
    assert source.count('### 案例') == 4
    reference_urls = set(re.findall(r'\]\((https://[^)]+)\)', chapters[23]))
    print(f'[{html_path}] PASS：{len(chapters)} 个章节，{source.count("<details>")} 组练习，{len(reference_urls)} 项一手参考资料')
    print(f'[{html_path}] PASS：{len(page.ids)} 个唯一标识，内部链接完整，本地资源完整，无外部加载依赖')


def check_all():
    check('index.html', 'course/tutorial.md')
    if (ROOT / 'index_v2.html').exists():
        check('index_v2.html', 'course/tutorial_v2.md')


if __name__ == '__main__':
    check_all()

