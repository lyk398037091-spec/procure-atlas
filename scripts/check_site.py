#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        for key in ('href','src'):
            if key in d: self.refs.append((tag,key,d[key]))

errors=[]; html_files=list(SITE.rglob('*.html'))
for file in html_files:
    p=Parser()
    try: p.feed(file.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'{file.relative_to(SITE)} parse error: {e}'); continue
    for tag,key,ref in p.refs:
        if not ref or ref.startswith(('#','mailto:','tel:','javascript:','data:')): continue
        u=urlsplit(ref)
        if u.scheme in ('http','https'): continue
        target=(file.parent/u.path).resolve()
        try: target.relative_to(SITE.resolve())
        except ValueError: errors.append(f'{file.relative_to(SITE)} escapes site root: {ref}'); continue
        if u.path.endswith('/'):
            target=target/'index.html'
        if not target.exists(): errors.append(f'{file.relative_to(SITE)} missing {ref} -> {target.relative_to(SITE)}')

required=['index.html','manufacturers/index.html','products/index.html','compare/index.html','methodology/index.html','rfq/index.html','llms.txt','sitemap.xml','robots.txt']
for r in required:
    if not (SITE/r).exists(): errors.append(f'missing required output {r}')

if errors:
    print('SITE CHECK FAILED')
    for e in errors[:100]: print(' -',e)
    raise SystemExit(1)
print(f'OK: parsed {len(html_files)} HTML files; all internal href/src targets resolve')
