#!/usr/bin/env python3
"""Static Korean vending-machine lead website. Python stdlib only.
Run: python build.py [--site-url https://YOUR-DOMAIN/]"""
from pathlib import Path
from html import escape
from urllib.parse import urljoin
from datetime import date
import json, argparse, shutil, re, os

ROOT=Path(__file__).resolve().parent
config=json.loads((ROOT/'site-config.json').read_text(encoding='utf-8'))
ap=argparse.ArgumentParser(); ap.add_argument('--site-url',default=None); args=ap.parse_args()
if args.site_url is not None: config['site_url']=args.site_url.rstrip('/')+'/' if args.site_url else ''
elif not config.get('site_url') and os.getenv('CONTEXT') == 'production' and os.getenv('URL'):
    config['site_url']=os.environ['URL'].rstrip('/')+'/'
IS_NETLIFY_PREVIEW=os.getenv('CONTEXT') in ('deploy-preview','branch-deploy')
OUT=ROOT/'dist'
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
(OUT/'assets').mkdir()
shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
SITE=config['site_name']; URL=config['site_url']; PARTNER=config['partner_name']
PROVIDER=config['provider_name']; MANUFACTURER=config['manufacturer_name']
INQUIRY_PHONE=config['inquiry_phone']
FORM_READY=True
PRIVACY_READY=all(config.get(x) for x in ['operator_name','operator_contact','partner_name','partner_retention','operator_retention'])

# Text is product-specific and based on the supplied brochures and agreements.
def page_url(slug): return URL+ (slug+'/' if slug else '') if URL else None
def full_path(root,slug=''):
    return root+(slug+'/' if slug else '')
def section_title(kicker,title,subtitle=''):
    return f'<div class="section-heading"><span class="eyebrow">{escape(kicker)}</span><h2>{title}</h2>{f"<p>{subtitle}</p>" if subtitle else ""}</div>'
def card(title,content,href=None,tag=None):
    foot=f'<a class="text-link" href="{href}">자세히 보기 <span aria-hidden="true">↗</span></a>' if href else ''
    tag_html=f'<span class="tiny-label">{tag}</span>' if tag else ''
    return f'<article class="info-card">{tag_html}<h3>{title}</h3><p>{content}</p>{foot}</article>'
def details(qa):return '<div class="faq-list">'+''.join(f'<details><summary>{q}</summary><div class="faq-answer"><p>{a}</p></div></details>' for q,a in qa)+'</div>'
def cta(root,product=''):
    href=root+'contact/'+('?product='+product if product else '')
    return f'<section class="cta-band"><div><span class="eyebrow">맞춤형 상담</span><h2>판매 상품과 설치 환경에 맞는 구성을 확인하세요.</h2><p>문의 접수 후 공급 담당자가 제품·구매 조건·설치 일정을 안내합니다.</p></div><a href="{href}" class="btn btn-light">견적 상담 신청 <span aria-hidden="true">↗</span></a></section>'

def hero(kicker,heading,desc,img,alt,buttons,meta=''):
    return f'''<section class="hero inner-hero"><div class="hero-copy"><span class="eyebrow"><span class="dot"></span>{kicker}</span><h1>{heading}</h1><p class="lead">{desc}</p><div class="actions">{buttons}</div>{f'<p class="micro">{meta}</p>' if meta else ''}</div><div class="hero-photo"><img src="{img}" alt="{escape(alt)}" width="720" height="700" fetchpriority="high"><span class="image-tag">연출 이미지</span></div></section>'''

def button(href,txt,kind='primary'):
    return f'<a class="btn btn-{kind}" href="{href}">{txt}<span aria-hidden="true">↗</span></a>'

PAGES=[]
def add(slug,title,description,heading,body,kind='article',image=None,faqs=None):
    PAGES.append(dict(slug=slug,title=title,desc=description,heading=heading,body=body,kind=kind,image=image,faqs=faqs or []))

