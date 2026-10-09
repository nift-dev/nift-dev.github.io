from pathlib import Path
import tempfile,zipfile,subprocess,json,shutil
root=Path('/home/nick/Repositories/nift/nift-dev.github.io');binary=Path('nift').resolve()
def run(p,*args,ok=True):
 r=subprocess.run([str(binary),*args],cwd=p,text=True,capture_output=True,timeout=45);assert (r.returncode==0)==ok,(args,r.stdout,r.stderr);return r.stdout+r.stderr
with tempfile.TemporaryDirectory(prefix='nift-workflow-example-') as tmp:
 base=Path(tmp)
 for name,target,source in [('build-systems','manifest','content/generated-api.json'),('asset-pipelines','home','src/js/app.js')]:
  with zipfile.ZipFile(root/'public/examples'/f'{name}.zip') as z:z.extractall(base)
  p=base/name;run(p,'build',target);run(p,'status','-p');run(p,'info','--tracking');before={str(f.relative_to(p)):f.stat().st_mtime_ns for f in (p/'.nift/public').rglob('*.info.json')};run(p,'build');assert before=={str(f.relative_to(p)):f.stat().st_mtime_ns for f in (p/'.nift/public').rglob('*.info.json')}
  subprocess.run(['node','--check',str(p/'public'/('app-js.js' if name=='build-systems' else 'frontend-js.js'))],check=True,capture_output=True)
  output=p/'public'/('manifest.json' if name=='build-systems' else 'asset-manifest.json');initial=output.read_bytes();f=p/source;f.write_text(f.read_text().replace('Hello','Hello again').replace(' assets',' verified assets'));run(p,'build');assert output.read_bytes()!=initial
  if name=='asset-pipelines':
   assert output.read_text() in (p/'public/home.html').read_text()
   prior=output.read_bytes();css=p/'content/styles.css';css.write_text(css.read_text()+'\nstrong { color: purple; }\n');run(p,'build');assert output.read_bytes()!=prior;assert output.read_text() in (p/'public/home.html').read_text()
  json.loads(output.read_text());run(p,'build','--all');print('PASS extracted complete example',name,'target/full/no-op/same-pass/JSON/JS')
 # Exercise the published external wrappers using real locally available tools.
 for tool,ext,script in [('sass','.css','sass.f'),('magick','.webp','image.f'),('magick','.avif','image.f')]:
  p=base/(tool+ext);p.mkdir();(p/'.nift').mkdir();(p/'content').mkdir();(p/'scripts').mkdir();(p/'public').mkdir();(p/'.nift/config.json').write_text(json.dumps({'config':{'content-dir':'content/','content-ext':'.txt','output-dir':'public/','output-ext':'.txt','default-template':'','minify-exts':[]}}));(p/'.nift/tracked.json').write_text(json.dumps({'tracked':[{'name':'asset','title':'Asset','output-ext':ext,'build':'scripts/build.f'}]}));(p/'content/asset.txt').write_text('recipe');shutil.copyfile(root/'examples/v410/recipes'/script,p/'scripts/build.f')
  if tool=='sass':
   (p/'src/styles').mkdir(parents=True);(p/'src/styles/main.scss').write_text('$brand: navy; body { color: $brand; }\n')
  else:
   (p/'src/images').mkdir(parents=True);subprocess.run(['magick','-size','8x8','xc:navy',str(p/'src/images/hero.png')],check=True,capture_output=True)
  run(p,'build','--all');assert (p/'public'/('asset'+ext)).stat().st_size>0;print('PASS real external recipe',tool,ext)
 # A process failure must fail the build and leave no successful item metadata.
 p=base/'sass.css';(p/'src/styles/main.scss').write_text('body { color: ; BROKEN');run(p,'build','--repair',ok=False);print('PASS compiler exit failure propagation')
print('esbuild recipe: CLI syntax checked against official reference; executable unavailable locally, no bundler execution claim')
