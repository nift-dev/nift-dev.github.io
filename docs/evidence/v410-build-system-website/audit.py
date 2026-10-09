from pathlib import Path
import re,json,collections,zipfile,html
root=Path('/home/nick/Repositories/nift/nift-dev.github.io');out=root/'docs/evidence/v410-build-system-website';out.mkdir(parents=True,exist_ok=True)
menu=(root/'templates/partials/docs-sidebar.html').read_text();inbound=collections.defaultdict(set)
for folder in ['content','templates']:
 for source in (root/folder).rglob('*.html'):
  for target in re.findall(r"@path\(['\"]([^'\"]+)['\"]\)",source.read_text()):inbound[target].add(str(source.relative_to(root)))
sitemap=(root/'content/sitemap.xml').read_text();rows=[];aliases={'docs/ai-assistants','docs/markdown','docs/template_files'}
for p in sorted((root/'content/docs').rglob('*.html')):
 name=str(p.relative_to(root/'content').with_suffix(''));nav=name in re.findall(r"@path\(['\"]([^'\"]+)['\"]\)",menu);links=sorted(inbound[name]-{'templates/partials/docs-sidebar.html',str(p.relative_to(root))});assert nav or links or name in aliases,name
 rows.append(dict(page=name,menu=nav,inbound=links,sitemap=name+'.html' in sitemap,intentional_alias=name in aliases))
assert len(rows)==94
for name in ['build-systems','asset-pipelines']:
 source=(root/f'content/docs/{name}.html').read_text();assert f'docs/{name}' in menu and f'docs/{name}.html' in sitemap
 files=root/f'examples/v410/{name}'
 with zipfile.ZipFile(root/f'public/examples/{name}.zip') as z:
  expected={f'{name}/{f.relative_to(files)}':f.read_bytes() for f in files.rglob('*') if f.is_file()};assert set(z.namelist())==set(expected)
  for f,data in expected.items():assert z.read(f)==data,f
  assert not any('/public/' in f or '/.nift/public/' in f for f in z.namelist())
 blocks=[html.unescape(b) for b in re.findall(r'<pre><code class="language-[^"]+">(.*?)</code></pre>',source,re.S)]
 assert json.loads((files/'.nift/tracked.json').read_text()) in [json.loads(b) for b in blocks if b.startswith('{')]
 if name=='build-systems':
  for script in (files/'scripts').glob('*.f'):assert script.read_text() in blocks,script
 if name=='asset-pipelines':
  for recipe in (root/'examples/v410/recipes').glob('*.f'):assert recipe.read_text() in blocks,recipe
(out/'docs-audit.json').write_text(json.dumps(rows,indent=2)+'\n')
(out/'workflow-audit.json').write_text(json.dumps({'docs_pages':94,'new_pages':['General build systems','Asset pipelines'],'orphan_pages':0,'sitemap_urls':100,'site_search':'No site-wide search implementation/index exists; sitemap and navigation cover both pages','download_source_identity':'PASS','displayed_scripts_and_tracking_identity':'PASS','desktop_viewport':[1280,900],'mobile_viewport':[390,844],'document_widths':{'desktop':1265,'mobile':375},'mobile_menu':'PASS: both new links visible in expanded Workflows & patterns','native_runtime_head':'c46c36e78176'},indent=2)+'\n')
print('PASS 94-page orphan audit, two menu/sitemap entries, exact downloadable/source/script identity')
