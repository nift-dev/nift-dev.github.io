#!/usr/bin/env python3
"""Validate tracked transformation routes, canonical mirrors and shared navigation."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re
from check_canonical_display import check, CANONICAL_PAGES
ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'public'
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.references=[];self.navs=[];self.in_nav=False;self.current=None;self.metadata={};self.description_count=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        for key in ('href','src'):
            if key in a:self.references.append(a[key])
        if tag=='nav' and a.get('aria-label')=='Documentation navigation':self.in_nav=True;self.navs.append([])
        if tag=='a' and self.in_nav:self.current=[a.get('href',''),''];self.navs[-1].append(self.current)
        if tag=='meta' and 'name' in a:
            self.metadata[a['name']]=a.get('content','')
            if a['name']=='description':self.description_count+=1
    def handle_data(self,data):
        if self.current is not None:self.current[1]+=data
    def handle_endtag(self,tag):
        if tag=='a':self.current=None
        if tag=='nav':self.in_nav=False
routes=json.loads((ROOT/'.nift/tracked.json').read_text())['tracked']
names={r['name'] for r in routes}
expected=['Migrations','Rewrites','Redesigns']
slugs=['existing-sites','rewrites','redesigns']
metadata=[]
for slug in slugs:
    assert 'docs/'+slug in names, slug
    p=Page();p.feed((PUBLIC/'docs'/(slug+'.html')).read_text())
    assert len(p.navs)==2, 'desktop/mobile shared navigation missing'
    for nav in p.navs:
        labels=[a[1] for a in nav];start=labels.index('Migrations');assert labels[start:start+3]==expected
        assert [a[0] for a in nav[start:start+3]]==['./'+s+'.html' for s in slugs]
    assert p.description_count==1, 'duplicate description tags'
    description=p.metadata['description']
    assert description.startswith(('Faithfully move' if slug=='existing-sites' else 'Rebuild the same' if slug=='rewrites' else 'Use existing requirements')), description
    metadata.append(description)
assert len(set(metadata))==3,'duplicate mode descriptions'
script=(PUBLIC/'assets/js/script.js').read_text()
assert "link.setAttribute('aria-current', 'page')" in script
assert 'if (path === currentPath)' in script
assert "event.key === 'Escape'" in script
assert all(check(CANONICAL_PAGES[name],name) for name in CANONICAL_PAGES)
for name in ('MIGRATION','REWRITE','REDESIGN','HANDOVER'):
    assert (PUBLIC/(name+'.md')).read_bytes()==(ROOT.parent/'nift/tests/fixtures'/(name+'.md')).read_bytes(), name
# Entire tracked publication: concrete internal targets must resolve. External
# URLs and dynamic query/fragment semantics are outside this filesystem check.
broken=[];count=0
for route in routes:
    ext=route.get('output-ext','.html')
    if ext!='.html':continue
    name=route['name'];path=PUBLIC/('index.html' if name=='/' else name+'.html')
    if not path.exists():continue
    source=path.read_text()
    head=source.split('</head>',1)[0]
    assert '@else' not in head and '@if(name' not in head, 'unevaluated head directive'
    p=Page();p.feed(source)
    if '<meta name="application-name"' in head:
        assert p.description_count==1, f'duplicate page metadata: {path} ({p.description_count})'
    for ref in p.references:
        u=urlsplit(ref)
        if u.scheme or u.netloc or not u.path:continue
        target=(PUBLIC/unquote(u.path.lstrip('/'))) if u.path.startswith('/') else path.parent/unquote(u.path)
        if target.is_dir():target=target/'index.html'
        count+=1
        if not target.exists():broken.append((str(path.relative_to(PUBLIC)),ref))
assert not broken, broken
print(f'PASS: transformation routes, metadata, two menus, canonical identity and {count} local references')
