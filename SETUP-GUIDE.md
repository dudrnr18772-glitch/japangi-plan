# 설치 안내 — 홈페이지 상담 신청 → 구글 스프레드시트 → Gmail 알림

**현재 상태: 소스 구현 및 로컬 테스트 완료, 실제 구글/Netlify 계정 연동 전.**

## 1. 데이터 흐름

1. 홈페이지 `/contact/`에서 고객이 정보를 입력하고 개인정보 필수 동의 후 제출합니다.
2. Netlify Function `/.netlify/functions/submit-lead`에서 값을 확인합니다.
3. 서버의 비밀키와 함께 Google Apps Script 웹 앱으로 전달합니다.
4. Apps Script가 Google Sheets의 `상담접수` 탭에 새 행을 작성합니다.
5. 기록에 성공하면 Apps Script의 `MailApp.sendEmail`을 사용해 **새 상담 접수 메일을 수신용 Gmail 주소로 전송**합니다.
6. 메일에는 접수번호·관심상품만 포함하며 고객의 연락처·이메일·주소는 포함하지 않습니다. 이메일 전송이 실패해도 이미 기록된 상담 데이터는 유지됩니다.

> 이 버전은 **홈페이지에서 접수된 상담**에 대해 메일을 발송합니다. 운영자가 시트에 직접 타이핑하거나 기존 행을 수정한 것에 대해서는 이메일을 보내지 않습니다.

## 2. 홈페이지 운영 정보 확정

`site-config.json`에서 `operator_name`, `operator_contact`, `operator_retention`, `partner_name`, `partner_retention`, `site_url`을 입력합니다.

- `operator_name`: 개인정보를 수집하는 운영 주체의 **정확한 법적 상호**
- `operator_contact`: 이용자 권리 행사 및 상담 연락처
- `operator_retention`: 운영사가 상담 정보를 보유하는 기간(운영 실태와 일치해야 함)
- `partner_name`: 정보를 실제 제공받는 제휴업체(현재 임시 값: 다브인터네셔널)
- `partner_retention`: 제휴업체의 개인정보 보유기간
- `site_url`: 실제로 공개할 도메인 (예: `https://your-domain.example/`)

개인정보 처리 정보가 비어 있으면 상담 제출 버튼은 비활성화됩니다. 실제 개인정보 제공 경로에 MTS해원이 포함되는 경우 고지·동의의 제공받는 자 항목을 그에 맞게 검토해야 합니다.

## 3. Google Sheets 및 Apps Script 준비

1. Google Sheets에서 새 파일을 만들고 이름을 `스마트자판기 구매센터 - 상담접수 관리`로 설정합니다.
2. 시트 주소 `https://docs.google.com/spreadsheets/d/<문서ID>/edit`에서 문서 ID를 복사합니다.
3. **확장 프로그램 → Apps Script**로 이동합니다.
4. 기본 코드를 모두 지우고 이 프로젝트의 `apps-script/Code.gs` 전체를 붙여넣습니다.
5. **프로젝트 설정 → 스크립트 속성**에서 다음 세 값을 추가합니다.

| 속성 키 | 입력 값 |
|---|---|
| `SHEET_ID` | 새 구글 스프레드시트 문서 ID |
| `LEAD_SECRET` | 32자리 이상의 무작위 비밀키(공개 금지) |
| `NOTIFY_EMAIL` | 새 문의 알림을 받을 Gmail 주소(예: 본인 계정) |

**Gmail 로그인 비밀번호나 앱 비밀번호를 입력할 필요가 없습니다.** `NOTIFY_EMAIL`은 알림을 받을 주소일 뿐이며, 실제 메일 발신은 Apps Script 실행 계정의 `MailApp` 권한으로 처리됩니다.

### 최초 실행 권한 승인 및 알림 테스트

6. Apps Script 상단 함수 선택 메뉴에서 `testSetup`을 고르고 **실행**합니다.
7. 시트 접근과 이메일 전송 권한 승인을 완료합니다.
8. `상담접수` 탭이 자동으로 생성되고, `NOTIFY_EMAIL`로 **테스트 메일**이 도착하면 성공입니다. 테스트 시 실제 고객 데이터 행은 추가되지 않습니다.
9. 메일이 도착하지 않으면 Gmail의 스팸함과 Apps Script **실행** 로그에서 오류를 확인합니다.

