# 자판기플랜 v8 — 승인형 PSEO 운영 홈페이지

- 기준 주소: https://japangi-plan.netlify.app/ (Netlify 사이트명 실제 확보·배포 전에는 미공개)
- 검색 키워드: 멀티자판기, 냉동자판기, 무인매장 창업; 학교/호텔 설치 안내
- 기본 공개용 정적 페이지 11개 (검색 색인 대상 9개, 상담·개인정보 2개 비색인)
- 상담 CTA: 팝업 + `/contact/` 예비 경로
- 내부 Google Apps Script 웹훅 → Google Sheets 저장 → Gmail 알림: 실제 연결은 별도

## 새 PSEO 구조

`pseo/pages.json`에 신규 후보를 등록합니다.

| status | 동작 |
|--|--|
| idea/draft/review/hold/retired | 정적 HTML·사이트맵·RSS 생성 안 함 |
| approved/published | 필수 정보·출처·이미지·FAQ·중복 검사 통과 시만 공개 |

`pseo_engine.py`가 검증한 approved 항목만 HTML로 추가합니다.
- 설명/H1/제목/실제 검색 의도/고유 가치/구매 전 행동과 출처 메모 필요
- 각각 충분한 본문을 가진 4개 이상 섹션과 FAQ 2개 이상 필요 (글자수 통과만으로 승인 자격을 뜻하지 않음)
- 실제 설치 사진 주장 시 image_type=`actual` 및 image_evidence 필요
- 연출 사진은 image_type=`illustration`으로 구분
- 검토자 reviewed_by, **실제 발행일** published_on 반드시 입력
- slug 중복과 기존 URL 충돌, 동일 대표 키워드, 신규 승인 페이지 간 과도한 본문 중복 차단
- 문제 발생 시 빌드 중단; 미승인 항목은 언제나 비공개

## 실행

```bash
python tests_pseo.py
python build.py
python validate_site.py
```

Netlify: build command=`python tests_pseo.py && python build.py && python validate_site.py` / publish=`dist`.
Netlify Git 연결을 권장합니다. GitHub에 승인한 자료와 코드를 커밋하면 Netlify에서 배포합니다. `/dist`는 정적 미리보기 산출물이며 Netlify Functions를 배포하려면 **원본**을 연결해야 합니다.

## 수정 후 제공물

- `dist/`: 재빌드된 완성 HTML. `rss.xml`은 **새로 공개한 승인 항목이 없는 현 상태에서는 0건**이며 허위 발행일은 채우지 않습니다.
- `pseo/release-report.json`: 후보별 비공개/공개 상태와 승인 통과 수
- `GPT-운영명령문.md`: 주차별 GPT 요청문
- `SEO-PLAN.md` · `DEPLOY-NETLIFY.md` · `SETUP-GUIDE.md`: 기타 안내
- `pseo/pages.json`: 사무실(초안)·헬스장(아이디어)·밀키트(아이디어) 후보 — 배포 전까지 비공개

## 공개 전 필수 점검

실제 사업자 법적 명칭, 연락처, 개인정보 처리 및 제3자 제공 계약, 보유기간, 설치 사례 사진 공개권한을 확정하고, Netlify 환경변수와 Apps Script의 Sheets/Gmail 계정 연결 및 테스트가 필요합니다. `site-config.json` 보유기간 값은 의도적으로 공란이므로 상담 접수는 현재 비활성화됩니다.

현재 실제 Netlify 도메인 배포나 검색 색인은 완료되지 않았습니다.
