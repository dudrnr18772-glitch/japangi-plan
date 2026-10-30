#!/usr/bin/env python3
"""Editorial PSEO: approved, fact-checked entries only; drafts never published.
The base site's curated HTML pages are maintained by build.py and seo_enhancements.py.
"""
import json, re, html, difflib
from pathlib import Path
from datetime import date
from urllib.parse import urlparse

VALID_STATUSES={'idea','draft','review','approved','published','hold','retired'}
SLUG_RE=re.compile(r'^[a-z0-9]+(?:[a-z0-9-]*/)*[a-z0-9-]+$')
MIN_SECTION_CHARS=135
MIN_BODY_CHARS=750

class QualityError(ValueError):
    pass

def chars(text):
    return len(re.sub(r'\s+','',re.sub(r'<[^>]+>','',text or '')))

def base_clean(s):
    s=re.sub(r'(?i)https?://\S+','',s)
    return re.sub(r'[^가-힣a-z0-9]','',s.lower())

def html_text(s):
    return html.escape(str(s),quote=True)

def load_editorial(path, reserved, assets_root, today=None):
    records=json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(records,list): raise QualityError('PSEO data must be a list')
    errors=[]; approved=[]; registry=[]; ids=set(); slugs=set(); keywords=set()
    today=today or date.today()
    for n,r in enumerate(records,1):
        rid=r.get('id') or f'#{n}'; status=r.get('status')
        if status not in VALID_STATUSES: errors.append(f'{rid}: invalid status {status!r}');continue
        if rid in ids: errors.append(f'{rid}: duplicate id')
        ids.add(rid)
        slug=r.get('slug','').strip('/')
        if not slug or not SLUG_RE.fullmatch(slug) or slug in reserved:
            errors.append(f'{rid}: slug invalid or conflicts with existing page: {slug!r}')
        if slug in slugs: errors.append(f'{rid}: duplicate slug: {slug}')
        slugs.add(slug)
        if status not in ('approved','published'):
            registry.append({'id':rid,'slug':slug,'status':status,'published':False,'reason':'비공개 초안 / 승인 전'})
            continue
        def need(field,threshold=1):
            if chars(str(r.get(field,'')))<threshold: errors.append(f'{rid}: {field} requires {threshold}+ chars')
        for k,v in [('keyword',3),('intent',30),('title',15),('description',55),('heading',12),('unique_value',70),('buyer_action',70),('source_notes',50),('image_alt',12)]: need(k,v)
        kw=base_clean(r.get('keyword',''))
        if kw in keywords: errors.append(f'{rid}: duplicate target keyword')
        keywords.add(kw)
        sections=r.get('sections',[])
        if len(sections)<4: errors.append(f'{rid}: 4+ sections required')
        if len(set(base_clean(x.get('heading','')) for x in sections))!=len(sections): errors.append(f'{rid}: duplicate section headings')
        for ix,x in enumerate(sections,1):
            if chars(x.get('body',''))<MIN_SECTION_CHARS: errors.append(f'{rid}: section {ix} too short (min {MIN_SECTION_CHARS} non-space chars)')
        if sum(chars(x.get('body','')) for x in sections)<MIN_BODY_CHARS: errors.append(f'{rid}: body too short (min {MIN_BODY_CHARS} non-space chars)')
        qa=r.get('faq',[])
        if len(qa)<2 or any(chars(x.get('answer',''))<55 for x in qa): errors.append(f'{rid}: 2+ substantive FAQs required')
        hero=r.get('image','')
        if hero and not (assets_root/hero).is_file(): errors.append(f'{rid}: missing image {hero}')
        if not hero: errors.append(f'{rid}: image required')
        if r.get('image_type') not in ('actual','illustration'): errors.append(f'{rid}: image_type actual/illustration required')
        if r.get('image_type')=='actual' and not r.get('image_evidence'):
            errors.append(f'{rid}: evidence for real installation photo required')
        if r.get('claims_real_installation') and r.get('image_type')!='actual':
            errors.append(f'{rid}: no real installation claim with illustration')
        reviewed=r.get('reviewed_by','').strip()
        if not reviewed: errors.append(f'{rid}: reviewed_by required for publication')
        date_s=r.get('published_on','')
        try:
            if date.fromisoformat(date_s)>today: errors.append(f'{rid}: future publish date')
        except (ValueError,TypeError): errors.append(f'{rid}: real published_on YYYY-MM-DD required')
        full_text=' '.join(x.get('body','') for x in sections)
        for other in approved:
            other_text=' '.join(x.get('body','') for x in other['sections'])
            ratio=difflib.SequenceMatcher(None,base_clean(full_text),base_clean(other_text),autojunk=False).ratio()
            if ratio>=0.78: errors.append(f'{rid}: content too similar to {other["id"]} ({ratio:.1%})')
        approved.append(r)
        registry.append({'id':rid,'slug':slug,'status':status,'published':True,'reason':'승인 및 품질 검사 대상'})
    if errors: raise QualityError('\n'.join(errors))
    return approved,registry

