#!/usr/bin/env python3
"""Offline About-page layout / code regression checks using the BUILT website.

Optional QA dependencies: playwright, beautifulsoup4; a Chromium binary.
  python3 scripts/check_about_render.py --chromium /usr/bin/chromium
  python3 scripts/check_about_render.py --screenshots /tmp/nift-about-review

This loads actual local HTML/CSS/JS/image bytes into a blank browser document;
no network access is needed. A small in-memory localStorage fixture supports
our theme UI on the blank document. It tests rendering, not file/HTTP origin
security, persistent storage, or the remote syntax-highlighting CDN.
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import shutil
from pathlib import Path
from urllib.parse import unquote, urlsplit

EXPECTED = """@for(post in posts) {
  <article>
    <h2>$[post.title]</h2>
    <p>$[post.excerpt]</p>
  </article>
}"""
WIDTHS = (1440, 1280, 1100, 1024, 901, 900, 768, 541, 540, 390, 320)
ROOT = Path(__file__).resolve().parent.parent


def embedded_page(public: Path, relative: str, theme: str) -> str:
    from bs4 import BeautifulSoup

    page = public / relative
    soup = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
    # Resolve links for the existing navigation script without navigating.
    base = soup.new_tag('base', href='https://nift.test/' + relative)
    soup.head.insert(0, base)
    init = soup.new_tag('script')
    init.string = """(() => {
      const data = {'nift-theme': THEME};
      Object.defineProperty(window, 'localStorage', {configurable:true, value:{
        getItem:k=>data[k]??null, setItem:(k,v)=>data[k]=String(v),
        removeItem:k=>delete data[k],
        clear:()=>Object.keys(data).forEach(k=>delete data[k])
      }});
    })();""".replace('THEME', json.dumps(theme))
    soup.head.insert(0, init)

    def local(uri: str) -> Path:
        parts = urlsplit(uri)
        if parts.scheme or parts.netloc:
            raise AssertionError(f'Unexpected external QA asset: {uri}')
        path = unquote(parts.path)
        result = (public / path.lstrip('/') if path.startswith('/') else page.parent / path).resolve()
        assert result.is_relative_to(public.resolve()), f'Asset outside public/: {result}'
        assert result.is_file(), f'Missing asset: {result}'
        return result

    for link in list(soup.find_all('link')):
        if 'stylesheet' in link.get('rel', []):
            style = soup.new_tag('style')
            style.string = local(link['href']).read_text(encoding='utf-8')
            link.replace_with(style)
        else:
            link.decompose()
    for image in soup.find_all('img'):
        path = local(image['src'])
        image['src'] = 'data:' + (mimetypes.guess_type(path)[0] or 'application/octet-stream') + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')
        image['loading'] = 'eager'
    for script in soup.find_all('script', src=True):
        text = local(script['src']).read_text(encoding='utf-8')
        script.attrs = {}
        script.string = text.replace('</script', '<\\/script')
    return str(soup)


LAYOUT_CHECK = r"""() => {
  const errors = [];
  const fail = m => errors.push(m);
  const rect = e => e.getBoundingClientRect();
  const within = (a,b) => a.left>=b.left-.7 && a.right<=b.right+.7 && a.top>=b.top-.7 && a.bottom<=b.bottom+.7;
  if (document.documentElement.scrollWidth > innerWidth+1) fail('horizontal page overflow');
  const cards = [...document.querySelectorAll('.about-capability-card')];
  if (cards.length !== 10) fail('expected ten capability cards');
  cards.forEach((card,i) => {
    const copy = card.querySelector('.about-card-copy');
    const art = card.querySelector('.about-card-art');
    if (!copy || !art) {fail(`card ${i}: missing dedicated copy/art columns`);return;}
    const c=rect(copy), a=rect(art), outer=rect(card);
    if (!(a.left>=c.right-.7 || a.top>=c.bottom-.7)) fail(`card ${i}: copy/art overlap`);
    if (!within(c,outer) || !within(a,outer)) fail(`card ${i}: content outside card`);
    if (copy.scrollWidth>copy.clientWidth+1) fail(`card ${i}: overflowing text`);
    if (getComputedStyle(card).borderRightWidth!=='1px') fail(`card ${i}: border not 1px`);
    for (const pseudo of ['::before','::after']) {
      const content=getComputedStyle(card,pseudo).content;
      if (content!=='none' && content!=='normal') fail(`card ${i}: unexpected overlay ${pseudo}`);
    }
  });
  const images=[...document.querySelectorAll('.about-poster-page img')];
  if (images.length!==12) fail('expected twelve illustrations');
  images.forEach((im,i) => {
    if (!im.complete || !im.naturalWidth) fail(`image ${i}: failed to load`);
    if (getComputedStyle(im).objectFit!=='contain') fail(`image ${i}: potentially cropped`);
    if (getComputedStyle(im).borderRightWidth!=='0px') fail(`image ${i}: second CSS border`);
    if (!within(rect(im),rect(im.parentElement))) fail(`image ${i}: outside its own column`);
    if (im.closest('.about-card-copy')) fail(`image ${i}: inside copy`);
  });
  document.querySelectorAll('.about-art-frame').forEach(frame => {
    const image=rect(frame.querySelector('img'));
    frame.querySelectorAll('span').forEach(label => {
      if(!within(rect(label),image)) fail('HTML artwork label outside its image');
    });
  });
  const panel=document.querySelector('.about-code-panel');
  const code=panel.querySelector('pre code');
  if (!code || panel.querySelectorAll('pre code').length!==1) fail('not one semantic code block');
  if (code) {
    if (getComputedStyle(code).backgroundColor!=='rgba(0, 0, 0, 0)') fail('code inherits inline chip background');
    if (getComputedStyle(code).borderTopWidth!=='0px') fail('code inherits inline chip border');
  }
  if (getComputedStyle(panel).backgroundColor!=='rgb(24, 24, 22)') fail('non-neutral About code panel');
  const button=panel.querySelector('.code-copy-button');
  if (!button || !within(rect(button),rect(panel))) fail('copy button missing or outside panel');
  if (document.querySelector('.about-card-art svg,.about-hero-art svg,.about-closing-art svg')) fail('SVG substituted for raster artwork');
  return errors;
}"""


CODE_BACKDROPS = r"""() => [...document.querySelectorAll('pre')].filter(pre=>pre.getClientRects().length).map(pre => {
  let el=pre;
  while(el) {
    const color=getComputedStyle(el).backgroundColor;
    const channels=(color.match(/[\d.]+/g)||[]).map(Number);
    if (channels.length===3 || (channels.length===4 && channels[3]>.99)) return {tag:pre.className, color,channels};
    el=el.parentElement;
  }
  return {tag:pre.className,color:'transparent',channels:[]};
})"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public', type=Path, default=ROOT / 'public')
    parser.add_argument('--chromium', default=shutil.which('chromium') or shutil.which('chromium-browser'))
    parser.add_argument('--screenshots', type=Path)
    args = parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
        from bs4 import BeautifulSoup
    except ImportError as exc:
        parser.error(f'Optional render-test dependency missing: {exc}. Install playwright and beautifulsoup4 in your QA environment.')

    source = BeautifulSoup((args.public / 'about.html').read_text(encoding='utf-8'), 'html.parser')
    raw = source.select_one('[data-about-template]')
    assert raw and raw.get_text() == EXPECTED, 'Built code differs from the literal six-line example'
    about_icon = source.select_one('link[rel="icon"]')['href']
    examples = BeautifulSoup((args.public / 'examples.html').read_text(encoding='utf-8'), 'html.parser')
    assert about_icon == examples.select_one('link[rel="icon"]')['href'], 'About has a different favicon'
    for img in source.select('.about-poster-page img'):
        assert img.get('width') and img.get('height'), 'Image has no intrinsic dimensions'
        assert img['src'].endswith('.webp'), 'Illustration is not a raster WebP'
    if args.screenshots:
        args.screenshots.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        opts = {'args': ['--no-sandbox']}
        if args.chromium:
            opts['executable_path'] = args.chromium
        browser = pw.chromium.launch(**opts)
        checks = 0
        for theme in ('dark', 'light'):
            ctx = browser.new_context(viewport={'width':1440,'height':1000}, color_scheme=theme)
            ctx.route('**/*', lambda route: route.abort())
            page = ctx.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.set_content(embedded_page(args.public, 'about.html', theme))
            page.wait_for_function("[...document.images].every(im=>im.complete)")
            assert page.locator('[data-about-template]').text_content() == EXPECTED
            assert page.locator('[data-about-template] .about-token-directive').count() == 1
            assert page.locator('[data-about-template] .about-token-tag').count() == 6
            assert page.locator('[data-about-template] .about-token-value').count() == 2
            for width in WIDTHS:
                page.set_viewport_size({'width':width,'height':1000})
                failures = page.evaluate(LAYOUT_CHECK)
                assert not failures, f'{theme} / {width}px: {failures}'
                checks += 1
                if args.screenshots and theme == 'dark' and width in (1440,900,390):
                    page.screenshot(path=str(args.screenshots / f'about-{width}.png'), full_page=True)
            # Exercise the shared theme/menu wiring with the actual site script.
            page.set_viewport_size({'width':390,'height':900})
            page.locator('[data-menu-toggle]').click()
            assert page.locator('[data-menu-toggle]').get_attribute('aria-expanded') == 'true'
            page.locator('[data-menu-toggle]').click()
            assert page.locator('[data-menu-toggle]').get_attribute('aria-expanded') == 'false'
            page.set_viewport_size({'width':1440,'height':1000})
            opposite='light' if theme=='dark' else 'dark'
            page.locator(f'.desktop-theme-switcher [data-theme-choice="{opposite}"]').click()
            assert page.locator('html').get_attribute('data-theme') == opposite
            assert not page.evaluate(LAYOUT_CHECK)
            # Inspect the exact copy payload without depending on the host clipboard.
            page.evaluate("""() => {document.execCommand = command => {
              if(command==='copy'){window.__aboutCopied=document.querySelector('textarea[readonly]').value;return true;}
              return false;
            };}""")
            page.locator('.about-code-panel .code-copy-button').click()
            assert page.evaluate('window.__aboutCopied') == EXPECTED, 'Copy includes line numbers, captions or HTML token tags'
            if args.screenshots and theme == 'dark':
                page.locator('.about-code-panel').screenshot(path=str(args.screenshots / 'about-code.png'))
            assert not errors, errors
            ctx.close()

        ctx = browser.new_context(viewport={'width':1440,'height':1100}, color_scheme='dark')
        ctx.route('**/*', lambda route: route.abort())
        page = ctx.new_page()
        for relative in ('docs/lambdas-closures.html','docs/getting-started.html','examples.html','index.html'):
            page.set_content(embedded_page(args.public, relative, 'dark'))
            for sample in page.evaluate(CODE_BACKDROPS):
                rgb=sample['channels'][:3]
                assert len(rgb)==3 and rgb[0]==rgb[1] and rgb[2]<=rgb[0] and max(rgb)-min(rgb)<=5, (relative,sample)
            if args.screenshots and relative=='docs/lambdas-closures.html':
                page.screenshot(path=str(args.screenshots / 'docs-code-charcoal.png'))
        ctx.close()
        browser.close()
    print(f'check-about-render passed: {checks} width/theme layouts, 12 raster assets, literal code + copy, menu/theme controls, 4 dark code surfaces')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
