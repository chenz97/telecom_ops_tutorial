#!/usr/bin/env python3
"""Verify personal annotations through the actual offline reading interface."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'execution' / 'qa'
OUT.mkdir(exist_ok=True)
URL = (ROOT / 'index.html').as_uri()
KEY = 'telecom-course-annotations-v1'
results = []

def record(message):
    results.append(message)
    print('PASS:', message, flush=True)

def saved(page):
    return page.evaluate('(key)=>JSON.parse(localStorage.getItem(key)).annotations', KEY)

def select(page, chapter='chapter-01', selector='p', start=0, end=30):
    page.locator(f'#{chapter} .prose {selector}').first.scroll_into_view_if_needed()
    page.evaluate('''({chapter,selector,start,end})=>{
      const root=document.querySelector('#'+chapter+' .prose '+selector);
      const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT); const nodes=[];let n,at=0;
      while(n=walker.nextNode()){nodes.push({n,start:at,end:at+n.length});at+=n.length}
      const left=nodes.find(x=>x.end>start),right=nodes.find(x=>x.end>=Math.min(end,at));
      const range=document.createRange();range.setStart(left.n,start-left.start);range.setEnd(right.n,Math.min(end,at)-right.start);
      const selection=getSelection();selection.removeAllRanges();selection.addRange(range);
    }''', {'chapter':chapter, 'selector':selector,'start':start,'end':end})
    page.locator('#annotation-toolbar').wait_for(state='visible')

def apply(page, kind):
    page.locator(f'[data-annotation-action="{kind}"]').click()

def library(page):
    page.locator('#open-annotations').click()

def close_library(page):
    page.locator('#close-annotation-library').click()

def comment(page, note):
    apply(page, 'comment')
    page.locator('#annotation-note').fill(note)
    page.locator('#annotation-form button[type=submit]').click()
    page.locator('#annotation-editor').wait_for(state='hidden')
    page.locator('#annotation-preview').wait_for(state='visible')

def slow_drag(page, selector, start, end, scroll=False):
    target=page.locator(selector).first;target.scroll_into_view_if_needed()
    points=target.evaluate("""(el,{start,end})=>{
      const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);const nodes=[];let node,offset=0;
      while(node=walker.nextNode()){nodes.push({node,offset,end:offset+node.length});offset+=node.length;}
      const point=at=>{const item=nodes.find(n=>n.end>at),r=document.createRange();
        r.setStart(item.node,at-item.offset);r.setEnd(item.node,at-item.offset+1);const b=r.getBoundingClientRect();
        return {x:b.left+1,y:b.top+b.height/2,right:b.right-1};};
      return {a:point(start),b:point(end)};
    }""",{'start':start,'end':end})
    page.mouse.move(points['a']['x'],points['a']['y']);page.mouse.down()
    page.wait_for_timeout(250)
    assert page.evaluate('getSelection().rangeCount')==1
    page.mouse.move((points['a']['x']+points['b']['right'])/2,(points['a']['y']+points['b']['y'])/2,steps=12)
    page.wait_for_timeout(200)
    assert not page.locator('#annotation-toolbar').is_visible()
    page.mouse.move(points['b']['right'],points['b']['y'],steps=12)
    page.wait_for_timeout(200)
    assert page.evaluate('getSelection().toString().length')>0
    if scroll:
        page.mouse.wheel(0,80);page.wait_for_timeout(150)
        assert page.evaluate('getSelection().toString().length')>0
    page.mouse.up()
    page.locator('#annotation-toolbar').wait_for(state='visible')
    assert page.evaluate('getSelection().toString().length')>0
    return page.evaluate('getSelection().toString()')

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={'width':1440,'height':1000}, accept_downloads=True, reduced_motion='reduce')
    page = context.new_page(); errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(URL)
    original = page.locator('#chapter-01 .prose').text_content()
    # Real pointer drag, independent from the scripted range helper.
    paragraph=page.locator('#chapter-01 .prose p').first
    paragraph.scroll_into_view_if_needed()
    coords=paragraph.evaluate('''el=>{const n=el.firstChild;const a=document.createRange(),b=document.createRange();
      a.setStart(n,0);a.setEnd(n,1);b.setStart(n,12);b.setEnd(n,13);
      const x=a.getBoundingClientRect(),y=b.getBoundingClientRect();return {x:x.left+1,y:x.top+x.height/2,end:y.right-1,endY:y.top+y.height/2};}''')
    page.mouse.move(coords['x'],coords['y']);page.mouse.down()
    page.wait_for_timeout(250)
    assert page.evaluate('getSelection().rangeCount')==1
    assert not page.locator('#annotation-toolbar').is_visible()
    page.mouse.move(coords['end'],coords['endY'],steps=20);page.mouse.up()
    page.locator('#annotation-toolbar').wait_for(state='visible')
    page.screenshot(path=str(OUT/'annotation-selection.png'))
    apply(page,'underline')
    assert page.locator('#chapter-01 .annotation-underline').count()>0
    assert saved(page)[0]['quote'].strip()
    record('A paused mouse press followed by dragging preserves the native selection and creates a saved underline')
    # Overlap three types, span the existing bold element and a paragraph boundary.
    select(page, selector='p', start=0, end=120); apply(page,'emphasis')
    select(page, selector='p', start=5, end=75)
    note='<img src=x onerror="window.annotationInjected=true">\n学习笔记：理解封装与逐跳转发。'
    comment(page,note)
    assert page.locator('.annotation-emphasis.annotation-comment').count()>0
    assert page.locator('#chapter-01 .prose').text_content()==original
    assert not page.evaluate('Boolean(window.annotationInjected)')
    library(page)
    assert page.locator('.annotation-card').count()==3
    assert page.locator('.annotation-card-note img').count()==0
    assert page.locator('.annotation-card-note').inner_text()==note
    page.screenshot(path=str(OUT/'annotation-library-safe-text.png'))
    card=page.locator('.annotation-card').filter(has=page.locator('.annotation-card-note'))
    card.get_by_role('button',name='编辑注释').click()
    page.locator('#annotation-note').fill('取消的修改')
    page.get_by_role('button',name='取消',exact=True).click()
    assert page.locator('.annotation-card-note').inner_text()==note
    card=page.locator('.annotation-card').filter(has=page.locator('.annotation-card-note'))
    card.get_by_role('button',name='编辑注释').click()
    page.locator('#annotation-note').fill('已编辑的注释：协议状态应与业务验证相互印证。')
    page.locator('#annotation-form button[type=submit]').click()
    page.locator('#annotation-library').wait_for(state='visible')
    assert '已编辑的注释' in page.locator('.annotation-card-note').inner_text()
    page.screenshot(path=str(OUT/'annotation-library-desktop.png'))
    close_library(page)
    page.reload()
    assert len(saved(page))==3
    assert page.locator('.annotation-underline').count()>0
    assert page.locator('.annotation-emphasis.annotation-comment').count()>0
    record('Overlapping types preserve the prose; comments are safe text, editable, cancellable and persistent')
    library(page)
    page.locator('.annotation-card').filter(has_text='· 下划线').get_by_role('button',name='删除',exact=True).click()
    assert page.locator('.annotation-underline').count()==0
    assert page.locator('.annotation-emphasis.annotation-comment').count()>0
    close_library(page)
    page.locator('[data-complete="chapter-00"]').click()
    page.locator('#reset-progress').click()
    page.reload()
    assert len(saved(page))==2
    record('Each overlapping record can be deleted independently; progress reset preserves annotations')
    # Keyboard text selection and Tab access to the toolbar.
    select(page,start=20,end=30)
    page.keyboard.press('Shift+ArrowRight')
    page.wait_for_timeout(150)
    page.keyboard.press('Tab')
    assert page.locator('[data-annotation-action=underline]').evaluate('el=>el===document.activeElement')
    page.keyboard.press('Enter')
    assert len(saved(page))==3
    record('Keyboard selection reaches the annotation tools with Tab and applies with Enter')
    # Multi-block range preserves original structural elements.
    page.locator('#chapter-01 .prose p').first.scroll_into_view_if_needed()
    page.evaluate('''()=>{const ps=document.querySelectorAll('#chapter-01 .prose p');const r=document.createRange();
      r.setStart(ps[0],0);r.setEnd(ps[1],ps[1].childNodes.length);getSelection().removeAllRanges();getSelection().addRange(r);}''')
    page.locator('#annotation-toolbar').wait_for(state='visible');apply(page,'underline')
    assert page.locator('#chapter-01 .prose').text_content()==original
    assert page.locator('#chapter-01 .prose strong').count()>0
    select(page,selector='p:has(strong)',start=0,end=120);apply(page,'emphasis')
    assert page.locator('#chapter-01 .prose strong .annotation-emphasis').count()>0
    select(page,chapter='chapter-23',selector='a',start=0,end=15);apply(page,'emphasis')
    link=page.locator('#chapter-23 .prose a').first
    assert link.locator('.annotation-emphasis').count()>0 and link.get_attribute('href').startswith('https://')
    select(page,chapter='chapter-02',selector='td',start=0,end=10);apply(page,'underline')
    assert page.locator('#chapter-02 td .annotation-underline').count()>0
    record('Cross-paragraph, bold, link and table selections retain the existing document structure')
    # Navigation restores search and opens collapsed answers.
    page.locator('#chapter-01 details').first.evaluate('el=>el.open=true')
    select(page,chapter='chapter-01',selector='details p',start=0,end=20);comment(page,'答案中的笔记')
    page.locator('#chapter-01 details').first.evaluate('el=>el.open=false')
    page.locator('#search').fill('NO_MATCH_ANNOTATION')
    library(page)
    page.locator('.annotation-card').filter(has_text='答案中的笔记').get_by_role('button',name='回到原文').click()
    assert page.locator('#search').input_value()==''
    assert page.locator('#chapter-01 details').first.get_attribute('open') is not None
    assert page.locator('.annotation-comment').count()>0
    page.locator('#chapter-01 .annotation-comment').first.click()
    page.locator('#annotation-preview').wait_for(state='visible')
    assert page.locator('#annotation-toolbar').is_visible()
    assert not page.locator('#annotation-library').is_visible()
    page.locator('#close-annotation-toolbar').click()
    record('Annotation navigation restores filtered chapters and answers; marks open the toolbar and bottom comment')
    library(page)
    before=saved(page)
    with page.expect_download() as download_event: page.locator('#export-annotations').click()
    download=download_event.value; export_path=OUT/'annotations-export.json';download.save_as(str(export_path))
    exported=json.loads(export_path.read_text())
    assert exported['annotations']==before
    page.locator('#annotation-file').set_input_files({'name':'broken.json','mimeType':'application/json','buffer':b'{broken'})
    page.wait_for_function("document.querySelector('#annotation-library-status').textContent.includes('无法读取')")
    assert saved(page)==before
    page.locator('#annotation-file').set_input_files(str(export_path))
    page.wait_for_function("document.querySelector('#annotation-library-status').textContent.includes('已导入 0')")
    assert saved(page)==before
    # Editing after a backup preserves the current note when that old backup is imported again.
    card=page.locator('.annotation-card').filter(has_text='已编辑的注释')
    card.get_by_role('button',name='编辑注释').click()
    page.locator('#annotation-note').fill('备份之后的新内容')
    page.locator('#annotation-form button[type=submit]').click()
    page.locator('#annotation-library').wait_for(state='visible')
    current=saved(page)
    page.locator('#annotation-file').set_input_files(str(export_path))
    page.wait_for_function("document.querySelector('#annotation-library-status').textContent.includes('已导入 0')")
    assert saved(page)==current
    assert page.locator('.annotation-card').filter(has_text='备份之后的新内容').count()==1
    invalid=json.loads(json.dumps(exported));invalid['annotations'][0]['type']='unknown'
    page.locator('#annotation-file').set_input_files({'name':'invalid.json','mimeType':'application/json','buffer':json.dumps(invalid).encode()})
    page.wait_for_function("document.querySelector('#annotation-library-status').textContent.includes('无法读取')")
    assert saved(page)==current
    record('Export is complete; invalid imports preserve data, and old backups preserve edited notes without duplicates')
    close_library(page)
    page.emulate_media(media='print');page.evaluate("dispatchEvent(new Event('beforeprint'))")
    assert page.locator('#annotation-print-notes').is_visible()
    assert '备份之后的新内容' in page.locator('#annotation-print-notes').inner_text()
    assert not page.locator('#annotation-toolbar').is_visible()
    page.locator('#annotation-print-notes').scroll_into_view_if_needed()
    page.screenshot(path=str(OUT/'annotation-print.png'))
    page.evaluate("dispatchEvent(new Event('afterprint'))");page.emulate_media(media='screen')
    record('Printing keeps markings and adds the personal comment appendix')
    for width in [390,760,1024,1440]:
        page.set_viewport_size({'width':width,'height':844})
        select(page,start=0,end=25)
        box=page.locator('#annotation-toolbar').bounding_box()
        assert box['x']>=0 and box['x']+box['width']<=width
        assert box['y']>=0 and box['y']+box['height']<=844
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        if width==390:
            page.screenshot(path=str(OUT/'annotation-selection-mobile.png'))
            apply(page,'comment');page.locator('#annotation-note').fill('手机阅读注释')
            page.screenshot(path=str(OUT/'annotation-editor-mobile.png'))
            page.locator('#annotation-form button[type=submit]').click()
            page.locator('#annotation-preview').wait_for(state='visible')
            library(page);page.screenshot(path=str(OUT/'annotation-library-mobile.png'))
            assert page.locator('#annotation-library').bounding_box()['width']<=width
            close_library(page)
        else: page.locator('#close-annotation-toolbar').click()
    record('Selection toolbar and comment management fit phone, tablet and desktop widths')
    # Cross-chapter selections are rejected without writing data.
    before=saved(page)
    page.evaluate('''()=>{const a=document.querySelector('#chapter-01 .prose p'),b=document.querySelector('#chapter-02 .prose p');
      const r=document.createRange();r.setStart(a,0);r.setEnd(b,1);getSelection().removeAllRanges();getSelection().addRange(r)}''')
    page.wait_for_timeout(200)
    assert not page.locator('#annotation-toolbar').is_visible()
    assert '同一章节' in page.locator('#annotation-status').inner_text()
    assert page.locator('#annotation-feedback').is_visible()
    box=page.locator('#annotation-feedback').bounding_box()
    assert 0<=box['y']<844
    assert saved(page)==before
    record('Cross-chapter selection is rejected with actionable feedback')
    page.evaluate("getSelection().removeAllRanges();const p=document.createElement('p');p.textContent='字'.repeat(5001);document.querySelector('#chapter-01 .prose').append(p);const r=document.createRange();r.selectNodeContents(p);getSelection().addRange(r)")
    page.wait_for_timeout(200)
    assert not page.locator('#annotation-toolbar').is_visible()
    assert '5000' in page.locator('#annotation-feedback').inner_text()
    assert saved(page)==before
    record('Oversized selections show a visible limit message without creating a record')
    # UTF-16 offsets preserve emoji and adjacent CJK text.
    page.evaluate("getSelection().removeAllRanges();const p=document.createElement('p');p.textContent='信息📡与网络连接🙂的关系';document.querySelector('#chapter-01 .prose').append(p);p.id='unicode-fixture'")
    select(page,selector='#unicode-fixture',start=2,end=11);apply(page,'underline')
    assert saved(page)[-1]['quote']=='📡与网络连接🙂'
    assert page.locator('#unicode-fixture').text_content()=='信息📡与网络连接🙂的关系'
    record('UTF-16 positions preserve emoji and Chinese characters without changing the original text')
    assert not errors,errors
    context.close()
    touch=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
    page=touch.new_page();page.goto(URL);select(page)
    box=page.locator('[data-annotation-action=comment]').bounding_box()
    page.touchscreen.tap(box['x']+box['width']/2,box['y']+box['height']/2)
    page.locator('#annotation-note').fill('触屏添加的注释')
    box=page.locator('#annotation-form button[type=submit]').bounding_box()
    page.touchscreen.tap(box['x']+box['width']/2,box['y']+box['height']/2)
    page.locator('#annotation-editor').wait_for(state='hidden')
    assert saved(page)[0]['note']=='触屏添加的注释'
    record('Touch taps open the comment editor and save the selected passage on a phone viewport')
    touch.close()
    gestures=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True,reduced_motion='reduce')
    page=gestures.new_page();page.on('pageerror',lambda error:errors.append(str(error)));page.goto(URL)
    original_gesture=page.locator('#chapter-01 .prose').text_content()
    text=slow_drag(page,'#chapter-01 .prose > p',0,85)
    assert len(text)>50
    apply(page,'wave')
    assert page.locator('#chapter-01 .annotation-wave').count()>0
    assert saved(page)[0]['type']=='wave' and saved(page)[0]['quote']==text
    assert page.locator('.annotation-wave').first.evaluate('el=>getComputedStyle(el).textDecorationStyle')=='wavy'
    record('Slow dragging across lines creates a persisted wavy underline with the exact selected text')
    text=slow_drag(page,'#chapter-01 .prose > p',5,70)
    assert not page.locator('#annotation-preview').is_visible()
    assert len(text)>50
    page.locator('#close-annotation-toolbar').click()
    text=slow_drag(page,'#chapter-01 .prose > p',70,5)
    assert len(text)>50
    page.locator('#close-annotation-toolbar').click()
    text=slow_drag(page,'#chapter-01 .prose > p',0,30,scroll=True)
    assert len(text)>15
    page.locator('#close-annotation-toolbar').click()
    page.locator('#chapter-01 .annotation-wave').first.dblclick()
    page.locator('#annotation-toolbar').wait_for(state='visible')
    assert page.evaluate('getSelection().toString().length')>0
    page.locator('#close-annotation-toolbar').click()
    record('Marked text supports forward and reverse dragging, scrolling during selection, and double-click selection')
    page.reload()
    assert len(saved(page))==1 and saved(page)[0]['type']=='wave'
    page.locator('#chapter-01 .annotation-wave').first.click()
    assert page.locator('[data-annotation-action=wave]').get_attribute('aria-pressed')=='true'
    apply(page,'underline')
    assert len(saved(page))==1 and saved(page)[0]['type']=='underline'
    assert page.locator('.annotation-wave').count()==0
    apply(page,'wave')
    assert len(saved(page))==1 and saved(page)[0]['type']=='wave'
    assert page.locator('.annotation-underline').count()==0
    apply(page,'emphasis');comment(page,'传输介质影响信号传播方式，信息内容通过编码恢复。')
    assert len(saved(page))==3
    assert page.locator('.annotation-wave.annotation-emphasis.annotation-comment').count()>0
    assert page.locator('#chapter-01 .prose').text_content()==original_gesture
    page.emulate_media(media='print')
    assert page.locator('.annotation-wave').first.evaluate('el=>getComputedStyle(el).textDecorationStyle')=='wavy'
    page.emulate_media(media='screen')
    page.screenshot(path=str(OUT/'annotation-wave-desktop.png'))
    record('Wavy underlines survive refresh and print, switch with straight underlines, and combine with emphasis and one comment')
    for width in [320,390,760]:
        page.locator('#close-annotation-toolbar').click()
        page.set_viewport_size({'width':width,'height':844})
        page.locator('#chapter-01 .annotation-wave').first.click()
        bar=page.locator('#annotation-toolbar').bounding_box();sheet=page.locator('#annotation-preview').bounding_box()
        assert bar['x']>=0 and bar['x']+bar['width']<=width
        assert bar['y']>=0 and bar['y']+bar['height']<=sheet['y']
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        if width==390:page.screenshot(path=str(OUT/'annotation-wave-mobile.png'))
    library(page)
    with page.expect_download() as download_event:page.locator('#export-annotations').click()
    wave_export=OUT/'annotations-wave-export.json';download_event.value.save_as(str(wave_export))
    exported_wave=json.loads(wave_export.read_text())
    assert any(a['type']=='wave' for a in exported_wave['annotations'])
    conflicting=next(a.copy() for a in exported_wave['annotations'] if a['type']=='wave')
    conflicting.update(id='imported-straight',type='underline',createdAt='2099-01-01T00:00:00Z')
    before_conflict=saved(page)
    page.locator('#annotation-file').set_input_files({'name':'straight.json','mimeType':'application/json','buffer':json.dumps({'version':1,'annotations':[conflicting]}).encode()})
    page.wait_for_function("document.querySelector('#annotation-library-status').textContent.includes('已导入 0')")
    assert saved(page)==before_conflict
    assert page.locator('.annotation-wave').count()>0 and page.locator('.annotation-underline').count()==0
    record('Importing another underline style on the same range preserves the current style and reports zero new records')
    close_library(page)
    page.locator('#chapter-01 .annotation-wave').first.click();apply(page,'wave')
    assert page.locator('.annotation-wave').count()==0
    assert page.locator('.annotation-emphasis.annotation-comment').count()>0
    library(page);page.locator('#annotation-file').set_input_files(str(wave_export))
    page.wait_for_function("document.querySelector('#annotation-library-status').textContent.includes('已导入 1')")
    assert page.locator('.annotation-wave').count()>0
    record('The wave action fits narrow screens, exports and imports correctly, and can be removed without deleting the comment')
    # Narrow screens with both scope selection and four annotation actions.
    close_library(page);select(page,selector='> p',start=0,end=12);apply(page,'underline')
    page.set_viewport_size({'width':320,'height':844})
    page.locator('#chapter-01 .annotation-underline.annotation-wave').first.click()
    assert page.locator('#annotation-target').is_visible()
    bar=page.locator('#annotation-toolbar').bounding_box();sheet=page.locator('#annotation-preview').bounding_box()
    assert bar['width']<=320 and bar['y']+bar['height']<=sheet['y']
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    record('Scope selection and all four annotation actions remain usable at 320px without covering the comment')
    gestures.close()
    # Inline interaction uses the same toolbar for clicks and selections.
    inline=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='reduce')
    page=inline.new_page();page.on('pageerror',lambda error:errors.append(str(error)));page.goto(URL)
    select(page,end=30);apply(page,'underline')
    page.locator('#chapter-01 .annotation-mark').first.click()
    page.wait_for_timeout(200)
    assert page.locator('#annotation-toolbar').is_visible()
    assert not page.locator('#annotation-preview').is_visible()
    assert not page.locator('#annotation-library').is_visible()
    assert page.locator('[data-annotation-action=underline]').get_attribute('aria-pressed')=='true'
    apply(page,'underline')
    assert page.locator('#annotation-toolbar').is_visible()
    assert len(saved(page))==0
    apply(page,'underline')
    apply(page,'emphasis')
    assert page.locator('[data-annotation-action=emphasis]').get_attribute('aria-pressed')=='true'
    apply(page,'underline')
    assert page.locator('#chapter-01 .annotation-underline').count()==0
    assert page.locator('#chapter-01 .annotation-emphasis').count()>0
    record('Clicking a mark opens the shared toolbar and independently toggles existing underline and emphasis')
    comment(page,'信息描述内容，信号承担物理传递。')
    assert len(saved(page))==2
    page.locator('#chapter-01 .annotation-comment').first.click()
    page.locator('#annotation-preview').wait_for(state='visible')
    assert page.locator('#annotation-preview-note').inner_text()=='信息描述内容，信号承担物理传递。'
    assert not page.locator('#annotation-library').is_visible()
    bar=page.locator('#annotation-toolbar').bounding_box();sheet=page.locator('#annotation-preview').bounding_box()
    assert bar['y']+bar['height']<=sheet['y']
    page.screenshot(path=str(OUT/'annotation-click-desktop.png'))
    page.locator('#close-annotation-preview').focus()
    page.keyboard.press('Tab')
    assert page.locator('#edit-annotation-preview').evaluate('el=>el===document.activeElement')
    page.keyboard.press('Tab')
    assert page.locator('#delete-annotation-preview').evaluate('el=>el===document.activeElement')
    page.evaluate("const r=document.createRange();r.selectNodeContents(document.querySelector('#annotation-preview-note'));getSelection().removeAllRanges();getSelection().addRange(r)")
    page.wait_for_timeout(150)
    assert page.locator('#annotation-preview').is_visible()
    page.evaluate('getSelection().removeAllRanges()')
    record('The bottom comment supports normal Tab navigation and copying its text without dismissing the panel')
    page.locator('#edit-annotation-preview').click();page.locator('#annotation-note').fill('取消编辑的文字')
    page.get_by_role('button',name='取消',exact=True).click()
    page.locator('#annotation-preview').wait_for(state='visible')
    assert page.locator('#annotation-preview-note').inner_text()=='信息描述内容，信号承担物理传递。'
    page.locator('#edit-annotation-preview').click();page.locator('#annotation-note').fill('区分信息内容与物理信号，再理解传输介质的作用。')
    page.locator('#annotation-form button[type=submit]').click()
    page.locator('#annotation-preview').wait_for(state='visible')
    assert page.locator('#annotation-preview-note').inner_text()=='区分信息内容与物理信号，再理解传输介质的作用。'
    select(page,end=30);apply(page,'comment')
    assert page.locator('#annotation-editor-title').inner_text()=='编辑注释'
    assert page.locator('#annotation-note').input_value()=='区分信息内容与物理信号，再理解传输介质的作用。'
    page.locator('#annotation-note').fill('同一业务可以经过不同介质，逐段验证连接状态。')
    page.locator('#annotation-form button[type=submit]').click();page.locator('#annotation-preview').wait_for(state='visible')
    assert len([a for a in saved(page) if a['type']=='comment'])==1
    record('The bottom comment can be edited or cancelled; reselecting the same passage edits its single existing comment')
    for width in [390,760,1024,1440]:
        page.locator('#close-annotation-toolbar').click()
        page.set_viewport_size({'width':width,'height':844})
        page.locator('#chapter-01 .annotation-comment').first.click()
        page.locator('#annotation-preview').wait_for(state='visible')
        bar=page.locator('#annotation-toolbar').bounding_box();sheet=page.locator('#annotation-preview').bounding_box()
        assert bar['y']>=0 and bar['y']+bar['height']<=sheet['y']
        assert sheet['x']>=0 and sheet['x']+sheet['width']<=width and sheet['y']+sheet['height']<=844
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        if width==390:
            page.screenshot(path=str(OUT/'annotation-click-mobile.png'))
            page.locator('#edit-annotation-preview').click()
            page.screenshot(path=str(OUT/'annotation-bottom-editor-mobile.png'))
            page.keyboard.press('Escape');page.locator('#annotation-preview').wait_for(state='visible')
    record('The click toolbar and bottom comment remain visible without overlap at phone, tablet and desktop widths')
    page.keyboard.press('Escape')
    assert not page.locator('#annotation-preview').is_visible() and not page.locator('#annotation-toolbar').is_visible()
    page.locator('#chapter-01 .annotation-comment').first.click();page.locator('#annotation-preview').wait_for(state='visible')
    page.locator('#delete-annotation-preview').click()
    assert not page.locator('#annotation-preview').is_visible()
    assert len(saved(page))==1 and saved(page)[0]['type']=='emphasis'
    assert page.locator('[data-annotation-action=comment]').get_attribute('aria-pressed')=='false'
    comment(page,'跨介质链路需要逐段核查输入与输出。')
    sample=saved(page)
    page.reload()
    page.locator('#chapter-01 .annotation-comment').first.click();page.locator('#annotation-preview').wait_for(state='visible')
    assert page.locator('#annotation-preview-note').inner_text()=='跨介质链路需要逐段核查输入与输出。'
    page.locator('#chapter-01 h2').click()
    assert not page.locator('#annotation-preview').is_visible() and not page.locator('#annotation-toolbar').is_visible()
    record('Escape and outside clicks dismiss the controls; deleting the comment keeps emphasis, and refresh restores the single note')
    # Differently sized overlapping annotations expose their exact scope in the shared toolbar.
    select(page,start=0,end=12);apply(page,'underline')
    select(page,start=0,end=30);apply(page,'emphasis')  # toggle off the existing emphasis
    page.locator('#chapter-01 .annotation-underline.annotation-comment').first.click()
    assert page.locator('#annotation-target').is_visible()
    assert page.locator('[data-annotation-action=underline]').get_attribute('aria-pressed')=='true'
    assert page.locator('#annotation-preview-note').inner_text()=='跨介质链路需要逐段核查输入与输出。'
    larger=next(a for a in saved(page) if a['type']=='comment')
    page.locator('#annotation-target').select_option(larger['id'])
    assert page.locator('[data-annotation-action=underline]').get_attribute('aria-pressed')=='false'
    assert page.locator('[data-annotation-action=comment]').get_attribute('aria-pressed')=='true'
    page.set_viewport_size({'width':390,'height':844})
    page.locator('#close-annotation-toolbar').click()
    page.locator('#chapter-01 .annotation-underline.annotation-comment').first.click()
    bar=page.locator('#annotation-toolbar').bounding_box();sheet=page.locator('#annotation-preview').bounding_box()
    assert bar['width']<=390 and bar['y']+bar['height']<=sheet['y']
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    heights=page.locator('#annotation-toolbar [data-annotation-action]').evaluate_all('els=>els.map(el=>el.getBoundingClientRect().height)')
    assert max(heights)==min(heights)==44
    page.screenshot(path=str(OUT/'annotation-overlap-mobile.png'))
    record('Overlapping ranges default to the smallest selection and can switch scope while keeping the associated comment visible')
    inline.close()
    # Legacy comments on an identical anchor retain all distinct note text in one record.
    legacy=json.loads(json.dumps(sample));copy=next(a for a in legacy if a['type']=='comment').copy()
    copy['id']='legacy-copy';copy['note']='以前保存的另一段注释';copy['createdAt']='2026-10-01T00:00:00Z';legacy.append(copy)
    migration=browser.new_context()
    migration.add_init_script('localStorage.setItem('+json.dumps(KEY)+', '+json.dumps(json.dumps({'version':1,'annotations':legacy}))+')')
    page=migration.new_page();page.goto(URL)
    migrated=saved(page);notes=[a for a in migrated if a['type']=='comment']
    assert len(notes)==1 and '以前保存的另一段注释' in notes[0]['note'] and '跨介质链路需要逐段核查输入与输出。' in notes[0]['note']
    page.reload();assert len([a for a in saved(page) if a['type']=='comment'])==1
    library(page)
    page.locator('#annotation-file').set_input_files({'name':'legacy.json','mimeType':'application/json','buffer':json.dumps({'version':1,'annotations':legacy}).encode()})
    page.wait_for_function("document.querySelector('#annotation-library-status').textContent.includes('已导入 0')")
    assert len([a for a in saved(page) if a['type']=='comment'])==1
    record('Legacy duplicate comments consolidate without losing text; repeated imports preserve one current comment')
    migration.close()
    # Import on an empty browser, then simulate updated source content before app initialization.
    fresh=browser.new_context()
    page=fresh.new_page();page.goto(URL);library(page)
    page.locator('#annotation-file').set_input_files(str(export_path))
    page.wait_for_function("document.querySelector('#annotation-count').textContent!=='0'")
    assert len(saved(page))==len(exported['annotations'])
    assert page.locator('.annotation-mark').count()>0
    record('Exported annotations merge into a fresh browser and render against the course')
    fresh.close()
    shifted=browser.new_context()
    shifted.add_init_script('''(({key,data})=>{
      localStorage.setItem(key,JSON.stringify(data));
      new MutationObserver((changes,observer)=>{
        const root=document.querySelector('#chapter-01 .prose');
        if(root && root.querySelector('p')){root.prepend(document.createTextNode('新增的导读段落。'));observer.disconnect();}
      }).observe(document,{childList:true,subtree:true});
    })(''' + json.dumps({'key':KEY,'data':exported}) + ')')
    page=shifted.new_page();page.goto(URL)
    target=exported['annotations'][0]
    assert page.locator(f'[data-annotation-ids~="{target["id"]}"]').all_text_contents()
    assert ''.join(page.locator(f'[data-annotation-ids~="{target["id"]}"]').all_text_contents())==target['quote']
    record('Quote and surrounding context restore anchors after text is inserted before the original passage')
    shifted.close()
    ambiguous=browser.new_context()
    ambiguous_quote='重复摘录示例'
    fake={'id':'ambiguous','chapter':'chapter-01','start':99999,'end':99999+len(ambiguous_quote),'quote':ambiguous_quote,'prefix':'missing','suffix':'missing','type':'comment','note':'保留的笔记','createdAt':'2026-10-02T00:00:00Z'}
    # Explicit duplicate excerpts keep this scenario independent of editorial changes.
    ambiguous.add_init_script('''(({key,data,quote})=>{
      localStorage.setItem(key,JSON.stringify(data));
      new MutationObserver((changes,observer)=>{
        const root=document.querySelector('#chapter-01 .prose');
        if(root && root.querySelector('p')){
          observer.disconnect();
          const fixture=document.createElement('p');
          fixture.textContent=quote+'；'+quote;
          root.prepend(fixture);
        }
      }).observe(document,{childList:true,subtree:true});
    })(''' + json.dumps({'key':KEY,'data':{'version':1,'annotations':[fake]},'quote':ambiguous_quote}) + ')')
    page=ambiguous.new_page();page.goto(URL);library(page)
    assert page.locator('.annotation-unresolved').count()==1
    assert page.locator('.annotation-card-note').inner_text()=='保留的笔记'
    assert page.locator('.annotation-mark').count()==0
    record('Ambiguous anchors preserve the original excerpt and comment for review')
    ambiguous.close()
    blocked=browser.new_context()
    blocked.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('Unavailable')}})")
    page=blocked.new_page();page.goto(URL);select(page);apply(page,'underline')
    assert page.locator('.annotation-underline').count()>0
    assert '尚未保存' in page.locator('#annotation-status').inner_text()
    library(page)
    with page.expect_download() as download_event:page.locator('#export-annotations').click()
    downloaded=download_event.value.path()
    assert len(json.loads(Path(downloaded).read_text())['annotations'])==1
    close_library(page)
    select(page);comment(page,'本页临时注释')
    page.locator('#delete-annotation-preview').click()
    assert '尚未保存' in page.locator('#annotation-feedback').inner_text()
    assert '导出' in page.locator('#annotation-feedback').inner_text()
    library(page)
    page.locator('.annotation-card').get_by_role('button',name='删除',exact=True).click()
    assert '尚未保存' in page.locator('#annotation-library-status').inner_text()
    record('With storage unavailable, current-page annotation and export remain usable; deletion retains the unsaved warning')
    blocked.close()
    broken=browser.new_context();broken.add_init_script("localStorage.setItem('telecom-course-annotations-v1','{broken')")
    page=broken.new_page();page.goto(URL);select(page);apply(page,'emphasis')
    assert len(saved(page))==1
    record('Malformed saved annotation data does not block reading or creating new annotations')
    broken.close();browser.close()
(OUT/'annotation-results.json').write_text(json.dumps({'checks':results,'browser_errors':errors},ensure_ascii=False,indent=2))
print(f'Completed {len(results)} annotation checks. Evidence: {OUT}')