## 4. Apps Script 웹 앱으로 배포

1. Apps Script 상단 **배포 → 새 배포**를 클릭합니다.
2. 유형 **웹 앱**, 실행 계정 **나**, 액세스 권한 **모든 사용자**로 설정합니다.
3. 배포 후 주소가 `/exec`로 끝나는 웹 앱 URL을 복사합니다.
4. 이후 `Code.gs` 내용을 수정한 경우 **배포 관리 → 배포 수정 → 새 버전**으로 다시 배포해야 실제 코드가 바뀝니다.

웹 앱 접근 자체는 공개일 수 있으므로 `LEAD_SECRET`은 충분히 긴 값이어야 합니다. 이 비밀키는 브라우저에서 내려받을 수 있는 자바스크립트에 절대 넣지 않습니다.

## 5. Netlify에 원본 프로젝트 배포

**ZIP의 `dist/` 폴더만 업로드하면 상담 접수 서버가 동작하지 않습니다. GitHub 연동 배포가 필요합니다.**

1. 원본 프로젝트의 모든 파일을 GitHub 저장소에 업로드합니다.
2. Netlify에서 GitHub 저장소를 연결합니다.
3. 빌드 명령: `python build.py`, 게시 폴더: `dist`, 서버 함수 폴더: `netlify/functions` (`netlify.toml`에 기재되어 있습니다).
4. Netlify → **Site configuration → Environment variables**에서 다음 항목을 추가합니다.

| 키 | 값 |
|---|---|
| `GOOGLE_SHEET_WEBHOOK_URL` | 4단계에서 복사한 Apps Script `/exec` URL |
| `LEAD_WEBHOOK_SECRET` | Apps Script의 `LEAD_SECRET`과 동일한 문자열 |

5. 환경변수 설정 후 Netlify에서 다시 배포합니다.
6. 실제로 `/contact/`에 테스트 정보를 입력하고 제출하면 **시트에 행이 추가된 뒤 새 Gmail 알림이 발송**됩니다.

## 6. 휴대폰 Gmail 알림

1. 스마트폰에 Gmail 앱을 설치하거나 기존 앱을 엽니다.
2. `NOTIFY_EMAIL`로 지정한 계정으로 로그인되어 있는지 확인합니다.
3. 휴대폰 설정에서 Gmail 앱 알림을 허용합니다.
4. Gmail 앱의 계정별 알림에서 새 메일 알림을 허용합니다.
5. 받은편지함에 테스트 메일이 도착해도 배너 알림이 없으면 휴대폰의 절전·집중모드 및 Gmail 알림 설정을 확인합니다.

Gmail이 메시지를 받은 뒤 휴대폰에 알림을 표시하는 시점은 기기 및 앱 설정에 따라 달라질 수 있으므로 항상 즉시 푸시가 도착한다고 보장할 수는 없습니다.

## 7. 문제 해결

- **제출 버튼 비활성화:** `site-config.json`의 운영사 정보·보유기간 미입력 상태입니다.
- **503 응답:** Netlify의 두 환경변수 중 하나가 누락되었을 가능성이 큽니다.
- **502 응답:** Apps Script URL, 스크립트 배포 권한, `LEAD_SECRET`, 일일 서비스 할당량 및 실행 로그를 확인하세요.
- **시트에 저장되었지만 Gmail 알림 없음:** Apps Script의 `NOTIFY_EMAIL`, 최초 `testSetup` 권한 승인, MailApp 일일 발송 한도와 실행 로그를 확인합니다.
- **중복 접수 안내:** 같은 상호·연락처·상품으로 5분 안에 신청하면 중복 제출을 방지합니다.
- **이메일은 오지만 휴대폰 푸시가 안 옴:** Gmail 앱의 계정별 알림 및 OS 알림 설정을 확인합니다.
- **시트 공유:** 개인정보가 저장되므로 공개 공유 링크를 사용하지 않고 필요한 담당자만 접근할 수 있도록 권한을 제한합니다.

## 8. 검색 공개 설정

`site_url`이 비어 있는 동안 `noindex`가 유지됩니다. 도메인을 정한 뒤 `site-config.json`을 수정해 재빌드하고 canonical·sitemap·robots를 확인하세요.
