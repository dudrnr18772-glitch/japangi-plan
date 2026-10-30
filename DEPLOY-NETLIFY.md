# Netlify 무료 도메인 배포 안내

**추천 사이트명:** 자판기플랜
**확정 기준 주소:** https://japangi-plan.netlify.app/
**사이트맵:** https://japangi-plan.netlify.app/sitemap.xml
**robots.txt:** https://japangi-plan.netlify.app/robots.txt

주의: 이 도메인은 빌드 기준값으로 설정됐지만 Netlify 프로젝트 이름을 생성·예약한 것은 아닙니다. `japangi-plan` 사이트명을 생성할 수 있는지 Netlify 대시보드에서 확인해야 합니다.

## 원본 프로젝트 ZIP을 GitHub에 업로드하는 경우
1. 프로젝트 루트의 `build.py`, `seo_enhancements.py`, `netlify.toml`, `assets/`, `netlify/functions/`, `apps-script/` 등 모든 파일을 업로드합니다.
2. Netlify에서 저장소를 연결합니다.
3. Build command: `python build.py`; Publish directory: `dist`; Python 3.11 지정.
4. `site-config.json`에 설정된 `https://japangi-plan.netlify.app/`를 기준으로 canonical / sitemap.xml을 생성합니다. Netlify 배포 프리뷰에서는 `noindex`를 유지합니다.
5. 개인정보 보유기간·운영사 연락처·정보 제공받는 자를 실무 및 법무 검토 후 `site-config.json`에 반영합니다. 이후 문의 접수 기능을 검증합니다.
6. 구글 Apps Script 웹 앱 URL, LEAD_WEBHOOK_SECRET을 Netlify Function 런타임 환경변수로 등록하고, 스프레드시트·Gmail 알림까지 테스트합니다.

## 정적 ZIP만 드래그앤드롭하는 경우
정적 ZIP에는 Netlify Functions와 빌드 과정이 포함되지 않으므로 문의 접수·Sheets/Gmail 연동 기능이 작동하지 않습니다. **전체 원본 프로젝트를 Git 연동 방식으로 배포**해야 합니다.

## SEO 검수
정식 주소에서 모든 페이지의 canonical과 og:url을 확인하고 `/sitemap.xml`, `/robots.txt`를 점검한 뒤 네이버 서치어드바이저에 사이트와 사이트맵을 등록하세요. 인덱싱 및 순위는 보장되지 않습니다.

## v7 상담 팝업
모든 주요 페이지의 상담 CTA는 클릭하면 팝업으로 열리며, 자바스크립트가 없는 환경에서는 `/contact/`로 이동합니다. 상담 폼은 Netlify Function을 이용하므로 드래그앤드롭 정적 배포에서는 실전 접수가 되지 않습니다.
