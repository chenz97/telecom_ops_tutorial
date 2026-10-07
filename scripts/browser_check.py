#!/usr/bin/env python3
"""Exercise the offline reader and save layout evidence."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'execution' / 'qa'
OUT.mkdir(parents=True, exist_ok=True)
URL = (ROOT / 'index.html').as_uri()
ANSWER_COUNT = (ROOT / 'course' / 'tutorial.md').read_text().count('<details>')
results = []

def record(message):
    results.append(message)
    print('PASS:', message)

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={'width':1440, 'height':1000}, device_scale_factor=1, reduced_motion='reduce')
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(URL)
    assert page.locator('.chapter').count() == 24
    assert page.locator('.prose details').count() == ANSWER_COUNT
    assert '**' not in page.locator('.chapters').inner_text()
    page.screenshot(path=str(OUT / 'desktop-home.png'))
    record(f'Offline page opens with 24 chapters and {ANSWER_COUNT} answer blocks')
    page.locator('#search').fill('光纤')
    assert 0 < page.locator('.chapter:visible').count() < 24
    assert page.locator('#search-status').inner_text().endswith('个章节')
    page.locator('#search').fill('NO_MATCH_7e091')
    assert page.locator('.chapter:visible').count() == 0
    assert page.locator('#no-results').is_visible()
    page.locator('#restore').click()
    assert page.locator('.chapter:visible').count() == 24
    record('Search filters text, reports no matches, and restores all chapters')
    page.locator('[data-complete="chapter-00"]').click()
    assert page.locator('#progress-label').inner_text() == '1 / 24'
    page.reload()
    assert page.locator('[data-complete="chapter-00"]').get_attribute('aria-pressed') == 'true'
    assert page.locator('#progress-label').inner_text() == '1 / 24'
    page.locator('#reset-progress').click()
    assert page.locator('#progress-label').inner_text() == '0 / 24'
    page.reload()
    assert page.locator('#progress-label').inner_text() == '0 / 24'
    record('Completion survives reload, and reset clears saved progress')
    page.locator('#font-size').select_option('larger')
    assert page.locator('#chapter-04 .prose').evaluate('(el)=>getComputedStyle(el).fontSize') == '21px'
    page.reload()
    assert page.locator('#font-size').input_value() == 'larger'
    page.locator('#font-size').select_option('standard')
    record('Font preference applies and survives reload')
    page.locator('#chapter-04').evaluate('(el)=>el.scrollIntoView()')
    page.wait_for_timeout(150)
    page.screenshot(path=str(OUT / 'desktop-broadband.png'))
    answer = page.locator('#chapter-04 details').first
    answer.locator('summary').click()
    assert answer.get_attribute('open') is not None
    record('Practice answers expand')
    page.locator('#search').fill('NO_MATCH_7e091')
    page.locator('a[href="#chapter-00"]').first.evaluate('(el)=>el.click()')
    assert page.locator('.chapter:visible').count() == 24
    record('Chapter navigation restores a target hidden by search')
    page.locator('#search').fill('NO_MATCH_7e091')
    page.emulate_media(media='print')
    page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
    assert page.locator('.chapter:visible').count() == 24
    assert page.locator('.prose details:not([open])').count() == 0
    assert not page.locator('.sidebar').is_visible()
    page.screenshot(path=str(OUT / 'print-preview.png'))
    page.evaluate("window.dispatchEvent(new Event('afterprint'))")
    page.emulate_media(media='screen')
    page.locator('#clear-search').click()
    record('Print mode includes filtered chapters and all answers, and hides reading controls')
    for width in [390, 760, 1024, 1440]:
        page.set_viewport_size({'width':width, 'height':900})
        page.goto(URL)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow at {width}'
        record(f'No page-level horizontal overflow at {width}px')
    page.set_viewport_size({'width':390, 'height':844})
    page.goto(URL)
    assert page.locator('.course-menu').get_attribute('open') is None
    page.screenshot(path=str(OUT / 'mobile-home.png'))
    page.locator('.course-menu summary').click()
    assert page.locator('.course-menu').get_attribute('open') is not None
    page.locator('.toc-link[href="#chapter-04"]').click()
    page.wait_for_timeout(400)
    assert 0 <= page.locator('#chapter-04').bounding_box()['y'] <= 40, page.locator('#chapter-04').bounding_box()
    assert page.locator('.course-menu').get_attribute('open') is None
    assert page.evaluate('location.hash') == '#chapter-04'
    page.screenshot(path=str(OUT / 'mobile-broadband.png'))
    record('Mobile directory expands, navigates, then collapses')
    page.goto(URL + '#chapter-21')
    page.locator('#chapter-21').evaluate('(el)=>el.scrollIntoView()')
    page.wait_for_timeout(200)
    page.screenshot(path=str(OUT / 'mobile-cases.png'))
    for width, heading, filename in [
        (1440, 'PPPoE 上线：从物理连通到用户会话', 'desktop-pppoe.png'),
        (390, 'PON 怎样让多户共享一段光纤', 'mobile-optical-budget.png'),
        (390, '为什么平均利用率较低也会丢包', 'mobile-queue-analysis.png'),
        (1440, '案例一：医院专线从需求到退网', 'desktop-vpn-case.png'),
    ]:
        page.set_viewport_size({'width': width, 'height': 1100})
        page.get_by_role('heading', name=heading, exact=True).evaluate('(el)=>el.scrollIntoView()')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(OUT / filename))
    page.set_viewport_size({'width': 1100, 'height': 1100})
    page.get_by_role('heading', name='把时延拆成可以计算的部分', exact=True).evaluate('(el)=>el.scrollIntoView()')
    page.emulate_media(media='print')
    page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
    page.get_by_role('heading', name='把时延拆成可以计算的部分', exact=True).evaluate('(el)=>el.scrollIntoView()')
    page.screenshot(path=str(OUT / 'print-delay-analysis.png'))
    page.evaluate("window.dispatchEvent(new Event('afterprint'))")
    page.emulate_media(media='screen')
    record('Expanded protocol tables, numerical analysis and cases render at desktop, mobile and print widths')
    assert not errors, errors
    record('No browser JavaScript errors')
    context.close()
    blocked = browser.new_context(viewport={'width':1280,'height':900})
    blocked.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('Storage unavailable')}})")
    page = blocked.new_page()
    page.goto(URL)
    page.locator('[data-complete="chapter-00"]').click()
    assert page.locator('#progress-label').inner_text() == '1 / 24'
    assert '未保存' in page.locator('#storage-note').inner_text()
    page.locator('#search').fill('光纤')
    assert page.locator('.chapter:visible').count() > 0
    record('Reading, search and completion work when browser storage is unavailable')
    blocked.close()
    malformed = browser.new_context()
    malformed.add_init_script("localStorage.setItem('telecom-course-progress-v1','{broken')")
    page = malformed.new_page()
    page.goto(URL)
    assert page.locator('#progress-label').inner_text() == '0 / 24'
    record('Malformed saved progress recovers to a readable course')
    malformed.close()
    nojs = browser.new_context(java_script_enabled=False, viewport={'width':390,'height':844})
    page = nojs.new_page()
    page.goto(URL)
    assert page.locator('.chapter:visible').count() == 24
    assert not page.locator('#search').is_visible()
    assert page.locator('.course-menu').get_attribute('open') is not None
    page.locator('#chapter-01 summary').first.click()
    assert page.locator('#chapter-01 details').first.get_attribute('open') is not None
    record('Without JavaScript, all chapters, navigation and answer disclosure remain readable')
    nojs.close()
    browser.close()
(OUT / 'results.json').write_text(json.dumps({'checks':results,'browser_errors':errors}, ensure_ascii=False, indent=2))
print(f'Completed {len(results)} browser checks. Evidence: {OUT}')