# Directory-relative URLs for direct file-open preview and for hosting at domain root.
# Page-local root path: ../ for first-level page; ./ for home page.
R='./'
add('',
 '멀티자판기·냉동자판기 구매와 SAFE24 무인매장 상담',
 '멀티자판기와 냉동 블록형 자판기 제품 정보를 비교하고 SAFE24 무인매장 구성을 알아보세요. 제품별 구매 조건과 설치 사례, 맞춤 견적 상담을 안내합니다.',
 '상품에 맞는 자판기, 공간에 맞는 무인매장.',
 f'''<section class="hero hero-home"><div class="hero-copy"><span class="eyebrow"><span class="dot"></span>스마트 자판기 · 냉동 판매 · 무인매장</span><h1>상품에 맞는 자판기,<br><em>공간에 맞는 무인매장.</em></h1><p class="lead">멀티자판기부터 냉동 블록형 자판기, 여러 대를 조합하는 SAFE24 무인매장까지. 제품 구성과 설치 사례를 살펴보고 구매 조건을 비교해 보세요.</p><div class="actions">{button('multi-vending-machine/','멀티자판기 보기')}{button('safe24-unmanned-store/','무인매장 구성','outline')}</div><div class="hero-trust"><div><strong>2종</strong><span>핵심 자판기 유형</span></div><div><strong>SAFE24</strong><span>다기기 매장 구성</span></div><div><strong>실제 사례</strong><span>학교·호텔·시설</span></div></div></div><div class="hero-collage"><figure class="collage-primary"><img src="assets/img/multi-hero.webp" alt="화이트 색상의 키오스크 결합형 스마트 멀티자판기" fetchpriority="high"></figure><figure class="collage-secondary"><img src="assets/img/frozen-hero.webp" alt="블랙 색상의 스마트 냉동 블록형 쇼케이스 자판기"></figure><div class="floating-note"><span class="signal-dot"></span>제품별 상담 연결</div></div></section>
<section class="section"><div class="container">{section_title('PRODUCTS','판매 목적에 맞춰 선택하는 자판기','판매할 상품과 설치 환경에 맞춰 제품의 기능과 운영 방식을 비교해 보세요.')}<div class="product-grid"><article class="product-card"><a href="multi-vending-machine/" class="product-img"><img loading="lazy" src="assets/img/multi-hero.webp" alt="스마트 멀티자판기 실제 제품 이미지"></a><div class="product-content"><span class="tiny-label">01 / SMART MULTI</span><h3>스마트 멀티자판기</h3><p>간식·음료·생활용품 등 상품에 따라 트레이를 구성하는 키오스크형 자판기.</p><a class="text-link" href="multi-vending-machine/">제품 사양과 구매 조건 보기 ↗</a></div></article><article class="product-card"><a href="frozen-vending-machine/" class="product-img"><img loading="lazy" src="assets/img/frozen-hero.webp" alt="블랙 색상의 냉동 블록형 쇼케이스 자판기"></a><div class="product-content"><span class="tiny-label">02 / FROZEN SHOWCASE</span><h3>냉동 블록형 자판기</h3><p>판매할 냉동식품의 크기와 종류에 맞춰 보관 블록을 구성하는 자판기.</p><a class="text-link" href="frozen-vending-machine/">냉동 구성과 설치 조건 보기 ↗</a></div></article><article class="product-card"><a href="safe24-unmanned-store/" class="product-img"><img loading="lazy" src="assets/img/safe24-hero.webp" alt="멀티자판기와 냉동자판기를 여러 대 구성한 SAFE24 무인매장"></a><div class="product-content"><span class="tiny-label">03 / UNMANNED STORE</span><h3>SAFE24 무인매장</h3><p>멀티·냉동 자판기를 조합해 공간과 상품군에 맞는 무인매장을 계획합니다.</p><a class="text-link" href="safe24-unmanned-store/">매장 구성 예시 보기 ↗</a></div></article></div></div></section>
<section class="section tinted"><div class="container">{section_title('WHY SMART','단순한 기계 구매에서 운영 방식까지','멀티자판기의 실제 운영 기능과 설치 시 확인할 사항을 알아보세요.')}<div class="three-cards">{card('키오스크 결합','터치스크린 화면으로 상품 선택과 결제 과정을 안내합니다.',tag='01')}{card('상품 구성의 유연성','트레이 또는 냉동 블록을 판매 상품에 맞춰 구성합니다.',tag='02')}{card('원격 관리 기능','재고·매출 관리와 매장 광고 영상 송출 등 운영 기능을 확인할 수 있습니다.',tag='03')}</div></div></section>
<section class="section"><div class="container split-feature"><div><span class="eyebrow">SAFE24 / UNMANNED STORE</span><h2>자판기를 여러 대 조합해<br>하나의 무인매장으로.</h2><p>SAFE24는 아이스크림, 음료, 간식 등 여러 상품군을 구성할 수 있는 무인매장입니다. 필요한 장비 조합과 설치 환경은 실제 상담을 통해 결정합니다.</p>{button('safe24-unmanned-store/','SAFE24 알아보기')}</div><div class="feature-image"><img loading="lazy" src="assets/img/safe24-hero.webp" alt="SAFE24 자판기 무인매장 구성 이미지"></div></div></section>
<section class="section tinted"><div class="container">{section_title('REAL INSTALLATIONS','설치 장소에 따라 달라지는 제안','학교·호텔 등 다양한 설치 공간과 상품 구성 사례를 살펴보세요.')}<div class="case-grid"><a class="case-card" href="installation-cases/"><img loading="lazy" src="assets/img/school-case.webp" alt="학교에 설치된 멀티자판기"><div><strong>학교·학원</strong><span>휴게 공간과 이용 시간에 맞는 상품 구성</span></div></a><a class="case-card" href="installation-cases/"><img loading="lazy" src="assets/img/hotel-case.webp" alt="호텔에 설치된 자판기"><div><strong>호텔·숙박시설</strong><span>이용객 편의 상품 판매</span></div></a><a class="case-card" href="installation-cases/"><img loading="lazy" src="assets/img/hotel-case-2.webp" alt="호텔 로비에 설치된 자판기"><div><strong>복합 공간</strong><span>설치 위치와 동선에 맞춘 구성</span></div></a></div></div></section>
{cta('', '')}''',kind='home',image='assets/img/multi-hero.webp')

# For subpages, use path ../
R='../'
add('multi-vending-machine',
 '멀티자판기 가격·구매·설치 안내 | 스마트 멀티밴딩머신',
 '스마트 멀티자판기의 실제 제품 사진, 상품 수납 방식, 키오스크 결제, 구매 조건과 설치 전 확인사항을 살펴보고 구매 상담을 신청하세요.',
 '멀티자판기 종류와 가격, 구매 전 확인할 사항',
 hero('SMART MULTI VENDING','멀티자판기 종류와 가격,<br><em>구매 전 확인할 사항</em>','음료·간식·생활용품 등 여러 상품을 판매하는 스마트 멀티자판기. 키오스크와 관리 기능, 상품별 트레이 구성까지 비교해 보세요.', ' ../assets/img/multi-hero.webp'.strip(),'화이트 색상의 스마트 멀티자판기 실물 이미지',button('../contact/?product=multi','멀티자판기 견적 문의')+button('../multi-purchase/','일시불·할부 조건','outline'))+
 f'''<section class="section"><div class="container">{section_title('PRODUCT DETAIL','이 제품의 핵심 기능','실제 제품의 판매 방식과 운영 기능을 살펴보세요.')}<div class="three-cards">{card('키오스크 결합형','화면에서 상품을 선택하고 결제할 수 있는 스마트 판매 구조입니다.','',tag='FEATURE 01')}{card('상품별 트레이 구성','스파이럴·트레이 등 판매 상품 크기와 특성에 맞춘 구성을 검토할 수 있습니다.',tag='FEATURE 02')}{card('재고·매출 관리','재고·매출 관리 프로그램과 매장 광고 영상 송출 기능이 제공됩니다. 적용 범위는 모델별로 확인하세요.',tag='FEATURE 03')}</div></div></section>
<section class="section tinted"><div class="container split-feature"><div><span class="eyebrow">MODEL INFORMATION</span><h2>실제 제품 사양을<br>확인하세요.</h2><p>대표 키오스크 결합형 모델은 폭 955mm, 높이 1,970mm, 깊이 920mm입니다.</p><ul class="check-list"><li>24인치 터치스크린을 활용한 상품 안내</li><li>캔·PET 음료, 과자, 생활용품 등 상품 판매</li><li>카드·간편결제 방식은 계약 모델별 확인 필요</li><li>전력 및 온도 조건은 최종 모델별 사양 확인</li></ul><p class="fineprint">소비전력과 사용 온도는 선택 모델과 설치 환경에 따라 달라질 수 있으므로 최종 사양을 확인하세요.</p></div><div class="feature-image white-image"><img loading="lazy" src="../assets/img/multi-two-units.webp" alt="실내 공간에 나란히 배치된 스마트 멀티자판기 두 대"></div></div></section>
<section class="section"><div class="container">{section_title('PURCHASE','멀티자판기 구매 방식','일시불과 36개월 할부 두 가지 방식의 구매 조건을 비교해 보세요.')}<div class="two-cards">{card('일시불 구매','일시불 조건은 730만 원(VAT 별도)으로 표시되어 있습니다. 모델과 적용 조건은 견적 상담 시 확인하세요.', '../multi-purchase/','일시불')}{card('36개월 할부','36개월 할부는 월 23만 원(VAT 별도)이고 보증금·보증보험료 등이 별도로 발생합니다.', '../multi-purchase/','할부')}</div><p class="fineprint">※ 가격은 2026년 8월 안내 조건을 기준으로 하며 실제 구매 시 적용 여부와 금액을 확인해야 합니다.</p></div></section>
<section class="section tinted"><div class="container">{section_title('FAQ','멀티자판기 구매 전 자주 묻는 질문')}{details([('멀티자판기로 음료만 판매해야 하나요?','아닙니다. 병·캔·PET 음료뿐 아니라 간식과 생활용품도 판매할 수 있습니다. 실제 수납 크기와 구성은 모델 및 트레이에 따라 달라집니다.'),('멀티자판기는 어디에 설치할 수 있나요?','학교·학원, 호텔, 스포츠시설, 사무공간 등 다양한 장소에 설치할 수 있습니다. 설치 가능 여부는 전원, 반입 동선, 설치 면적 등에 따라 달라집니다.'),('일시불과 할부 중 선택할 수 있나요?','구매 조건에는 일시불과 36개월 할부 방식이 마련되어 있습니다. 적용 여부, 현재 금액, 보증금 및 설치비는 상담 과정에서 확인이 필요합니다.')])}</div></section>
{cta('../','multi')}
''',image='assets/img/multi-hero.webp')

