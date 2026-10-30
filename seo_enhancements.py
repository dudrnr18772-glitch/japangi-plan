# -*- coding: utf-8 -*-
"""Editorial SEO enhancements and location-specific genuine installation photo pages.
These are source-level changes; rebuilding reproduces all content.
"""
from html import escape
import re

def strip_section(body, marker):
    pattern=re.compile(r'<section\b[^>]*>.*?</section>', re.DOTALL)
    return pattern.sub(lambda m: '' if marker in m.group(0) else m.group(0),body)

def feature_block(kicker, heading, paragraphs, checks=(), link=None, label=None):
    paras=''.join('<p>'+escape(x)+'</p>' for x in paragraphs)
    bullets=''.join('<li>'+escape(x)+'</li>' for x in checks)
    more=('<p><a class="text-link" href="'+link+'">'+escape(label or '관련 내용 확인')+' ↗</a></p>') if link else ''
    return '<section class="section article-section"><div class="container narrow"><span class="eyebrow">'+escape(kicker)+'</span><h2>'+escape(heading)+'</h2>'+paras+('<ul class="check-list">'+bullets+'</ul>' if bullets else '')+more+'</div></section>'

def comparison_block(heading, columns, rows, caption=''):
    head=''.join('<th scope="col">'+escape(x)+'</th>' for x in columns)
    data=''.join('<tr>'+''.join('<td>'+escape(str(x))+'</td>' for x in row)+'</tr>' for row in rows)
    return '<section class="section tinted"><div class="container"><div class="section-heading"><span class="eyebrow">COMPARISON</span><h2>'+escape(heading)+'</h2></div><div class="responsive-table"><table><thead><tr>'+head+'</tr></thead><tbody>'+data+'</tbody></table></div>'+('<p class="fineprint">'+escape(caption)+'</p>' if caption else '')+'</div></section>'

def photo_section(root, heading, items):
    cards=''.join('<article class="photo-tile"><img loading="lazy" src="'+root+'assets/img/'+path+'" alt="'+escape(alt)+'" width="660" height="790"><div><h3>'+escape(title)+'</h3><p>'+escape(body)+'</p></div></article>' for path,alt,title,body in items)
    return '<section class="section"><div class="container"><div class="section-heading"><span class="eyebrow">REAL INSTALLATIONS</span><h2>'+escape(heading)+'</h2><p>아래 사진은 MTS해원이 제공한 설치 사례 자료에서 가져온 실제 현장 사진입니다. 장소마다 제품 구성과 설치 조건은 달라질 수 있습니다.</p></div><div class="photo-grid">'+cards+'</div></div></section>'