def render_record(record, root, cta):
    e=html_text; title=e(record['heading']); intro=e(record['intent']); alt=e(record['image_alt'])
    image_src=root+'assets/img/'+e(record['image'])
    image_label='실제 설치 사진' if record['image_type']=='actual' else '제품·환경 연출 이미지'
    blocks=[f'<section class="page-intro"><div class="container narrow"><span class="eyebrow">자판기 설치 안내</span><h1>{title}</h1><p class="lead">{intro}</p></div></section>',
    f'<section class="section"><div class="container split-feature"><div><span class="eyebrow">설치 전 확인할 핵심</span><h2>{e(record["unique_value_heading"])}</h2><p>{e(record["unique_value"])}</p></div><figure class="feature-image"><img src="{image_src}" alt="{alt}" width="1440" height="1080"><figcaption class="fineprint">{e(image_label)}</figcaption></figure></div></section>']
    for idx,s in enumerate(record['sections']):
        cls='section tinted' if idx%2 else 'section'
        blocks.append(f'<section class="{cls} article-section"><div class="container narrow"><span class="eyebrow">{e(s.get("eyebrow","설치 가이드"))}</span><h2>{e(s["heading"])}</h2><p>{e(s["body"])}</p></div></section>')
    faq=''.join(f'<details><summary>{e(q["question"])}</summary><div class="faq-answer"><p>{e(q["answer"])}</p></div></details>' for q in record['faq'])
    blocks.append(f'<section class="section"><div class="container narrow"><h2>{e(record["keyword"])} 자주 묻는 질문</h2><div class="faq-list">{faq}</div></div></section>')
    blocks.append(f'<section class="section tinted article-section"><div class="container narrow"><h2>구매·설치 상담 전 준비사항</h2><p>{e(record["buyer_action"])}</p><p class="fineprint">제품과 설치 환경에 따라 적용 가능한 사양과 조건이 다릅니다. 계약 전 공급업체를 통해 확인해 주세요.</p></div></section>')
    blocks.append(cta)
    return '\n'.join(blocks)


def render_rss(site_url,brand,entries,max_items=40):
    from email.utils import format_datetime
    from datetime import datetime, timezone
    out=['<?xml version="1.0" encoding="UTF-8"?>','<rss version="2.0"><channel>',f'<title>{html_text(brand)} 신규 자판기 안내</title>',f'<link>{html_text(site_url)}</link>','<description>새로 발행한 자판기 구매·설치 안내 페이지를 제공합니다.</description>','<language>ko</language>']
    for p in sorted(entries,key=lambda x:x['published_on'],reverse=True)[:max_items]:
        url=site_url+p['slug'].strip('/')+'/'
        d=date.fromisoformat(p['published_on'])
        pub=format_datetime(datetime(d.year,d.month,d.day,0,0,0,tzinfo=timezone.utc))
        # feed only genuinely published records; do not reuse fabricated date of drafts
        out.append('<item><title>'+html_text(p['title'])+'</title><link>'+html_text(url)+'</link><guid isPermaLink="true">'+html_text(url)+'</guid><pubDate>'+pub+'</pubDate><description>'+html_text(p['description'])+'</description></item>')
    out.append('</channel></rss>')
    return '\n'.join(out)