add('frozen-vending-machine','냉동자판기 구매·가격·설치 조건 | 냉동 블록형 쇼케이스','냉동 블록형 쇼케이스 자판기의 보관 블록 구성, 판매 상품, 온도 관리와 설치 조건을 비교하고 제품 상담을 신청하세요.','냉동자판기 구매와 가격, 설치 조건 안내',
hero('FROZEN SHOWCASE','냉동자판기 구매와 가격,<br><em>설치 조건 안내</em>','아이스크림·냉동식품 등 상품의 크기와 종류에 맞춰 블록을 구성하는 냉동 블록형 쇼케이스 자판기를 소개합니다.','../assets/img/frozen-hero.webp','블랙 색상의 냉동 블록형 쇼케이스 자판기',button('../contact/?product=frozen','냉동자판기 견적 문의')+button('../safe24-unmanned-store/','무인매장 구성 보기','outline'))+
 f'''<section class="section"><div class="container">{section_title('FROZEN FEATURES','블록형 냉동자판기의 특징','판매할 상품의 크기와 종류에 맞는 보관 구성이 핵심입니다.')}<div class="three-cards">{card('상품별 블록 구성','소형·중형·대형 상품에 따라 보관 블록 크기를 다르게 구성할 수 있습니다.',tag='01')}{card('잠금·배출 구조','선택한 상품의 블록을 잠금 해제해 인도하는 구조입니다.',tag='02')}{card('통합 관리','재고·매출 및 운영 데이터 관리와 화면을 통한 상품 안내 기능이 있습니다.',tag='03')}</div></div></section>
<section class="section tinted"><div class="container split-feature"><div><span class="eyebrow">FROZEN CABINET</span><h2>상품 크기에 맞춰<br>블록을 선택하세요.</h2><p>상품 크기에 따라 45칸·24칸·16칸 등의 보관 구성을 검토할 수 있습니다. 단순히 칸 수가 많다고 적합한 것은 아니며 실제 상품의 포장 크기와 운영 방식을 함께 확인해야 합니다.</p><ul class="check-list"><li>아이스크림 및 소형 냉동 간식</li><li>밀키트·도시락류 등 중형 상품</li><li>육류·포장 냉동식품 등 크기가 큰 상품</li></ul><p class="fineprint">대표 모델의 높이는 약 2,050mm입니다. 최종 제품 규격·냉동 온도·인증·사양은 공급 모델별 확인이 필요합니다.</p></div><div class="feature-image white-image"><img loading="lazy" src="../assets/img/frozen-model.webp" alt="냉동식품을 위한 블록형 쇼케이스 자판기 모델"></div></div></section>
<section class="section"><div class="container">{section_title('BUYING GUIDE','냉동자판기 견적에서 확인할 사항')}<div class="two-cards">{card('제품 구성·사양','냉동 블록 구성, 목표 온도, 전원 조건, 보관 상품 크기, 결제 및 관리 기능을 확인하세요.',tag='제품 선정')}{card('설치·운영 조건','반입 동선, 설치 공간, 냉동 유지 방식, 전기료, 상품 공급·재고 관리 방식도 함께 검토하세요.',tag='운영 검토')}</div></div></section>
<section class="section tinted"><div class="container">{section_title('FAQ','냉동자판기 관련 질문')}{details([('냉동자판기로 어떤 식품을 판매할 수 있나요?','아이스크림, 밀키트, 육류, 냉동식품 등 상품 유형에 맞춘 블록을 구성할 수 있습니다. 실제 보관 적합성은 식품별 요구 온도와 제품 사양을 함께 확인해야 합니다.'),('냉동자판기는 멀티자판기와 무엇이 다른가요?','멀티자판기는 다양한 상온·냉장 상품의 판매와 트레이 구성이 중심이고, 냉동 블록형 쇼케이스는 냉동 상품 보관과 블록별 배출 방식이 중심입니다.'),('냉동자판기도 무인매장에 여러 대 설치할 수 있나요?','SAFE24는 냉동 쇼케이스와 멀티자판기를 함께 배치하는 방식도 가능합니다. 실제 가능 대수는 전력·면적·동선 등을 검토해야 합니다.')])}</div></section>
{cta('../','frozen')}''',image='assets/img/frozen-hero.webp')

