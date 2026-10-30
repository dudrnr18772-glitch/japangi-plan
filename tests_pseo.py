import json,tempfile,unittest
from pathlib import Path
from datetime import date
from pseo_engine import load_editorial,QualityError,render_rss
ROOT=Path(__file__).resolve().parent
class EditorialTest(unittest.TestCase):
 def test_drafts_do_not_publish(self):
  p,r=load_editorial(ROOT/'pseo/pages.json', {'multi-vending-machine'},ROOT/'assets/img')
  self.assertEqual(p,[])
  self.assertEqual(len(r),3)
 def approved_fixture(self):
  return {'id':'TEST001','status':'approved','slug':'test-vending-guide','keyword':'샘플 자판기 도입','intent':'설치 목적과 구매 조건을 비교하려는 사업자를 위한 가이드입니다. 실제 정보는 예시로만 사용합니다.',
   'title':'샘플 자판기 도입과 설치 조건 비교 | 자판기플랜','description':'도입 전에 전원, 반입, 상품 구성을 비교하는 교육용 샘플입니다. 이 항목은 품질 게이트의 자동 테스트에만 사용하며 실제 홈페이지에 공개하지 않습니다.',
   'heading':'샘플 자판기 도입과 설치 조건','unique_value_heading':'확인할 장소별 변수','unique_value':'고객 동선과 상품 보관 조건이 달라질 수 있어 실제 현장을 먼저 조사하는 것이 중요합니다. 필요한 정보만 설명합니다. 담당자가 현장 사진과 주요 치수를 확인한 후 사용자를 위한 구성을 제안해야 합니다. 설치 계획이 불확실하면 별도 안내로 구분합니다.',
   'buyer_action':'제품 설치 전에 설치 장소의 폭과 높이, 콘센트와 인터넷 연결 가능 여부를 현장에서 직접 확인하세요. 세부 조건은 계약 담당자와 협의합니다. 건물 관리주체의 승인이 필요한지 확인하고 주차장에서 현장까지 반입 경로도 점검해야 합니다.',
   'source_notes':'이 콘텐츠는 생산 배포 대상이 아닌 테스트 용도의 예시 텍스트로 구성했습니다. 실제 고객 사례나 설치 정보를 주장하지 않습니다.',
   'image':'multi-hero.webp','image_type':'illustration','image_alt':'다양한 상품을 보여주는 스마트 자판기 연출 이미지','claims_real_installation':False,
   'reviewed_by':'QA reviewer','published_on':'2026-10-30',
   'sections':[{'heading':f'{k} 확인','body':(('제품을 선택할 때는 판매할 상품의 크기를 먼저 조사하고 현장의 폭과 높이를 확인해야 합니다. 현장 담당자가 통신과 전기 설비를 검토하고 상품 보충 흐름을 확인한 다음 실제 모델을 선정하는 편이 좋습니다. 기기 가격만으로 판단하지 말고 설치 장소의 유지보수 조건을 함께 비교합니다. '*2)+f'{k} 구별되는 테스트 자료')} for k in ('판매 상품','장소 동선','전기 조건','운영 유지')],
   'faq':[{'question':'어디에 설치하나요?','answer':'설치 공간과 사용 목적을 정한 뒤 출입문의 유효 폭 및 전력 용량을 확인합니다. 실제 모델에 따라 필요한 공간이 달라질 수 있습니다. 현장 사진을 기준으로 고객 통행 공간과 상품 보충 동선까지 확인하는 것을 권장합니다.'}, {'question':'비용은 어떻게 확인하나요?','answer':'본체 가격뿐 아니라 설치 운송비와 부가세, 결제 수단, 유지보수 범위를 동일한 기준으로 확인한 다음 견적을 비교하세요. 보증금과 추가 설비 공사 비용이 포함되어 있는지 견적서에서 항목별로 확인해야 합니다.'}]}
 def test_approved_with_evidence_passes(self):
  with tempfile.TemporaryDirectory() as tmp:
   file=Path(tmp)/'data.json';file.write_text(json.dumps([self.approved_fixture()],ensure_ascii=False),encoding='utf-8')
   published,_=load_editorial(file,{'multi-vending-machine'},ROOT/'assets/img',date(2026,10,30))
   self.assertEqual(len(published),1)
   rss=render_rss('https://japangi-plan.netlify.app/','자판기플랜',published)
   self.assertIn('TEST001',published[0]['id'])
   self.assertIn('test-vending-guide',rss)
 def test_approved_missing_unique_content_blocked(self):
  r=self.approved_fixture();r['sections'][0]['body']='짧은 글'
  with tempfile.TemporaryDirectory() as tmp:
   file=Path(tmp)/'data.json';file.write_text(json.dumps([r],ensure_ascii=False),encoding='utf-8')
   with self.assertRaises(QualityError):load_editorial(file,set(),ROOT/'assets/img',date(2026,10,30))
 def test_fake_installation_blocked(self):
  r=self.approved_fixture();r['claims_real_installation']=True
  with tempfile.TemporaryDirectory() as tmp:
   file=Path(tmp)/'data.json';file.write_text(json.dumps([r],ensure_ascii=False),encoding='utf-8')
   with self.assertRaises(QualityError):load_editorial(file,set(),ROOT/'assets/img',date(2026,10,30))
if __name__=='__main__':unittest.main()
