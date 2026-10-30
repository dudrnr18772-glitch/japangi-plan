#!/usr/bin/env python3
"""Post-build static checks, no external dependencies."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
from xml.etree import ElementTree as ET
import json,re,sys
OUT=Path(__file__).resolve().parent/'dist'
class Scan(HTMLParser):
 def __init__(self):super().__init__();self.h1=0;self.title=0;self.desc=0;self.canonical=[];self.assets=[];self.body_text=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=='h1':self.h1+=1
  if tag=='title':self.title+=1
  if tag=='meta' and d.get('name')=='description':self.desc+=1
  if tag=='link' and d.get('rel')=='canonical':self.canonical.append(d.get('href'))
  if tag in ('a','img','script','link'):
   k={'a':'href','img':'src','script':'src','link':'href'}[tag];v=d.get(k)
   if v and not (v.startswith('#') or v.startswith(('https:','http:','mailto:','tel:','data:','javascript:'))):self.assets.append(v)
errors=[];pages=list(OUT.rglob('index.html'))
for f in pages:
 p=Scan();p.feed(f.read_text(encoding='utf-8'))
 if p.h1!=1:errors.append(f'{f.relative_to(OUT)}: expected 1 H1 got {p.h1}')
 if p.title!=1 or p.desc!=1:errors.append(f'{f.relative_to(OUT)}: title/description missing')
 if len(p.canonical)!=1:errors.append(f'{f.relative_to(OUT)}: canonical count wrong')
 for v in p.assets:
  path=unquote(v.split('?')[0].split('#')[0]).strip()
  target=(f.parent/path).resolve()
  # Link to /contact/ etc is valid even if a slash is absent from relative HTML.
  if v.startswith('/.netlify/functions/'):continue
  if not target.exists() and not (target/'index.html').exists():errors.append(f'{f.relative_to(OUT)}: broken {v}')
rss=ET.parse(OUT/'rss.xml');ss=ET.parse(OUT/'sitemap.xml')
manifest=json.loads(((OUT.parent)/'pseo/release-report.json').read_text(encoding='utf-8'))
if len(list(OUT.rglob('index.html')))!=11+manifest['published_count']:errors.append('Unexpected page count: unpublished drafts must remain private')
if len([r for r in manifest['registry'] if r['published']])!=manifest['published_count']:errors.append('Publication manifest inconsistent')
if errors: print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(pages)} page HTML links, metadata, sitemap, RSS, draft exclusion')