add('safe24-unmanned-store','무인매장 창업·구축 안내 | SAFE24 자판기 무인매장','멀티자판기와 냉동자판기 여러 대를 조합하는 SAFE24 무인매장. 상품 구성, 공간 계획, 인테리어 비용 범위와 상담 절차를 알아보세요.','자판기로 시작하는 SAFE24 무인매장 창업',
hero('SAFE24 / UNMANNED STORE','자판기 여러 대로 완성하는<br><em>SAFE24 무인매장</em>','스마트 멀티자판기와 냉동자판기를 조합해 아이스크림·냉동식품·음료·간식 등 다양한 상품을 판매하는 무인매장 구성안입니다.','../assets/img/safe24-hero.webp','여러 대의 냉동·멀티자판기가 배치된 SAFE24 무인매장',button('../contact/?product=safe24','무인매장 구축 상담')+button('../installation-cases/','설치 사례 보기','outline'))+
 f'''<section class="section"><div class="container">{section_title('STORE COMPOSITION','어떤 상품을 팔 것인지부터 설계합니다','판매 상품과 매장 규모에 맞는 장비 조합을 검토하세요.')}<div class="three-cards">{card('냉동 상품','아이스크림과 냉동식품 등 냉동 보관이 필요한 상품군',tag='FROZEN')}{card('냉장·음료','생수와 음료 등을 판매할 수 있는 기기 구성',tag='BEVERAGE')}{card('간식·생활 상품','과자·잡화·반려동물 간식 등 점포 특성에 맞는 상품 구성',tag='SNACK')}</div></div></section>
<section class="section tinted"><div class="container split-feature"><div><span class="eyebrow">STORE PLAN</span><h2>기기 수량보다 중요한 것은<br>매장 동선과 상품군입니다.</h2><p>여러 대의 자판기를 설치한다면 기기 크기뿐 아니라 고객 이동 동선, 보충 작업, 전기 용량, 통신, 설치·반입 경로를 함께 고려해야 합니다.</p><ul class="check-list"><li>공간과 판매 상품에 맞춘 자판기 조합</li><li>결제·재고·운영 방식 검토</li><li>인테리어와 전기·통신 공사 범위 분리</li><li>상품 관리 및 설치 후 유지관리 조건 확인</li></ul></div><div class="feature-image"><img loading="lazy" src="../assets/img/safe24-config.webp" alt="SAFE24에서 제안한 여러 형태의 무인매장 구성 예시"></div></div></section>
<section class="section"><div class="container">{section_title('BUDGET','무인매장 창업비용은 어떻게 구성될까요?')}<div class="two-cards">{card('기기 구매 비용','멀티·냉동자판기 모델과 대수에 따라 달라집니다. 실제 장비 견적은 별도로 확인해야 합니다.',tag='장비')}{card('인테리어·시설 비용','10평 기준 인테리어 참고 비용은 약 2,000만 원입니다. 전기·도배·바닥 공사 등의 포함 범위는 견적 시 확인해야 합니다.',tag='매장 시설')}</div><div class="notice"><strong>비용 예시 안내</strong><p>위 2,000만 원은 인테리어 관련 참고 견적으로, 자판기 구매비·임대차 보증금·초기 상품비 등을 모두 포함한 총창업비가 아닙니다. 공간 조건과 실제 시공 범위에 따라 달라집니다.</p></div></div></section>
<section class="section tinted"><div class="container">{section_title('FAQ','SAFE24 무인매장 관련 질문')}{details([('SAFE24는 자판기 한 대 제품인가요?','아닙니다. SAFE24는 멀티자판기와 냉동자판기 등 여러 대의 기기를 조합하는 무인매장 구성안입니다.'),('무인매장은 몇 대부터 구성해야 하나요?','정해진 대수보다 상품군, 공간 규모, 예산, 전기 용량, 이용 고객 수요를 고려한 구성이 중요합니다. 현장 조건을 확인한 후 적합한 대수를 제안받을 수 있습니다.'),('창업비용에 기계 가격도 포함되나요?','10평 기준 약 2,000만 원은 인테리어비 참고 금액입니다. 자판기 구매 비용과 기타 초기비용은 별도 확인해야 합니다.'),('상담 후 계약·설치도 진행되나요?','문의 내용은 제휴 제품 공급 담당자에게 연결되며 상세 견적, 계약, 설치·유지관리는 공급업체 상담 과정에서 안내됩니다.')])}</div></section>
{cta('../','safe24')}''',image='assets/img/safe24-hero.webp')

add('multi-purchase','멀티자판기 일시불·36개월 할부 조건 비교 | 구매 안내','멀티자판기 일시불과 36개월 할부 조건, 보증금·설치비·추가 비용을 비교하고 상담 전 확인할 사항을 안내합니다.','멀티자판기 일시불과 36개월 할부 조건',
 f'''<section class="page-intro"><div class="container narrow"><span class="eyebrow">PURCHASE OPTIONS</span><h1>멀티자판기 일시불과<br><em>36개월 할부 조건</em></h1><p class="lead">멀티자판기 구매 시 일시불과 36개월 할부 조건을 비교하고, 계약 전 확인해야 할 비용을 살펴보세요.</p></div></section><section class="section"><div class="container narrow">{section_title('COMPARISON','일시불·할부 구매 조건')}<div class="price-table"><div class="price-card"><span>일시불</span><strong>730만 원</strong><small>VAT 별도 · 안내 조건</small><ul><li>계약금 100만 원 표기</li><li>설치비 포함(당사 지원) 표기</li><li>도서산간 등 추가 비용 가능</li></ul></div><div class="price-card featured"><span>36개월 할부</span><strong>월 23만 원</strong><small>VAT 별도 · 36개월 · 안내 조건</small><ul><li>보증금 100만 원 별도</li><li>보증보험료 약 20~25만 원 별도 표기</li><li>설치비 포함(당사 지원) 표기</li></ul></div></div><div class="notice"><strong>반드시 확인하세요</strong><p>가격·보증금·설치비·A/S 및 유지보수 조건은 2026년 8월 안내 조건을 기준으로 합니다. 실제 계약 전 최신 조건, 적용 모델, 부가세, 총납부액, 추가 설치비 등을 제휴 공급업체에 확인해야 합니다. 보증금의 반환 조건도 확인이 필요합니다.</p></div></div></section>
<section class="section tinted"><div class="container narrow">{section_title('CHECKLIST','계약 전에 함께 확인할 내용')}<div class="two-cards">{card('설치 환경','전기·인터넷 준비, 지역별 추가 운송비, 지게차·반입, 트레이 변경 비용 등이 발생할 수 있습니다.',tag='현장 확인')}{card('서비스와 유지관리','구매 조건에는 초기 3년 A/S와 이후 유지보수 계약 내용이 포함되어 있습니다. 각 조건의 실제 적용 범위를 확인하세요.',tag='계약 확인')}</div></div></section>{cta('../','multi')}''')