def enhance(pages,add):
    byslug={p['slug']:p for p in pages}
    # Remove the duplicate installation gallery, generic use-cases and unnecessary about page.
    pages[:]=[p for p in pages if p['slug'] not in ('installation-cases','use-cases','about')]
    byslug={p['slug']:p for p in pages}
    home=byslug['']
    home['title']='자판기플랜 | 멀티자판기·냉동자판기 구매 및 무인매장 창업'
    home['heading']='멀티자판기·냉동자판기 구매와 무인매장 창업 안내'
    home['desc']='멀티자판기와 냉동자판기 구매를 비교하고, 무인매장 창업에 필요한 기기 구성·가격·설치 조건을 알아보세요. 학교·호텔 등 설치 사례와 구매 상담까지 안내합니다.'
    home['body']=home['body'].replace('상품에 맞는 자판기,<br><em>공간에 맞는 무인매장.</em>','멀티자판기·냉동자판기 구매와<br><em>무인매장 창업 안내</em>')
    home['body']=home['body'].replace('SMART MULTI','SMART MULTI')
    home['body']=strip_section(home['body'],'REAL INSTALLATIONS')
    home['body']=home['body'].replace('실제 사례</strong>','설치 사례</strong>')
    home['body']=home['body'].replace('<strong>SAFE24</strong><span>다기기 매장 구성</span>', '<strong>무인매장</strong><span>다기기 매장 구성</span>')
    home['body']=home['body'].replace('<h3>SAFE24 무인매장</h3>', '<h3>무인매장 창업·구축</h3>')
    home['body']=home['body'].replace('실제 제품 이미지','제품 구성 연출 이미지')
    home['body']=home['body'].replace('실제 설치 사례','설치 장소별 실제 사례')
    home['body']=home['body'].replace('href="installation-cases/"','href="installation-locations/"')
    home['body'] += feature_block('BUYING GUIDE','자판기 구매는 무엇부터 비교해야 할까요?',[
      '자판기를 구매하려면 먼저 판매할 상품을 정해야 합니다. 음료와 간식처럼 형태가 다른 상품을 함께 판매한다면 멀티자판기의 트레이 구성과 배출 방식을 살펴보고, 냉동식품이 중심이라면 냉동자판기의 블록 구성과 요구 온도를 확인하는 것이 좋습니다.',
      '기계 가격만 비교하면 카드결제 구성, 설치비, 반입 작업, 전원·통신 준비 비용을 놓치기 쉽습니다. 특히 구형 음료 전용 자판기와 스마트 멀티자판기는 상품 구성과 운영 기능이 달라 단순한 가격 비교보다 용도에 맞는 제품 선택이 중요합니다.'
    ],['판매할 상품 종류와 포장 규격','설치할 공간의 전원·환기·반입 조건','일시불·할부·운영 비용과 A/S 범위'],'multi-vending-machine/','멀티자판기 구매 기준 보기')
    home['body'] += '<section class="section tinted"><div class="container"><div class="section-heading"><span class="eyebrow">INSTALLATION LOCATIONS</span><h2>설치 장소별 실제 자판기 사진</h2><p>학교와 호텔처럼 이용 고객과 판매 목적이 다른 공간을 실제 설치 사진과 함께 살펴보세요.</p></div><div class="two-cards"><a class="location-photo-card" href="school-vending-machine/"><img src="assets/img/school-real-01.webp" loading="lazy" alt="실제 학교 시설에 설치된 멀티자판기"/><div><h3>학교 자판기</h3><p>학교·학원 설치 사례와 상품 구성·운영 조건</p></div></a><a class="location-photo-card" href="hotel-vending-machine/"><img src="assets/img/hotel-real-01.webp" loading="lazy" alt="실제 숙박시설에 설치된 스마트 자판기"/><div><h3>호텔 자판기</h3><p>호텔·숙박시설 설치 사례와 편의상품 구성</p></div></a></div><p class="section-link"><a class="text-link" href="installation-locations/">설치 장소별 안내 전체 보기 ↗</a></p></div></section>'

    multi=byslug['multi-vending-machine']
    multi['title']='멀티자판기 가격·구매·설치조건 | 자판기플랜'
    multi['heading']='멀티자판기 가격과 구매·설치 조건'
    multi['desc']='멀티자판기 구매 전 알아야 할 가격 구성, 판매 가능 상품, 키오스크·결제 기능, 트레이 구성, 설치 조건과 일시불·할부 안내를 확인하세요.'
    multi['body']+=feature_block('MULTI VENDING BASICS','멀티자판기는 어떤 경우에 적합할까요?',[
      '멀티자판기는 음료, 과자, 소형 생활용품처럼 서로 다른 상품을 한 기기에서 판매하려는 경우에 검토할 수 있는 장비입니다. 상품별 크기와 무게에 따라 트레이 구성을 맞추는 것이 중요하며, 배출 방식과 수납 가능 수량은 모델별로 달라집니다.',
      '기존 음료 전용 자판기를 찾는 고객과는 구매 목적이 다를 수 있습니다. 구형 음료수자판기와 초기 가격만 비교하기보다 판매 품목의 폭, 키오스크 결제 기능, 재고 확인과 관리 편의성을 함께 따져보는 것이 현실적입니다.'
    ],['상품별 포장 크기·무게·온도 조건 확인','설치 장소의 이용자와 예상 판매 품목 구분','현장 전원·통신·반입 가능 여부 확인'])
    multi['body']+=comparison_block('멀티자판기와 기존 음료 전용 자판기의 차이',
      ['비교 항목','스마트 멀티자판기','기존 음료 전용 자판기'],[
       ['판매 상품','음료·간식·소형 생활용품 등 복합 구성 검토','음료 판매 중심'],
       ['상품 수납','트레이 조합과 상품별 설정 검토','음료 규격에 맞춘 구조가 일반적'],
       ['결제·관리','화면 기반 결제·재고 관리 기능 확인','모델과 연식에 따라 기능 차이 큼'],
       ['가격 판단','복합 운영 기능과 사후관리 포함 비교','중고·구형 제품 가격과 직접 단순 비교 주의']
      ],'비교는 제품 선택을 위한 일반적인 참고사항입니다. 실제 적용 기능과 가격은 모델별로 다릅니다.')
    multi['body']+=feature_block('INSTALLATION','멀티자판기 설치에서 놓치기 쉬운 조건',[
      '대표 모델 자료에는 폭 955mm·깊이 920mm·높이 1,970mm로 안내된 사양이 있습니다. 이 수치는 모든 모델의 규격이 아니므로 구입할 제품을 먼저 결정한 뒤 출입문·엘리베이터·설치 위치를 확인해야 합니다.',
      '기기 앞 상품 인출 공간, 문 열림 범위, 바닥의 평탄도, 전원과 통신 환경도 함께 점검해야 합니다. 특히 학교나 호텔처럼 통행량이 많은 시설은 이용객이 기계 앞에 서 있어도 통로가 확보되는지가 중요합니다.'
    ],['반입 시 출입문·엘리베이터 유효 폭','접지 및 전력 용량·콘센트 위치','상품 보충 작업과 고객 통행 공간'],'../guides/vending-installation/','자판기 설치 체크리스트')
    multi['body']+=feature_block('PRICE & CONTRACT','멀티자판기 가격은 어떻게 확인하면 될까요?',[
      '제공된 2026년 8월 구매 조건에는 일시불 730만 원(VAT 별도), 36개월 할부 월 23만 원(VAT 별도)이 안내되어 있습니다. 다만 계약금·보증금·보증보험료, 설치 지역에 따른 추가 비용이 별도이므로 이 금액만으로 총구매비를 판단할 수는 없습니다.',
      '구매를 검토할 때는 본체 사양, 계약 방식, 부가세, 배송·설치 비용, A/S 범위를 동일한 기준으로 비교하는 것이 좋습니다. 실제 적용 금액은 공급업체의 최신 견적을 확인해야 합니다.'
    ],[],'../multi-purchase/','일시불·할부 구매 조건 비교')

    frozen=byslug['frozen-vending-machine']
    frozen['title']='냉동자판기 가격·구매·설치 | 냉동식품 자판기 안내'
    frozen['heading']='냉동자판기 구매와 냉동식품 판매 조건'
    frozen['desc']='냉동자판기의 블록형 보관 구조, 밀키트·아이스크림 등 판매 상품, 냉동 온도·전원·설치 조건, 견적 확인 항목을 자세히 안내합니다.'
    frozen['body']+=feature_block('FROZEN PRODUCTS','냉동자판기에 어떤 식품을 넣을 수 있을까요?',[
     '냉동자판기는 아이스크림, 밀키트, 포장 냉동식품처럼 냉동 상태로 보관해야 하는 상품을 판매하는 데 활용됩니다. 다만 기기에 들어간다고 모두 판매할 수 있는 것은 아닙니다. 식품별 표시 보관 온도와 포장 크기, 유통·판매 형태가 실제 기기의 기능에 맞는지 확인해야 합니다.',
     '같은 냉동식품이라도 아이스크림 컵과 밀키트 박스는 필요한 공간이 다릅니다. 따라서 상품의 가로·세로·높이, 포장 중량, 예상 판매량을 정리한 뒤 블록 수와 크기를 결정하는 편이 좋습니다.'
    ],['판매할 식품의 포장 규격 목록 작성','식품별 권장 보관 온도 확인','블록 개수와 재고 보충 주기 검토'])
    frozen['body']+=comparison_block('냉동자판기 구매 전 비교할 항목',
     ['구분','중점 확인 사항','구매 판단 기준'],[
     ['보관 방식','블록형 구획과 문 개방 구조','상품별 공간 배분이 가능한가'],
     ['온도 조건','목표 온도와 유지 관리','판매 식품의 요구 온도를 충족하는가'],
     ['운영 기능','상품 선택·결제·재고 확인','관리 담당자가 운영하기 편한가'],
     ['현장 설치','전원·환기·반입 동선','설치와 유지관리 공간이 충분한가'],
     ['비용','본체·배송·추가 공사·유지비','총도입비를 비교했는가'],
    ])
    frozen['body']+=feature_block('FROZEN LOCATION','냉동자판기 설치 시 주의할 점',[
      '냉동자판기는 실내 온도와 환기 조건에 따라 냉각 장치의 작동 부담이 달라질 수 있습니다. 제품별 권장 이격거리와 소비전력은 실제 선택 모델의 사양을 기준으로 확인해야 하며, 배전 용량이 부족한 현장은 별도 공사가 필요할 수 있습니다.',
      '아이스크림이나 냉동 밀키트처럼 식품을 판매할 때는 판매자의 영업신고·보관·상품 관리 의무도 운영 형태에 따라 검토해야 합니다. 기기 공급 범위와 운영자의 식품 관리 책임을 구분하는 것이 중요합니다.'
    ],[],'../guides/vending-installation/','설치 전 체크리스트')

    safe=byslug['safe24-unmanned-store']
    safe['slug']='unmanned-store'
    safe['title']='무인매장 창업비용·자판기 구성과 설치 안내'
    safe['heading']='무인매장 창업비용과 자판기 구성'
    safe['desc']='자판기를 활용한 무인매장 창업을 준비한다면 장비 구입비·인테리어·전기·상품비를 구분해 보세요. 멀티·냉동자판기 조합과 SAFE24 구성 예시를 안내합니다.'
    safe['body']=safe['body'].replace('자판기 여러 대로 완성하는<br><em>SAFE24 무인매장</em>','무인매장 창업비용과<br><em>자판기 구성 방법</em>')
    safe['body']=safe['body'].replace('SAFE24 / UNMANNED STORE','UNMANNED VENDING STORE')
    safe['body']=safe['body'].replace('SAFE24 무인매장 관련 질문','무인매장 창업 관련 질문')
    safe['body']+=feature_block('STORE START','자판기 무인매장은 어떤 방식으로 운영하나요?',[
      '자판기 기반 무인매장은 멀티자판기와 냉동자판기 등을 한 공간에 배치하고, 상품 보충과 재고·매출 관리를 운영자가 담당하는 방식입니다. 일반 무인점포와 달리 판매 기기 자체가 상품 선택과 결제·인출 기능을 담당하므로 점포 규모보다 적절한 기기 조합과 운영 동선이 중요합니다.',
      'SAFE24는 이러한 방식으로 다양한 기기를 조합하는 무인매장 제안 명칭입니다. 처음부터 SAFE24라는 이름을 알아야 하는 것은 아닙니다. 무인매장 창업을 고민하는 고객이 기기 구성과 비용을 이해한 뒤 선택할 수 있도록 안내합니다.'
    ])
    safe['body']+=comparison_block('기기 대수에 따른 무인매장 구성 예시',
     ['유형','기기 조합 예시','검토할 사항'],[
     ['소형 예시','멀티 1대 + 냉동 1대','설치 면적·상품군의 중복 확인'],
     ['중형 예시','멀티 2대 + 냉동 2대','전기 용량·보충 동선 검토'],
     ['확장 예시','판매 상품에 따라 5대 이상','회전율·관리 인력·시설비 검토'],
    ],'대수와 조합은 이해를 돕기 위한 계획 예시이며 실제 공급 패키지나 보장 수익을 의미하지 않습니다.')
    safe['body']+=feature_block('STORE BUDGET','무인매장 창업비용, 무엇이 포함될까요?',[
      '무인매장 창업비용은 자판기 구매비와 인테리어 비용만으로 끝나지 않습니다. 임대차 보증금, 전기·통신 시설, 운송·반입, 냉동 관련 설비, 초기 상품 매입과 재고 관리 비용을 구분해야 전체 예산을 비교할 수 있습니다.',
      'SAFE24 제공 자료에는 10평 인테리어 참고 금액 약 2,000만 원이 제시되어 있지만, 이 금액이 전체 창업비용을 뜻하는 것은 아닙니다. 자판기 구입비와 임대차 비용, 상품비 등은 별도로 계산해야 합니다. 매장 조건과 공사 범위에 따라 실제 비용은 달라집니다.'
    ],['기기 구매비와 계약 방식','인테리어·전기·통신·반입 비용','보증금·초도 상품·운영 예비비'])
    safe['body']+=feature_block('OPERATIONS','무인매장 운영에서 미리 정할 것',[
      '무인 운영이라도 상품 발주·보충, 소비기한 관리, 위생·청결, 문의 대응, 기기 점검을 담당할 운영자는 필요합니다. 냉동식품 취급 여부와 영업 형태에 따라 신고·시설 기준도 별도로 확인해야 합니다.',
      '구매 상담에서는 매장 주소와 예상 면적, 주요 판매 상품, 예산 범위를 함께 전달하면 적합한 기기 구성에 대한 논의를 구체적으로 시작할 수 있습니다.'
    ],[],'../contact/?product=safe24','무인매장 구축 상담 신청')

    purchase=byslug['multi-purchase']
    purchase['title']='멀티자판기 가격·일시불·36개월 할부 구매 조건'
    purchase['heading']='멀티자판기 가격과 일시불·할부 조건'
    purchase['desc']='멀티자판기 일시불·36개월 할부 가격과 계약금·보증금·보험료·설치비 등 추가 비용을 구분해 총구매비를 확인하는 방법을 안내합니다.'
    purchase['body']+=feature_block('TOTAL COST','멀티자판기 총구매비를 비교하는 방법',[
     '일시불과 할부는 현금흐름이 다르기 때문에 본체 금액과 월 납입액만으로 비교하기 어렵습니다. 제공된 조건에는 일시불 730만 원(VAT 별도), 36개월 할부 월 23만 원(VAT 별도)이 안내되어 있으며, 할부 기간 전체의 단순 납입액은 828만 원(VAT 별도)입니다. 다만 보증금·보증보험료 등은 별도이고 그 성격도 확인해야 합니다.',
     '장비 도입 예산을 검토할 때는 부가세, 계약금·보증금, 설치비, 추후 유지관리 비용과 설치 환경에서 발생하는 추가 작업을 구분해 확인하는 편이 좋습니다. 실제 계약 금액과 조건은 현재 견적서에서 다시 확인해야 합니다.'
    ],['할부 월 납입액 × 계약기간과 초기 비용을 분리','계약금·보증금의 반환·정산 조건 확인','설치·A/S 포함 범위 명확히 확인'])
    # no fake case photos; new combined location hub + separate pilot pages, real images only.
    add('installation-locations','설치 장소별 자판기 추천·실제 설치 사례','학교·학원, 호텔·숙박시설, 병원, 스포츠시설에 설치된 실제 자판기 사진과 장소별 상품 구성·설치 조건을 함께 비교합니다.','설치 장소별 자판기 선택과 실제 사례',
      '<section class="page-intro"><div class="container narrow"><span class="eyebrow">INSTALLATION LOCATIONS</span><h1>설치 장소별 자판기 선택과<br><em>실제 설치 사례</em></h1><p class="lead">학교 자판기부터 호텔·병원·스포츠시설 자판기까지, 공간의 이용자와 판매 상품에 맞는 구성 방법을 사진과 함께 살펴보세요.</p></div></section>'+
      feature_block('LOCATION GUIDE','설치 장소에 따라 필요한 자판기가 달라지는 이유',[
       '학교의 쉬는 시간과 호텔의 심야 시간대는 자판기가 사용되는 방식이 다릅니다. 같은 모델이라도 이용자의 연령과 방문 시간, 판매 상품, 보충 담당자의 접근성에 따라 실제 운영 방식이 달라집니다.',
       '설치사례 사진은 해당 공간에서 기기가 어떻게 배치되는지 이해하는 데 도움이 됩니다. 다만 사진에 있는 기기 구성과 판매량이 다른 장소에서도 그대로 적용되는 것은 아니므로 도입 전 실제 설치 조건을 확인하는 것이 중요합니다.'
      ])+
      '<section class="section tinted"><div class="container"><div class="two-cards"><a class="location-photo-card" href="../school-vending-machine/"><img src="../assets/img/school-real-01.webp" alt="제공된 학교 현장에 실제 설치된 자판기" loading="lazy"><div><h2>학교 자판기 설치</h2><p>학교·학원 실제 설치 사진, 상품 종류와 안전한 설치 공간 선택</p></div></a><a class="location-photo-card" href="../hotel-vending-machine/"><img src="../assets/img/hotel-real-01.webp" alt="제공된 호텔 현장에 실제 설치된 자판기" loading="lazy"><div><h2>호텔 자판기 설치</h2><p>숙박시설 실제 설치 사진, 음료·편의용품 구성과 보충 동선</p></div></a></div></div></section>'+
      photo_section('../','스포츠시설·병원 등 다른 설치 유형',[
       ('sports-real-01.webp','스포츠시설에 설치된 멀티자판기 사진','스포츠시설','운동 전후 이용자 수요에 맞춘 상품 구성과 설치 위치 검토'),
       ('hospital-real-01.webp','병원 시설 내 설치된 멀티자판기 사진','병원·의료시설','환자와 방문객의 이용 동선을 고려한 설치 조건 검토')
      ])+
      '<section class="section tinted"><div class="container narrow"><span class="eyebrow">NEXT STEP</span><h2>설치 장소가 정해졌다면</h2><p>설치 주소, 예상 상품군, 전기·통신 준비 상태, 예상 구매 수량을 확인해 상담을 신청할 수 있습니다. 기기 규격과 반입 동선은 선택한 모델에 맞춰 검토합니다.</p><p><a class="text-link" href="../guides/vending-installation/">설치 전 체크리스트 확인 ↗</a></p></div></section>')
    add('school-vending-machine','학교 자판기 설치·구매 | 실제 학교 설치 사진과 선택 기준','학교 자판기 설치를 검토한다면 실제 학교·학원 설치 사진, 음료·간식 상품 구성, 전원·안전·보충 동선과 멀티자판기 구매 상담 정보를 확인하세요.','학교 자판기 설치와 구매 전 확인할 사항',
     '<section class="page-intro"><div class="container narrow"><span class="eyebrow">SCHOOL VENDING MACHINE</span><h1>학교 자판기 설치와<br><em>구매 전 확인할 사항</em></h1><p class="lead">학교·학원에 자판기를 설치할 때는 학생 이용 시간, 판매 가능 상품, 기기 앞 안전한 통행 공간, 상품 보충 담당자까지 함께 고려해야 합니다.</p></div></section>'+
      feature_block('SCHOOL INSTALLATION','학교 자판기, 어떤 상품부터 준비하나요?',[
       '학교와 학원에서는 쉬는 시간과 점심시간처럼 짧은 시간에 이용이 집중될 수 있습니다. 생수·음료·포장 간식 등 학교 정책과 이용자 특성에 맞는 품목을 먼저 선정하고, 상품 규격에 따라 트레이 구성을 검토하는 것이 좋습니다.',
       '멀티자판기는 한 대의 기기에서 여러 상품을 구성할 수 있지만, 판매 품목의 제한 여부와 결제 방식, 위치별 혼잡 가능성은 학교 측과 미리 확인해야 합니다.'
      ],['학생 이동 동선과 기기 앞 대기 공간','학교 내부 허용 판매 품목·운영 시간','전원·통신·상품 보충 경로'])+
      photo_section('../','실제 학교·학원 자판기 설치 사진',[
       ('school-real-01.webp','학교 교육시설 공간에 실제 설치된 스마트 멀티자판기','학교 내부 설치','학교 내 공용 공간에 배치된 멀티자판기 사례'),
       ('school-real-02.webp','학교 공용 공간에 실제 설치된 멀티자판기 두 대','교육시설 복수 기기','이용 동선과 기기 간격을 함께 살펴볼 수 있는 설치 사례'),
       ('school-real-03.webp','교육시설에 설치된 두 대의 자판기','학교·학원 설치 사례','상품 구성을 달리한 기기의 배치와 접근성을 참고할 수 있는 사진')
      ])+
      feature_block('SCHOOL CHECKLIST','학교 자판기 설치 상담 전에 준비할 정보',[
       '학교명과 설치 예정 공간의 위치, 희망 상품, 사용 가능한 전기·통신 조건, 구입 또는 공급 방식을 확인하면 상담이 더 구체적으로 진행됩니다. 정확한 비용은 제품과 설치 환경에 따라 달라집니다.',
       '기기를 몇 대 설치할지 고민된다면 이용 예상 인원, 판매 품목의 종류, 상품 보충 주기 등을 먼저 정리하는 것이 좋습니다.'
      ],[],'../contact/?product=multi','학교 자판기 설치 상담')+
      '<section class="section tinted"><div class="container narrow"><span class="eyebrow">RELATED</span><h2>함께 확인할 내용</h2><p><a class="text-link" href="../multi-vending-machine/">멀티자판기 기능·가격 확인 ↗</a> · <a class="text-link" href="../installation-locations/">다른 설치 장소 보기 ↗</a></p></div></section>')
    add('hotel-vending-machine','호텔 자판기 구매·설치 | 실제 숙박시설 설치 사례','호텔·숙박시설 자판기 도입을 검토한다면 실제 설치 사진, 생수·음료·간식·편의용품 구성, 로비·공용층 설치 조건과 제품 상담 정보를 확인하세요.','호텔 자판기 구매와 설치 사례',
     '<section class="page-intro"><div class="container narrow"><span class="eyebrow">HOTEL VENDING MACHINE</span><h1>호텔 자판기 구매와<br><em>실제 설치 사례</em></h1><p class="lead">호텔 로비와 공용층에 자판기를 설치하면 투숙객이 생수·간식·편의용품을 구매할 수 있습니다. 설치 위치와 상품 구성, 보충 방식이 핵심입니다.</p></div></section>'+
      feature_block('HOTEL USE CASE','호텔 자판기에는 어떤 상품이 적합할까요?',[
       '호텔 자판기에는 생수·음료·포장 간식뿐 아니라 세면도구 등 소형 편의용품을 함께 구성하는 경우가 있습니다. 실제 투숙객의 체류시간과 객실 구성, 주변 편의점 접근성을 살펴보면 상품군을 정하는 데 도움이 됩니다.',
       '로비와 공용층은 이동 동선과 조명, 소음, 전원 위치가 중요합니다. 기기 앞에 사람이 서 있어도 통로를 방해하지 않아야 하며, 관리 직원이 상품을 보충하기 쉬운 위치인지도 확인해야 합니다.'
      ],['자주 찾는 생수·음료·간식·편의용품','객실·로비와 공용층 사이의 동선','상품 보충 및 민원 대응 담당자'])+
      photo_section('../','실제 호텔·숙박시설 자판기 설치 사진',[
       ('hotel-real-01.webp','실제 호텔 유리창 옆에 설치된 자판기','숙박시설 실내 설치','투숙객이 접근하기 쉬운 실내 공용 공간 배치 사례'),
       ('hotel-real-02.webp','실제 숙박시설 내부에 설치된 멀티자판기','로비·공용층 설치','건물 내 동선을 고려한 기기 배치와 이용 공간'),
       ('hotel-real-03.webp','호텔 내부에 설치된 여러 대의 멀티자판기','여러 대의 자판기','판매할 상품군이 다양할 때 고려하는 복수 기기 사례')
      ])+
      feature_block('HOTEL CHECKLIST','호텔 자판기 설치 전 확인할 내용',[
       '도입 목적이 매출 보조인지 투숙객 편의 제공인지에 따라 상품 구성과 기기 수량이 달라집니다. 설치 장소 사진, 설치 예정 층, 전원·통신 여건, 희망 제품 수량을 미리 정리하면 구매 상담이 수월합니다.'
      ],[],'../contact/?product=multi','호텔 자판기 구매 상담')+
      '<section class="section tinted"><div class="container narrow"><span class="eyebrow">RELATED</span><h2>함께 확인할 내용</h2><p><a class="text-link" href="../multi-vending-machine/">멀티자판기 제품 정보 ↗</a> · <a class="text-link" href="../installation-locations/">다른 설치 장소 보기 ↗</a></p></div></section>')
    guide=byslug['guides/vending-installation']
    guide['title']='자판기 설치 조건 7가지 | 전원·공간·반입 체크리스트'
    guide['desc']='멀티자판기·냉동자판기 설치 전에 확인할 전원 용량, 접지, 환기, 통신, 출입문·엘리베이터 반입, 설치비와 추가 공사 조건을 정리했습니다.'
    guide['body']+=feature_block('POWER & CONNECTIVITY','자판기 전원과 통신은 어떻게 준비하나요?',[
       '자판기는 기기 모델마다 요구 전압과 소비전력이 다릅니다. 특히 냉동 기기는 냉각장치를 사용하므로 전기 용량과 접지, 차단기 여유, 콘센트 위치를 사전에 확인해야 합니다. 해당 모델의 전기 사양을 모른 채 일반 콘센트에 연결해도 된다고 단정할 수는 없습니다.',
       '결제 단말기와 재고 관리 기능은 모델에 따라 통신 연결이 필요할 수 있습니다. 설치 장소의 유선·무선 통신 환경과 관리 담당자가 확인할 수 있는 접속 방식을 미리 점검하면 설치 후 운영이 수월합니다.'
    ],['선택 모델의 정격전압·소비전력 확인','분전반과 차단기 여유·접지 여부 점검','결제·원격관리 기능의 통신 방식 확인'])
    guide['body']+=feature_block('DELIVERY & SPACE','기기 반입과 설치 공간은 어떻게 계산하나요?',[
       '설치 예정 장소의 넓이만 확인하면 충분하지 않습니다. 실제로는 출입문 높이와 유효 폭, 건물 출입 경사로, 엘리베이터 내부 치수, 복도 회전 구간, 문 열림 범위까지 함께 확인해야 합니다. 반입이 어려우면 추가 인력이나 별도 운송 장비가 필요할 수 있습니다.',
       '설치 후에는 상품 인출과 보충 작업 공간, 고객 대기 공간, 냉각기 환기 거리도 확보해야 합니다. 냉동기기의 권장 이격거리는 제조사 모델별로 다르므로 실제 규격표를 기준으로 최종 확인하는 것이 안전합니다.'
    ],['출입문·엘리베이터·복도의 최소 유효 치수 확인','기기 앞 고객 대기·문 열림·상품 보충 공간 확보','기기 후면·측면 환기 필요 거리 확인'])
    guide['body']+=feature_block('COST CHECK','설치비가 달라지는 주요 원인',[
       '설치 지역, 건물 출입 조건, 기기 수량, 전기·통신 공사 필요 여부에 따라 최종 설치비가 달라질 수 있습니다. 자판기 구매 조건에 기본 설치가 포함되어 있더라도 모든 현장에 추가 비용이 없는 것은 아닙니다.',
       '견적을 요청할 때는 설치 예정 주소, 층수, 엘리베이터 유무, 현장 사진, 전원 위치, 희망 상품군을 함께 전달하면 필요한 공사 범위를 더 정확하게 검토할 수 있습니다.'
    ],[],'../../contact/','설치 조건 상담 신청')
    # universal link migrations and references to removed pages
    for p in pages:
       p['body']=p['body'].replace('safe24-unmanned-store/','unmanned-store/')
       p['body']=p['body'].replace('installation-cases/','installation-locations/')
       p['body']=p['body'].replace('use-cases/','installation-locations/')
       p['body']=p['body'].replace('스마트자판기 구매센터','자판기플랜')
    # retire misleading generated illustrations pretending to be authentic case images
    for p in pages:
       if p['slug'] in ('','multi-vending-machine','frozen-vending-machine','unmanned-store'):
           p['body']=p['body'].replace('실제 제품 이미지','제품 이해를 돕는 연출 이미지')
           p['body']=p['body'].replace('실물 이미지','연출 이미지')
    # Keep one primary inquiry CTA at the END of each expanded page.
    for p in pages:
        if p['slug'] in ('','multi-vending-machine','frozen-vending-machine','unmanned-store','multi-purchase'):
            match=re.search(r'<section class="cta-band">.*?</section>',p['body'],re.DOTALL)
            if match:
                p['body']=p['body'][:match.start()]+p['body'][match.end():]+match.group(0)
    return pages
