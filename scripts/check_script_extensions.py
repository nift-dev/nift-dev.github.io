#!/usr/bin/env python3
from pathlib import Path
import re,sys
bad=[]
for p in Path('content').rglob('*'):
    if not p.is_file(): continue
    text=p.read_text(errors='ignore')
    for i,line in enumerate(text.splitlines(),1):
        if re.search(r'\b(?:run|import)\b[^\n]*["\'`][^"\'`]*\.nift["\'`]', line): bad.append(f'{p}:{i}:{line.strip()}')
if bad:
    print('\n'.join(bad));sys.exit(1)
print('script extension gate: PASS')