add('installation-cases','자판기 실제 설치 사례 | 학교·호텔·학원·무인매장','제휴업체 제품 자료에 수록된 학교·학원·호텔 등 자판기 설치 사진을 바탕으로 설치 장소별 특징을 소개합니다.','학교·호텔·시설별 자판기 설치 사례',
 f'''<section class="page-intro"><div class="container narrow"><span class="eyebrow">INSTALLATION STORIES</span><h1>다양한 공간에서 확인하는<br><em>자판기 설치 사례</em></h1><p class="lead">실제 학교·호텔 등에서 활용한 자판기 설치 사례입니다. 공간에 따른 배치와 상품 구성 참고용으로 살펴보세요.</p></div></section><section class="section"><div class="container"><div class="case-gallery"><article><img src="../assets/img/school-case.webp" alt="안동 소재 학교에 설치된 멀티자판기 사진" loading="lazy"><div><span class="eyebrow">SCHOOL</span><h2>학교·학원</h2><p>쉬는 시간, 점심시간 등 이용 시점에 따라 간식과 음료 상품 구성을 검토할 수 있습니다.</p></div></article><article><img src="../assets/img/hotel-case.webp" alt="호텔 내 자판기 설치 사례" loading="lazy"><div><span class="eyebrow">HOTEL</span><h2>호텔·숙박시설</h2><p>이용객을 위한 생수, 간식, 편의용품 등 설치 목적에 맞는 상품 구성 사례를 참고합니다.</p></div></article><article><img src="../assets/img/academy-case.webp" alt="학교 공간에 설치된 스마트 자판기 사진" loading="lazy"><div><span class="eyebrow">EDUCATION</span><h2>교육시설 내부</h2><p>제품 크기와 반입 동선, 전기 시설, 보충 동선 등을 고려해 설치합니다.</p></div></article><article><img src="../assets/img/hotel-case-2.webp" alt="숙박시설 로비의 복수 자판기 설치 사례" loading="lazy"><div><span class="eyebrow">MULTI UNITS</span><h2>여러 대의 기기 조합</h2><p>하나의 시설에서 여러 종류의 상품을 판매할 때 자판기 조합과 배치 방법을 검토합니다.</p></div></article></div></div></section>{cta('../','')}
''',image='assets/img/school-case.webp')

add('use-cases','업종별 자판기 추천 | 학교·호텔·헬스장·사무실','학교, 호텔, 헬스장, 사무실 등 공간에 맞는 자판기 판매 상품과 설치 조건을 비교합니다. 실물 제품 선택과 견적 요청에 필요한 기준을 확인하세요.','업종과 설치 장소에 맞는 자판기 선택',
 f'''<section class="page-intro"><div class="container narrow"><span class="eyebrow">USE CASES</span><h1>설치 장소에 맞는<br><em>자판기 선택 가이드</em></h1><p class="lead">같은 자판기라도 판매할 상품과 운영 시간이 다르면 필요한 수납 방식과 유지관리 방식이 달라집니다.</p></div></section><section class="section"><div class="container">{section_title('LOCATION GUIDE','장소별 검토 포인트')}<div class="two-cards">{card('학교·학원','쉬는 시간·점심시간 등 이용 집중 시간, 허용되는 상품, 반입 동선을 고려합니다.', '../installation-cases/','교육시설')}{card('호텔·숙박시설','생수·간식·편의용품 판매, 객실 접근성과 공동 공간 위치를 검토합니다.', '../installation-cases/','숙박시설')}{card('사무실·공장','근로자 이용 시간, 음료·간식 수요, 상품 보충 담당자를 확인합니다.',tag='사업장')}{card('헬스장·스포츠시설','운동 전후 음료와 간식 등 판매 상품의 수요, 설치 공간 및 이용 동선을 고려합니다.',tag='스포츠시설')}{card('무인매장','냉동·냉장·상온 상품군을 분리해 여러 대를 조합하고 전기·통신을 확인합니다.', '../safe24-unmanned-store/','무인매장')}{card('냉동식품 판매점','냉동 보관 조건, 상품별 포장 규격, 보충·재고 관리 방식을 검토합니다.', '../frozen-vending-machine/','냉동 판매')}</div></div></section>{cta('../','')}''')

add('guides/vending-installation','자판기 설치 조건 | 전원·통신·반입·공간 체크리스트','멀티자판기와 냉동자판기 설치 전 전원, 인터넷, 반입 동선, 기기 규격, 판매 상품을 확인하는 실무 체크리스트입니다.','자판기 설치 전 확인해야 할 7가지 조건',
 f'''<section class="page-intro"><div class="container narrow"><span class="eyebrow">INSTALLATION CHECKLIST</span><h1>자판기 설치 전<br><em>확인해야 할 7가지</em></h1><p class="lead">제품을 구매하기 전에 설치 장소의 전기·통신·반입 조건을 확인하면 예상하지 못한 추가비용을 줄일 수 있습니다.</p></div></section><section class="section"><div class="container narrow"><ol class="steps"><li><strong>기기 모델과 규격</strong><p>최종 모델의 폭·높이·깊이와 문 열림 공간을 확인합니다.</p></li><li><strong>전원 및 소비전력</strong><p>전압, 전원 용량, 접지, 분전반 여유와 다른 기기와의 전력 사용을 확인합니다.</p></li><li><strong>인터넷 연결</strong><p>관리 기능과 결제 시스템에 필요한 통신 수단을 확인합니다.</p></li><li><strong>반입 동선</strong><p>출입문, 엘리베이터, 계단, 바닥 하중, 지게차 필요 여부를 확인합니다.</p></li><li><strong>환기·냉각 공간</strong><p>멀티 및 냉동 모델별 권장 이격거리와 공기 흐름을 확인합니다.</p></li><li><strong>판매 상품과 보관 조건</strong><p>냉장·냉동 요구 온도, 포장 크기, 상품 보충 방식 등을 검토합니다.</p></li><li><strong>배송·설치 추가비용</strong><p>도서산간, 전기·통신 공사, 장거리 반입 등의 비용 발생 여부를 확인합니다.</p></li></ol></div></section>{cta('../../','')}''')

add('about','홈페이지 소개','멀티·냉동자판기와 SAFE24 무인매장 구매 정보, 실제 제품 자료 및 상담 연결 서비스에 대해 안내합니다.','멀티자판기·냉동자판기 구매센터 소개',
 f'''<section class="page-intro"><div class="container narrow"><span class="eyebrow">ABOUT THE SITE</span><h1>좋은 기기를 고르기 위한<br><em>구매 정보의 출발점</em></h1><p class="lead">멀티자판기, 냉동 블록형 자판기, SAFE24 무인매장에 관한 실제 제품 정보를 이해하기 쉽게 정리하고 구매 상담으로 연결합니다.</p></div></section><section class="section"><div class="container narrow">{section_title('OUR GUIDE','정보 제공 원칙')}<div class="two-cards">{card('실제 제품 사양 안내','제품별 규격, 판매 방식, 구매 조건을 확인하기 쉽게 안내합니다. 세부 사양은 모델별로 달라질 수 있습니다.',tag='제품 정보')}{card('고객 중심 구매 상담','고객이 희망하는 제품·상품·설치 환경을 파악하여 상세 견적 상담을 진행할 수 있도록 연결합니다.',tag='구매 상담')}</div><div class="notice"><strong>제품 안내</strong><p>판매 및 제품 안내 협력: 다브인터네셔널 · 자판기 업체: MTS해원. 제품 구매 조건은 신청서를 통해 상담 후 확인하세요.</p></div></div></section>{cta('../','')}''')

# On-site contact form, submitted to a Netlify Function. The form does not use Google Forms.
operator=escape(config.get('operator_name') or '운영사 법적 상호 미설정')
partner=escape(PARTNER)
operator_retention=escape(config.get('operator_retention') or '상담 개시 시 안내')
partner_retention=escape(config.get('partner_retention') or '상담 개시 시 안내')
contact=escape(config.get('operator_contact') or '운영사 연락처 미설정')
privacy_ready=PRIVACY_READY
consent_version=escape(config.get('privacy_consent_version') or '2026-10-v1',quote=True)
form_cta=f'''<form id="inquiry-form" class="inquiry-form" action="/.netlify/functions/submit-lead" method="post" data-consent-version="{consent_version}" novalidate>
<div class="form-row"><div><label for="company">상호명 <abbr title="필수">*</abbr></label><input id="company" name="company" autocomplete="organization" maxlength="80" required placeholder="상호명 또는 창업 예정"></div><div><label for="representative">대표자명 <abbr title="필수">*</abbr></label><input id="representative" name="representative" autocomplete="name" maxlength="40" required placeholder="이름"></div></div>
<div class="form-row"><div><label for="phone">상담 연락처 <abbr title="필수">*</abbr></label><input id="phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" maxlength="25" required placeholder="010-0000-0000"></div><div><label for="email">제품 자료를 받을 이메일 <abbr title="필수">*</abbr></label><input id="email" name="email" type="email" autocomplete="email" maxlength="120" required placeholder="example@email.com"></div></div>
<label for="product">관심상품 <abbr title="필수">*</abbr></label><select id="product" name="product" required><option value="" selected disabled>관심상품 선택</option><option value="멀티자판기">멀티자판기</option><option value="냉동자판기">냉동자판기</option><option value="SAFE24 무인매장">자판기 무인매장 창업·구축</option><option value="상담 후 결정">상담 후 결정</option></select>
<label for="address">설치 예정 사업장 주소 <abbr title="필수">*</abbr></label><input id="address" name="address" autocomplete="street-address" maxlength="200" required placeholder="예: 서울특별시 강남구 역삼동 (상세 번지 선택)">
<div class="form-row"><div><label for="quantity">희망 수량 (선택)</label><select id="quantity" name="quantity"><option value="미정">미정</option><option value="1대">1대</option><option value="2~3대">2~3대</option><option value="4~5대">4~5대</option><option value="6대 이상">6대 이상</option></select></div><div><label for="timeline">도입 희망 시기 (선택)</label><select id="timeline" name="timeline"><option value="미정">미정</option><option value="1개월 이내">1개월 이내</option><option value="1~3개월">1~3개월</option><option value="3개월 이후">3개월 이후</option></select></div></div>
<label for="message">문의사항 (선택)</label><textarea id="message" name="message" rows="4" maxlength="1000" placeholder="제품 사용 목적, 설치 환경, 상담 요청사항을 적어주세요."></textarea>
<div class="anti-bot" aria-hidden="true"><label for="website_url">Website</label><input id="website_url" name="website_url" type="text" tabindex="-1" autocomplete="off"></div>
<fieldset class="consent"><legend>개인정보 동의</legend><label class="checkline"><input type="checkbox" name="collect_agree" value="yes" required><span><strong>[필수] 개인정보 수집·이용 동의</strong><small>처리자: {operator} · 목적: 자판기 구매·설치 상담 접수 및 응대 · 항목: 상호명, 대표자명, 연락처, 관심상품, 이메일, 설치 예정 주소 및 선택 입력 정보 · 보유기간: {operator_retention} · 동의 거부 가능, 거부 시 상담 접수 불가. <a href="../privacy/">자세히 보기</a></small></span></label><label class="checkline"><input type="checkbox" name="share_agree" value="yes" required><span><strong>[필수] 개인정보 제3자 제공 동의</strong><small>제공받는 자: {partner} · 목적: 제품 상담 및 견적·계약·설치 안내 · 항목: 상호명, 대표자명, 연락처, 관심상품, 이메일, 설치 주소 및 선택 입력 정보 · 제공받는 자 보유기간: {partner_retention} · 동의 거부 가능, 거부 시 제휴 상담 연결 불가. 추가 제공 업체는 실제 전달 경로에 맞게 별도 고지합니다.</small></span></label></fieldset>
{'' if privacy_ready else '<div class="notice notice-warning" role="note"><strong>상담 신청 준비 중</strong><p>온라인 상담 신청 서비스가 시작되면 이 페이지에서 바로 문의하실 수 있습니다.</p></div>'}
<button class="btn btn-primary submit" type="submit" {'' if privacy_ready else 'disabled aria-disabled="true"'}>구매·설치 상담 신청하기 <span aria-hidden="true">↗</span></button><p class="form-status" id="inquiry-status" role="status" aria-live="polite">{'' if privacy_ready else '온라인 상담 접수 준비 중입니다.'}</p>
</form>'''
add('contact','멀티자판기·냉동자판기·무인매장 구매 상담','멀티자판기·냉동자판기·무인매장 구매 상담을 신청하세요. 상호명, 연락처, 설치 장소, 관심상품을 접수해 제품별 상담을 진행합니다.','자판기 구매·무인매장 상담 신청',
 f'''<section class="page-intro"><div class="container narrow"><span class="eyebrow">CONTACT</span><h1>자판기 구매·설치 상담,<br><em>홈페이지에서 바로 신청하세요.</em></h1><p class="lead">희망 제품과 설치 장소를 알려주시면 확인 후 구매 조건과 설치 내용을 안내해 드립니다.</p></div></section><section class="section"><div class="container contact-layout"><div><span class="eyebrow">CONSULTATION</span><h2>맞춤 견적을 위해 필요한 정보</h2><ol class="steps"><li><strong>사업장 정보</strong><p>상호명과 대표자명, 설치 예정 지역을 알려주세요.</p></li><li><strong>희망 제품</strong><p>멀티자판기, 냉동자판기 또는 SAFE24 무인매장을 선택하세요.</p></li><li><strong>연락처와 이메일</strong><p>견적과 제품 안내를 받으실 연락처를 남겨주세요.</p></li></ol><div class="notice"><strong>상담 안내</strong><p>상담 문의 전화: {escape(INQUIRY_PHONE)}<br>실제 제품 사양과 최종 구매 조건은 담당자 상담을 통해 안내됩니다.</p></div></div><div class="form-card"><span class="eyebrow">INQUIRY FORM</span><h2>구매 상담 신청</h2><p class="muted">필수 항목을 입력한 뒤 아래에서 개인정보 동의를 확인해 주세요.</p>{form_cta}</div></div></section>''')

add('privacy','개인정보 처리방침','자판기 구매 상담 시 개인정보의 수집·이용과 제휴업체 제공에 관한 사항을 안내합니다.','개인정보 처리방침',
 f'''<section class="page-intro compact"><div class="container narrow"><span class="eyebrow">PRIVACY POLICY</span><h1>개인정보 처리방침</h1><p class="lead">문의 상담 시 처리하는 개인정보를 안내합니다.</p></div></section><section class="section"><div class="container narrow legal"><h2>1. 개인정보 처리자</h2><p>홈페이지 운영사: {operator}<br>연락처: {contact}</p><h2>2. 개인정보 수집 항목과 목적</h2><p>구매·설치 상담 접수와 응대를 위해 상호명, 대표자명, 연락처, 관심상품, 이메일, 설치 예정 주소를 수집합니다. 희망 수량, 도입 시기, 문의사항은 선택 항목입니다. 접수 시각, 접수 ID, 유입 페이지 등 기술적 접수정보도 상담 기록에 저장할 수 있습니다.</p><h2>3. 수집·이용 보유기간</h2><p>{operator_retention}. 관련 법령에 따른 별도 보관 의무가 적용되는 경우 그 근거와 기간을 구체적으로 안내합니다.</p><h2>4. 제3자 제공</h2><p>제공받는 자: {partner}. 목적: 제품 상담, 견적, 계약 및 설치 일정 안내. 제공 항목: 상담 신청 시 입력한 기본·선택 정보. 제공받는 자 보유기간: {partner_retention}.</p><h2>5. 처리 방식</h2><p>홈페이지에서 신청한 정보는 전송 서버를 통해 상담 관리 구글 스프레드시트에 저장됩니다. 신규 접수 알림은 상담 식별번호와 관심상품 정도의 최소 정보만 포함하도록 구성하며, 고객 연락처는 알림 서비스에 전송하지 않습니다.</p><h2>6. 정보주체의 권리</h2><p>개인정보의 열람·정정·삭제 및 처리정지 등의 요청은 위 운영사 연락처로 신청할 수 있습니다. 요청 처리 절차와 파기 방법은 실제 운영 정책을 반영해 안내합니다.</p>{'' if privacy_ready else '<div class="notice notice-warning"><strong>상담 정보 보호 안내</strong><p>개인정보 처리에 관한 상세 정책은 상담 서비스 개시 시 확인하실 수 있습니다.</p></div>'}</div></section>''')

from seo_enhancements import enhance
enhance(PAGES,add)
# New editorial PSEO pages are data-driven but never automatically released.
# Only approved/published and quality-validated records can enter the public build.
from pseo_engine import load_editorial, render_record, render_rss, QualityError
APPROVED, EDITORIAL_REGISTRY = load_editorial(
    ROOT/'pseo/pages.json',
    reserved={p['slug'] for p in PAGES} | {'privacy','contact','about','installation-cases','use-cases'},
    assets_root=ROOT/'assets/img'
)
for record in APPROVED:
    slug=record['slug'].strip('/')
    page_root='../'*len(slug.split('/'))
    add(slug,record['title'],record['description'],record['heading'],
        render_record(record,page_root,cta(page_root)),kind='editorial',
        image='assets/img/'+record['image'])
# Approved location/topic pages become discoverable from the corresponding hub.
if APPROVED:
    hub=next((p for p in PAGES if p['slug']=='installation-locations'),None)
    if hub:
        listing=''.join('<article class="info-card"><h3><a href="../'+escape(r['slug'].strip('/'))+'/">'+escape(r['keyword'])+'</a></h3><p>'+escape(r['description'])+'</p><a class="text-link" href="../'+escape(r['slug'].strip('/'))+'/">상세 안내 보기 ↗</a></article>' for r in APPROVED)
        hub['body']+='<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">새로 공개한 안내</span><h2>상세 설치·구매 안내</h2></div><div class="three-cards">'+listing+'</div></div></section>'

(ROOT/'pseo/release-report.json').write_text(json.dumps({
    'published_count':len(APPROVED),'approved_pages':[x['slug'] for x in APPROVED],
    'registry':EDITORIAL_REGISTRY,'note':'초안과 검토중 콘텐츠는 공개 HTML 및 sitemap/rss에 포함되지 않습니다.'
},ensure_ascii=False,indent=2),encoding='utf-8')
nav=[('멀티자판기','multi-vending-machine'),('냉동자판기','frozen-vending-machine'),('무인매장 창업','unmanned-store'),('설치 장소별 사례','installation-locations'),('구매 조건','multi-purchase')]

for p in PAGES:
    slug=p['slug']; depth=len(slug.split('/')) if slug else 0; root='../'*depth if depth else './'
    def href(target):return root+ (target+'/' if target else '')
    def asset(x):return root+x
    canonical=f'<link rel="canonical" href="{escape(page_url(slug))}">' if URL else ''
    robots_meta='<meta name="robots" content="noindex,follow">' if (IS_NETLIFY_PREVIEW or not URL or slug in ('contact','privacy')) else ''
    ogurl=f'<meta property="og:url" content="{escape(page_url(slug))}">' if URL else ''
    naver_meta=(f'<meta name="naver-site-verification" content="{escape(config["naver_site_verification"])}">' if config.get('naver_site_verification') else '')
    google_meta=(f'<meta name="google-site-verification" content="{escape(config["google_site_verification"])}">' if config.get('google_site_verification') else '')
    structured=[{'@type':'WebSite','@id':URL+'#website','name':SITE,'inLanguage':'ko','url':URL,'publisher':{'@id':URL+'#organization'}} if URL else {'@type':'WebSite','name':SITE,'inLanguage':'ko'}]
    if URL and config.get('operator_name'):
        structured.append({'@type':'Organization','@id':URL+'#organization','name':config['operator_name'],'url':URL})
    if URL:
        structured.append({'@type':'WebPage','@id':page_url(slug)+'#webpage','name':p['title'],'description':p['desc'],'inLanguage':'ko','url':page_url(slug),'isPartOf':{'@id':URL+'#website'}})
        if slug:
            structured.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'홈','item':URL},{'@type':'ListItem','position':2,'name':p['heading'].replace('<br>',' ').replace('<em>','').replace('</em>',''),'item':page_url(slug)}]})
    ld=json.dumps({'@context':'https://schema.org','@graph':structured},ensure_ascii=False).replace('</','<\\/')
    nav_html=''.join(f'<a href="{href(target)}"'+(' aria-current="page"' if slug==target else '')+f'>{text}</a>' for text,target in nav)
    breadcrumb=('' if not slug else f'<div class="container crumb"><a href="{href("")}">홈</a><span aria-hidden="true">/</span><span>{escape(p["heading"])}</span></div>')
    head=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light"><meta name="theme-color" content="#102c3d"><title>{escape(p['title'] if SITE in p['title'] else p['title']+' | '+SITE)}</title><meta name="description" content="{escape(p['desc'])}">{robots_meta}{canonical}{naver_meta}{google_meta}<meta property="og:type" content="website"><meta property="og:site_name" content="{escape(SITE)}"><meta property="og:locale" content="ko_KR"><meta property="og:title" content="{escape(p['title'])}"><meta property="og:description" content="{escape(p['desc'])}"><meta property="og:image" content="{escape(urljoin(URL,'assets/img/og-cover.jpg')) if URL else asset('assets/img/og-cover.jpg')}">{ogurl}<link rel="alternate" type="application/rss+xml" title="자판기플랜 신규 콘텐츠" href="{asset('rss.xml')}"><link rel="icon" type="image/svg+xml" href="{asset('assets/favicon.svg')}"><link rel="stylesheet" href="{asset('assets/site.css')}"><script type="application/ld+json">{ld}</script></head>'''
    header=f'''<body><a class="skip-link" href="#main">본문 바로가기</a><header class="site-header"><div class="container header-inner"><a class="brand" href="{href('')}" aria-label="{escape(SITE)} 홈으로"><span class="brand-symbol">V<span></span></span><span class="brand-copy"><strong>{escape(SITE)}</strong><small>멀티자판기 · 냉동자판기 · 무인매장</small></span></a><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="메뉴 열기"><span></span><span></span><span></span></button><nav class="site-nav" id="site-nav" aria-label="주 메뉴">{nav_html}<a class="nav-cta" href="{href('contact')}">견적 상담 <span aria-hidden="true">↗</span></a></nav></div></header>'''
    footer=f'''<footer class="site-footer"><div class="container footer-upper"><div><a class="footer-brand" href="{href('')}">{escape(SITE)}<span>.</span></a><p>멀티자판기 · 냉동자판기 · 자판기 무인매장<br>제품 비교, 설치 조건, 창업비용 및 구매 상담을 안내합니다.</p></div><div class="footer-links"><div><strong>제품·서비스</strong><a href="{href('multi-vending-machine')}">멀티자판기</a><a href="{href('frozen-vending-machine')}">냉동자판기</a><a href="{href('unmanned-store')}">무인매장 창업</a></div><div><strong>고객 안내</strong><a href="{href('installation-locations')}">설치 장소별 안내</a><a href="{href('guides/vending-installation')}">설치 전 체크리스트</a><a href="{href('contact')}">견적 상담</a></div></div></div><div class="container footer-bottom"><span>© 2026 {escape(SITE)}. All rights reserved.</span><span><a href="{href('privacy')}">개인정보 처리방침</a></span></div></footer><a class="floating-cta" href="{href('contact')}" aria-label="견적 상담 신청">견적 상담 <span aria-hidden="true">↗</span></a><script defer src="{asset('assets/site.js')}"></script></body></html>'''
    modal=''
    if slug not in ('contact','privacy'):
        # The same consent fields used in the dedicated fallback page are reused once per page.
        # Do not change ID names: each rendered page has only one inquiry form.
        local_form=form_cta.replace('href="../privacy/"','href="'+href('privacy')+'"')
        modal=('''<div class="inquiry-overlay" id="inquiry-overlay" hidden>'''
               '''<div class="inquiry-backdrop" data-close-inquiry="true"></div>'''
               '''<section class="inquiry-dialog" role="dialog" aria-modal="true" aria-labelledby="dialog-title" tabindex="-1">'''
               '''<div class="dialog-heading"><div><span class="eyebrow">PRODUCT INQUIRY</span>'''
               '''<h2 id="dialog-title">자판기 구매·설치 상담</h2>'''
               '''<p class="dialog-description">관심상품과 설치 장소를 남겨 주세요.</p></div>'''
               '''<button type="button" class="dialog-close" data-close-inquiry="true" aria-label="상담 창 닫기">×</button></div>'''
               +local_form+'</section></div>')
    html=head+header+breadcrumb+'<main id="main">'+p['body']+'</main>'+footer.replace('</body></html>',modal+'</body></html>')

    dest=OUT/slug/'index.html' if slug else OUT/'index.html'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(html,encoding='utf-8')

# Search crawler metadata. Domain-specific outputs omitted until configured.
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\n'+(f'Sitemap: {URL}sitemap.xml\n' if URL else ''),encoding='utf-8')
if URL:
    editorial_dates={r['slug'].strip('/'):r['published_on'] for r in APPROVED}
    # Original curated pages retain their established editorial revision date.
    # New pages must use their real, approved publication date from pseo/pages.json.
    links=[f'<url><loc>{escape(page_url(p["slug"]))}</loc><lastmod>{editorial_dates.get(p["slug"], "2026-10-29")}</lastmod></url>' for p in PAGES if p['slug'] not in ('privacy','contact')]
    xml_head='<?xml version="1.0" encoding="UTF-8"?>'
    if len(links)<=500:
        (OUT/'sitemap.xml').write_text(xml_head+'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(links)+'</urlset>',encoding='utf-8')
    else:
        submaps=[]
        for i in range(0,len(links),500):
            name=f'sitemap-{i//500+1}.xml'
            (OUT/name).write_text(xml_head+'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(links[i:i+500])+'</urlset>',encoding='utf-8')
            submaps.append(f'<sitemap><loc>{escape(URL+name)}</loc></sitemap>')
        (OUT/'sitemap.xml').write_text(xml_head+'<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(submaps)+'</sitemapindex>',encoding='utf-8')
# RSS is intentionally empty until a real new editorial page has been published.
# The original curated pages have no independently verified publication dates.
(OUT/'rss.xml').write_text(render_rss(URL or 'https://japangi-plan.netlify.app/',SITE,APPROVED),encoding='utf-8')
# custom 404 fallback
(OUT/'404.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><title>페이지를 찾을 수 없습니다</title><meta name="viewport" content="width=device-width,initial-scale=1"><body style="font:18px sans-serif;text-align:center;padding:10vh 1rem"><h1>페이지를 찾을 수 없습니다</h1><p><a href="/">홈으로 돌아가기</a></p></body></html>',encoding='utf-8')
print('Generated',len(PAGES),'pages in',OUT)
print('Canonical domain:',URL or '(not set; intentionally omitted)')
print('On-site inquiry form generated:', FORM_READY)
print('Privacy details verified:', PRIVACY_READY)
